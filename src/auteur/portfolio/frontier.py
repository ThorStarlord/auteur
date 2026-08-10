"""Non-dominated operational tradeoff frontier."""

from __future__ import annotations

from auteur.portfolio.models import (
    PortfolioFrontier,
    PortfolioScenario,
    _stable_id,
)


class FrontierCalculator:
    """Calculate non-dominated operational tradeoff frontier.

    A portfolio is dominated only when another is at least as favorable
    on every selected dimension and strictly more favorable on at least one.
    """

    SUPPORTED_DIMENSIONS = {
        "blockers": lambda s: s.blocked_milestone_count or 0,
        "stale_artifacts": lambda s: s.stale_artifact_count or 0,
        "uncertainty": lambda s: len(s.uncertainty_summary) if s.uncertainty_summary else 0,
        "optionality": lambda s: -(s.open_decision_count or 0),  # negative: more = better
    }

    def calculate(
        self,
        scenarios: list[PortfolioScenario],
        dimensions: list[str] | None = None,
        portfolio_id: str = "",
    ) -> PortfolioFrontier:
        """Calculate non-dominated frontier.

        Args:
            scenarios: Portfolio scenarios to evaluate.
            dimensions: Dimension names to use (default: blockers, stale_artifacts).
            portfolio_id: Parent portfolio ID.

        Returns:
            PortfolioFrontier with non-dominated scenario IDs.
        """
        dims = dimensions or ["blockers", "stale_artifacts"]

        # Validate dimensions
        for d in dims:
            if d not in self.SUPPORTED_DIMENSIONS:
                raise ValueError(f"Unsupported dimension: {d}. Supported: {list(self.SUPPORTED_DIMENSIONS.keys())}")

        # Compute scores for each scenario
        scored: list[tuple[str, dict[str, float]]] = []
        for s in scenarios:
            scores = {d: self.SUPPORTED_DIMENSIONS[d](s) for d in dims}
            scored.append((s.scenario_id, scores))

        # Determine non-dominated set
        non_dominated: list[str] = []
        explanations: list[str] = []

        for i, (sid_a, scores_a) in enumerate(scored):
            is_dominated = False
            for j, (sid_b, scores_b) in enumerate(scored):
                if i == j:
                    continue
                # Check if b dominates a
                b_at_least_as_good = all(scores_b[d] <= scores_a[d] for d in dims)
                b_strictly_better = any(scores_b[d] < scores_a[d] for d in dims)
                if b_at_least_as_good and b_strictly_better:
                    is_dominated = True
                    break

            if not is_dominated:
                non_dominated.append(sid_a)
                score_str = ", ".join(f"{d}={scores_a[d]}" for d in dims)
                explanations.append(f"{sid_a[:16]}... non-dominated ({score_str})")

        if not non_dominated and scored:
            # All scenarios are tied on all dimensions — all are non-dominated
            non_dominated = [s[0] for s in scored]
            explanations = ["All scenarios tied on all dimensions — all non-dominated"]

        return PortfolioFrontier(
            frontier_id=_stable_id("frontier", portfolio_id or "port"),
            portfolio_id=portfolio_id or "",
            dimensions=dims,
            non_dominated_ids=non_dominated,
            explanations=explanations,
        )
