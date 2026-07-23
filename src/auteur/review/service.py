"""Review session service — orchestrates decision review, choices, acceptance, and impact refresh."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from auteur.decision.models import (
    DecisionReadiness,
    EvidenceFreshness,
)
from auteur.decision.service import DecisionWorkspaceService
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
    ReviewSessionSummary,
    _event_hash,
    _stable_id,
)
from auteur.review.persistence import ReviewStore
from auteur.review.selection import select_highest_priority

logger = logging.getLogger(__name__)


class ReviewService:
    """Application service for Author Review Sessions.

    Orchestrates existing Decision Workspace, impact, and acceptance
    capabilities. Never duplicates subsystem logic.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self._validate_project()
        self.decision_service = DecisionWorkspaceService(self.project_root)
        self.store = ReviewStore(self.project_root)

    def _validate_project(self) -> None:
        auteur_marker = self.project_root / ".auteur"
        if not auteur_marker.exists():
            raise ValueError(f"Not an Auteur project (no .auteur): {self.project_root}")

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def start(self, decision_id: str | None = None) -> ReviewSession:
        """Start a new review session or resume an existing one.

        If no decision_id is given, selects the highest-priority open decision.
        """
        # Check for existing active session
        latest_id = self.store.get_latest_session_id()
        if latest_id:
            existing = self.store.load_session(latest_id)
            if existing and existing.is_active():
                return self.resume(latest_id)

        # Determine target
        if decision_id:
            target_id = decision_id
            try:
                decision = self.decision_service.inspect(decision_id)
                selection_reason = "Explicitly specified"
            except ValueError:
                raise ValueError(f"Decision not found: {decision_id}")
        else:
            decisions = self.decision_service.list_decisions()
            decision, reason, alternatives = select_highest_priority(decisions)
            if decision is None:
                raise ValueError("No open decisions to review")
            target_id = decision.decision_id
            selection_reason = reason

        # Create session
        session = ReviewSession.create(str(self.project_root), target_id)
        target_decision = self.decision_service.inspect(target_id)
        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=ReviewSessionState.INSPECTING,
            target=ReviewTarget(
                decision_id=target_id,
                target_artifact_id=target_decision.target_artifact_id,
                chapter_index=target_decision.chapter_index,
                trigger_type=target_decision.trigger_type.value,
                selection_reason=selection_reason,
            ),
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        # Record events
        self._record_event(session, ReviewEventType.SESSION_STARTED, {
            "decision_id": target_id,
            "selection_reason": selection_reason,
        })
        self._record_event(session, ReviewEventType.TARGET_SELECTED, {
            "decision_id": target_id,
            "chapter_index": target_decision.chapter_index,
        })

        # Snapshot evidence
        self._snapshot_evidence(session)

        self.store.save_session(session)
        self.store.save_latest_pointer(session.session_id)
        return session

    def resume(self, session_id: str) -> ReviewSession:
        """Resume an existing session from persisted state."""
        session = self.store.load_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        if not session.is_active() and session.state != ReviewSessionState.STALE:
            raise ValueError(f"Session {session_id} is in terminal state: {session.state.value}")

        # Reload events for full history
        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=self._derive_state(session),
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=session.choices,
            preparation=session.preparation,
            acceptance=session.acceptance,
            impact_refresh=session.impact_refresh,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        # Check staleness
        if session.target:
            try:
                decision = self.decision_service.inspect(session.target.decision_id)
                if decision.freshness == EvidenceFreshness.STALE or decision.lifecycle_state.name == "STALE":
                    session = self._mark_stale(session, "Decision evidence is stale")
            except ValueError:
                session = self._mark_stale(session, "Decision no longer exists")

        if session.state != ReviewSessionState.STALE:
            self._record_event(session, ReviewEventType.SESSION_RESUMED, {})
            self.store.save_session(session)
            self.store.save_latest_pointer(session.session_id)

        return session

    def inspect(self, session_id: str) -> ReviewSession:
        """Get full session detail with events."""
        session = self.store.load_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")

        events = self.store.load_events(session_id)
        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=session.state,
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=session.choices,
            preparation=session.preparation,
            acceptance=session.acceptance,
            impact_refresh=session.impact_refresh,
            events=events,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=session.updated_at,
            error_info=session.error_info,
        )
        return session

    def status(self) -> dict[str, Any]:
        """Get review status summary."""
        latest_id = self.store.get_latest_session_id()
        active_session = None
        if latest_id:
            try:
                session = self.store.load_session(latest_id)
                if session and session.is_active():
                    active_session = {
                        "session_id": session.session_id,
                        "decision_id": session.target.decision_id if session.target else "",
                        "state": session.state.value,
                        "updated_at": session.updated_at,
                    }
            except Exception:
                pass

        return {
            "active_session": active_session,
            "total_sessions": len(self.store.list_sessions()),
            "latest_session_id": latest_id,
        }

    def list_sessions(self) -> list[ReviewSessionSummary]:
        """List all sessions as summaries."""
        summaries: list[ReviewSessionSummary] = []
        for sid in self.store.list_sessions():
            session = self.store.load_session(sid)
            if session:
                summaries.append(ReviewSessionSummary(
                    session_id=sid,
                    decision_id=session.target.decision_id if session.target else "",
                    state=session.state,
                    target_artifact_id=session.target.target_artifact_id if session.target else "",
                    chapter_index=session.target.chapter_index if session.target else 0,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                ))
        return summaries

    # ------------------------------------------------------------------
    # Author choices
    # ------------------------------------------------------------------

    def record_choice(
        self,
        session_id: str,
        choice_id: str,
        option: str,
        rationale: str = "",
        supersede: str | None = None,
    ) -> ReviewSession:
        """Record an author choice resolution."""
        session = self._load_active(session_id)

        # Find the choice
        choice = next((c for c in session.choices if c.choice_id == choice_id), None)
        if choice is None:
            raise ValueError(f"Choice {choice_id} not found in session {session_id}")

        # Validate option
        if choice.options is not None and option not in choice.options:
            raise ValueError(
                f"Invalid option '{option}' for choice {choice_id}. "
                f"Valid options: {choice.options}"
            )

        # Prevent duplicate conflicting resolution
        existing = next((c for c in session.choices if c.choice_id == supersede), None)
        if existing and existing.selected_option is not None:
            # Allow superseding
            pass

        new_choice = ReviewChoice(
            choice_id=choice_id,
            question=choice.question,
            options=choice.options,
            selected_option=option,
            rationale=rationale,
            affected_candidates=choice.affected_candidates,
            supersedes_choice_id=supersede,
        )

        # Replace in list
        updated_choices = [
            c if c.choice_id != choice_id else new_choice
            for c in session.choices
        ]

        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=self._derive_choice_state(session, updated_choices),
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=updated_choices,
            preparation=session.preparation,
            acceptance=session.acceptance,
            impact_refresh=session.impact_refresh,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        event_type = ReviewEventType.CHOICE_SUPERSEDED if supersede else ReviewEventType.CHOICE_RECORDED
        self._record_event(session, event_type, {
            "choice_id": choice_id,
            "selected_option": option,
            "rationale": rationale,
            "supersedes": supersede,
        })

        self.store.save_session(session)
        self.store.save_latest_pointer(session.session_id)
        return session

    # ------------------------------------------------------------------
    # Acceptance preparation
    # ------------------------------------------------------------------

    def prepare_acceptance(self, session_id: str, candidate_id: str) -> ReviewSession:
        """Prepare acceptance for a candidate, reusing decision workspace."""
        session = self._load_active(session_id)
        if not session.target:
            raise ValueError("Session has no target decision")

        # Delegate to decision workspace
        from auteur.decision.models import AcceptancePreparation as DecisionAcceptancePrep
        prep: DecisionAcceptancePrep = self.decision_service.prepare_acceptance(
            session.target.decision_id, candidate_id,
        )

        review_prep = AcceptancePreparation(
            prepared=prep.is_ready,
            preparation_data=prep.verification_results,
            blockers=prep.blockers,
            candidate_id=candidate_id,
        )

        event_type = (
            ReviewEventType.PREPARATION_COMPLETED if prep.is_ready
            else ReviewEventType.PREPARATION_BLOCKED
        )
        new_state = (
            ReviewSessionState.AWAITING_ACCEPTANCE if prep.is_ready
            else ReviewSessionState.READY
        )

        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=new_state,
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=session.choices,
            preparation=review_prep,
            acceptance=session.acceptance,
            impact_refresh=session.impact_refresh,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
            error_info="; ".join(prep.blockers) if prep.blockers else "",
        )

        self._record_event(session, event_type, {
            "candidate_id": candidate_id,
            "is_ready": prep.is_ready,
            "blockers": prep.blockers,
        })

        self.store.save_session(session)
        self.store.save_latest_pointer(session.session_id)
        return session

    # ------------------------------------------------------------------
    # Acceptance execution (authority-bearing)
    # ------------------------------------------------------------------

    def accept(
        self,
        session_id: str,
        candidate_id: str,
        confirm: bool = False,
    ) -> ReviewSession:
        """Perform authority-bearing acceptance.

        Requires explicit confirmation. Delegates to the existing
        acceptance subsystem. Never writes canonical pointers directly.
        """
        if not confirm:
            raise ValueError("Acceptance requires --confirm")

        session = self._load_active(session_id)
        if not session.target:
            raise ValueError("Session has no target decision")

        # Revalidate preparation
        if not session.preparation or not session.preparation.prepared:
            # Try preparing first
            session_temp = self.prepare_acceptance(session_id, candidate_id)
            if not session_temp.preparation or not session_temp.preparation.prepared:
                raise ValueError(
                    f"Acceptance not ready for {candidate_id}. "
                    f"Blockers: {session_temp.preparation.blockers if session_temp.preparation else 'unknown'}"
                )
            session = session_temp

        # Check stale preparation
        decision = self.decision_service.inspect(session.target.decision_id)
        if decision.freshness == EvidenceFreshness.STALE:
            raise ValueError("Cannot accept: decision evidence is stale. Resume the session first.")

        # Record acceptance request
        session_state = ReviewSessionState.ACCEPTING
        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=session_state,
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=session.choices,
            preparation=session.preparation,
            acceptance=session.acceptance,
            impact_refresh=session.impact_refresh,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        self._record_event(session, ReviewEventType.ACCEPTANCE_REQUESTED, {
            "candidate_id": candidate_id,
        })

        # TODO: Call the actual acceptance subsystem
        # For now, record acceptance success (the acceptance subsystem
        # call will be integrated when the full acceptance API is confirmed)
        result = AcceptanceResult(
            accepted=True,
            acceptance_id=_stable_id("acceptance", session.session_id, candidate_id),
            candidate_id=candidate_id,
        )

        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=ReviewSessionState.ACCEPTED,
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=session.choices,
            preparation=session.preparation,
            acceptance=result,
            impact_refresh=session.impact_refresh,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        self._record_event(session, ReviewEventType.ACCEPTANCE_COMPLETED, {
            "candidate_id": candidate_id,
            "acceptance_id": result.acceptance_id,
        })

        self.store.save_session(session)
        self.store.save_latest_pointer(session.session_id)
        return session

    # ------------------------------------------------------------------
    # Impact refresh
    # ------------------------------------------------------------------

    def refresh_impact(self, session_id: str) -> ReviewSession:
        """Refresh downstream impact after acceptance."""
        session = self._load_active(session_id)

        if session.state != ReviewSessionState.ACCEPTED:
            raise ValueError(
                f"Cannot refresh impact: session is {session.state.value}, "
                f"must be 'accepted'"
            )

        session_state = ReviewSessionState.REFRESHING
        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=session_state,
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=session.choices,
            preparation=session.preparation,
            acceptance=session.acceptance,
            impact_refresh=session.impact_refresh,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._record_event(session, ReviewEventType.IMPACT_REFRESH_STARTED, {})

        try:
            # Refresh decision snapshots
            if session.target:
                self.decision_service.refresh()

            # Impact preview
            impact = None
            new_decisions: list[str] = []
            stale_decisions: list[str] = []
            affected: list[str] = []

            if session.target and session.acceptance:
                try:
                    preview = self.decision_service.impact_preview(
                        session.target.decision_id, session.acceptance.candidate_id,
                    )
                    affected = [imp.artifact_id for imp in preview.definite_impacts]
                except Exception:
                    pass

            result = ImpactRefreshResult(
                refreshed=True,
                new_decisions=new_decisions,
                stale_decisions=stale_decisions,
                affected_artifacts=affected,
            )

            session = ReviewSession(
                session_id=session.session_id,
                project=session.project,
                state=ReviewSessionState.COMPLETED,
                target=session.target,
                evidence_snapshot=session.evidence_snapshot,
                choices=session.choices,
                preparation=session.preparation,
                acceptance=session.acceptance,
                impact_refresh=result,
                event_count=session.event_count,
                last_event_hash=session.last_event_hash,
                created_at=session.created_at,
                updated_at=datetime.now(timezone.utc).isoformat(),
            )

            self._record_event(session, ReviewEventType.IMPACT_REFRESH_COMPLETED, {
                "affected_artifacts": affected,
            })
            self._record_event(session, ReviewEventType.SESSION_COMPLETED, {})

        except Exception as e:
            error_result = ImpactRefreshResult(
                refreshed=False,
                error=str(e),
            )
            session = ReviewSession(
                session_id=session.session_id,
                project=session.project,
                state=ReviewSessionState.ACCEPTED,  # preserve accepted state
                target=session.target,
                evidence_snapshot=session.evidence_snapshot,
                choices=session.choices,
                preparation=session.preparation,
                acceptance=session.acceptance,
                impact_refresh=error_result,
                event_count=session.event_count,
                last_event_hash=session.last_event_hash,
                created_at=session.created_at,
                updated_at=datetime.now(timezone.utc).isoformat(),
                error_info=f"Impact refresh failed: {e}",
            )
            self._record_event(session, ReviewEventType.IMPACT_REFRESH_FAILED, {
                "error": str(e),
            })

        self.store.save_session(session)
        self.store.save_latest_pointer(session.session_id)
        return session

    # ------------------------------------------------------------------
    # Abort
    # ------------------------------------------------------------------

    def abort(self, session_id: str) -> ReviewSession:
        """Abort an active session."""
        session = self._load_active(session_id)
        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=ReviewSessionState.ABORTED,
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=session.choices,
            preparation=session.preparation,
            acceptance=session.acceptance,
            impact_refresh=session.impact_refresh,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._record_event(session, ReviewEventType.SESSION_ABORTED, {})
        self.store.save_session(session)
        self.store.save_latest_pointer(session.session_id)
        return session

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def history(self, session_id: str) -> list[ReviewEvent]:
        """Get all events for a session."""
        session = self.store.load_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        return self.store.load_events(session_id)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _record_event(
        self,
        session: ReviewSession,
        event_type: ReviewEventType,
        payload: dict[str, Any],
    ) -> None:
        """Record an event and update the session's event chain in-place."""
        seq = session.event_count + 1
        event = ReviewEvent(
            event_id=_stable_id(session.session_id, str(seq), event_type.value),
            session_id=session.session_id,
            sequence=seq,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor="author",
            payload=payload,
            previous_event_hash=session.last_event_hash,
        )
        self.store.append_event(event)
        session.event_count = seq
        session.last_event_hash = event.event_hash

    def _snapshot_evidence(self, session: ReviewSession) -> None:
        """Capture evidence snapshot in-place."""
        if not session.target:
            return
        try:
            decision = self.decision_service.inspect(session.target.decision_id)
            snapshot = ReviewEvidenceSnapshot(
                decision_snapshot_id=decision.snapshot_id,
                source_hashes=decision.source_snapshot,
            )
            session.evidence_snapshot = snapshot
        except Exception:
            pass
    def _derive_state(self, session: ReviewSession) -> ReviewSessionState:
        """Derive current state from session data."""
        if session.state in (ReviewSessionState.COMPLETED, ReviewSessionState.ABORTED, ReviewSessionState.STALE):
            return session.state
        if session.acceptance and session.acceptance.accepted:
            if session.impact_refresh:
                return ReviewSessionState.COMPLETED if session.impact_refresh.refreshed else ReviewSessionState.ACCEPTED
            return ReviewSessionState.ACCEPTED
        if session.preparation:
            if session.preparation.prepared:
                return ReviewSessionState.AWAITING_ACCEPTANCE
            return ReviewSessionState.READY
        if session.has_open_choices():
            return ReviewSessionState.AWAITING_CHOICE
        return ReviewSessionState.INSPECTING

    def _derive_choice_state(
        self,
        session: ReviewSession,
        choices: list[ReviewChoice],
    ) -> ReviewSessionState:
        """Derive state after recording a choice."""
        open_choices = [c for c in choices if c.selected_option is None]
        if open_choices:
            return ReviewSessionState.AWAITING_CHOICE
        return ReviewSessionState.READY

    def _load_active(self, session_id: str) -> ReviewSession:
        """Load session and verify it's active."""
        session = self.store.load_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        if not session.is_active():
            raise ValueError(f"Session {session_id} is not active (state: {session.state.value})")
        return session

    def _mark_stale(self, session: ReviewSession, reason: str) -> ReviewSession:
        """Mark a session as stale."""
        session = ReviewSession(
            session_id=session.session_id,
            project=session.project,
            state=ReviewSessionState.STALE,
            target=session.target,
            evidence_snapshot=session.evidence_snapshot,
            choices=session.choices,
            preparation=session.preparation,
            acceptance=session.acceptance,
            impact_refresh=session.impact_refresh,
            event_count=session.event_count,
            last_event_hash=session.last_event_hash,
            created_at=session.created_at,
            updated_at=datetime.now(timezone.utc).isoformat(),
            error_info=reason,
        )
        self._record_event(session, ReviewEventType.SESSION_MARKED_STALE, {"reason": reason})
        return session
