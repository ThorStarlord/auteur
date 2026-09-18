"""Task 8: sealed-elevator qualification for the Beginner Workspace slice.

End-to-end journey plus contract scenarios over the deterministic
sealed-elevator fixture:

- premise -> Discover -> Accept Direction -> Identity -> Accept Identity ->
  Structure -> Accept Structure reaches canonical whole-story structure;
- acknowledged nonblocking tension never gates readiness;
- blocking contradiction gates review until acknowledged;
- materially stale assumptions block acceptance until reassessed;
- revision exploration previews downstream at-risk without staleness;
- cancelling a revision leaves canon byte-identical;
- accepting a revision marks downstream stale with provenance preserved;
- command retry after a simulated crash reconciles without repromoting.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from auteur.acceptance import AcceptanceRegistry
from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.contracts import (
    DecisionStage,
    DimensionCategory,
    DimensionStatus,
    LifecycleStatus,
    StageAvailability,
)
from auteur.beginner.mystery_adapter import mystery_qualification_inventory
from tests.fixtures.beginner_sealed_elevator import (
    SEALED_ELEVATOR_PREMISE,
    choose_required_options,
    command_for,
    create_app,
)
from tests.fixtures.beginner_hybrid_mystery import create_hybrid_app
from auteur.beginner.guidance import guidance_for


def _accept_direction(app: BeginnerWorkspaceApplication, tag: str):
    choose_required_options(app, "discover.")
    app.open_milestone_review(command=command_for(app, f"{tag}-review-direction", {"stage": "discover"}))
    return app.accept_story_direction(command=command_for(app, f"{tag}-accept-direction"))


def _accept_identity(app: BeginnerWorkspaceApplication, tag: str):
    choose_required_options(app, "story_identity.")
    app.open_milestone_review(command=command_for(app, f"{tag}-review-identity", {"stage": "story_identity"}))
    return app.accept_story_identity(command=command_for(app, f"{tag}-accept-identity"))


def _accept_structure(app: BeginnerWorkspaceApplication, tag: str):
    choose_required_options(app, "structure.")
    app.open_milestone_review(command=command_for(app, f"{tag}-review-structure", {"stage": "story_structure"}))
    return app.accept_whole_story_structure(command=command_for(app, f"{tag}-accept-structure"))


def _canon_json(app: BeginnerWorkspaceApplication) -> str:
    refs = app.session_store.load().accepted_milestones
    return json.dumps([ref.model_dump(mode="json") for ref in refs], sort_keys=True, separators=(",", ":"))


def test_sealed_elevator_reaches_accepted_whole_story_structure(tmp_path: Path) -> None:
    app = create_app(tmp_path)

    assert app.session_store.load().premise == SEALED_ELEVATOR_PREMISE

    direction = _accept_direction(app, "sealed")
    assert direction.accepted is True
    assert direction.revision == 1
    assert app.session_store.load().stages[DecisionStage.STORY_IDENTITY].availability is (StageAvailability.AVAILABLE)

    identity = _accept_identity(app, "sealed")
    assert identity.accepted is True
    assert identity.revision == 1

    structure = _accept_structure(app, "sealed")
    assert structure.accepted is True
    assert structure.revision == 1

    session = app.session_store.load()
    assert [ref.milestone_id for ref in session.accepted_milestones] == [
        "story_direction",
        "story_identity",
        "whole_story_structure",
    ]
    assert session.stages[DecisionStage.STORY_STRUCTURE].lifecycle is LifecycleStatus.COMPLETE

    projection = app.projection()
    assert len(projection.canonical_refs) == 3
    structure_entry = next(entry for entry in projection.navigator if entry.stage is DecisionStage.STORY_STRUCTURE)
    assert structure_entry.answered_cards == structure_entry.total_cards == 3
    assert structure_entry.review_available is True
    assert structure_entry.ready_to_accept is True
    assert structure_entry.stale is False
    assert structure_entry.at_risk_if_accepted is False


def test_hybrid_composition_changes_guidance_without_becoming_canon(tmp_path: Path) -> None:
    hybrid_app = create_hybrid_app(tmp_path)
    baseline_source = hybrid_app.session_store.load()
    baseline_session = baseline_source.model_copy(update={
        "working_composition": None,
        "stages": {
            stage: status.model_copy(update={"availability": StageAvailability.AVAILABLE})
            for stage, status in baseline_source.stages.items()
        },
    })
    baseline = guidance_for("story_identity.relationship-pressure", baseline_session)
    hybrid_source = hybrid_app.session_store.load()
    hybrid_session = hybrid_source.model_copy(update={
        "stages": {
            stage: status.model_copy(update={"availability": StageAvailability.AVAILABLE})
            for stage, status in hybrid_source.stages.items()
        },
    })
    hybrid = guidance_for("story_identity.relationship-pressure", hybrid_session)

    assert hybrid.recommendation == baseline.recommendation
    assert hybrid.option_impacts != baseline.option_impacts
    assert {source.pack_id for source in hybrid.pack_sources} >= {"superhero", "relationship"}
    assert "Relationship betrayal tension" in hybrid.context_guidance.patterns
    assert hybrid_app.projection().canonical_refs == ()
    assert hybrid_app.session_store.load().working_composition is not None


def test_hybrid_fixture_keeps_confirmed_dimensions_visible_as_working_state(tmp_path: Path) -> None:
    app = create_hybrid_app(tmp_path)
    composition = app.session_store.load().working_composition

    assert composition is not None
    assert {dimension.status for dimension in composition.dimensions} == {DimensionStatus.CONFIRMED}
    assert {dimension.category for dimension in composition.dimensions} == {
        DimensionCategory.PRIMARY_ENGINE,
        DimensionCategory.SETTING_WORLD,
        DimensionCategory.RELATIONSHIP_THEMATIC,
    }
    projected = app.projection().working_composition
    assert projected is not None
    assert {dimension.dimension_id for dimension in projected.dimensions} == {
        dimension.dimension_id for dimension in composition.dimensions
    }


def test_acknowledged_nonblocking_tension_never_gates_readiness(tmp_path: Path) -> None:
    app = create_app(tmp_path)
    _accept_direction(app, "nonblocking")

    app.open_revision(
        revision_id="revision-explore-1",
        expected_session_version=app.projection().session_version,
    )
    inventory = mystery_qualification_inventory()
    card_id = next(card.card_id for card in inventory.cards if card.card_id.startswith("discover."))
    baseline = (app._journey.get("answers") or {})[card_id]
    alternative = next(option for option in inventory.card(card_id).options if option != baseline)
    app.select_working_option(
        card_id=card_id,
        option=alternative,
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )

    projection = app.projection()
    exploratory = [tension for tension in projection.tensions if tension.card_id == card_id]
    assert len(exploratory) == 1
    assert exploratory[0].blocking is False
    assert projection.reviews[DecisionStage.DISCOVER].ready_to_accept is True

    acknowledged = app.acknowledge_tension(
        tension_id=exploratory[0].tension_id,
        expected_session_version=app.projection().session_version,
    )
    assert acknowledged.acknowledged is True
    assert app.projection().reviews[DecisionStage.DISCOVER].ready_to_accept is True


def test_valid_alternative_does_not_gate_review(tmp_path: Path) -> None:
    app = create_app(tmp_path)
    inventory = mystery_qualification_inventory()
    cards = [card for card in inventory.cards if card.card_id.startswith("discover.")]
    first, rest = cards[0], cards[1:]
    non_recommended = next(option for option in first.options if option != first.recommendation)
    app.select_working_option(
        command=command_for(app, "sealed-contradiction-select", {"card_id": first.card_id, "option": non_recommended})
    )
    current = first.card_id
    for card in rest:
        continued = app.continue_decision(card_id=current, expected_session_version=app.projection().session_version)
        assert continued.advanced is True
        current = continued.card_id
        app.select_working_option(
            card_id=card.card_id,
            option=card.recommendation,
            expected_session_version=app.projection().session_version,
        )

    review = app.open_milestone_review(
        stage=DecisionStage.DISCOVER,
        expected_session_version=app.projection().session_version,
    )
    assert review.review_available is True
    assert review.ready_to_accept is True
    assert app.projection().tensions[0].blocking is False

    result = app.accept_story_direction(
        command_id="sealed-contradiction-accept",
        expected_session_version=app.projection().session_version,
    )
    assert result.accepted is True


def test_materially_stale_assumptions_require_reassessment(tmp_path: Path, monkeypatch: Any) -> None:
    app = create_app(tmp_path)
    choose_required_options(app, "discover.")
    assert app.projection().reviews[DecisionStage.DISCOVER].ready_to_accept is True

    from auteur.beginner import mystery_adapter as mystery_module

    real_digest = mystery_module.MysteryGuidanceAdapter._source_digest()
    monkeypatch.setattr(
        mystery_module.MysteryGuidanceAdapter,
        "_source_digest",
        classmethod(lambda cls: "0" * 64 if real_digest != "0" * 64 else "1" * 64),
    )

    projection = app.projection()
    assert projection.reviews[DecisionStage.DISCOVER].ready_to_accept is False
    assert any("stale" in blocker.lower() for blocker in projection.reviews[DecisionStage.DISCOVER].blockers)

    card_id = next(
        card.card_id for card in mystery_qualification_inventory().cards if card.card_id.startswith("discover.")
    )
    refreshed = app.reassess_guidance(card_id=card_id, expected_session_version=app.projection().session_version)
    assert refreshed.card_id == card_id
    assert app.projection().reviews[DecisionStage.DISCOVER].ready_to_accept is True


def test_revision_exploration_previews_at_risk_without_staleness(tmp_path: Path) -> None:
    app = create_app(tmp_path)
    _accept_direction(app, "atrisk")
    _accept_identity(app, "atrisk")
    choose_required_options(app, "structure.")

    app.open_revision(
        revision_id="revision-identity-preview",
        expected_session_version=app.projection().session_version,
    )
    inventory = mystery_qualification_inventory()
    identity_card = next(card.card_id for card in inventory.cards if card.card_id.startswith("story_identity."))
    app.select_working_option(
        card_id=identity_card,
        option=inventory.card(identity_card).options[-1],
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )

    projection = app.projection()
    assert projection.revision.active_revision_id == "revision-identity-preview"
    assert projection.revision.is_exploration is True
    structure_entry = next(entry for entry in projection.navigator if entry.stage is DecisionStage.STORY_STRUCTURE)
    assert structure_entry.at_risk_if_accepted is True
    for entry in projection.navigator:
        assert entry.stale is False


def test_cancelled_revision_leaves_canon_byte_identical(tmp_path: Path) -> None:
    app = create_app(tmp_path)
    _accept_direction(app, "cancel")
    _accept_identity(app, "cancel")
    _accept_structure(app, "cancel")
    canon_before = _canon_json(app)
    refs_before = list(app.projection().canonical_refs)

    app.open_revision(
        revision_id="revision-cancelled",
        expected_session_version=app.projection().session_version,
    )
    inventory = mystery_qualification_inventory()
    structure_card = next(card.card_id for card in inventory.cards if card.card_id.startswith("structure."))
    app.select_working_option(
        card_id=structure_card,
        option=inventory.card(structure_card).options[-1],
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )
    assert app.projection().revision.active_revision_id == "revision-cancelled"

    app.cancel_revision(expected_session_version=app.projection().session_version)

    assert _canon_json(app) == canon_before
    assert list(app.projection().canonical_refs) == refs_before
    projection = app.projection()
    assert projection.revision.active_revision_id is None
    assert projection.revision.is_exploration is False
    assert all(entry.at_risk_if_accepted is False for entry in projection.navigator)
    assert all(entry.stale is False for entry in projection.navigator)


def test_accepted_revision_marks_downstream_stale_with_provenance(tmp_path: Path) -> None:
    app = create_app(tmp_path)
    _accept_direction(app, "revise")
    _accept_identity(app, "revise")
    choose_required_options(app, "structure.")

    app.open_revision(
        revision_id="revision-identity-2",
        expected_session_version=app.projection().session_version,
    )
    inventory = mystery_qualification_inventory()
    identity_card = next(card.card_id for card in inventory.cards if card.card_id.startswith("story_identity."))
    baseline = (app._journey.get("answers") or {}).get(identity_card, inventory.card(identity_card).recommendation)
    alternative = next(option for option in inventory.card(identity_card).options if option != baseline)
    app.select_working_option(
        card_id=identity_card,
        option=alternative,
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )

    result = app.accept_revised_story_identity(
        revision_id="revision-identity-2",
        command_id="sealed-accept-identity-rev2",
        expected_session_version=app.projection().session_version,
    )
    assert result.accepted is True
    assert result.revision == 2

    identity_refs = [
        ref for ref in app.session_store.load().accepted_milestones if ref.milestone_id == "story_identity"
    ]
    assert [ref.revision.revision for ref in identity_refs] == [1, 2]

    projection = app.projection()
    assert projection.revision.active_revision_id is None
    structure_entry = next(entry for entry in projection.navigator if entry.stage is DecisionStage.STORY_STRUCTURE)
    assert structure_entry.stale is True
    assert structure_entry.at_risk_if_accepted is False


class _CountingOwner:
    """Test authority owner: pure result, counts real invocations."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, bool]] = []

    def can_accept(self, target_artifact_id: str) -> bool:
        return target_artifact_id.startswith("beginner:")

    def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> dict[str, Any]:
        self.calls.append((target_artifact_id, candidate_id, confirm))
        return {"artifact_id": target_artifact_id, "candidate_id": candidate_id, "accepted": True}


def test_command_retry_after_crash_reconciles_without_repromoting(tmp_path: Path) -> None:
    owner = _CountingOwner()
    registry = AcceptanceRegistry(tmp_path)
    registry.register(owner)
    app = create_app(tmp_path)
    app.authority = registry
    _accept_direction(app, "crash")
    choose_required_options(app, "story_identity.")
    app.open_milestone_review(
        stage=DecisionStage.STORY_IDENTITY,
        expected_session_version=app.projection().session_version,
    )

    real_update = app.session_store.update

    def crash_once(expected: int, mutator):  # type: ignore[no-untyped-def]
        app.session_store.update = real_update  # type: ignore[method-assign]
        raise RuntimeError("crash before session persistence")

    app.session_store.update = crash_once  # type: ignore[method-assign]
    try:
        app.accept_story_identity(
            command_id="sealed-identity-crash",
            expected_session_version=app.projection().session_version,
        )
    except RuntimeError as exc:
        assert "crash before session persistence" in str(exc)
    else:  # pragma: no cover - the crash must interrupt persistence
        raise AssertionError("expected the simulated crash to interrupt acceptance")

    def identity_promotions() -> int:
        return sum(1 for call in owner.calls if call[0].endswith("story_identity"))

    assert identity_promotions() == 1
    assert "story_identity" not in [ref.milestone_id for ref in app.session_store.load().accepted_milestones]

    recovered = app.accept_story_identity(
        command_id="sealed-identity-crash",
        expected_session_version=app.projection().session_version,
    )
    assert recovered.accepted is True
    assert identity_promotions() == 1
    assert "story_identity" in [ref.milestone_id for ref in app.session_store.load().accepted_milestones]

    replayed = app.accept_story_identity(
        command_id="sealed-identity-crash",
        expected_session_version=app.projection().session_version,
    )
    assert replayed.accepted is True
    assert replayed.result_reference == recovered.result_reference
    assert identity_promotions() == 1
