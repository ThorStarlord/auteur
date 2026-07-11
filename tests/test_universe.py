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


from auteur.universe.validation import (
    validate_universe_identity,
    ValidationDiagnostic,
)


def test_validate_empty_forbidden_and_required():
    """Universe with no forbidden or required elements should produce a diagnostic."""
    universe = UniverseIdentity(
        name="Bare World",
        slug="bare-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Earth"),
        magic_system="None",
        core_mythology="",
        timeline=TimelineProfile(current_era="Today", era_description="", years_of_history=0),
        forbidden_elements=[],
        required_elements=[],
        cross_story_constraints=[]
    )

    diagnostics = validate_universe_identity(universe)

    assert len(diagnostics) > 0
    assert any(d.rule == "universe.empty_forbidden_and_required" for d in diagnostics)


def test_validate_magic_system_without_mythology():
    """Universe with magic but no mythology should produce a warning."""
    universe = UniverseIdentity(
        name="Magic World",
        slug="magic-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Arcania"),
        magic_system="Rune magic requiring 10 years of study",
        core_mythology="",  # Empty!
        timeline=TimelineProfile(current_era="Now", era_description="", years_of_history=0),
        forbidden_elements=["Modern tech"],
        required_elements=["Runes"],
        cross_story_constraints=[]
    )

    diagnostics = validate_universe_identity(universe)

    assert any(d.rule == "universe.setting_and_mythology_coherence" for d in diagnostics)


def test_validate_all_required_constraints():
    """Universe where all constraints are 'required' should produce an info-level suggestion."""
    universe = UniverseIdentity(
        name="Rigid World",
        slug="rigid-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Metropolis"),
        magic_system="",
        core_mythology="",
        timeline=TimelineProfile(current_era="Era 1", era_description="", years_of_history=0),
        forbidden_elements=["Change"],
        required_elements=["Conformity"],
        cross_story_constraints=[
            CrossStoryConstraint(rule="Rule 1", applies_to_all_stories=True, severity="required"),
            CrossStoryConstraint(rule="Rule 2", applies_to_all_stories=True, severity="required"),
            CrossStoryConstraint(rule="Rule 3", applies_to_all_stories=True, severity="required"),
        ]
    )

    diagnostics = validate_universe_identity(universe)

    assert any(d.rule == "universe.constraint_severity_balance" for d in diagnostics)


def test_validate_passes_for_coherent_universe():
    """A well-formed Universe should have no errors (may have info/warnings)."""
    universe = UniverseIdentity(
        name="Coherent World",
        slug="coherent-world",
        description="A balanced fantasy setting",
        setting_profile=SettingProfile(
            setting_type="multi_world",
            primary_location="Realm of Light",
            known_locations=["Realm of Darkness"],
            worldbuilding_scope="regional"
        ),
        magic_system="Balance between Light and Dark magic",
        core_mythology="The eternal struggle between creation and entropy",
        timeline=TimelineProfile(
            current_era="Age of Awakening",
            era_description="Magic returns to the world",
            years_of_history=1000
        ),
        forbidden_elements=["Absolute good or evil", "Technology"],
        required_elements=["Moral ambiguity", "Magic", "Ancient relics"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="No story should resolve the Light/Dark conflict permanently",
                applies_to_all_stories=True,
                severity="required"
            ),
            CrossStoryConstraint(
                rule="Consider showing the cost of magic use",
                applies_to_all_stories=True,
                severity="warning"
            )
        ]
    )

    diagnostics = validate_universe_identity(universe)
    errors = [d for d in diagnostics if d.severity == "error"]

    assert len(errors) == 0
