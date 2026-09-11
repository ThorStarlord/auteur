"""Active contract tests for Layer 3 realization CLI commands."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_realization.cli_realization import CliRealizationCommands


def _chapter(genre: str = "netorare", *, phase: int = 1) -> ChapterOutline:
    now = datetime.now(timezone.utc)
    return ChapterOutline(
        genre=genre,
        story_id=f"{genre}_story",
        name="Chapter 1 Outline",
        description="First chapter",
        created_at=now,
        modified_at=now,
        parent_id="book_001",
        chapter_number=1,
        phase=phase,
        title="The Setup",
        goal="Establish the initial situation",
        conflict="Internal doubt vs external pressure",
        turning_point="The temptation arrives",
        emotional_beat="comfort -> confusion",
    )


def _save_chapter(project: Path, chapter: ChapterOutline) -> None:
    outlines_dir = project / ".auteur" / "outlines" / chapter.genre
    outlines_dir.mkdir(parents=True, exist_ok=True)
    OutlineLoader().save_outline(chapter, str(outlines_dir / "chapter_01.yaml"))


def _seed(project: Path, genre: str = "netorare", *, phase: int = 1) -> CliRealizationCommands:
    _save_chapter(project, _chapter(genre, phase=phase))
    commands = CliRealizationCommands(project, genre)
    assert commands.seed_command(force=False) == 0
    return commands


def test_commands_initialize_expected_paths(tmp_path: Path) -> None:
    commands = CliRealizationCommands(tmp_path, "netorare")
    assert commands.project_path == tmp_path
    assert commands.scenes_dir == tmp_path / ".auteur" / "scenes" / "netorare"


def test_seed_rejects_missing_chapter_outlines(tmp_path: Path) -> None:
    commands = CliRealizationCommands(tmp_path, "netorare")
    assert commands.seed_command(force=False) == 1


def test_seed_creates_draft_scene_files(tmp_path: Path) -> None:
    commands = _seed(tmp_path)
    scene_files = sorted(commands.scenes_dir.glob("**/*.yaml"))
    assert len(scene_files) == 2


def test_midpoint_seed_creates_three_scenes(tmp_path: Path) -> None:
    commands = _seed(tmp_path, phase=5)
    assert len(list(commands.scenes_dir.glob("**/*.yaml"))) == 3


def test_seed_rejects_existing_scenes_without_force(tmp_path: Path) -> None:
    commands = _seed(tmp_path)
    assert commands.seed_command(force=False) == 1
    assert commands.seed_command(force=True) == 0


def test_inspect_accepts_seeded_draft_scenes(tmp_path: Path) -> None:
    commands = _seed(tmp_path)
    assert commands.inspect_command() == 0


def test_validate_accepts_seeded_draft_scenes(tmp_path: Path) -> None:
    commands = _seed(tmp_path)
    assert commands.validate_command() == 0


def test_graph_text_accepts_seeded_draft_scenes(tmp_path: Path) -> None:
    commands = _seed(tmp_path)
    assert commands.graph_command("text") == 0


def test_graph_dot_accepts_seeded_draft_scenes(tmp_path: Path) -> None:
    commands = _seed(tmp_path)
    assert commands.graph_command("dot") == 0


def test_inspect_and_graph_reject_missing_scenes(tmp_path: Path) -> None:
    commands = CliRealizationCommands(tmp_path, "netorare")
    assert commands.inspect_command() == 1
    assert commands.graph_command("text") == 1
    assert commands.validate_command() == 2


def test_same_runtime_supports_mystery(tmp_path: Path) -> None:
    commands = _seed(tmp_path, "mystery")
    assert commands.inspect_command() == 0


def test_same_runtime_supports_gentlefemdom(tmp_path: Path) -> None:
    commands = _seed(tmp_path, "gentlefemdom")
    assert commands.graph_command("text") == 0
