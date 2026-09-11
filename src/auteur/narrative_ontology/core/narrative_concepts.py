"""Compatibility facade for the historical twelve Layer-0 concepts.

The canonical definitions live in ``src/auteur/data/ontology/base_ontology.yaml``.
This module preserves the original public constants without maintaining a
second Python copy of ontology definitions. A narrow projection preserves two
legacy API observations (three historical genre tags and Setup's one-to-one
cardinality) while the V2 registry exposes the reconciled canonical semantics.
"""

from __future__ import annotations

from auteur.narrative_ontology.loader.ontology_loader import OntologyLoader
from auteur.narrative_ontology.schema.ontology_types import Concept


_loader = OntologyLoader()
_LEGACY_GENRES = ["netorare", "mystery", "gentlefemdom"]


def _legacy_projection(name: str, declaration: dict) -> Concept:
    """Project canonical YAML into the historical public-object contract.

    New runtime code must use ``OntologyRegistry``. This adapter exists solely
    so older callers/tests are not forced through a breaking migration in the
    same release as the source-of-truth consolidation.
    """

    concept = Concept.model_validate(declaration)
    rules = [
        rule.model_copy(update={"applies_to": list(_LEGACY_GENRES)})
        if not rule.applies_to
        else rule
        for rule in concept.validation_rules
    ]
    relationships = concept.relationships
    if name == "Setup":
        relationships = [
            relation.model_copy(update={"cardinality": "one-to-one"})
            if relation.target_concept == "Payoff"
            else relation
            for relation in relationships
        ]
    return concept.model_copy(
        update={"validation_rules": rules, "relationships": relationships}
    )


# Intentionally limited to the historical compatibility core. Modern V2
# vocabulary is available through OntologyRegistry / OntologyLoader's core view.
ALL_CONCEPTS: dict[str, Concept] = {
    name: _legacy_projection(name, declaration)
    for name, declaration in _loader.load_base_ontology().items()
}

CHARACTER = ALL_CONCEPTS["Character"]
ARC = ALL_CONCEPTS["Arc"]
THEME = ALL_CONCEPTS["Theme"]
GOAL = ALL_CONCEPTS["Goal"]
CONFLICT = ALL_CONCEPTS["Conflict"]
PAYOFF = ALL_CONCEPTS["Payoff"]
SYMBOL = ALL_CONCEPTS["Symbol"]
RELATIONSHIP_CONCEPT = ALL_CONCEPTS["Relationship"]
BEAT = ALL_CONCEPTS["Beat"]
SETUP = ALL_CONCEPTS["Setup"]
REVELATION = ALL_CONCEPTS["Revelation"]
REVERSAL = ALL_CONCEPTS["Reversal"]

CHARACTER_RULES = CHARACTER.validation_rules
ARC_RULES = ARC.validation_rules
THEME_RULES = THEME.validation_rules
GOAL_RULES = GOAL.validation_rules
CONFLICT_RULES = CONFLICT.validation_rules
PAYOFF_RULES = PAYOFF.validation_rules
SYMBOL_RULES = SYMBOL.validation_rules
RELATIONSHIP_RULES = RELATIONSHIP_CONCEPT.validation_rules
BEAT_RULES = BEAT.validation_rules
SETUP_RULES = SETUP.validation_rules
REVELATION_RULES = REVELATION.validation_rules
REVERSAL_RULES = REVERSAL.validation_rules

CHARACTER_RELATIONSHIPS = CHARACTER.relationships
ARC_RELATIONSHIPS = ARC.relationships
THEME_RELATIONSHIPS = THEME.relationships
GOAL_RELATIONSHIPS = GOAL.relationships
CONFLICT_RELATIONSHIPS = CONFLICT.relationships
PAYOFF_RELATIONSHIPS = PAYOFF.relationships
SYMBOL_RELATIONSHIPS = SYMBOL.relationships
RELATIONSHIP_CONCEPT_RELATIONSHIPS = RELATIONSHIP_CONCEPT.relationships
BEAT_RELATIONSHIPS = BEAT.relationships
SETUP_RELATIONSHIPS = SETUP.relationships
REVELATION_RELATIONSHIPS = REVELATION.relationships
REVERSAL_RELATIONSHIPS = REVERSAL.relationships


def get_concept(name: str) -> Concept:
    """Return one historical base concept by case-sensitive canonical name."""

    try:
        return ALL_CONCEPTS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown narrative concept: {name}") from exc
