"""Regression tests for fail-closed Author Review acceptance."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from auteur.decision.models import EvidenceFreshness
from auteur.review.models import (
    AcceptancePreparation,
    ReviewEventType,
    ReviewSession,
    ReviewSessionState,
    ReviewTarget,
)
from auteur.review.service import ReviewService


def _prepared_review(tmp_path, candidate_id: str = "candidate-1") -> tuple[ReviewService, ReviewSession]:
    (tmp_path / ".auteur").mkdir()
    service = ReviewService(tmp_path)
    session = ReviewSession(
        session_id="review-acceptance-boundary",
        project=str(tmp_path),
        state=ReviewSessionState.AWAITING_ACCEPTANCE,
        target=ReviewTarget(
            decision_id="decision-1",
            target_artifact_id="chapter-1",
            chapter_index=1,
        ),
        preparation=AcceptancePreparation(
            prepared=True,
            candidate_id=candidate_id,
        ),
    )
    service.store.save_session(session)
    service.store.save_latest_pointer(session.session_id)
    return service, session


def test_confirmed_review_acceptance_fails_closed_without_owning_route(tmp_path, monkeypatch):
    service, session = _prepared_review(tmp_path)
    canonical = tmp_path / "story_identity.yaml"
    canonical.write_bytes(b"title: unchanged\n")
    before = canonical.read_bytes()

    monkeypatch.setattr(
        service.decision_service,
        "inspect",
        lambda _decision_id: SimpleNamespace(freshness=EvidenceFreshness.CURRENT),
    )

    result = service.accept(session.session_id, "candidate-1", confirm=True)

    assert result.state == ReviewSessionState.AWAITING_ACCEPTANCE
    assert result.acceptance is not None
    assert result.acceptance.accepted is False
    assert result.acceptance.acceptance_id == ""
    assert "not wired to an owning authority workflow" in result.acceptance.error
    assert canonical.read_bytes() == before

    persisted = service.store.load_session(session.session_id)
    assert persisted is not None
    assert persisted.state == ReviewSessionState.AWAITING_ACCEPTANCE
    assert persisted.acceptance is not None
    assert persisted.acceptance.accepted is False

    event_types = [event.event_type for event in service.history(session.session_id)]
    assert event_types == [ReviewEventType.ACCEPTANCE_REFUSED]
    assert ReviewEventType.ACCEPTANCE_REQUESTED not in event_types
    assert ReviewEventType.ACCEPTANCE_COMPLETED not in event_types

    with pytest.raises(ValueError, match="must be 'accepted'"):
        service.refresh_impact(session.session_id)


def test_review_accept_rejects_candidate_different_from_prepared_candidate(tmp_path):
    service, session = _prepared_review(tmp_path, candidate_id="candidate-1")

    with pytest.raises(ValueError, match="does not match requested candidate"):
        service.accept(session.session_id, "candidate-2", confirm=True)

    persisted = service.store.load_session(session.session_id)
    assert persisted is not None
    assert persisted.state == ReviewSessionState.AWAITING_ACCEPTANCE
    assert persisted.acceptance is None
    assert service.history(session.session_id) == []


def test_review_accept_still_requires_explicit_confirmation(tmp_path):
    service, session = _prepared_review(tmp_path)

    with pytest.raises(ValueError, match="requires --confirm"):
        service.accept(session.session_id, "candidate-1", confirm=False)

    persisted = service.store.load_session(session.session_id)
    assert persisted is not None
    assert persisted.state == ReviewSessionState.AWAITING_ACCEPTANCE
    assert persisted.acceptance is None
    assert service.history(session.session_id) == []
