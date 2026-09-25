"""Bounded, genre-neutral Structure inventory for the deterministic fallback.

Deterministic Curated Mode uses these three structure decisions when the working
architecture has no Mystery material. They are a small curated set, not a
per-genre taxonomy.
"""

from __future__ import annotations

import hashlib
import json

from auteur.story_design_packs.models import PackProvenance

from .guidance import (
    EvidenceReference,
    QualificationCard,
    QualificationInventory,
    QualificationStage,
    register_evidence_source,
    register_guidance_adapter,
)

GENERIC_STRUCTURE_CARD_IDS = (
    "structure.escalation-pattern",
    "structure.reversal-placement",
    "structure.resolution-shape",
)

_GENERIC_STRUCTURE_RULE_IDS = {
    "generic.structure.escalation",
    "generic.structure.reversal",
    "generic.structure.resolution",
}


class _GenericStructureEvidenceSource:
    def validate(self, reference: EvidenceReference) -> None:
        if reference.phase is not None or reference.field is not None:
            raise ValueError("GenericStructure evidence cannot cite template metadata")
        if reference.rule_id not in _GENERIC_STRUCTURE_RULE_IDS:
            raise ValueError("unknown GenericStructure rule")


register_evidence_source("GenericStructure", _GenericStructureEvidenceSource())


def _evidence(
    rule_id: str,
    options: tuple[str, ...],
    recommendation: str,
) -> tuple[EvidenceReference, ...]:
    return (
        EvidenceReference(claim="decision", source="GenericStructure", rule_id=rule_id),
        EvidenceReference(
            claim="recommendation",
            source="GenericStructure",
            rule_id=rule_id,
            option_labels=(recommendation,),
        ),
        EvidenceReference(
            claim="option",
            source="GenericStructure",
            rule_id=rule_id,
            option_labels=options,
        ),
        EvidenceReference(claim="consequence", source="GenericStructure", rule_id=rule_id),
    )


_GENERIC_CARDS: tuple[QualificationCard, ...] = (
    QualificationCard(
        card_id="structure.escalation-pattern",
        stage=QualificationStage.STRUCTURE,
        title="Escalation pattern",
        question="How should the story's pressure escalate?",
        source_subject="Generic structure: escalation",
        options=(
            "Steadily rising pressure",
            "Escalating bursts with setbacks",
            "Late concentrated pressure",
        ),
        recommendation="Steadily rising pressure",
        narrative_principle="Escalation determines how the central pressure compounds toward the climax.",
        warnings_or_tensions=(
            "Steady escalation keeps the pressure legible.",
            "Bursts or late concentration change how the middle is paced.",
        ),
        downstream_consequences=(
            "The escalation pattern determines when and how the central pressure intensifies.",
        ),
        evidence_references=_evidence(
            "generic.structure.escalation",
            (
                "Steadily rising pressure",
                "Escalating bursts with setbacks",
                "Late concentrated pressure",
            ),
            "Steadily rising pressure",
        ),
    ),
    QualificationCard(
        card_id="structure.reversal-placement",
        stage=QualificationStage.STRUCTURE,
        title="Reversal placement",
        question="Where should the story's major reversal land?",
        source_subject="Generic structure: reversal",
        options=("Midpoint reversal", "Reversal near the climax", "Many small reversals"),
        recommendation="Midpoint reversal",
        narrative_principle="Reversal placement decides when the story reframes what the protagonist believed.",
        warnings_or_tensions=(
            "A midpoint reversal reorients the second half.",
            "A late or distributed reversal changes the story's momentum differently.",
        ),
        downstream_consequences=(
            "The reversal's placement determines when earlier assumptions are reframed.",
        ),
        evidence_references=_evidence(
            "generic.structure.reversal",
            ("Midpoint reversal", "Reversal near the climax", "Many small reversals"),
            "Midpoint reversal",
        ),
    ),
    QualificationCard(
        card_id="structure.resolution-shape",
        stage=QualificationStage.STRUCTURE,
        title="Resolution shape",
        question="What shape should the resolution take?",
        source_subject="Generic structure: resolution",
        options=("Resolved with cost", "Ambiguous but earned", "Clear and restorative"),
        recommendation="Resolved with cost",
        narrative_principle="The resolution shape decides what the story's outcome costs and confirms.",
        warnings_or_tensions=(
            "A costly resolution keeps the pressure meaningful.",
            "Ambiguity or restoration change what the ending promises.",
        ),
        downstream_consequences=(
            "The resolution shape determines what the ending settles and what it leaves open.",
        ),
        evidence_references=_evidence(
            "generic.structure.resolution",
            ("Resolved with cost", "Ambiguous but earned", "Clear and restorative"),
            "Resolved with cost",
        ),
    ),
)

_CANONICAL_CARD_DEFINITIONS = {
    card.card_id: json.dumps(card.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    for card in _GENERIC_CARDS
}


class GenericStructureAdapter:
    """Bounded genre-neutral Structure guidance for Deterministic Curated Mode."""

    genre = "generic"

    @staticmethod
    def inventory() -> QualificationInventory:
        return QualificationInventory(cards=_GENERIC_CARDS)

    @staticmethod
    def validate_inventory(inventory: QualificationInventory) -> None:
        for card in inventory.cards:
            if card.card_id not in GENERIC_STRUCTURE_CARD_IDS:
                raise ValueError(f"not a generic structure card: {card.card_id}")
            expected = _CANONICAL_CARD_DEFINITIONS.get(card.card_id)
            actual = json.dumps(card.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
            if expected != actual:
                raise ValueError(f"generic structure card does not match definition: {card.card_id}")

    @staticmethod
    def pack_sources() -> tuple[PackProvenance, ...]:
        return (
            PackProvenance(
                pack_id="generic-structure",
                version="curated",
                content_hash=hashlib.sha256(
                    json.dumps(_CANONICAL_CARD_DEFINITIONS, sort_keys=True).encode("utf-8")
                ).hexdigest(),
            ),
        )

    @staticmethod
    def tutor_session_fingerprints() -> dict[str, str]:
        digest = hashlib.sha256(
            json.dumps(_CANONICAL_CARD_DEFINITIONS, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return {"GenericStructure": digest}


def register_generic_structure_adapter() -> None:
    register_guidance_adapter(GenericStructureAdapter())
