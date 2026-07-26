"""Typed models for Portfolio Commitment and Coordinated Execution."""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class CommitmentState(str, enum.Enum):
    CREATED = "created"
    VALIDATING = "validating"
    READY = "ready"
    PLANNED = "planned"
    EXECUTING = "executing"
    AWAITING_AUTHOR = "awaiting_author"
    PARTIALLY_COMPLETED = "partially_completed"
    DIVERGED = "diverged"
    RECONCILING = "reconciling"
    SUPERSEDED = "superseded"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class ExecutionStepType(str, enum.Enum):
    START_REVIEW = "start_review"
    RESUME_REVIEW = "resume_review"
    INSPECT_EVIDENCE = "inspect_evidence"
    RESOLVE_AUTHOR_CHOICE = "resolve_author_choice"
    PREPARE_ACCEPTANCE = "prepare_acceptance"
    REQUEST_ACCEPTANCE = "request_acceptance"
    REFRESH_IMPACT = "refresh_impact"
    REFRESH_PLAN = "refresh_plan"
    RUN_REASONING = "run_reasoning"
    RUN_RECONCILIATION = "run_reconciliation"
    MARK_ASSIGNMENT_COMPLETE = "mark_assignment_complete"


class ExecutionStepState(str, enum.Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class AssignmentState(str, enum.Enum):
    PENDING = "pending"
    BLOCKED = "blocked"
    REVIEW_NOT_STARTED = "review_not_started"
    REVIEW_ACTIVE = "review_active"
    AWAITING_AUTHOR_CHOICE = "awaiting_author_choice"
    READY_FOR_ACCEPTANCE = "ready_for_acceptance"
    ACCEPTED_AS_COMMITTED = "accepted_as_committed"
    ACCEPTED_DIFFERENTLY = "accepted_differently"
    REJECTED = "rejected"
    STALE = "stale"
    FAILED = "failed"


class DivergenceType(str, enum.Enum):
    CANDIDATE_CHANGED = "candidate_changed"
    DIFFERENT_CANDIDATE_ACCEPTED = "different_candidate_accepted"
    DECISION_REMOVED = "decision_removed"
    REVIEW_TARGET_CHANGED = "review_target_changed"
    SOURCE_BECAME_STALE = "source_became_stale"
    ASSUMPTION_INVALIDATED = "assumption_invalidated"
    DEPENDENCY_CHANGED = "dependency_changed"
    NEW_BLOCKING_DECISION = "new_blocking_decision"
    MANUAL_PROJECT_CHANGE = "manual_project_change"


class DivergenceSeverity(str, enum.Enum):
    INFORMATIONAL = "informational"
    RECOVERABLE = "recoverable"
    BLOCKING = "blocking"
    COMMITMENT_BREAKING = "commitment_breaking"


class CommitmentEventType(str, enum.Enum):
    COMMITMENT_CREATED = "commitment_created"
    PLAN_GENERATED = "plan_generated"
    EXECUTION_STARTED = "execution_started"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    REVIEW_CREATED = "review_created"
    REVIEW_REUSED = "review_reused"
    AUTHOR_ACTION_REQUIRED = "author_action_required"
    ASSIGNMENT_ACCEPTED = "assignment_accepted"
    ASSIGNMENT_DIVERGED = "assignment_diverged"
    DIVERGENCE_DETECTED = "divergence_detected"
    RECONCILIATION_CREATED = "reconciliation_created"
    COMMITMENT_SUPERSEDED = "commitment_superseded"
    COMMITMENT_COMPLETED = "commitment_completed"
    COMMITMENT_ABORTED = "commitment_aborted"


SCHEMA_VERSION = "commitment-v1"


def _stable_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class PortfolioCommitment:
    """An immutable record of a committed portfolio direction."""
    commitment_id: str
    portfolio_scenario_id: str = ""
    assignments: dict[str, str] = field(default_factory=dict)  # decision_id → candidate_id
    assumptions: list[str] = field(default_factory=list)
    state: CommitmentState = CommitmentState.CREATED
    superseded_by: str = ""
    completion_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION
    tool_version: str = "0.13.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "commitment_id": self.commitment_id,
            "portfolio_scenario_id": self.portfolio_scenario_id,
            "assignments": self.assignments,
            "assumptions": self.assumptions,
            "state": self.state.value,
            "superseded_by": self.superseded_by,
            "completion_id": self.completion_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
        }


@dataclass(frozen=True)
class ExecutionStep:
    """A single step in a commitment execution plan."""
    step_id: str
    commitment_id: str
    decision_id: str
    candidate_id: str
    step_type: ExecutionStepType
    state: ExecutionStepState = ExecutionStepState.PENDING
    prerequisites: list[str] = field(default_factory=list)
    safe_to_execute: bool = False
    result: str = ""


@dataclass(frozen=True)
class ExecutionPlan:
    """Coordinated execution plan for a commitment."""
    plan_id: str
    commitment_id: str
    steps: list[ExecutionStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class DivergenceFinding:
    """A single divergence between committed and live state."""
    finding_id: str
    commitment_id: str
    divergence_type: DivergenceType
    severity: DivergenceSeverity
    expected: str = ""
    actual: str = ""
    decision_id: str = ""
    description: str = ""
    recommended_action: str = ""


@dataclass(frozen=True)
class CommitmentProgress:
    """Aggregate progress across all committed assignments."""
    commitment_id: str
    total: int = 0
    accepted_as_committed: int = 0
    accepted_differently: int = 0
    under_review: int = 0
    awaiting_author: int = 0
    blocked: int = 0
    stale: int = 0
    pending: int = 0
    state: str = ""


@dataclass(frozen=True)
class CommitmentEvent:
    """An immutable event in a commitment's history."""
    event_id: str
    commitment_id: str
    event_type: CommitmentEventType
    sequence: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: str = ""
