"""Assemble project plan state from real Auteur subsystems.

Loads decisions, review sessions, impact, and provenance state to build
the planning dependency graph and derive milestones.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.planning.models import (
    DependencyEvidence,
    DependencyStrength,
    DependencyType,
    NodeType,
    PlanDependency,
    PlanningNode,
    PlanningHorizon,
    _stable_id,
)
from auteur.planning.graph import PlanningGraph
from auteur.planning.milestones import MilestoneEngine

logger = logging.getLogger(__name__)


class PlanAssembler:
    """Assemble plan state from real Auteur subsystems.

    Tolerates optional subsystems — missing subsystems produce partial
    state with clear provenance markers rather than failures.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.milestone_engine = MilestoneEngine(self.project_root)

    def assemble_graph(
        self,
        decisions: list[Any] | None = None,
        sessions: list[dict] | None = None,
        status_data: dict[str, Any] | None = None,
        horizon: PlanningHorizon = PlanningHorizon.PROJECT,
        chapter_index: int | None = None,
    ) -> tuple[PlanningGraph, list[PlanningNode], list[dict]]:
        """Assemble a dependency graph from real project state.

        Returns:
            Tuple of (graph, nodes, raw_sessions).
        """
        graph = PlanningGraph()
        nodes: list[PlanningNode] = []
        raw_sessions = sessions or []

        # Add decision nodes
        if decisions:
            for d in decisions:
                node = self._decision_to_node(d)
                graph.add_node(node)
                nodes.append(node)

        # Add review session nodes
        for s in raw_sessions:
            node = self._session_to_node(s)
            graph.add_node(node)
            nodes.append(node)

        # Add dependency edges from decision relationships
        if decisions:
            self._add_decision_edges(graph, decisions)

        # Add dependency edges from review sessions
        self._add_session_edges(graph, raw_sessions, decisions or [])

        # Add impact-derived edges
        if status_data:
            self._add_impact_edges(graph, status_data, nodes)

        # Filter by horizon if needed
        if horizon != PlanningHorizon.PROJECT:
            graph = graph.subgraph_by_horizon(horizon, chapter_index)
            nodes = graph.nodes

        return graph, nodes, raw_sessions

    def assemble(
        self,
        decisions: list[Any] | None = None,
        sessions: list[dict] | None = None,
        status_data: dict[str, Any] | None = None,
        horizon: PlanningHorizon = PlanningHorizon.PROJECT,
        chapter_index: int | None = None,
    ) -> tuple[PlanningGraph, list[PlanningNode], list[PlanDependency], list[dict]]:
        """Full assembly returning all components."""
        graph, nodes, raw_sessions = self.assemble_graph(
            decisions, sessions, status_data, horizon, chapter_index,
        )
        edges = graph.edges
        return graph, nodes, edges, raw_sessions

    # ------------------------------------------------------------------
    # Node construction
    # ------------------------------------------------------------------

    def _decision_to_node(self, decision: Any) -> PlanningNode:
        """Convert an AuthorDecision to a PlanningNode."""
        decision_id = decision.decision_id if hasattr(decision, "decision_id") else str(getattr(decision, "decision_id", ""))
        label = decision.title if hasattr(decision, "title") else decision_id
        chapter = getattr(decision, "chapter_index", None)
        freshness = "current"
        if hasattr(decision, "freshness"):
            f = getattr(decision, "freshness")
            freshness = f.value if hasattr(f, "value") else str(f)
        elif hasattr(decision, "lifecycle_state"):
            ls = getattr(decision, "lifecycle_state")
            if hasattr(ls, "value") and ls.value == "stale":
                freshness = "stale"

        readiness = getattr(decision, "readiness", None)
        if readiness:
            rv = readiness.value if hasattr(readiness, "value") else str(readiness)
        else:
            rv = "unknown"

        return PlanningNode(
            node_id=decision_id,
            node_type=NodeType.DECISION,
            label=label,
            chapter_index=chapter if isinstance(chapter, int) else None,
            source_subsystem="decision",
            source_ref=decision_id,
            freshness=freshness,
            metadata={"readiness": rv},
        )

    def _session_to_node(self, session: dict) -> PlanningNode:
        """Convert a review session dict to a PlanningNode."""
        session_id = session.get("session_id", "")
        decision_id = session.get("decision_id", "")
        target = session.get("target", {})
        if isinstance(target, dict):
            decision_id = target.get("decision_id", decision_id)
        state = session.get("state", "unknown")
        label = f"Review: {decision_id[:16] if decision_id else session_id[:16]}..."

        return PlanningNode(
            node_id=session_id,
            node_type=NodeType.REVIEW_SESSION,
            label=label,
            source_subsystem="review",
            source_ref=decision_id,
            freshness="current" if state not in ("stale", "aborted") else "stale",
            metadata={"state": state, "decision_id": decision_id},
        )

    # ------------------------------------------------------------------
    # Edge construction
    # ------------------------------------------------------------------

    def _add_decision_edges(self, graph: PlanningGraph, decisions: list[Any]) -> None:
        """Add dependency edges from decision relationships."""
        # Build a lookup of decisions by ID
        dec_map = {}
        for d in decisions:
            did = d.decision_id if hasattr(d, "decision_id") else getattr(d, "decision_id", "")
            dec_map[did] = d

        for decision in decisions:
            decision_id = decision.decision_id if hasattr(decision, "decision_id") else getattr(decision, "decision_id", "")
            chapter = getattr(decision, "chapter_index", None)

            # Evidence that references other decisions -> dependency
            evidence = getattr(decision, "evidence", [])
            for ev in evidence:
                if hasattr(ev, "source_ref") and ev.source_ref:
                    ref = ev.source_ref
                    if ref in dec_map and ref != decision_id:
                        graph.add_edge(PlanDependency(
                            edge_id=_stable_id("edge", decision_id, ref, "evidence"),
                            source_id=decision_id,
                            target_id=ref,
                            dependency_type=DependencyType.REQUIRES_EVIDENCE_FROM,
                            strength=DependencyStrength.SOFT,
                            reason=f"Decision depends on evidence from {ref}",
                            evidence=DependencyEvidence(
                                reason=f"Evidence source: {ref}",
                                source_subsystem="decision",
                                freshness="current",
                            ),
                        ))

            # Same-chapter ordering (lower chapter -> higher chapter dependency)
            # Only if decisions exist in different chapters
            for other_id, other in dec_map.items():
                if other_id == decision_id:
                    continue
                other_ch = getattr(other, "chapter_index", None)
                if chapter is not None and other_ch is not None:
                    if isinstance(chapter, int) and isinstance(other_ch, int):
                        if chapter < other_ch:
                            graph.add_edge(PlanDependency(
                                edge_id=_stable_id("edge", decision_id, other_id, "chapter"),
                                source_id=decision_id,
                                target_id=other_id,
                                dependency_type=DependencyType.REFRESH_AFTER,
                                strength=DependencyStrength.SOFT,
                                reason=f"Chapter {chapter} decisions typically precede Chapter {other_ch}",
                            ))

            # Prerequisite chain from blocked decisions
            readiness = getattr(decision, "readiness", None)
            if readiness:
                rv = readiness.value if hasattr(readiness, "value") else str(readiness)
                if rv == "blocked":
                    conflicts = getattr(decision, "conflicts", [])
                    for c in conflicts:
                        ref = getattr(c, "source_decision_id", None) or getattr(c, "related_decision_id", None)
                        if ref and ref in dec_map and ref != decision_id:
                            graph.add_edge(PlanDependency(
                                edge_id=_stable_id("edge", decision_id, ref, "blocked_by"),
                                source_id=decision_id,
                                target_id=ref,
                                dependency_type=DependencyType.PREREQUISITE,
                                strength=DependencyStrength.HARD,
                                reason=f"Decision blocked by unresolved conflict with {ref}",
                            ))

    def _add_session_edges(
        self,
        graph: PlanningGraph,
        sessions: list[dict],
        decisions: list[Any],
    ) -> None:
        """Add dependency edges from review sessions to decisions."""
        for s in sessions:
            session_id = s.get("session_id", "")
            target = s.get("target", {})
            if isinstance(target, dict):
                decision_id = target.get("decision_id", s.get("decision_id", ""))
            else:
                decision_id = s.get("decision_id", "")

            if decision_id and graph.has_node(decision_id):
                state = s.get("state", "")
                if state in ("open", "inspecting", "awaiting_choice"):
                    graph.add_edge(PlanDependency(
                        edge_id=_stable_id("edge", session_id, decision_id, "reviews"),
                        source_id=session_id,
                        target_id=decision_id,
                        dependency_type=DependencyType.REQUIRES_REVIEW_COMPLETION,
                        strength=DependencyStrength.HARD,
                        reason=f"Review session targets decision {decision_id}",
                    ))
                elif state == "completed":
                    graph.add_edge(PlanDependency(
                        edge_id=_stable_id("edge", session_id, decision_id, "reviewed"),
                        source_id=session_id,
                        target_id=decision_id,
                        dependency_type=DependencyType.REQUIRES_ACCEPTANCE_OF,
                        strength=DependencyStrength.HARD,
                        reason=f"Completed review session for {decision_id} requires acceptance",
                    ))

    def _add_impact_edges(
        self,
        graph: PlanningGraph,
        status_data: dict[str, Any],
        nodes: list[PlanningNode],
    ) -> None:
        """Add dependency edges from impact analysis."""
        impacts = status_data.get("impacts", [])
        for impact in impacts:
            source_id = impact.get("source_artifact_id", "") if isinstance(impact, dict) else ""
            target_id = impact.get("target_artifact_id", "") if isinstance(impact, dict) else ""
            if source_id and target_id and source_id != target_id:
                if graph.has_node(source_id) and graph.has_node(target_id):
                    graph.add_edge(PlanDependency(
                        edge_id=_stable_id("edge", source_id, target_id, "impact"),
                        source_id=source_id,
                        target_id=target_id,
                        dependency_type=DependencyType.INVALIDATES,
                        strength=DependencyStrength.HARD,
                        reason=f"Impact analysis: {source_id} affects {target_id}",
                        evidence=DependencyEvidence(
                            reason="Impact finding",
                            source_subsystem="impact",
                            freshness="current",
                        ),
                    ))

    # ------------------------------------------------------------------
    # Source state
    # ------------------------------------------------------------------

    def load_decisions(self, service) -> list[Any]:
        """Load decisions from DecisionWorkspaceService."""
        try:
            return service.list_decisions()
        except Exception as e:
            logger.warning(f"Could not load decisions: {e}")
            return []

    def load_sessions(self, service) -> list[dict]:
        """Load review sessions from ReviewService."""
        try:
            sessions = service.list_sessions()
            # Convert session objects to dicts if needed
            result = []
            for s in sessions:
                if hasattr(s, "to_dict"):
                    result.append(s.to_dict())
                elif isinstance(s, dict):
                    result.append(s)
                else:
                    result.append({
                        "session_id": getattr(s, "session_id", ""),
                        "decision_id": getattr(getattr(s, "target", None), "decision_id", ""),
                        "state": getattr(s, "state", ""),
                        "target": {"decision_id": getattr(getattr(s, "target", None), "decision_id", "")},
                        "updated_at": getattr(s, "updated_at", ""),
                    })
            return result
        except Exception as e:
            logger.warning(f"Could not load sessions: {e}")
            return []

    def load_status(self) -> dict[str, Any]:
        """Load project status."""
        try:
            from auteur.status import gather_status
            return gather_status(self.project_root)
        except Exception as e:
            logger.warning(f"Could not load status: {e}")
            return {}
