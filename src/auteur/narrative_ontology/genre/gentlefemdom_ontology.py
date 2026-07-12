"""Gentle femdom-specific narrative ontology concepts.

This module defines genre-specific concepts for gentle femdom narratives, including
authority arcs, surrender beats, and trust checkpoints.
"""

from typing import List, Dict, Any
from auteur.narrative_ontology.base_concept import (
    BaseConcept,
    Relationship,
    ValidationRule,
)


class AuthorityArc(BaseConcept):
    """Represents a power dynamic progression in gentle femdom narratives.

    An authority arc is a narrative progression specific to gentle femdom that
    tracks the evolution of power dynamics, dominance, and submission between
    characters, emphasizing consensuality and emotional connection.

    Attributes:
        name: Always "Authority Arc"
        definition: Definition of the concept
        authority_type: Type of authority (sensual, romantic, protective)
        dynamic_type: Nature of the power dynamic (consensual, negotiated, evolving)
    """

    def __init__(
        self,
        authority_type: str = "sensual",
        dynamic_type: str = "consensual",
    ):
        """Initialize an AuthorityArc concept.

        Args:
            authority_type: Type (sensual, romantic, protective, tender)
            dynamic_type: Nature (consensual, negotiated, evolving)
        """
        super().__init__(
            name="Authority Arc",
            definition="A narrative arc progression tracking the evolution of power dynamics and dominance between characters, emphasizing consensuality, emotional connection, and mutual respect.",
            category="genre-specific",
            parent_concepts=["Arc"],
            relationships=[
                Relationship(
                    source="Authority Arc",
                    target="Character",
                    cardinality="many-to-many",
                    description="Authority arc involves multiple characters in power dynamic",
                    direction="involves",
                ),
                Relationship(
                    source="Authority Arc",
                    target="Surrender Beat",
                    cardinality="one-to-many",
                    description="Authority arc contains surrender beats",
                    direction="contains",
                ),
                Relationship(
                    source="Authority Arc",
                    target="Trust Checkpoint",
                    cardinality="one-to-many",
                    description="Authority arc includes trust checkpoints",
                    direction="validates_through",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="femdom_authority_consensual",
                    condition="Authority arc must maintain consensual framework",
                    error_message="Authority arc must be explicitly consensual",
                    applies_to=["Authority Arc"],
                ),
                ValidationRule(
                    rule_id="femdom_authority_type_valid",
                    condition="Authority type must be sensual, romantic, protective, or tender",
                    error_message="Invalid authority type for gentle femdom",
                    applies_to=["Authority Arc"],
                ),
                ValidationRule(
                    rule_id="femdom_authority_dynamic_clear",
                    condition="Power dynamic must be clearly established and evolving",
                    error_message="Authority arc requires clear dynamic progression",
                    applies_to=["Authority Arc"],
                ),
                ValidationRule(
                    rule_id="femdom_authority_emotional_connection",
                    condition="Authority arc must maintain emotional connection between characters",
                    error_message="Authority arc must prioritize emotional intimacy",
                    applies_to=["Authority Arc"],
                ),
            ],
            metadata={
                "genre": "gentlefemdom",
                "authority_type": authority_type,
                "dynamic_type": dynamic_type,
                "valid_types": ["sensual", "romantic", "protective", "tender"],
                "valid_dynamics": ["consensual", "negotiated", "evolving"],
                "emotional_core_alignment": ["authority", "surrender", "dominance", "trust", "control"],
            },
        )


class SurrenderBeat(BaseConcept):
    """Represents a character moment of acceptance in gentle femdom narratives.

    A surrender beat is a significant narrative moment where a character accepts
    or embraces the power dynamic, typically involving emotional openness and
    vulnerability.

    Attributes:
        name: Always "Surrender Beat"
        definition: Definition of the concept
        beat_type: Type of surrender (emotional, physical, psychological)
        intensity_level: How intense the moment is (subtle, moderate, profound)
    """

    def __init__(
        self,
        beat_type: str = "emotional",
        intensity_level: str = "moderate",
    ):
        """Initialize a SurrenderBeat concept.

        Args:
            beat_type: Type (emotional, physical, psychological, spiritual)
            intensity_level: Intensity (subtle, moderate, profound)
        """
        super().__init__(
            name="Surrender Beat",
            definition="A significant narrative moment where a character accepts or embraces the power dynamic, typically involving emotional openness, vulnerability, and mutual trust.",
            category="genre-specific",
            parent_concepts=["Beat"],
            relationships=[
                Relationship(
                    source="Surrender Beat",
                    target="Authority Arc",
                    cardinality="many-to-one",
                    description="Part of authority arc progression",
                    direction="part_of",
                ),
                Relationship(
                    source="Surrender Beat",
                    target="Character",
                    cardinality="one-to-many",
                    description="Surrender beat involves specific characters",
                    direction="involves",
                ),
                Relationship(
                    source="Surrender Beat",
                    target="Emotion",
                    cardinality="many-to-many",
                    description="Surrender beats embody specific emotions",
                    direction="embodies",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="femdom_surrender_consensual",
                    condition="Surrender beat must represent genuine choice, not coercion",
                    error_message="Surrender beat must be consensual and authentic",
                    applies_to=["Surrender Beat"],
                ),
                ValidationRule(
                    rule_id="femdom_surrender_type_valid",
                    condition="Beat type must be emotional, physical, psychological, or spiritual",
                    error_message="Invalid surrender beat type",
                    applies_to=["Surrender Beat"],
                ),
                ValidationRule(
                    rule_id="femdom_surrender_intensity_valid",
                    condition="Intensity must be subtle, moderate, or profound",
                    error_message="Invalid surrender beat intensity level",
                    applies_to=["Surrender Beat"],
                ),
                ValidationRule(
                    rule_id="femdom_surrender_character_agency",
                    condition="Character must retain agency and ability to withdraw consent",
                    error_message="Surrender beat must preserve character agency",
                    applies_to=["Surrender Beat"],
                ),
            ],
            metadata={
                "genre": "gentlefemdom",
                "beat_type": beat_type,
                "intensity_level": intensity_level,
                "valid_types": ["emotional", "physical", "psychological", "spiritual"],
                "valid_intensity": ["subtle", "moderate", "profound"],
            },
        )


class TrustCheckpoint(BaseConcept):
    """Represents a validation milestone in gentle femdom narratives.

    A trust checkpoint is a narrative moment where the relationship's foundation
    of trust, consent, and mutual respect is explicitly validated or tested,
    ensuring the dynamic remains healthy and consensual.

    Attributes:
        name: Always "Trust Checkpoint"
        definition: Definition of the concept
        checkpoint_type: Type of checkpoint (negotiation, boundary, renewal)
        validation_outcome: Expected result (reinforced, renegotiated, withdrawn)
    """

    def __init__(
        self,
        checkpoint_type: str = "negotiation",
        validation_outcome: str = "reinforced",
    ):
        """Initialize a TrustCheckpoint concept.

        Args:
            checkpoint_type: Type (negotiation, boundary, renewal, crisis)
            validation_outcome: Expected outcome (reinforced, renegotiated, withdrawn)
        """
        super().__init__(
            name="Trust Checkpoint",
            definition="A narrative moment where the relationship's foundation of trust, consent, and mutual respect is explicitly validated or tested, ensuring the dynamic remains healthy and consensual.",
            category="genre-specific",
            parent_concepts=["Checkpoint"],
            relationships=[
                Relationship(
                    source="Trust Checkpoint",
                    target="Authority Arc",
                    cardinality="many-to-one",
                    description="Validation point in authority arc",
                    direction="validates",
                ),
                Relationship(
                    source="Trust Checkpoint",
                    target="Character",
                    cardinality="many-to-many",
                    description="Checkpoint involves all characters in dynamic",
                    direction="involves",
                ),
                Relationship(
                    source="Trust Checkpoint",
                    target="Consent Boundary",
                    cardinality="one-to-one",
                    description="Checkpoint tests consent boundaries",
                    direction="tests",
                ),
            ],
            validation_rules=[
                ValidationRule(
                    rule_id="femdom_checkpoint_consent_explicit",
                    condition="Trust checkpoint must explicitly address consent",
                    error_message="Trust checkpoint must include explicit consent discussion",
                    applies_to=["Trust Checkpoint"],
                ),
                ValidationRule(
                    rule_id="femdom_checkpoint_type_valid",
                    condition="Checkpoint type must be negotiation, boundary, renewal, or crisis",
                    error_message="Invalid trust checkpoint type",
                    applies_to=["Trust Checkpoint"],
                ),
                ValidationRule(
                    rule_id="femdom_checkpoint_outcome_valid",
                    condition="Outcome must be reinforced, renegotiated, or withdrawn",
                    error_message="Invalid trust checkpoint outcome",
                    applies_to=["Trust Checkpoint"],
                ),
                ValidationRule(
                    rule_id="femdom_checkpoint_honesty",
                    condition="Checkpoint must involve honest communication between characters",
                    error_message="Trust checkpoint requires genuine character communication",
                    applies_to=["Trust Checkpoint"],
                ),
                ValidationRule(
                    rule_id="femdom_checkpoint_agency",
                    condition="All characters must have agency in checkpoint resolution",
                    error_message="Trust checkpoint must preserve character agency",
                    applies_to=["Trust Checkpoint"],
                ),
            ],
            metadata={
                "genre": "gentlefemdom",
                "checkpoint_type": checkpoint_type,
                "validation_outcome": validation_outcome,
                "valid_types": ["negotiation", "boundary", "renewal", "crisis"],
                "valid_outcomes": ["reinforced", "renegotiated", "withdrawn"],
            },
        )


class GentleFemdomOntology:
    """Container for all gentle femdom-specific ontology concepts.

    This class provides a unified interface to access all gentle femdom-specific
    concepts and their relationships.
    """

    def __init__(self):
        """Initialize the gentle femdom ontology."""
        self.genre = "gentlefemdom"
        self.theme_set = [
            "authority",
            "surrender",
            "dominance",
            "trust",
            "control",
        ]

        # Instantiate all genre-specific concepts
        self.authority_arc = AuthorityArc()
        self.surrender_beat = SurrenderBeat()
        self.trust_checkpoint = TrustCheckpoint()

        # Store all concepts for easy iteration
        self.concepts = {
            "Authority Arc": self.authority_arc,
            "Surrender Beat": self.surrender_beat,
            "Trust Checkpoint": self.trust_checkpoint,
        }

    def get_concept(self, concept_name: str) -> BaseConcept:
        """Get a concept by name.

        Args:
            concept_name: The name of the concept

        Returns:
            The BaseConcept object

        Raises:
            KeyError: If concept not found in gentle femdom ontology
        """
        return self.concepts[concept_name]

    def get_all_concepts(self) -> Dict[str, BaseConcept]:
        """Get all concepts in the gentle femdom ontology.

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
        """Check if a concept is valid in gentle femdom ontology.

        Args:
            concept_name: The concept to validate

        Returns:
            True if concept exists in gentle femdom ontology
        """
        return concept_name in self.concepts

    def get_theme_set(self) -> List[str]:
        """Get the theme set for gentle femdom genre.

        Returns:
            List of themes for gentle femdom
        """
        return self.theme_set.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire ontology to a dictionary representation.

        Returns:
            Dictionary representation of the gentle femdom ontology
        """
        return {
            "genre": self.genre,
            "theme_set": self.theme_set,
            "concepts": {name: concept.to_dict() for name, concept in self.concepts.items()},
        }
