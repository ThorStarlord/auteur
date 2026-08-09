"""TDD tests for Author Decision Objects (M4 + thin M2, bounded M3).

Approved design: "Author Decision Objects" (post-propagation solution discovery,
2026-08; full document lives in the implementation-design worktree). Golden
acceptance fixtures: frozen discovery Cases D and E.

First batch is expected RED: the `auteur.author_decisions` module does not exist yet.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "author_decisions"
CASE_D = FIXTURES / "case-d"
CASE_E = FIXTURES / "case-e"

from auteur.author_decisions import (  # noqa: E402  (module under test; absent -> RED)
    AuthorDecision,
    build_decision_context,
    enumerate_combinations,
    DecisionValidationError,
)


# ---------------------------------------------------------------------------
# Schema (minimum semantics + anti-creep)
# ---------------------------------------------------------------------------

def test_valid_d_like_decision_parses():
    dec = AuthorDecision.from_yaml(CASE_D / "nine-chairs-structure.yaml")
    assert dec.decision_id == "nine-chairs-structure"
    assert len(dec.unresolved_choice.options) == 2


def test_valid_e_like_decision_parses():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    assert dec.combination.rule == "choose_k_of_n"
    assert dec.combination.k == 2


def test_options_require_at_least_two():
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict({"unresolved_choice": {"question": "q", "options": ["only one"]}})


def test_options_cannot_be_open_ended():
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict({"unresolved_choice": {"question": "q", "options": None}})


def test_alternative_ids_match_options_length():
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict({
            "unresolved_choice": {"question": "q", "options": ["a", "b"]},
            "alternative_ids": ["a"],
        })


def test_unknown_fields_rejected():
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict({
            "unresolved_choice": {"question": "q", "options": ["a", "b"]},
            "alternative_ids": ["a", "b"],
            "combination": {"rule": "one_of"},
            "criterion": {"text": "c", "evaluator": "author_or_consumer"},
            "novel_unknown_field": "x",
        })


def test_cardinality_bounds():
    base = {
        "unresolved_choice": {"question": "q", "options": ["a", "b", "c"]},
        "alternative_ids": ["a", "b", "c"],
        "criterion": {"text": "c", "evaluator": "author_or_consumer"},
    }
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict({**base, "combination": {"rule": "choose_k_of_n", "k": 4}})  # k > n
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict({**base, "combination": {"rule": "choose_k_of_n", "k": 0}})
    dec = AuthorDecision.from_dict({**base, "combination": {"rule": "one_of"}})
    assert dec.combination.rule == "one_of"


def test_criterion_required():
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict({
            "unresolved_choice": {"question": "q", "options": ["a", "b"]},
            "alternative_ids": ["a", "b"],
            "combination": {"rule": "one_of"},
        })


# ---------------------------------------------------------------------------
# Context (thin projection; refs resolved; fail-closed)
# ---------------------------------------------------------------------------

def test_context_resolves_constraint_refs_verbatim():
    dec = AuthorDecision.from_yaml(CASE_D / "nine-chairs-structure.yaml")
    identity = load_identity(CASE_D / "story_identity.yaml")
    blueprint = load_blueprint(CASE_D / "blueprint.yaml")
    ctx = build_decision_context(dec, identity, blueprint)
    assert len(ctx.constraints) == 8
    assert ctx.constraints[0].text == "a character who authoritatively explains the room's rules"


def test_unresolvable_constraint_ref_fails_closed():
    dec = AuthorDecision.from_dict({
        "unresolved_choice": {"question": "q", "options": ["a", "b"]},
        "alternative_ids": ["a", "b"],
        "combination": {"rule": "one_of"},
        "criterion": {"text": "c", "evaluator": "author_or_consumer"},
        "hard_constraints": [{"ref": "not_this[99]", "snapshot": "x"}],
    })
    identity = load_identity(CASE_D / "story_identity.yaml")
    blueprint = load_blueprint(CASE_D / "blueprint.yaml")
    with pytest.raises(DecisionValidationError):
        build_decision_context(dec, identity, blueprint)


def test_blocked_provenance_count_derived_and_refs_exist():
    dec = AuthorDecision.from_yaml(CASE_D / "nine-chairs-structure.yaml")
    identity = load_identity(CASE_D / "story_identity.yaml")
    blueprint = load_blueprint(CASE_D / "blueprint.yaml")
    ctx = build_decision_context(dec, identity, blueprint)
    assert ctx.blocked_count == 9
    assert ctx.blocked_provenance_verified is True


def test_blocked_provenance_mismatch_fails_closed():
    dec = AuthorDecision.from_yaml(CASE_D / "nine-chairs-structure.yaml")
    identity = load_identity(CASE_D / "story_identity.yaml")
    blueprint = load_blueprint(CASE_D / "blueprint.yaml")
    blueprint.identity_propagation.outcomes = []  # simulate lost provenance
    with pytest.raises(DecisionValidationError):
        build_decision_context(dec, identity, blueprint)


def test_default_reference_resolves_to_product_value():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    identity = load_identity(CASE_E / "story_identity.yaml")
    blueprint = load_blueprint(CASE_E / "blueprint.yaml")
    ctx = build_decision_context(dec, identity, blueprint)
    assert ctx.resolved_defaults["contract.mandatory_ending_tone"] == "bittersweet"


# ---------------------------------------------------------------------------
# Anti-inference invariant: alternatives are authored, never extracted
# ---------------------------------------------------------------------------

def test_context_alternatives_are_authored_options_verbatim():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    identity = load_identity(CASE_E / "story_identity.yaml")
    blueprint = load_blueprint(CASE_E / "blueprint.yaml")
    ctx = build_decision_context(dec, identity, blueprint)
    assert ctx.alternative_labels == ["Anders' debt", "Marta's pregnancy", "Signe's marriage"]
    assert ctx.alternative_source == "authored"


# ---------------------------------------------------------------------------
# M3: deterministic enumeration (bounded; never a verdict)
# ---------------------------------------------------------------------------

def test_d_enumeration_two_one_of():
    dec = AuthorDecision.from_yaml(CASE_D / "nine-chairs-structure.yaml")
    combos = enumerate_combinations(dec)
    assert combos == [("nine_parallel_arcs",), ("one_structural_spine",)]


def test_e_enumeration_three_pairs_under_budget():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    combos = enumerate_combinations(dec)
    assert len(combos) == 3
    assert all(len(c) == 2 for c in combos)


def test_report_contains_no_verdict():
    dec = AuthorDecision.from_yaml(CASE_E / "salt-of-the-earth-subplot-cut.yaml")
    identity = load_identity(CASE_E / "story_identity.yaml")
    blueprint = load_blueprint(CASE_E / "blueprint.yaml")
    ctx = build_decision_context(dec, identity, blueprint)
    report = ctx.build_report()
    assert report.get("verdict") is None
    assert "recommended" not in report


# ---------------------------------------------------------------------------
# helpers (module-local; real loaders live in the module under test)
# ---------------------------------------------------------------------------

def load_identity(path: Path):
    from auteur.identity import StoryIdentity
    return StoryIdentity.from_yaml(path)


def load_blueprint(path: Path):
    from auteur.blueprint import StoryBlueprint

    return StoryBlueprint.from_yaml(path)


def test_derived_choice_id_comes_from_decision_id_not_question():
    """Guard: editing question/option wording must not change the derived choice identity."""
    base = {
        "alternative_ids": ["a", "b"],
        "combination": {"rule": "one_of"},
        "criterion": {"text": "c", "evaluator": "author_or_consumer"},
    }
    d1 = AuthorDecision.from_dict({
        **base,
        "decision_id": "stable-id",
        "unresolved_choice": {"question": "First wording?", "options": ["a", "b"]},
    })
    d2 = AuthorDecision.from_dict({
        **base,
        "decision_id": "stable-id",
        "unresolved_choice": {"question": "Completely edited wording!", "options": ["a", "b"]},
    })
    assert d1.unresolved_choice.choice_id == "stable-id"
    assert d2.unresolved_choice.choice_id == "stable-id"
    assert d1.unresolved_choice.choice_id == d2.unresolved_choice.choice_id

# ---------------------------------------------------------------------------
# Review fixes — F2: provenance multiplicity (multiset equality)
# ---------------------------------------------------------------------------

def _blocked_outcome(rule, source):
    from auteur.blueprint import PropagationOutcome
    return PropagationOutcome(
        rule=rule,
        classification="BLOCKED_INSUFFICIENT_EXPLICIT_INPUT",
        source=source,
    )


def _decision_with_blocked_refs(refs):
    return AuthorDecision.from_dict({
        "decision_id": "f2-test",
        "unresolved_choice": {"question": "q", "options": ["a", "b"]},
        "alternative_ids": ["a", "b"],
        "combination": {"rule": "one_of"},
        "criterion": {"text": "c", "evaluator": "author_or_consumer"},
        "blocked_provenance": {"outcome_refs": refs},
    })


def _blueprint_with_blocked(outcomes):
    bp = load_blueprint(CASE_D / "blueprint.yaml")
    bp.identity_propagation.outcomes = outcomes
    return bp


def _f2_ref(rule, source):
    return {"rule": rule, "classification": "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT", "source": source}


def test_duplicate_refs_cannot_be_satisfied_by_one_outcome():
    dec = _decision_with_blocked_refs([_f2_ref("r.x", "s.a"), _f2_ref("r.x", "s.a")])
    bp = _blueprint_with_blocked([_blocked_outcome("r.x", "s.a")])
    with pytest.raises(DecisionValidationError):
        build_decision_context(dec, load_identity(CASE_D / "story_identity.yaml"), bp)


def test_two_identical_outcomes_satisfy_two_identical_refs():
    dec = _decision_with_blocked_refs([_f2_ref("r.x", "s.a"), _f2_ref("r.x", "s.a")])
    bp = _blueprint_with_blocked([_blocked_outcome("r.x", "s.a"), _blocked_outcome("r.x", "s.a")])
    ctx = build_decision_context(dec, load_identity(CASE_D / "story_identity.yaml"), bp)
    assert ctx.blocked_provenance_verified is True


def test_missing_occurrence_fails():
    dec = _decision_with_blocked_refs([_f2_ref("r.x", "s.a")])
    bp = _blueprint_with_blocked([_blocked_outcome("r.x", "s.a"), _blocked_outcome("r.x", "s.a")])
    with pytest.raises(DecisionValidationError):
        build_decision_context(dec, load_identity(CASE_D / "story_identity.yaml"), bp)


def test_extra_occurrence_fails():
    dec = _decision_with_blocked_refs([_f2_ref("r.x", "s.a"), _f2_ref("r.x", "s.a")])
    bp = _blueprint_with_blocked([_blocked_outcome("r.x", "s.a")])
    with pytest.raises(DecisionValidationError):
        build_decision_context(dec, load_identity(CASE_D / "story_identity.yaml"), bp)


def test_ordering_of_outcomes_is_irrelevant():
    dec = _decision_with_blocked_refs([_f2_ref("r.x", "s.a"), _f2_ref("r.y", "s.b")])
    bp = _blueprint_with_blocked([_blocked_outcome("r.y", "s.b"), _blocked_outcome("r.x", "s.a")])
    ctx = build_decision_context(dec, load_identity(CASE_D / "story_identity.yaml"), bp)
    assert ctx.blocked_provenance_verified is True

def test_one_of_rejects_stray_k():
    with pytest.raises(DecisionValidationError):
        AuthorDecision.from_dict({
            "unresolved_choice": {"question": "q", "options": ["a", "b"]},
            "alternative_ids": ["a", "b"],
            "combination": {"rule": "one_of", "k": 2},
            "criterion": {"text": "c", "evaluator": "author_or_consumer"},
        })
