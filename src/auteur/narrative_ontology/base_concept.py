"""Legacy dataclass compatibility model for narrative ontology concepts.

Narrative Ontology V2 uses the Pydantic models in ``schema.ontology_types`` and
the YAML-backed ``OntologyRegistry`` as the production semantic path.  These
dataclasses remain only so historical genre modules and external callers can
continue to construct the older object shape during the compatibility window.
They are not an independent ontology source and must not be used to introduce
new canonical concept definitions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Relationship:
    """Legacy relationship object retained for compatibility.

    New ontology vocabulary should use ``schema.ontology_types.Relationship``
and, when applicable, a registered ``RelationType`` id.
    """

    source: str
    target: str
    cardinality: str
    description: str
    direction: str = "has"


@dataclass
class ValidationRule:
    """Legacy free-text validation-rule object retained for compatibility.

    Conditions stored here are descriptive only. Production deterministic rule
    execution is owned by ``OntologyValidator`` and named V2 executors.
    """

    rule_id: str
    condition: str
    error_message: str
    applies_to: List[str] = field(default_factory=list)


@dataclass
class BaseConcept:
    """Legacy concept shape retained for historical callers/tests.

    The canonical semantic definition of shipped concepts lives under
    ``src/auteur/data/ontology/``. Mutating one of these objects does not alter
    the V2 registry or any accepted narrative authority.
    """

    name: str
    definition: str
    category: str = "base"
    parent_concepts: List[str] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    validation_rules: List[ValidationRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_relationship(self, relationship: Relationship) -> None:
        self.relationships.append(relationship)

    def add_validation_rule(self, rule: ValidationRule) -> None:
        self.validation_rules.append(rule)

    def get_related_concepts(self) -> List[str]:
        return [rel.target for rel in self.relationships]

    def get_validation_rules_for_concept(self, concept_name: str) -> List[ValidationRule]:
        return [rule for rule in self.validation_rules if concept_name in rule.applies_to]

    def is_subtype_of(self, parent_name: str) -> bool:
        return parent_name in self.parent_concepts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "definition": self.definition,
            "category": self.category,
            "parent_concepts": self.parent_concepts,
            "relationships": [
                {
                    "source": rel.source,
                    "target": rel.target,
                    "cardinality": rel.cardinality,
                    "description": rel.description,
                    "direction": rel.direction,
                }
                for rel in self.relationships
            ],
            "validation_rules": [
                {
                    "rule_id": rule.rule_id,
                    "condition": rule.condition,
                    "error_message": rule.error_message,
                    "applies_to": rule.applies_to,
                }
                for rule in self.validation_rules
            ],
            "metadata": self.metadata,
        }
