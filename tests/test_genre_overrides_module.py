"""Tests for the auteur.structure.genres module."""

from __future__ import annotations


def test_genres_module_exports_override_rule_ids() -> None:
    """The genres module should export the glossary-documented rule ID constants."""
    from auteur.structure.genres import (
        FORBIDDEN_MISMATCH_OVERRIDE_BYPASSED,
        RUNWAY_OVERRIDE_BYPASSED,
    )

    assert FORBIDDEN_MISMATCH_OVERRIDE_BYPASSED == "genre.forbidden_mismatch.override_bypassed"
    assert RUNWAY_OVERRIDE_BYPASSED == "genre.runway.override_bypassed"


def test_genres_module_exports_genre_override() -> None:
    """The genres module should re-export GenreOverride and OverrideType."""
    from auteur.structure.genres import GenreOverride, OverrideType

    assert GenreOverride is not None
    assert OverrideType is not None


def test_analyzer_produces_genre_diagnostic_rules() -> None:
    """run_all_diagnostics should produce diagnostics with genre.* rules when
    a genre mismatch exists and no override is declared."""
    from auteur.blueprint import StoryBlueprint
    from auteur.structure.analyzer import analyze_structure
    from tests.test_structure_analyzer import _blueprint_data_with_story_engine

    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "netorare"
    data["identity"]["length_class"] = "short_story"

    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(bp)

    # Should produce at least one diagnostic with a genre.* rule prefix
    genre_rules = [d for d in diagnostics if d.rule.startswith("genre.")]
    assert len(genre_rules) > 0, (
        "Expected at least one genre.* diagnostic for a Netorare short story"
    )
