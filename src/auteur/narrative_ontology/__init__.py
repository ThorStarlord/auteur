"""Auteur Narrative Ontology.

Layer 0 is the shared semantic foundation used by Identity, Structure,
Realization, and Expression. It defines reusable concepts, relation vocabulary,
and deterministic invariants; it does not own accepted story state.
"""

from auteur.narrative_ontology.registry import OntologyIntegrityError, OntologyRegistry
from auteur.narrative_ontology.scope_vocabulary import (
    EntryKind,
    SegmentKind,
    semantic_scope_name,
)

__all__ = [
    "OntologyIntegrityError",
    "OntologyRegistry",
    "EntryKind",
    "SegmentKind",
    "semantic_scope_name",
]
