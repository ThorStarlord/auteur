"""Typed models for Author Review Sessions."""

from __future__ import annotations

import enum
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ReviewSessionState(str, enum.Enum):
    OPEN = "open"
    INSPECTING = "inspecting"
    AWAITING_CHOICE = "awaiting_choice"
    READY = "ready"
    PREPARED = "prepared"
    AWAITING_ACCEPTANCE = "awaiting_acceptance"
    ACCEPTING = "accepting"
    ACCEPTED = "accepted"
    REFRESHING = "refreshing"
    COMPLETED = "completed"
    STALE = "stale"
    BLOCKED = "blocked"
    ABORTED = "aborted"


class ReviewEventType(str, enum.Enum):
    SESSION_STARTED = "session_started"
    TARGET_SELECTED = "target_selected"
    EVIDENCE_SNAPSHOTTED = "evidence_snapshottted"
    CHOICE_RECORDED = "choice_recorded"
    CHOICE_SUPERSEDED = "choice_superseded"
    PREPARATION_BLOCKED = "preparation_blocked"
    PREPARATION_COMPLETED = "preparation_completed"
    ACCEPTANCE_REQUESTED = "acceptance_requested"
    ACCEPTANCE_REFUSED = "acceptance_refused"
    ACCEPTANCE_COMPLETED = "acceptance_completed"
    IMPACT_REFRESH_STARTED = "impact_refresh_started"
    IMPACT_REFRESH_FAILED = "impact_refresh_failed"
    IMPACT_REFRESH_COMPLETED = "impact_refresh_completed"
    SESSION_MARKED_STALE = "session_marked_stale"
    SESSION_RESUMED = "session_resumed"
    SESSION_COMPLETED = "session_completed"
    SESSION_ABORTED = "session_aborted"
def _event_hash(session_id: str, sequence: int, event_type: str, prev_hash: str | None, payload: dict[str, Any]) -> str:
    raw = json.dumps({
        "session_id": session_id,
        "sequence": sequence,
        "event_type": event_type,
        "previous_event_hash": prev_hash,
        "payload": payload,
    }, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()

def _stable_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass(frozen=True)
class ReviewTarget:
    """The decision and artifact being reviewed."""
    decision_id: str
    target_artifact_id: str
    chapter_index: int = 0
    trigger_type: str = ""
    selection_reason: str = ""


@dataclass(frozen=True)
class ReviewChoice:
    """An author choice recorded during review."""
    choice_id: str
    question: str
    options: list[str] | None = None
    selected_option: str | None = None
    rationale: str = ""
    affected_candidates: list[str] = field(default_factory=list)
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    supersedes_choice_id: str | None = None


@dataclass(frozen=True)
class ReviewEvidenceSnapshot:
    """Immutable references to evidence at snapshot time."""
    decision_snapshot_id: str | None = None
    reasoning_report_ids: list[str] = field(default_factory=list)
    reconciliation_conflict_ids: list[str] = field(default_factory=list)
    impact_finding_ids: list[str] = field(default_factory=list)
    source_hashes: dict[str, str] = field(default_factory=dict)
    captured_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class ReviewEvent:
    """An immutable event in a review session's history."""
    event_id: str
    session_id: str
    sequence: int
    event_type: ReviewEventType
    timestamp: str
    actor: str = "author"
    payload: dict[str, Any] = field(default_factory=dict)
    source_refs: dict[str, Any] = field(default_factory=dict)
    previous_event_hash: str | None = None
    event_hash: str = ""

    def __post_init__(self) -> None:
        if not self.event_hash:
            object.__setattr__(self, "event_hash", _event_hash(
                self.session_id, self.sequence, self.event_type.value,
                self.previous_event_hash, self.payload,
            ))


@dataclass(frozen=True)
class AcceptancePreparation:
    """Result of acceptance preparation during a review."""
    prepared: bool
    preparation_data: dict[str, Any] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    prepared_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    candidate_id: str = ""


@dataclass(frozen=True)
class AcceptanceResult:
    """Result of an acceptance action."""
    accepted: bool
    acceptance_id: str = ""
    candidate_id: str = ""
    error: str = ""
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class ImpactRefreshResult:
    """Result of refreshing downstream impact after acceptance."""
    refreshed: bool
    new_decisions: list[str] = field(default_factory=list)
    stale_decisions: list[str] = field(default_factory=list)
    affected_artifacts: list[str] = field(default_factory=list)
    error: str = ""
    refreshed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class ReviewSessionSummary:
    """Summary for listing sessions."""
    session_id: str
    decision_id: str
    state: ReviewSessionState
    target_artifact_id: str
    chapter_index: int
    created_at: str
    updated_at: str


@dataclass
class ReviewSession:
    """Complete review session with state and history.

    event_count and last_event_hash are mutated during event recording;
    all other fields should be treated as immutable after construction.
    """
    session_id: str
    project: str
    state: ReviewSessionState
    target: ReviewTarget | None = None
    evidence_snapshot: ReviewEvidenceSnapshot | None = None
    choices: list[ReviewChoice] = field(default_factory=list)
    preparation: AcceptancePreparation | None = None
    acceptance: AcceptanceResult | None = None
    impact_refresh: ImpactRefreshResult | None = None
    events: list[ReviewEvent] = field(default_factory=list)
    event_count: int = 0
    last_event_hash: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_info: str = ""

    @staticmethod
    def create(project: str, decision_id: str) -> ReviewSession:
        """Create a new session with a deterministic ID."""
        now = datetime.now(timezone.utc).isoformat()
        session_id = _stable_id(project, decision_id, now[:19])
        return ReviewSession(
            session_id=session_id,
            project=project,
            state=ReviewSessionState.OPEN,
            target=ReviewTarget(decision_id=decision_id, target_artifact_id=""),
            created_at=now,
            updated_at=now,
        )

    def has_open_choices(self) -> bool:
        return any(c.selected_option is None for c in self.choices)

    def is_acceptance_ready(self) -> bool:
        return self.state in (ReviewSessionState.PREPARED, ReviewSessionState.AWAITING_ACCEPTANCE)

    def is_active(self) -> bool:
        return self.state not in (
            ReviewSessionState.COMPLETED,
            ReviewSessionState.STALE,
            ReviewSessionState.ABORTED,
        )
