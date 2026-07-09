"""Tests: genre pipeline registry allows third-party genre implementations."""

import pytest
from auteur.genres.registry import (
    GenrePipelineSpec,
    get_genre_pipeline,
    get_all_genres,
)
from auteur.blueprint import Genre


class TestGenrePipelineRegistry:
    """Verify registry treats all genres as equivalent."""

    def test_registry_returns_all_three_genres(self):
        """Registry returns specs for netorare, mystery, gentlefemdom."""
        genres = get_all_genres()
        assert len(genres) >= 3
        genre_ids = [g.genre for g in genres]
        assert Genre.NETORARE in genre_ids
        assert Genre.MYSTERY in genre_ids
        assert Genre.GENTLEFEMDOM in genre_ids

    def test_get_genre_pipeline_netorare(self):
        """Get netorare spec from registry."""
        spec = get_genre_pipeline(Genre.NETORARE)
        assert spec.genre == Genre.NETORARE
        assert spec.slug == "netorare"
        assert "classic_humiliation" in spec.core_ids
        assert "horror" in spec.core_ids

    def test_get_genre_pipeline_gentlefemdom(self):
        """Get gentlefemdom spec from registry."""
        spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
        assert spec.genre == Genre.GENTLEFEMDOM
        assert spec.slug == "gentlefemdom"
        assert "sensual_dominance" in spec.core_ids
        assert "tender_surrender" in spec.core_ids
        assert "romantic_authority" in spec.core_ids

    def test_spec_has_template_factory(self):
        """Each spec has factory for creating templates."""
        spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
        template = spec.template_factory("sensual_dominance")
        assert template.core_id == "sensual_dominance"
        assert template.primary_emotion == "playful_control"

    def test_spec_has_validate_choices_function(self):
        """Each spec has validation function."""
        spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
        template = spec.template_factory("sensual_dominance")
        choices = {4: {"want": "want-establish-trust"}}
        result = spec.validate_choices(template, choices)
        assert isinstance(result, tuple)
        assert len(result) == 3  # (is_valid, errors, warnings)

    def test_spec_has_identity_strategy(self):
        """Each spec has identity generation strategy."""
        spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
        assert callable(spec.identity_strategy)

    def test_get_genre_pipeline_mystery(self):
        """Get mystery spec from registry."""
        spec = get_genre_pipeline(Genre.MYSTERY)
        assert spec.genre == Genre.MYSTERY
        assert spec.slug == "mystery"
        assert "howdunit" in spec.core_ids
        assert "paranoia" in spec.core_ids
        assert "cozy" in spec.core_ids
