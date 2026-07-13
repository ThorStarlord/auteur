"""Narrative orchestration for Structure composition and integration.

This package defines ownership, references, validation, and orchestration across
Book, Sequence, Chapter, and Arc outlines. It transforms Layer 2 from disconnected
schemas into one coherent narrative structure system.
"""

# Ownership (Task 1) - always available
from auteur.narrative_orchestration.schema.ownership import (
    OwnershipRule,
    OwnershipMapping,
    ArtifactType,
    StructuralFact,
)

__all__ = [
    "OwnershipRule",
    "OwnershipMapping",
    "ArtifactType",
    "StructuralFact",
]
