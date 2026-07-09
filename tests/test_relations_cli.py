from __future__ import annotations

import yaml

from auteur.cli import main


def _write_project(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "relations.yaml").write_text(
        yaml.safe_dump(
            {
                "relations": [
                    {
                        "id": "elena_marcus",
                        "from_character": "Elena",
                        "to_character": "Marcus",
                        "trust": 20,
                        "resentment": 70,
                        "dependency": 40,
                        "attraction": 10,
                        "fear": 30,
                        "obligation": 50,
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project


def test_relations_validate_succeeds_for_valid_project(tmp_path) -> None:
    project = _write_project(tmp_path)

    assert main(["relations", "validate", str(project)]) == 0


def test_relations_diagnose_reports_soft_warnings(tmp_path) -> None:
    project = _write_project(tmp_path)

    assert main(["relations", "diagnose", str(project)]) == 0
    assert (project / "relations_diagnostics.json").exists()


def test_relations_graph_writes_graph_artifact(tmp_path) -> None:
    project = _write_project(tmp_path)

    assert main(["relations", "graph", str(project)]) == 0

    graph = yaml.safe_load((project / "relations_graph.yaml").read_text(encoding="utf-8"))
    assert graph["edges"][0]["type"] == "directed_relation"


def test_relations_apply_writes_updated_relations_without_mutating_source_by_default(tmp_path) -> None:
    project = _write_project(tmp_path)
    change_path = project / "chapters" / "03" / "relation_changes.yaml"
    change_path.parent.mkdir(parents=True)
    change_path.write_text(
        yaml.safe_dump(
            {
                "chapter": 3,
                "relation_changes": [
                    {
                        "relation": "elena_marcus",
                        "trust": 8,
                        "resentment": -5,
                        "reason": "Marcus protects Elena publicly.",
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    output = project / "updated_relations.yaml"
    assert main(["relations", "apply", str(project), "3", str(change_path), "--output", str(output)]) == 0

    updated = yaml.safe_load(output.read_text(encoding="utf-8"))
    original = yaml.safe_load((project / "relations.yaml").read_text(encoding="utf-8"))
    assert updated["relations"][0]["trust"] == 28
    assert updated["relations"][0]["resentment"] == 65
    assert updated["relations"][0]["last_changed_in"] == "chapter_03"
    assert original["relations"][0]["trust"] == 20


def test_relations_apply_rejects_chapter_mismatch(tmp_path) -> None:
    project = _write_project(tmp_path)
    change_path = project / "chapters" / "04" / "relation_changes.yaml"
    change_path.parent.mkdir(parents=True)
    change_path.write_text(
        yaml.safe_dump(
            {
                "chapter": 4,
                "relation_changes": [
                    {"relation": "elena_marcus", "trust": 8, "reason": "A scene."}
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    assert main(["relations", "apply", str(project), "3", str(change_path)]) != 0
    assert yaml.safe_load((project / "relations.yaml").read_text(encoding="utf-8"))["relations"][0]["trust"] == 20


def test_relations_apply_clamps_metric_deltas(tmp_path) -> None:
    project = _write_project(tmp_path)
    change_path = project / "chapters" / "03" / "relation_changes.yaml"
    change_path.parent.mkdir(parents=True)
    change_path.write_text(
        yaml.safe_dump(
            {
                "chapter": 3,
                "relation_changes": [
                    {"relation": "elena_marcus", "trust": 200, "fear": -100, "reason": "Extreme event."}
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    assert main(["relations", "apply", str(project), "3", str(change_path)]) == 0
    updated = yaml.safe_load((project / "relations.yaml").read_text(encoding="utf-8"))
    assert updated["relations"][0]["trust"] == 100
    assert updated["relations"][0]["fear"] == 0
