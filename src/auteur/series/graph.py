from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel, Field

from auteur.series.models import DependencyEdge, SeriesIdentity


class GraphNode(BaseModel):
    id: str
    type: str
    label: str


class SeriesDependencyGraph(BaseModel):
    edge_semantics: str = "source_affects_target"
    nodes: list[GraphNode]
    edges: list[DependencyEdge]
    impact_metadata: dict[str, dict[str, list[str]]] = Field(default_factory=dict)


def build_dependency_graph(series: SeriesIdentity) -> SeriesDependencyGraph:
    nodes: list[GraphNode] = [GraphNode(id="series", type="series", label=series.title)]
    nodes.extend(
        GraphNode(id=f"book_{book.book_number}", type="book", label=book.title)
        for book in series.book_plans
    )
    nodes.extend(GraphNode(id=arc.id, type="character_arc", label=arc.character) for arc in series.character_arcs)
    nodes.extend(GraphNode(id=arc.id, type="relationship_arc", label=" / ".join(arc.participants)) for arc in series.relationship_arcs)
    nodes.extend(GraphNode(id=arc.id, type="faction_arc", label=arc.faction) for arc in series.faction_arcs)
    nodes.extend(GraphNode(id=mystery.id, type="mystery", label=mystery.question) for mystery in series.mysteries)

    known = {node.id for node in nodes}
    edges = list(series.dependency_edges)
    for book in series.book_plans:
        book_id = f"book_{book.book_number}"
        for setup in book.required_setups:
            if setup in known:
                edges.append(DependencyEdge(source=book_id, target=setup, type="sets_up"))
        for payoff in book.required_payoffs:
            if payoff in known:
                edges.append(DependencyEdge(source=payoff, target=book_id, type="pays_off"))

    dependents: dict[str, set[str]] = defaultdict(set)
    dependencies: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        dependents[edge.source].add(edge.target)
        dependencies[edge.target].add(edge.source)

    impact_metadata = {
        node.id: {
            "dependents": sorted(dependents.get(node.id, set())),
            "dependencies": sorted(dependencies.get(node.id, set())),
        }
        for node in nodes
    }
    return SeriesDependencyGraph(nodes=nodes, edges=edges, impact_metadata=impact_metadata)
