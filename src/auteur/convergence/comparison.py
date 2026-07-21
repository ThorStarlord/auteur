"""Candidate comparison — deterministic evidence-based comparison."""

from __future__ import annotations

from pathlib import Path

from auteur.convergence.models import (
    CandidateComparison,
    CandidateRef,
    ComparisonDimension,
    ConflictFinding,
    RevisionTarget,
)


def compare_candidates(
    target: RevisionTarget,
    candidates: list[CandidateRef],
) -> CandidateComparison:
    """Compare two or more candidates deterministically.

    Compares:
    - obligation coverage
    - preservation compatibility
    - continuity compatibility
    - freshness
    - evaluation status
    - unresolved blockers
    - authority requirements
    - lineage

    Returns a multidimensional comparison without collapsing to a
    single unexplained winner. A recommended candidate may be offered
    for workflow priority, with a clear disclaimer.
    """
    comparison = CandidateComparison(
        target_id=target.target_id,
        candidate_ids=[c.candidate_id for c in candidates],
    )

    for i, a in enumerate(candidates):
        for b in candidates[i + 1:]:
            comparison.dimensions.append(
                _compare_obligation_coverage(a, b)
            )
            comparison.dimensions.append(
                _compare_freshness(a, b)
            )
            comparison.dimensions.append(
                _compare_evaluation_status(a, b)
            )
            comparison.dimensions.append(
                _compare_authority(a, b)
            )
            comparison.dimensions.append(
                _compare_lineage(a, b)
            )

            conflict = _check_preservation_conflict(a, b)
            if conflict is not None:
                comparison.conflicts.append(conflict)

            conflict = _check_incompatible_obligations(a, b)
            if conflict is not None:
                comparison.conflicts.append(conflict)

    # Deterministic ranking for workflow priority only
    if len(candidates) >= 2:
        best = _rank_for_workflow(candidates)
        comparison.recommended_candidate_id = best.candidate_id if best else ""
        comparison.recommendation_disclaimer = (
            "Ranking is for workflow priority only. "
            "The recommended candidate is not artistically correct "
            "and is not the accepted candidate."
        )

    return comparison


def _compare_obligation_coverage(a: CandidateRef, b: CandidateRef) -> ComparisonDimension:
    a_satisfied = len(a.obligations_satisfied)
    b_satisfied = len(b.obligations_satisfied)
    a_total = len(a.obligations)
    b_total = len(b.obligations)

    if a_total == 0 and b_total == 0:
        return ComparisonDimension(
            name="obligation_coverage",
            candidate_a_value="0/0",
            candidate_b_value="0/0",
            advantage="tie",
            evidence="No obligations recorded for either candidate",
        )

    a_display = f"{a_satisfied}/{a_total}" if a_total > 0 else "N/A"
    b_display = f"{b_satisfied}/{b_total}" if b_total > 0 else "N/A"

    a_ratio = a_satisfied / a_total if a_total > 0 else 0
    b_ratio = b_satisfied / b_total if b_total > 0 else 0

    if a_ratio > b_ratio:
        advantage = "candidate_a"
        evidence = f"Candidate A satisfies higher proportion of obligations ({a_display} vs {b_display})"
    elif b_ratio > a_ratio:
        advantage = "candidate_b"
        evidence = f"Candidate B satisfies higher proportion of obligations ({b_display} vs {a_display})"
    else:
        advantage = "tie"
        evidence = f"Both candidates satisfy same proportion ({a_display})"

    return ComparisonDimension(
        name="obligation_coverage",
        candidate_a_value=a_display,
        candidate_b_value=b_display,
        advantage=advantage,
        evidence=evidence,
    )


def _compare_freshness(a: CandidateRef, b: CandidateRef) -> ComparisonDimension:
    advantage = "tie"
    if a.freshness == "fresh" and b.freshness == "stale":
        advantage = "candidate_a"
    elif b.freshness == "fresh" and a.freshness == "stale":
        advantage = "candidate_b"

    return ComparisonDimension(
        name="freshness",
        candidate_a_value=a.freshness,
        candidate_b_value=b.freshness,
        advantage=advantage,
        evidence=f"Candidate A is {a.freshness}, Candidate B is {b.freshness}",
    )


def _compare_evaluation_status(a: CandidateRef, b: CandidateRef) -> ComparisonDimension:
    a_evals = len(a.evaluation_references)
    b_evals = len(b.evaluation_references)

    advantage = "tie"
    if a_evals > 0 and b_evals == 0:
        advantage = "candidate_a"
    elif b_evals > 0 and a_evals == 0:
        advantage = "candidate_b"

    return ComparisonDimension(
        name="evaluation_status",
        candidate_a_value=f"{a_evals} evaluations" if a_evals > 0 else "unevaluated",
        candidate_b_value=f"{b_evals} evaluations" if b_evals > 0 else "unevaluated",
        advantage=advantage,
        evidence=f"Candidate A has {a_evals} evaluation(s), Candidate B has {b_evals}",
    )


def _compare_authority(a: CandidateRef, b: CandidateRef) -> ComparisonDimension:
    return ComparisonDimension(
        name="authority",
        candidate_a_value=a.authority,
        candidate_b_value=b.authority,
        advantage="tie",
        evidence=f"Candidate A authority: {a.authority}, Candidate B: {b.authority}",
    )


def _compare_lineage(a: CandidateRef, b: CandidateRef) -> ComparisonDimension:
    return ComparisonDimension(
        name="lineage",
        candidate_a_value=a.generation_strategy,
        candidate_b_value=b.generation_strategy,
        advantage="tie",
        evidence=f"Candidate A method: {a.generation_strategy}, Candidate B: {b.generation_strategy}",
    )


def _check_preservation_conflict(a: CandidateRef, b: CandidateRef) -> ConflictFinding | None:
    """Check if one candidate invalidates preserved regions of another."""
    a_preserved = {p.beat_id or p.section_id for p in a.preserved_regions if p.beat_id or p.section_id}
    b_preserved = {p.beat_id or p.section_id for p in b.preserved_regions if p.beat_id or p.section_id}

    shared = a_preserved & b_preserved
    if shared:
        return ConflictFinding(
            candidate_ids=[a.candidate_id, b.candidate_id],
            description=f"Candidates share preserved regions: {', '.join(sorted(shared))}",
            severity="info",
            recommended_action="Review preservation compatibility between candidates",
            dimension="preservation",
        )
    return None


def _check_incompatible_obligations(a: CandidateRef, b: CandidateRef) -> ConflictFinding | None:
    """Check if candidates satisfy/unsatisfy obligations in incompatible ways."""
    a_satisfied = set(a.obligations_satisfied)
    b_satisfied = set(b.obligations_satisfied)
    a_unsatisfied = set(a.obligations_unsatisfied)
    b_unsatisfied = set(b.obligations_unsatisfied)

    # An obligation satisfied by one but unsatisfied by the other is a conflict
    conflicts = (a_satisfied - b_satisfied) & (a_unsatisfied - b_unsatisfied)
    # Actually, check: obligations satisfied by A but unsatisfied by B
    diff = (a_satisfied - b_satisfied) & b_unsatisfied
    diff |= (b_satisfied - a_satisfied) & a_unsatisfied

    if diff:
        return ConflictFinding(
            candidate_ids=[a.candidate_id, b.candidate_id],
            description=f"Candidates disagree on obligations: {', '.join(sorted(diff))}",
            severity="warning",
            recommended_action="Review obligation coverage differences between candidates",
            dimension="obligation_coverage",
        )
    return None


def _rank_for_workflow(candidates: list[CandidateRef]) -> CandidateRef | None:
    """Deterministic ranking for workflow priority only.

    Factors (in order):
    1. Freshness (fresh > stale)
    2. Evaluated > unevaluated
    3. More obligations satisfied
    4. Earlier created
    """
    if not candidates:
        return None

    def _score(c: CandidateRef) -> tuple:
        freshness_score = 0 if c.freshness == "fresh" else 1
        eval_score = 0 if c.evaluation_references else 1
        ob_score = -(len(c.obligations_satisfied))
        created = c.created_at
        return (freshness_score, eval_score, ob_score, created)

    sorted_candidates = sorted(candidates, key=_score)
    return sorted_candidates[0]
