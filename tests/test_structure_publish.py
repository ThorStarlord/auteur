"""Tests for structure publish command (v0.31.0)."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True, exist_ok=True)
    (root / ".auteur").mkdir(parents=True, exist_ok=True)
    return root


@pytest.fixture
def with_outlines(project_root: Path) -> Path:
    """Project with chapter outlines."""
    import yaml
    ch1 = project_root / "chapters" / "ch_001"
    ch1.mkdir(parents=True, exist_ok=True)
    (ch1 / "outline.yaml").write_text(yaml.safe_dump({
        "chapter_index": 1,
        "chapter_summary": "The hero begins their journey.",
        "scenes": [
            {"scene_id": "s1", "pov_character": "Hero", "location": "village",
             "summary": "Hero wakes up.", "estimated_tension": 3, "emotional_tone": "calm"},
        ],
        "arc_pushes": ["establish_status_quo"],
        "thematic_reinforcement": "courage",
    }), encoding="utf-8")
    ch2 = project_root / "chapters" / "ch_002"
    ch2.mkdir(parents=True, exist_ok=True)
    (ch2 / "outline.yaml").write_text(yaml.safe_dump({
        "chapter_index": 2,
        "chapter_summary": "The call to adventure.",
        "scenes": [
            {"scene_id": "s2", "pov_character": "Hero", "location": "crossroads",
             "summary": "A stranger appears.", "estimated_tension": 5, "emotional_tone": "unease"},
        ],
        "arc_pushes": ["inciting_incident"],
    }), encoding="utf-8")
    return project_root


class TestStructurePublishCLI:

    def test_publish_no_outlines(self, project_root):
        from auteur.cli import main
        rc = main(["structure", "publish", "--project", str(project_root)])
        assert rc == 1

    def test_publish_markdown_default(self, with_outlines):
        from auteur.cli import main
        rc = main(["structure", "publish", "--project", str(with_outlines)])
        assert rc == 0
        md = with_outlines / "published" / "chapter-structure" / "structure.md"
        assert md.exists()
        text = md.read_text(encoding="utf-8")
        assert "Chapter Structure" in text
        assert "Chapter 1" in text or "ch_001" in text
        assert "Hero" in text

    def test_publish_yaml_format(self, with_outlines):
        from auteur.cli import main
        rc = main(["structure", "publish", "--project", str(with_outlines), "--format", "yaml"])
        assert rc == 0
        yml = with_outlines / "published" / "chapter-structure" / "structure.yaml"
        assert yml.exists()
        import yaml
        data = yaml.safe_load(yml.read_text(encoding="utf-8"))
        assert len(data) == 2

    def test_publish_with_output_path(self, with_outlines, tmp_path):
        from auteur.cli import main
        out = tmp_path / "custom.md"
        rc = main(["structure", "publish", "--project", str(with_outlines), "--output", str(out)])
        assert rc == 0
        assert out.exists()
