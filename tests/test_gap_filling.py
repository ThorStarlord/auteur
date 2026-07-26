"""Tests for Automated Gap Filling (v0.21.0)."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestFiller:

    def test_detect_no_gaps(self, project_root):
        from auteur.lifecycle.filler import LifecycleFiller
        filler = LifecycleFiller(project_root)
        gaps = filler.detect_fillable_gaps()
        assert isinstance(gaps, list)

    def test_fill_requires_confirm(self, project_root):
        from auteur.lifecycle.filler import LifecycleFiller
        filler = LifecycleFiller(project_root)
        with pytest.raises(ValueError, match="Confirmation required"):
            filler.fill_gap("simulate", confirm=False)

    def test_fill_unknown_gap(self, project_root):
        from auteur.lifecycle.filler import LifecycleFiller
        filler = LifecycleFiller(project_root)
        with pytest.raises(ValueError, match="Unknown gap type"):
            filler.fill_gap("bogus", confirm=True)


class TestService:

    def test_lifecycle_fill_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["lifecycle", "fill", "--help"])
        assert exc.value.code == 0

    def test_lifecycle_fill_detect_no_gaps(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "fill", "--project", str(project_root),
                    "--confirm"])
        assert rc == 0

    def test_lifecycle_fill_json(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "fill", "--project", str(project_root),
                    "--confirm", "--json"])
        assert rc == 0

    def test_lifecycle_fill_simulate_gap(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "fill", "--project", str(project_root),
                    "--gap", "simulate", "--confirm"])
        assert rc == 0

    def test_lifecycle_fill_portfolio_gap(self, project_root):
        from auteur.cli import main
        rc = main(["lifecycle", "fill", "--project", str(project_root),
                    "--gap", "portfolio", "--confirm"])
        assert rc == 0
