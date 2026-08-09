"""Bounded deterministic companion (M3): enumeration and report.

May enumerate permitted alternatives/combinations, apply cardinality rules, and
carry constraint/default/provenance information. MUST NOT render a creative
verdict, invent alternatives, or resolve blocked provenance.
"""
from __future__ import annotations

import itertools
from typing import Any


def enumerate_combinations(decision) -> list[tuple[str, ...]]:
    """Enumerate the permitted combination space from the authored alternatives.

    one_of            -> one tuple per alternative
    choose_k_of_n     -> every k-subset of the alternatives (schema-validated)
    """
    ids = list(decision.alternative_ids)
    if decision.combination.rule == "choose_k_of_n":
        k = decision.combination.k or 1
        return [tuple(c) for c in itertools.combinations(ids, k)]
    return [(i,) for i in ids]


def build_report(ctx) -> dict[str, Any]:
    """Deterministic decision-support report: feasibility/constraint/conflict info only.

    Deliberately contains no 'verdict' and no 'recommended' key: choosing between
    constraint-consistent alternatives is the author's/consumer's responsibility.
    """
    combos = enumerate_combinations(ctx.decision)
    return {
        "decision_id": ctx.decision.decision_id,
        "question": ctx.decision.unresolved_choice.question,
        "alternatives": ctx.alternative_labels,
        "alternative_source": ctx.alternative_source,
        "combination": ctx.decision.combination.rule,
        "enumerated_combinations": [list(c) for c in combos],
        "constraints": [{"ref": c.ref, "text": c.text} for c in ctx.constraints],
        "blocked_provenance": {
            "expected": ctx.blocked_count,
            "verified": ctx.blocked_provenance_verified,
        },
        "resolved_defaults": ctx.resolved_defaults,
        "criterion": ctx.decision.criterion.text,
        "criterion_evaluator": ctx.decision.criterion.evaluator,
    }
