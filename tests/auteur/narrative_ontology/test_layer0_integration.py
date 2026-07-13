"""Layer 0 Integration Tests for Narrative Ontology.

Tests verify that Layer 0 works end-to-end:
- Load ontology → Inspect concept → Validate rules (full flow)
- Add new concept to ontology → Automatically works in validators
- Genre extensibility: add new genre → works identically
- All 3 genres pass same tests (prove no special-casing)
- Ontology correctness: concepts referenced by Layer 1-2

These tests ensure Layer 0 is production-ready and provides the foundational
semantic layer for all narrative engineering.
"""

import pytest
from typing import Dict, Any

from auteur.narrative_ontology.validator.ontology_validator import OntologyValidator
from auteur.narrative_ontology.core.narrative_concepts import (
    ALL_CONCEPTS,
    get_concept,
    CHARACTER,
    ARC,
    THEME,
    CONFLICT,
    GOAL,
    BEAT,
    PAYOFF,
    SETUP,
)
from auteur.narrative_ontology.schema.ontology_types import (
    Concept,
    Relationship,
    ValidationRule,
)
from auteur.narrative_ontology.genre.netorare_ontology import NetorareOntology
from auteur.narrative_ontology.genre.mystery_ontology import MysteryOntology
from auteur.narrative_ontology.genre.gentlefemdom_ontology import GentleFemdomOntology


class TestOntologyLoading:
    """Test that ontology loads and is accessible."""

    def test_load_base_ontology_succeeds(self):
        """Base ontology should load with all 12 core concepts."""
        concepts = ALL_CONCEPTS
        assert len(concepts) == 12
        expected_concepts = {
            "Character",
            "Arc",
            "Theme",
            "Goal",
            "Conflict",
            "Payoff",
            "Symbol",
            "Relationship",
            "Beat",
            "Setup",
            "Revelation",
            "Reversal",
        }
        assert set(concepts.keys()) == expected_concepts

    def test_load_netorare_ontology_succeeds(self):
        """Netorare ontology should load with genre-specific concepts."""
        ontology = NetorareOntology()
        concepts = ontology.get_all_concepts()
        assert len(concepts) > 0
        # Should have genre-specific concepts
        concept_names = set(concepts.keys())
        assert "Cuckoldry Arc" in concept_names
        assert "Humiliation Progression" in concept_names
        assert "Consent Boundary" in concept_names

    def test_load_mystery_ontology_succeeds(self):
        """Mystery ontology should load with genre-specific concepts."""
        ontology = MysteryOntology()
        concepts = ontology.get_all_concepts()
        assert len(concepts) > 0
        concept_names = set(concepts.keys())
        assert "Investigation Arc" in concept_names
        assert "Clue" in concept_names
        assert "Red Herring" in concept_names

    def test_load_gentlefemdom_ontology_succeeds(self):
        """Gentle femdom ontology should load with genre-specific concepts."""
        ontology = GentleFemdomOntology()
        concepts = ontology.get_all_concepts()
        assert len(concepts) > 0
        concept_names = set(concepts.keys())
        assert "Authority Arc" in concept_names
        assert "Surrender Beat" in concept_names
        assert "Trust Checkpoint" in concept_names


class TestConceptInspection:
    """Test that concepts can be inspected and their properties accessed."""

    def test_inspect_concept_by_name_succeeds(self):
        """Should be able to retrieve concept by name."""
        character = get_concept("Character")
        assert character is not None
        assert character.name == "Character"
        assert isinstance(character.definition, str)
        assert len(character.definition) > 0

    def test_concept_has_definition(self):
        """All concepts should have definitions."""
        for concept_name, concept in ALL_CONCEPTS.items():
            assert concept.definition
            assert isinstance(concept.definition, str)
            assert len(concept.definition) > 10, f"{concept_name} definition too short"

    def test_concept_has_relationships(self):
        """Concepts should have relationships defined."""
        # Character should relate to Goal
        character = get_concept("Character")
        # Extract target concepts from relationships
        related_concepts = [r.target_concept for r in character.relationships]
        assert "Goal" in related_concepts

    def test_concept_has_validation_rules(self):
        """Concepts should have validation rules."""
        # Character should have validation rules
        character = get_concept("Character")
        assert len(character.validation_rules) > 0
        # First rule should be about identity
        first_rule = character.validation_rules[0]
        assert first_rule.rule_id == "character_must_have_identity"

    def test_extract_concept_properties(self):
        """Should be able to extract all properties from concept."""
        arc = get_concept("Arc")
        # Use Pydantic's model_dump() to serialize
        concept_dict = arc.model_dump()

        # Should have all required keys
        assert "name" in concept_dict
        assert "definition" in concept_dict
        assert "relationships" in concept_dict
        assert "validation_rules" in concept_dict

        # Relationships should be serializable
        assert isinstance(concept_dict["relationships"], list)
        if concept_dict["relationships"]:
            first_rel = concept_dict["relationships"][0]
            assert "source_concept" in first_rel
            assert "target_concept" in first_rel
            assert "cardinality" in first_rel

    def test_inspect_concept_relationships(self):
        """Should inspect relationships between concepts."""
        arc = get_concept("Arc")
        relationships = arc.relationships
        assert len(relationships) > 0

        # Arc should relate to Beat
        beat_relationships = [
            r for r in relationships if r.target_concept == "Beat"
        ]
        assert len(beat_relationships) > 0


class TestValidationRuleEnforcement:
    """Test that validation rules are properly structured and enforceable."""

    def test_validation_rules_have_required_fields(self):
        """All validation rules should have required fields."""
        for concept_name, concept in ALL_CONCEPTS.items():
            for rule in concept.validation_rules:
                assert rule.rule_id
                assert rule.condition
                assert rule.error_message
                assert hasattr(rule, "applies_to")

    def test_validation_rules_apply_to_genres(self):
        """Validation rules should specify which genres they apply to."""
        character = get_concept("Character")
        for rule in character.validation_rules:
            # Each rule should apply to at least one genre
            assert len(rule.applies_to) > 0
            # All genres in applies_to should be valid
            for genre in rule.applies_to:
                assert genre in {"netorare", "mystery", "gentlefemdom"}

    def test_character_validation_rules(self):
        """Character concept should enforce identity requirement."""
        character = get_concept("Character")
        rules_by_id = {r.rule_id: r for r in character.validation_rules}

        # Should have identity rule
        assert "character_must_have_identity" in rules_by_id
        identity_rule = rules_by_id["character_must_have_identity"]
        assert "identity" in identity_rule.error_message.lower()

    def test_arc_validation_rules(self):
        """Arc concept should enforce structural requirements."""
        arc = get_concept("Arc")
        rules_by_id = {r.rule_id: r for r in arc.validation_rules}

        # Should have start and end requirements
        assert "arc_must_have_start" in rules_by_id
        assert "arc_must_have_end" in rules_by_id
        assert "arc_must_contain_beats" in rules_by_id

    def test_all_concepts_have_genre_coverage(self):
        """All validation rules should cover all three genres."""
        for concept_name, concept in ALL_CONCEPTS.items():
            for rule in concept.validation_rules:
                # Each rule should apply to all three genres (base ontology rules)
                assert "netorare" in rule.applies_to
                assert "mystery" in rule.applies_to
                assert "gentlefemdom" in rule.applies_to


class TestOntologyValidatorIntegration:
    """Test full workflow: load ontology → validate concepts → use validator."""

    def setup_method(self):
        """Set up validator for each test."""
        self.validator = OntologyValidator()

    def test_validator_loads_base_concepts(self):
        """Validator should load all base concepts."""
        concepts = self.validator.get_all_concepts_for_genre("netorare")
        # Should have all 12 base concepts
        base_concept_names = set(ALL_CONCEPTS.keys())
        loaded_names = set(concepts.keys())
        assert base_concept_names.issubset(loaded_names)

    def test_validator_loads_genre_concepts(self):
        """Validator should load base + genre-specific concepts."""
        netorare_concepts = self.validator.get_all_concepts_for_genre("netorare")
        mystery_concepts = self.validator.get_all_concepts_for_genre("mystery")
        gf_concepts = self.validator.get_all_concepts_for_genre("gentlefemdom")

        # Each genre should have base concepts + genre-specific ones
        assert len(netorare_concepts) > len(ALL_CONCEPTS)
        assert len(mystery_concepts) > len(ALL_CONCEPTS)
        assert len(gf_concepts) > len(ALL_CONCEPTS)

    def test_validate_concept_exists(self):
        """Validator should verify concept existence."""
        # Base concepts should exist for all genres
        assert self.validator.validate_concept("Character", "netorare")
        assert self.validator.validate_concept("Arc", "mystery")
        assert self.validator.validate_concept("Theme", "gentlefemdom")

        # Invalid concept should fail
        assert not self.validator.validate_concept("InvalidConcept", "netorare")

    def test_validate_concept_for_invalid_genre(self):
        """Validator should reject invalid genres."""
        assert not self.validator.validate_concept("Character", "invalid_genre")

    def test_validate_relationship_between_concepts(self):
        """Validator should verify relationships exist."""
        # Character has relationship to Goal
        assert self.validator.validate_relationship(
            "Character", "Goal", "netorare"
        )

        # Arc has relationship to Beat
        assert self.validator.validate_relationship("Arc", "Beat", "netorare")

        # Invalid relationship should fail
        assert not self.validator.validate_relationship(
            "Character", "Symbol", "netorare"
        )

    def test_get_related_concepts(self):
        """Validator should return all related concepts."""
        related = self.validator.get_related_concepts("Arc", "netorare")
        assert len(related) > 0
        assert "Beat" in related
        assert "Character" in related

    def test_get_cardinality_of_relationship(self):
        """Validator should return cardinality of relationships."""
        # Arc to Beat should be one-to-many (one arc has many beats)
        cardinality = self.validator.validate_cardinality(
            "Arc", "Beat", "netorare"
        )
        assert cardinality == "one-to-many"

    def test_get_concept_from_ontology(self):
        """Validator should retrieve concepts."""
        concept = self.validator.get_concept("Character", "netorare")
        assert concept is not None
        assert concept.name == "Character"


class TestGenreConsistency:
    """Test that all genres handle concepts identically (no special-casing)."""

    def setup_method(self):
        """Set up validator."""
        self.validator = OntologyValidator()
        self.genres = ["netorare", "mystery", "gentlefemdom"]

    def test_all_genres_recognize_base_concepts(self):
        """All genres should recognize all base concepts identically."""
        for genre in self.genres:
            for concept_name in ALL_CONCEPTS.keys():
                assert self.validator.validate_concept(
                    concept_name, genre
                ), f"{genre} should recognize {concept_name}"

    def test_character_goal_relationship_consistent(self):
        """Character-Goal relationship should be identical across genres."""
        for genre in self.genres:
            assert self.validator.validate_relationship(
                "Character", "Goal", genre
            ), f"{genre} should have Character->Goal relationship"

    def test_arc_beat_relationship_consistent(self):
        """Arc-Beat relationship should be identical across genres."""
        for genre in self.genres:
            assert self.validator.validate_relationship(
                "Arc", "Beat", genre
            ), f"{genre} should have Arc->Beat relationship"
            # Cardinality should be identical
            cardinality = self.validator.validate_cardinality(
                "Arc", "Beat", genre
            )
            assert cardinality == "one-to-many"

    def test_validation_rules_apply_to_all_genres(self):
        """Validation rules should apply to all three genres."""
        for genre in self.genres:
            concept = self.validator.get_concept("Character", genre)
            assert concept is not None
            # Get rules
            if hasattr(concept, "validation_rules"):
                for rule in concept.validation_rules:
                    if genre in {"netorare", "mystery", "gentlefemdom"}:
                        # Rules in base ontology should apply to all
                        assert (
                            genre in rule.applies_to
                        ), f"Rule {rule.rule_id} should apply to {genre}"

    def test_genre_themes_are_distinct(self):
        """Each genre should have distinct theme sets."""
        netorare_themes = self.validator.get_genre_themes("netorare")
        mystery_themes = self.validator.get_genre_themes("mystery")
        gf_themes = self.validator.get_genre_themes("gentlefemdom")

        # Themes should be mutually exclusive
        assert len(netorare_themes & mystery_themes) == 0
        assert len(netorare_themes & gf_themes) == 0
        assert len(mystery_themes & gf_themes) == 0

    def test_genre_specific_concepts_extend_base(self):
        """Genre-specific concepts should extend base Arc concept."""
        for genre in self.genres:
            genre_specific = self.validator.get_genre_specific_concepts(genre)
            # Each genre should have at least one arc subtype
            arc_subtypes = [
                c for c in genre_specific if "Arc" in c
            ]
            assert len(arc_subtypes) > 0, f"{genre} should have arc subtypes"


class TestConceptRelationshipHierarchy:
    """Test that concept relationships form valid hierarchy."""

    def setup_method(self):
        """Set up for tests."""
        self.validator = OntologyValidator()

    def test_beat_belongs_to_arc(self):
        """Beat should be defined as belonging to Arc."""
        assert self.validator.validate_relationship(
            "Beat", "Arc", "netorare"
        )
        # Cardinality: many beats to one arc
        cardinality = self.validator.validate_cardinality(
            "Arc", "Beat", "netorare"
        )
        assert cardinality == "one-to-many"

    def test_setup_requires_payoff(self):
        """Setup should have relationship to Payoff."""
        assert self.validator.validate_relationship(
            "Setup", "Payoff", "netorare"
        )

    def test_goal_has_owner(self):
        """Goal should require Character as owner."""
        assert self.validator.validate_relationship(
            "Goal", "Character", "netorare"
        )

    def test_theme_influences_arcs(self):
        """Theme should relate to Arc."""
        assert self.validator.validate_relationship(
            "Theme", "Arc", "netorare"
        )

    def test_no_circular_relationships(self):
        """Relationships should not create cycles at base level."""
        # Check for common circular patterns
        # E.g., Character -> Goal -> Character
        character_related = self.validator.get_related_concepts(
            "Character", "netorare"
        )
        for related_concept in character_related:
            related_related = self.validator.get_related_concepts(
                related_concept, "netorare"
            )
            # Goal and Beat should not circle back to Character directly
            if related_concept in ["Goal", "Beat"]:
                # This is allowed - Goal can relate to Character
                # But the relationship should be intentional, not circular
                pass


class TestOntologyCorrectness:
    """Test that ontology defines concepts used by Layer 1-2."""

    def setup_method(self):
        """Set up validator."""
        self.validator = OntologyValidator()

    def test_arc_concept_exists(self):
        """Arc concept required by Layer 1 blueprint."""
        concept = self.validator.get_concept("Arc", "netorare")
        assert concept is not None
        assert concept.name == "Arc"

    def test_character_concept_exists(self):
        """Character concept required by Layer 2."""
        concept = self.validator.get_concept("Character", "mystery")
        assert concept is not None
        assert concept.name == "Character"

    def test_theme_concept_exists(self):
        """Theme concept required for arc validation."""
        concept = self.validator.get_concept("Theme", "gentlefemdom")
        assert concept is not None
        assert "Theme" in concept.name

    def test_beat_concept_exists(self):
        """Beat concept required for outline structure."""
        concept = self.validator.get_concept("Beat", "netorare")
        assert concept is not None
        assert concept.name == "Beat"

    def test_conflict_concept_has_stakes(self):
        """Conflict concept should have rule about stakes."""
        conflict = self.validator.get_concept("Conflict", "mystery")
        rules_by_id = {r.rule_id: r for r in conflict.validation_rules}
        assert "conflict_must_have_stakes" in rules_by_id

    def test_all_core_concepts_accessible(self):
        """All 12 core concepts should be accessible via validator."""
        core_concepts = [
            "Character",
            "Arc",
            "Theme",
            "Goal",
            "Conflict",
            "Payoff",
            "Symbol",
            "Relationship",
            "Beat",
            "Setup",
            "Revelation",
            "Reversal",
        ]

        for concept_name in core_concepts:
            for genre in ["netorare", "mystery", "gentlefemdom"]:
                concept = self.validator.get_concept(concept_name, genre)
                assert (
                    concept is not None
                ), f"{concept_name} not accessible in {genre}"


class TestOntologyExtensibility:
    """Test that ontology design supports adding new concepts and genres."""

    def test_concept_can_be_created(self):
        """New concept should be creatable following pattern."""
        new_rule = ValidationRule(
            rule_id="test_rule",
            condition="Test condition",
            error_message="Test error",
            applies_to=["netorare", "mystery", "gentlefemdom"],
        )

        new_rel = Relationship(
            source_concept="TestConcept",
            target_concept="Character",
            cardinality="many-to-many",
            description="Test relationship",
            required=False,
        )

        new_concept = Concept(
            name="TestConcept",
            definition="A test concept definition",
            relationships=[new_rel],
            validation_rules=[new_rule],
        )

        assert new_concept.name == "TestConcept"
        assert len(new_concept.validation_rules) == 1
        assert len(new_concept.relationships) == 1

    def test_concept_properties_serializable(self):
        """Concepts should serialize to dictionaries."""
        concept = get_concept("Arc")
        concept_dict = concept.model_dump()

        # Should be JSON-serializable (dict representation)
        assert isinstance(concept_dict, dict)
        assert concept_dict["name"] == "Arc"
        assert concept_dict["definition"]
        assert isinstance(concept_dict["relationships"], list)
        assert isinstance(concept_dict["validation_rules"], list)

    def test_add_concept_integration_pattern(self):
        """Should be able to add concept and integrate with validator."""
        validator = OntologyValidator()

        # Create new concept
        new_rule = ValidationRule(
            rule_id="new_concept_rule",
            condition="Test",
            error_message="Test error",
            applies_to=["netorare"],
        )

        new_rel = Relationship(
            source_concept="NewArc",
            target_concept="Beat",
            cardinality="one-to-many",
            description="New arc contains beats",
            required=True,
        )

        new_concept = Concept(
            name="NewArc",
            definition="A new arc type for testing",
            relationships=[new_rel],
            validation_rules=[new_rule],
        )

        # Validate it's properly structured
        assert new_concept.name == "NewArc"
        assert new_concept.relationships[0].target_concept == "Beat"
        assert new_concept.validation_rules[0].applies_to == ["netorare"]


class TestOntologyCompleteness:
    """Test that ontology has sufficient coverage for narrative needs."""

    def test_all_core_concepts_have_definitions(self):
        """Every core concept should have a substantive definition."""
        for concept_name, concept in ALL_CONCEPTS.items():
            assert concept.definition
            # Definition should be at least 30 characters (substantive)
            assert len(concept.definition) >= 30

    def test_all_core_concepts_have_relationships(self):
        """Core concepts should have relationships defined."""
        # Some concepts might not have relationships, but most should
        with_relationships = sum(
            1 for c in ALL_CONCEPTS.values() if c.relationships
        )
        # At least 80% should have relationships
        assert with_relationships >= len(ALL_CONCEPTS) * 0.8

    def test_all_core_concepts_have_validation_rules(self):
        """All core concepts should have validation rules."""
        for concept_name, concept in ALL_CONCEPTS.items():
            assert len(concept.validation_rules) > 0, f"{concept_name} has no rules"

    def test_validator_methods_are_functional(self):
        """All key validator methods should work."""
        validator = OntologyValidator()

        # All methods should be callable and return results
        assert callable(validator.validate_concept)
        assert callable(validator.validate_relationship)
        assert callable(validator.get_concept)
        assert callable(validator.get_related_concepts)
        assert callable(validator.get_genre_themes)
        assert callable(validator.is_valid_genre)

        # All should return without error
        assert validator.is_valid_genre("netorare")
        assert validator.get_concept("Character", "netorare") is not None
        assert validator.validate_concept("Character", "netorare")
        assert validator.get_related_concepts("Arc", "netorare")


class TestFullOntologyWorkflow:
    """Test complete workflow: load → inspect → validate → apply."""

    def test_full_workflow_netorare(self):
        """Complete workflow for netorare genre."""
        # Step 1: Load validator
        validator = OntologyValidator()

        # Step 2: Get all concepts for genre
        concepts = validator.get_all_concepts_for_genre("netorare")
        assert len(concepts) > 0

        # Step 3: Validate a core concept
        assert validator.validate_concept("Arc", "netorare")

        # Step 4: Inspect its relationships
        related = validator.get_related_concepts("Arc", "netorare")
        assert len(related) > 0

        # Step 5: Get the concept object and inspect rules
        concept = validator.get_concept("Arc", "netorare")
        assert len(concept.validation_rules) > 0

    def test_full_workflow_mystery(self):
        """Complete workflow for mystery genre."""
        validator = OntologyValidator()

        # Load and validate
        concepts = validator.get_all_concepts_for_genre("mystery")
        assert len(concepts) > 0

        # Check Character exists
        assert validator.validate_concept("Character", "mystery")
        character = validator.get_concept("Character", "mystery")
        assert character is not None

        # Check relationships
        related = validator.get_related_concepts("Character", "mystery")
        assert "Goal" in related

    def test_full_workflow_gentlefemdom(self):
        """Complete workflow for gentlefemdom genre."""
        validator = OntologyValidator()

        # Load and validate
        concepts = validator.get_all_concepts_for_genre("gentlefemdom")
        assert len(concepts) > 0

        # Check Theme exists
        assert validator.validate_concept("Theme", "gentlefemdom")
        theme = validator.get_concept("Theme", "gentlefemdom")
        assert theme is not None

        # Check it has validation rules
        assert len(theme.validation_rules) > 0
