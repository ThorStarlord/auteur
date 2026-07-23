"""Immutable event storage for review sessions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auteur.review.models import (
    AcceptancePreparation,
    AcceptanceResult,
    ImpactRefreshResult,
    ReviewChoice,
    ReviewEvent,
    ReviewEventType,
    ReviewEvidenceSnapshot,
    ReviewSession,
    ReviewSessionState,
    ReviewTarget,
    _event_hash,
)


class ReviewStore:
    """Append-only event storage for review sessions.

    Layout::

        .auteur/reviews/
            sessions/       <session_id>.json  — current session state
            events/         <session_id>/      — {seq:05d}.json events
            latest/         latest.json        — pointer to active session
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.sessions_dir = self.project_root / ".auteur" / "reviews" / "sessions"
        self.events_dir = self.project_root / ".auteur" / "reviews" / "events"
        self.latest_dir = self.project_root / ".auteur" / "reviews" / "latest"

    # ------------------------------------------------------------------
    # Event writing
    # ------------------------------------------------------------------

    def append_event(self, event: ReviewEvent) -> str:
        """Append an immutable event to the session's event chain.

        Returns the event_hash.
        """
        self.events_dir.mkdir(parents=True, exist_ok=True)
        session_event_dir = self.events_dir / event.session_id
        session_event_dir.mkdir(parents=True, exist_ok=True)

        event_path = session_event_dir / f"{event.sequence:05d}.json"

        if event_path.exists():
            existing = json.loads(event_path.read_text())
            if existing.get("event_hash") != event.event_hash:
                raise ValueError(
                    f"Event conflict at sequence {event.sequence} for "
                    f"session {event.session_id}: existing hash "
                    f"{existing.get('event_hash')} != new {event.event_hash}"
                )
            return event.event_hash  # idempotent

        event_path.write_text(json.dumps({
            "event_id": event.event_id,
            "session_id": event.session_id,
            "sequence": event.sequence,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp,
            "actor": event.actor,
            "payload": event.payload,
            "source_refs": event.source_refs,
            "previous_event_hash": event.previous_event_hash,
            "event_hash": event.event_hash,
        }, indent=2, default=str))

        return event.event_hash

    def save_session(self, session: ReviewSession) -> None:
        """Save current session state snapshot."""
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        path = self.sessions_dir / f"{session.session_id}.json"

        data = {
            "session_id": session.session_id,
            "project": session.project,
            "state": session.state.value,
            "target": {
                "decision_id": session.target.decision_id,
                "target_artifact_id": session.target.target_artifact_id,
                "chapter_index": session.target.chapter_index,
                "trigger_type": session.target.trigger_type,
                "selection_reason": session.target.selection_reason,
            } if session.target else None,
            "evidence_snapshot": {
                "decision_snapshot_id": session.evidence_snapshot.decision_snapshot_id,
                "reasoning_report_ids": session.evidence_snapshot.reasoning_report_ids,
                "reconciliation_conflict_ids": session.evidence_snapshot.reconciliation_conflict_ids,
                "impact_finding_ids": session.evidence_snapshot.impact_finding_ids,
                "source_hashes": session.evidence_snapshot.source_hashes,
                "captured_at": session.evidence_snapshot.captured_at,
            } if session.evidence_snapshot else None,
            "choices": [
                {
                    "choice_id": c.choice_id,
                    "question": c.question,
                    "options": c.options,
                    "selected_option": c.selected_option,
                    "rationale": c.rationale,
                    "affected_candidates": c.affected_candidates,
                    "recorded_at": c.recorded_at,
                    "supersedes_choice_id": c.supersedes_choice_id,
                }
                for c in session.choices
            ],
            "preparation": {
                "prepared": session.preparation.prepared,
                "preparation_data": session.preparation.preparation_data,
                "blockers": session.preparation.blockers,
                "prepared_at": session.preparation.prepared_at,
                "candidate_id": session.preparation.candidate_id,
            } if session.preparation else None,
            "acceptance": {
                "accepted": session.acceptance.accepted,
                "acceptance_id": session.acceptance.acceptance_id,
                "candidate_id": session.acceptance.candidate_id,
                "error": session.acceptance.error,
                "completed_at": session.acceptance.completed_at,
            } if session.acceptance else None,
            "impact_refresh": {
                "refreshed": session.impact_refresh.refreshed,
                "new_decisions": session.impact_refresh.new_decisions,
                "stale_decisions": session.impact_refresh.stale_decisions,
                "affected_artifacts": session.impact_refresh.affected_artifacts,
                "error": session.impact_refresh.error,
                "refreshed_at": session.impact_refresh.refreshed_at,
            } if session.impact_refresh else None,
            "event_count": session.event_count,
            "last_event_hash": session.last_event_hash,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "error_info": session.error_info,
        }

        temp_path = path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(data, indent=2, default=str))
        temp_path.replace(path)

    def save_latest_pointer(self, session_id: str) -> None:
        """Update atomic latest-session pointer."""
        self.latest_dir.mkdir(parents=True, exist_ok=True)
        path = self.latest_dir / "latest.json"
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps({
            "session_id": session_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }))
        temp.replace(path)

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def load_session(self, session_id: str) -> ReviewSession | None:
        """Load session from snapshot."""
        path = self.sessions_dir / f"{session_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return self._deserialize_session(data)

    def load_events(self, session_id: str) -> list[ReviewEvent]:
        """Load all events for a session, ordered by sequence."""
        session_event_dir = self.events_dir / session_id
        if not session_event_dir.exists():
            return []
        events: list[ReviewEvent] = []
        for path in sorted(session_event_dir.glob("*.json"), key=lambda p: int(p.stem)):
            data = json.loads(path.read_text())
            events.append(ReviewEvent(
                event_id=data["event_id"],
                session_id=data["session_id"],
                sequence=data["sequence"],
                event_type=ReviewEventType(data["event_type"]),
                timestamp=data["timestamp"],
                actor=data.get("actor", "author"),
                payload=data.get("payload", {}),
                source_refs=data.get("source_refs", {}),
                previous_event_hash=data.get("previous_event_hash"),
                event_hash=data["event_hash"],
            ))
        return events

    def get_latest_session_id(self) -> str | None:
        """Get the most recent active session ID."""
        path = self.latest_dir / "latest.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return data.get("session_id")
        except (json.JSONDecodeError, OSError):
            return None

    def list_sessions(self) -> list[str]:
        """List all session IDs."""
        if not self.sessions_dir.exists():
            return []
        return sorted([p.stem for p in self.sessions_dir.glob("*.json")])

    # ------------------------------------------------------------------
    # Deserialization
    # ------------------------------------------------------------------

    def _deserialize_session(self, data: dict[str, Any]) -> ReviewSession:
        """Deserialize session from snapshot dict."""
        target_data = data.get("target")
        target = ReviewTarget(
            decision_id=target_data["decision_id"],
            target_artifact_id=target_data.get("target_artifact_id", ""),
            chapter_index=target_data.get("chapter_index", 0),
            trigger_type=target_data.get("trigger_type", ""),
            selection_reason=target_data.get("selection_reason", ""),
        ) if target_data else None

        ev_data = data.get("evidence_snapshot")
        evidence = ReviewEvidenceSnapshot(
            decision_snapshot_id=ev_data.get("decision_snapshot_id") if ev_data else None,
            reasoning_report_ids=ev_data.get("reasoning_report_ids", []) if ev_data else [],
            reconciliation_conflict_ids=ev_data.get("reconciliation_conflict_ids", []) if ev_data else [],
            impact_finding_ids=ev_data.get("impact_finding_ids", []) if ev_data else [],
            source_hashes=ev_data.get("source_hashes", {}) if ev_data else {},
            captured_at=ev_data.get("captured_at", "") if ev_data else "",
        ) if ev_data else None

        choices = [
            ReviewChoice(
                choice_id=c["choice_id"],
                question=c["question"],
                options=c.get("options"),
                selected_option=c.get("selected_option"),
                rationale=c.get("rationale", ""),
                affected_candidates=c.get("affected_candidates", []),
                recorded_at=c.get("recorded_at", ""),
                supersedes_choice_id=c.get("supersedes_choice_id"),
            )
            for c in data.get("choices", [])
        ]

        prep_data = data.get("preparation")
        preparation = AcceptancePreparation(
            prepared=prep_data["prepared"],
            preparation_data=prep_data.get("preparation_data", {}),
            blockers=prep_data.get("blockers", []),
            prepared_at=prep_data.get("prepared_at", ""),
            candidate_id=prep_data.get("candidate_id", ""),
        ) if prep_data else None

        acc_data = data.get("acceptance")
        acceptance = AcceptanceResult(
            accepted=acc_data["accepted"],
            acceptance_id=acc_data.get("acceptance_id", ""),
            candidate_id=acc_data.get("candidate_id", ""),
            error=acc_data.get("error", ""),
            completed_at=acc_data.get("completed_at", ""),
        ) if acc_data else None

        ir_data = data.get("impact_refresh")
        impact = ImpactRefreshResult(
            refreshed=ir_data["refreshed"],
            new_decisions=ir_data.get("new_decisions", []),
            stale_decisions=ir_data.get("stale_decisions", []),
            affected_artifacts=ir_data.get("affected_artifacts", []),
            error=ir_data.get("error", ""),
            refreshed_at=ir_data.get("refreshed_at", ""),
        ) if ir_data else None

        return ReviewSession(
            session_id=data["session_id"],
            project=data["project"],
            state=ReviewSessionState(data["state"]),
            target=target,
            evidence_snapshot=evidence,
            choices=choices,
            preparation=preparation,
            acceptance=acceptance,
            impact_refresh=impact,
            event_count=data.get("event_count", 0),
            last_event_hash=data.get("last_event_hash"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            error_info=data.get("error_info", ""),
        )
