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
# They began as PASSING baseline tests documenting that these advisory fields
# were silent (no diagnostic emitted at all), without asserting that the
# silence was correct or desirable -- see auteur#38 for the ratified target
# contract. Every one of those negative assertions has since been converted to
# a positive behavior assertion by the phase that implemented the field.
#
# Phase 2 (`forbidden_elements`), Phase 3 (`required_elements`), and Phase 4
# (`cross_story_constraints` human-review notices) each deliberately updated or
# replaced the relevant negative assertion below as that phase's diagnostic
# code shipped. All three advisory fields are now implemented, so no negative
# "still unimplemented" assertion remains in this module.


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


def test_missing_required_element_produces_missing_diagnostic(tmp_path):
    """Phase 3 (auteur#45): a Series missing a required phrase is flagged.

    This was the Phase 1 baseline test
    `test_baseline_required_element_currently_produces_no_diagnostic`; its two
    negative assertions were deliberately converted to positive Phase 3
    behavior assertions when required_elements enforcement shipped. The
    UNEVALUABLE assertion stays negative on purpose: this fixture has plenty of
    searchable text, so only MISSING may fire.
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

    assert "UNIVERSE_REQUIRED_ELEMENT_MISSING" in rules
    assert "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE" not in rules

    missing = [
        d for d in result.data.diagnostics if d.rule == "UNIVERSE_REQUIRED_ELEMENT_MISSING"
    ]
    assert len(missing) == 1
    assert missing[0].severity == DiagnosticSeverity.WARNING
    assert required_phrase in missing[0].message
    assert "not found in any searchable Series field" in missing[0].message


def test_cross_story_constraint_produces_human_review_notice(tmp_path):
    """Phase 4 (auteur#47): a configured cross-story rule is surfaced for human review.

    This was the Phase 1 baseline test
    `test_baseline_cross_story_constraint_currently_produces_no_diagnostic`; its
    negative assertion was deliberately converted to positive Phase 4 behavior
    assertions when the human-review notice shipped. The notice reports
    NON-evaluation -- it must never claim the rule passed or failed.
    """
    data = valid_trilogy_data()
    rule = "Stories should explore power without resorting to magic solutions"

    universe = UniverseIdentity(
        name="Cross-Story-Constrained World",
        slug="cross-story-constrained-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        cross_story_constraints=[
            CrossStoryConstraint(
                rule=rule,
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

    assert rules.count("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED") == 1

    notice = next(
        d
        for d in result.data.diagnostics
        if d.rule == "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"
    )
    # A configured severity of "required" must NOT upgrade the notice: it
    # reports non-evaluation, not a rule outcome.
    assert notice.severity == DiagnosticSeverity.INFO
    assert rule in notice.message
    assert "not automatically evaluated" in notice.message.lower()
    assert "human review" in notice.message.lower()
    assert "applies_to_all_stories=True" in notice.message
    assert "configured_severity=required" in notice.message

    # No automatic pass/fail claim exists anywhere in the generated wording.
    generated = notice.message.replace(rule, " ").lower()
    for word in ("passed", "failed", "satisfied", "violated", "enforced", "compliant"):
        assert word not in generated


def test_structured_forbidden_and_required_diagnostics_coexist_on_one_run(tmp_path):
    """Structured, forbidden and required enforcement all fire on the same run.

    This proves the baseline tests exercise real Universe-to-Series validation
    (the genre-rule structured constraint still fires, exactly as in
    test_series_diagnose_enforces_structured_universe_constraints above)
    rather than accidentally bypassing it. The structured genre-violation
    assertion keeps passing unchanged across every phase.

    Phase 2 (auteur#43) narrowed this test: the forbidden_elements entry is now
    "Ash Empire", a phrase that genuinely appears in the default fixture title
    ("The Ash Empire Trilogy"), so the forbidden-elements assertion is positive
    (PRESENT). The previous entry ("Glasswing Choir Accord") appears nowhere in
    the default fixture text, which under the ratified contract means neither
    PRESENT nor UNEVALUABLE -- indistinguishable from a wiring failure, so it
    could not serve as the positive Phase 2 assertion this test needs.

    Phase 3 (auteur#45) converted the required_elements half: the existing
    "Obsidian Marrow Requiem" entry is genuinely absent from the default
    fixture text, so it now yields a positive MISSING assertion.

    Phase 4 (auteur#47) converted the last negative half: the configured
    cross_story_constraints entry now yields a positive NOT_EVALUATED
    human-review notice, and this run additionally proves the full ratified
    aggregate order structured -> forbidden -> required -> cross-story. The
    Phase 2 and Phase 3 assertions are unchanged and must not be weakened.
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

    # Phase 3 shipped: the absent required element is now reported on the same run.
    assert rules.count("UNIVERSE_REQUIRED_ELEMENT_MISSING") == 1
    assert "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE" not in rules
    required_missing = next(
        d for d in result.data.diagnostics if d.rule == "UNIVERSE_REQUIRED_ELEMENT_MISSING"
    )
    assert required_missing.severity == DiagnosticSeverity.WARNING
    assert "Obsidian Marrow Requiem" in required_missing.message

    # Phase 4 shipped: the cross-story rule is surfaced for human review on the
    # same run, without suppressing or being suppressed by the others.
    assert rules.count("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED") == 1
    cross_story = next(
        d
        for d in result.data.diagnostics
        if d.rule == "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"
    )
    assert cross_story.severity == DiagnosticSeverity.INFO
    assert "not automatically evaluated" in cross_story.message.lower()
    assert "human review" in cross_story.message.lower()

    # Ratified aggregate order: structured -> forbidden -> required -> cross-story.
    assert rules.index("UNIVERSE_FORBIDDEN_ELEMENT_PRESENT") < rules.index(
        "UNIVERSE_REQUIRED_ELEMENT_MISSING"
    ) < rules.index("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED")


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


def test_required_and_forbidden_enforcement_coexist(tmp_path):
    """Phase 3 (auteur#45): forbidden PRESENT and required MISSING coexist.

    This replaces the Phase 2 test
    `test_required_elements_remain_silent_alongside_forbidden_enforcement`,
    whose premise ("required_elements stays silent") became false in Phase 3.
    Phase 4 (auteur#47) extended it again: the cross-story human-review notice
    now fires on the same run. No advisory validator suppresses another, and
    the aggregate order is forbidden -> required -> cross-story.
    """
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

    diagnostics = handle_series_diagnose(series).data.diagnostics
    rules = [d.rule for d in diagnostics]

    # Phase 2 behavior remains intact.
    assert "UNIVERSE_FORBIDDEN_ELEMENT_PRESENT" in rules
    # Phase 3 fires on the same run.
    assert rules.count("UNIVERSE_REQUIRED_ELEMENT_MISSING") == 1
    assert "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE" not in rules

    # Phase 4 fires on the same run as a non-blocking INFO human-review notice.
    assert rules.count("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED") == 1
    cross_story = next(
        d for d in diagnostics if d.rule == "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"
    )
    assert cross_story.severity == DiagnosticSeverity.INFO

    # Deterministic aggregate order: forbidden -> required -> cross-story.
    assert rules.index("UNIVERSE_FORBIDDEN_ELEMENT_PRESENT") < rules.index(
        "UNIVERSE_REQUIRED_ELEMENT_MISSING"
    ) < rules.index("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED")


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


# --- Phase 3 handler-level behavior (auteur#45) ----------------------------


def _universe_requiring(tmp_path, *required: str, name: str = "Requiring World") -> Path:
    universe = UniverseIdentity(
        name=name,
        slug="requiring-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        required_elements=list(required),
    )
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    return universe_path


def test_present_required_element_produces_no_diagnostic_through_handler(tmp_path):
    """A satisfied required element emits nothing -- no positive success diagnostic."""
    data = valid_trilogy_data()
    # "Ash Empire" genuinely appears in the default fixture title.
    data["universe_constraint_path"] = str(_universe_requiring(tmp_path, "Ash Empire"))
    series = SeriesIdentity.model_validate(data)

    rules = [d.rule for d in handle_series_diagnose(series).data.diagnostics]

    assert "UNIVERSE_REQUIRED_ELEMENT_MISSING" not in rules
    assert "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE" not in rules


def test_empty_searchable_series_emits_one_unevaluable_per_required_element(tmp_path):
    """Every searchable field blank -> one UNEVALUABLE per required element, no MISSING."""
    data = valid_trilogy_data()
    data["title"] = "  "
    data["core_question"] = " \t "
    data["global_arc"] = {"beginning": " ", "midpoint": " ", "ending": None}
    for book in data["book_plans"]:
        book["title"] = " "
        book["core_answer"] = " "
    data["recurring_symbols"] = []
    data["universe_constraint_path"] = str(
        _universe_requiring(tmp_path, "Obsidian Marrow Requiem", "Ash Empire")
    )
    series = SeriesIdentity.model_validate(data)

    diagnostics = handle_series_diagnose(series).data.diagnostics
    rules = [d.rule for d in diagnostics]

    assert rules.count("UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE") == 2
    assert "UNIVERSE_REQUIRED_ELEMENT_MISSING" not in rules

    unevaluable = [
        d for d in diagnostics if d.rule == "UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE"
    ]
    assert all(d.severity == DiagnosticSeverity.INFO for d in unevaluable)
    assert unevaluable[0].message == (
        'Required element "Obsidian Marrow Requiem" could not be evaluated: '
        "no searchable Series text is present"
    )


def test_blank_required_element_surfaces_unsupported_diagnostic(tmp_path):
    """Malformed required input is reported, not silently skipped (#38 Decision D)."""
    data = valid_trilogy_data()
    data["universe_constraint_path"] = str(
        _universe_requiring(tmp_path, "  ", "Obsidian Marrow Requiem")
    )
    series = SeriesIdentity.model_validate(data)

    diagnostics = handle_series_diagnose(series).data.diagnostics
    rules = [d.rule for d in diagnostics]

    assert rules.count("UNIVERSE_ADVISORY_RULE_UNSUPPORTED") == 1
    unsupported = next(d for d in diagnostics if d.rule == "UNIVERSE_ADVISORY_RULE_UNSUPPORTED")
    assert unsupported.severity == DiagnosticSeverity.INFO
    assert "required_elements[0]" in unsupported.message
    assert "empty or whitespace-only" in unsupported.message

    # The valid sibling entry is still evaluated normally.
    assert rules.count("UNIVERSE_REQUIRED_ELEMENT_MISSING") == 1


def test_structured_and_required_diagnostics_coexist(tmp_path):
    """A violated structured constraint and a missing required element both fire."""
    data = valid_trilogy_data()
    universe = UniverseIdentity(
        name="Structured-Plus-Required World",
        slug="structured-plus-required",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        required_elements=["Obsidian Marrow Requiem"],
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

    rules = [d.rule for d in handle_series_diagnose(series).data.diagnostics]

    assert any(rule.startswith("UNIVERSE_GENRE_VIOLATION") for rule in rules)
    assert "UNIVERSE_REQUIRED_ELEMENT_MISSING" in rules


def test_required_enforcement_and_cross_story_notices_coexist(tmp_path):
    """Phase 3 enforcement and Phase 4 notices fire together, neither suppressing the other.

    This replaces `test_required_enforcement_does_not_wake_cross_story_notices`,
    whose premise ("Phase 4 stays silent") became false when auteur#47 shipped.
    """
    data = valid_trilogy_data()
    universe = UniverseIdentity(
        name="Cross-Story-Plus-Required World",
        slug="cross-story-plus-required",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
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

    diagnostics = handle_series_diagnose(series).data.diagnostics
    rules = [d.rule for d in diagnostics]

    assert "UNIVERSE_REQUIRED_ELEMENT_MISSING" in rules
    assert rules.count("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED") == 1

    cross_story = next(
        d for d in diagnostics if d.rule == "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"
    )
    assert cross_story.severity == DiagnosticSeverity.INFO
    assert "human review" in cross_story.message.lower()


def test_duplicate_required_entries_each_produce_a_diagnostic_through_handler(tmp_path):
    """Duplicate configuration entries are not deduplicated by the handler path."""
    data = valid_trilogy_data()
    data["universe_constraint_path"] = str(
        _universe_requiring(tmp_path, "Obsidian Marrow Requiem", "Obsidian Marrow Requiem")
    )
    series = SeriesIdentity.model_validate(data)

    rules = [d.rule for d in handle_series_diagnose(series).data.diagnostics]

    assert rules.count("UNIVERSE_REQUIRED_ELEMENT_MISSING") == 2

# --- Phase 4 handler-level behavior (auteur#47, #38 Decision C) -------------


def _universe_with_cross_story(
    tmp_path,
    *rules: str,
    name: str = "Cross-Story World",
    applies_to_all_stories: bool = True,
    severity: str = "required",
    forbidden: tuple[str, ...] = (),
    required: tuple[str, ...] = (),
) -> Path:
    universe = UniverseIdentity(
        name=name,
        slug="cross-story-world",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        forbidden_elements=list(forbidden),
        required_elements=list(required),
        cross_story_constraints=[
            CrossStoryConstraint(
                rule=rule,
                applies_to_all_stories=applies_to_all_stories,
                severity=severity,
            )
            for rule in rules
        ],
    )
    universe_path = tmp_path / "universe.yaml"
    universe.to_yaml(universe_path)
    return universe_path


def test_blank_searchable_series_still_produces_cross_story_notice(tmp_path):
    """Cross-story notices do not depend on Series text at all.

    Forbidden and required both degrade to UNEVALUABLE when every searchable
    field is blank; the cross-story notice fires regardless, because Phase 4
    never searches Series text in the first place.
    """
    data = valid_trilogy_data()
    data["title"] = "  "
    data["core_question"] = " \t "
    data["global_arc"] = {"beginning": " ", "midpoint": " ", "ending": None}
    for book in data["book_plans"]:
        book["title"] = " "
        book["core_answer"] = " "
    data["recurring_symbols"] = []
    data["universe_constraint_path"] = str(
        _universe_with_cross_story(
            tmp_path,
            "Stories must not resolve conflicts with off-page deities",
            forbidden=("Glasswing Choir Accord",),
            required=("Obsidian Marrow Requiem",),
        )
    )
    series = SeriesIdentity.model_validate(data)

    diagnostics = handle_series_diagnose(series).data.diagnostics
    rules = [d.rule for d in diagnostics]

    assert rules.count("UNIVERSE_FORBIDDEN_ELEMENT_UNEVALUABLE") == 1
    assert rules.count("UNIVERSE_REQUIRED_ELEMENT_UNEVALUABLE") == 1
    assert rules.count("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED") == 1

    notice = next(
        d for d in diagnostics if d.rule == "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"
    )
    assert notice.severity == DiagnosticSeverity.INFO
    assert "not automatically evaluated" in notice.message.lower()


def test_multiple_cross_story_constraints_preserve_order_through_handler(tmp_path):
    """One notice per configured entry, in configured order, with no dedup."""
    data = valid_trilogy_data()
    data["universe_constraint_path"] = str(
        _universe_with_cross_story(
            tmp_path,
            "Rule alpha about the Concordat",
            "Rule beta about the Concordat",
            "Rule alpha about the Concordat",
        )
    )
    series = SeriesIdentity.model_validate(data)

    diagnostics = handle_series_diagnose(series).data.diagnostics
    notices = [
        d for d in diagnostics if d.rule == "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"
    ]

    assert len(notices) == 3
    assert all(d.severity == DiagnosticSeverity.INFO for d in notices)
    assert "Rule alpha about the Concordat" in notices[0].message
    assert "Rule beta about the Concordat" in notices[1].message
    assert "Rule alpha about the Concordat" in notices[2].message


def test_cross_story_notice_severity_stays_info_for_every_configured_severity(tmp_path):
    """Configured severity is metadata only; the notice never becomes WARNING/ERROR."""
    for configured in ("required", "warning", "info"):
        target = tmp_path / configured
        target.mkdir()
        data = valid_trilogy_data()
        data["universe_constraint_path"] = str(
            _universe_with_cross_story(
                target,
                "Stories must not resolve conflicts with off-page deities",
                severity=configured,
            )
        )
        series = SeriesIdentity.model_validate(data)

        diagnostics = handle_series_diagnose(series).data.diagnostics
        notice = next(
            d for d in diagnostics if d.rule == "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"
        )

        assert notice.severity == DiagnosticSeverity.INFO
        assert f"configured_severity={configured}" in notice.message


def test_cross_story_notice_does_not_suppress_structured_diagnostics(tmp_path):
    """A violated structured constraint still fires alongside the cross-story notice."""
    data = valid_trilogy_data()
    universe = UniverseIdentity(
        name="Structured-Plus-Cross-Story World",
        slug="structured-plus-cross-story",
        description="",
        setting_profile=SettingProfile(setting_type="single_world", primary_location="Realm"),
        timeline=TimelineProfile(current_era="Now"),
        cross_story_constraints=[
            CrossStoryConstraint(
                rule="Stories must not resolve conflicts with off-page deities",
                applies_to_all_stories=False,
                severity="warning",
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

    diagnostics = handle_series_diagnose(series).data.diagnostics
    rules = [d.rule for d in diagnostics]

    assert any(rule.startswith("UNIVERSE_GENRE_VIOLATION") for rule in rules)
    assert rules.count("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED") == 1

    notice = next(
        d for d in diagnostics if d.rule == "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED"
    )
    assert "applies_to_all_stories=False" in notice.message
    assert "configured_severity=warning" in notice.message
    # Structured diagnostics precede every advisory diagnostic.
    assert rules.index(
        next(r for r in rules if r.startswith("UNIVERSE_GENRE_VIOLATION"))
    ) < rules.index("UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED")


def test_handler_path_does_not_mutate_series_or_universe_artifact(tmp_path):
    """Diagnosing twice mutates nothing and yields identical output."""
    data = valid_trilogy_data()
    universe_path = _universe_with_cross_story(
        tmp_path,
        "Stories must not resolve conflicts with off-page deities",
        forbidden=("Ash Empire",),
        required=("Obsidian Marrow Requiem",),
    )
    data["universe_constraint_path"] = str(universe_path)
    series = SeriesIdentity.model_validate(data)

    series_before = series.model_dump(mode="json")
    universe_before = universe_path.read_bytes()

    first = [
        (d.rule, d.severity, d.message) for d in handle_series_diagnose(series).data.diagnostics
    ]
    second = [
        (d.rule, d.severity, d.message) for d in handle_series_diagnose(series).data.diagnostics
    ]

    assert first == second
    assert series.model_dump(mode="json") == series_before
    assert universe_path.read_bytes() == universe_before


def test_blank_cross_story_rule_still_fails_universe_loading(tmp_path):
    """Malformed-input boundary is unchanged: Phase 4 does not disguise it.

    `CrossStoryConstraint.rule` is `Field(min_length=1)`, so a blank rule fails
    pydantic validation during Universe loading and surfaces through the
    existing UNIVERSE_CONTRACT_INVALID path -- never as a cross-story notice and
    never as UNIVERSE_ADVISORY_RULE_UNSUPPORTED.
    """
    data = valid_trilogy_data()
    universe_path = _universe_with_cross_story(tmp_path, "Placeholder rule text")
    universe_path.write_text(
        universe_path.read_text(encoding="utf-8").replace("Placeholder rule text", ""),
        encoding="utf-8",
    )
    data["universe_constraint_path"] = str(universe_path)
    series = SeriesIdentity.model_validate(data)

    diagnostics = handle_series_diagnose(series).data.diagnostics
    rules = [d.rule for d in diagnostics]

    assert "UNIVERSE_CONTRACT_INVALID" in rules
    assert "UNIVERSE_CROSS_STORY_CONSTRAINT_NOT_EVALUATED" not in rules
    assert "UNIVERSE_ADVISORY_RULE_UNSUPPORTED" not in rules
