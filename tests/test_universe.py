import pytest
from pathlib import Path
from auteur.universe.models import (
    UniverseIdentity,
    SettingProfile,
    MythologyProfile,
    TimelineProfile,
    CrossStoryConstraint,
)


def test_universe_identity_requires_name_and_slug():
    """UniverseIdentity cannot be created without name and slug."""
    with pytest.raises(ValueError):
        UniverseIdentity(name="", slug="test")
    with pytest.raises(ValueError):
        UniverseIdentity(name="Test", slug="")


def test_universe_identity_slug_must_be_lowercase_and_safe():
    """Universe slug must match pattern: lowercase, hyphens, underscores, no spaces or special chars."""
    valid = UniverseIdentity(name="My World", slug="my-world", description="", setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"), magic_system="", core_mythology="", timeline=TimelineProfile(current_era="Present Day", era_description="", years_of_history=0), forbidden_elements=[], required_elements=[], cross_story_constraints=[])
    assert valid.slug == "my-world"

    with pytest.raises(ValueError):
        UniverseIdentity(name="My World", slug="My World", description="", setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"), magic_system="", core_mythology="", timeline=TimelineProfile(current_era="Present Day", era_description="", years_of_history=0), forbidden_elements=[], required_elements=[], cross_story_constraints=[])


def test_universe_identity_yaml_round_trip(tmp_path):
    """UniverseIdentity can be written to YAML and loaded back identically."""
    universe = UniverseIdentity(
        name="Steampunk Mystique",
        slug="steampunk-mystique",
        description="A world blending Victorian aesthetics with hidden magic.",
        setting_profile=SettingProfile(
            setting_type="single_world",
            primary_location="Cogsworth Empire",
            known_locations=["Capital City", "Industrial Wastelands"],
            worldbuilding_scope="regional"
        ),
        magic_system="Rune-based enchantment inscribed on mechanical devices",
        core_mythology="Ancient clockwork deity awakening",
        timeline=TimelineProfile(
            current_era="Industrial Revolution",
            era_description="1880s analog world",
            years_of_history=200
        ),
        forbidden_elements=["Modern technology (electricity)", "Digital AI"],
        required_elements=["Clockwork aesthetics", "Steam-powered devices"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="All magic requires a physical mechanical focus",
                applies_to_all_stories=True,
                severity="required"
            ),
            CrossStoryConstraint(
                rule="The awakening deity should remain mysterious",
                applies_to_all_stories=True,
                severity="warning"
            )
        ]
    )

    path = tmp_path / "test_universe.yaml"
    universe.to_yaml(path)
    loaded = UniverseIdentity.from_yaml(path)

    assert loaded.name == universe.name
    assert loaded.slug == universe.slug
    assert loaded.setting_profile.primary_location == "Cogsworth Empire"
    assert len(loaded.cross_story_constraints) == 2


def test_setting_profile_valid_types():
    """SettingProfile accepts valid setting_type values."""
    valid_types = ["single_world", "multi_world", "dimension_hopping", "time_travel", "parallel_universes"]
    for stype in valid_types:
        sp = SettingProfile(setting_type=stype, primary_location="Test")
        assert sp.setting_type == stype


def test_cross_story_constraint_severity_levels():
    """CrossStoryConstraint severity must be one of: required, warning, info."""
    valid = CrossStoryConstraint(rule="Test rule", applies_to_all_stories=True, severity="required")
    assert valid.severity == "required"

    with pytest.raises(ValueError):
        CrossStoryConstraint(rule="Test rule", applies_to_all_stories=True, severity="invalid")
