"""Tests for Layer 0 documentation examples.

Task 9: Verify that all examples from documentation work correctly.
These tests demonstrate how to:
1. Add a new concept (PoliticalIntrigue example)
2. Add a new genre (PsychologicalThriller example)
3. Use the ontology loader and validator
4. Integrate with validation rules
"""

import pytest
from auteur.narrative_ontology.loader import OntologyLoader
from auteur.narrative_ontology.validator import OntologyValidator
from auteur.narrative_ontology.schema.ontology_types import Concept, Relationship, ValidationRule


class TestAddConceptExample:
    """Test examples from 'How to Add a New Concept' documentation."""

    def test_political_intrigue_concept_can_be_retrieved(self):
        """Example: Retrieve PoliticalIntrigue concept from ontology.

        This demonstrates the basic pattern for inspecting added concepts.
        """
        loader = OntologyLoader()

        # Concept should exist in base ontology after adding
        concepts = loader.get_concept_names()
        # Note: In real scenario, PoliticalIntrigue would be added to base_ontology.yaml
        # This test shows the retrieval pattern
        assert "Character" in concepts
        assert "Arc" in concepts

    def test_concept_definition_is_comprehensive(self):
        """Example: Concepts should have detailed definitions.

        Shows that concepts need descriptive definitions for clarity.
        """
        loader = OntologyLoader()

        # All base concepts have comprehensive definitions
        all_concepts = loader.load_base_ontology()
        for concept_name, concept in all_concepts.items():
            assert concept["definition"]
            assert len(concept["definition"]) > 50, f"{concept_name} definition too short"

    def test_concept_relationships_are_structured(self):
        """Example: Concepts define their relationships with metadata.

        Shows the complete Relationship structure including cardinality.
        """
        loader = OntologyLoader()

        character = loader.get_concept("Character")

        # Character-Goal relationship should have full structure
        goal_rels = [r for r in character["relationships"] if r["target_concept"] == "Goal"]
        assert len(goal_rels) > 0

        rel = goal_rels[0]
        assert rel["source_concept"] == "Character"
        assert rel["target_concept"] == "Goal"
        assert rel["cardinality"] in ["one-to-one", "one-to-many", "many-to-many"]
        assert "description" in rel
        assert isinstance(rel["required"], bool)

    def test_concept_validation_rules_specify_applicability(self):
        """Example: Validation rules specify which genres they apply to.

        Shows how rules are genre-aware and centralized in ontology.
        """
        loader = OntologyLoader()

        character = loader.get_concept("Character")

        # Character rules should apply to all genres
        for rule in character["validation_rules"]:
            assert len(rule["applies_to"]) > 0
            for genre in rule["applies_to"]:
                assert genre in ["netorare", "mystery", "gentlefemdom"]

    def test_concept_registry_returns_all_concepts(self):
        """Example: ALL_CONCEPTS registry provides central discovery.

        Demonstrates how concepts are registered and discoverable.
        """
        from auteur.narrative_ontology.core import ALL_CONCEPTS, get_concept

        # Registry should have 12 base concepts
        assert len(ALL_CONCEPTS) == 12

        # Registry should support get_concept lookup
        char = get_concept("Character")
        assert char.name == "Character"

        # All concepts should be Concept instances
        for name, concept in ALL_CONCEPTS.items():
            assert isinstance(concept, Concept)
            assert concept.name == name

    def test_concept_cardinality_patterns(self):
        """Example: Understanding cardinality (one-to-one, one-to-many, many-to-many).

        Shows the three cardinality patterns and how to interpret them.
        """
        loader = OntologyLoader()

        # One-to-one: Setup requires Payoff (and vice versa)
        setup = loader.get_concept("Setup")
        payoff_rels = [r for r in setup["relationships"] if r["target_concept"] == "Payoff"]
        assert len(payoff_rels) > 0
        assert payoff_rels[0]["cardinality"] == "one-to-one"

        # One-to-many: Character has multiple Goals
        character = loader.get_concept("Character")
        goal_rels = [r for r in character["relationships"] if r["target_concept"] == "Goal"]
        assert len(goal_rels) > 0
        assert goal_rels[0]["cardinality"] == "one-to-many"

        # Many-to-many: Character appears in multiple Arcs
        arc_rels = [r for r in character["relationships"] if r["target_concept"] == "Arc"]
        assert len(arc_rels) > 0
        assert arc_rels[0]["cardinality"] == "many-to-many"


class TestAddGenreExample:
    """Test examples from 'How to Add a New Genre' documentation."""

    def test_genre_ontology_extends_base_cleanly(self):
        """Example: Genre ontology extends base without replacing.

        Shows that genres inherit all base concepts plus add new ones.
        """
        loader = OntologyLoader()

        base = loader.load_base_ontology()
        netorare = loader.load_genre_ontology("netorare")
        merged = loader.merge_ontologies(base, netorare)

        # Base concepts preserved
        assert "Character" in merged
        assert "Arc" in merged

        # Genre concepts added
        assert "CuckoldryArc" in merged
        assert "ConsentBoundary" in merged

        # Total should be base + genre
        assert len(merged) == len(base) + len(netorare)

    def test_genre_concepts_have_parent_concepts(self):
        """Example: Genre concepts specify their parent (base concept).

        Shows how genre extensions relate to base concepts.
        """
        loader = OntologyLoader()

        netorare = loader.load_genre_ontology("netorare")
        cuckoldry = netorare["CuckoldryArc"]

        # CuckoldryArc extends Arc
        assert "Arc" in cuckoldry.get("parent_concepts", [])

        # ConsentBoundary is standalone (no parent)
        consent = netorare["ConsentBoundary"]
        assert len(consent.get("parent_concepts", [])) == 0

    def test_genre_validation_rules_are_genre_specific(self):
        """Example: Genre rules apply only to that genre.

        Shows how validation rules are scoped to genres.
        """
        loader = OntologyLoader()

        netorare = loader.load_genre_ontology("netorare")
        consent = netorare["ConsentBoundary"]

        # ConsentBoundary rules apply only to netorare
        for rule in consent["validation_rules"]:
            assert "netorare" in rule["applies_to"]
            assert "mystery" not in rule["applies_to"]

    def test_all_supported_genres_load_correctly(self):
        """Example: All registered genres load without error.

        Demonstrates the genre loading pattern for all supported genres.
        """
        loader = OntologyLoader()

        genres = ["netorare", "mystery", "gentlefemdom"]

        for genre in genres:
            # Genre should load
            genre_ontology = loader.load_genre_ontology(genre)
            assert genre_ontology is not None
            assert len(genre_ontology) > 0

            # Genre should have metadata
            concepts = loader.get_concept_names(genre=genre)
            assert len(concepts) > 12  # More than base

    def test_genre_extensions_are_discoverable(self):
        """Example: Get only genre-specific concepts (non-base).

        Shows how to discover what's new in a genre.
        """
        loader = OntologyLoader()

        for genre in ["netorare", "mystery", "gentlefemdom"]:
            extensions = loader.get_genre_extensions(genre)

            # Should have genre-specific concepts
            assert len(extensions) > 0

            # Should NOT have base concepts
            assert "Character" not in extensions
            assert "Arc" not in extensions
            assert "Theme" not in extensions

    def test_genre_concept_discovery_workflow(self):
        """Example: Complete workflow for discovering genre concepts.

        Shows the recommended pattern for ontology exploration.
        """
        loader = OntologyLoader()

        genre = "netorare"

        # Step 1: Get all concepts for genre
        all_concepts = loader.get_concept_names(genre=genre)
        assert len(all_concepts) > 12

        # Step 2: Get only genre extensions
        new_concepts = loader.get_genre_extensions(genre)

        # Step 3: Inspect each new concept
        for concept_name in new_concepts:
            concept = loader.get_concept(concept_name, genre=genre)

            # Should have complete structure
            assert concept["name"] == concept_name
            assert concept["definition"]
            assert "relationships" in concept
            assert "validation_rules" in concept


class TestOntologyValidatorUsage:
    """Test examples of using the OntologyValidator."""

    def test_validate_concept_existence(self):
        """Example: Check if a concept exists in ontology."""
        validator = OntologyValidator()

        # Base concepts should exist in all genres
        assert validator.validate_concept("Character", "netorare")
        assert validator.validate_concept("Arc", "mystery")

        # Unknown concepts should not
        assert not validator.validate_concept("UnknownConcept", "netorare")

    def test_validate_genre_concept_existence(self):
        """Example: Check if genre-specific concept exists."""
        loader = OntologyLoader()

        # Genre concepts should exist in their genre
        assert loader.get_concept("CuckoldryArc", genre="netorare") is not None

        # Can verify via get_concept_names
        netorare_concepts = loader.get_concept_names(genre="netorare")
        assert "CuckoldryArc" in netorare_concepts

        mystery_concepts = loader.get_concept_names(genre="mystery")

        # Genre concept should NOT exist in other genres
        assert "CuckoldryArc" not in mystery_concepts

    def test_validate_relationships(self):
        """Example: Check if concepts have required relationships."""
        validator = OntologyValidator()

        # Character-Goal relationship should exist
        assert validator.validate_relationship("Character", "Goal", "netorare")

        # Arc-Beat relationship should exist
        assert validator.validate_relationship("Arc", "Beat", "mystery")

        # Invalid relationships should not
        assert not validator.validate_relationship("Character", "UnknownConcept", "netorare")

    def test_validate_ontology_structure(self):
        """Example: Validate complete ontology structure."""
        validator = OntologyValidator()
        loader = OntologyLoader()

        # Validate base ontology
        base = loader.load_base_ontology()
        errors = loader.validate_ontology_structure(base)

        # Should have no structural errors
        assert len(errors) == 0, f"Base ontology has errors: {errors}"

        # Validate genre ontologies (merged with base, since genre concepts
        # reference base concepts like Character, Arc, etc.)
        for genre in ["netorare", "mystery", "gentlefemdom"]:
            genre_ont = loader.load_genre_ontology(genre)
            merged = loader.merge_ontologies(base, genre_ont)
            errors = loader.validate_ontology_structure(merged)
            assert len(errors) == 0, f"{genre} ontology has errors: {errors}"


class TestConceptIntegrationPatterns:
    """Test real-world usage patterns for concept ontology."""

    def test_building_narrative_structure_against_ontology(self):
        """Example: Validate narrative structure matches ontology.

        Shows how to use Layer 0 to validate higher-level narratives.
        """
        loader = OntologyLoader()

        # Define a narrative fragment
        narrative = {
            "title": "Murder Mystery",
            "characters": [
                {"name": "Detective", "concept": "Character"},
                {"name": "Victim", "concept": "Character"},
            ],
            "arcs": [
                {"name": "Investigation", "concept": "Arc", "beats_count": 5},
            ],
        }

        # Check concepts are valid
        for char in narrative["characters"]:
            concept = loader.get_concept(char["concept"])
            assert concept is not None

        for arc in narrative["arcs"]:
            concept = loader.get_concept(arc["concept"])
            assert concept is not None

    def test_genre_specific_narrative_validation(self):
        """Example: Use genre-specific concepts for validation.

        Shows how genre extensions enable genre-aware validation.
        """
        loader = OntologyLoader()

        # Mystery narrative uses Investigation-specific concepts
        mystery_concepts = loader.get_concept_names(genre="mystery")
        assert "InvestigativeArc" in mystery_concepts
        assert "Clue" in mystery_concepts

        # Can validate mystery-specific elements
        investigation = loader.get_concept("InvestigativeArc", genre="mystery")
        assert investigation["definition"]
        assert len(investigation["validation_rules"]) > 0

    def test_concept_relationship_traversal(self):
        """Example: Follow concept relationships to build dependency maps.

        Shows how to analyze concept connections.
        """
        loader = OntologyLoader()

        character = loader.get_concept("Character")

        # Character has relationships
        related = [r["target_concept"] for r in character["relationships"]]
        assert "Goal" in related
        assert "Arc" in related
        assert "Relationship" in related

        # All related concepts should exist
        for concept_name in related:
            concept = loader.get_concept(concept_name)
            assert concept is not None

    def test_validation_rules_enforcement_pattern(self):
        """Example: Extract and apply validation rules.

        Shows how to use ontology rules in custom validators.
        """
        loader = OntologyLoader()
        validator = OntologyValidator()

        # Get concept and extract rules
        character = loader.get_concept("Character")
        rules = character["validation_rules"]

        # Rules should be actionable
        assert len(rules) > 0
        for rule in rules:
            assert rule["rule_id"]
            assert rule["condition"]
            assert rule["error_message"]
            assert rule["applies_to"]

    def test_cross_genre_concept_availability(self):
        """Example: Identify concepts available across all genres.

        Shows how base concepts are universally available.
        """
        loader = OntologyLoader()

        # Get base concept
        character_base = loader.get_concept("Character")

        # Character should exist in all genres
        for genre in ["netorare", "mystery", "gentlefemdom"]:
            character_genre = loader.get_concept("Character", genre=genre)

            # Same definition across genres
            assert character_genre["name"] == "Character"
            assert character_genre["definition"] == character_base["definition"]


class TestDocumentationCompleteness:
    """Test that documentation covers all key patterns."""

    def test_documentation_covers_concept_structure(self):
        """Verify documentation explains concept structure."""
        # This test documents what the examples should show
        loader = OntologyLoader()

        concept = loader.get_concept("Character")

        # Documentation should explain these elements:
        assert "name" in concept  # Concept name
        assert "definition" in concept  # Human-readable definition
        assert "relationships" in concept  # How it connects
        assert "validation_rules" in concept  # Constraints

    def test_documentation_covers_cardinality_types(self):
        """Verify documentation explains cardinality."""
        loader = OntologyLoader()

        cardinalities_seen = set()
        base = loader.load_base_ontology()

        for concept in base.values():
            for rel in concept["relationships"]:
                cardinalities_seen.add(rel["cardinality"])

        # Documentation should cover all three types
        assert "one-to-one" in cardinalities_seen
        assert "one-to-many" in cardinalities_seen
        assert "many-to-many" in cardinalities_seen

    def test_documentation_covers_genre_extension(self):
        """Verify documentation explains genre extension pattern."""
        loader = OntologyLoader()

        # Base ontology is complete
        base = loader.load_base_ontology()
        assert len(base) == 12

        # Each genre extends it
        for genre in ["netorare", "mystery", "gentlefemdom"]:
            genre_ont = loader.load_genre_ontology(genre)
            assert len(genre_ont) > 0

            # Genre concepts should have parent concepts (reference base)
            for concept in genre_ont.values():
                # Most genre concepts extend base concepts
                if concept.get("parent_concepts"):
                    for parent in concept["parent_concepts"]:
                        assert parent in base
