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
from auteur.beginner.contracts import DecisionStage, LifecycleStatus, StageAvailability
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


def test_non_recommended_answer_blocks_readiness_until_tension_acknowledged(tmp_path: Path) -> None:
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
    assert projection.reviews[DecisionStage.DISCOVER].ready_to_accept is False
    blockers = projection.reviews[DecisionStage.DISCOVER].blockers
    assert any("tension" in blocker.lower() for blocker in blockers)
    assert len(projection.tensions) == 1
    assert projection.tensions[0].blocking is True
    assert projection.tensions[0].acknowledged is False
    # Ordinary navigation already stayed nonblocking above: both continues
    # succeeded while the blocking tension was unresolved.

    tension_id = projection.tensions[0].tension_id
    app.acknowledge_tension(tension_id=tension_id, expected_session_version=app.projection().session_version)

    projection = app.projection()
    assert projection.tensions[0].acknowledged is True
    assert projection.reviews[DecisionStage.DISCOVER].ready_to_accept is True


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
    # Parent canonical session untouched at session level.
    assert app.session_store.load() == parent_before


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
    assert app.session_store.load() == parent_before


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
    assert app.session_store.load() == session_before


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
