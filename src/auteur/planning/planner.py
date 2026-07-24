"""Project plan production — ordered actions and complete project plans."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.planning.models import (
    CriticalPath,
    PlanAction,
    PlanBlocker,
    PlanMilestone,
    PlanningNode,
    PlanningHorizon,
    ProjectPlan,
    compute_plan_id,
    _stable_id,
)
from auteur.planning.graph import PlanningGraph
from auteur.planning.milestones import MilestoneEngine
from auteur.planning.critical_path import CriticalPathAnalyzer
from auteur.planning.coordinator import SessionCoordinator

logger = logging.getLogger(__name__)


class Planner:
    """Produce ordered actions and complete project plans."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.milestone_engine = MilestoneEngine(self.project_root)

    def create_plan(
        self,
        graph: PlanningGraph,
        nodes: list[PlanningNode],
        edges: list,
        milestones: list[PlanMilestone],
        sessions: list[dict],
        horizon: PlanningHorizon = PlanningHorizon.PROJECT,
        chapter_index: int | None = None,
        prev_plan: ProjectPlan | None = None,
    ) -> ProjectPlan:
        """Create a complete project plan from assembled components.

        Args:
            graph: The dependency graph.
            nodes: All planning nodes.
            edges: All dependency edges.
            milestones: Derived milestones.
            sessions: Raw session dicts.
            horizon: Planning horizon scope.
            chapter_index: Optional chapter filter.
            prev_plan: Previous plan for history computation.

        Returns:
            A complete ProjectPlan with all analysis fields populated.
        """
        # Detect cycles
        cycles = graph.detect_cycles()

        # Compute critical paths
        analyzer = CriticalPathAnalyzer(graph)
        critical_paths = analyzer.compute_critical_paths(milestones, cycles)

        # Compute blockers
        blockers = analyzer.compute_blockers(milestones)

        # Coordinate sessions
        coordinator = SessionCoordinator(graph)
        coordination = coordinator.coordinate_sessions(sessions, nodes)

        # Find safe parallel work
        parallel_groups = coordinator.detect_parallel_work(nodes, sessions)

        # Compute next action
        next_action = analyzer.compute_next_action(
            critical_paths, milestones, nodes, cycles,
        )

        # Identify authority-required actions
        authority_actions = self._find_authority_actions(
            critical_paths, nodes, milestones,
        )

        # Compute counts
        open_decisions = sum(1 for n in nodes if n.node_type.value == "decision")
        active_sessions = sum(
            1 for s in sessions if s.get("state") in (
                "open", "inspecting", "awaiting_choice", "ready", "prepared",
            )
        )
        blocked_milestones = sum(
            1 for m in milestones if m.state.value == "blocked"
        )

        # Determine project title
        title = self._derive_title(horizon, chapter_index)

        # Compute plan ID
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        plan_id = compute_plan_id(str(self.project_root), horizon.value, ts)

        # Detect staleness
        is_stale, stale_reason = self._detect_staleness(
            prev_plan, milestones, sessions,
        )

        # History
        history = self._compute_history(prev_plan, milestones, sessions) if prev_plan else []

        return ProjectPlan(
            plan_id=plan_id,
            project=str(self.project_root),
            horizon=horizon,
            title=title,
            created_at=ts,
            open_decision_count=open_decisions,
            active_review_session_count=active_sessions,
            blocked_milestone_count=blocked_milestones,
            nodes=nodes,
            edges=edges,
            milestones=milestones,
            cycles=cycles,
            critical_paths=critical_paths,
            blockers=blockers,
            safe_parallel_work=parallel_groups,
            coordination_findings=coordination,
            authority_required_actions=authority_actions,
            recommended_next_action=next_action,
            is_stale=is_stale,
            stale_reason=stale_reason,
            plan_history=history,
        )

    def _derive_title(self, horizon: PlanningHorizon, chapter_index: int | None) -> str:
        if horizon == PlanningHorizon.PROJECT:
            return "Project Plan"
        if horizon == PlanningHorizon.BOOK:
            return "Book Plan"
        if horizon == PlanningHorizon.ACT:
            return "Act Plan"
        if horizon == PlanningHorizon.CHAPTER:
            return f"Chapter {chapter_index} Plan" if chapter_index else "Chapter Plan"
        if horizon == PlanningHorizon.SCENE:
            return "Scene Plan"
        return "Project Plan"

    def _find_authority_actions(
        self,
        critical_paths: list[CriticalPath],
        nodes: list[PlanningNode],
        milestones: list[PlanMilestone],
    ) -> list[PlanAction]:
        """Find actions that require author authority."""
        actions: list[PlanAction] = []
        node_map = {n.node_id: n for n in nodes}

        for cp in critical_paths:
            for nid in cp.authority_required_steps:
                n = node_map.get(nid)
                if n:
                    actions.append(PlanAction(
                        action_id=_stable_id("auth", nid),
                        title=f"Resolve: {n.label}",
                        reason=f"On critical path; requires author authority",
                        source_node_id=nid,
                        authority="authority_required",
                        safe_to_execute=False,
                        expected_result_state=f"{nid}_resolved",
                    ))

        # Deduplicate
        seen_ids = set()
        unique: list[PlanAction] = []
        for a in sorted(actions, key=lambda x: x.action_id):
            if a.source_node_id not in seen_ids:
                seen_ids.add(a.source_node_id)
                unique.append(a)
        return unique

    def _detect_staleness(
        self,
        prev_plan: ProjectPlan | None,
        milestones: list[PlanMilestone],
        sessions: list[dict],
    ) -> tuple[bool, str]:
        """Detect if the plan is stale compared to current state."""
        if not prev_plan:
            return False, ""

        # Check for stale milestones
        stale_milestones = [m for m in milestones if m.state.value == "stale"]
        if stale_milestones:
            names = "; ".join(m.title for m in stale_milestones[:3])
            return True, f"Stale milestones: {names}"

        # Check for stale sessions
        stale_sessions = [s for s in sessions if s.get("state") == "stale"]
        if stale_sessions:
            return True, f"{len(stale_sessions)} stale review sessions"

        return False, ""

    def _compute_history(
        self,
        prev_plan: ProjectPlan,
        milestones: list[PlanMilestone],
        sessions: list[dict],
    ) -> list:
        """Compute semantic history between previous and current state."""
        # This is a simplified history — full diff is deferred
        entries = []

        # Check milestone changes
        prev_milestones = {m.milestone_id: m.state.value for m in prev_plan.milestones}
        for m in milestones:
            prev_state = prev_milestones.get(m.milestone_id)
            if prev_state and prev_state != m.state.value:
                entries.append({
                    "change_type": "milestone_state_changed",
                    "description": f"Milestone '{m.title}' changed from {prev_state} to {m.state.value}",
                    "milestone_id": m.milestone_id,
                    "before_state": prev_state,
                    "after_state": m.state.value,
                })

        # Check session changes
        prev_sessions = {s.get("session_id", ""): s.get("state", "") for s in getattr(prev_plan, "_raw_sessions", [])}
        for s in sessions:
            sid = s.get("session_id", "")
            prev_state = prev_sessions.get(sid)
            if prev_state and prev_state != s.get("state"):
                entries.append({
                    "change_type": "session_state_changed",
                    "description": f"Session {sid[:16]}... changed from {prev_state} to {s.get('state')}",
                    "session_id": sid,
                    "before_state": prev_state,
                    "after_state": s.get("state", ""),
                })

        return entries
