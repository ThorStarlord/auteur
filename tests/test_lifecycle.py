"""Tests for Decision Lifecycle Integration (v0.14.0)."""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.lifecycle.models import (
    DecisionLifecycleEntry,
    LifecycleStage,
    LifecycleSummary,
)
from auteur.lifecycle.integrator import LifecycleIntegrator
from auteur.lifecycle.service import LifecycleService


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path


# =========================================================================
# Models
# =========================================================================


class TestModels:

    def test_entry_defaults(self):
        e = DecisionLifecycleEntry(decision_id="dec-1")
        assert e.decision_id == "dec-1"
        assert e.stage == LifecycleStage.OPEN
        assert e.simulation_count == 0
        assert not e.diverged

    def test_stage_enum_order(self):
        """Stages should be in logical order."""
        stages = list(LifecycleStage)
        indices = {s: i for i, s in enumerate(stages)}
        assert indices[LifecycleStage.OPEN] < indices[LifecycleStage.SIMULATED]
        assert indices[LifecycleStage.SIMULATED] < indices[LifecycleStage.PORTFOLIO]

    def test_summary_defaults(self):
        s = LifecycleSummary()
        assert s.total_decisions == 0
        assert s.committed == 0

    def test_summary_increments(self):
        s = LifecycleSummary()
        s.diverged += 1
        assert s.diverged == 1


# =========================================================================
# Integrator — read-only probe behavior
# =========================================================================


class TestIntegrator:

    def test_empty_project(self, project_root):
        integrator = LifecycleIntegrator(project_root)
        entries = integrator.get_lifecycle_entries()
        assert entries == []

    def test_empty_summary(self, project_root):
        integrator = LifecycleIntegrator(project_root)
        summary = integrator.get_summary()
        assert summary.total_decisions == 0
        assert summary.committed == 0

    def test_probe_failures_silent(self, project_root):
        """Probe failures must not raise — logged and recovered."""
        integrator = LifecycleIntegrator(project_root)
        result = integrator._probe_decisions()
        assert isinstance(result, dict)


# =========================================================================
# Service
# =========================================================================


class TestService:

    def test_status(self, project_root):
        svc = LifecycleService(project_root)
        entries = svc.status()
        assert isinstance(entries, list)

    def test_inspect_nonexistent(self, project_root):
        svc = LifecycleService(project_root)
        result = svc.inspect("nonexistent")
        assert result is None

    def test_summary(self, project_root):
        svc = LifecycleService(project_root)
        summary = svc.summary()
        assert summary.total_decisions == 0


# =========================================================================
# CLI
# =========================================================================


class TestCLI:

    def test_lifecycle_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["lifecycle", "--help"])
        assert exc.value.code == 0

    def test_lifecycle_help_with_command(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["lifecycle", "status", "--help"])

    def test_lifecycle_status(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "status", "--project", str(project_root)])
        assert rc == 0

    def test_lifecycle_inspect(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "inspect", "dec-1", "--project", str(project_root)])
        assert rc == 1  # not found

    def test_lifecycle_summary(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "summary", "--project", str(project_root)])
        assert rc == 0

    def test_lifecycle_summary_json(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "summary", "--project", str(project_root), "--json"])
        assert rc == 0

    def test_lifecycle_no_project(self, tmp_path):
        from auteur.cli import main
        rc = main(["lifecycle", "status", "--project", str(tmp_path)])
        assert rc == 0
        rc2 = main(["lifecycle", "summary", "--project", str(tmp_path)])
        assert rc2 == 0

    def test_lifecycle_status_json(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "status", "--project", str(project_root), "--json"])
        assert rc == 0

    def test_lifecycle_inspect_not_found(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "inspect", "nonexistent",
                    "--project", str(project_root)])
        assert rc == 1

    def test_lifecycle_after_commitment(self, project_root):
        """Commitment created: lifecycle commands must not break."""
        from auteur.cli import main
        rc1 = main(["commit", "create", "--project", str(project_root),
                     "--assignment", "dec-lifecycle=a", "--confirm"])
        assert rc1 == 0
        rc2 = main(["lifecycle", "status", "--project", str(project_root)])
        assert rc2 == 0
        rc3 = main(["lifecycle", "summary", "--project", str(project_root)])
        assert rc3 == 0
