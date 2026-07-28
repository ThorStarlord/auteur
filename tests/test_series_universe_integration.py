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
from auteur.universe.constraints import ConstraintEnforcement, ConstraintType, StructuredConstraint
from auteur.series.handlers import handle_series_diagnose


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


def test_series_diagnose_enforces_structured_universe_constraints(tmp_path):
    data = valid_trilogy_data()
    universe = UniverseIdentity(
        name="Genre-Locked World",
        slug="genre-locked",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        structured_constraints=[
            StructuredConstraint(
                id="allowed_genre",
                type=ConstraintType.GENRE_RULE,
                description="Only mystery books are allowed",
                enforcement=ConstraintEnforcement.DETERMINISTIC,
                schema={"allowed_values": ["mystery"]},
            )
        ],
    )
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    data["universe_constraint_path"] = str(universe_path)
    series = SeriesIdentity.model_validate(data)

    result = handle_series_diagnose(series)
    assert any(d.rule.startswith("UNIVERSE_GENRE_VIOLATION") for d in result.data.diagnostics)


# --- Phase 1 baseline characterization tests (auteur#39) -------------------
#
# These tests record CURRENT production behavior of `handle_series_diagnose`
# (the function backing `auteur series diagnose`) with respect to the three
# advisory Universe fields (`forbidden_elements`, `required_elements`,
# `cross_story_constraints`), per the ratified product contract in
# auteur#38 (https://github.com/ThorStarlord/auteur/issues/38#issuecomment-5103131461).
#
# They are PASSING baseline tests, not failing tests and not expected-failure
# tests. They document that these advisory fields are currently silent (no
# diagnostic is emitted for them at all) rather than asserting that this
# silence is correct or desirable. Passing today is not evidence that this
# is the right behavior -- see auteur#38 for the ratified target contract.
#
# Phase 2 (`forbidden_elements`), Phase 3 (`required_elements`), and Phase 4
# (`cross_story_constraints` human-review notices) are each expected to
# deliberately update or replace the relevant negative assertion below as
# that phase's diagnostic code is introduced.


_ADVISORY_DIAGNOSTIC_IDS = (
    "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT",
    "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE",
    "UNIVERSE_REQUIRED_ELEMENT_MISSING",
    "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE",
    "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED",
)


def test_baseline_forbidden_element_currently_produces_no_diagnostic(tmp_path):
    """Baseline: a Series containing a forbidden phrase gets no advisory diagnostic today.

    Phase 2 must update this assertion once forbidden_elements enforcement ships.
    """
    data = valid_trilogy_data()
    # Distinctive multiword phrase, unlikely to collide with any fixture text.
    data["title"] = "The Ash Empire Trilogy: The Glasswing Choir Accord"

    universe = UniverseIdentity(
        name="Glasswing-Forbidden World",
        slug="glasswing-forbidden-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        forbidden_elements=["Glasswing Choir Accord"],
    )
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    data["universe_constraint_path"] = str(universe_path)
    series = SeriesIdentity.model_validate(data)

    result = handle_series_diagnose(series)
    rules = [d.rule for d in result.data.diagnostics]

    assert not any(
        rule == "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT" or rule.startswith("UNIVERSE_FORBIDDEN_ELEMENT_PRESENT")
        for rule in rules
    )
    assert "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE" not in rules


def test_baseline_required_element_currently_produces_no_diagnostic(tmp_path):
    """Baseline: a Series missing a required phrase gets no advisory diagnostic today.

    Phase 3 must update this assertion once required_elements enforcement ships.
    """
    data = valid_trilogy_data()
    # The Series has plenty of searchable text (title, core_question, book
    # titles/core_answers, recurring_symbols) but none of it contains this
    # distinctive required phrase.
    required_phrase = "Obsidian Marrow Requiem"
    assert required_phrase not in str(data)

    universe = UniverseIdentity(
        name="Obsidian-Required World",
        slug="obsidian-required-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        required_elements=[required_phrase],
    )
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    data["universe_constraint_path"] = str(universe_path)
    series = SeriesIdentity.model_validate(data)

    result = handle_series_diagnose(series)
    rules = [d.rule for d in result.data.diagnostics]

    assert "UNIVERSE_REQUIRED_ELEMENT_MISSING" not in rules
    assert "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE" not in rules


def test_baseline_cross_story_constraint_currently_produces_no_diagnostic(tmp_path):
    """Baseline: a populated cross_story_constraints entry gets no notice today.

    Phase 4 must update this assertion once the human-review "not evaluated"
    notice (UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED) ships.
    """
    data = valid_trilogy_data()

    universe = UniverseIdentity(
        name="Cross-Story-Constrained World",
        slug="cross-story-constrained-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="Stories should explore power without resorting to magic solutions",
                applies_to_all_stories=True,
                severity="required",
            )
        ],
    )
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    data["universe_constraint_path"] = str(universe_path)
    series = SeriesIdentity.model_validate(data)

    result = handle_series_diagnose(series)
    rules = [d.rule for d in result.data.diagnostics]

    assert "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED" not in rules


def test_baseline_advisory_fields_silent_while_structured_validation_still_active(tmp_path):
    """Baseline: advisory fields stay silent even while structured enforcement runs.

    This proves the baseline tests exercise real Universe-to-Series validation
    (the genre-rule structured constraint still fires, exactly as in
    test_series_diagnose_enforces_structured_universe_constraints above)
    rather than accidentally bypassing it. Phases 2-4 must update the
    "advisory IDs absent" assertion as each phase ships; the structured
    genre-violation assertion is expected to keep passing unchanged.
    """
    data = valid_trilogy_data()

    universe = UniverseIdentity(
        name="Genre-Locked-Plus-Advisory World",
        slug="genre-locked-plus-advisory",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        forbidden_elements=["Glasswing Choir Accord"],
        required_elements=["Obsidian Marrow Requiem"],
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="Stories should explore power without resorting to magic solutions",
                applies_to_all_stories=True,
                severity="required",
            )
        ],
        structured_constraints=[
            StructuredConstraint(
                id="allowed_genre",
                type=ConstraintType.GENRE_RULE,
                description="Only mystery books are allowed",
                enforcement=ConstraintEnforcement.DETERMINISTIC,
                schema={"allowed_values": ["mystery"]},
            )
        ],
    )
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    data["universe_constraint_path"] = str(universe_path)
    series = SeriesIdentity.model_validate(data)

    result = handle_series_diagnose(series)
    rules = [d.rule for d in result.data.diagnostics]

    # The existing structured (deterministic) enforcement path is unaffected.
    assert any(rule.startswith("UNIVERSE_GENRE_VIOLATION") for rule in rules)

    # None of the advisory diagnostic codes exist yet.
    for advisory_id in _ADVISORY_DIAGNOSTIC_IDS:
        assert advisory_id not in rules
