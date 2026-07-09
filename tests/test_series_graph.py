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
