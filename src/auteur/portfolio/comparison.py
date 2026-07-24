"""Semantic portfolio comparison."""

from __future__ import annotations

from dataclasses import dataclass, field

from auteur.portfolio.models import PortfolioScenario, _stable_id


@dataclass(frozen=True)
class PortfolioComparison:
    """Result of comparing two portfolio scenarios."""
    comparison_id: str
    scenario_a_id: str
    scenario_b_id: str
    shared_effects: int = 0
    a_only_effects: list[str] = field(default_factory=list)
    b_only_effects: list[str] = field(default_factory=list)
    staleness_difference: int = 0
    open_decision_difference: int = 0
    blocked_milestone_difference: int = 0
    evidence_asymmetry: str = ""
    uncertainty_asymmetry: str = ""


class PortfolioComparator:
    """Compare two portfolio scenarios."""

    def compare(
        self, a: PortfolioScenario, b: PortfolioScenario,
    ) -> PortfolioComparison:
        cid = _stable_id("pcmp", a.scenario_id, b.scenario_id)
        staleness_diff = (a.stale_artifact_count or 0) - (b.stale_artifact_count or 0)
        decision_diff = (a.open_decision_count or 0) - (b.open_decision_count or 0)
        milestone_diff = (a.blocked_milestone_count or 0) - (b.blocked_milestone_count or 0)

        a_only = [f"A: {v}" for v in a.assignment.values() if v not in b.assignment.values()]
        b_only = [f"B: {v}" for v in b.assignment.values() if v not in a.assignment.values()]

        return PortfolioComparison(
            comparison_id=cid,
            scenario_a_id=a.scenario_id,
            scenario_b_id=b.scenario_id,
            shared_effects=min(len(a.cross_effects), len(b.cross_effects)),
            a_only_effects=a_only,
            b_only_effects=b_only,
            staleness_difference=staleness_diff,
            open_decision_difference=decision_diff,
            blocked_milestone_difference=milestone_diff,
        )
