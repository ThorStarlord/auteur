"""Session coordination and safe parallel-work detection for project planning."""

from __future__ import annotations

from auteur.planning.models import (
    CoordinationFinding,
    CoordinationFindingType,
    DependencyStrength,
    ParallelWorkGroup,
    PlanningNode,
    NodeType,
    _stable_id,
)
from auteur.planning.graph import PlanningGraph


class SessionCoordinator:
    """Identify session conflicts, stale sessions, and safe parallel work."""

    def __init__(self, graph: PlanningGraph) -> None:
        self.graph = graph

    def coordinate_sessions(
        self,
        sessions: list[dict],
        nodes: list[PlanningNode],
    ) -> list[CoordinationFinding]:
        """Analyze review sessions for conflicts and coordination requirements.

        Args:
            sessions: List of session summary dicts from ReviewService.
            nodes: Planning nodes for cross-referencing.

        Returns:
            List of coordination findings.
        """
        findings: list[CoordinationFinding] = []

        # Group sessions by target decision
        sessions_by_target: dict[str, list[dict]] = {}
        for s in sessions:
            target = s.get("target", {})
            if isinstance(target, dict):
                tid = target.get("decision_id", s.get("decision_id", ""))
            else:
                tid = str(target)
            sessions_by_target.setdefault(tid, []).append(s)

        # 1. Same target: check for conflicts
        for target_id, session_list in sessions_by_target.items():
            if len(session_list) < 2:
                continue

            active = [s for s in session_list if s.get("state") in ("open", "inspecting", "awaiting_choice", "ready", "prepared")]
            if len(active) >= 2:
                findings.append(CoordinationFinding(
                    finding_id=_stable_id("cf", "conflict", target_id),
                    finding_type=CoordinationFindingType.CONFLICTING,
                    session_ids=[s.get("session_id", "") for s in active],
                    description=f"Multiple active sessions for target {target_id}",
                    recommendation="Complete or abort one session before proceeding",
                    target_overlap=target_id,
                    evidence=f"{len(active)} active sessions share target",
                ))

            # Compatible sessions (only one active)
            completed = [s for s in session_list if s.get("state") == "completed"]
            if active and completed:
                latest = max(active, key=lambda x: x.get("updated_at", ""))
                findings.append(CoordinationFinding(
                    finding_id=_stable_id("cf", "compatible", target_id),
                    finding_type=CoordinationFindingType.COMPATIBLE,
                    session_ids=[latest.get("session_id", "")],
                    description=f"Session {latest.get('session_id', '')[:8]}... can proceed for {target_id}",
                    recommendation="Resume current session",
                    target_overlap=target_id,
                    evidence=f"{len(completed)} completed sessions for same target",
                ))

        # 2. Stale sessions
        for s in sessions:
            if s.get("state") == "stale":
                findings.append(CoordinationFinding(
                    finding_id=_stable_id("cf", "stale", s.get("session_id", "")),
                    finding_type=CoordinationFindingType.STALE,
                    session_ids=[s.get("session_id", "")],
                    description=f"Session {s.get('session_id', '')[:8]}... is stale",
                    recommendation="Restart session with fresh evidence",
                    evidence=f"state=stale, target={s.get('target', '')}",
                ))

        # 3. Superseded sessions
        for s in sessions:
            target = s.get("target", {})
            sid = target.get("session_id") if isinstance(target, dict) else None
            if sid and sid != s.get("session_id"):
                findings.append(CoordinationFinding(
                    finding_id=_stable_id("cf", "superseded", s.get("session_id", "")),
                    finding_type=CoordinationFindingType.SUPERSEDED,
                    session_ids=[s.get("session_id", ""), sid],
                    description=f"Session {s.get('session_id', '')[:8]}... superseded by {sid[:8]}...",
                    recommendation="Abort superseded session explicitly",
                    evidence=f"target.session_id changed from {sid[:16]}...",
                ))

        # 4. Dependency-ordered sessions
        for edge in self.graph.edges:
            if edge.dependency_type.name in ("REQUIRES_REVIEW_COMPLETION", "PREREQUISITE"):
                source_sessions = [s for s in sessions if s.get("session_id") == edge.source_id or s.get("decision_id") == edge.source_id]
                target_sessions = [s for s in sessions if s.get("session_id") == edge.target_id or s.get("decision_id") == edge.target_id]
                if source_sessions and target_sessions:
                    findings.append(CoordinationFinding(
                        finding_id=_stable_id("cf", "order", edge.edge_id),
                        finding_type=CoordinationFindingType.ORDER_REQUIRED,
                        session_ids=[edge.source_id, edge.target_id],
                        description=f"Session {edge.source_id[:8]}... should complete before {edge.target_id[:8]}...",
                        recommendation="Complete upstream session first",
                        target_overlap=edge.reason or f"{edge.dependency_type.value} dependency",
                        evidence=f"edge={edge.edge_id}, type={edge.dependency_type.value}",
                    ))

        return findings

    def detect_parallel_work(
        self,
        nodes: list[PlanningNode],
        sessions: list[dict],
    ) -> list[ParallelWorkGroup]:
        """Identify groups of work items that may proceed concurrently.

        Two actions are parallel-safe only when:
        - No hard dependency exists between them
        - No shared authority-bearing target exists
        - No active review session conflict exists
        - Neither action invalidates the other's source state
        - Both actions are independently fresh
        """
        groups: list[ParallelWorkGroup] = []
        seen: set[str] = set()

        # Group nodes that have no hard dependencies between them
        for i, n1 in enumerate(nodes):
            if n1.node_id in seen:
                continue
            if n1.node_type in (NodeType.MILESTONE,):
                continue

            group_ids = [n1.node_id]
            seen.add(n1.node_id)

            for j in range(i + 1, len(nodes)):
                n2 = nodes[j]
                if n2.node_id in seen:
                    continue
                if n2.node_type in (NodeType.MILESTONE,):
                    continue

                if self._is_parallel_safe(n1, n2, sessions):
                    group_ids.append(n2.node_id)
                    seen.add(n2.node_id)

            if len(group_ids) > 1:
                groups.append(ParallelWorkGroup(
                    group_id=_stable_id("parallel", *group_ids[:3]),
                    action_ids=group_ids,
                    shared_assumptions=["No hard dependency", "Fresh evidence", "No session conflict"],
                    conflict_checks=["Check session state before execution"],
                    authority_categories=self._categorize_authority(group_ids, nodes),
                ))

        return groups

    def _is_parallel_safe(
        self,
        n1: PlanningNode,
        n2: PlanningNode,
        sessions: list[dict],
    ) -> bool:
        """Check if two nodes can proceed in parallel."""
        # 1. No hard dependency between them
        for edge in self.graph.edges:
            if edge.strength != DependencyStrength.HARD:
                continue
            if (edge.source_id == n1.node_id and edge.target_id == n2.node_id):
                return False
            if (edge.source_id == n2.node_id and edge.target_id == n1.node_id):
                return False

        # 2. No shared authority-bearing target
        n1_target = n1.source_ref
        n2_target = n2.source_ref
        if n1_target and n2_target and n1_target == n2_target:
            if n1.node_type == NodeType.DECISION or n2.node_type == NodeType.DECISION:
                return False

        # 3. No session conflict
        n1_sessions = [s for s in sessions if s.get("decision_id") == n1.source_ref or s.get("session_id") == n1.node_id]
        n2_sessions = [s for s in sessions if s.get("decision_id") == n2.source_ref or s.get("session_id") == n2.node_id]
        for s1 in n1_sessions:
            for s2 in n2_sessions:
                if s1.get("state") in ("open", "active") and s2.get("state") in ("open", "active"):
                    target1 = s1.get("target", {})
                    target2 = s2.get("target", {})
                    if isinstance(target1, dict) and isinstance(target2, dict):
                        if target1.get("decision_id") == target2.get("decision_id"):
                            return False

        # 4. Both fresh
        if n1.freshness == "stale" or n2.freshness == "stale":
            return False

        return True

    def _categorize_authority(self, node_ids: list[str], nodes: list[PlanningNode]) -> list[str]:
        """Categorize the authority levels needed for a group of actions."""
        cats: set[str] = set()
        node_map = {n.node_id: n for n in nodes}
        for nid in node_ids:
            n = node_map.get(nid)
            if n:
                if n.node_type == NodeType.DECISION:
                    cats.add("authority_required")
                elif n.node_type == NodeType.REFRESH:
                    cats.add("read_only")
                elif n.node_type == NodeType.REVIEW_SESSION:
                    cats.add("recommendation")
        return sorted(cats)
