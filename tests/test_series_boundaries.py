from __future__ import annotations

import json

import yaml

from series_fixtures import valid_trilogy_data


def test_series_handlers_return_structured_data_without_writing(tmp_path):
    from auteur.series.handlers import (
        handle_series_bible,
        handle_series_compile,
        handle_series_diagnose,
        handle_series_graph,
        handle_series_validate,
    )
    from auteur.series.models import SeriesIdentity

    series = SeriesIdentity.model_validate(valid_trilogy_data())

    validate_result = handle_series_validate(series)
    compile_result = handle_series_compile(series)
    diagnose_result = handle_series_diagnose(series)
    graph_result = handle_series_graph(series)
    bible_result = handle_series_bible(series)

    assert validate_result.is_success
    assert len(compile_result.data.identities) == 3
    assert diagnose_result.data.diagnostics == []
    assert graph_result.data.graph.nodes
    assert bible_result.data.bible["mysteries"]
    assert not list(tmp_path.iterdir())


def test_series_serializers_write_artifacts(tmp_path):
    from auteur.series.handlers import (
        handle_series_bible,
        handle_series_compile,
        handle_series_diagnose,
        handle_series_graph,
    )
    from auteur.series.models import SeriesIdentity
    from auteur.series.serializers import (
        serialize_series_bible,
        serialize_series_compile,
        serialize_series_diagnostics,
        serialize_series_graph,
    )

    series = SeriesIdentity.model_validate(valid_trilogy_data())

    written = serialize_series_compile(handle_series_compile(series), tmp_path / "series")
    report = serialize_series_diagnostics(handle_series_diagnose(series), tmp_path / "series_report.json")
    graph = serialize_series_graph(handle_series_graph(series), tmp_path / "dependency_graph.yaml")
    bible = serialize_series_bible(handle_series_bible(series), tmp_path / "series_bible.json")

    assert (tmp_path / "series" / "book_01" / "story_identity.yaml") in written
    assert json.loads(report.read_text(encoding="utf-8"))["diagnostics"] == []
    assert yaml.safe_load(graph.read_text(encoding="utf-8"))["edge_semantics"] == "source_affects_target"
    assert json.loads(bible.read_text(encoding="utf-8"))["book_context_packets"]


def test_series_formatters_produce_stable_messages():
    from auteur.series.formatters import (
        format_series_bible_success,
        format_series_compile_success,
        format_series_diagnostics_success,
        format_series_graph_success,
        format_series_validate_success,
    )

    assert "valid" in format_series_validate_success("series_identity.yaml")
    assert "compiled 3" in format_series_compile_success(3, "series")
    assert "diagnostics" in format_series_diagnostics_success("series_report.json")
    assert "graph" in format_series_graph_success("dependency_graph.yaml")
    assert "bible" in format_series_bible_success("series_bible.json")
