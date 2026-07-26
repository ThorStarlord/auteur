"""Tests for scene publish command (v0.31.0)."""

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
def with_scenes(project_root: Path) -> Path:
    """Project with scene realization artifacts."""
    import yaml
    genre_dir = project_root / ".auteur" / "scenes" / "netorare"
    genre_dir.mkdir(parents=True, exist_ok=True)
    # Scene 1
    (genre_dir / "scene_01_01.yaml").write_text(yaml.safe_dump({
        "id": "scene_01_01",
        "chapter_id": "chapter_01",
        "status": "incomplete",
        "narrative_position": 1,
        "pov_character_id": "hero",
        "participants": ["hero", "villain"],
        "goal": {"actor_id": "hero", "objective": "Find the artifact"},
        "opposition": {"source_id": "villain", "pressure": "Blocks the path"},
        "outcome": {"result": "partial", "knowledge_added": ["artifact location"]},
        "tags": ["conflict"],
    }), encoding="utf-8")
    # Scene 2
    (genre_dir / "scene_01_02.yaml").write_text(yaml.safe_dump({
        "id": "scene_01_02",
        "chapter_id": "chapter_01",
        "status": "ready",
        "narrative_position": 2,
        "pov_character_id": "hero",
        "participants": ["hero"],
        "goal": {"actor_id": "hero", "objective": "Escape the trap"},
        "opposition": {"source_id": "external", "pressure": "Booby-trapped corridor"},
        "turn": {"type": "reversal", "event": "Floor gives way", "impact": "Hero falls into pit"},
        "decision": {"actor_id": "hero", "choice": "Use grappling hook"},
        "outcome": {"result": "success", "knowledge_added": ["escape route"]},
        "entry_state": {"knowledge": [], "emotional": {"fear": "high"}},
        "exit_state": {"knowledge": [{"what": "escape route", "how_known": "discovered", "degree": "certain", "source": "inference"}], "emotional": {"relief": "moderate"}},
        "tags": ["tension", "climax"],
    }), encoding="utf-8")
    return project_root


class TestScenePublishCLI:

    def test_publish_no_scenes(self, project_root):
        from auteur.cli import main
        rc = main(["scene", "publish", "--project", str(project_root)])
        assert rc == 1

    def test_publish_markdown_default(self, with_scenes):
        from auteur.cli import main
        rc = main(["scene", "publish", "--project", str(with_scenes)])
        assert rc == 0
        md = with_scenes / "published" / "scenes" / "scenes.md"
        assert md.exists()
        text = md.read_text(encoding="utf-8")
        assert "Scene Realization Artifacts" in text
        assert "scene_01_01" in text
        assert "scene_01_02" in text
        assert "hero" in text or "Hero" in text

    def test_publish_yaml_format(self, with_scenes):
        from auteur.cli import main
        rc = main(["scene", "publish", "--project", str(with_scenes), "--format", "yaml"])
        assert rc == 0
        yml = with_scenes / "published" / "scenes" / "scenes.yaml"
        assert yml.exists()
        import yaml
        data = yaml.safe_load(yml.read_text(encoding="utf-8"))
        assert len(data) == 2

    def test_publish_with_output_path(self, with_scenes, tmp_path):
        from auteur.cli import main
        out = tmp_path / "custom.md"
        rc = main(["scene", "publish", "--project", str(with_scenes), "--output", str(out)])
        assert rc == 0
        assert out.exists()

    def test_publish_yaml_with_output_path(self, with_scenes, tmp_path):
        from auteur.cli import main
        out = tmp_path / "custom.yaml"
        rc = main(["scene", "publish", "--project", str(with_scenes), "--output", str(out),
                    "--format", "yaml"])
        assert rc == 0
        assert out.exists()
        import yaml
        data = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert len(data) == 2
