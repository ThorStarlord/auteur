from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from auteur.relations.diagnostics import RelationDiagnostic, diagnose_relation_changes, diagnose_relation_map
from auteur.relations.graph import build_relation_graph
from auteur.relations.models import RELATION_METRICS, RelationChangeSet, RelationMap
from auteur.relations.serializers import load_relation_change_sets, load_relation_map


@dataclass(frozen=True)
class RelationHandlerResult:
    is_success: bool
    exit_code: int = 0
    error: str | None = None
    data: object | None = None


def handle_relations_validate(project: Path) -> RelationHandlerResult:
    try:
        load_relation_map(project)
        return RelationHandlerResult(is_success=True)
    except Exception as exc:
        return RelationHandlerResult(is_success=False, exit_code=1, error=str(exc))


def handle_relations_diagnose(project: Path) -> RelationHandlerResult:
    try:
        relation_map = load_relation_map(project)
        diagnostics: list[RelationDiagnostic] = diagnose_relation_map(relation_map)
        for change_set in load_relation_change_sets(project):
            diagnostics.extend(diagnose_relation_changes(relation_map, change_set))
        return RelationHandlerResult(is_success=True, data=diagnostics)
    except Exception as exc:
        return RelationHandlerResult(is_success=False, exit_code=1, error=str(exc))


def handle_relations_graph(project: Path) -> RelationHandlerResult:
    try:
        relation_map = load_relation_map(project)
        graph = build_relation_graph(relation_map, load_relation_change_sets(project))
        return RelationHandlerResult(is_success=True, data=graph)
    except Exception as exc:
        return RelationHandlerResult(is_success=False, exit_code=1, error=str(exc))


def handle_relations_apply(project: Path, chapter: int, changes_path: Path) -> RelationHandlerResult:
    try:
        relation_map = load_relation_map(project)
        changes = RelationChangeSet.from_yaml(changes_path)
        diagnostics = diagnose_relation_changes(relation_map, changes)
        errors = [item for item in diagnostics if item.severity == "error"]
        if errors:
            return RelationHandlerResult(is_success=False, exit_code=1, error=errors[0].message, data=diagnostics)
        updated = apply_relation_changes(relation_map, changes, chapter)
        return RelationHandlerResult(is_success=True, data=updated)
    except Exception as exc:
        return RelationHandlerResult(is_success=False, exit_code=1, error=str(exc))


def apply_relation_changes(relation_map: RelationMap, changes: RelationChangeSet, chapter: int) -> RelationMap:
    updated = relation_map.model_copy(deep=True)
    by_id = {relation.id: relation for relation in updated.relations}
    for change in changes.relation_changes:
        relation = by_id[change.relation]
        for metric in RELATION_METRICS:
            delta = getattr(change, metric)
            if delta is None:
                continue
            current = getattr(relation, metric)
            setattr(relation, metric, min(100, max(0, current + delta)))
        relation.last_changed_in = f"chapter_{chapter:02d}"
    return updated

