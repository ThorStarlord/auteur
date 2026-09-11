"""Tests for Author Review Sessions."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from auteur.review.models import (
    AcceptancePreparation,
    ReviewChoice,
    ReviewEvent,
    ReviewEventType,
    ReviewSession,
    ReviewSessionState,
    ReviewTarget,
    _event_hash,
    _stable_id,
)
from auteur.review.persistence import ReviewStore
from auteur.review.selection import select_highest_priority
from auteur.review.service import ReviewService
from auteur.decision.models import AuthorDecision, DecisionReadiness, EvidenceFreshness


@pytest.fixture
def review_project(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir()
    return tmp_path


@pytest.fixture
def review_service(review_project: Path) -> ReviewService:
    return ReviewService(review_project)


# =========================================================================
# Models
# =========================================================================


class TestReviewModels:

    def test_session_create(self):
        session = ReviewSession.create("/test/proj", "dec-001")
        assert len(session.session_id) == 16
        assert session.state == ReviewSessionState.OPEN
        assert session.target.decision_id == "dec-001"

    def test_session_has_open_choices(self):
        session = ReviewSession.create("/test", "d1")
        assert session.has_open_choices() is False

        with_choices = ReviewSession(
            session_id="s1", project="/test", state=ReviewSessionState.OPEN,
            choices=[ReviewChoice(choice_id="c1", question="Pick one?", options=["a", "b"])],
        )
        assert with_choices.has_open_choices() is True

        resolved = ReviewSession(
            session_id="s2", project="/test", state=ReviewSessionState.OPEN,
            choices=[ReviewChoice(choice_id="c1", question="Pick one?",
                                  options=["a", "b"], selected_option="a")],
        )
        assert resolved.has_open_choices() is False

    def test_session_active(self):
        assert ReviewSession.create("/test", "d1").is_active() is True
        assert ReviewSession(session_id="s1", project="/test",
                             state=ReviewSessionState.COMPLETED).is_active() is False
        assert ReviewSession(session_id="s2", project="/test",
                             state=ReviewSessionState.ABORTED).is_active() is False

    def test_stable_id_deterministic(self):
        assert _stable_id("proj", "dec-1", "ts") == _stable_id("proj", "dec-1", "ts")

    def test_event_hash_chaining(self):
        h1 = _event_hash("s1", 1, "session_started", None, {"type": "start"})
        h2 = _event_hash("s1", 2, "choice_recorded", h1, {"type": "choose"})
        h3 = _event_hash("s1", 3, "acceptance_completed", h2, {"type": "accept"})
        assert h1 != h2 and h2 != h3 and h1 != h3


# =========================================================================
# Persistence
# =========================================================================


class TestReviewPersistence:

    def test_save_and_load_session(self, review_project: Path):
        store = ReviewStore(review_project)
        session = ReviewSession.create(str(review_project), "dec-001")
        session.state = ReviewSessionState.INSPECTING
        session.target = ReviewTarget(decision_id="dec-001", target_artifact_id="t-1", chapter_index=1)
        store.save_session(session)
        store.save_latest_pointer(session.session_id)

        loaded = store.load_session(session.session_id)
        assert loaded is not None
        assert loaded.session_id == session.session_id
        assert loaded.state == ReviewSessionState.INSPECTING
        assert loaded.target.decision_id == "dec-001"

    def test_append_event(self, review_project: Path):
        store = ReviewStore(review_project)
        session = ReviewSession.create(str(review_project), "d1")
        store.save_session(session)

        event = ReviewEvent(
            event_id="ev-001", session_id=session.session_id, sequence=1,
            event_type=ReviewEventType.SESSION_STARTED, timestamp="2026-07-22T12:00:00",
        )
        store.append_event(event)
        events = store.load_events(session.session_id)
        assert len(events) == 1
        assert events[0].event_type == ReviewEventType.SESSION_STARTED

    def test_event_idempotent(self, review_project: Path):
        store = ReviewStore(review_project)
        session = ReviewSession.create(str(review_project), "d1")
        store.save_session(session)
        event = ReviewEvent(
            event_id="ev-001", session_id=session.session_id, sequence=1,
            event_type=ReviewEventType.SESSION_STARTED, timestamp="2026-07-22T12:00:00",
        )
        store.append_event(event)
        store.append_event(event)  # idempotent
        assert len(store.load_events(session.session_id)) == 1

    def test_event_conflict_rejected(self, review_project: Path):
        store = ReviewStore(review_project)
        session = ReviewSession.create(str(review_project), "d1")
        store.save_session(session)
        event1 = ReviewEvent(
            event_id="ev-001", session_id=session.session_id, sequence=1,
            event_type=ReviewEventType.SESSION_STARTED, timestamp="2026-07-22T12:00:00",
        )
        store.append_event(event1)
        event2 = ReviewEvent(
            event_id="ev-002", session_id=session.session_id, sequence=1,
            event_type=ReviewEventType.CHOICE_RECORDED, timestamp="2026-07-22T12:00:01",
        )
        with pytest.raises(ValueError, match="Event conflict"):
            store.append_event(event2)

    def test_list_sessions(self, review_project: Path):
        store = ReviewStore(review_project)
        assert store.list_sessions() == []
        store.save_session(ReviewSession.create(str(review_project), "d1"))
        store.save_session(ReviewSession.create(str(review_project), "d2"))
        assert len(store.list_sessions()) == 2


# =========================================================================
# Selection
# =========================================================================


class TestReviewSelection:

    def test_select_highest_priority_blocked(self):
        decisions = [
            AuthorDecision(decision_id="d1", project="/test", chapter_index=1, target_artifact_id="t-1",
                           readiness=DecisionReadiness.NEEDS_EVALUATION),
            AuthorDecision(decision_id="d2", project="/test", chapter_index=1, target_artifact_id="t-2",
                           readiness=DecisionReadiness.BLOCKED),
        ]
        selected, _, _ = select_highest_priority(decisions)
        assert selected.decision_id == "d2"

    def test_select_empty(self):
        selected, reason, _ = select_highest_priority([])
        assert selected is None
        assert "No open decisions" in reason

    def test_select_authority_over_acceptance(self):
        decisions = [
            AuthorDecision(decision_id="d1", project="/test", chapter_index=1, target_artifact_id="t-1",
                           readiness=DecisionReadiness.READY_FOR_ACCEPTANCE),
            AuthorDecision(decision_id="d2", project="/test", chapter_index=1, target_artifact_id="t-2",
                           readiness=DecisionReadiness.NEEDS_AUTHOR_DECISION),
        ]
        selected, _, _ = select_highest_priority(decisions)
        assert selected.decision_id == "d2"


# =========================================================================
# Service
# =========================================================================


class TestReviewService:

    def test_start_no_decisions(self, review_service: ReviewService):
        with pytest.raises(ValueError, match="No open decisions"):
            review_service.start()

    def test_inspect_nonexistent(self, review_service: ReviewService):
        with pytest.raises(ValueError, match="Session not found"):
            review_service.inspect("nonexistent")

    def test_status_no_sessions(self, review_service: ReviewService):
        status = review_service.status()
        assert status["total_sessions"] == 0
        assert status["active_session"] is None

    def test_list_empty(self, review_service: ReviewService):
        assert review_service.list_sessions() == []

    def test_abort_nonexistent(self, review_service: ReviewService):
        with pytest.raises(ValueError, match="Session not found"):
            review_service.abort("nonexistent")

    def test_start_session_compatibility_validates_candidate(self, review_project: Path, monkeypatch):
        service = ReviewService(review_project)
        expected = ReviewSession.create(str(review_project), "decision-1")
        monkeypatch.setattr(service, "start", lambda decision_id=None: expected)
        monkeypatch.setattr(
            service.decision_service,
            "inspect",
            lambda _decision_id: SimpleNamespace(candidates=[SimpleNamespace(candidate_id="candidate-1")]),
        )

        assert service.start_session("decision-1", "candidate-1") is expected
        with pytest.raises(ValueError, match="Candidate not found"):
            service.start_session("decision-1", "missing")
        with pytest.raises(ValueError, match="requires decision_id"):
            service.start_session(candidate_id="candidate-1")

    def test_accept_fails_closed_without_owning_executor(self, review_project: Path):
        service = ReviewService(review_project)
        session = ReviewSession(
            session_id="review-1",
            project=str(review_project),
            state=ReviewSessionState.AWAITING_ACCEPTANCE,
            target=ReviewTarget(decision_id="decision-1", target_artifact_id="scene-1", chapter_index=1),
            preparation=AcceptancePreparation(prepared=True, candidate_id="candidate-1"),
        )
        service.store.save_session(session)
        service.store.save_latest_pointer(session.session_id)
        service.decision_service.inspect = lambda _decision_id: SimpleNamespace(freshness=EvidenceFreshness.CURRENT)

        with pytest.raises(ValueError, match="owning acceptance workflow"):
            service.accept(session.session_id, "candidate-1", confirm=True)

        reloaded = service.store.load_session(session.session_id)
        assert reloaded is not None
        assert reloaded.state == ReviewSessionState.AWAITING_ACCEPTANCE
        assert reloaded.acceptance is None
        event_types = {event.event_type for event in service.store.load_events(session.session_id)}
        assert ReviewEventType.ACCEPTANCE_REQUESTED not in event_types
        assert ReviewEventType.ACCEPTANCE_COMPLETED not in event_types

    def test_accept_rejects_candidate_other_than_prepared(self, review_project: Path):
        service = ReviewService(review_project)
        session = ReviewSession(
            session_id="review-2",
            project=str(review_project),
            state=ReviewSessionState.AWAITING_ACCEPTANCE,
            target=ReviewTarget(decision_id="decision-1", target_artifact_id="scene-1", chapter_index=1),
            preparation=AcceptancePreparation(prepared=True, candidate_id="candidate-1"),
        )
        service.store.save_session(session)
        service.store.save_latest_pointer(session.session_id)

        with pytest.raises(ValueError, match="prepared candidate"):
            service.accept(session.session_id, "candidate-2", confirm=True)
