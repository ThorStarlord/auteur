"""Tests for the OntologyValidator.

Tests cover concept validation, relationship validation, arc properties,
character properties, and genre-specific rule enforcement.
"""

import pytest
from auteur.narrative_ontology.validator.ontology_validator import OntologyValidator
from auteur.narrative_ontology.core.narrative_concepts import (
    CHARACTER,
    ARC,
    THEME,
    GOAL,
    CONFLICT,
)
from auteur.narrative_ontology.genre.netorara_ontology import (
    NetorareOntology,
    CuckoldryArc,
)
from auteur.narrative_ontology.genre.mystery_ontology import MysteryOntology
from auteur.narrative_ontology.genre.gentlefemdom_ontology import GentleFemdomOntology


class TestOntologyValidatorBasicConcepts:
    """Test basic concept validation."""

    def test_validator_instantiation(self):
        """Test that OntologyValidator instantiates correctly."""
        validator = OntologyValidator()
        assert validator is not None

    def test_validate_concept_exists_base(self):
        """Test validating a concept that exists in base ontology."""
        validator = OntologyValidator()
        result = validator.validate_concept("Character", "netorare")
        assert result is True

    def test_validate_concept_not_exists(self):
        """Test validating a concept that doesn't exist."""
        validator = OntologyValidator()
        result = validator.validate_concept("InvalidConcept", "netorare")
        assert result is False

    def test_validate_multiple_base_concepts(self):
        """Test validating multiple base concepts."""
        validator = OntologyValidator()
        concepts = ["Character", "Arc", "Theme", "Goal", "Conflict"]
        for concept in concepts:
            assert validator.validate_concept(concept, "netorare") is True

    def test_base_concepts_valid_for_all_genres(self):
        """Test that base concepts are valid for all genres."""
        validator = OntologyValidator()
        concept = "Character"
        for genre in ["netorare", "mystery", "gentlefemdom"]:
            assert validator.validate_concept(concept, genre) is True


class TestOntologyValidatorGenreSpecific:
    """Test genre-specific concept validation."""

    def test_validate_netorare_cuckoldry_arc(self):
        """Test validating netorare-specific Cuckoldry Arc."""
        validator = OntologyValidator()
        result = validator.validate_concept("Cuckoldry Arc", "netorare")
        assert result is True

    def test_netorare_concept_not_valid_for_mystery(self):
        """Test that netorare concepts don't validate for mystery genre."""
        validator = OntologyValidator()
        # Cuckoldry Arc should only be valid for netorare
        result = validator.validate_concept("Cuckoldry Arc", "mystery")
        assert result is False

    def test_netorare_concept_not_valid_for_gentlefemdom(self):
        """Test that netorare concepts don't validate for gentlefemdom."""
        validator = OntologyValidator()
        result = validator.validate_concept("Cuckoldry Arc", "gentlefemdom")
        assert result is False

    def test_validate_mystery_investigation_arc(self):
        """Test validating mystery-specific Investigation Arc."""
        validator = OntologyValidator()
        result = validator.validate_concept("Investigation Arc", "mystery")
        assert result is True

    def test_validate_gentlefemdom_authority_arc(self):
        """Test validating gentlefemdom-specific Authority Arc."""
        validator = OntologyValidator()
        result = validator.validate_concept("Authority Arc", "gentlefemdom")
        assert result is True


class TestOntologyValidatorRelationships:
    """Test relationship validation between concepts."""

    def test_validate_valid_relationship_character_to_goal(self):
        """Test validating a valid Character->Goal relationship."""
        validator = OntologyValidator()
        result = validator.validate_relationship("Character", "Goal", "netorare")
        assert result is True

    def test_validate_valid_relationship_character_to_arc(self):
        """Test validating a valid Character->Arc relationship."""
        validator = OntologyValidator()
        result = validator.validate_relationship("Character", "Arc", "netorare")
        assert result is True

    def test_validate_valid_relationship_arc_to_beat(self):
        """Test validating a valid Arc->Beat relationship."""
        validator = OntologyValidator()
        result = validator.validate_relationship("Arc", "Beat", "netorare")
        assert result is True

    def test_validate_invalid_relationship_nonexistent_source(self):
        """Test validating relationship with nonexistent source concept."""
        validator = OntologyValidator()
        result = validator.validate_relationship("InvalidSource", "Goal", "netorare")
        assert result is False

    def test_validate_invalid_relationship_nonexistent_target(self):
        """Test validating relationship with nonexistent target concept."""
        validator = OntologyValidator()
        result = validator.validate_relationship("Character", "InvalidTarget", "netorare")
        assert result is False

    def test_validate_relationship_arc_to_character(self):
        """Test validating Arc has relationship to Character."""
        validator = OntologyValidator()
        result = validator.validate_relationship("Arc", "Character", "netorare")
        assert result is True

    def test_validate_relationship_theme_to_arc(self):
        """Test validating Theme has relationship to Arc."""
        validator = OntologyValidator()
        result = validator.validate_relationship("Theme", "Arc", "netorare")
        assert result is True


class TestOntologyValidatorArcProperties:
    """Test arc property validation."""

    def test_validate_arc_properties_base_arc(self):
        """Test validating properties of a base Arc type."""
        validator = OntologyValidator()
        arc_data = {"type": "Arc", "start_state": "initial", "end_state": "resolved"}
        result = validator.validate_arc_properties("Arc", "netorare")
        assert result is True

    def test_validate_arc_properties_character_arc(self):
        """Test validating a character arc."""
        validator = OntologyValidator()
        result = validator.validate_arc_properties("Arc", "mystery")
        assert result is True

    def test_validate_arc_properties_netorare_cuckoldry(self):
        """Test validating a netorare cuckoldry arc."""
        validator = OntologyValidator()
        result = validator.validate_arc_properties("Cuckoldry Arc", "netorare")
        assert result is True

    def test_validate_arc_properties_mystery_investigation(self):
        """Test validating a mystery investigation arc."""
        validator = OntologyValidator()
        result = validator.validate_arc_properties("Investigation Arc", "mystery")
        assert result is True

    def test_validate_arc_properties_gentlefemdom_authority(self):
        """Test validating a gentlefemdom authority arc."""
        validator = OntologyValidator()
        result = validator.validate_arc_properties("Authority Arc", "gentlefemdom")
        assert result is True

    def test_validate_arc_properties_invalid_arc_type(self):
        """Test validating invalid arc type."""
        validator = OntologyValidator()
        result = validator.validate_arc_properties("InvalidArcType", "netorare")
        assert result is False


class TestOntologyValidatorCharacterProperties:
    """Test character property validation."""

    def test_validate_character_properties_basic(self):
        """Test validating basic character properties."""
        validator = OntologyValidator()
        result = validator.validate_character_properties("Character", "netorare")
        assert result is True

    def test_validate_character_properties_all_genres(self):
        """Test validating character properties across genres."""
        validator = OntologyValidator()
        for genre in ["netorare", "mystery", "gentlefemdom"]:
            result = validator.validate_character_properties("Character", genre)
            assert result is True

    def test_validate_character_properties_with_goals(self):
        """Test character can have goals."""
        validator = OntologyValidator()
        result = validator.validate_character_properties("Character", "netorare")
        assert result is True

    def test_validate_character_in_multiple_arcs(self):
        """Test character can participate in multiple arcs."""
        validator = OntologyValidator()
        result = validator.validate_character_properties("Character", "netorare")
        assert result is True


class TestOntologyValidatorValidationRules:
    """Test enforcement of validation rules."""

    def test_enforce_character_must_have_identity_rule(self):
        """Test enforcing character identity rule."""
        validator = OntologyValidator()
        concept = "Character"
        genre = "netorare"
        # Should have validation rules for Character
        result = validator.enforce_validation_rules(concept, {}, genre)
        assert result is not None

    def test_enforce_arc_must_have_beats_rule(self):
        """Test enforcing arc must contain beats rule."""
        validator = OntologyValidator()
        concept = "Arc"
        genre = "netorare"
        result = validator.enforce_validation_rules(concept, {}, genre)
        assert result is not None

    def test_enforce_theme_validation_rules(self):
        """Test enforcing theme validation rules."""
        validator = OntologyValidator()
        concept = "Theme"
        genre = "netorare"
        result = validator.enforce_validation_rules(concept, {}, genre)
        assert result is not None

    def test_enforce_goal_must_have_owner_rule(self):
        """Test enforcing goal must have owner rule."""
        validator = OntologyValidator()
        concept = "Goal"
        genre = "netorare"
        result = validator.enforce_validation_rules(concept, {}, genre)
        assert result is not None

    def test_enforce_conflict_must_have_stakes_rule(self):
        """Test enforcing conflict must have stakes rule."""
        validator = OntologyValidator()
        concept = "Conflict"
        genre = "netorare"
        result = validator.enforce_validation_rules(concept, {}, genre)
        assert result is not None

    def test_enforce_netorare_specific_rules(self):
        """Test enforcing netorare-specific rules."""
        validator = OntologyValidator()
        concept = "Cuckoldry Arc"
        genre = "netorare"
        result = validator.enforce_validation_rules(concept, {}, genre)
        assert result is not None

    def test_enforce_mystery_specific_rules(self):
        """Test enforcing mystery-specific rules."""
        validator = OntologyValidator()
        concept = "Investigation Arc"
        genre = "mystery"
        result = validator.enforce_validation_rules(concept, {}, genre)
        assert result is not None

    def test_enforce_gentlefemdom_specific_rules(self):
        """Test enforcing gentlefemdom-specific rules."""
        validator = OntologyValidator()
        concept = "Authority Arc"
        genre = "gentlefemdom"
        result = validator.enforce_validation_rules(concept, {}, genre)
        assert result is not None


class TestOntologyValidatorCrossGenre:
    """Test cross-genre validation scenarios."""

    def test_netorare_concept_rejected_in_mystery(self):
        """Test that netorare concepts are rejected in mystery genre."""
        validator = OntologyValidator()
        # Cuckoldry Arc should not be valid for mystery
        assert validator.validate_concept("Cuckoldry Arc", "mystery") is False

    def test_netorare_concept_rejected_in_gentlefemdom(self):
        """Test that netorare concepts are rejected in gentlefemdom."""
        validator = OntologyValidator()
        assert validator.validate_concept("Cuckoldry Arc", "gentlefemdom") is False

    def test_mystery_concept_rejected_in_netorare(self):
        """Test that mystery concepts are rejected in netorare."""
        validator = OntologyValidator()
        assert validator.validate_concept("Investigation Arc", "netorare") is False

    def test_gentlefemdom_concept_rejected_in_netorare(self):
        """Test that gentlefemdom concepts are rejected in netorare."""
        validator = OntologyValidator()
        assert validator.validate_concept("Authority Arc", "netorare") is False

    def test_base_concepts_work_everywhere(self):
        """Test that base concepts work in all genres."""
        validator = OntologyValidator()
        base_concepts = ["Character", "Arc", "Theme", "Goal"]
        for concept in base_concepts:
            for genre in ["netorare", "mystery", "gentlefemdom"]:
                assert validator.validate_concept(concept, genre) is True


class TestOntologyValidatorIntegration:
    """Integration tests for complete validation workflows."""

    def test_validate_netorare_workflow(self):
        """Test complete netorare validation workflow."""
        validator = OntologyValidator()
        # Validate base concepts
        assert validator.validate_concept("Character", "netorare") is True
        assert validator.validate_concept("Arc", "netorare") is True
        # Validate genre-specific concepts
        assert validator.validate_concept("Cuckoldry Arc", "netorare") is True
        # Validate relationships
        assert validator.validate_relationship("Character", "Arc", "netorare") is True
        assert validator.validate_relationship("Arc", "Beat", "netorare") is True
        # Validate arc properties
        assert validator.validate_arc_properties("Cuckoldry Arc", "netorare") is True

    def test_validate_mystery_workflow(self):
        """Test complete mystery validation workflow."""
        validator = OntologyValidator()
        # Validate base concepts
        assert validator.validate_concept("Character", "mystery") is True
        # Validate genre-specific concepts
        assert validator.validate_concept("Investigation Arc", "mystery") is True
        # Validate arc properties
        assert validator.validate_arc_properties("Investigation Arc", "mystery") is True

    def test_validate_gentlefemdom_workflow(self):
        """Test complete gentlefemdom validation workflow."""
        validator = OntologyValidator()
        # Validate base concepts
        assert validator.validate_concept("Character", "gentlefemdom") is True
        # Validate genre-specific concepts
        assert validator.validate_concept("Authority Arc", "gentlefemdom") is True
        # Validate arc properties
        assert validator.validate_arc_properties("Authority Arc", "gentlefemdom") is True

    def test_multi_genre_consistency(self):
        """Test that all three genres can be validated consistently."""
        validator = OntologyValidator()
        genres = ["netorare", "mystery", "gentlefemdom"]
        base_concepts = ["Character", "Arc", "Theme", "Goal"]

        # Base concepts should work for all genres
        for concept in base_concepts:
            for genre in genres:
                assert validator.validate_concept(concept, genre) is True

        # Each genre should validate its specific concepts
        genre_concepts = {
            "netorare": ["Cuckoldry Arc", "Humiliation Progression"],
            "mystery": ["Investigation Arc", "Clue"],
            "gentlefemdom": ["Authority Arc", "Surrender Beat"],
        }

        for genre, concepts in genre_concepts.items():
            for concept in concepts:
                assert validator.validate_concept(concept, genre) is True
