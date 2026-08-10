"""Candidate-specific impact and project-plan projection."""

from __future__ import annotations

import logging
from pathlib import Path

from auteur.simulation.models import (
    CandidateSnapshot,
    ConfidenceLevel,
    ConsequenceCategory,
    CounterfactualBaseline,
    CounterfactualScenario,
    ProjectedConsequence,
    ProjectedCriticalPath,
    ProjectedPlan,
    ScenarioAssumption,
    ScenarioState,
    compute_scenario_id,
    _stable_id,
)
from auteur.simulation.overlay import ScenarioOverlay

logger = logging.getLogger(__name__)


def _normalize_assumptions(assumptions: list[ScenarioAssumption]) -> str:
    """Compute a deterministic hash of normalized assumptions."""
    import hashlib
    import json
    sorted_text = sorted(a.description for a in assumptions)
    return hashlib.sha256(json.dumps(sorted_text, sort_keys=True).encode()).hexdigest()[:16]


def _ensure_assumptions(
    assumptions: list[ScenarioAssumption | dict] | None,
) -> list[ScenarioAssumption]:
    """Normalize assumptions — handle dicts from JSON deserialization."""
    from auteur.simulation.models import AssumptionCategory
    result: list[ScenarioAssumption] = []
    if assumptions:
        for a in assumptions:
            if isinstance(a, dict):
                cat = a.get("category", "structural")
                result.append(ScenarioAssumption(
                    assumption_id=a.get("assumption_id", ""),
                    description=a.get("description", ""),
                    is_default=a.get("is_default", True),
                    category=AssumptionCategory(cat) if isinstance(cat, str) else cat,
                ))
            else:
                result.append(a)
    return result


class ScenarioProjector:
    """Project candidate-specific downstream effects for a scenario.

    Reuses existing impact analysis and planning contracts without
    mutating any live store.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def create_scenario(
        self,
        baseline: CounterfactualBaseline,
        decision_id: str,
        candidate_id: str,
        candidate_snapshot: CandidateSnapshot | None = None,
        assumptions: list[ScenarioAssumption] | None = None,
    ) -> CounterfactualScenario:
        """Create a counterfactual scenario with baseline reference."""
        normalized = _ensure_assumptions(assumptions)
        default_assumptions = self._default_assumptions()
        all_assumptions = normalized + [
            a for a in default_assumptions
            if a.assumption_id not in {x.assumption_id for x in normalized}
        ]
        ahash = _normalize_assumptions(all_assumptions)
        scenario_id = compute_scenario_id(
            str(self.project_root), baseline.baseline_id,
            decision_id, candidate_id, ahash,
        )

        return CounterfactualScenario(
            scenario_id=scenario_id,
            decision_id=decision_id,
            candidate_id=candidate_id,
            baseline_id=baseline.baseline_id,
            state=ScenarioState.CREATED,
            candidate_snapshot=candidate_snapshot,
            assumptions=all_assumptions,
            assumptions_hash=ahash,
            source_hashes={
                "baseline": baseline.baseline_id,
                "candidate": candidate_id,
            },
        )

    def project(self, scenario: CounterfactualScenario) -> CounterfactualScenario:
        """Run projection on a scenario.

        Constructs an overlay, derives consequences, and produces
        projected impact and plan data.
        """
        # Normalize assumptions in case they came from JSON deserialization
        norm_assumptions = _ensure_assumptions(list(scenario.assumptions))

        overlay = ScenarioOverlay(baseline=CounterfactualBaseline(
            baseline_id=scenario.baseline_id, project=str(self.project_root),
        ))

        try:
            consequences: list[ProjectedConsequence] = []

            # 1. Project known consequences from candidate selection
            consequences.extend(self._project_known_consequences(scenario))

            # 2. Project derived impact via overlay
            consequences.extend(self._project_derived_impact(scenario, overlay))

            # 3. Project inferred consequences
            consequences.extend(self._project_inferred_consequences(scenario, overlay))

            # 4. Build projected plan
            proj_plan = self._project_plan(scenario, overlay)

            # 5. Build projected critical path
            proj_cp = self._project_critical_path(scenario, overlay)

            # 6. Determine unknowns
            unknowns = self._determine_unknowns(scenario)
            if unknowns:
                consequences.append(ProjectedConsequence(
                    consequence_id=_stable_id("unknown", scenario.scenario_id),
                    target="multiple",
                    description="; ".join(unknowns[:5]),
                    classification=ConsequenceCategory.UNKNOWN,
                    confidence=ConfidenceLevel.UNDETERMINED,
                    projected_action="Review unresolved uncertainty",
                ))

            # Build uncertainty summary
            uncertainty_parts = []
            uncertain = [c for c in consequences if c.confidence in (
                ConfidenceLevel.LOW, ConfidenceLevel.UNDETERMINED)]
            if uncertain:
                uncertainty_parts.append(f"{len(uncertain)} uncertain consequences")
            if unknowns:
                uncertainty_parts.append(f"{len(unknowns)} unknowns")

            return CounterfactualScenario(
                scenario_id=scenario.scenario_id,
                decision_id=scenario.decision_id,
                candidate_id=scenario.candidate_id,
                baseline_id=scenario.baseline_id,
                state=ScenarioState.PROJECTED,
                candidate_snapshot=scenario.candidate_snapshot,
                assumptions=norm_assumptions,
                assumptions_hash=scenario.assumptions_hash,
                projected_consequences=sorted(consequences, key=lambda c: c.consequence_id),
                projected_plan=proj_plan,
                projected_critical_path=proj_cp,
                uncertainty_summary="; ".join(uncertainty_parts) if uncertainty_parts else "No significant uncertainty",
                source_hashes=scenario.source_hashes,
            )
        except Exception as e:
            logger.exception(f"Projection failed for {scenario.scenario_id}")
            return CounterfactualScenario(
                scenario_id=scenario.scenario_id,
                decision_id=scenario.decision_id,
                candidate_id=scenario.candidate_id,
                baseline_id=scenario.baseline_id,
                state=ScenarioState.FAILED,
                assumptions=norm_assumptions,
                error=str(e),
            )

    def _default_assumptions(self) -> list[ScenarioAssumption]:
        """Default assumptions for any scenario."""
        return [
            ScenarioAssumption(
                assumption_id=_stable_id("assume", "candidate-accepted"),
                description="Candidate is hypothetically accepted without further textual changes",
                is_default=True,
            ),
            ScenarioAssumption(
                assumption_id=_stable_id("assume", "unrelated-open"),
                description="Unrelated open decisions remain unresolved",
                is_default=True,
            ),
            ScenarioAssumption(
                assumption_id=_stable_id("assume", "dependencies-valid"),
                description="Current structural dependencies remain valid",
                is_default=True,
            ),
            ScenarioAssumption(
                assumption_id=_stable_id("assume", "workflow-contracts"),
                description="Downstream generation follows current workflow contracts",
                is_default=True,
            ),
        ]

    def _project_known_consequences(
        self, scenario: CounterfactualScenario,
    ) -> list[ProjectedConsequence]:
        """Project consequences that are directly KNOWN from current state."""
        consequences: list[ProjectedConsequence] = []

        consequences.append(ProjectedConsequence(
            consequence_id=_stable_id("known", scenario.scenario_id, "decision-resolved"),
            target=scenario.decision_id,
            description=f"Decision {scenario.decision_id[:16]}... hypothetically resolved via candidate {scenario.candidate_id[:16]}...",
            classification=ConsequenceCategory.KNOWN,
            confidence=ConfidenceLevel.CERTAIN,
            supporting_evidence=[scenario.candidate_id],
            projected_action="Review candidate evidence",
        ))

        consequences.append(ProjectedConsequence(
            consequence_id=_stable_id("known", scenario.scenario_id, "artifact-stale"),
            target=scenario.decision_id,
            description="Artifacts dependent on this decision may become stale",
            classification=ConsequenceCategory.KNOWN,
            confidence=ConfidenceLevel.CERTAIN,
            projected_action="Refresh stale artifacts after decision",
        ))

        return consequences

    def _project_derived_impact(
        self, scenario: CounterfactualScenario,
        overlay: ScenarioOverlay,
    ) -> list[ProjectedConsequence]:
        """Project consequences deterministically derived from known rules."""
        consequences: list[ProjectedConsequence] = []

        try:
            from auteur.decision.service import DecisionWorkspaceService
            svc = DecisionWorkspaceService(self.project_root)
            preview = svc.impact_preview(scenario.decision_id, scenario.candidate_id)
            if preview:
                if preview.definite_impacts:
                    overlay.record_stale_artifact(
                        preview.definite_impacts[0].artifact_id
                    )
                    consequences.append(ProjectedConsequence(
                        consequence_id=_stable_id("derived", scenario.scenario_id, "impact"),
                        target=preview.definite_impacts[0].artifact_id,
                        description=f"Definite impact: {preview.definite_impacts[0].description}",
                        classification=ConsequenceCategory.DERIVED,
                        confidence=ConfidenceLevel.HIGH,
                        supporting_evidence=["impact_preview"],
                    ))
        except Exception:
            pass

        return consequences

    def _project_inferred_consequences(
        self, scenario: CounterfactualScenario,
        overlay: ScenarioOverlay,
    ) -> list[ProjectedConsequence]:
        """Project consequences based on semantic inference."""
        consequences: list[ProjectedConsequence] = []

        consequences.append(ProjectedConsequence(
            consequence_id=_stable_id("infer", scenario.scenario_id, "milestone"),
            target="milestones",
            description="Milestone progress may change depending on downstream effects",
            classification=ConsequenceCategory.INFERRED,
            confidence=ConfidenceLevel.MEDIUM,
            projected_action="Re-evaluate milestones after projection",
        ))

        consequences.append(ProjectedConsequence(
            consequence_id=_stable_id("infer", scenario.scenario_id, "new-decisions"),
            target="decisions",
            description="New decisions may be required for downstream chapters",
            classification=ConsequenceCategory.INFERRED,
            confidence=ConfidenceLevel.LOW,
            projected_action="Review downstream chapters for new decisions",
        ))

        return consequences

    def _determine_unknowns(self, scenario: CounterfactualScenario) -> list[str]:
        """Determine what remains unknowable."""
        return [
            "Full manuscript impact without regeneration",
            "Author's creative response to downstream choices",
            "Reader reception of candidate content",
        ]

    def _project_plan(
        self, scenario: CounterfactualScenario,
        overlay: ScenarioOverlay,
    ) -> ProjectedPlan:
        """Build a projected project plan using the overlay."""
        plan_milestones: list[dict] = []
        plan_edges: list[dict] = []
        plan_cycles: list[list[str]] = []
        open_decisions = 1
        blocked_milestones = 0

        try:
            from auteur.planning.service import PlanningService
            svc = PlanningService(self.project_root)
            live_plan = svc.refresh(save=False)
            if live_plan:
                plan_milestones = [{"title": m.title} for m in live_plan.milestones]
                open_decisions = live_plan.open_decision_count
                blocked_milestones = live_plan.blocked_milestone_count
        except Exception:
            pass

        if open_decisions > 0:
            open_decisions = max(open_decisions - 1, 0)

        return ProjectedPlan(
            plan_id=_stable_id("proj-plan", scenario.scenario_id),
            open_decision_count=open_decisions,
            blocked_milestone_count=blocked_milestones,
            milestones=plan_milestones,
            edges=plan_edges,
            cycles=plan_cycles,
        )

    def _project_critical_path(
        self, scenario: CounterfactualScenario,
        overlay: ScenarioOverlay,
    ) -> ProjectedCriticalPath:
        """Build a projected critical path using overlay state."""
        path_nodes: list[str] = []
        blocked_mids: list[str] = []
        auth_steps: list[str] = []
        leverage = 0.0

        try:
            from auteur.planning.service import PlanningService
            svc = PlanningService(self.project_root)
            live_plan = svc.refresh(save=False)
            if live_plan and live_plan.critical_paths:
                for cp in live_plan.critical_paths:
                    if scenario.decision_id in cp.ordered_node_ids:
                        path_nodes = [n for n in cp.ordered_node_ids
                                      if n != scenario.decision_id]
                        blocked_mids = cp.blocked_milestone_ids[:]
                        auth_steps = cp.authority_required_steps[:]
                        leverage = cp.cumulative_leverage
                        break
                    else:
                        path_nodes = cp.ordered_node_ids[:]
                        blocked_mids = cp.blocked_milestone_ids[:]
                        auth_steps = cp.authority_required_steps[:]
                        leverage = cp.cumulative_leverage
        except Exception:
            pass

        return ProjectedCriticalPath(
            path_id=_stable_id("proj-cp", scenario.scenario_id),
            ordered_node_ids=path_nodes,
            blocked_milestone_ids=blocked_mids,
            cumulative_leverage=leverage,
            authority_required_steps=auth_steps,
        )
