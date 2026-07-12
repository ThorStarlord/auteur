"""Tests for narrative ontology schema types."""

import pytest
from auteur.narrative_ontology.schema.ontology_types import (
    Concept,
    Relationship,
    ValidationRule,
    GenreOntologyExtension,
)


class TestConceptCreation:
    """Test Concept model creation and validation."""

    def test_concept_creation_with_all_fields(self):
        """Test successful creation with all required fields."""
        concept = Concept(
            name="Character",
            definition="A person in the narrative",
            relationships=[],
            validation_rules=[],
        )
        assert concept.name == "Character"
        assert concept.definition == "A person in the narrative"
        assert concept.relationships == []
        assert concept.validation_rules == []

    def test_concept_with_relationships(self):
        """Test Concept with relationships."""
        rel = Relationship(
            source_concept="Character",
            target_concept="Plot",
            cardinality="many-to-many",
            description="Characters participate in plots",
            required=True,
        )
        concept = Concept(
            name="Character",
            definition="A person in the narrative",
            relationships=[rel],
            validation_rules=[],
        )
        assert len(concept.relationships) == 1
        assert concept.relationships[0].target_concept == "Plot"

    def test_concept_with_validation_rules(self):
        """Test Concept with validation rules."""
        rule = ValidationRule(
            rule_id="char_01",
            condition="character must have motivation",
            error_message="Every character needs a motivation",
            applies_to=["netorare", "mystery", "gentlefemdom"],
        )
        concept = Concept(
            name="Character",
            definition="A person in the narrative",
            relationships=[],
            validation_rules=[rule],
        )
        assert len(concept.validation_rules) == 1
        assert concept.validation_rules[0].rule_id == "char_01"

    def test_concept_name_immutable(self):
        """Test that concept name is stored correctly."""
        concept = Concept(
            name="TestName",
            definition="A test definition",
            relationships=[],
            validation_rules=[],
        )
        assert concept.name == "TestName"


class TestRelationshipCreation:
    """Test Relationship model creation and validation."""

    def test_relationship_creation_one_to_one(self):
        """Test relationship creation with one-to-one cardinality."""
        rel = Relationship(
            source_concept="Character",
            target_concept="Protagonist",
            cardinality="one-to-one",
            description="Each character can be one protagonist",
            required=True,
        )
        assert rel.source_concept == "Character"
        assert rel.target_concept == "Protagonist"
        assert rel.cardinality == "one-to-one"
        assert rel.required is True

    def test_relationship_creation_one_to_many(self):
        """Test relationship creation with one-to-many cardinality."""
        rel = Relationship(
            source_concept="Plot",
            target_concept="Scene",
            cardinality="one-to-many",
            description="One plot contains many scenes",
            required=True,
        )
        assert rel.cardinality == "one-to-many"

    def test_relationship_creation_many_to_many(self):
        """Test relationship creation with many-to-many cardinality."""
        rel = Relationship(
            source_concept="Character",
            target_concept="Plot",
            cardinality="many-to-many",
            description="Characters participate in plots",
            required=False,
        )
        assert rel.cardinality == "many-to-many"
        assert rel.required is False

    def test_relationship_invalid_cardinality(self):
        """Test that invalid cardinality raises error."""
        with pytest.raises((ValueError, TypeError)):
            Relationship(
                source_concept="A",
                target_concept="B",
                cardinality="invalid-cardinality",
                description="test",
                required=True,
            )


class TestValidationRuleCreation:
    """Test ValidationRule model creation and validation."""

    def test_validation_rule_creation(self):
        """Test successful ValidationRule creation."""
        rule = ValidationRule(
            rule_id="rule_001",
            condition="character.motivation != ''",
            error_message="Character must have a motivation",
            applies_to=["netorare", "mystery"],
        )
        assert rule.rule_id == "rule_001"
        assert rule.condition == "character.motivation != ''"
        assert rule.error_message == "Character must have a motivation"
        assert rule.applies_to == ["netorare", "mystery"]

    def test_validation_rule_with_all_genres(self):
        """Test ValidationRule that applies to all genres."""
        rule = ValidationRule(
            rule_id="rule_002",
            condition="plot.has_climax",
            error_message="Every plot must have a climax",
            applies_to=["netorare", "mystery", "gentlefemdom"],
        )
        assert len(rule.applies_to) == 3

    def test_validation_rule_with_single_genre(self):
        """Test ValidationRule that applies to single genre."""
        rule = ValidationRule(
            rule_id="rule_003",
            condition="netorare_specific_condition",
            error_message="This only applies to netorare",
            applies_to=["netorare"],
        )
        assert rule.applies_to == ["netorare"]

    def test_validation_rule_condition_is_string(self):
        """Test that condition is always a string."""
        rule = ValidationRule(
            rule_id="rule_004",
            condition="is_valid() and has_coherence()",
            error_message="Not valid",
            applies_to=["mystery"],
        )
        assert isinstance(rule.condition, str)


class TestGenreOntologyExtension:
    """Test GenreOntologyExtension model creation and validation."""

    def test_genre_extension_creation(self):
        """Test successful GenreOntologyExtension creation."""
        extension = GenreOntologyExtension(
            genre="netorare",
            extends="base",
            new_concepts=["Humiliation", "Betrayal"],
            metadata={"version": "1.0"},
        )
        assert extension.genre == "netorare"
        assert extension.extends == "base"
        assert extension.new_concepts == ["Humiliation", "Betrayal"]
        assert extension.metadata == {"version": "1.0"}

    def test_genre_extension_with_default_extends(self):
        """Test GenreOntologyExtension with default extends value."""
        extension = GenreOntologyExtension(
            genre="mystery",
            extends="base",
            new_concepts=["Clue", "Red Herring"],
            metadata={},
        )
        assert extension.extends == "base"

    def test_genre_extension_extends_another_genre(self):
        """Test GenreOntologyExtension extending another genre."""
        extension = GenreOntologyExtension(
            genre="mystery_cozy",
            extends="mystery",
            new_concepts=["Sleepy Town"],
            metadata={"subgenre": "cozy"},
        )
        assert extension.extends == "mystery"

    def test_genre_extension_with_empty_metadata(self):
        """Test GenreOntologyExtension with empty metadata."""
        extension = GenreOntologyExtension(
            genre="gentlefemdom",
            extends="base",
            new_concepts=["Power Exchange"],
            metadata={},
        )
        assert extension.metadata == {}

    def test_genre_extension_with_multiple_new_concepts(self):
        """Test GenreOntologyExtension with multiple new concepts."""
        new_concepts = [
            "Dominance",
            "Submission",
            "Consent",
            "Power Dynamic",
        ]
        extension = GenreOntologyExtension(
            genre="gentlefemdom",
            extends="base",
            new_concepts=new_concepts,
            metadata={"core_count": 3},
        )
        assert len(extension.new_concepts) == 4
        assert "Dominance" in extension.new_concepts


class TestIntegration:
    """Integration tests across multiple types."""

    def test_concept_with_multiple_relationships_and_rules(self):
        """Test Concept with multiple relationships and rules."""
        rel1 = Relationship(
            source_concept="Plot",
            target_concept="Scene",
            cardinality="one-to-many",
            description="Plot contains scenes",
            required=True,
        )
        rel2 = Relationship(
            source_concept="Plot",
            target_concept="Character",
            cardinality="many-to-many",
            description="Plot involves characters",
            required=True,
        )
        rule1 = ValidationRule(
            rule_id="plot_01",
            condition="plot.has_climax",
            error_message="Plot must have climax",
            applies_to=["netorare", "mystery", "gentlefemdom"],
        )
        rule2 = ValidationRule(
            rule_id="plot_02",
            condition="plot.is_coherent",
            error_message="Plot must be coherent",
            applies_to=["mystery"],
        )
        concept = Concept(
            name="Plot",
            definition="A series of events",
            relationships=[rel1, rel2],
            validation_rules=[rule1, rule2],
        )
        assert len(concept.relationships) == 2
        assert len(concept.validation_rules) == 2

    def test_all_three_genres_use_same_types(self):
        """Test that all three genres can use the same type definitions."""
        genres = ["netorare", "mystery", "gentlefemdom"]

        for genre in genres:
            concept = Concept(
                name="GenericConcept",
                definition="A concept used in all genres",
                relationships=[],
                validation_rules=[],
            )
            extension = GenreOntologyExtension(
                genre=genre,
                extends="base",
                new_concepts=[],
                metadata={},
            )
            assert concept.name == "GenericConcept"
            assert extension.genre == genre

    def test_relationship_targets_can_reference_concepts(self):
        """Test that relationships can properly reference concepts."""
        concept1 = Concept(
            name="Character",
            definition="A character",
            relationships=[],
            validation_rules=[],
        )
        concept2_name = "Plot"

        rel = Relationship(
            source_concept=concept1.name,
            target_concept=concept2_name,
            cardinality="many-to-many",
            description="Characters participate in plots",
            required=True,
        )
        assert rel.source_concept == "Character"
        assert rel.target_concept == "Plot"

    def test_validation_rule_applies_to_genres(self):
        """Test that validation rules properly specify genre applicability."""
        rule = ValidationRule(
            rule_id="universal_rule",
            condition="must_be_coherent",
            error_message="All stories must be coherent",
            applies_to=["netorare", "mystery", "gentlefemdom"],
        )

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            assert genre in rule.applies_to
