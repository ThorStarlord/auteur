from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from auteur.relations.models import RELATION_METRICS, RelationChangeSet, RelationMap


class RelationDiagnostic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str
    severity: str
    message: str
    evidence: list[str] = []


JUMP_THRESHOLD = 30
HIGH_INTENSITY_THRESHOLD = 80


def diagnose_relation_map(relation_map: RelationMap) -> list[RelationDiagnostic]:
    diagnostics: list[RelationDiagnostic] = []
    for relation in relation_map.relations:
        high_metrics = [
            metric for metric in RELATION_METRICS if getattr(relation, metric) >= HIGH_INTENSITY_THRESHOLD
        ]
        if high_metrics and not relation.private_truth.strip():
            diagnostics.append(
                RelationDiagnostic(
                    rule="relations.private_truth_missing",
                    severity="warning",
                    message=f"Relation {relation.id} has high-intensity metrics but no private_truth.",
                    evidence=[f"metrics: {', '.join(high_metrics)}"],
                )
            )
    return diagnostics


def diagnose_relation_changes(relation_map: RelationMap, changes: RelationChangeSet) -> list[RelationDiagnostic]:
    diagnostics: list[RelationDiagnostic] = []
    by_id = {relation.id: relation for relation in relation_map.relations}
    for change in changes.relation_changes:
        relation = by_id.get(change.relation)
        if relation is None:
            diagnostics.append(
                RelationDiagnostic(
                    rule="relations.unknown_relation",
                    severity="error",
                    message=f"Relation change references unknown relation {change.relation}.",
                    evidence=[f"chapter_{changes.chapter:02d}"],
                )
            )
            continue
        for metric, delta in change.metric_deltas().items():
            if abs(delta) > JUMP_THRESHOLD and not change.reason.strip():
                diagnostics.append(
                    RelationDiagnostic(
                        rule="relations.metric_jump_unexplained",
                        severity="warning",
                        message=f"{relation.id} {metric} changes by {delta} without a reason.",
                        evidence=[f"chapter_{changes.chapter:02d}", metric],
                    )
                )
    return diagnostics

