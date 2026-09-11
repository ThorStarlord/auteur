"""Legacy Python genre-ontology compatibility surfaces.

Production Narrative Ontology V2 discovery and validation is data-driven through
packaged ``src/auteur/data/ontology/*_ontology.yaml`` resources and
``OntologyRegistry``.  The classes exported here remain for historical callers
and tests; they are not independent semantic authorities and new genre ontology
work must not add a parallel Python registry.
"""

from auteur.narrative_ontology.genre.netorare_ontology import (
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
