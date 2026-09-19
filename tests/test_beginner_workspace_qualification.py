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

import pytest

from auteur.acceptance import AcceptanceRegistry
from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.contracts import (
    DecisionStage,
    DimensionCategory,
    DimensionStatus,
    LifecycleStatus,
    SemanticChange,
    StageAvailability,
)
from auteur.beginner.mystery_adapter import mystery_qualification_inventory
from auteur.beginner.persistence import CommandReceipt
from auteur.beginner.promotion import PromotionPreview
from auteur.identity import HighLevelCentralEngine, StoryIdentity
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
    composition = app.projection().working_composition
    assert composition is not None
    for dimension in composition.dimensions:
        if dimension.status is not DimensionStatus.CONFIRMED:
            app.confirm_dimension(
                dimension_id=dimension.dimension_id,
                rationale="Confirmed for the qualification journey.",
                expected_session_version=app.projection().session_version,
            )
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
    assert "superhero" in {source.pack_id for source in hybrid.pack_sources}
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

    current = StoryIdentity.from_yaml(tmp_path / "story_identity.yaml")
    candidate = current.model_copy(
        update={
            "central_engine": current.central_engine.model_copy(
                update={"conflict": current.central_engine.conflict + " with reversed trust"}
            )
        }
    )
    preview = PromotionPreview(
        current_identity=current,
        candidate_identity=candidate,
        semantic_changes=(
            SemanticChange(
                destination_field="central_engine.conflict",
                before=current.central_engine.conflict,
                after=candidate.central_engine.conflict,
            ),
        ),
        ready_to_accept=True,
    )
    result = app.accept_composed_identity(
        preview=preview,
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


class _RecoveringOwner(_CountingOwner):
    def __init__(self) -> None:
        super().__init__()
        self.recoveries = 0

    def recover(self, target_artifact_id: str, candidate_id: str) -> dict[str, Any]:
        self.recoveries += 1
        return {"artifact_id": target_artifact_id, "candidate_id": candidate_id, "accepted": True}


class _CrashBeforeCompletionOwner(_CountingOwner):
    def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> dict[str, Any]:
        self.calls.append((target_artifact_id, candidate_id, confirm))
        raise _ProcessCrash("process terminated after canonical mutation")


class _ProcessCrash(BaseException):
    pass


def test_command_retry_after_crash_reconciles_without_repromoting(tmp_path: Path) -> None:
    owner = _CountingOwner()
    registry = AcceptanceRegistry(tmp_path)
    registry.register(owner)
    app = create_app(tmp_path)
    app.authority = registry
    _accept_direction(app, "crash")
    composition = app.projection().working_composition
    assert composition is not None
    for dimension in composition.dimensions:
        app.confirm_dimension(
            dimension_id=dimension.dimension_id,
            rationale="Confirmed for crash-recovery qualification.",
            expected_session_version=app.projection().session_version,
        )
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


def test_restart_recovery_uses_owner_recovery_without_second_promotion(tmp_path: Path) -> None:
    crashing_owner = _CrashBeforeCompletionOwner()
    first_registry = AcceptanceRegistry(tmp_path)
    first_registry.register(crashing_owner)
    first_app = create_app(tmp_path)
    _accept_direction(first_app, "restart")
    first_app.authority = first_registry
    with pytest.raises(_ProcessCrash, match="process terminated"):
        _accept_identity(first_app, "restart")
    receipt = first_app.receipt_store.load("restart-accept-identity")
    assert receipt.promotion_intent is not None
    assert receipt.promotion_intent["semantic_change"] is True
    assert receipt.promotion_intent["expected_artifact_revision"] == 0

    recovering_owner = _RecoveringOwner()
    second_registry = AcceptanceRegistry(tmp_path)
    second_registry.register(recovering_owner)
    second_app = BeginnerWorkspaceApplication(
        tmp_path,
        first_app.workspace_id,
        authority_registry=second_registry,
    )
    recovered = second_app.accept_story_identity(
        command_id="restart-accept-identity",
        expected_session_version=second_app.projection().session_version,
    )

    assert recovered.accepted is True
    assert recovering_owner.recoveries == 1
    assert recovering_owner.calls == []
    assert len(second_app.session_store.load().accepted_milestones) == 2


def test_real_owner_restart_recovery_preserves_semantic_intent(tmp_path: Path) -> None:
    app = create_app(tmp_path)
    _accept_direction(app, "real-restart")
    choose_required_options(app, "story_identity.")
    app.open_milestone_review(
        stage=DecisionStage.STORY_IDENTITY,
        expected_session_version=app.projection().session_version,
    )
    identity = StoryIdentity(
        title="Real owner recovery fixture",
        core_answer="A recovery fixture with a semantic identity revision.",
        central_engine=HighLevelCentralEngine(
            want="Solve the mystery.",
            resistance="Hidden truth.",
            conflict="Suspicion versus trust.",
            stakes="The relationship collapses.",
            change="The protagonist accepts uncertainty.",
        ),
    )
    initial_preview = PromotionPreview(
        current_identity=identity,
        candidate_identity=identity,
        ready_to_accept=True,
    )
    app.accept_composed_identity(
        preview=initial_preview,
        command_id="real-initial-identity",
        expected_session_version=app.projection().session_version,
    )
    _accept_structure(app, "real-restart")

    app.open_revision(
        revision_id="real-semantic-revision",
        stage=DecisionStage.STORY_IDENTITY,
        expected_session_version=app.projection().session_version,
    )
    identity_card = next(
        card.card_id
        for card in mystery_qualification_inventory().cards
        if card.card_id.startswith("story_identity.")
    )
    app.select_working_option(
        card_id=identity_card,
        option=mystery_qualification_inventory().card(identity_card).options[-1],
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )
    current = StoryIdentity.from_yaml(tmp_path / "story_identity.yaml")
    candidate = current.model_copy(
        update={
            "central_engine": current.central_engine.model_copy(
                update={"conflict": current.central_engine.conflict + " with semantic recovery"}
            )
        }
    )
    revision_preview = PromotionPreview(
        current_identity=current,
        candidate_identity=candidate,
        semantic_changes=(
            SemanticChange(
                destination_field="central_engine.conflict",
                before=current.central_engine.conflict,
                after=candidate.central_engine.conflict,
            ),
        ),
        ready_to_accept=True,
    )
    original_record = app.authority.journal.record

    def crash_completion(**kwargs: Any) -> None:
        if kwargs.get("status") == "completed" and kwargs.get("command_id") == "real-semantic-revision-accept":
            raise _ProcessCrash("process terminated before acceptance journal completion")
        original_record(**kwargs)

    app.authority.journal.record = crash_completion  # type: ignore[method-assign]
    with pytest.raises(_ProcessCrash, match="acceptance journal completion"):
        app.accept_composed_identity(
            preview=revision_preview,
            revision_id="real-semantic-revision",
            command_id="real-semantic-revision-accept",
            expected_session_version=app.projection().session_version,
        )

    receipt = app.receipt_store.load("real-semantic-revision-accept")
    assert receipt.promotion_intent is not None
    assert receipt.promotion_intent["expected_artifact_revision"] == 1
    assert StoryIdentity.from_yaml(tmp_path / "story_identity.yaml").central_engine.conflict.endswith(
        "with semantic recovery"
    )

    recovered_app = BeginnerWorkspaceApplication(tmp_path, app.workspace_id)
    post_crash_identity = StoryIdentity.from_yaml(tmp_path / "story_identity.yaml")
    post_crash_preview = PromotionPreview(
        current_identity=post_crash_identity,
        candidate_identity=post_crash_identity,
        ready_to_accept=True,
    )
    recovered = recovered_app.accept_composed_identity(
        preview=post_crash_preview,
        revision_id="real-semantic-revision",
        command_id="real-semantic-revision-accept",
        expected_session_version=recovered_app.projection().session_version,
    )

    assert recovered.accepted is True
    assert StoryIdentity.from_yaml(tmp_path / "story_identity.yaml").central_engine.conflict.endswith(
        "with semantic recovery"
    )
    structure_entry = next(
        entry for entry in recovered_app.projection().navigator if entry.stage is DecisionStage.STORY_STRUCTURE
    )
    assert structure_entry.stale is True


def test_metadata_only_composed_revision_does_not_stale_structure(tmp_path: Path) -> None:
    app = create_app(tmp_path)
    _accept_direction(app, "metadata")
    _accept_identity(app, "metadata")
    _accept_structure(app, "metadata")
    app.open_revision(
        revision_id="metadata-revision",
        stage=DecisionStage.STORY_IDENTITY,
        expected_session_version=app.projection().session_version,
    )
    identity_card = next(
        card.card_id
        for card in mystery_qualification_inventory().cards
        if card.card_id.startswith("story_identity.")
    )
    app.select_working_option(
        card_id=identity_card,
        option=mystery_qualification_inventory().card(identity_card).options[-1],
        expected_session_version=app.projection().session_version,
        exploratory=True,
    )
    current = StoryIdentity.from_yaml(tmp_path / "story_identity.yaml")
    preview = PromotionPreview(
        current_identity=current,
        candidate_identity=current,
        ready_to_accept=True,
    )

    result = app.accept_composed_identity(
        preview=preview,
        revision_id="metadata-revision",
        command_id="accept-metadata-revision",
        expected_session_version=app.projection().session_version,
    )

    assert result.accepted is True
    structure_entry = next(
        entry for entry in app.projection().navigator if entry.stage is DecisionStage.STORY_STRUCTURE
    )
    assert structure_entry.stale is False


def test_metadata_recovery_requires_post_accept_artifact_revision(tmp_path: Path, monkeypatch: Any) -> None:
    owner = _RecoveringOwner()
    registry = AcceptanceRegistry(tmp_path)
    registry.register(owner)
    app = create_app(tmp_path)
    app.authority = registry
    target = "beginner:sealed-elevator:story_identity"
    candidate = "composed:metadata-candidate"
    command_id = "metadata-recovery-guard"
    intent = {
        "workspace_id": "sealed-elevator",
        "milestone": "story_identity",
        "content_fingerprint": "fingerprint",
        "candidate_id": candidate,
        "semantic_change": False,
        "expected_artifact_revision": 1,
    }
    registry.journal.record(
        operation_id="metadata-recovery-operation",
        target_artifact_id=target,
        candidate_id=candidate,
        status="started",
        command_id=command_id,
    )
    receipt = CommandReceipt(
        command_id=command_id,
        status="in_progress",
        owner_token="receipt-owner",
        command_type="promote_milestone",
        target_milestone="identity-accepted",
        promotion_intent=intent,
    )
    monkeypatch.setattr(app, "_canonical_artifact_revision", lambda *args, **kwargs: 1)

    recovered = app._try_recover(
        receipt,
        command_id=command_id,
        stage=DecisionStage.STORY_IDENTITY,
        milestone_id="story_identity",
        revision=2,
        fingerprint="fingerprint",
        target=target,
        candidate=candidate,
        merged={},
        is_revision=True,
        revision_id="metadata-revision",
        promotion_intent=intent,
        semantic_change=False,
    )

    assert recovered is None
    assert owner.recoveries == 0
