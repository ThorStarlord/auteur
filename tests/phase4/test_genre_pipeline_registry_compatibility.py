"""Compatibility tests for built-in genre pipeline registry imports."""

from auteur.blueprint import Genre
from auteur.genres.registry import get_all_genres, get_genre_pipeline


def test_registry_returns_all_three_built_in_genres():
    specs = get_all_genres()
    genre_ids = [spec.genre for spec in specs]

    assert len(specs) >= 3
    assert Genre.NETORARE in genre_ids
    assert Genre.MYSTERY in genre_ids
    assert Genre.GENTLEFEMDOM in genre_ids


def test_registry_specs_expose_templates_and_profiles():
    gentle = get_genre_pipeline(Genre.GENTLEFEMDOM)
    netorare = get_genre_pipeline(Genre.NETORARE)
    mystery = get_genre_pipeline(Genre.MYSTERY)

    assert {"classic_humiliation", "horror", "mystery"} <= set(netorare.core_ids)
    assert {"howdunit", "paranoia", "cozy"} <= set(mystery.core_ids)
    assert {
        "sensual_dominance",
        "tender_surrender",
        "romantic_authority",
    } <= set(gentle.core_ids)

    template = gentle.template_factory("sensual_dominance")
    profile = gentle.identity_profile_factory("sensual_dominance")
    assert template.primary_emotion == "playful_control"
    assert profile.default_title == "Untitled: Sensual Dominance"


def test_registered_validator_retains_tuple_interface():
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    template = spec.template_factory("sensual_dominance")

    result = spec.validate_choices(template, {4: {"want": "want-establish-trust"}})

    assert isinstance(result, tuple)
    assert len(result) == 3

