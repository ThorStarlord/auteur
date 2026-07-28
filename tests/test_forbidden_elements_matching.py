"""Focused unit tests for forbidden-element extraction, normalization and matching.

Phase 2 of auteur#38 Decision A (auteur#43). Handler-level behavior is covered
separately in tests/test_series_universe_integration.py.
"""

from __future__ import annotations

from series_fixtures import valid_trilogy_data

from auteur.series.models import SeriesIdentity
from auteur.series.universe_advisory import (
    FORBIDDEN_ELEMENT_PRESENT,
    FORBIDDEN_ELEMENT_UNEVALUABLE,
    extract_searchable_fields,
    normalize_text,
    validate_forbidden_elements,
)


def _series(**overrides) -> SeriesIdentity:
    data = valid_trilogy_data()
    data.update(overrides)
    return SeriesIdentity.model_validate(data)


def _blank_series() -> SeriesIdentity:
    """A Series whose every searchable field is empty or whitespace-only."""
    data = valid_trilogy_data()
    data["title"] = "   "
    data["core_question"] = "\t\n "
    data["global_arc"] = {"beginning": " ", "midpoint": "  ", "ending": None}
    for book in data["book_plans"]:
        book["title"] = " "
        book["core_answer"] = " "
    data["recurring_symbols"] = []
    return SeriesIdentity.model_validate(data)


# --- normalization ---------------------------------------------------------


def test_normalize_applies_nfkc_casefold_whitespace_collapse_and_trim():
    assert normalize_text("  Glasswing\t\nChoir  ") == "glasswing choir"
    # NFKC folds fullwidth forms to ASCII.
    assert normalize_text("Ｆｕｌｌ") == "full"


# --- matching --------------------------------------------------------------


def test_exact_single_word_match():
    series = _series(title="The Dragons Return")
    diagnostics = validate_forbidden_elements(series, ["dragons"])
    assert [d.id for d in diagnostics] == [FORBIDDEN_ELEMENT_PRESENT]
    assert diagnostics[0].conflict_source.endswith("title")


def test_case_insensitive_match():
    series = _series(title="THE GLASSWING CHOIR RETURNS")
    diagnostics = validate_forbidden_elements(series, ["Glasswing Choir"])
    assert len(diagnostics) == 1
    assert diagnostics[0].severity == "WARNING"


def test_nfkc_compatibility_form_matches():
    # Fullwidth "ＤＲＡＧＯＮＳ" normalizes to "dragons" under NFKC + casefold.
    series = _series(title="The ＤＲＡＧＯＮＳ Return")
    diagnostics = validate_forbidden_elements(series, ["dragons"])
    assert len(diagnostics) == 1


def test_whitespace_collapse_across_spaces_tabs_and_newlines():
    series = _series(core_question="Will the glasswing \t\n  choir sing?")
    diagnostics = validate_forbidden_elements(series, ["glasswing choir"])
    assert len(diagnostics) == 1
    assert diagnostics[0].conflict_source.endswith("core_question")


def test_whole_word_negative_iron_does_not_match_ironic():
    series = _series(title="Ironic consequences")
    assert validate_forbidden_elements(series, ["iron"]) == []


def test_whole_word_positive_iron_matches_an_iron_crown():
    series = _series(title="An iron crown")
    diagnostics = validate_forbidden_elements(series, ["iron"])
    assert len(diagnostics) == 1


def test_contiguous_phrase_required():
    series = _series(title="Modern people, ancient technology")
    assert validate_forbidden_elements(series, ["modern technology"]) == []


# --- extraction ------------------------------------------------------------


def test_field_path_extraction_is_deterministic_and_ordered():
    series = _series()
    paths = [path for path, _ in extract_searchable_fields(series)]
    assert paths[:5] == [
        "title",
        "core_question",
        "global_arc.beginning",
        "global_arc.midpoint",
        "global_arc.ending",
    ]
    assert "book_plans[0].title" in paths
    assert "book_plans[0].core_answer" in paths
    assert paths == [path for path, _ in extract_searchable_fields(series)]
    assert paths.index("book_plans[0].title") < paths.index("book_plans[1].title")


def test_excluded_fields_are_never_searched():
    series = _series()
    paths = [path for path, _ in extract_searchable_fields(series)]
    assert not any(
        path.startswith(("character_arcs", "relationships", "character_states")) for path in paths
    )


def test_phrase_only_in_excluded_field_produces_no_diagnostic():
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
    data["character_states"] = [
        {
            "character_id": "elena",
            "book": 1,
            "state": {"oath": "Glasswing Choir Accord"},
        }
    ]
    series = SeriesIdentity.model_validate(data)
    assert validate_forbidden_elements(series, ["Glasswing Choir Accord"]) == []


# --- cardinality and states ------------------------------------------------


def test_searchable_text_but_no_match_emits_nothing():
    series = _series()
    assert validate_forbidden_elements(series, ["Obsidian Marrow Requiem"]) == []


def test_multiple_forbidden_elements_only_matching_ones_reported():
    series = _series(title="An iron crown")
    diagnostics = validate_forbidden_elements(series, ["iron", "Obsidian Marrow Requiem"])
    assert [d.constraint for d in diagnostics] == ["iron"]
    assert diagnostics[0].source == "universe:forbidden_elements[0]"


def test_repeated_occurrences_in_one_field_produce_one_diagnostic():
    series = _series(title="iron and iron and more iron")
    assert len(validate_forbidden_elements(series, ["iron"])) == 1


def test_same_element_in_multiple_fields_produces_one_diagnostic_per_field():
    series = _series(title="An iron crown", core_question="Is iron enough?")
    diagnostics = validate_forbidden_elements(series, ["iron"])
    assert [d.conflict_source.split(":")[-1] for d in diagnostics] == ["title", "core_question"]


def test_blank_series_emits_one_unevaluable_per_element():
    series = _blank_series()
    diagnostics = validate_forbidden_elements(series, ["iron", "dragons"])
    assert [d.id for d in diagnostics] == [
        FORBIDDEN_ELEMENT_UNEVALUABLE,
        FORBIDDEN_ELEMENT_UNEVALUABLE,
    ]
    assert all(d.severity == "INFO" for d in diagnostics)
    assert diagnostics[0].explanation == (
        'Forbidden element "iron" could not be evaluated: no searchable Series text is present'
    )
    assert diagnostics[1].source == "universe:forbidden_elements[1]"


def test_no_forbidden_elements_means_no_diagnostics():
    assert validate_forbidden_elements(_series(), []) == []


def test_series_is_not_mutated_during_validation():
    series = _series(title="An iron crown")
    before = series.model_dump(mode="json")
    validate_forbidden_elements(series, ["iron"])
    assert series.model_dump(mode="json") == before
