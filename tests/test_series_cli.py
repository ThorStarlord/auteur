from __future__ import annotations

import json

import yaml

from auteur.cli import main
from series_fixtures import valid_trilogy_data


def _write_series(tmp_path):
    path = tmp_path / "series_identity.yaml"
    path.write_text(yaml.safe_dump(valid_trilogy_data(), sort_keys=False), encoding="utf-8")
    return path


def test_series_validate_succeeds(tmp_path):
    path = _write_series(tmp_path)

    assert main(["series", "validate", str(path)]) == 0


def test_series_validate_ignores_soft_diagnostics(tmp_path):
    data = valid_trilogy_data()
    for book in data["book_plans"]:
        book["scope"] = "city"
        book["central_engine"]["stakes"] = "The same village is threatened."
    path = tmp_path / "series_identity.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    report = tmp_path / "series_report.json"

    assert main(["series", "validate", str(path)]) == 0
    assert main(["series", "diagnose", str(path), "--output", str(report)]) == 0
    diagnostics = json.loads(report.read_text(encoding="utf-8"))["diagnostics"]
    assert any(d["rule"] == "series.scope.flat_stakes" for d in diagnostics)


def test_series_compile_writes_book_identities(tmp_path):
    path = _write_series(tmp_path)
    output = tmp_path / "series"

    assert main(["series", "compile", str(path), "--output", str(output)]) == 0
    assert (output / "book_01" / "story_identity.yaml").exists()
    assert (output / "book_02" / "story_identity.yaml").exists()
    assert (output / "book_03" / "story_identity.yaml").exists()


def test_series_diagnose_graph_and_bible_write_artifacts(tmp_path):
    path = _write_series(tmp_path)
    report = tmp_path / "series_report.json"
    graph = tmp_path / "dependency_graph.yaml"
    bible = tmp_path / "series_bible.json"

    assert main(["series", "diagnose", str(path), "--output", str(report)]) == 0
    assert main(["series", "graph", str(path), "--output", str(graph)]) == 0
    assert main(["series", "bible", str(path), "--output", str(bible)]) == 0

    assert json.loads(report.read_text(encoding="utf-8"))["diagnostics"] == []
    assert yaml.safe_load(graph.read_text(encoding="utf-8"))["nodes"]
    assert json.loads(bible.read_text(encoding="utf-8"))["mysteries"]
