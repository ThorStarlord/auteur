"""Read-only Narrative Change Preview for Structure revision plans."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from auteur.impact.graph import DependencyGraph
from auteur.provenance.store import canonical_content_hash
from auteur.structure.revision_application import _resolve_target_path
from auteur.structure.revision_service import StructuralRevisionPlan


def _changed_fields(plan: StructuralRevisionPlan) -> list[str]:
    fields: set[str] = set()
    for operation in plan.operations:
        data = operation.requested_change.get("data")
        if isinstance(data, dict):
            fields.update(str(key) for key in data)
        field = operation.requested_change.get("field")
        if isinstance(field, str) and field:
            fields.add(field.split(".", 1)[0])
        if not data and not field and operation.target_type not in {"blueprint", "unknown"}:
            fields.add(operation.target_type)
    return sorted(fields)


def _currentness(plan: StructuralRevisionPlan, project_root: Path) -> tuple[str, list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    for precondition in plan.preconditions:
        target = _resolve_target_path(precondition.target_id, project_root)
        actual = canonical_content_hash(target) if target and target.is_file() else ""
        met = bool(actual) and actual == precondition.expected_hash
        checks.append(
            {
                "target_id": precondition.target_id,
                "expected_hash": precondition.expected_hash,
                "actual_hash": actual,
                "met": met,
            }
        )
    if not checks:
        return "unproven", []
    return ("current" if all(check["met"] for check in checks) else "stale"), checks


def _downstream(targets: list[str]) -> list[dict[str, Any]]:
    graph = DependencyGraph()
    graph.add_standard_workflow_edges()
    impacts: dict[str, dict[str, Any]] = {}
    for target in targets:
        for artifact_id, path in graph.transitive_dependents(target).items():
            candidate = {
                "artifact_id": artifact_id,
                "impact_kind": "definite",
                "dependency_path": path,
                "impact_reason": f"Built-in structural dependency downstream of {target}.",
            }
            prior = impacts.get(artifact_id)
            if prior is None or len(path) < len(prior["dependency_path"]):
                impacts[artifact_id] = candidate
    return sorted(
        impacts.values(),
        key=lambda item: (len(item["dependency_path"]), item["artifact_id"]),
    )


def build_revision_preview(project_root: Path, plan_id: str) -> dict[str, Any]:
    """Project a revision plan's bounded downstream consequences without writes."""
    root = project_root.resolve()
    path = root / ".auteur" / "structure" / "revision-plans" / f"{plan_id}.yaml"
    if not path.is_file():
        raise ValueError(f"Revision plan not found: {plan_id}")
    try:
        plan = StructuralRevisionPlan.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
    except Exception as exc:
        raise ValueError(f"Invalid revision plan {plan_id}: {exc}") from exc

    targets = list(dict.fromkeys(plan.target_ids or plan.scope.target_artifact_ids))
    currentness, checks = _currentness(plan, root)
    downstream = _downstream(targets)
    ready = currentness == "current" and plan.state.value == "ready"
    return {
        "plan_id": plan.plan_id,
        "plan_state": plan.state.value,
        "authority_status": "DERIVED PREVIEW / NOT APPLIED",
        "mutates_story": False,
        "currentness": currentness,
        "preconditions": checks,
        "direct_targets": targets,
        "changed_fields": _changed_fields(plan),
        "definite_downstream_impacts": downstream,
        "inferred_downstream_impacts": [],
        "impact_basis": "existing built-in structural dependency graph",
        "ready_for_authority_action": ready,
        "next_command": (
            f"auteur structure revision apply {plan.plan_id} --project . --confirm"
            if ready
            else (
                f"auteur structure revision validate {plan.plan_id} --project ."
                if currentness == "current"
                else None
            )
        ),
    }
