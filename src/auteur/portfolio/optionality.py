"""Optionality analysis for portfolio scenarios."""

from __future__ import annotations

from auteur.portfolio.models import OptionalityReport, PortfolioScenario, _stable_id


class OptionalityAnalyzer:
    """Analyze remaining viable decisions and reversibility."""

    def analyze(self, scenario: PortfolioScenario) -> OptionalityReport:
        """Analyze optionality for a portfolio scenario."""
        remaining = {}
        irreversible = []
        for dec_id, cand_id in scenario.assignment.items():
            remaining[dec_id] = [cand_id]
        return OptionalityReport(
            report_id=_stable_id("opt", scenario.scenario_id),
            remaining_candidates=remaining,
            irreversible_decisions=irreversible,
            summary=f"{len(remaining)} decisions locked, {len(irreversible)} irreversible",
        )
