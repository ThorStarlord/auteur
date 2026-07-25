"""Tests for Author Dashboard (v0.27.0)."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True, exist_ok=True)
    (root / ".auteur").mkdir(parents=True, exist_ok=True)
    return root


class TestDashboardCLI:

    def test_dashboard_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["dashboard", "--help"])
        assert exc.value.code == 0

    def test_dashboard_default(self, project_root):
        from auteur.cli import main
        rc = main(["dashboard", "--project", str(project_root)])
        assert rc == 0

    def test_dashboard_json(self, project_root):
        from auteur.cli import main
        rc = main(["dashboard", "--project", str(project_root), "--json"])
        assert rc == 0
