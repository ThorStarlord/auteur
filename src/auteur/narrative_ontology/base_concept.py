"""Base concept classes for the narrative ontology.

This module defines the foundational building blocks for representing narrative
concepts, their relationships, and validation rules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Relationship:
    """Represents a relationship between two narrative concepts.

    Attributes:
        source: The source concept name
        target: The target concept name
        cardinality: Relationship cardinality (one-to-one, one-to-many, many-to-many)
        description: Human-readable description of the relationship
        direction: "has" or "participates_in" or custom relationship type
    """

    source: str
    target: str
    cardinality: str
    description: str
    direction: str = "has"


@dataclass
class ValidationRule:
    """Represents a validation rule for a narrative concept.

    Attributes:
        rule_id: Unique identifier for the rule
        condition: Description of the condition being validated
        error_message: Message to show when validation fails
        applies_to: Which concepts this rule applies to
    """

    rule_id: str
    condition: str
    error_message: str
    applies_to: List[str] = field(default_factory=list)


@dataclass
class BaseConcept:
    """Base class for all narrative concepts in the ontology.

    A concept represents a kind of thing that exists in narrative (Character, Arc,
    Theme, etc.). Each concept has a definition, relationships to other concepts,
    and validation rules that constrain how it can be used.

    Attributes:
        name: The concept name (e.g., "Character", "Arc")
        definition: Human-readable definition of the concept
        category: The category this concept belongs to (base, genre-specific)
        parent_concepts: List of concepts this one inherits from or extends
        relationships: List of Relationship objects defining connections to other concepts
        validation_rules: List of ValidationRule objects that constrain this concept
        metadata: Additional metadata for the concept (e.g., theme sets for genres)
    """

    name: str
    definition: str
    category: str = "base"
    parent_concepts: List[str] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    validation_rules: List[ValidationRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to another concept.

        Args:
            relationship: The Relationship object to add
        """
        self.relationships.append(relationship)

    def add_validation_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule to this concept.

        Args:
            rule: The ValidationRule object to add
        """
        self.validation_rules.append(rule)

    def get_related_concepts(self) -> List[str]:
        """Get list of concepts this one relates to.

        Returns:
            List of related concept names
        """
        return [rel.target for rel in self.relationships]

    def get_validation_rules_for_concept(self, concept_name: str) -> List[ValidationRule]:
        """Get validation rules that apply to a specific concept.

        Args:
            concept_name: The name of the concept to check

        Returns:
            List of ValidationRule objects that apply to the concept
        """
        return [rule for rule in self.validation_rules if concept_name in rule.applies_to]

    def is_subtype_of(self, parent_name: str) -> bool:
        """Check if this concept is a subtype of another.

        Args:
            parent_name: The name of the potential parent concept

        Returns:
            True if this concept inherits from the parent
        """
        return parent_name in self.parent_concepts

    def to_dict(self) -> Dict[str, Any]:
        """Convert the concept to a dictionary representation.

        Returns:
            Dictionary representation of the concept
        """
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
