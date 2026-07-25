"""Portfolio-wide impact and planning projection."""

from __future__ import annotations

import logging
from pathlib import Path

from auteur.portfolio.models import (
    CrossDecisionEffect,
    CrossEffectType,
    PortfolioScenario,
    PortfolioScenarioState,
    _stable_id,
)

logger = logging.getLogger(__name__)


class PortfolioProjector:
    """Project portfolio-wide effects from component scenarios."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def project(
        self,
        scenario: PortfolioScenario,
    ) -> PortfolioScenario:
        """Project portfolio-wide effects for a candidate combination."""
        try:
            # Count stale artifacts via simulation scenarios if available
            stale_count = 0
            open_decisions = len(scenario.assignment)
            blocked_ms = 0

            # Load component scenario projections
            for csid in scenario.component_scenario_ids:
                try:
                    from auteur.simulation.persistence import SimulationStore
                    store = SimulationStore(self.project_root)
                    sim = store.load_scenario(csid)
                    if sim and sim.projected_consequences:
                        stale_count += sum(
                            1 for c in sim.projected_consequences
                            if "stale" in c.description.lower()
                        )
                except Exception:
                    pass

            # Cross-decision effects
            effects: list[CrossDecisionEffect] = self._detect_cross_effects(scenario)

            return PortfolioScenario(
                scenario_id=scenario.scenario_id,
                portfolio_id=scenario.portfolio_id,
                assignment=scenario.assignment,
                state=PortfolioScenarioState.PROJECTED,
                component_scenario_ids=scenario.component_scenario_ids,
                cross_effects=effects,
                stale_artifact_count=stale_count,
                open_decision_count=max(open_decisions - 1, 0),
                blocked_milestone_count=blocked_ms,
                uncertainty_summary=f"{stale_count} projected stale artifacts" if stale_count else "No projected staleness",
            )
        except Exception as e:
            logger.exception(f"Portfolio projection failed for {scenario.scenario_id}")
            return PortfolioScenario(
                scenario_id=scenario.scenario_id,
                portfolio_id=scenario.portfolio_id,
                assignment=scenario.assignment,
                state=PortfolioScenarioState.FAILED,
                error=str(e),
            )

    def _detect_cross_effects(
        self, scenario: PortfolioScenario,
    ) -> list[CrossDecisionEffect]:
        """Detect emergent cross-decision effects."""
        effects: list[CrossDecisionEffect] = []
        decisions = list(scenario.assignment.keys())
        if len(decisions) >= 2:
            effects.append(CrossDecisionEffect(
                effect_id=_stable_id("cross", scenario.scenario_id, "combined"),
                effect_type=CrossEffectType.JOINTLY_UNLOCKS_MILESTONE,
                participating_decisions=decisions,
                participating_candidates=list(scenario.assignment.values()),
                description=f"Combination of {len(decisions)} decisions may unlock milestones",
                evidence_classification="derived",
                confidence="medium",
            ))
        return effects
