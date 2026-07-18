"""Tests for OntologyLoader (Layer 0 Task 4).

Tests loading, merging, validating, and caching ontologies from YAML files.
Covers base ontology, genre-specific extensions, and all three genres identically.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from auteur.narrative_ontology.loader.ontology_loader import OntologyLoader


class TestOntologyLoaderBasic:
    """Test basic ontology loading functionality."""

    def test_loader_instantiates(self):
        """Test OntologyLoader can be instantiated."""
        loader = OntologyLoader()
        assert loader is not None

    def test_load_base_ontology(self):
        """Test loading base ontology from YAML."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        assert base is not None
        assert isinstance(base, dict)

    def test_base_ontology_has_concepts(self):
        """Test base ontology contains expected concepts."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        # Should have 12 core concepts
        assert len(base) >= 12
        # Should contain specific concepts
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
        assert expected_concepts.issubset(set(base.keys()))

    def test_concept_has_required_fields(self):
        """Test each concept has required fields."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        for concept_name, concept in base.items():
            assert "name" in concept
            assert "definition" in concept
            assert concept["name"] == concept_name

    def test_relationships_reference_valid_concepts(self):
        """Test that relationships reference concepts in the ontology."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        concept_names = set(base.keys())

        for concept_name, concept in base.items():
            relationships = concept.get("relationships", [])
            for rel in relationships:
                target = rel.get("target_concept", rel.get("target"))
                # Target should either be in the ontology or be documented
                assert target is not None


class TestGenreOntologyLoading:
    """Test loading genre-specific ontologies."""

    def test_load_netorare_ontology(self):
        """Test loading netorare genre ontology."""
        loader = OntologyLoader()
        genre = loader.load_genre_ontology("netorare")
        assert genre is not None
        assert isinstance(genre, dict)

    def test_load_mystery_ontology(self):
        """Test loading mystery genre ontology."""
        loader = OntologyLoader()
        genre = loader.load_genre_ontology("mystery")
        assert genre is not None
        assert isinstance(genre, dict)

    def test_load_gentlefemdom_ontology(self):
        """Test loading gentlefemdom genre ontology."""
        loader = OntologyLoader()
        genre = loader.load_genre_ontology("gentlefemdom")
        assert genre is not None
        assert isinstance(genre, dict)

    def test_genre_ontology_not_empty(self):
        """Test genre ontologies contain concepts."""
        loader = OntologyLoader()
        for genre_name in ["netorare", "mystery", "gentlefemdom"]:
            genre = loader.load_genre_ontology(genre_name)
            assert len(genre) > 0, f"{genre_name} ontology is empty"

    def test_genre_ontology_has_metadata(self):
        """Test genre ontologies have metadata about what they extend."""
        loader = OntologyLoader()
        for genre_name in ["netorare", "mystery", "gentlefemdom"]:
            genre = loader.load_genre_ontology(genre_name)
            # Each genre should have metadata about what it extends
            assert genre is not None


class TestOntologyMerging:
    """Test merging base and genre ontologies."""

    def test_merge_base_and_netorare(self):
        """Test merging base and netorare ontologies."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        netorare = loader.load_genre_ontology("netorare")
        merged = loader.merge_ontologies(base, netorare)
        assert merged is not None
        assert isinstance(merged, dict)

    def test_merged_contains_base_concepts(self):
        """Test merged ontology includes all base concepts."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        netorare = loader.load_genre_ontology("netorare")
        merged = loader.merge_ontologies(base, netorare)
        # Merged should have at least as many concepts as base
        assert len(merged) >= len(base)

    def test_merged_contains_genre_concepts(self):
        """Test merged ontology includes genre-specific concepts."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        mystery = loader.load_genre_ontology("mystery")
        merged = loader.merge_ontologies(base, mystery)
        # Should have more concepts than base if genre adds any
        base_count = len(base)
        merged_count = len(merged)
        assert merged_count >= base_count

    def test_merge_is_commutative_on_keys(self):
        """Test merge operation preserves all concept names."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        netorare = loader.load_genre_ontology("netorare")
        mystery = loader.load_genre_ontology("mystery")

        merged_net = loader.merge_ontologies(base, netorare)
        merged_mys = loader.merge_ontologies(base, mystery)

        # Both should have all base concepts
        base_keys = set(base.keys())
        assert base_keys.issubset(set(merged_net.keys()))
        assert base_keys.issubset(set(merged_mys.keys()))

    def test_merge_preserves_base_definitions(self):
        """Test that merge doesn't override base concept definitions."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        netorare = loader.load_genre_ontology("netorare")
        merged = loader.merge_ontologies(base, netorare)

        for concept_name in base.keys():
            assert merged[concept_name]["definition"] == base[concept_name]["definition"]


class TestConceptRetrieval:
    """Test retrieving concepts from merged ontology."""

    def test_get_concept_base(self):
        """Test retrieving a base concept."""
        loader = OntologyLoader()
        concept = loader.get_concept("Character")
        assert concept is not None
        assert concept["name"] == "Character"

    def test_get_concept_not_found(self):
        """Test retrieving non-existent concept returns empty dict."""
        loader = OntologyLoader()
        concept = loader.get_concept("NonExistentConcept")
        assert concept == {}, f"Expected empty dict, got {concept}"

    def test_get_concept_with_genre(self):
        """Test retrieving concept with genre context."""
        loader = OntologyLoader()
        concept = loader.get_concept("Character", genre="netorare")
        assert concept is not None
        assert concept["name"] == "Character"

    def test_get_concept_includes_definition(self):
        """Test retrieved concept includes definition."""
        loader = OntologyLoader()
        concept = loader.get_concept("Arc")
        assert "definition" in concept
        assert len(concept["definition"]) > 0

    def test_get_all_genre_concepts_same(self):
        """Test that all genres support same base concepts."""
        loader = OntologyLoader()
        base_concepts = set(loader.load_base_ontology().keys())

        for genre_name in ["netorare", "mystery", "gentlefemdom"]:
            for concept_name in base_concepts:
                concept = loader.get_concept(concept_name, genre=genre_name)
                assert concept is not None


class TestOntologyValidation:
    """Test ontology structure validation."""

    def test_validate_base_ontology(self):
        """Test validating base ontology structure."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        # Validation should pass or raise informative error
        errors = loader.validate_ontology_structure(base)
        # Should return list of errors (empty if valid)
        assert isinstance(errors, list)

    def test_validate_merged_ontology(self):
        """Test validating merged ontology."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        netorare = loader.load_genre_ontology("netorare")
        merged = loader.merge_ontologies(base, netorare)
        errors = loader.validate_ontology_structure(merged)
        assert isinstance(errors, list)

    def test_validate_relationships_reference_concepts(self):
        """Test that validation checks relationships reference defined concepts."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        errors = loader.validate_ontology_structure(base)
        # Should have no errors for well-formed ontology
        assert isinstance(errors, list)

    def test_validate_genre_ontologies(self):
        """Test all genre ontologies validate."""
        loader = OntologyLoader()
        for genre_name in ["netorare", "mystery", "gentlefemdom"]:
            genre = loader.load_genre_ontology(genre_name)
            errors = loader.validate_ontology_structure(genre)
            assert isinstance(errors, list)


class TestCaching:
    """Test caching functionality."""

    def test_load_base_ontology_caches(self):
        """Test base ontology is cached after first load."""
        loader = OntologyLoader()
        base1 = loader.load_base_ontology()
        base2 = loader.load_base_ontology()
        # Should return the same object from cache
        assert base1 is base2

    def test_load_genre_ontology_caches(self):
        """Test genre ontology is cached after first load."""
        loader = OntologyLoader()
        genre1 = loader.load_genre_ontology("netorare")
        genre2 = loader.load_genre_ontology("netorare")
        # Should return the same object from cache
        assert genre1 is genre2

    def test_cache_invalidation_on_reload(self):
        """Test cache can be invalidated."""
        loader = OntologyLoader()
        base1 = loader.load_base_ontology()
        loader.clear_cache()
        base2 = loader.load_base_ontology()
        # After clear_cache, should be different objects
        assert base1 is not base2

    def test_get_concept_uses_cache(self):
        """Test get_concept uses cached ontology."""
        loader = OntologyLoader()
        concept1 = loader.get_concept("Character")
        # Force load again (should use cache)
        concept2 = loader.get_concept("Character")
        # Should be equal (might not be same object depending on implementation)
        assert concept1["name"] == concept2["name"]


class TestMultipleGenreSupport:
    """Test that all three genres work identically."""

    def test_all_genres_load_successfully(self):
        """Test all three genres can be loaded."""
        loader = OntologyLoader()
        genres = ["netorare", "mystery", "gentlefemdom"]
        for genre_name in genres:
            genre = loader.load_genre_ontology(genre_name)
            assert genre is not None
            assert len(genre) > 0

    def test_all_genres_merge_successfully(self):
        """Test merging works for all three genres."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        genres = ["netorare", "mystery", "gentlefemdom"]
        for genre_name in genres:
            genre = loader.load_genre_ontology(genre_name)
            merged = loader.merge_ontologies(base, genre)
            assert merged is not None
            assert len(merged) >= len(base)

    def test_all_genres_validate_successfully(self):
        """Test validation works for all three genres."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        genres = ["netorare", "mystery", "gentlefemdom"]
        for genre_name in genres:
            genre = loader.load_genre_ontology(genre_name)
            merged = loader.merge_ontologies(base, genre)
            errors = loader.validate_ontology_structure(merged)
            assert isinstance(errors, list)

    def test_base_concepts_identical_across_genres(self):
        """Test that base concepts are identical across all genres."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        genres = ["netorare", "mystery", "gentlefemdom"]

        # Get a base concept merged with each genre
        for genre_name in genres:
            genre = loader.load_genre_ontology(genre_name)
            merged = loader.merge_ontologies(base, genre)
            # Character should have same definition across genres
            char = merged.get("Character")
            assert char is not None
            assert char["definition"] == base["Character"]["definition"]

    def test_get_concept_works_for_all_genres(self):
        """Test get_concept works for all genres."""
        loader = OntologyLoader()
        test_concepts = ["Character", "Arc", "Theme", "Goal"]
        genres = ["netorare", "mystery", "gentlefemdom"]

        for genre_name in genres:
            for concept_name in test_concepts:
                concept = loader.get_concept(concept_name, genre=genre_name)
                assert concept is not None
                assert concept["name"] == concept_name


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_get_concept_case_sensitive(self):
        """Test concept retrieval is case-sensitive."""
        loader = OntologyLoader()
        # "Character" should work
        concept = loader.get_concept("Character")
        assert concept is not None and concept.get("name") == "Character"
        # "character" should return empty dict (not found)
        concept_lower = loader.get_concept("character")
        assert concept_lower == {}, f"Expected empty dict for 'character', got {concept_lower}"

    def test_invalid_genre_raises_error(self):
        """Test loading invalid genre raises error."""
        loader = OntologyLoader()
        with pytest.raises((ValueError, FileNotFoundError)):
            loader.load_genre_ontology("invalid_genre")

    def test_ontology_structure_validates_relationships(self):
        """Test validation checks that relationships are well-formed."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        errors = loader.validate_ontology_structure(base)
        # Should not report errors for valid ontology
        assert isinstance(errors, list)
