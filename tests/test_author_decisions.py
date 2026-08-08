"""TDD tests for Author Decision Objects (M4 + thin M2, bounded M3).

Design: docs/design/2026-08-post-propagation-author-decision-objects.md (approved
with revisions). Golden acceptance fixtures: frozen discovery Cases D and E.

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