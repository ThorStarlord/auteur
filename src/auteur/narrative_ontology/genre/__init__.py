"""Genre-specific narrative ontologies for netorare, mystery, and gentle femdom.

This package contains genre-specific extensions to the base narrative ontology,
defining concepts, relationships, and validation rules unique to each genre.
"""

from auteur.narrative_ontology.genre.netorara_ontology import (
    NetorareOntology,
    CuckoldryArc,
    HumiliationProgression,
    ConsentBoundary,
)
from auteur.narrative_ontology.genre.mystery_ontology import (
    MysteryOntology,
    InvestigationArc,
    Clue,
    RedHerring,
)
from auteur.narrative_ontology.genre.gentlefemdom_ontology import (
    GentleFemdomOntology,
    AuthorityArc,
    SurrenderBeat,
    TrustCheckpoint,
)

__all__ = [
    "NetorareOntology",
    "CuckoldryArc",
    "HumiliationProgression",
    "ConsentBoundary",
    "MysteryOntology",
    "InvestigationArc",
    "Clue",
    "RedHerring",
    "GentleFemdomOntology",
    "AuthorityArc",
    "SurrenderBeat",
    "TrustCheckpoint",
]
