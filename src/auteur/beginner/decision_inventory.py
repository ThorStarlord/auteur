"""Bounded adaptive decision inventory for the rich beginner journey."""

from __future__ import annotations

from auteur.identity import StoryIdentity

from .architecture_models import (
    ArchitectureActivation,
    ArchitectureFacet,
    NarrativeArchitectureAnalysis,
)
from .contracts import SessionEnvelope
from .guidance import QualificationInventory, QualificationStage
from .generic_structure import GenericStructureAdapter
from .mystery_adapter import MysteryGuidanceAdapter


def _mystery_is_material(
    analysis: NarrativeArchitectureAnalysis,
    accepted_identity: StoryIdentity | None,
) -> bool:
    if accepted_identity is not None and accepted_identity.story_type.genre.value == "mystery":
        return True
    return any(
        component.activation is ArchitectureActivation.ACTIVE
        and (
            (
                component.facet is ArchitectureFacet.GENRE_CONSTELLATION
                and (component.normalized_concept or component.label.casefold()) == "mystery"
            )
            or (
                component.facet is ArchitectureFacet.NARRATIVE_ENGINE
                and "investigation" in component.label.casefold()
            )
        )
        for component in analysis.components
    )


def structure_inventory_for(
    *,
    session: SessionEnvelope,
    analysis: NarrativeArchitectureAnalysis,
    accepted_identity: StoryIdentity | None,
) -> QualificationInventory:
    """Return Structure cards: curated Mystery when material, else bounded generic."""
    del session
    if not _mystery_is_material(analysis, accepted_identity):
        return GenericStructureAdapter.inventory()
    return QualificationInventory(
        cards=tuple(
            card
            for card in MysteryGuidanceAdapter.inventory().cards
            if card.stage is QualificationStage.STRUCTURE
        )
    )
