from __future__ import annotations

from pathlib import Path

from series_fixtures import valid_trilogy_data

from auteur.series.models import SeriesIdentity
from auteur.series.universe_integration import validate_series_against_universe
from auteur.universe.models import (
    CrossStoryConstraint,
    SettingProfile,
    TimelineProfile,
    UniverseIdentity,
)


def _series_with_universe(universe_path: Path) -> SeriesIdentity:
    """Build a valid SeriesIdentity that references a universe constraint file."""
    data = valid_trilogy_data()
    data["universe_constraint_path"] = str(universe_path)
    return SeriesIdentity.model_validate(data)


def test_series_with_universe_constraint_path(tmp_path):
    """SeriesIdentity can reference a UniverseIdentity file."""
    universe = UniverseIdentity(
        name="Fantasy World",
        slug="fantasy-world",
        description="A medieval fantasy setting",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="The Realm"),
        magic_system="Old magic tied to nature",
        core_mythology="Gods of the Four Elements",
        timeline=TimelineProfile(
            current_era="Age of Decline", era_description="Magic fades", years_of_history=5000
        ),
        forbidden_elements=["Modern technology"],
        required_elements=["Magic", "Medieval aesthetics"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="All books must feature magic as a core element",
                applies_to_all_stories=True,
                severity="required",
            )
        ],
    )

    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)

    series = _series_with_universe(universe_path)

    assert series.universe_constraint_path == universe_path


def test_validate_series_against_universe_constraints(tmp_path):
    """Series diagnostics should check universe constraint compliance."""
    universe = UniverseIdentity(
        name="Tech-Free World",
        slug="tech-free-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Wilderness"),
        magic_system="",
        core_mythology="",
        timeline=TimelineProfile(current_era="Now", era_description="", years_of_history=0),
        forbidden_elements=["Electricity", "Computers"],
        required_elements=["Nature", "Community"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="Technology should not solve narrative problems",
                applies_to_all_stories=True,
                severity="required",
            )
        ],
    )

    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)

    series = _series_with_universe(universe_path)

    diagnostics = validate_series_against_universe(series, universe)

    # For a coherent series, should have no errors
    errors = [d for d in diagnostics if d.severity.value == "error"]
    assert len(errors) == 0
