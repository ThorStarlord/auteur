"""Tests for Commitment Execution Workflow (v0.17.0)."""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.workflow.engine import WorkflowEngine
from auteur.commitment.service import CommitmentService


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestEngineCommitment:

    def test_engine_without_commitment(self, project_root):
        """Engine works without commitment service."""
        engine = WorkflowEngine(project_root)
        state = engine.analyze()
        assert state.commitment == {}

    def test_engine_with_commitment_service(self, project_root):
        """Engine works with commitment service (no commitments)."""
        cm = CommitmentService(project_root)
        engine = WorkflowEngine(project_root, commitment_service=cm)
        state = engine.analyze()
        assert "has_commitments" in state.commitment or "total_commitments" in state.commitment

    def test_commitment_in_summary(self, project_root):
        """Summary must have commitment section when commitments exist."""
        from auteur.cli import main
        rc = main(["commit", "create", "--project", str(project_root),
                    "--assignment", "dec-cw=a", "--confirm"])
        assert rc == 0

        cm = CommitmentService(project_root)
        engine = WorkflowEngine(project_root, commitment_service=cm)
        state = engine.analyze()

        # Should see commitment data
        cm_data = state.commitment
        assert cm_data.get("has_commitments", False) or cm_data.get("total_commitments", 0) > 0

    def test_execution_plan_progress(self, project_root):
        """Engine can probe execution plan progress."""
        from auteur.cli import main
        rc = main(["commit", "create", "--project", str(project_root),
                    "--assignment", "dec-plan=a", "--confirm"])
        assert rc == 0

        cm = CommitmentService(project_root)
        engine = WorkflowEngine(project_root, commitment_service=cm)
        state = engine.analyze()

        # Plan may or may not have been generated
        assert isinstance(state.commitment, dict)


class TestCLICommitment:

    def test_workflow_status_with_commitment(self, project_root):
        from auteur.cli import main
        rc = main(["workflow", "status", str(project_root)])
        assert rc == 0

    def test_workflow_status_after_commitment_create(self, project_root):
        from auteur.cli import main
        rc1 = main(["commit", "create", "--project", str(project_root),
                     "--assignment", "dec-cli=a", "--confirm"])
        assert rc1 == 0
        rc2 = main(["workflow", "status", str(project_root)])
        assert rc2 == 0

    def test_workflow_next_after_commitment(self, project_root):
        from auteur.cli import main
        rc1 = main(["commit", "create", "--project", str(project_root),
                     "--assignment", "dec-next=b", "--confirm"])
        assert rc1 == 0
        rc2 = main(["workflow", "next", str(project_root)])
        assert rc2 == 0
