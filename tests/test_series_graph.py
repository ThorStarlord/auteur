from __future__ import annotations

from series_fixtures import valid_trilogy_data


def test_graph_contains_nodes_edges_and_impact_metadata():
    from auteur.series.graph import build_dependency_graph
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())
    graph = build_dependency_graph(series)

    node_ids = {node.id for node in graph.nodes}
    assert {"series", "book_1", "book_2", "book_3", "emperor_identity", "elena_arc"} <= node_ids
    assert any(edge.source == "emperor_identity" and edge.target == "book_3" for edge in graph.edges)
    assert "book_3" in graph.impact_metadata["emperor_identity"]["dependents"]
    assert "elena_arc" in graph.impact_metadata["emperor_identity"]["dependents"]


def test_graph_edge_semantics_source_affects_target():
    from auteur.series.graph import build_dependency_graph
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())
    graph = build_dependency_graph(series)

    assert graph.edge_semantics == "source_affects_target"
    assert "emperor_identity" in graph.impact_metadata["book_1"]["dependents"]
    assert "book_1" in graph.impact_metadata["emperor_identity"]["dependencies"]
    assert "book_3" in graph.impact_metadata["emperor_identity"]["dependents"]
    assert "emperor_identity" in graph.impact_metadata["book_3"]["dependencies"]


def test_graph_preserves_generic_setup_nodes_and_deduplicates_edges():
    from auteur.series.graph import build_dependency_graph
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    data["book_plans"][0]["required_setups"] = ["prophecy"]
    data["book_plans"][2]["required_payoffs"] = ["prophecy"]
    series = SeriesIdentity.model_validate(data)
    graph = build_dependency_graph(series)

    assert any(node.id == "prophecy" and node.type == "narrative_dependency" for node in graph.nodes)
    assert sum(edge.source == "book_1" and edge.target == "prophecy" for edge in graph.edges) == 1
    assert sum(edge.source == "prophecy" and edge.target == "book_3" for edge in graph.edges) == 1


def test_series_graph_serializer_writes_mermaid_companion(tmp_path):
    from auteur.series.handlers import SeriesGraphData, SeriesHandlerResult
    from auteur.series.serializers import serialize_series_graph
    from auteur.series.graph import build_dependency_graph
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())
    output = tmp_path / "dependency_graph.yaml"
    serialize_series_graph(
        SeriesHandlerResult.success(SeriesGraphData(graph=build_dependency_graph(series))), output
    )

    mermaid = output.with_suffix(".mmd")
    assert mermaid.exists()
    assert "graph LR" in mermaid.read_text(encoding="utf-8")


def test_graph_derives_arc_and_mystery_book_dependencies():
    from auteur.series.graph import build_dependency_graph
    from auteur.series.models import SeriesIdentity

    data = valid_trilogy_data()
    data["thematic_arcs"] = [{
        "id": "order_theme",
        "theme": "order versus freedom",
        "books": [1, 2, 3],
        "progression": {"1": "introduces", "2": "deepens", "3": "resolves"},
    }]
    series = SeriesIdentity.model_validate(data)
    graph = build_dependency_graph(series)

    assert any(node.id == "order_theme" and node.type == "thematic_arc" for node in graph.nodes)
    assert any(edge.source == "book_1" and edge.target == "order_theme" for edge in graph.edges)
    assert any(edge.source == "book_3" and edge.target == "order_theme" for edge in graph.edges)
    assert any(edge.source == "book_1" and edge.target == "emperor_identity" for edge in graph.edges)


def test_mermaid_graph_escapes_arbitrary_ids_and_labels(tmp_path):
    from auteur.series.handlers import SeriesGraphData, SeriesHandlerResult
    from auteur.series.serializers import serialize_series_graph
    from auteur.series.graph import SeriesDependencyGraph, GraphNode
    from auteur.series.models import DependencyEdge, DependencyType

    graph = SeriesDependencyGraph(
        nodes=[GraphNode(id="arc one", type="thematic_arc", label='A [danger] | "theme"')],
        edges=[DependencyEdge(source="arc one", target="arc one", type=DependencyType.TRANSFORMS)],
    )
    output = tmp_path / "graph.yaml"
    serialize_series_graph(SeriesHandlerResult.success(SeriesGraphData(graph=graph)), output)
    mermaid = output.with_suffix(".mmd").read_text(encoding="utf-8")

    assert "arc_one" in mermaid
    assert "[danger]" not in mermaid
    assert "|" not in mermaid.splitlines()[1]
