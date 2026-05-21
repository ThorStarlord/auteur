from pathlib import Path

import pytest

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint
from auteur.structure import DiagnosticLayer, DiagnosticSeverity, analyze_structure, run_all_diagnostics


SAMPLE_YAML = Path(__file__).parent.parent / "examples" / "sample_blueprint.yaml"


def _minimal_blueprint_data() -> dict[str, object]:
    return {
        "identity": {
            "title": "Test Story",
            "author_intent": "A test premise.",
            "length_class": "novel",
            "genre": "literary",
            "medium": "novel",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG",
            "mandatory_ending_tone": "open",
        },
        "emotional_design": {
            "overall_emotional_arc": "quiet pressure",
        },
        "theme": {
            "central_question": "What does truth cost?",
            "thesis": "Truth costs belonging.",
            "motifs": [],
        },
    }


def _blueprint_data_with_story_engine() -> dict[str, object]:
    data = _minimal_blueprint_data()
    data["story_engine"] = _story_engine(
        want="The protagonist wants to expose the town's founding lie.",
        change="The protagonist learns truth may require exile.",
        thematic_function="Tests that truth costs belonging through the main plot.",
    )
    data["structure"] = {"subplot_budget": 1}
    return data


def _claim(text: str) -> dict[str, object]:
    return {"author_text": text, "checkable_claims": []}


def _story_engine(
    *,
    want: str,
    change: str,
    thematic_function: str,
    thread_thematic_function: str = "Shows that truth costs belonging at civic scale.",
) -> dict[str, object]:
    return {
        "main_thread": {
            "want": _claim(want),
            "resistance": _claim("The town needs the lie to survive."),
            "conflict": _claim("Revealing truth saves conscience but destroys home."),
            "stakes": _claim("Each step toward truth costs a relationship."),
            "change": _claim(change),
            "thematic_function": thematic_function,
        },
        "threads": [
            {
                "name": "The mayor's bargain",
                "type": "political",
                "want": _claim("The mayor wants to keep the founding crime buried."),
                "resistance": _claim("The protagonist keeps finding witnesses."),
                "conflict": _claim("Order depends on a public lie."),
                "stakes": _claim("Exposure may collapse the town's fragile peace."),
                "change": _claim("The bargain moves from rumor to open coercion."),
                "supports_main_by": ["escalates"],
                "thematic_function": thread_thematic_function,
            }
        ],
    }


# ============================================================================
# AUTEUR-001: run_all_diagnostics signature backwards-compatibility
# ============================================================================


def test_run_all_diagnostics_accepts_optional_outline_kwarg(tmp_path):
    """AUTEUR-001 RED: run_all_diagnostics must accept outline=None as a
    keyword argument and produce the same result as the two-argument form."""
    blueprint = StoryBlueprint.model_validate(_blueprint_data_with_story_engine())
    bible_path = tmp_path / "bible.json"
    bible = StoryBible(bible_path)

    # Two-argument form (existing callers)
    result_two_arg = run_all_diagnostics(blueprint, bible)

    # Three-argument form with outline=None (new, backwards-compatible)
    result_with_none = run_all_diagnostics(blueprint, bible, outline=None)

    assert isinstance(result_with_none, list)
    assert [(d.severity, d.layer, d.rule) for d in result_two_arg] == [
        (d.severity, d.layer, d.rule) for d in result_with_none
    ]


# ============================================================================
# Original tests (unchanged)
# ============================================================================


def test_analyzer_reports_missing_story_engine():
    blueprint = StoryBlueprint.model_validate(_minimal_blueprint_data())

    diagnostics = analyze_structure(blueprint)

    assert [(d.severity, d.layer, d.rule) for d in diagnostics] == [
        (
            DiagnosticSeverity.ERROR,
            DiagnosticLayer.STRUCTURAL_FORCES,
            "story_engine.missing",
        )
    ]


def test_analyzer_accepts_sample_blueprint_without_findings():
    blueprint = StoryBlueprint.from_yaml(SAMPLE_YAML)

    assert analyze_structure(blueprint) == []


def test_analyzer_reports_scope_and_thread_coherence_problems():
    data = _minimal_blueprint_data()
    data["story_engine"] = _story_engine(
        want="The protagonist wants to expose the town's founding lie.",
        change="The protagonist wants to expose the town's founding lie.",
        thematic_function="Tests whether honesty matters.",
        thread_thematic_function="Shows how officials preserve civic comfort.",
    )
    data["structure"] = {"subplot_budget": 0}
    blueprint = StoryBlueprint.model_validate(data)

    diagnostics = analyze_structure(blueprint)

    assert {d.rule for d in diagnostics} == {
        "threads.exceeds_subplot_budget",
        "main_thread.change_duplicates_want",
        "theme.thesis_unrepresented",
    }
    by_rule = {d.rule: d for d in diagnostics}
    assert by_rule["threads.exceeds_subplot_budget"].layer == DiagnosticLayer.SCOPE
    assert by_rule["main_thread.change_duplicates_want"].layer == DiagnosticLayer.STRUCTURAL_FORCES
    assert by_rule["theme.thesis_unrepresented"].layer == DiagnosticLayer.THEME
    assert by_rule["threads.exceeds_subplot_budget"].repair_options.preserve_intent
    assert by_rule["threads.exceeds_subplot_budget"].repair_options.challenge_intent


def test_analyzer_reports_threads_that_do_not_drive_main_movement():
    data = _minimal_blueprint_data()
    data["story_engine"] = _story_engine(
        want="The protagonist wants to expose the town's founding lie.",
        change="The protagonist learns truth may require exile.",
        thematic_function="Tests that truth costs belonging through the main plot.",
    )
    data["story_engine"]["threads"][0]["supports_main_by"] = ["contrasts"]
    blueprint = StoryBlueprint.model_validate(data)

    diagnostics = analyze_structure(blueprint)

    by_rule = {d.rule: d for d in diagnostics}
    diagnostic = by_rule["thread.supports_main_by.lacks_escalation_or_pressure"]
    assert diagnostic.severity == DiagnosticSeverity.WARNING
    assert diagnostic.layer == DiagnosticLayer.THREADS
    assert diagnostic.evidence == [
        "thread.name = The mayor's bargain",
        "thread.supports_main_by = ['contrasts']",
    ]
    assert diagnostic.repair_options.preserve_intent
    assert diagnostic.repair_options.challenge_intent


def test_analyzer_reports_missing_subplot_budget_when_threads_exist():
    data = _minimal_blueprint_data()
    data["story_engine"] = _story_engine(
        want="The protagonist wants to expose the town's founding lie.",
        change="The protagonist learns truth may require exile.",
        thematic_function="Tests that truth costs belonging through the main plot.",
    )
    blueprint = StoryBlueprint.model_validate(data)

    diagnostics = analyze_structure(blueprint)

    assert [d.rule for d in diagnostics] == ["structure.subplot_budget.missing"]
    assert diagnostics[0].severity == DiagnosticSeverity.WARNING
    assert diagnostics[0].layer == DiagnosticLayer.SCOPE


def test_analyzer_reports_ending_tone_that_target_experience_says_to_avoid():
    data = _blueprint_data_with_story_engine()
    data["identity"]["target_experience"] = {
        "primary": "dread",
        "progression": "dread -> catharsis",
        "avoid": ["hopeful ending"],
    }
    data["contract"]["mandatory_ending_tone"] = "hopeful"
    blueprint = StoryBlueprint.model_validate(data)

    diagnostics = analyze_structure(blueprint)

    by_rule = {d.rule: d for d in diagnostics}
    diagnostic = by_rule["target_experience.ending_tone_avoided"]
    assert diagnostic.severity == DiagnosticSeverity.ERROR
    assert diagnostic.layer == DiagnosticLayer.TARGET_EXPERIENCE
    assert "identity.target_experience.avoid" in diagnostic.evidence
    assert "contract.mandatory_ending_tone = hopeful" in diagnostic.evidence
    assert diagnostic.repair_options.preserve_intent
    assert diagnostic.repair_options.challenge_intent
