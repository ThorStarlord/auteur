from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.relations.diagnostics import RelationDiagnostic
from auteur.relations.models import RelationChangeSet, RelationMap


def load_relation_map(project: Path) -> RelationMap:
    return RelationMap.from_yaml(project / "relations.yaml")


def load_relation_change_sets(project: Path) -> list[RelationChangeSet]:
    change_sets: list[RelationChangeSet] = []
    for path in sorted((project / "chapters").glob("*/relation_changes.yaml")):
        change_sets.append(RelationChangeSet.from_yaml(path))
    return change_sets


def write_relation_diagnostics(diagnostics: list[RelationDiagnostic], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"diagnostics": [item.model_dump(mode="json") for item in diagnostics]}, indent=2),
        encoding="utf-8",
    )
    return output


def write_relation_graph(graph: dict, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(graph, sort_keys=False), encoding="utf-8")
    return output


def write_relation_map(relation_map: RelationMap, output: Path) -> Path:
    return relation_map.to_yaml(output)

