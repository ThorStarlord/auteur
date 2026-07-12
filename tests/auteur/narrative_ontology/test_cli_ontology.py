"""Tests for ontology CLI commands.

Tests the following commands:
- auteur ontology inspect <concept>
- auteur ontology inspect <concept> --genre netorare
- auteur ontology list
- auteur ontology validate <genre>
- auteur ontology themes <genre>
"""

from pathlib import Path
from auteur.cli import main
import json
import pytest


class TestOntologyInspect:
    """Test 'auteur ontology inspect' command."""

    def test_inspect_base_concept_shows_definition(self, capsys):
        """Inspect a base concept shows its definition and relationships."""
        rc = main(["ontology", "inspect", "Character"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Character" in out
        assert "definition" in out.lower()

    def test_inspect_base_concept_shows_relationships(self, capsys):
        """Inspect shows related concepts."""
        rc = main(["ontology", "inspect", "Character"])
        assert rc == 0
        out = capsys.readouterr().out
        assert ("Arc" in out or "Goal" in out)

    def test_inspect_nonexistent_concept_fails(self):
        """Inspecting a nonexistent concept returns error."""
        rc = main(["ontology", "inspect", "NonexistentConcept"])
        assert rc != 0

    def test_inspect_concept_with_genre_flag(self, capsys):
        """Inspect a concept with genre filter."""
        rc = main(["ontology", "inspect", "Character", "--genre", "netorare"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Character" in out

    def test_inspect_genre_specific_concept(self, capsys):
        """Inspect a genre-specific concept."""
        rc = main(["ontology", "inspect", "CuckoldryArc", "--genre", "netorare"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "CuckoldryArc" in out or "Cuckoldry" in out

    def test_inspect_invalid_genre_fails(self):
        """Inspecting with invalid genre returns error."""
        rc = main(["ontology", "inspect", "Character", "--genre", "invalid_genre"])
        assert rc != 0

    def test_inspect_outputs_json_with_flag(self, capsys):
        """Inspect with --json outputs valid JSON."""
        rc = main(["ontology", "inspect", "Character", "--json"])
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "name" in data
        assert data["name"] == "Character"


class TestOntologyList:
    """Test 'auteur ontology list' command."""

    def test_list_shows_all_base_concepts(self, capsys):
        """List shows all base concepts."""
        rc = main(["ontology", "list"])
        assert rc == 0
        out = capsys.readouterr().out
        # Should include major base concepts
        assert "Character" in out
        assert "Arc" in out
        assert "Theme" in out

    def test_list_with_genre_shows_genre_concepts(self, capsys):
        """List with genre shows genre-specific concepts."""
        rc = main(["ontology", "list", "--genre", "netorare"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Character" in out  # Base concepts included
        # Genre-specific concepts may appear

    def test_list_invalid_genre_fails(self):
        """List with invalid genre returns error."""
        rc = main(["ontology", "list", "--genre", "invalid_genre"])
        assert rc != 0

    def test_list_outputs_json_with_flag(self, capsys):
        """List with --json outputs valid JSON array."""
        rc = main(["ontology", "list", "--json"])
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "Character" in data


class TestOntologyValidate:
    """Test 'auteur ontology validate' command."""

    def test_validate_base_ontology_succeeds(self, capsys):
        """Validate base ontology structure."""
        rc = main(["ontology", "validate"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "valid" in out.lower()

    def test_validate_netorare_ontology(self, capsys):
        """Validate netorare genre ontology."""
        rc = main(["ontology", "validate", "netorare"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "valid" in out.lower()

    def test_validate_mystery_ontology(self, capsys):
        """Validate mystery genre ontology."""
        rc = main(["ontology", "validate", "mystery"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "valid" in out.lower()

    def test_validate_gentlefemdom_ontology(self, capsys):
        """Validate gentlefemdom genre ontology."""
        rc = main(["ontology", "validate", "gentlefemdom"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "valid" in out.lower()

    def test_validate_invalid_genre_fails(self):
        """Validate with invalid genre returns error."""
        rc = main(["ontology", "validate", "invalid_genre"])
        assert rc != 0

    def test_validate_outputs_errors_if_any(self, capsys):
        """Validate reports errors if structure is invalid."""
        # This tests the error reporting path
        rc = main(["ontology", "validate", "netorare"])
        out = capsys.readouterr().out
        # Should either report valid or list specific errors
        assert ("valid" in out.lower()) or ("error" in out.lower())


class TestOntologyThemes:
    """Test 'auteur ontology themes' command."""

    def test_themes_shows_genre_themes(self, capsys):
        """Themes command shows theme set for a genre."""
        rc = main(["ontology", "themes", "netorare"])
        assert rc == 0
        out = capsys.readouterr().out
        # Should show themes-related information
        assert len(out) > 0

    def test_themes_mystery_genre(self, capsys):
        """Themes command for mystery genre."""
        rc = main(["ontology", "themes", "mystery"])
        assert rc == 0
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_themes_gentlefemdom_genre(self, capsys):
        """Themes command for gentlefemdom genre."""
        rc = main(["ontology", "themes", "gentlefemdom"])
        assert rc == 0
        out = capsys.readouterr().out
        assert len(out) > 0

    def test_themes_invalid_genre_fails(self):
        """Themes with invalid genre returns error."""
        rc = main(["ontology", "themes", "invalid_genre"])
        assert rc != 0

    def test_themes_outputs_json_with_flag(self, capsys):
        """Themes with --json outputs valid JSON."""
        rc = main(["ontology", "themes", "netorare", "--json"])
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        # Should be dict or list with theme data
        assert isinstance(data, (dict, list))


class TestOntologyIntegration:
    """Integration tests for ontology commands."""

    def test_inspect_then_list_consistency(self, capsys):
        """Concepts listed should be inspectable."""
        rc = main(["ontology", "list", "--json"])
        assert rc == 0
        out = capsys.readouterr().out
        concepts = json.loads(out)

        # Try to inspect first concept
        if concepts:
            first_concept = concepts[0]
            rc = main(["ontology", "inspect", first_concept, "--json"])
            assert rc == 0

    def test_all_genres_validate(self):
        """All known genres must pass validation."""
        for genre in ["netorare", "mystery", "gentlefemdom"]:
            rc = main(["ontology", "validate", genre])
            assert rc == 0, f"Genre {genre} failed validation"

    def test_validate_base_then_genre(self):
        """Base validation passes before genre validation."""
        rc = main(["ontology", "validate"])
        assert rc == 0

        rc = main(["ontology", "validate", "netorare"])
        assert rc == 0
