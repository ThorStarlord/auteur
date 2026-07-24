"""Simulation service — application-service boundary for counterfactual planning."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.simulation.models import (
    CounterfactualBaseline,
    CounterfactualScenario,
    ScenarioAssumption,
    ScenarioComparison,
    ScenarioPromotionResult,
    ScenarioState,
    CandidateSnapshot,
    _stable_id,
)
from auteur.simulation.baseline import BaselineCapture
from auteur.simulation.projection import ScenarioProjector
from auteur.simulation.comparison import ScenarioComparator
from auteur.simulation.persistence import SimulationStore
from auteur.simulation.promotion import ScenarioPromoter

logger = logging.getLogger(__name__)


class SimulationService:
    """Application-service boundary for counterfactual narrative planning.

    Composes baseline capture, scenario creation/projection, comparison,
    persistence, and promotion. Never mutates live project state.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._validate_project()
        self.baseline_capture = BaselineCapture(self.project_root)
        self.projector = ScenarioProjector(self.project_root)
        self.comparator = ScenarioComparator()
        self.store = SimulationStore(self.project_root)
        self.promoter = ScenarioPromoter(self.project_root)

    def _validate_project(self) -> None:
        marker = self.project_root / ".auteur"
        if not marker.exists():
            raise ValueError(f"Not an Auteur project (no .auteur directory): {self.project_root}")

    # ------------------------------------------------------------------
    # Baseline
    # ------------------------------------------------------------------

    def capture_baseline(self, plan_id: str = "") -> CounterfactualBaseline:
        """Capture current project state as an immutable baseline."""
        baseline = self.baseline_capture.capture(plan_id=plan_id)
        self.store.save_baseline(baseline)
        return baseline

    # ------------------------------------------------------------------
    # Scenario creation and projection
    # ------------------------------------------------------------------

    def create_scenario(
        self,
        decision_id: str,
        candidate_id: str,
        assumptions: list[str] | None = None,
        baseline_id: str | None = None,
    ) -> CounterfactualScenario:
        """Create a counterfactual scenario.

        If no baseline_id is given, captures a fresh baseline automatically.
        """
        baseline: CounterfactualBaseline | None = None
        if baseline_id:
            baseline = self.store.load_baseline(baseline_id)
        if baseline is None:
            baseline = self.capture_baseline()

        # Build candidate snapshot from decision workspace
        candidate_snapshot = self._build_candidate_snapshot(decision_id, candidate_id)

        # Parse assumptions
        assumption_objs: list[ScenarioAssumption] = []
        if assumptions:
            for a in assumptions:
                assumption_objs.append(ScenarioAssumption(
                    assumption_id=_stable_id("user-assume", a[:32]),
                    description=a,
                    is_default=False,
                ))

        scenario = self.projector.create_scenario(
            baseline=baseline,
            decision_id=decision_id,
            candidate_id=candidate_id,
            candidate_snapshot=candidate_snapshot,
            assumptions=assumption_objs,
        )

        self.store.save_scenario(scenario)
        self.store.save_latest(scenario.scenario_id)
        return scenario

    def project_scenario(self, scenario_id: str) -> CounterfactualScenario:
        """Run projection on an existing scenario."""
        scenario = self.store.load_scenario(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario not found: {scenario_id}")

        projected = self.projector.project(scenario)
        self.store.save_scenario(projected)
        self.store.save_latest(projected.scenario_id)
        return projected
    def promote_scenario(
        self, scenario_id: str, confirm: bool = False,
    ) -> ScenarioPromotionResult:
        """Promote a scenario into author review."""
        scenario = self.store.load_scenario(scenario_id)
        if scenario is None:
            return ScenarioPromotionResult(
                success=False, scenario_id=scenario_id,
                error=f"Scenario not found: {scenario_id}",
            )

        result = self.promoter.promote(scenario, confirm=confirm)
        if result.success:
            self.store.save_promotion(scenario_id, result.review_session_id)
            # Update scenario state to PROMOTED
            updated = CounterfactualScenario(
                scenario_id=scenario.scenario_id,
                decision_id=scenario.decision_id,
                candidate_id=scenario.candidate_id,
                baseline_id=scenario.baseline_id,
                state=ScenarioState.PROMOTED,
                candidate_snapshot=scenario.candidate_snapshot,
                assumptions=scenario.assumptions,
                assumptions_hash=scenario.assumptions_hash,
                projected_consequences=scenario.projected_consequences,
                projected_plan=scenario.projected_plan,
                projected_critical_path=scenario.projected_critical_path,
                uncertainty_summary=scenario.uncertainty_summary,
                source_hashes=scenario.source_hashes,
                created_at=scenario.created_at,
            )
            self.store.save_scenario(updated)
            self.store.save_latest(scenario.scenario_id)

        return result

    def discard_scenario(self, scenario_id: str) -> None:
        """Mark a scenario as discarded."""
        scenario = self.store.load_scenario(scenario_id)
        if scenario is None:
            raise ValueError(f"Scenario not found: {scenario_id}")
        updated = CounterfactualScenario(
            scenario_id=scenario.scenario_id,
            decision_id=scenario.decision_id,
            candidate_id=scenario.candidate_id,
            baseline_id=scenario.baseline_id,
            state=ScenarioState.DISCARDED,
            candidate_snapshot=scenario.candidate_snapshot,
            assumptions=scenario.assumptions,
            assumptions_hash=scenario.assumptions_hash,
            projected_consequences=scenario.projected_consequences,
            projected_plan=scenario.projected_plan,
            projected_critical_path=scenario.projected_critical_path,
            uncertainty_summary=scenario.uncertainty_summary,
            source_hashes=scenario.source_hashes,
            created_at=scenario.created_at,
        )
        self.store.save_scenario(updated)
        self.store.save_latest(scenario.scenario_id)

    # ------------------------------------------------------------------
    # Status, inspect, history, list
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Get simulation status."""
        latest_id = self.store.load_latest_id()
        scenarios = self.store.list_scenarios()
        active = [s for s in scenarios if s.get("state") not in ("discarded", "failed")]
        return {
            "has_latest": latest_id is not None,
            "latest_scenario_id": latest_id or "",
            "total_scenarios": len(scenarios),
            "active_scenarios": len(active),
        }

    def inspect(self, scenario_id: str) -> CounterfactualScenario | None:
        """Inspect a scenario."""
        return self.store.load_scenario(scenario_id)

    def list_scenarios(self) -> list[dict[str, Any]]:
        """List all scenarios."""
        return self.store.list_scenarios()

    def history(self) -> list[dict[str, Any]]:
        """Get simulation history."""
        return self.store.list_history()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_candidate_snapshot(
        self, decision_id: str, candidate_id: str,
    ) -> CandidateSnapshot | None:
        """Build a candidate snapshot from the decision workspace."""
        try:
            from auteur.decision.service import DecisionWorkspaceService
            svc = DecisionWorkspaceService(self.project_root)
            decision = svc.inspect(decision_id)
            if decision:
                for c in getattr(decision, "candidates", []):
                    cid = c.candidate_id if hasattr(c, "candidate_id") else str(c)
                    if cid == candidate_id:
                        return CandidateSnapshot(
                            candidate_id=candidate_id,
                            decision_id=decision_id,
                            label=getattr(c, "label", getattr(c, "title", candidate_id)),
                            freshness="current",
                        )
        except Exception as e:
            logger.debug(f"Could not build candidate snapshot: {e}")
        return CandidateSnapshot(
            candidate_id=candidate_id,
            decision_id=decision_id,
        )
