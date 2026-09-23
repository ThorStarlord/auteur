from __future__ import annotations

from auteur.beginner.architecture_analysis import DeterministicArchitectureAnalyzer
from auteur.beginner.contracts import (
    DecisionStage,
    LifecycleStatus,
    SessionEnvelope,
    StageAvailability,
    StageStatus,
)
from auteur.beginner.decision_inventory import structure_inventory_for
from auteur.beginner.generic_structure import GENERIC_STRUCTURE_CARD_IDS
from auteur.beginner.guidance import guidance_for, guidance_source_fingerprints


def _analysis(premise: str):
    return DeterministicArchitectureAnalyzer().analyze(premise=premise, source_provenance=())


def test_generic_structure_inventory_used_when_mystery_not_material() -> None:
    analysis = _analysis("Two rival pastry chefs fall in love while saving a bakery.")
    inventory = structure_inventory_for(session=None, analysis=analysis, accepted_identity=None)
    ids = {card.card_id for card in inventory.cards}
    assert ids == set(GENERIC_STRUCTURE_CARD_IDS)


def test_mystery_structure_inventory_still_used_when_mystery_material() -> None:
    analysis = _analysis("A detective investigates a locked room murder.")
    inventory = structure_inventory_for(session=None, analysis=analysis, accepted_identity=None)
    ids = {card.card_id for card in inventory.cards}
    assert "structure.final-revelation" in ids
    assert ids.isdisjoint(GENERIC_STRUCTURE_CARD_IDS)


def _structure_ready_session() -> SessionEnvelope:
    session = SessionEnvelope.new("project-1", "mystery", "Two rival pastry chefs fall in love.")
    stages = dict(session.stages)
    stages[DecisionStage.STORY_STRUCTURE] = StageStatus(
        stage=DecisionStage.STORY_STRUCTURE,
        lifecycle=LifecycleStatus.WORKING,
        availability=StageAvailability.AVAILABLE,
    )
    return session.model_copy(update={"stages": stages})


def test_guidance_for_generic_structure_card() -> None:
    guidance = guidance_for("structure.escalation-pattern", _structure_ready_session())
    assert guidance.card_id == "structure.escalation-pattern"
    assert guidance.authority_status == "DERIVED / NOT CANON"
    assert guidance.recommendation in guidance.alternatives or guidance.recommendation


def test_guidance_source_fingerprints_include_generic_and_mystery() -> None:
    fingerprints = guidance_source_fingerprints()
    assert "GenericStructure" in fingerprints
    assert "HowdunitTemplate" in fingerprints
