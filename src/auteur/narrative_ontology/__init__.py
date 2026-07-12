"""Narrative ontology module for defining narrative concepts and their relationships.

This module provides the foundational semantic layer that defines what narrative
concepts exist, their relationships, and validation rules. It answers: "What kinds
of things exist in narrative?" Not "how do we build stories?" but "what vocabulary
does story-building use?"
"""

from auteur.narrative_ontology.base_concept import BaseConcept, Relationship
from auteur.narrative_ontology.schema.ontology_types import (
    Concept,
    ValidationRule,
    GenreOntologyExtension,
)

__all__ = [
    "BaseConcept",
    "Relationship",
    "Concept",
    "ValidationRule",
    "GenreOntologyExtension",
]
