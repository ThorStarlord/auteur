from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.contracts import AcceptedMilestoneReference, RevisionRef, SessionEnvelope


def _foundation_app(tmp_path):
    app = BeginnerWorkspaceApplication(tmp_path, "continuation-1")
    session = SessionEnvelope.new("project", "mystery", "A locked room")
    session = session.model_copy(
        update={
            "accepted_milestones": [
                AcceptedMilestoneReference(
                    milestone_id="whole_story_structure",
                    revision=RevisionRef(artifact_id="blueprint", revision=1),
                )
            ]
        }
    )
    app.session_store.create(session)
    return app


def test_continuation_requires_explicit_acceptance_at_each_boundary(tmp_path) -> None:
    app = _foundation_app(tmp_path)

    projection = app.propose_outline(
        expected_session_version=app.projection().session_version,
        command_id="outline-proposal",
    )
    assert projection.continuation.outline_proposal is not None
    assert "accept-outline" in projection.available_actions

    projection = app.accept_outline(
        expected_session_version=projection.session_version,
        command_id="outline-acceptance",
    )
    projection = app.propose_chapter_plan(
        expected_session_version=projection.session_version,
        command_id="chapter-plan-proposal",
    )
    assert projection.continuation.chapter_plan is not None
    assert not projection.continuation.chapter_plan_accepted


def test_draft_handoff_records_accepted_inputs_without_writing_canon(tmp_path) -> None:
    app = _foundation_app(tmp_path)
    version = app.projection().session_version
    app.propose_outline(expected_session_version=version, command_id="outline")
    app.accept_outline(expected_session_version=app.projection().session_version, command_id="accept-outline")
    app.propose_chapter_plan(expected_session_version=app.projection().session_version, command_id="chapter")
    app.accept_chapter_plan(expected_session_version=app.projection().session_version, command_id="accept-chapter")
    app.propose_scene_plans(expected_session_version=app.projection().session_version, command_id="scenes")
    app.accept_scene_plans(expected_session_version=app.projection().session_version, command_id="accept-scenes")
    projection = app.prepare_draft_handoff(
        expected_session_version=app.projection().session_version,
        command_id="draft-handoff",
    )

    assert projection.continuation.draft_handoff.accepted_inputs == (
        "story_identity",
        "whole_story_structure",
        "outline",
        "chapter_plan",
        "scene_plan",
    )
    assert projection.continuation.draft_handoff.command == "auteur draft <project> 1"
    assert not (tmp_path / "story_identity.yaml").exists()
    assert not (tmp_path / "blueprint.yaml").exists()


def test_projection_reorients_to_review_after_chapter_draft_exists(tmp_path) -> None:
    app = _foundation_app(tmp_path)
    version = app.projection().session_version
    app.propose_outline(expected_session_version=version, command_id="outline")
    app.accept_outline(expected_session_version=app.projection().session_version, command_id="accept-outline")
    app.propose_chapter_plan(expected_session_version=app.projection().session_version, command_id="chapter")
    app.accept_chapter_plan(expected_session_version=app.projection().session_version, command_id="accept-chapter")
    app.propose_scene_plans(expected_session_version=app.projection().session_version, command_id="scenes")
    app.accept_scene_plans(expected_session_version=app.projection().session_version, command_id="accept-scenes")
    app.prepare_draft_handoff(expected_session_version=app.projection().session_version, command_id="draft")
    draft_path = tmp_path / "chapters" / "01" / "final.md"
    draft_path.parent.mkdir(parents=True)
    draft_path.write_text("Chapter 1", encoding="utf-8")

    projection = app.projection()

    assert projection.continuation.draft_status == "drafted"
    assert "review-chapter-1" in projection.available_actions


def test_upstream_change_marks_downstream_continuation_stale(tmp_path) -> None:
    app = _foundation_app(tmp_path)
    projection = app.projection()
    for method, command_id in (
        (app.propose_outline, "stale-outline"),
        (app.accept_outline, "stale-accept-outline"),
        (app.propose_chapter_plan, "stale-chapter"),
        (app.accept_chapter_plan, "stale-accept-chapter"),
        (app.propose_scene_plans, "stale-scenes"),
        (app.accept_scene_plans, "stale-accept-scenes"),
        (app.prepare_draft_handoff, "stale-handoff"),
    ):
        projection = method(expected_session_version=projection.session_version, command_id=command_id)
    session = app.session_store.load()
    changed = session.accepted_milestones[0].model_copy(
        update={"fingerprint": "changed-upstream-fingerprint"}
    )
    app.session_store.update(
        session.session_version,
        lambda current: current.model_copy(update={"accepted_milestones": [changed, *current.accepted_milestones[1:]]}),
    )
    stale = app.projection()
    assert stale.continuation.stale is True
    assert stale.continuation.draft_handoff.status == "stale"
    assert "review-stale-continuation" in stale.available_actions


def test_restart_reload_preserves_continuation_and_replays_receipt(tmp_path) -> None:
    app = _foundation_app(tmp_path)
    projection = app.propose_outline(expected_session_version=1, command_id="reload-outline")
    restarted = BeginnerWorkspaceApplication(tmp_path, "continuation-1")
    replay = restarted.propose_outline(expected_session_version=999, command_id="reload-outline")
    assert replay.continuation.outline_proposal.proposal_id == projection.continuation.outline_proposal.proposal_id
    assert len(replay.continuation.outline_proposal.chapters) == 1
    assert restarted.session_store.load().session_version == projection.session_version
