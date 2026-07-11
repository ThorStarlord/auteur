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
