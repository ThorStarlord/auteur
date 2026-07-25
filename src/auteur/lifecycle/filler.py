"""Automated gap filling for decision lifecycle. Requires confirmation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.lifecycle.integrator import LifecycleIntegrator
from auteur.lifecycle.models import LifecycleStage

logger = logging.getLogger(__name__)


class LifecycleFiller:
    """Fill lifecycle gaps by routing to appropriate subsystems."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.integrator = LifecycleIntegrator(self.project_root)

    def detect_fillable_gaps(self) -> list[dict[str, Any]]:
        """Detect gaps that can be automatically filled.

        Returns list of gap descriptors with action, subsystem, and affected decisions.
        """
        entries = self.integrator.get_lifecycle_entries()
        gaps: list[dict[str, Any]] = []

        open_decisions = [e for e in entries if e.stage == LifecycleStage.OPEN]
        if open_decisions:
            gaps.append({
                "gap_type": "simulate",
                "title": f"Create simulation scenarios for {len(open_decisions)} open decision(s)",
                "description": "Generate counterfactual scenarios for decisions not yet simulated.",
                "decision_ids": [e.decision_id for e in open_decisions],
                "command": "auteur simulate create",
            })

        sim_decisions = [e for e in entries if e.stage == LifecycleStage.SIMULATED]
        if sim_decisions:
            gaps.append({
                "gap_type": "portfolio",
                "title": f"Create portfolio for {len(sim_decisions)} simulated decision(s)",
                "description": "Generate portfolio combinations for simulated decisions.",
                "decision_ids": [e.decision_id for e in sim_decisions],
                "command": "auteur portfolio generate-combinations",
            })

        return gaps

    def fill_gap(self, gap_type: str, confirm: bool = False) -> list[dict[str, Any]]:
        """Execute gap filling for a specific gap type.

        Args:
            gap_type: One of 'simulate' or 'portfolio'.
            confirm: Must be True to execute.

        Returns:
            List of per-action results.
        """
        if not confirm:
            raise ValueError("Confirmation required. Pass confirm=True.")
        if gap_type == "simulate":
            return self._fill_simulate()
        elif gap_type == "portfolio":
            return self._fill_portfolio()
        else:
            raise ValueError(f"Unknown gap type: {gap_type}")

    def _fill_simulate(self) -> list[dict[str, Any]]:
        """Create simulation scenarios for open decisions."""
        results: list[dict[str, Any]] = []
        entries = self.integrator.get_lifecycle_entries()
        open_decisions = [e for e in entries if e.stage == LifecycleStage.OPEN]

        if not open_decisions:
            return [{"action": "simulate", "status": "skipped", "message": "No open decisions to simulate"}]

        try:
            from auteur.simulation.service import SimulationService
            svc = SimulationService(self.project_root)
        except Exception as e:
            return [{"action": "simulate", "status": "failed", "message": str(e)}]

        for entry in open_decisions:
            try:
                scenario = svc.create_scenario(
                    decision_id=entry.decision_id,
                    candidate_id="auto",
                )
                results.append({
                    "decision_id": entry.decision_id,
                    "action": "simulate",
                    "status": "created",
                    "scenario_id": getattr(scenario, "scenario_id", ""),
                    "message": "Simulation scenario created",
                })
            except Exception as e:
                results.append({
                    "decision_id": entry.decision_id,
                    "action": "simulate",
                    "status": "failed",
                    "message": str(e),
                })

        return results

    def _fill_portfolio(self) -> list[dict[str, Any]]:
        """Create portfolio for simulated decisions."""
        results: list[dict[str, Any]] = []
        entries = self.integrator.get_lifecycle_entries()
        sim_decisions = [e for e in entries if e.stage == LifecycleStage.SIMULATED]

        if not sim_decisions:
            return [{"action": "portfolio", "status": "skipped", "message": "No simulated decisions without portfolio"}]

        try:
            from auteur.portfolio.service import PortfolioService
            svc = PortfolioService(self.project_root)
        except Exception as e:
            return [{"action": "portfolio", "status": "failed", "message": str(e)}]

        assignments = {e.decision_id: e.description or "auto" for e in sim_decisions}
        try:
            portfolio = svc.create_portfolio(assignments=assignments, confirm=True)
            portfolio = svc.generate_combinations(portfolio.portfolio_id)
            results.append({
                "action": "portfolio",
                "status": "created",
                "portfolio_id": portfolio.portfolio_id,
                "decision_count": len(sim_decisions),
                "message": f"Portfolio created with {len(sim_decisions)} decision(s)",
            })
        except Exception as e:
            results.append({
                "action": "portfolio",
                "status": "failed",
                "message": str(e),
            })

        return results
