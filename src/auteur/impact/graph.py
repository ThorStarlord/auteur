"""Dependency graph construction and navigation for artifact impact analysis."""

from __future__ import annotations

import json
from typing import Any

from auteur.impact.models import ArtifactRef, DependencyEdge


class DependencyGraph:
    """Directed graph of artifact dependencies.

    Nodes are artifact IDs. Edges represent source → target dependency
    (source must exist before target).
    """

    def __init__(self) -> None:
        self._nodes: dict[str, ArtifactRef] = {}
        self._edges: list[DependencyEdge] = []
        self._outgoing: dict[str, list[DependencyEdge]] = {}  # source_id → edges
        self._incoming: dict[str, list[DependencyEdge]] = {}  # target_id → edges

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_node(self, ref: ArtifactRef) -> None:
        self._nodes[ref.artifact_id] = ref

    def add_edge(self, source_id: str, target_id: str, **kwargs: Any) -> DependencyEdge:
        edge = DependencyEdge(source_id=source_id, target_id=target_id, **kwargs)
        self._edges.append(edge)
        self._outgoing.setdefault(source_id, []).append(edge)
        self._incoming.setdefault(target_id, []).append(edge)
        return edge

    def remove_node(self, artifact_id: str) -> None:
        self._nodes.pop(artifact_id, None)
        self._outgoing.pop(artifact_id, None)
        self._incoming.pop(artifact_id, None)
        self._edges = [e for e in self._edges if e.source_id != artifact_id and e.target_id != artifact_id]

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def has_node(self, artifact_id: str) -> bool:
        return artifact_id in self._nodes

    def get_node(self, artifact_id: str) -> ArtifactRef | None:
        return self._nodes.get(artifact_id)

    def nodes(self) -> dict[str, ArtifactRef]:
        return dict(self._nodes)

    def edges(self) -> list[DependencyEdge]:
        return list(self._edges)

    def direct_dependencies(self, artifact_id: str) -> list[DependencyEdge]:
        """Edges where artifact_id is the target (its dependencies)."""
        return list(self._incoming.get(artifact_id, []))

    def direct_dependents(self, artifact_id: str) -> list[DependencyEdge]:
        """Edges where artifact_id is the source (its dependents)."""
        return list(self._outgoing.get(artifact_id, []))

    def direct_dependent_ids(self, artifact_id: str) -> list[str]:
        return [e.target_id for e in self.direct_dependents(artifact_id)]

    def transitive_dependents(self, artifact_id: str) -> dict[str, list[str]]:
        """All downstream nodes reachable from artifact_id, with dependency paths."""
        result: dict[str, list[str]] = {}
        visited: set[str] = set()

        def _dfs(current: str, path: list[str]) -> None:
            for edge in self._outgoing.get(current, []):
                target = edge.target_id
                if target in visited:
                    continue
                visited.add(target)
                full_path = path + [target]
                result[target] = full_path
                _dfs(target, full_path)
            # Also walk reverse for completeness: if current appears as
            # an incoming dependency of something not directly linked
            for edge in self._incoming.get(current, []):
                pass  # incoming edges are handled by outgoing traversal

        _dfs(artifact_id, [artifact_id])
        return result

    def missing_nodes(self) -> list[str]:
        """IDs referenced as edge sources/targets that are not registered as nodes."""
        referenced: set[str] = set()
        for e in self._edges:
            referenced.add(e.source_id)
            referenced.add(e.target_id)
        return sorted(referenced - set(self._nodes.keys()))

    # ------------------------------------------------------------------
    # Cycles
    # ------------------------------------------------------------------

    def has_cycle(self) -> bool:
        try:
            self.find_cycle_members()
            return True
        except ValueError:
            return False

    def find_cycle_members(self) -> list[str]:
        """Return members of first detected cycle, or raise ValueError if acyclic."""
        WHITE, GRAY, BLACK = 0, 1, 2
        # Collect all nodes referenced in edges as well
        all_nodes = set(self._nodes.keys())
        for e in self._edges:
            all_nodes.add(e.source_id)
            all_nodes.add(e.target_id)
        color: dict[str, int] = {n: WHITE for n in all_nodes}
        parent: dict[str, str | None] = {}

        def _dfs_visit(node: str, path: list[str]) -> list[str]:
            color[node] = GRAY
            path.append(node)
            for edge in self._outgoing.get(node, []):
                neighbor = edge.target_id
                if neighbor not in color:
                    color[neighbor] = WHITE
                    parent[neighbor] = node
                if color.get(neighbor) == GRAY:
                    # Cycle found: trace from neighbor back through path
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
                if color.get(neighbor) == WHITE:
                    result = _dfs_visit(neighbor, path)
                    if result:
                        return result
            color[node] = BLACK
            path.pop()
            return []

        for node in sorted(self._nodes):
            if color.get(node) == WHITE:
                result = _dfs_visit(node, [])
                if result:
                    return result
        raise ValueError("No cycle detected")

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {aid: ref.to_dict() for aid, ref in sorted(self._nodes.items())},
            "edges": [e.to_dict() for e in sorted(self._edges, key=lambda x: (x.source_id, x.target_id))],
            "missing_nodes": self.missing_nodes(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str, sort_keys=True)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DependencyGraph:
        g = cls()
        for aid, ref_dict in d.get("nodes", {}).items():
            g.add_node(ArtifactRef.from_dict(ref_dict))
        for e_dict in d.get("edges", []):
            g.add_edge(**{k: v for k, v in e_dict.items() if k in ("source_id", "target_id", "kind", "source", "rule_id")},
                       fields=tuple(e_dict.get("fields", [])))
        return g

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def add_standard_workflow_edges(self) -> None:
        """Add edges for the standard Auteur workflow pipeline."""
        workflow_edges = [
            ("story_identity", "blueprint", "structural", "R001"),
            ("blueprint", "chapter_outline", "structural", "R002"),
            ("chapter_outline", "scene_realization", "structural", "R003"),
            ("scene_realization", "scene_expression", "structural", "R004"),
            ("scene_expression", "chapter_expression", "structural", "R005"),
            ("chapter_expression", "book_expression", "structural", "R006"),
            ("book_expression", "published_output", "structural", "R007"),
            ("chapter_outline", "reasoning_review", "structural", "R008"),
            ("scene_realization", "reasoning_review", "structural", "R008"),
            ("scene_expression", "reasoning_review", "structural", "R008"),
            ("chapter_expression", "reasoning_review", "structural", "R008"),
            ("chapter_expression", "reconciliation_result", "structural", "R010"),
            ("reconciliation_result", "accepted_chapter", "structural", ""),
            ("accepted_chapter", "book_assembly", "structural", "R009"),
            ("book_assembly", "published_output", "structural", "R011"),
        ]
        for src, tgt, kind, rule_id in workflow_edges:
            self.add_edge(src, tgt, kind=kind, rule_id=rule_id)
