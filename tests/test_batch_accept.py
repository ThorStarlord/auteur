"""Tests for Batch Acceptance (v0.19.0)."""

from __future__ import annotations

from pathlib import Path

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
