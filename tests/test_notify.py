"""Tests for Author Notification (v0.18.0)."""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.notify.models import (
    NotificationFinding,
    NotificationType,
    NotificationSeverity,
)
from auteur.notify.service import NotificationService


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path


# =========================================================================
# Models
# =========================================================================


class TestModels:

    def test_finding_defaults(self):
        f = NotificationFinding(
            finding_id="f1",
            notification_type=NotificationType.DIVERGENCE,
            severity=NotificationSeverity.WARNING,
            title="Test",
        )
        assert f.finding_id == "f1"
        assert f.subsystem == ""

    def test_finding_to_dict(self):
        f = NotificationFinding(
            finding_id="f1", notification_type=NotificationType.LIFECYCLE_GAP,
            severity=NotificationSeverity.INFO, title="gap",
        )
        d = f.to_dict()
        assert d["type"] == "lifecycle_gap"


# =========================================================================
# Scanner / Service
# =========================================================================


class TestService:

    def test_empty_project(self, project_root):
        svc = NotificationService(project_root)
        findings = svc.scan()
        assert isinstance(findings, list)

    def test_has_findings_false(self, project_root):
        svc = NotificationService(project_root)
        assert svc.has_findings() is False


# =========================================================================
# CLI
# =========================================================================


class TestCLI:

    def test_notify_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["notify", "--help"])
        assert exc.value.code == 0

    def test_notify_clean_project(self, project_root):
        from auteur.cli import main
        rc = main(["notify", "--project", str(project_root)])
        assert rc == 0

    def test_notify_json(self, project_root):
        from auteur.cli import main
        rc = main(["notify", "--project", str(project_root), "--json"])
        assert rc == 0

    def test_notify_after_commitment(self, project_root):
        from auteur.cli import main
        rc1 = main(["commit", "create", "--project", str(project_root),
                     "--assignment", "dec-not=a", "--confirm"])
        assert rc1 == 0
        rc2 = main(["notify", "--project", str(project_root)])
        assert rc2 == 0
