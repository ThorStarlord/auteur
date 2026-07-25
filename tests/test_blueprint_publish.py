"""Tests for blueprint publish command (v0.26.0).

Uses demo/blueprint.yaml which is a known-valid blueprint.
"""

from __future__ import annotations

from pathlib import Path

import pytest

DEMO_BLUEPRINT = Path("demo/blueprint.yaml")


class TestBlueprintPublishCLI:

    def test_publish_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["blueprint", "publish", "--help"])
        assert exc.value.code == 0

    def test_publish_missing_blueprint(self, tmp_path):
        from auteur.cli import main
        rc = main(["blueprint", "publish", str(tmp_path / "nonexistent.yaml")])
        assert rc == 1

    @pytest.mark.skipif(not DEMO_BLUEPRINT.exists(), reason="demo/blueprint.yaml not available")
    def test_publish_markdown_default(self, tmp_path):
        from auteur.cli import main
        out = tmp_path / "out.md"
        rc = main(["blueprint", "publish", str(DEMO_BLUEPRINT), "--output", str(out)])
        assert rc == 0
        assert out.exists()
        text = out.read_text(encoding="utf-8")
        assert any(kw in text for kw in ["Story Identity", "Crown", "Identity"])

    @pytest.mark.skipif(not DEMO_BLUEPRINT.exists(), reason="demo/blueprint.yaml not available")
    def test_publish_yaml_format(self, tmp_path):
        from auteur.cli import main
        out = tmp_path / "out.yaml"
        rc = main(["blueprint", "publish", str(DEMO_BLUEPRINT), "--format", "yaml", "--output", str(out)])
        assert rc == 0
        assert out.exists()
        import yaml
        data = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert "story_engine" in data

    @pytest.mark.skipif(not DEMO_BLUEPRINT.exists(), reason="demo/blueprint.yaml not available")
    def test_publish_to_dir(self, tmp_path):
        from auteur.cli import main
        out_dir = tmp_path / "out"
        out_dir.mkdir(parents=True, exist_ok=True)
        rc = main(["blueprint", "publish", str(DEMO_BLUEPRINT), "--output", str(out_dir)])
        assert rc == 0
        md = out_dir / "blueprint.md"
        assert md.exists()
        assert md.stat().st_size > 0
