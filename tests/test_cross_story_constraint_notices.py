"""Focused tests for cross_story_constraints human-review notices.

Phase 4 (auteur#47) implements auteur#38 Decision C: every configured
``cross_story_constraints`` entry is surfaced as a deterministic, non-blocking
INFO notice stating that the rule was NOT automatically evaluated and requires
human review.

These tests deliberately live outside `test_forbidden_elements_matching.py` and
`test_required_elements_matching.py`: Phase 4 performs no text matching at all,
so it does not belong with that machinery.
"""

from __future__ import annotations

from copy import deepcopy

from auteur.series.universe_advisory import (
    CROSS_STORY_CONSTRAINT_NOT_EVALUATED,
    surface_cross_story_constraints,
)
from auteur.universe.models import CrossStoryConstraint

# Words that would falsely claim the rule was actually evaluated. Checked
# case-insensitively against the generated text only, never against caller
# supplied rule text (a rule may legitimately contain any of these words).
_OUTCOME_CLAIM_WORDS = (
    "passed",
    "failed",
    "satisfied",
    "violated",
    "enforced",
    "compliant",
    "noncompliant",
)


def _constraint(
    rule: str = "Stories must not resolve conflicts with off-page deities",
    *,
    applies_to_all_stories: bool = True,
    severity: str = "required",
) -> CrossStoryConstraint:
    return CrossStoryConstraint(
        rule=rule,
        applies_to_all_stories=applies_to_all_stories,
        severity=severity,
    )


def _generated_text(diagnostic, rule: str) -> str:
    """Return the diagnostic text with the caller-supplied rule removed.

    Negative assertions must only inspect wording this module generates. Rule
    text is operator-authored and may contain any word at all, so leaving it in
    would make the outcome-claim assertions brittle and meaningless.
    """
    return (diagnostic.explanation + " " + diagnostic.conflict).replace(rule, " ")


def _assert_no_outcome_claim(diagnostic, rule: str) -> None:
    generated = _generated_text(diagnostic, rule).lower()
    for word in _OUTCOME_CLAIM_WORDS:
        assert word not in generated, f"generated text claims an outcome: {word!r}"


# --- cardinality -----------------------------------------------------------


def test_empty_list_produces_no_notices():
    assert surface_cross_story_constraints([]) == []


def test_one_constraint_produces_exactly_one_notice():
    rule = "Every book must reference the Concordat schism"
    diagnostics = surface_cross_story_constraints([_constraint(rule)])

    assert len(diagnostics) == 1
    assert diagnostics[0].id == CROSS_STORY_CONSTRAINT_NOT_EVALUATED
    assert diagnostics[0].severity == "INFO"


def test_multiple_constraints_preserve_order_and_indices():
    rules = ["Rule alpha", "Rule beta", "Rule gamma"]
    diagnostics = surface_cross_story_constraints([_constraint(r) for r in rules])

    assert len(diagnostics) == 3
    assert [d.constraint for d in diagnostics] == rules
    assert [d.source for d in diagnostics] == [
        "universe:cross_story_constraints[0]",
        "universe:cross_story_constraints[1]",
        "universe:cross_story_constraints[2]",
    ]


def test_duplicate_rules_remain_separate_entries():
    rule = "Stories must not resolve conflicts with off-page deities"
    diagnostics = surface_cross_story_constraints([_constraint(rule), _constraint(rule)])

    assert len(diagnostics) == 2
    assert diagnostics[0].source == "universe:cross_story_constraints[0]"
    assert diagnostics[1].source == "universe:cross_story_constraints[1]"
    assert diagnostics[0].constraint == diagnostics[1].constraint == rule


# --- metadata representation ----------------------------------------------


def test_applies_to_all_stories_true_is_represented():
    diagnostic = surface_cross_story_constraints(
        [_constraint(applies_to_all_stories=True)]
    )[0]

    assert "applies_to_all_stories=True" in diagnostic.explanation


def test_applies_to_all_stories_false_is_represented_and_not_suppressed():
    rule = "Only the first arc may name the Concordat"
    diagnostics = surface_cross_story_constraints(
        [_constraint(rule, applies_to_all_stories=False)]
    )

    assert len(diagnostics) == 1
    assert "applies_to_all_stories=False" in diagnostics[0].explanation
    assert diagnostics[0].severity == "INFO"


def test_configured_severity_required_is_metadata_only():
    diagnostic = surface_cross_story_constraints([_constraint(severity="required")])[0]

    assert "configured_severity=required" in diagnostic.explanation
    assert diagnostic.severity == "INFO"


def test_configured_severity_warning_is_metadata_only():
    diagnostic = surface_cross_story_constraints([_constraint(severity="warning")])[0]

    assert "configured_severity=warning" in diagnostic.explanation
    assert diagnostic.severity == "INFO"


def test_configured_severity_info_is_metadata_only():
    diagnostic = surface_cross_story_constraints([_constraint(severity="info")])[0]

    assert "configured_severity=info" in diagnostic.explanation
    assert diagnostic.severity == "INFO"


# --- exact diagnostic contract --------------------------------------------


def test_exact_source_string():
    diagnostics = surface_cross_story_constraints([_constraint(), _constraint("Second")])

    assert diagnostics[0].source == "universe:cross_story_constraints[0]"
    assert diagnostics[1].source == "universe:cross_story_constraints[1]"


def test_exact_conflict_source_string():
    diagnostics = surface_cross_story_constraints([_constraint(), _constraint("Second")])

    assert diagnostics[0].conflict_source == (
        "universe_identity.yaml:cross_story_constraints[0]"
    )
    assert diagnostics[1].conflict_source == (
        "universe_identity.yaml:cross_story_constraints[1]"
    )


def test_literal_rule_is_preserved_verbatim():
    rule = "  Mixed   Case Rule with  odd spacing  "
    diagnostic = surface_cross_story_constraints([_constraint(rule)])[0]

    assert diagnostic.constraint == rule
    assert rule in diagnostic.explanation


def test_lsm_context_is_empty_dict():
    diagnostic = surface_cross_story_constraints([_constraint()])[0]

    assert diagnostic.lsm_context == {}


def test_repeated_calls_are_deterministic():
    constraints = [
        _constraint("Rule alpha", severity="info"),
        _constraint("Rule beta", applies_to_all_stories=False, severity="warning"),
    ]

    first = surface_cross_story_constraints(constraints)
    second = surface_cross_story_constraints(constraints)

    assert first == second


def test_input_objects_are_not_mutated():
    constraints = [
        _constraint("Rule alpha"),
        _constraint("Rule beta", applies_to_all_stories=False, severity="info"),
    ]
    before = deepcopy([c.model_dump() for c in constraints])

    surface_cross_story_constraints(constraints)

    assert [c.model_dump() for c in constraints] == before


# --- semantic honesty ------------------------------------------------------


def test_explanation_requires_human_review():
    diagnostic = surface_cross_story_constraints([_constraint()])[0]

    assert "human review" in diagnostic.explanation.lower()
    assert "human review" in diagnostic.conflict.lower()


def test_explanation_explicitly_states_non_evaluation():
    diagnostic = surface_cross_story_constraints([_constraint()])[0]

    assert "not automatically evaluated" in diagnostic.explanation.lower()


def test_explanation_makes_no_pass_fail_or_compliance_claim():
    rule = "Stories must not resolve conflicts with off-page deities"
    diagnostic = surface_cross_story_constraints([_constraint(rule)])[0]

    _assert_no_outcome_claim(diagnostic, rule)


def test_outcome_words_inside_rule_text_do_not_leak_into_a_claim():
    """A rule whose own text uses outcome words is still reported honestly."""
    rule = "No arc may be considered satisfied until the Concordat is enforced"
    diagnostic = surface_cross_story_constraints([_constraint(rule)])[0]

    # The literal rule is preserved verbatim...
    assert rule in diagnostic.explanation
    # ...but nothing this module generates claims an outcome.
    _assert_no_outcome_claim(diagnostic, rule)
    assert "not automatically evaluated" in diagnostic.explanation.lower()


# --- no cross-contamination with Phase 2 / Phase 3 semantics ---------------


def test_rule_text_resembling_forbidden_element_does_not_alter_behavior():
    rule = "Glasswing Choir Accord"
    diagnostics = surface_cross_story_constraints([_constraint(rule)])

    assert len(diagnostics) == 1
    assert diagnostics[0].id == CROSS_STORY_CONSTRAINT_NOT_EVALUATED
    assert diagnostics[0].severity == "INFO"
    assert diagnostics[0].constraint == rule


def test_rule_text_resembling_required_element_does_not_alter_behavior():
    rule = "Obsidian Marrow Requiem"
    diagnostics = surface_cross_story_constraints([_constraint(rule)])

    assert len(diagnostics) == 1
    assert diagnostics[0].id == CROSS_STORY_CONSTRAINT_NOT_EVALUATED
    assert diagnostics[0].severity == "INFO"
    assert diagnostics[0].constraint == rule


def test_notice_function_signature_takes_no_series():
    """Phase 4 must not read Series text: the function accepts only constraints."""
    import inspect

    params = list(inspect.signature(surface_cross_story_constraints).parameters)

    assert params == ["cross_story_constraints"]
