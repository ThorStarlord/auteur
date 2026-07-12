"""Mystery-specific narrative ontology concepts.

This module defines genre-specific concepts for mystery narratives, including
investigation arcs, clues, and red herrings.
"""

from typing import List, Dict, Any
from auteur.narrative_ontology.base_concept import (
    BaseConcept,
    Relationship,
    ValidationRule,
)


class InvestigationArc(BaseConcept):
    """Represents an investigation progression through evidence gathering.

    An investigation arc is a narrative progression specific to mystery that tracks
    the systematic discovery and analysis of evidence leading toward revelation.

    Attributes:
        name: Always "Investigation Arc"
        definition: Definition of the concept
        investigation_type: Type of investigation (police, amateur, forensic, etc.)
        complexity_level: How complex the investigation is
    """

    def __init__(
        self,
        investigation_type: str = "general",
        complexity_level: int = 3,
    ):
        """Initialize an InvestigationArc concept.

        Args:
            investigation_type: Type of investigation (police, amateur, forensic, legal)
            complexity_level: Complexity level 1-5 (default: 3)
        """
        super().__init__(
            name="Investigation Arc",
            definition="A narrative arc progression tracking systematic evidence gathering and analysis leading toward revelation of the mystery.",
            category="genre-specific",
            parent_concepts=["Arc"],
            relationships=[
                Relationship(
                    source="Investigation Arc",
                    target="Character",
                    cardinality="many-to-one",
                    description="Investigation involves multiple characters with different roles",
                    direction="involves",
                ),
                Relationship(
                    source="Investigation Arc",
                    target="Clue",
                    cardinality="one-to-many",
                    description="Investigation arc contains multiple clues",
                    direction="contains",
                ),
                Relationship(
                    source="Investigation Arc",
                    target="Red Herring",
                    cardinality="one-to-many",
                    description="Investigation arc may include red herrings for misdirection",
                    direction="includes",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="mystery_investigation_clues",
                    condition="Investigation arc must contain at least one clue",
                    error_message="Investigation arc requires at least one piece of evidence",
                    applies_to=["Investigation Arc"],
                ),
                ValidationRule(
                    rule_id="mystery_investigation_progression",
                    condition="Clues must progress logically toward revelation",
                    error_message="Investigation clues must form a logical progression",
                    applies_to=["Investigation Arc"],
                ),
                ValidationRule(
                    rule_id="mystery_investigation_type_valid",
                    condition="Investigation type must be one of: police, amateur, forensic, legal, detective",
                    error_message="Invalid investigation type for mystery",
                    applies_to=["Investigation Arc"],
                ),
                ValidationRule(
                    rule_id="mystery_investigation_complexity",
                    condition="Complexity level must be between 1 and 5",
                    error_message="Investigation complexity must be in range 1-5",
                    applies_to=["Investigation Arc"],
                ),
            ],
            metadata={
                "genre": "mystery",
                "investigation_type": investigation_type,
                "complexity_level": complexity_level,
                "valid_types": ["police", "amateur", "forensic", "legal", "detective"],
                "emotional_core_alignment": ["investigation", "deception", "revelation", "doubt"],
            },
        )


class Clue(BaseConcept):
    """Represents a discrete piece of information in a mystery investigation.

    A clue is an individual piece of evidence that contributes to solving the
    mystery. Clues can be physical evidence, testimony, observations, or deductions.

    Attributes:
        name: Always "Clue"
        definition: Definition of the concept
        clue_type: Type of clue (physical, testimony, observation, deduction)
        significance: How important this clue is (major, minor, contextual)
    """

    def __init__(
        self,
        clue_type: str = "physical",
        significance: str = "minor",
    ):
        """Initialize a Clue concept.

        Args:
            clue_type: Type (physical, testimony, observation, deduction)
            significance: Importance level (major, minor, contextual)
        """
        super().__init__(
            name="Clue",
            definition="A discrete piece of information or evidence that contributes to solving the mystery, such as physical evidence, testimony, observations, or logical deductions.",
            category="genre-specific",
            parent_concepts=["Information"],
            relationships=[
                Relationship(
                    source="Clue",
                    target="Investigation Arc",
                    cardinality="many-to-one",
                    description="Part of investigation arc progression",
                    direction="part_of",
                ),
                Relationship(
                    source="Clue",
                    target="Character",
                    cardinality="many-to-many",
                    description="Clues connect characters to the investigation",
                    direction="involves",
                ),
                Relationship(
                    source="Clue",
                    target="Revelation",
                    cardinality="many-to-one",
                    description="Multiple clues lead to final revelation",
                    direction="leads_to",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="mystery_clue_type_valid",
                    condition="Clue type must be one of: physical, testimony, observation, deduction",
                    error_message="Invalid clue type for mystery",
                    applies_to=["Clue"],
                ),
                ValidationRule(
                    rule_id="mystery_clue_significance_valid",
                    condition="Significance must be one of: major, minor, contextual",
                    error_message="Invalid clue significance level",
                    applies_to=["Clue"],
                ),
                ValidationRule(
                    rule_id="mystery_clue_context",
                    condition="Each clue must have clear context in investigation",
                    error_message="Clue must have defined role in investigation arc",
                    applies_to=["Clue"],
                ),
            ],
            metadata={
                "genre": "mystery",
                "clue_type": clue_type,
                "significance": significance,
                "valid_types": ["physical", "testimony", "observation", "deduction"],
                "valid_significance": ["major", "minor", "contextual"],
            },
        )


class RedHerring(BaseConcept):
    """Represents a misdirection element in mystery narratives.

    A red herring is a piece of information that appears significant but leads
    away from the true solution, creating false theories and prolonging the mystery.

    Attributes:
        name: Always "Red Herring"
        definition: Definition of the concept
        deception_level: How convincing the red herring is (subtle, moderate, obvious)
        resolution_point: When/how the red herring is revealed as false
    """

    def __init__(
        self,
        deception_level: str = "moderate",
        resolution_point: str = "mid-story",
    ):
        """Initialize a RedHerring concept.

        Args:
            deception_level: How convincing (subtle, moderate, obvious)
            resolution_point: When revealed (early, mid-story, late, final)
        """
        super().__init__(
            name="Red Herring",
            definition="A piece of information that appears significant but leads away from the true solution, creating false theories and misdirection in the investigation.",
            category="genre-specific",
            parent_concepts=["Misdirection"],
            relationships=[
                Relationship(
                    source="Red Herring",
                    target="Investigation Arc",
                    cardinality="many-to-one",
                    description="Part of investigation arc structure",
                    direction="part_of",
                ),
                Relationship(
                    source="Red Herring",
                    target="Clue",
                    cardinality="one-to-one",
                    description="Often disguised as or presented alongside clues",
                    direction="mimics",
                ),
                Relationship(
                    source="Red Herring",
                    target="Character",
                    cardinality="many-to-many",
                    description="Can involve multiple characters in the deception",
                    direction="involves",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="mystery_red_herring_deception",
                    condition="Red herring deception level must be subtle, moderate, or obvious",
                    error_message="Invalid red herring deception level",
                    applies_to=["Red Herring"],
                ),
                ValidationRule(
                    rule_id="mystery_red_herring_resolution",
                    condition="Red herring must have defined resolution point",
                    error_message="Red herring must be resolved at specific narrative point",
                    applies_to=["Red Herring"],
                ),
                ValidationRule(
                    rule_id="mystery_red_herring_plausibility",
                    condition="Red herring must be plausible within mystery context",
                    error_message="Red herring must fit coherently into investigation",
                    applies_to=["Red Herring"],
                ),
                ValidationRule(
                    rule_id="mystery_red_herring_purpose",
                    condition="Each red herring must serve narrative purpose",
                    error_message="Red herring must meaningfully extend or complicate mystery",
                    applies_to=["Red Herring"],
                ),
            ],
            metadata={
                "genre": "mystery",
                "deception_level": deception_level,
                "resolution_point": resolution_point,
                "valid_deception_levels": ["subtle", "moderate", "obvious"],
                "valid_resolution_points": ["early", "mid-story", "late", "final"],
            },
        )


class MysteryOntology:
    """Container for all mystery-specific ontology concepts.

    This class provides a unified interface to access all mystery-specific
    concepts and their relationships.
    """

    def __init__(self):
        """Initialize the mystery ontology."""
        self.genre = "mystery"
        self.theme_set = [
            "investigation",
            "deception",
            "revelation",
            "conspiracy",
            "doubt",
        ]

        # Instantiate all genre-specific concepts
        self.investigation_arc = InvestigationArc()
        self.clue = Clue()
        self.red_herring = RedHerring()

        # Store all concepts for easy iteration
        self.concepts = {
            "Investigation Arc": self.investigation_arc,
            "Clue": self.clue,
            "Red Herring": self.red_herring,
        }

    def get_concept(self, concept_name: str) -> BaseConcept:
        """Get a concept by name.

        Args:
            concept_name: The name of the concept

        Returns:
            The BaseConcept object

        Raises:
            KeyError: If concept not found in mystery ontology
        """
        return self.concepts[concept_name]

    def get_all_concepts(self) -> Dict[str, BaseConcept]:
        """Get all concepts in the mystery ontology.

        Returns:
            Dictionary mapping concept names to BaseConcept objects
        """
        return self.concepts.copy()

    def get_concepts_by_category(self, category: str) -> Dict[str, BaseConcept]:
        """Get all concepts in a specific category.

        Args:
            category: The category to filter by

        Returns:
            Dictionary of concepts in the specified category
        """
        return {
            name: concept
            for name, concept in self.concepts.items()
            if concept.category == category
        }

    def validate_concept(self, concept_name: str) -> bool:
        """Check if a concept is valid in mystery ontology.

        Args:
            concept_name: The concept to validate

        Returns:
            True if concept exists in mystery ontology
        """
        return concept_name in self.concepts

    def get_theme_set(self) -> List[str]:
        """Get the theme set for mystery genre.

        Returns:
            List of themes for mystery
        """
        return self.theme_set.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire ontology to a dictionary representation.

        Returns:
            Dictionary representation of the mystery ontology
        """
        return {
            "genre": self.genre,
            "theme_set": self.theme_set,
            "concepts": {name: concept.to_dict() for name, concept in self.concepts.items()},
        }
