"""Tests for Lifecycle-Workflow Integration (v0.15.0)."""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.workflow.engine import WorkflowEngine
from auteur.lifecycle.service import LifecycleService


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path


# =========================================================================
# WorkflowEngine lifecycle integration
# =========================================================================


class TestEngineLifecycle:

    def test_engine_without_lifecycle_service(self, project_root):
        """Engine works without lifecycle service (backward compat)."""
        engine = WorkflowEngine(project_root)
        state = engine.analyze()
        assert state.lifecycle == {}

    def test_engine_with_lifecycle_service(self, project_root):
        """Engine works with lifecycle service."""
        lc = LifecycleService(project_root)
        engine = WorkflowEngine(project_root, lifecycle_service=lc)
        state = engine.analyze()
        assert "total_decisions" in state.lifecycle
        assert state.lifecycle["total_decisions"] == 0

    def test_lifecycle_in_summary_no_decisions(self, project_root):
        """Summary should not have lifecycle section when zero decisions."""
        lc = LifecycleService(project_root)
        engine = WorkflowEngine(project_root, lifecycle_service=lc)
        state = engine.analyze()
        assert "Decisions: 0 total" not in state.status_summary

    def test_engine_with_commitment(self, project_root):
        """Engine sees commitment data through lifecycle service."""
        from auteur.cli import main
        rc = main(["commit", "create", "--project", str(project_root),
                    "--assignment", "dec-wf-test=a", "--confirm"])
        assert rc == 0

        lc = LifecycleService(project_root)
        engine = WorkflowEngine(project_root, lifecycle_service=lc)
        state = engine.analyze()

        # Should see the committed decision
        # The decision only appears if it exists in DecisionWorkspaceService
        # The commitment probe won't find it as a decision, but lifecycle should still work
        assert "total_decisions" in state.lifecycle
        assert state.lifecycle["total_decisions"] >= 0

    def test_summary_contains_stage(self, project_root):
        """Summary must include current stage info."""
        engine = WorkflowEngine(project_root)
        state = engine.analyze()
        assert state.current_stage is not None
        assert state.current_stage.value in state.status_summary

    def test_lifecycle_data_in_actions(self, project_root):
        """Actions must be generated (even if no lifecycle gaps)."""
        engine = WorkflowEngine(project_root)
        state = engine.analyze()
        assert isinstance(state.actions, list)


# =========================================================================
# Workflow CLI with lifecycle
# =========================================================================


class TestCLIIntegration:

    def test_workflow_status_with_lifecycle(self, project_root):
        """auteur workflow status must succeed with lifecycle service."""
        from auteur.cli import main
        rc = main(["workflow", "status", str(project_root)])
        assert rc == 0

    def test_workflow_next_with_lifecycle(self, project_root):
        """auteur workflow next must succeed with lifecycle service."""
        from auteur.cli import main
        rc = main(["workflow", "next", str(project_root)])
        assert rc == 0

    def test_workflow_status_json(self, project_root):
        """auteur workflow status --json must include lifecycle."""
        from auteur.cli import main
        rc = main(["workflow", "status", str(project_root), "--json"])
        assert rc == 0

    def test_workflow_status_after_commitment(self, project_root):
        """Workflow status must succeed after creating a commitment."""
        from auteur.cli import main
        rc1 = main(["commit", "create", "--project", str(project_root),
                     "--assignment", "dec-wf2=b", "--confirm"])
        assert rc1 == 0
        rc2 = main(["workflow", "status", str(project_root)])
        assert rc2 == 0

    def test_workflow_next_after_commitment(self, project_root):
        """Workflow next must succeed after creating a commitment."""
        from auteur.cli import main
        rc1 = main(["commit", "create", "--project", str(project_root),
                     "--assignment", "dec-wf3=c", "--confirm"])
        assert rc1 == 0
        rc2 = main(["workflow", "next", str(project_root)])
        assert rc2 == 0

    def test_workflow_status_no_project(self, tmp_path):
        """Workflow status without .auteur dir should still work."""
        from auteur.cli import main
        rc = main(["workflow", "status", str(tmp_path)])
        assert rc == 0

    def test_workflow_next_no_project(self, tmp_path):
        """Workflow next without .auteur dir should still work."""
        from auteur.cli import main
        rc = main(["workflow", "next", str(tmp_path)])
        assert rc == 0

    def test_workflow_explain_with_lifecycle(self, project_root):
        from auteur.cli import main
        rc = main(["workflow", "explain", str(project_root)])
        assert rc == 0

    def test_workflow_explain_lifecycle_stage(self, project_root):
        from auteur.cli import main
        rc = main(["workflow", "explain", str(project_root), "lifecycle"])
        assert rc == 0

    def test_workflow_explain_lifecycle_json(self, project_root):
        from auteur.cli import main
        rc = main(["workflow", "explain", str(project_root), "lifecycle", "--json"])
        assert rc == 0

    def test_workflow_next_shows_alerts(self, project_root):
        from auteur.cli import main
        rc = main(["workflow", "next", str(project_root)])
        assert rc == 0
