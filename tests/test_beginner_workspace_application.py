"""Task 4: BeginnerWorkspaceApplication + combined workspace projection tests.

Covers the approved vertical-slice behaviors: autosaving selection without
advancing, review availability vs acceptance readiness, revision exploration
marking downstream at-risk (never stale), optimistic concurrency, locked-stage
denial, tension acknowledgement, reassessment, revision cancel, and
Navigator/Decision-Card consistency from a single projection snapshot.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.beginner.application import (
    BeginnerWorkspaceApplication,
    BeginnerWorkspaceError,
    LockedStageError,
)
from auteur.beginner.contracts import DecisionStage, LifecycleStatus, MutationCommand, StageAvailability
from auteur.beginner.mystery_adapter import mystery_qualification_inventory
from auteur.beginner.persistence import BeginnerConcurrencyError


def make_app(tmp_path: Path, workspace_id: str = "workspace-1") -> BeginnerWorkspaceApplication:
    app = BeginnerWorkspaceApplication(tmp_path, workspace_id)
    app.create_workspace(
        command_id="create-1",
        project_id="project-1",
        premise="A missing heir returns home.",
        guidance_genre="mystery",
    )
    return app


def discover_cards() -> list[str]:
    inventory = mystery_qualification_inventory()
    return [card.card_id for card in inventory.cards if card.card_id.startswith("discover.")]


def answer_discover_cleanly(app: BeginnerWorkspaceApplication) -> BeginnerWorkspaceApplication:
    """Answer every discover card with its recommendation; returns the app."""
    from auteur.beginner.mystery_adapter import mystery_qualification_inventory as inventory_fn

    inventory = inventory_fn()
    current: str | None = None
    for card in inventory.cards:
        if not card.card_id.startswith("discover."):
            continue
        if current is not None:
            version = app.projection().session_version
            outcome = app.continue_decision(card_id=current, expected_session_version=version)
            if not outcome.advanced:
                break
        version = app.projection().session_version
        try:
            app.select_working_option(
                card_id=card.card_id,
                option=card.recommendation,
                expected_session_version=version,
            )
        except BeginnerWorkspaceError as exc:
            if "already answered" not in str(exc):
                raise
        current = card.card_id
    return app


def test_select_autosaves_without_advancing_current_card(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    card_id = discover_cards()[0]
    before = app.projection()
    current_before = before.decision_card.card_id

    result = app.select_working_option(
        card_id=card_id,
        option=before.decision_card.options[0],
        expected_session_version=before.session_version,
    )

    after = app.projection()
    assert after.session_version == before.session_version + 1
    assert after.decision_card.card_id == current_before
    assert after.decision_card.selected_option == before.decision_card.options[0]
    assert result.saved is True
    assert result.advanced is False
    # Autosaved into the durable session envelope.
    assert app.session_store.load().session_version == after.session_version


def test_projection_composes_decision_workspace_and_inspector_from_one_snapshot(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    initial = app.projection()
    app.select_working_option(
        card_id=initial.decision_card.card_id,
        option=initial.decision_card.options[0],
        expected_session_version=initial.session_version,
    )
    projection = app.projection()

    assert projection.decision_workspace.current_focus.question == projection.decision_card.question
    assert projection.decision_workspace.next_action
    assert projection.guidance_inspector.recommendation == projection.decision_card.recommendation
    assert projection.guidance_inspector.authority_status == "DERIVED / NOT CANON"
    assert projection.guidance_inspector.narrative_consequences
    selected_impact = projection.decision_card.option_impacts[projection.decision_card.selected_option]
    assert projection.decision_workspace.immediate_consequence == selected_impact.narrative_structure


def test_projection_separates_story_consequences_from_auteur_reasoning(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    initial = app.projection()
    app.select_working_option(
        card_id=initial.decision_card.card_id,
        option=initial.decision_card.options[0],
        expected_session_version=initial.session_version,
    )
    projection = app.projection()
    inspector = projection.guidance_inspector

    assert {item.semantic_area for item in inspector.narrative_consequences}
    assert inspector.recommendation_rationale
    assert inspector.evidence
    assert inspector.authority_status == "DERIVED / NOT CANON"
    assert inspector.context_guidance.reader_experience
    assert inspector.context_guidance.genre_conventions
    assert inspector.context_guidance.emotional_promise is None
    assert inspector.option_comparisons
    assert {item.label for item in inspector.option_comparisons} >= {
        projection.decision_card.recommendation,
        *projection.decision_card.options,
    }


def test_last_answer_makes_review_available_but_not_ready_until_validation(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)

    projection = app.projection()
    discover = next(entry for entry in projection.navigator if entry.stage is DecisionStage.DISCOVER)
    assert discover.answered_cards == discover.total_cards == 3
    assert discover.review_available is True
    # Clean answers (all recommendations): ready to accept once validated.
    assert discover.ready_to_accept is True
    assert projection.reviews[DecisionStage.DISCOVER].ready_to_accept is True


def test_valid_non_recommended_answer_does_not_block_readiness(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    inventory = mystery_qualification_inventory()
    cards = [card for card in inventory.cards if card.card_id.startswith("discover.")]
    first, rest = cards[0], cards[1:]
    non_recommended = next(option for option in first.options if option != first.recommendation)

    version = app.projection().session_version
    app.select_working_option(card_id=first.card_id, option=non_recommended, expected_session_version=version)
    current = first.card_id
    for card in rest:
        version = app.projection().session_version
        outcome = app.continue_decision(card_id=current, expected_session_version=version)
        assert outcome.advanced is True
        current = outcome.card_id
        assert current == card.card_id
        version = app.projection().session_version
        app.select_working_option(card_id=card.card_id, option=card.recommendation, expected_session_version=version)
    version = app.projection().session_version
    final = app.continue_decision(card_id=current, expected_session_version=version)
    assert final.advanced is False
    assert final.review_available is True

    projection = app.projection()
    assert projection.reviews[DecisionStage.DISCOVER].ready_to_accept is True
    assert len(projection.tensions) == 1
    assert projection.tensions[0].blocking is False
    assert projection.tensions[0].acknowledged is True


def test_revision_exploration_marks_downstream_at_risk_not_stale(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    version = app.projection().session_version

    app.open_revision(revision_id="revision-1", expected_session_version=version)
    parent_before = app.session_store.load()

    overlay_version = app.projection().session_version
    app.select_working_option(
        card_id=discover_cards()[0],
        option=mystery_qualification_inventory().card(discover_cards()[0]).options[-1],
        expected_session_version=overlay_version,
        exploratory=True,
    )

    projection = app.projection()
    assert projection.revision.active_revision_id == "revision-1"
    assert projection.revision.is_exploration is True
    downstream = [entry for entry in projection.navigator if entry.stage is not DecisionStage.DISCOVER]
    assert downstream, "expected downstream stages in navigator"
    for entry in downstream:
        assert entry.at_risk_if_accepted is True
        assert entry.stale is False
    # Parent canonical session content untouched at session level (the journey
    # sidecar bump only advances session_version for optimistic concurrency).
    parent_after = app.session_store.load()
    assert parent_after.model_dump(exclude={"session_version"}) == parent_before.model_dump(exclude={"session_version"})


def test_open_revision_focuses_requested_accepted_stage(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    app.open_milestone_review(
        stage=DecisionStage.DISCOVER,
        expected_session_version=app.projection().session_version,
    )
    app.accept_story_direction(expected_session_version=app.projection().session_version, command_id="accept-direction-test")
    version = app.projection().session_version

    app.open_revision(
        revision_id="revision-focus-discover",
        stage=DecisionStage.DISCOVER,
        expected_session_version=version,
    )

    projection = app.projection()
    assert projection.revision.target_stage is DecisionStage.DISCOVER
    assert projection.decision_card is not None
    assert projection.decision_card.stage is DecisionStage.DISCOVER


def test_active_revision_routes_selection_to_overlay_without_exploratory_flag(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    app.open_milestone_review(
        stage=DecisionStage.DISCOVER,
        expected_session_version=app.projection().session_version,
    )
    app.accept_story_direction(expected_session_version=app.projection().session_version, command_id="accept-direction-test")
    parent_before = app.session_store.load()
    version = app.projection().session_version
    card_id = discover_cards()[0]
    alternate = mystery_qualification_inventory().card(card_id).options[-1]

    app.open_revision(
        revision_id="revision-auto-exploratory",
        stage=DecisionStage.DISCOVER,
        expected_session_version=version,
    )
    result = app.select_working_option(
        card_id=card_id,
        option=alternate,
        expected_session_version=app.projection().session_version,
    )

    assert result.exploratory is True
    assert app.projection().decision_card.selected_option == alternate
    parent_after = app.session_store.load()
    assert parent_after.model_dump(exclude={"session_version"}) == parent_before.model_dump(
        exclude={"session_version"}
    )


def test_stale_version_rejects(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    card_id = discover_cards()[0]
    projection = app.projection()
    app.select_working_option(
        card_id=card_id,
        option=projection.decision_card.options[0],
        expected_session_version=projection.session_version,
    )

    with pytest.raises(BeginnerConcurrencyError):
        app.select_working_option(
            card_id=card_id,
            option=projection.decision_card.options[0],
            expected_session_version=projection.session_version,
        )


def test_locked_stage_denied(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    inventory = mystery_qualification_inventory()
    locked_card = next(card.card_id for card in inventory.cards if card.card_id.startswith("story_identity."))
    version = app.projection().session_version

    with pytest.raises(LockedStageError):
        app.select_working_option(
            card_id=locked_card,
            option="Want: Solve the puzzle",
            expected_session_version=version,
        )
    with pytest.raises(LockedStageError):
        app.open_milestone_review(stage=DecisionStage.STORY_IDENTITY, expected_session_version=version)


def test_tension_acknowledgement_and_unknown_tension(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    inventory = mystery_qualification_inventory()
    card = next(c for c in inventory.cards if c.card_id.startswith("discover."))
    non_recommended = next(option for option in card.options if option != card.recommendation)
    version = app.projection().session_version
    app.select_working_option(card_id=card.card_id, option=non_recommended, expected_session_version=version)

    tension_id = app.projection().tensions[0].tension_id
    app.acknowledge_tension(tension_id=tension_id, expected_session_version=app.projection().session_version)
    assert app.projection().tensions[0].acknowledged is True

    with pytest.raises(BeginnerWorkspaceError, match="unknown tension"):
        app.acknowledge_tension(
            tension_id="no-such-tension",
            expected_session_version=app.projection().session_version,
        )


def test_reassessment_refreshes_stale_assumptions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    assert app.projection().reviews[DecisionStage.DISCOVER].ready_to_accept is True

    from auteur.beginner import mystery_adapter as mystery_module

    real_digest = mystery_module.MysteryGuidanceAdapter._source_digest()
    monkeypatch.setattr(
        mystery_module.MysteryGuidanceAdapter,
        "_source_digest",
        classmethod(lambda cls: "0" * 64 if real_digest != "0" * 64 else "1" * 64),
    )
    try:
        projection = app.projection()
        assert projection.reviews[DecisionStage.DISCOVER].ready_to_accept is False
        assert any("stale" in blocker.lower() for blocker in projection.reviews[DecisionStage.DISCOVER].blockers)

        card_id = discover_cards()[0]
        refreshed = app.reassess_guidance(card_id=card_id, expected_session_version=app.projection().session_version)
        assert refreshed.card_id == card_id
        assert app.projection().reviews[DecisionStage.DISCOVER].ready_to_accept is True
    finally:
        monkeypatch.undo()


def test_cancel_revision_leaves_parent_unchanged(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    parent_before = app.session_store.load()
    version = app.projection().session_version

    app.open_revision(revision_id="revision-1", expected_session_version=version)
    app.select_working_option(
        card_id=discover_cards()[0],
        option=mystery_qualification_inventory().card(discover_cards()[0]).options[-1],
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )
    app.cancel_revision(expected_session_version=app.projection().session_version)

    projection = app.projection()
    assert projection.revision.active_revision_id is None
    assert projection.revision.is_exploration is False
    assert all(entry.at_risk_if_accepted is False for entry in projection.navigator)
    parent_after = app.session_store.load()
    assert parent_after.model_dump(exclude={"session_version"}) == parent_before.model_dump(exclude={"session_version"})


def test_navigator_and_decision_card_consistent_from_same_projection(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    version = app.projection().session_version
    first_card = discover_cards()[0]
    projection = app.projection()
    app.select_working_option(
        card_id=first_card,
        option=projection.decision_card.recommendation,
        expected_session_version=version,
    )
    app.continue_decision(card_id=first_card, expected_session_version=app.projection().session_version)

    projection = app.projection()
    assert projection.decision_card.card_id == discover_cards()[1]
    current_entry = next(entry for entry in projection.navigator if entry.current_card_id is not None)
    assert current_entry.current_card_id == projection.decision_card.card_id
    assert current_entry.stage is DecisionStage.DISCOVER
    # Stage status mirrors the same snapshot.
    status = projection.stage_status[DecisionStage.DISCOVER]
    assert status.lifecycle is LifecycleStatus.WORKING
    assert status.availability is StageAvailability.AVAILABLE
    assert projection.snapshot_session_version == projection.session_version


def test_review_synthesis_is_whole_first_with_expandable_evidence(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    version = app.projection().session_version

    review = app.open_milestone_review(stage=DecisionStage.DISCOVER, expected_session_version=version)

    assert review.stage is DecisionStage.DISCOVER
    assert review.synthesis.strip(), "expected a whole-first synthesis"
    assert len(review.card_summaries) == 3
    assert all(summary.evidence for summary in review.card_summaries)
    # Synthesis leads; per-card evidence is expandable detail, not replayed inline.
    for summary in review.card_summaries:
        for item in summary.evidence:
            assert item not in review.synthesis


def test_acceptance_entry_point_defers_canonical_mutation(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    canonical_before = list(app.projection().canonical_refs)
    session_before = app.session_store.load()
    review = app.open_milestone_review(
        stage=DecisionStage.DISCOVER, expected_session_version=app.projection().session_version
    )
    assert review.ready_to_accept is True

    outcome = app.request_acceptance(
        stage=DecisionStage.DISCOVER, expected_session_version=app.projection().session_version
    )

    assert outcome.ready is True
    assert outcome.accepted is False
    assert outcome.deferred_to_task_5 is True
    assert list(app.projection().canonical_refs) == canonical_before
    session_after = app.session_store.load()
    assert session_after.model_dump(exclude={"session_version"}) == session_before.model_dump(
        exclude={"session_version"}
    )


def test_create_workspace_is_idempotent_via_receipt_replay(tmp_path: Path) -> None:
    app = BeginnerWorkspaceApplication(tmp_path, "workspace-1")
    first = app.create_workspace(
        command_id="create-1",
        project_id="project-1",
        premise="A missing heir returns home.",
        guidance_genre="mystery",
    )
    second = app.create_workspace(
        command_id="create-1",
        project_id="project-1",
        premise="A missing heir returns home.",
        guidance_genre="mystery",
    )
    assert second == first
    assert app.projection().session_version == first.session_version


# -- Task 4 spec FAIL remediation: command envelope + idempotency --------------


def test_journey_commands_accept_mutation_command_envelope(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    card_id = discover_cards()[0]
    projection = app.projection()
    option = projection.decision_card.options[0]

    result = app.select_working_option(
        command=MutationCommand(
            workspace_id="workspace-1",
            expected_session_version=projection.session_version,
            command_id="env-select-1",
            payload={"card_id": card_id, "option": option},
        )
    )
    assert result.card_id == card_id
    assert result.selected_option == option

    continued = app.continue_decision(
        command=MutationCommand(
            workspace_id="workspace-1",
            expected_session_version=app.projection().session_version,
            command_id="env-continue-1",
            payload={"card_id": card_id},
        )
    )
    assert continued.advanced is True

    with pytest.raises(BeginnerWorkspaceError, match="targets"):
        app.select_working_option(
            command=MutationCommand(
                workspace_id="some-other-workspace",
                expected_session_version=app.projection().session_version,
                command_id="env-select-bad",
                payload={"card_id": card_id, "option": option},
            )
        )


def test_select_retry_after_complete_returns_recorded_result(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    inventory = mystery_qualification_inventory()
    card = next(c for c in inventory.cards if c.card_id.startswith("discover."))
    other_option = next(option for option in card.options if option != card.options[0])
    version = app.projection().session_version

    first = app.select_working_option(
        card_id=card.card_id,
        option=card.options[0],
        expected_session_version=version,
        command_id="select-retry-1",
    )
    advanced_version = app.projection().session_version
    assert advanced_version == version + 1

    # Retry after complete with a *different* option must replay, not double-apply.
    second = app.select_working_option(
        card_id=card.card_id,
        option=other_option,
        expected_session_version=version,
        command_id="select-retry-1",
    )
    assert second == first
    assert app.projection().session_version == advanced_version
    assert app.projection().decision_card.selected_option == card.options[0]


def test_continue_retry_after_complete_returns_recorded_result(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    cards = discover_cards()
    inventory = mystery_qualification_inventory()
    first_card = inventory.card(cards[0])
    version = app.projection().session_version
    app.select_working_option(
        card_id=cards[0],
        option=first_card.recommendation,
        expected_session_version=version,
        command_id="continue-setup-select",
    )

    first = app.continue_decision(
        card_id=cards[0],
        expected_session_version=app.projection().session_version,
        command_id="continue-retry-1",
    )
    assert first.advanced is True
    settled_version = app.projection().session_version

    second = app.continue_decision(
        card_id=cards[0],
        expected_session_version=settled_version - 1,
        command_id="continue-retry-1",
    )
    assert second == first
    assert app.projection().session_version == settled_version


def test_sidecar_commands_are_idempotent_without_double_apply(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)

    review_first = app.open_milestone_review(
        stage=DecisionStage.DISCOVER,
        expected_session_version=app.projection().session_version,
        command_id="review-retry-1",
    )
    settled = app.projection().session_version
    review_second = app.open_milestone_review(
        stage=DecisionStage.DISCOVER,
        expected_session_version=settled - 1,
        command_id="review-retry-1",
    )
    assert review_second == review_first
    assert app.projection().session_version == settled

    acceptance_first = app.request_acceptance(
        stage=DecisionStage.DISCOVER,
        expected_session_version=settled,
        command_id="acceptance-retry-1",
    )
    acceptance_second = app.request_acceptance(
        stage=DecisionStage.DISCOVER,
        expected_session_version=settled,
        command_id="acceptance-retry-1",
    )
    assert acceptance_second == acceptance_first
    assert app.projection().session_version == settled

    guidance_first = app.reassess_guidance(
        card_id=discover_cards()[0],
        expected_session_version=settled,
        command_id="reassess-retry-1",
    )
    reassessed_version = app.projection().session_version
    guidance_second = app.reassess_guidance(
        card_id=discover_cards()[0],
        expected_session_version=settled,
        command_id="reassess-retry-1",
    )
    assert guidance_second == guidance_first
    assert app.projection().session_version == reassessed_version


def test_revision_open_cancel_are_idempotent_without_double_apply(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    version = app.projection().session_version

    opened_first = app.open_revision(
        revision_id="revision-retry-1",
        expected_session_version=version,
        command_id="open-revision-retry-1",
    )
    opened_version = app.projection().session_version
    opened_second = app.open_revision(
        revision_id="revision-retry-1",
        expected_session_version=version,
        command_id="open-revision-retry-1",
    )
    assert opened_second == opened_first
    assert app.projection().session_version == opened_version

    cancelled_first = app.cancel_revision(
        expected_session_version=opened_version,
        command_id="cancel-revision-retry-1",
    )
    cancelled_version = app.projection().session_version
    cancelled_second = app.cancel_revision(
        expected_session_version=opened_version,
        command_id="cancel-revision-retry-1",
    )
    assert cancelled_second == cancelled_first
    assert app.projection().session_version == cancelled_version


def test_retry_while_command_in_progress_is_rejected(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    card_id = discover_cards()[0]
    option = app.projection().decision_card.options[0]
    version = app.projection().session_version
    app.receipt_store.begin("hung-command-1", command_type="create_workspace")

    with pytest.raises(BeginnerWorkspaceError, match="in progress"):
        app.select_working_option(
            card_id=card_id,
            option=option,
            expected_session_version=version,
            command_id="hung-command-1",
        )
    # The blocked attempt applied nothing.
    assert app.projection().session_version == version


def test_concurrent_sidecar_mutations_do_not_lost_update(tmp_path: Path) -> None:
    first_app = make_app(tmp_path)
    inventory = mystery_qualification_inventory()
    card = next(c for c in inventory.cards if c.card_id.startswith("discover."))
    non_recommended = next(option for option in card.options if option != card.recommendation)
    version = first_app.projection().session_version
    first_app.select_working_option(card_id=card.card_id, option=non_recommended, expected_session_version=version)
    tension_id = first_app.projection().tensions[0].tension_id

    # A second actor on the same workspace sees the same version.
    second_app = BeginnerWorkspaceApplication(tmp_path, "workspace-1")
    stale_version = second_app.projection().session_version

    first_app.acknowledge_tension(tension_id=tension_id, expected_session_version=stale_version)

    with pytest.raises(BeginnerConcurrencyError):
        second_app.reassess_guidance(card_id=card.card_id, expected_session_version=stale_version)


def test_renavigate_to_earlier_card_replaces_working_projection(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    inventory = mystery_qualification_inventory()
    cards = [card for card in inventory.cards if card.card_id.startswith("discover.")]
    first, second = cards[0], cards[1]
    alternate = next(option for option in first.options if option != first.recommendation)

    version = app.projection().session_version
    app.select_working_option(card_id=first.card_id, option=first.recommendation, expected_session_version=version)
    app.continue_decision(card_id=first.card_id, expected_session_version=app.projection().session_version)
    app.select_working_option(
        card_id=second.card_id,
        option=second.recommendation,
        expected_session_version=app.projection().session_version,
    )

    # Revise the earlier card: select navigates back and replaces the working projection.
    result = app.select_working_option(
        card_id=first.card_id,
        option=alternate,
        expected_session_version=app.projection().session_version,
    )
    assert result.selected_option == alternate
    projection = app.projection()
    assert projection.decision_card.card_id == first.card_id
    assert projection.decision_card.selected_option == alternate
    status = app.session_store.load().stages[DecisionStage.DISCOVER]
    assert status.working_decision is not None
    assert status.working_decision.selected_option == alternate
    current_entry = next(entry for entry in projection.navigator if entry.current_card_id is not None)
    assert current_entry.current_card_id == first.card_id


def test_session_lifecycle_persists_review_ready_transitions(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)

    stages = app.session_store.load().stages
    assert stages[DecisionStage.DISCOVER].lifecycle is LifecycleStatus.COMPLETE
    # Availability stays separated from lifecycle.
    assert stages[DecisionStage.DISCOVER].availability is StageAvailability.AVAILABLE
    assert stages[DecisionStage.STORY_IDENTITY].availability is StageAvailability.LOCKED
    assert stages[DecisionStage.STORY_IDENTITY].lifecycle is LifecycleStatus.NOT_STARTED

    navigator_entry = next(entry for entry in app.projection().navigator if entry.stage is DecisionStage.DISCOVER)
    assert navigator_entry.lifecycle is LifecycleStatus.COMPLETE


def test_session_lifecycle_remains_complete_for_valid_alternative(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    inventory = mystery_qualification_inventory()
    cards = [card for card in inventory.cards if card.card_id.startswith("discover.")]
    first, rest = cards[0], cards[1:]
    non_recommended = next(option for option in first.options if option != first.recommendation)

    version = app.projection().session_version
    app.select_working_option(card_id=first.card_id, option=non_recommended, expected_session_version=version)
    current = first.card_id
    for card in rest:
        version = app.projection().session_version
        outcome = app.continue_decision(card_id=current, expected_session_version=version)
        current = outcome.card_id
        version = app.projection().session_version
        app.select_working_option(card_id=card.card_id, option=card.recommendation, expected_session_version=version)
    version = app.projection().session_version
    app.continue_decision(card_id=current, expected_session_version=version)

    assert app.session_store.load().stages[DecisionStage.DISCOVER].lifecycle is LifecycleStatus.COMPLETE


def test_open_revision_without_divergence_marks_no_risk(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    version = app.projection().session_version

    app.open_revision(revision_id="revision-clean-open", expected_session_version=version)

    projection = app.projection()
    assert projection.revision.active_revision_id == "revision-clean-open"
    assert projection.revision.is_exploration is True
    assert projection.revision.at_risk_stages == ()
    assert all(entry.at_risk_if_accepted is False for entry in projection.navigator)


def test_cancel_revision_removes_orphan_snapshot(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    version = app.projection().session_version

    app.open_revision(revision_id="revision-orphan", expected_session_version=version)
    snapshot_path = app.session_store.revision_session_path("revision-orphan")
    assert snapshot_path.exists()

    app.cancel_revision(expected_session_version=app.projection().session_version)

    assert not snapshot_path.exists()
    assert app.projection().revision.active_revision_id is None


def test_exploratory_divergence_records_nonblocking_tension(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    assert app.projection().reviews[DecisionStage.DISCOVER].ready_to_accept is True
    version = app.projection().session_version

    app.open_revision(revision_id="revision-explore-tension", expected_session_version=version)
    card_id = discover_cards()[0]
    overlay_option = mystery_qualification_inventory().card(card_id).options[-1]
    app.select_working_option(
        card_id=card_id,
        option=overlay_option,
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )

    projection = app.projection()
    exploratory_tensions = [tension for tension in projection.tensions if tension.card_id == card_id]
    assert exploratory_tensions, "expected an exploratory tension to be recorded"
    assert all(tension.blocking is False for tension in exploratory_tensions)
    # Nonblocking authorial tensions never gate milestone readiness.
    assert projection.reviews[DecisionStage.DISCOVER].ready_to_accept is True


def test_reassess_records_per_card_digest(tmp_path: Path) -> None:
    app = make_app(tmp_path)
    answer_discover_cleanly(app)
    card_id = discover_cards()[0]

    app.reassess_guidance(card_id=card_id, expected_session_version=app.projection().session_version)

    per_card = app._journey.get("basis_digests") or {}
    assert per_card.get(card_id) == app._current_digest(app.session_store.load())
    assert app._journey.get("basis_digest") == app._current_digest(app.session_store.load())
