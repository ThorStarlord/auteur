"""Critical-path computation for project planning.

This is NOT duration-based CPM. It computes a **narrative blocking critical
path** based on graph structure and milestone impact.

The resulting path is labelled "blocking critical path", not "creative priority".
"""

from __future__ import annotations

from auteur.planning.models import (
    CriticalPath,
    DependencyStrength,
    MilestoneState,
    PlanAction,
    PlanBlocker,
    PlanDependency,
    PlanMilestone,
    PlanningNode,
    _stable_id,
)
from auteur.planning.graph import PlanningGraph


class CriticalPathAnalyzer:
    """Compute deterministic blocking critical paths and leverage."""

    LEVERAGE_DIRECT_BLOCKED = 1.0
    LEVERAGE_TRANSITIVE_BLOCKED = 0.5
    LEVERAGE_MILESTONE_BLOCKING = 10.0
    LEVERAGE_MILESTONE_IN_PROGRESS = 5.0
    LEVERAGE_AUTHORITY_REQUIRED = 3.0
    LEVERAGE_STALE = 2.0
    LEVERAGE_PARALLEL_WORKAROUND = -1.0

    def __init__(self, graph: PlanningGraph) -> None:
        self.graph = graph

    def compute_critical_paths(
        self,
        milestones: list[PlanMilestone],
        cycles: list[list[str]],
    ) -> list[CriticalPath]:
        """Compute all blocking critical paths.

        Paths are ordered by cumulative leverage (highest first).
        Cycles are reported separately and excluded from ordering.
        """
        blocked_nodes = self._find_blocked_nodes(milestones, cycles)
        if not blocked_nodes:
            return []

        # Compute leverage for each blocked node
        node_leverage: list[tuple[str, float]] = []
        for nid in blocked_nodes:
            lev = self._compute_leverage(nid, milestones, cycles)
            node_leverage.append((nid, lev))

        # Sort by leverage descending, then by node_id for determinism
        node_leverage.sort(key=lambda x: (-x[1], x[0]))

        # Build paths from sorted nodes
        paths: list[CriticalPath] = []
        for nid, lev in node_leverage:
            path = self._build_path(nid, milestones, cycles)
            if path:
                path_cum = sum(
                    self._compute_leverage(nid, milestones, cycles)
                    for nid in path.ordered_node_ids
                )
                object.__setattr__(path, "cumulative_leverage", path_cum)
                paths.append(path)

        return paths

    def compute_next_action(
        self,
        critical_paths: list[CriticalPath],
        milestones: list[PlanMilestone],
        nodes: list[PlanningNode],
        cycles: list[list[str]],
    ) -> PlanAction | None:
        """Compute the single highest-leverage next action.

        Ordering preference:
        1. Malformed provenance / graph corruption (cycles)
        2. Hard dependency cycles
        3. Stale acceptance preparation
        4. Failed post-acceptance refresh
        5. Blocked active review session
        6. Unresolved author-required decision on critical path
        7. Safe action unlocking critical-path work
        8. Required evidence refresh
        9. Milestone gate
        10. Lower-leverage independent work
        """
        # 1. Cycles need attention first
        if cycles:
            cycle_nodes = []
            for cycle in cycles:
                for nid in cycle:
                    n = self.graph.get_node(nid)
                    if n:
                        cycle_nodes.append(n.label or nid)
            return PlanAction(
                action_id=_stable_id("action", "resolve-cycles"),
                title="Resolve dependency cycles",
                reason=f"Hard cycle detected involving: {', '.join(cycle_nodes[:5])}",
                source_node_id=cycles[0][0] if cycles[0] else "",
                authority="authority_required",
                safe_to_execute=False,
                expected_result_state="cycles_resolved",
            )

        # 2. Critical path has highest leverage
        if critical_paths:
            best = critical_paths[0]
            if best.ordered_node_ids:
                first_nid = best.ordered_node_ids[0]
                first_node = self.graph.get_node(first_nid)
                if first_node:
                    return PlanAction(
                        action_id=_stable_id("action", f"resolve-{first_nid[:12]}"),
                        title=f"Resolve {first_node.label or first_nid}",
                        reason=best.explanation[:200] if best.explanation else f"First step on critical path (leverage={best.cumulative_leverage:.1f})",
                        source_node_id=first_nid,
                        authority="authority_required" if first_nid in best.authority_required_steps else "recommendation",
                        safe_to_execute=first_nid in best.safe_steps,
                        expected_result_state="critical_path_unblocked",
                        blocked_milestones_released=best.blocked_milestone_ids,
                    )

        # 3. No critical path — check for ready milestones
        ready_milestones = [m for m in milestones if m.state == MilestoneState.READY]
        if ready_milestones:
            m = ready_milestones[0]
            return PlanAction(
                action_id=_stable_id("action", f"milestone-{m.milestone_id[:12]}"),
                title=f"Complete milestone: {m.title}",
                reason=f"Milestone {m.title} is ready for completion",
                source_node_id=m.milestone_id,
                authority=m.authority_requirement,
                safe_to_execute=m.authority_requirement == "read_only",
                expected_result_state=f"milestone_{m.milestone_id}_completed",
            )

        # 4. No work needed
        return None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _find_blocked_nodes(
        self,
        milestones: list[PlanMilestone],
        cycles: list[list[str]],
    ) -> list[str]:
        """Find nodes that are blocked (have unresolved HARD incoming edges)."""
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)

        blocked: list[str] = []
        for nid in self.graph.topological_sort():
            if nid in cycle_nodes:
                continue
            for edge in self.graph.incoming_edges(nid):
                if edge.strength == DependencyStrength.HARD:
                    blocked.append(nid)
                    break
        return blocked

    def _compute_leverage(
        self,
        node_id: str,
        milestones: list[PlanMilestone],
        cycles: list[list[str]],
    ) -> float:
        """Compute leverage score for a node."""
        leverage = 0.0

        # Direct blocked nodes
        direct = self.graph.direct_dependents(node_id)
        leverage += len(direct) * self.LEVERAGE_DIRECT_BLOCKED

        # Transitive blocked nodes
        transitive = self.graph.transitive_dependents(node_id)
        leverage += len(transitive) * self.LEVERAGE_TRANSITIVE_BLOCKED

        # Blocked milestones
        for m in milestones:
            if node_id in m.dependent_node_ids or any(
                nid == node_id for nid in m.dependent_node_ids
            ):
                if m.state == MilestoneState.BLOCKED:
                    leverage += self.LEVERAGE_MILESTONE_BLOCKING
                elif m.state == MilestoneState.IN_PROGRESS:
                    leverage += self.LEVERAGE_MILESTONE_IN_PROGRESS

        # Authority requirement
        node = self.graph.get_node(node_id)
        if node:
            if node.source_subsystem in ("decision", "review"):
                leverage += self.LEVERAGE_AUTHORITY_REQUIRED

        # Staleness
        if node and node.freshness == "stale":
            leverage += self.LEVERAGE_STALE

        return leverage

    def _build_path(
        self,
        start_node_id: str,
        milestones: list[PlanMilestone],
        cycles: list[list[str]],
    ) -> CriticalPath | None:
        """Build a critical path starting from a blocked node."""
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)

        ordered: list[str] = []
        edges_on_path: list[PlanDependency] = []
        seen: set[str] = set()

        # Walk forward from the start node
        queue = [start_node_id]
        while queue:
            nid = queue.pop(0)
            if nid in seen or nid in cycle_nodes:
                continue
            seen.add(nid)
            ordered.append(nid)

            for edge in self.graph.outgoing_edges(nid):
                if edge.strength == DependencyStrength.HARD:
                    edges_on_path.append(edge)
                    if edge.target_id not in seen:
                        queue.append(edge.target_id)

        if not ordered:
            return None

        # Find blocked milestones
        blocked_mids: list[str] = []
        for m in milestones:
            if m.state in (MilestoneState.BLOCKED, MilestoneState.IN_PROGRESS):
                for nid in ordered:
                    if nid in m.dependent_node_ids:
                        blocked_mids.append(m.milestone_id)
                        break

        # Authority-required and safe steps
        auth_steps: list[str] = []
        safe_steps: list[str] = []
        for nid in ordered:
            node = self.graph.get_node(nid)
            if node:
                if node.source_subsystem in ("decision", "review"):
                    auth_steps.append(nid)
                else:
                    safe_steps.append(nid)

        # Explanation
        explanation_lines = [f"Critical path from {start_node_id}:"]
        for i, nid in enumerate(ordered):
            node = self.graph.get_node(nid)
            label = node.label if node else nid
            auth = " [AUTHOR]" if nid in auth_steps else ""
            explanation_lines.append(f"  {i+1}. {label}{auth}")
        if blocked_mids:
            explanation_lines.append(f"Blocked milestones: {len(blocked_mids)}")
        explanation_lines.append(f"Cumulative leverage: {sum(self._compute_leverage(nid, milestones, cycles) for nid in ordered):.1f}")

        return CriticalPath(
            path_id=_stable_id("path", start_node_id),
            ordered_node_ids=ordered,
            dependency_edges=edges_on_path,
            blocked_milestone_ids=blocked_mids,
            cumulative_leverage=0.0,  # Set by caller
            authority_required_steps=auth_steps,
            safe_steps=safe_steps,
            explanation="\n".join(explanation_lines),
            alternatives=[],
        )

    def compute_blockers(self, milestones: list[PlanMilestone]) -> list[PlanBlocker]:
        """Compute blockers from milestone state."""
        blockers: list[PlanBlocker] = []
        for m in milestones:
            if m.state == MilestoneState.BLOCKED:
                for cond in m.blocked_conditions:
                    blockers.append(PlanBlocker(
                        blocker_id=_stable_id("blocker", m.milestone_id, cond[:32]),
                        source_node_id=m.milestone_id,
                        description=f"{m.title}: {cond}",
                        severity="blocking",
                        category="milestone",
                        evidence=m.evidence,
                    ))
            elif m.state == MilestoneState.STALE:
                blockers.append(PlanBlocker(
                    blocker_id=_stable_id("blocker", m.milestone_id, "stale"),
                    source_node_id=m.milestone_id,
                    description=f"{m.title} is stale",
                    severity="warning",
                    category="staleness",
                    evidence=m.evidence,
                ))
        return blockers
