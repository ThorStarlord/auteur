"""Tests for User-defined Milestones (v0.20.0)."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestService:

    def test_add_milestone(self, project_root):
        from auteur.planning.service import PlanningService
        svc = PlanningService(project_root)
        entry = svc.add_user_milestone("Test Milestone", scope="project", description="A test")
        assert entry["title"] == "Test Milestone"
        assert entry["state"] == "not_started"

    def test_list_user_milestones(self, project_root):
        from auteur.planning.service import PlanningService
        svc = PlanningService(project_root)
        svc.add_user_milestone("M1", scope="chapter")
        milestones = svc.list_user_milestones()
        assert len(milestones) == 1

    def test_remove_milestone(self, project_root):
        from auteur.planning.service import PlanningService
        svc = PlanningService(project_root)
        entry = svc.add_user_milestone("Remove Me")
        found = svc.remove_user_milestone(entry["milestone_id"])
        assert found is True
        assert len(svc.list_user_milestones()) == 0

    def test_remove_nonexistent(self, project_root):
        from auteur.planning.service import PlanningService
        svc = PlanningService(project_root)
        found = svc.remove_user_milestone("nonexistent")
        assert found is False

    def test_duplicate_title(self, project_root):
        from auteur.planning.service import PlanningService
        svc = PlanningService(project_root)
        svc.add_user_milestone("Unique")
        with pytest.raises(ValueError, match="already exists"):
            svc.add_user_milestone("Unique")  # same title → same hash → duplicate


class TestCLI:

    def test_milestones_add(self, project_root):
        from auteur.cli import main
        rc = main(["plan", "milestones", "--add", "My Milestone",
                    "--scope", "chapter", "--description", "My desc",
                    "--project", str(project_root)])
        assert rc == 0

    def test_milestones_list(self, project_root):
        from auteur.cli import main
        rc = main(["plan", "milestones", "--project", str(project_root)])
        assert rc == 0

    def test_milestones_remove(self, project_root):
        from auteur.cli import main
        # Add first
        from auteur.planning.service import PlanningService
        svc = PlanningService(project_root)
        entry = svc.add_user_milestone("To Remove")
        # Remove via CLI
        rc = main(["plan", "milestones", "--remove", entry["milestone_id"],
                    "--project", str(project_root)])
        assert rc == 0

    def test_milestones_remove_nonexistent(self, project_root):
        from auteur.cli import main
        rc = main(["plan", "milestones", "--remove", "nonexistent-id",
                    "--project", str(project_root)])
        assert rc == 1

    def test_milestones_json(self, project_root):
        from auteur.cli import main
        rc = main(["plan", "milestones", "--project", str(project_root), "--json"])
        assert rc == 0
