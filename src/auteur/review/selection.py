"""Deterministic review-target selection from the Decision Workspace."""

from __future__ import annotations

from typing import Any

from auteur.decision.models import DecisionReadiness, EvidenceFreshness, LifecycleState


def select_highest_priority(
    decisions: list[Any],
) -> tuple[Any | None, str, list[str]]:
    """Select the highest-priority open decision for review.

    Args:
        decisions: List of AuthorDecision objects.

    Returns:
        Tuple of (selected_decision, reason, alternatives_considered).
    """
    if not decisions:
        return None, "No open decisions", []

    # Priority order (highest first)
    priority_map = {
        DecisionReadiness.BLOCKED: 1,
        DecisionReadiness.STALE: 2,
        DecisionReadiness.NEEDS_AUTHOR_DECISION: 3,
        DecisionReadiness.READY_FOR_ACCEPTANCE: 4,
        DecisionReadiness.NEEDS_RECONCILIATION: 5,
        DecisionReadiness.NEEDS_EVALUATION: 6,
        DecisionReadiness.NEEDS_COMPARISON: 7,
        DecisionReadiness.NEEDS_CANDIDATE: 8,
        DecisionReadiness.RESOLVED: 9,
    }

    ranked = []
    for d in decisions:
        priority = priority_map.get(d.readiness, 99)
        ranked.append((priority, d.chapter_index, d.decision_id, d))

    ranked.sort(key=lambda x: (x[0], x[1], x[2]))
    selected = ranked[0]
    decision = selected[3]

    alternatives = [
        f"ch{d.chapter_index}/{d.decision_id[:12]}... ({d.readiness.value})"
        for _, _, _, d in ranked[1:4]
    ]

    readiness_label = decision.readiness.value
    reason = (
        f"Highest priority decision: {readiness_label} "
        f"(ch{decision.chapter_index}, {decision.target_artifact_id[:24]})"
    )

    return decision, reason, alternatives
