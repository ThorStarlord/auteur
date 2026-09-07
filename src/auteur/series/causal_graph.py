"""Deterministic causal dependency graph for narrative state changes."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CausalEdge:
    source: str
    target: str
    kind: str
    evidence_refs: tuple[str, ...] = ()


@dataclass
class CausalStoryGraph:
    edges: list[CausalEdge] = field(default_factory=list)

    def add(self, edge: CausalEdge) -> None:
        if edge not in self.edges:
            self.edges.append(edge)
            self.edges.sort(key=lambda item: (item.source, item.target, item.kind))

    def dependents(self, source: str) -> tuple[str, ...]:
        return tuple(sorted({edge.target for edge in self.edges if edge.source == source}))

    def descendants(self, source: str) -> tuple[str, ...]:
        seen: set[str] = set()
        frontier = [source]
        while frontier:
            current = frontier.pop(0)
            for target in self.dependents(current):
                if target not in seen:
                    seen.add(target)
                    frontier.append(target)
        return tuple(sorted(seen))

    def cycles(self) -> list[list[str]]:
        adjacency: dict[str, list[str]] = {}
        for edge in self.edges:
            adjacency.setdefault(edge.source, []).append(edge.target)
        found: list[list[str]] = []

        def visit(node: str, path: list[str]) -> None:
            if node in path:
                found.append(path[path.index(node):] + [node])
                return
            for target in sorted(adjacency.get(node, [])):
                visit(target, [*path, node])

        for node in sorted(adjacency):
            visit(node, [])
        return found
