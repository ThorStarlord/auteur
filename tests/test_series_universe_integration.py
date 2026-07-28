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
from auteur.structure.diagnostics import DiagnosticSeverity


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


# Advisory codes still unimplemented after Phase 2 (auteur#43): required_elements
# is Phase 3 (#38 Decision B) and cross_story_constraints is Phase 4 (Decision C).
_UNIMPLEMENTED_ADVISORY_DIAGNOSTIC_IDS = (
    "UNIVERSE_REQUIRED_ELEMENT_MISSING",
    "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE",
    "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED",
)


def test_forbidden_element_in_title_produces_present_diagnostic(tmp_path):
    """Phase 2 (auteur#43): a Series title containing a forbidden phrase is flagged.

    This was the Phase 1 baseline test
    `test_baseline_forbidden_element_currently_produces_no_diagnostic`; its two
    negative assertions were deliberately converted to positive Phase 2
    behavior assertions when forbidden_elements enforcement shipped.
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

    assert "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT" in rules
    assert "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE" not in rules

    present = [d for d in result.data.diagnostics if d.rule == "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT"]
    assert len(present) == 1
    assert present[0].severity == DiagnosticSeverity.WARNING
    assert "title" in present[0].message
    assert "Glasswing Choir Accord" in present[0].message


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
    rather than accidentally bypassing it. Phases 3-4 must update the
    remaining "advisory IDs absent" assertions as each phase ships; the
    structured genre-violation assertion keeps passing unchanged.

    Phase 2 (auteur#43) narrowed this test: the forbidden_elements entry is now
    "Ash Empire", a phrase that genuinely appears in the default fixture title
    ("The Ash Empire Trilogy"), so the forbidden-elements assertion is positive
    (PRESENT). The previous entry ("Glasswing Choir Accord") appears nowhere in
    the default fixture text, which under the ratified contract means neither
    PRESENT nor UNEVALUABLE -- indistinguishable from a wiring failure, so it
    could not serve as the positive Phase 2 assertion this test needs.
    required_elements and cross_story_constraints remain silent.
    """
    data = valid_trilogy_data()

    universe = UniverseIdentity(
        name="Genre-Locked-Plus-Advisory World",
        slug="genre-locked-plus-advisory",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        forbidden_elements=["Ash Empire"],
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

    # Phase 2 shipped: forbidden_elements is now enforced on the same run.
    assert "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT" in rules
    assert "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE" not in rules

    # Phases 3-4 are still unimplemented: those codes remain silent.
    for advisory_id in _UNIMPLEMENTED_ADVISORY_DIAGNOSTIC_IDS:
        assert advisory_id not in rules


# --- Phase 2 handler-level behavior (auteur#43) ----------------------------


def _universe_forbidding(tmp_path, *forbidden: str, name: str = "Forbidding World") -> Path:
    universe = UniverseIdentity(
        name=name,
        slug="forbidding-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        forbidden_elements=list(forbidden),
    )
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    return universe_path


def test_forbidden_element_in_nested_field_reports_exact_field_path(tmp_path):
    """A phrase in a nested supported field is flagged with its exact path."""
    data = valid_trilogy_data()
    data["book_plans"][1]["core_answer"] = (
        "Elena invokes the Glasswing Choir Accord and the revolution fractures."
    )
    data["universe_constraint_path"] = str(
        _universe_forbidding(tmp_path, "Glasswing Choir Accord")
    )
    series = SeriesIdentity.model_validate(data)

    result = handle_series_diagnose(series)
    present = [d for d in result.data.diagnostics if d.rule == "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT"]

    assert len(present) == 1
    assert "book_plans[1].core_answer" in present[0].message
    assert present[0].severity == DiagnosticSeverity.WARNING


def test_empty_searchable_series_emits_one_unevaluable_per_forbidden_element(tmp_path):
    """Every searchable field blank -> one UNEVALUABLE per forbidden element."""
    data = valid_trilogy_data()
    data["title"] = "  "
    data["core_question"] = " \t "
    data["global_arc"] = {"beginning": " ", "midpoint": " ", "ending": None}
    for book in data["book_plans"]:
        book["title"] = " "
        book["core_answer"] = " "
    data["recurring_symbols"] = []
    data["universe_constraint_path"] = str(
        _universe_forbidding(tmp_path, "Glasswing Choir Accord", "Modern technology")
    )
    series = SeriesIdentity.model_validate(data)

    result = handle_series_diagnose(series)
    rules = [d.rule for d in result.data.diagnostics]

    assert rules.count("UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE") == 2
    assert "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT" not in rules

    unevaluable = [
        d for d in result.data.diagnostics if d.rule == "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE"
    ]
    assert all(d.severity == DiagnosticSeverity.INFO for d in unevaluable)
    assert unevaluable[0].message == (
        'Forbidden element "Glasswing Choir Accord" could not be evaluated: '
        "no searchable Series text is present"
    )


def test_searchable_text_without_match_emits_no_forbidden_diagnostic(tmp_path):
    """Text exists but nothing matches -> neither PRESENT nor UNEVALUABLE."""
    data = valid_trilogy_data()
    data["universe_constraint_path"] = str(
        _universe_forbidding(tmp_path, "Obsidian Marrow Requiem")
    )
    series = SeriesIdentity.model_validate(data)

    rules = [d.rule for d in handle_series_diagnose(series).data.diagnostics]

    assert "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT" not in rules
    assert "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE" not in rules


def test_multiple_forbidden_elements_only_matching_ones_are_reported(tmp_path):
    """Some elements match, some do not -> diagnostics only for the matches."""
    data = valid_trilogy_data()
    data["title"] = "The Ash Empire Trilogy: An Iron Crown"
    data["universe_constraint_path"] = str(
        _universe_forbidding(tmp_path, "iron", "Obsidian Marrow Requiem")
    )
    series = SeriesIdentity.model_validate(data)

    rules = [d.rule for d in handle_series_diagnose(series).data.diagnostics]

    assert rules.count("UNIVERSE_FORBIDDEN_ELEMENT_PRESENT") == 1


def test_forbidden_element_only_in_excluded_field_stays_silent(tmp_path):
    """Excluded fields (relationships/character_states) are not searched in v1."""
    data = valid_trilogy_data()
    data["relationships"] = [
        {
            "id": "elena_kade",
            "party_a": "elena",
            "party_b": "kade",
            "book": 1,
            "state": "allied",
            "notes": "Bound by the Glasswing Choir Accord",
        }
    ]
    data["universe_constraint_path"] = str(
        _universe_forbidding(tmp_path, "Glasswing Choir Accord")
    )
    series = SeriesIdentity.model_validate(data)

    rules = [d.rule for d in handle_series_diagnose(series).data.diagnostics]

    assert "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT" not in rules


def test_required_elements_remain_silent_alongside_forbidden_enforcement(tmp_path):
    """Phase 3 has not shipped: required_elements stays silent while Phase 2 fires."""
    data = valid_trilogy_data()
    universe = UniverseIdentity(
        name="Mixed Advisory World",
        slug="mixed-advisory-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        forbidden_elements=["Ash Empire"],
        required_elements=["Obsidian Marrow Requiem"],
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

    rules = [d.rule for d in handle_series_diagnose(series).data.diagnostics]

    assert "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT" in rules
    for advisory_id in _UNIMPLEMENTED_ADVISORY_DIAGNOSTIC_IDS:
        assert advisory_id not in rules


def test_blank_forbidden_element_surfaces_unsupported_diagnostic(tmp_path):
    """Malformed advisory input is reported, not silently skipped (#38 Decision D)."""
    data = valid_trilogy_data()
    data["title"] = "The Ash Empire Trilogy: An Iron Crown"
    data["universe_constraint_path"] = str(_universe_forbidding(tmp_path, "  ", "iron"))
    series = SeriesIdentity.model_validate(data)

    diagnostics = handle_series_diagnose(series).data.diagnostics
    rules = [d.rule for d in diagnostics]

    assert rules.count("UNIVERSE_ADVISORY_RULE_UNSUPPORTED") == 1
    unsupported = next(d for d in diagnostics if d.rule == "UNIVERSE_ADVISORY_RULE_UNSUPPORTED")
    assert unsupported.severity == DiagnosticSeverity.INFO
    assert "empty or whitespace-only" in unsupported.message

    # The valid sibling entry is still evaluated normally.
    assert rules.count("UNIVERSE_FORBIDDEN_ELEMENT_PRESENT") == 1
    assert "UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE" not in rules
