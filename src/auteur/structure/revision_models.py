"""Structural revision models — typed plan, operation, result, and event contracts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RevisionPlanState(str, Enum):
    DRAFT = "draft"
    VALIDATING = "validating"
    READY = "ready"
    STALE = "stale"
    BLOCKED = "blocked"
    AWAITING_AUTHORITY = "awaiting_authority"
    APPLYING = "applying"
    PARTIALLY_APPLIED = "partially_applied"
    APPLIED = "applied"
    RECONCILING = "reconciling"
    REEVALUATING = "reevaluating"
    COMPLETED_RESOLVED = "completed_resolved"
    COMPLETED_IMPROVED = "completed_improved"
    COMPLETED_WITH_REMAINING_FINDINGS = "completed_with_remaining_findings"
    SUPERSEDED = "superseded"
    ABORTED = "aborted"
    FAILED = "failed"


class RevisionOperationType(str, Enum):
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
    REORDER = "reorder"
    SPLIT = "split"
    MERGE = "merge"
    RELINK = "relink"
    UPDATE_DEPENDENCY = "update_dependency"
    UPDATE_MILESTONE = "update_milestone"
    UPDATE_OUTLINE_FIELD = "update_outline_field"
    APPLY_EXISTING_IMPACT_PROPOSAL = "apply_existing_impact_proposal"


class RevisionOperation(BaseModel):
    operation_id: str
    target_id: str
    target_type: str
    operation_type: RevisionOperationType
    before_expectation: dict[str, Any] = Field(default_factory=dict)
    requested_change: dict[str, Any] = Field(default_factory=dict)
    preconditions: list[str] = Field(default_factory=list)
    authority_level: str = "authority_bearing"
    predicted_consequences: list[str] = Field(default_factory=list)
    order: int = 0


class RevisionScope(BaseModel):
    target_artifact_ids: list[str] = Field(default_factory=list)
    allowed_fields: list[str] = Field(default_factory=list)
    allowed_operations: list[RevisionOperationType] = Field(default_factory=list)
    protected_artifact_ids: list[str] = Field(default_factory=list)


class StructuralRevisionPlan(BaseModel):
    """Root plan model — a semantic, content-addressed revision plan.

    Contains a stable plan ID derived from deterministic content hashes,
    all target artifacts, expected before-state hashes, ordered operations,
    and scope constraints. Never mutated after creation; recorded immutably
    via RevisionApplication and RevisionCompletion.
    """
    plan_id: str
    project: str = ""
    state: RevisionPlanState = RevisionPlanState.DRAFT
    source_ids: list[str] = Field(default_factory=list)
    target_artifact_ids: list[str] = Field(default_factory=list)
    target_hashes: dict[str, str] = Field(default_factory=dict)
    operations: list[RevisionOperation] = Field(default_factory=list)
    scope: RevisionScope = Field(default_factory=RevisionScope)
    preconditions: list[RevisionPrecondition] = Field(default_factory=list)
    created_at: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class RevisionPrecondition(BaseModel):
    target_id: str
    expected_hash: str
    actual_hash: str | None = None
    met: bool = False
    message: str = ""


class RevisionTargetResult(BaseModel):
    target_id: str
    target_type: str
    before_hash: str
    after_hash: str | None = None
    diff: dict[str, Any] = Field(default_factory=dict)
    operation_ids: list[str] = Field(default_factory=list)
    success: bool = False
    error: str | None = None


class RevisionApplication(BaseModel):
    application_id: str
    plan_id: str
    state: str = "pending"  # pending, applying, applied, failed
    target_results: list[RevisionTargetResult] = Field(default_factory=list)
    created_at: str = ""
    confirmed: bool = False


class RevisionImpactResult(BaseModel):
    changed_artifact_ids: list[str] = Field(default_factory=list)
    directly_affected: list[str] = Field(default_factory=list)
    transitively_affected: list[str] = Field(default_factory=list)
    invalidated_assumptions: list[str] = Field(default_factory=list)
    predicted_vs_observed: dict[str, Any] = Field(default_factory=dict)


class RevisionFreshnessResult(BaseModel):
    freshness_before: dict[str, str] = Field(default_factory=dict)
    freshness_after: dict[str, str] = Field(default_factory=dict)
    affected_stale: list[str] = Field(default_factory=list)
    unaffected_unchanged: list[str] = Field(default_factory=list)
    eligible_refresh: list[str] = Field(default_factory=list)


class RevisionReevaluationResult(BaseModel):
    critic_id: str = ""
    original_findings: list[dict[str, Any]] = Field(default_factory=list)
    new_findings: list[dict[str, Any]] = Field(default_factory=list)
    resolved_finding_ids: list[str] = Field(default_factory=list)
    remaining_finding_ids: list[str] = Field(default_factory=list)
    source_hash_used: str = ""


class RevisionCompletion(BaseModel):
    completion_id: str
    plan_id: str
    application_id: str
    state: RevisionPlanState
    reconciliation: RevisionImpactResult | None = None
    freshness: RevisionFreshnessResult | None = None
    reevaluation: RevisionReevaluationResult | None = None
    created_at: str = ""


class RevisionEvent(BaseModel):
    event_id: str
    plan_id: str
    event_type: str  # created, validated, applied, reconciled, reevaluated, completed, superseded, aborted
    timestamp: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


def _stable_plan_id(
    project: str,
    source_ids: list[str],
    target_ids: list[str],
    target_hashes: dict[str, str],
    operations: list[RevisionOperation],
    scope: RevisionScope,
) -> str:
    """Derive a stable semantic plan ID from content, not timestamps."""
    payload = {
        "project": project,
        "source_ids": sorted(source_ids),
        "target_ids": sorted(target_ids),
        "target_hashes": {k: v for k, v in sorted(target_hashes.items())},
        "operations": [
            {
                "operation_id": o.operation_id,
                "target_id": o.target_id,
                "operation_type": o.operation_type.value,
                "order": o.order,
            }
            for o in sorted(operations, key=lambda x: x.order)
        ],
        "scope": scope.model_dump(mode="json"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "plan_" + hashlib.sha256(raw.encode()).hexdigest()[:24]


def _stable_app_id(plan_id: str, confirmed: bool) -> str:
    raw = json.dumps({"plan_id": plan_id, "confirmed": confirmed, "ts": datetime.now(timezone.utc).isoformat()},
                     sort_keys=True, separators=(",", ":"))
    return "app_" + hashlib.sha256(raw.encode()).hexdigest()[:16]


def _stable_event_id(plan_id: str, event_type: str) -> str:
    raw = json.dumps({"plan_id": plan_id, "event_type": event_type,
                      "ts": datetime.now(timezone.utc).isoformat()},
                     sort_keys=True, separators=(",", ":"))
    return "evt_" + hashlib.sha256(raw.encode()).hexdigest()[:16]
