"""Netorare-specific narrative ontology concepts.

This module defines genre-specific concepts for netorare narratives, including
cuckoldry arcs, humiliation progressions, and consent boundaries.
"""

from typing import List, Dict, Any
from auteur.narrative_ontology.base_concept import (
    BaseConcept,
    Relationship,
    ValidationRule,
)


class CuckoldryArc(BaseConcept):
    """Represents a cuckoldry arc progression through humiliation/acceptance.

    A cuckoldry arc is a narrative progression specific to netorare that tracks
    the emotional and psychological journey through stages of revelation,
    humiliation, and potential acceptance or resolution.

    Attributes:
        name: Always "Cuckoldry Arc"
        definition: Definition of the concept
        stages: List of progression stages (revelation, humiliation, acceptance)
        intensity_progression: How intensity escalates through stages
    """

    def __init__(
        self,
        stages: List[str] = None,
        intensity_progression: str = "escalating",
    ):
        """Initialize a CuckoldryArc concept.

        Args:
            stages: List of progression stages (default: revelation, humiliation, acceptance)
            intensity_progression: How intensity changes (escalating, cyclical, plateau)
        """
        if stages is None:
            stages = ["revelation", "humiliation", "acceptance"]

        super().__init__(
            name="Cuckoldry Arc",
            definition="A narrative arc progression through stages of cuckoldry, tracking the emotional and psychological journey through revelation, humiliation, and potential acceptance or resolution.",
            category="genre-specific",
            parent_concepts=["Arc"],
            relationships=[
                Relationship(
                    source="Cuckoldry Arc",
                    target="Character",
                    cardinality="many-to-one",
                    description="Cuckoldry arc involves multiple characters with specific roles",
                    direction="involves",
                ),
                Relationship(
                    source="Cuckoldry Arc",
                    target="Humiliation Progression",
                    cardinality="one-to-one",
                    description="Each cuckoldry arc has an accompanying humiliation progression",
                    direction="has",
                ),
                Relationship(
                    source="Cuckoldry Arc",
                    target="Consent Boundary",
                    cardinality="one-to-one",
                    description="Each cuckoldry arc must respect safety constraints",
                    direction="respects",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="netorara_cuckoldry_stages",
                    condition="Cuckoldry arc must have at least revelation and humiliation stages",
                    error_message="Cuckoldry arc requires revelation and humiliation stages",
                    applies_to=["Cuckoldry Arc"],
                ),
                ValidationRule(
                    rule_id="netorara_cuckoldry_characters",
                    condition="Cuckoldry arc must involve at least two characters",
                    error_message="Cuckoldry arc requires at least two distinct character roles",
                    applies_to=["Cuckoldry Arc"],
                ),
                ValidationRule(
                    rule_id="netorara_cuckoldry_consent",
                    condition="Cuckoldry arc must have explicit consent boundaries",
                    error_message="Cuckoldry arc requires defined consent boundaries for safety",
                    applies_to=["Cuckoldry Arc"],
                ),
            ],
            metadata={
                "genre": "netorare",
                "stages": stages,
                "intensity_progression": intensity_progression,
                "emotional_core_alignment": ["humiliation", "cuckoldry", "shame"],
            },
        )


class HumiliationProgression(BaseConcept):
    """Represents the escalating emotional state progression in netorare narratives.

    Humiliation progression tracks how the emotional intensity and nature of
    humiliation evolves throughout the narrative, from initial exposure to
    deeper psychological impact.

    Attributes:
        name: Always "Humiliation Progression"
        definition: Definition of the concept
        intensity_levels: Number of distinct intensity levels
        progression_type: How humiliation escalates (linear, cyclical, stepped)
    """

    def __init__(
        self,
        intensity_levels: int = 5,
        progression_type: str = "escalating",
    ):
        """Initialize a HumiliationProgression concept.

        Args:
            intensity_levels: Number of distinct intensity levels (default: 5)
            progression_type: How it progresses (escalating, cyclical, stepped, plateau)
        """
        super().__init__(
            name="Humiliation Progression",
            definition="Tracks the escalating emotional state and intensity of humiliation throughout the narrative, from initial exposure to deeper psychological impact.",
            category="genre-specific",
            parent_concepts=["Progression"],
            relationships=[
                Relationship(
                    source="Humiliation Progression",
                    target="Cuckoldry Arc",
                    cardinality="one-to-one",
                    description="Part of cuckoldry arc structure",
                    direction="part_of",
                ),
                Relationship(
                    source="Humiliation Progression",
                    target="Theme",
                    cardinality="many-to-many",
                    description="Embodies netorare themes like degradation and shame",
                    direction="embodies",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="netorara_humiliation_levels",
                    condition="Humiliation progression must have at least 2 intensity levels",
                    error_message="Humiliation progression requires multiple distinct intensity levels",
                    applies_to=["Humiliation Progression"],
                ),
                ValidationRule(
                    rule_id="netorara_humiliation_consistency",
                    condition="Intensity levels must be consistent with progression type",
                    error_message="Humiliation progression type and intensity levels must align",
                    applies_to=["Humiliation Progression"],
                ),
                ValidationRule(
                    rule_id="netorara_humiliation_theme_alignment",
                    condition="Humiliation progression must align with netorare theme set",
                    error_message="Humiliation progression must use only netorare-approved themes",
                    applies_to=["Humiliation Progression"],
                ),
            ],
            metadata={
                "genre": "netorare",
                "intensity_levels": intensity_levels,
                "progression_type": progression_type,
                "valid_progression_types": ["escalating", "cyclical", "stepped", "plateau"],
                "intensity_scale": list(range(1, intensity_levels + 1)),
            },
        )


class ConsentBoundary(BaseConcept):
    """Represents safety constraints and consent boundaries in netorare narratives.

    Consent boundaries define the limits of acceptable content and ensure that
    humiliation and cuckoldry elements remain within explicitly defined constraints,
    protecting both characters and readers.

    Attributes:
        name: Always "Consent Boundary"
        definition: Definition of the concept
        boundary_type: Type of boundary (hard_stop, warning_zone, safe_zone)
        applies_to_elements: Which narrative elements this boundary constrains
    """

    def __init__(
        self,
        boundary_type: str = "hard_stop",
        applies_to_elements: List[str] = None,
    ):
        """Initialize a ConsentBoundary concept.

        Args:
            boundary_type: Type (hard_stop, warning_zone, safe_zone)
            applies_to_elements: Which elements are constrained (default: all)
        """
        if applies_to_elements is None:
            applies_to_elements = [
                "humiliation",
                "degradation",
                "physical_content",
                "emotional_content",
            ]

        super().__init__(
            name="Consent Boundary",
            definition="Safety constraints defining the limits of acceptable content in netorare narratives, ensuring humiliation and cuckoldry elements remain within explicitly defined constraints.",
            category="genre-specific",
            parent_concepts=["Constraint"],
            relationships=[
                Relationship(
                    source="Consent Boundary",
                    target="Cuckoldry Arc",
                    cardinality="one-to-one",
                    description="Required safety constraint for cuckoldry arcs",
                    direction="constrains",
                ),
                Relationship(
                    source="Consent Boundary",
                    target="Character",
                    cardinality="one-to-many",
                    description="Protects all characters involved",
                    direction="protects",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="netorara_consent_required",
                    condition="Every cuckoldry arc must have explicit consent boundary",
                    error_message="Consent boundary is mandatory for netorare content",
                    applies_to=["Consent Boundary", "Cuckoldry Arc"],
                ),
                ValidationRule(
                    rule_id="netorara_consent_type_valid",
                    condition="Boundary type must be one of: hard_stop, warning_zone, safe_zone",
                    error_message="Invalid consent boundary type",
                    applies_to=["Consent Boundary"],
                ),
                ValidationRule(
                    rule_id="netorara_consent_coverage",
                    condition="Consent boundary must cover all potentially harmful content types",
                    error_message="Consent boundary must explicitly cover all content types",
                    applies_to=["Consent Boundary"],
                ),
            ],
            metadata={
                "genre": "netorare",
                "boundary_type": boundary_type,
                "applies_to_elements": applies_to_elements,
                "boundary_types": ["hard_stop", "warning_zone", "safe_zone"],
            },
        )


class NetorareOntology:
    """Container for all netorare-specific ontology concepts.

    This class provides a unified interface to access all netorare-specific
    concepts and their relationships.
    """

    def __init__(self):
        """Initialize the netorare ontology."""
        self.genre = "netorare"
        self.theme_set = [
            "humiliation",
            "degradation",
            "cuckoldry",
            "shame",
            "exposure",
        ]

        # Instantiate all genre-specific concepts
        self.cuckoldry_arc = CuckoldryArc()
        self.humiliation_progression = HumiliationProgression()
        self.consent_boundary = ConsentBoundary()

        # Store all concepts for easy iteration
        self.concepts = {
            "Cuckoldry Arc": self.cuckoldry_arc,
            "Humiliation Progression": self.humiliation_progression,
            "Consent Boundary": self.consent_boundary,
        }

    def get_concept(self, concept_name: str) -> BaseConcept:
        """Get a concept by name.

        Args:
            concept_name: The name of the concept

        Returns:
            The BaseConcept object or None if not found

        Raises:
            KeyError: If concept not found in netorare ontology
        """
        return self.concepts[concept_name]

    def get_all_concepts(self) -> Dict[str, BaseConcept]:
        """Get all concepts in the netorare ontology.

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
        """Check if a concept is valid in netorare ontology.

        Args:
            concept_name: The concept to validate

        Returns:
            True if concept exists in netorare ontology
        """
        return concept_name in self.concepts

    def get_theme_set(self) -> List[str]:
        """Get the theme set for netorare genre.

        Returns:
            List of themes for netorare
        """
        return self.theme_set.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire ontology to a dictionary representation.

        Returns:
            Dictionary representation of the netorare ontology
        """
        return {
            "genre": self.genre,
            "theme_set": self.theme_set,
            "concepts": {name: concept.to_dict() for name, concept in self.concepts.items()},
        }
