"""Tests for Batch Acceptance (v0.19.0)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestService:

    def test_requires_confirm(self, project_root):
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        with pytest.raises(ValueError, match="Confirmation required"):
            svc.batch_accept("nonexistent", confirm=False)

    def test_requires_existing_commitment(self, project_root):
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        with pytest.raises(ValueError, match="Commitment not found"):
            svc.batch_accept("nonexistent", confirm=True)

    def test_skips_assignments_without_review(self, project_root):
        from auteur.cli import main
        rc = main(["commit", "create", "--project", str(project_root),
                    "--assignment", "dec-ba=a", "--confirm"])
        assert rc == 0

        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        status = svc.status()
        cid = status["latest_commitment_id"]
        results = svc.batch_accept(cid, confirm=True)
        assert len(results) == 1
        assert results[0]["status"] == "skipped"

    def test_batch_accept_uses_current_review_contract_and_reports_refusal(self, project_root, monkeypatch):
        from auteur.commitment.service import CommitmentService
        import auteur.review.service as review_service_module

        svc = CommitmentService(project_root)
        commitment = svc.create_commitment({"decision-1": "candidate-1"}, confirm=True)
        seen_kwargs = {}

        class FakeReviewService:
            def __init__(self, _project_root):
                pass

            def list_sessions(self):
                return [{"decision_id": "decision-1", "session_id": "review-1"}]

            def prepare_acceptance(self, _session_id, _candidate_id):
                return None

            def accept(self, _session_id, _candidate_id, **kwargs):
                seen_kwargs.update(kwargs)
                return SimpleNamespace(
                    acceptance=SimpleNamespace(
                        accepted=False,
                        error="Review acceptance is not wired to an owning authority workflow.",
                    )
                )

        monkeypatch.setattr(review_service_module, "ReviewService", FakeReviewService)

        results = svc.batch_accept(commitment.commitment_id, confirm=True)

        assert seen_kwargs == {"confirm": True}
        assert results == [{
            "decision_id": "decision-1",
            "candidate_id": "candidate-1",
            "status": "failed",
            "message": "Review acceptance is not wired to an owning authority workflow.",
            "session_id": "review-1",
        }]


class TestCLI:

    def test_accept_after_create(self, project_root):
        from auteur.cli import main
        rc1 = main(["commit", "create", "--project", str(project_root),
                     "--assignment", "dec-accept=a", "--confirm"])
        assert rc1 == 0
        from auteur.commitment.service import CommitmentService
        svc = CommitmentService(project_root)
        status = svc.status()
        cid = status["latest_commitment_id"]
        rc2 = main(["commit", "accept", cid, "--project", str(project_root),
                     "--confirm"])
        assert rc2 == 0  # will skip, not fail

    def test_accept_no_confirm(self, project_root):
        from auteur.cli import main
        with pytest.raises(SystemExit):
            main(["commit", "accept", "nonexistent", "--project", str(project_root)])

    def test_accept_nonexistent(self, project_root):
        from auteur.cli import main
        rc = main(["commit", "accept", "nonexistent", "--project", str(project_root),
                    "--confirm"])
        assert rc == 1

    def test_accept_returns_nonzero_when_review_refuses_authority(self, project_root, monkeypatch):
        from auteur.cli import main
        from auteur.commitment.service import CommitmentService
        import auteur.review.service as review_service_module

        svc = CommitmentService(project_root)
        commitment = svc.create_commitment({"decision-1": "candidate-1"}, confirm=True)

        class FakeReviewService:
            def __init__(self, _project_root):
                pass

            def list_sessions(self):
                return [{"decision_id": "decision-1", "session_id": "review-1"}]

            def prepare_acceptance(self, _session_id, _candidate_id):
                return None

            def accept(self, _session_id, _candidate_id, **_kwargs):
                return SimpleNamespace(
                    acceptance=SimpleNamespace(
                        accepted=False,
                        error="Review acceptance is not wired to an owning authority workflow.",
                    )
                )

        monkeypatch.setattr(review_service_module, "ReviewService", FakeReviewService)

        rc = main([
            "commit", "accept", commitment.commitment_id,
            "--project", str(project_root), "--confirm",
        ])

        assert rc == 1
