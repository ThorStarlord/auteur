"""Decision and milestone dependency graph for project planning."""

from __future__ import annotations

from typing import Any

from auteur.planning.models import (
    DependencyStrength,
    DependencyType,
    PlanDependency,
    PlanningNode,
    PlanningHorizon,
    _stable_id,
)


class PlanningGraph:
    """Directed dependency graph for project planning nodes.

    Manages nodes and edges, provides deterministic traversal, cycle detection,
    and subgraph extraction by horizon.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, PlanningNode] = {}
        self._edges: dict[str, PlanDependency] = {}
        self._outgoing: dict[str, list[str]] = {}  # source -> [edge_id, ...]
        self._incoming: dict[str, list[str]] = {}  # target -> [edge_id, ...]

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_node(self, node: PlanningNode) -> None:
        """Add a node. Replaces existing node with same ID."""
        self._nodes[node.node_id] = node
        if node.node_id not in self._outgoing:
            self._outgoing[node.node_id] = []
        if node.node_id not in self._incoming:
            self._incoming[node.node_id] = []

    def add_edge(self, edge: PlanDependency) -> None:
        """Add a dependency edge. Duplicate edges are normalized."""
        existing = self._find_duplicate(edge)
        if existing:
            return
        self._edges[edge.edge_id] = edge
        self._outgoing.setdefault(edge.source_id, []).append(edge.edge_id)
        self._incoming.setdefault(edge.target_id, []).append(edge.edge_id)

    def _find_duplicate(self, edge: PlanDependency) -> PlanDependency | None:
        """Return existing edge if one with same source, target, type exists."""
        for e in self._edges.values():
            if e.source_id == edge.source_id and e.target_id == edge.target_id and e.dependency_type == edge.dependency_type:
                return e
        return None

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all its edges."""
        self._nodes.pop(node_id, None)
        for edge_id in list(self._outgoing.get(node_id, [])):
            self._edges.pop(edge_id, None)
        for edge_id in list(self._incoming.get(node_id, [])):
            self._edges.pop(edge_id, None)
        self._outgoing.pop(node_id, None)
        self._incoming.pop(node_id, None)
        # Clean up references from other nodes
        for src in list(self._outgoing):
            self._outgoing[src] = [eid for eid in self._outgoing[src] if eid in self._edges]
        for tgt in list(self._incoming):
            self._incoming[tgt] = [eid for eid in self._incoming[tgt] if eid in self._edges]

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def nodes(self) -> list[PlanningNode]:
        """All nodes in insertion order (deterministic)."""
        return list(self._nodes.values())

    @property
    def edges(self) -> list[PlanDependency]:
        """All edges in insertion order (deterministic)."""
        return list(self._edges.values())

    def get_node(self, node_id: str) -> PlanningNode | None:
        return self._nodes.get(node_id)

    def get_edge(self, edge_id: str) -> PlanDependency | None:
        return self._edges.get(edge_id)

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def has_edge(self, source_id: str, target_id: str, dep_type: DependencyType) -> bool:
        for e in self._edges.values():
            if e.source_id == source_id and e.target_id == target_id and e.dependency_type == dep_type:
                return True
        return False

    def outgoing_edges(self, node_id: str) -> list[PlanDependency]:
        """Edges where this node is the source."""
        return [self._edges[eid] for eid in self._outgoing.get(node_id, []) if eid in self._edges]

    def incoming_edges(self, node_id: str) -> list[PlanDependency]:
        """Edges where this node is the target."""
        return [self._edges[eid] for eid in self._incoming.get(node_id, []) if eid in self._edges]
    def direct_dependencies(self, node_id: str) -> list[PlanningNode]:
        """Nodes that this node directly depends on (incoming edges)."""
        result = []
        for edge in self.incoming_edges(node_id):
            n = self._nodes.get(edge.source_id)
            if n:
                result.append(n)
        return result

    def direct_dependents(self, node_id: str) -> list[PlanningNode]:
        """Nodes that directly depend on this node (outgoing edges)."""
        result = []
        for edge in self.outgoing_edges(node_id):
            n = self._nodes.get(edge.target_id)
            if n:
                result.append(n)
        return result

    def transitive_dependencies(self, node_id: str) -> list[PlanningNode]:
        """All nodes transitively upstream (recursive incoming)."""
        seen: set[str] = set()
        result: list[PlanningNode] = []
        self._walk_transitive(node_id, self.incoming_edges, seen, result, upstream=True)
        return result

    def transitive_dependents(self, node_id: str) -> list[PlanningNode]:
        """All nodes transitively downstream (recursive outgoing)."""
        seen: set[str] = set()
        result: list[PlanningNode] = []
        self._walk_transitive(node_id, self.outgoing_edges, seen, result, upstream=False)
        return result

    def _walk_transitive(
        self,
        node_id: str,
        edge_fn,
        seen: set[str],
        result: list[PlanningNode],
        upstream: bool = True,
    ) -> None:
        if node_id in seen:
            return
        seen.add(node_id)
        for edge in edge_fn(node_id):
            nid = edge.source_id if upstream else edge.target_id
            if nid not in seen and nid in self._nodes:
                result.append(self._nodes[nid])
                self._walk_transitive(nid, edge_fn, seen, result, upstream=upstream)

    # ------------------------------------------------------------------
    # Cycle detection
    # ------------------------------------------------------------------

    def detect_cycles(self) -> list[list[str]]:
        """Return all simple cycles in the graph. Uses DFS with ancestor tracking.

        Only considers HARD edges for cycle detection. Returns list of cycles,
        where each cycle is a list of node IDs in traversal order.
        """
        visited: set[str] = set()
        stack: set[str] = set()
        cycles_list: list[list[str]] = []
        parent: dict[str, str | None] = {}

        def dfs(node_id: str) -> None:
            visited.add(node_id)
            stack.add(node_id)
            for edge in self.outgoing_edges(node_id):
                if edge.strength != DependencyStrength.HARD:
                    continue
                target = edge.target_id
                if target not in self._nodes:
                    continue
                if target not in visited:
                    parent[target] = node_id
                    dfs(target)
                elif target in stack:
                    # Reconstruct cycle: target -> ... -> node_id -> target
                    cycle = [target]
                    cur = node_id
                    while cur is not None and cur != target:
                        cycle.append(cur)
                        cur = parent.get(cur)
                    # cur == target now
                    cycle.append(target)
                    cycles_list.append(cycle)
            stack.discard(node_id)

        for nid in self._nodes:
            if nid not in visited:
                parent[nid] = None
                dfs(nid)

        # Deduplicate cycles by sorted member set
        seen: set[str] = set()
        unique: list[list[str]] = []
        for cycle in cycles_list:
            key = "-".join(sorted(cycle))
            if key not in seen:
                seen.add(key)
                unique.append(cycle)

        return unique

    # ------------------------------------------------------------------
    # Subgraph extraction
    # ------------------------------------------------------------------

    def subgraph_by_horizon(self, horizon: PlanningHorizon, chapter_index: int | None = None) -> PlanningGraph:
        """Extract a subgraph containing only nodes matching the given horizon.

        For CHAPTER and SCENE horizons, also filters by chapter_index.
        """
        sub = PlanningGraph()
        for node in self._nodes.values():
            if self._node_matches_horizon(node, horizon, chapter_index):
                sub.add_node(node)

        for edge in self._edges.values():
            if sub.has_node(edge.source_id) and sub.has_node(edge.target_id):
                sub.add_edge(edge)

        return sub

    def _node_matches_horizon(self, node: PlanningNode, horizon: PlanningHorizon, chapter_index: int | None = None) -> bool:
        if horizon == PlanningHorizon.PROJECT:
            return True
        if horizon == PlanningHorizon.BOOK:
            return True  # All nodes belong to some book
        if horizon == PlanningHorizon.CHAPTER:
            if chapter_index is not None:
                return node.chapter_index == chapter_index
            return node.chapter_index is not None
        if horizon == PlanningHorizon.SCENE:
            if chapter_index is not None:
                return node.chapter_index == chapter_index
            return node.scene_id is not None
        return True

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [_n_dict(n) for n in self._nodes.values()],
            "edges": [_e_dict(e) for e in self._edges.values()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlanningGraph:
        g = cls()
        for nd in data.get("nodes", []):
            g.add_node(PlanningNode(
                node_id=nd["node_id"],
                node_type=PlanningNode(nd.get("node_type", "decision")),
                label=nd["label"],
                chapter_index=nd.get("chapter_index"),
                book_index=nd.get("book_index"),
                act_index=nd.get("act_index"),
                scene_id=nd.get("scene_id"),
                source_subsystem=nd.get("source_subsystem", ""),
                source_ref=nd.get("source_ref", ""),
                freshness=nd.get("freshness", "current"),
                metadata=nd.get("metadata", {}),
            ))
        for ed in data.get("edges", []):
            g.add_edge(PlanDependency(
                edge_id=ed["edge_id"],
                source_id=ed["source_id"],
                target_id=ed["target_id"],
                dependency_type=DependencyType(ed["dependency_type"]),
                strength=DependencyStrength(ed.get("strength", "hard")),
                reason=ed.get("reason", ""),
            ))
        return g

    # ------------------------------------------------------------------
    # Deterministic ordering
    # ------------------------------------------------------------------

    def topological_sort(self) -> list[str]:
        """Return nodes in topological order (dependencies first).

        Falls back to insertion order for nodes in cycles. Only considers
        HARD edges for ordering.
        """
        in_degree: dict[str, int] = {}
        for nid in self._nodes:
            hard_incoming = sum(
                1 for e in self.incoming_edges(nid)
                if e.strength == DependencyStrength.HARD
            )
            in_degree[nid] = hard_incoming

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        # Sort deterministically
        queue.sort()
        result: list[str] = []

        while queue:
            nid = queue.pop(0)
            result.append(nid)
            for edge in self.outgoing_edges(nid):
                if edge.strength != DependencyStrength.HARD:
                    continue
                target = edge.target_id
                if target in in_degree:
                    in_degree[target] -= 1
                    if in_degree[target] == 0:
                        queue.append(target)
                        queue.sort()

        # Add remaining nodes (in cycles or disconnected)
        for nid in self._nodes:
            if nid not in result:
                result.append(nid)

        return result

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return len(self._edges)


def _n_dict(n: PlanningNode) -> dict[str, Any]:
    return {
        "node_id": n.node_id,
        "node_type": n.node_type.value,
        "label": n.label,
        "chapter_index": n.chapter_index,
        "source_subsystem": n.source_subsystem,
        "source_ref": n.source_ref,
        "freshness": n.freshness,
    }


def _e_dict(e: PlanDependency) -> dict[str, Any]:
    return {
        "edge_id": e.edge_id,
        "source_id": e.source_id,
        "target_id": e.target_id,
        "dependency_type": e.dependency_type.value,
        "strength": e.strength.value,
        "reason": e.reason,
    }
