"""Focused unit tests for required-element extraction, normalization and matching.

Phase 3 of auteur#38 Decision B (auteur#45). Handler-level behavior is covered
separately in tests/test_series_universe_integration.py.

required_elements inverts the Phase 2 reporting rule: forbidden_elements reports
when a phrase IS found, required_elements reports when a phrase is NOT found in
any searchable field (union presence).
"""

from __future__ import annotations

import copy

from series_fixtures import valid_trilogy_data

from auteur.series.models import SeriesIdentity
from auteur.series.universe_advisory import (
    ADVISORY_RULE_UNSUPPORTED,
    REQUIRED_ELEMENT_MISSING,
    REQUIRED_ELEMENT_UNEVALUABLE,
    extract_searchable_fields,
    validate_required_elements,
)

# A distinctive phrase that appears nowhere in the default fixture text.
ABSENT_PHRASE = "Obsidian Marrow Requiem"


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


# --- matching: presence produces no diagnostic ------------------------------


def test_exact_single_word_presence_is_satisfied():
    series = _series(title="The Dragons Return")
    assert validate_required_elements(series, ["dragons"]) == []


def test_case_insensitive_presence_is_satisfied():
    series = _series(title="The DRAGONS Return")
    assert validate_required_elements(series, ["dragons"]) == []


def test_nfkc_presence_is_satisfied():
    # Fullwidth characters fold to ASCII under NFKC.
    series = _series(title="The Ｄｒａｇｏｎｓ Return")
    assert validate_required_elements(series, ["dragons"]) == []


def test_whitespace_collapse_presence_is_satisfied():
    series = _series(title="The Glasswing\t\n  Choir Accord")
    assert validate_required_elements(series, ["  Glasswing   Choir Accord "]) == []


def test_whole_word_boundary_iron_does_not_match_ironic():
    series = _series(title="An Ironic Crown")
    diagnostics = validate_required_elements(series, ["iron"])
    assert [d.id for d in diagnostics] == [REQUIRED_ELEMENT_MISSING]


def test_positive_whole_word_boundary_match_is_satisfied():
    series = _series(title="An Iron Crown")
    assert validate_required_elements(series, ["iron"]) == []


def test_non_contiguous_phrase_is_missing():
    series = _series(title="The Glasswing and the Choir of the Accord")
    diagnostics = validate_required_elements(series, ["Glasswing Choir Accord"])
    assert [d.id for d in diagnostics] == [REQUIRED_ELEMENT_MISSING]


# --- searchable fields ------------------------------------------------------


def test_presence_in_supported_nested_field_is_satisfied():
    data = valid_trilogy_data()
    data["book_plans"][1]["core_answer"] = (
        "Elena invokes the Glasswing Choir Accord and the revolution fractures."
    )
    series = SeriesIdentity.model_validate(data)
    assert validate_required_elements(series, ["Glasswing Choir Accord"]) == []


def test_presence_only_in_excluded_field_produces_missing():
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
    series = SeriesIdentity.model_validate(data)
    diagnostics = validate_required_elements(series, ["Glasswing Choir Accord"])
    assert [d.id for d in diagnostics] == [REQUIRED_ELEMENT_MISSING]


def test_searchable_field_set_is_unchanged_and_excludes_character_fields():
    series = _series()
    paths = [path for path, _ in extract_searchable_fields(series)]
    assert paths[:5] == [
        "title",
        "core_question",
        "global_arc.beginning",
        "global_arc.midpoint",
        "global_arc.ending",
    ]
    assert not any(
        path.startswith(("character_arcs", "relationships", "character_states"))
        for path in paths
    )


def test_presence_in_one_field_suffices_even_though_others_lack_it():
    """Union presence: the element need not appear in every searchable field."""
    data = valid_trilogy_data()
    data["book_plans"][0]["core_answer"] = "The Glasswing Choir Accord is signed."
    series = SeriesIdentity.model_validate(data)
    assert "Glasswing Choir Accord" not in series.title
    assert validate_required_elements(series, ["Glasswing Choir Accord"]) == []


# --- MISSING ----------------------------------------------------------------


def test_searchable_text_but_absent_phrase_produces_exactly_one_missing():
    series = _series()
    diagnostics = validate_required_elements(series, [ABSENT_PHRASE])

    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.id == REQUIRED_ELEMENT_MISSING
    assert diagnostic.severity == "WARNING"
    assert diagnostic.source == "universe:required_elements[0]"
    assert diagnostic.constraint == ABSENT_PHRASE
    assert diagnostic.conflict_source == "series_identity.yaml"
    assert ABSENT_PHRASE in diagnostic.explanation
    assert "not found in any searchable" in diagnostic.explanation
    assert diagnostic.lsm_context == {}


def test_no_success_diagnostic_is_emitted_for_a_present_element():
    """Required elements only report absence -- never a positive PRESENT."""
    series = _series(title="The Ash Empire Trilogy")
    assert validate_required_elements(series, ["Ash Empire"]) == []


def test_match_in_multiple_fields_still_produces_nothing():
    data = valid_trilogy_data()
    data["title"] = "The Glasswing Choir Accord"
    data["book_plans"][0]["core_answer"] = "The Glasswing Choir Accord holds."
    series = SeriesIdentity.model_validate(data)
    assert validate_required_elements(series, ["Glasswing Choir Accord"]) == []


# --- UNEVALUABLE ------------------------------------------------------------


def test_all_blank_searchable_text_produces_unevaluable_not_missing():
    series = _blank_series()
    diagnostics = validate_required_elements(series, [ABSENT_PHRASE, "Ash Empire"])

    assert [d.id for d in diagnostics] == [
        REQUIRED_ELEMENT_UNEVALUABLE,
        REQUIRED_ELEMENT_UNEVALUABLE,
    ]
    assert all(d.severity == "INFO" for d in diagnostics)
    assert all(d.conflict_source == "series_identity.yaml" for d in diagnostics)
    assert [d.source for d in diagnostics] == [
        "universe:required_elements[0]",
        "universe:required_elements[1]",
    ]
    assert diagnostics[0].explanation == (
        f'Required element "{ABSENT_PHRASE}" could not be evaluated: '
        "no searchable Series text is present"
    )


# --- multiple / duplicate entries -------------------------------------------


def test_multiple_required_elements_report_only_the_absent_ones():
    series = _series(title="The Ash Empire Trilogy")
    diagnostics = validate_required_elements(series, ["Ash Empire", ABSENT_PHRASE])

    assert len(diagnostics) == 1
    assert diagnostics[0].id == REQUIRED_ELEMENT_MISSING
    assert diagnostics[0].source == "universe:required_elements[1]"


def test_duplicate_entries_preserve_separate_source_indices():
    series = _series()
    diagnostics = validate_required_elements(series, [ABSENT_PHRASE, ABSENT_PHRASE])

    assert len(diagnostics) == 2
    assert [d.source for d in diagnostics] == [
        "universe:required_elements[0]",
        "universe:required_elements[1]",
    ]
    assert all(d.id == REQUIRED_ELEMENT_MISSING for d in diagnostics)


# --- malformed entries ------------------------------------------------------


def test_empty_required_entry_emits_advisory_rule_unsupported():
    series = _series()
    diagnostics = validate_required_elements(series, [""])

    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic.id == ADVISORY_RULE_UNSUPPORTED
    assert diagnostic.severity == "INFO"
    assert diagnostic.constraint == ""
    assert diagnostic.source == "universe:required_elements[0]"
    assert diagnostic.conflict_source == "universe_identity.yaml:required_elements[0]"
    assert "empty or whitespace-only" in diagnostic.explanation
    assert "required-element rule" in diagnostic.explanation


def test_whitespace_only_required_entry_emits_advisory_rule_unsupported():
    series = _series()
    diagnostics = validate_required_elements(series, ["   \t "])

    assert [d.id for d in diagnostics] == [ADVISORY_RULE_UNSUPPORTED]
    assert diagnostics[0].constraint == "   \t "
    assert diagnostics[0].conflict_source == "universe_identity.yaml:required_elements[0]"


def test_malformed_entry_never_emits_missing_or_unevaluable():
    for series in (_series(), _blank_series()):
        diagnostics = validate_required_elements(series, ["  "])
        assert [d.id for d in diagnostics] == [ADVISORY_RULE_UNSUPPORTED]


def test_malformed_entry_alongside_valid_siblings_preserves_indices():
    series = _series(title="The Ash Empire Trilogy")
    diagnostics = validate_required_elements(
        series, ["Ash Empire", "  ", ABSENT_PHRASE]
    )

    assert [(d.id, d.source) for d in diagnostics] == [
        (ADVISORY_RULE_UNSUPPORTED, "universe:required_elements[1]"),
        (REQUIRED_ELEMENT_MISSING, "universe:required_elements[2]"),
    ]


# --- determinism and purity -------------------------------------------------


def test_validator_does_not_mutate_series():
    series = _series()
    before = copy.deepcopy(series.model_dump())
    validate_required_elements(series, [ABSENT_PHRASE, "  ", "Ash Empire"])
    assert series.model_dump() == before


def test_output_order_follows_required_elements_list_order():
    series = _series()
    elements = ["Alpha Phrase", "Beta Phrase", "Gamma Phrase"]
    diagnostics = validate_required_elements(series, elements)

    assert [d.constraint for d in diagnostics] == elements
    assert [d.source for d in diagnostics] == [
        "universe:required_elements[0]",
        "universe:required_elements[1]",
        "universe:required_elements[2]",
    ]
    # Repeated invocation is byte-identical.
    again = validate_required_elements(series, elements)
    assert [(d.id, d.source, d.explanation) for d in again] == [
        (d.id, d.source, d.explanation) for d in diagnostics
    ]


def test_empty_required_elements_list_produces_no_diagnostics():
    assert validate_required_elements(_series(), []) == []
