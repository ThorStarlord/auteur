"""Narrative ontology module for defining narrative concepts and their relationships.

This module provides the foundational semantic layer that defines what narrative
concepts exist, their relationships, and validation rules. It answers: "What kinds
of things exist in narrative?" Not "how do we build stories?" but "what vocabulary
does story-building use?"
"""

from auteur.narrative_ontology.base_concept import BaseConcept, Relationship
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
    "BaseConcept",
    "Relationship",
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
