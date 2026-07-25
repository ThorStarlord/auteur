"""Tests for Chapter Structure Propose (v0.22.0)."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True, exist_ok=True)
    (root / ".auteur").mkdir(parents=True, exist_ok=True)
    # Note: no blueprint needed for list/help tests
    return root


class TestCLI:

    def test_structure_propose_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["structure", "propose", "--help"])
        assert exc.value.code == 0

    def test_propose_list_empty(self, project_root):
        from auteur.cli import main
        rc = main(["structure", "propose", "--list", "--project", str(project_root)])
        assert rc == 0

    def test_propose_list_json(self, project_root):
        from auteur.cli import main
        rc = main(["structure", "propose", "--list", "--project", str(project_root), "--json"])
        assert rc == 0

    def test_propose_apply_nonexistent(self, project_root):
        from auteur.cli import main
        rc = main(["structure", "propose", "--apply", "nonexistent", "--project", str(project_root)])
        assert rc == 1
