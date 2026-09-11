"""Tests for Layer 3 CLI realization commands.

Tests the integration of scene management commands with the CLI:
- seed: Create template scenes from chapter outlines
- validate: Run all validators
- inspect: Display scene coverage
- graph: Visualize scene sequence
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_realization.cli_realization import (
    CliRealizationCommands,
    handle_realization_graph,
    handle_realization_inspect,
    handle_realization_seed,
    handle_realization_validate,
)


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    with TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        (project_path / ".auteur" / "outlines" / "netorare").mkdir(parents=True)
        yield project_path


@pytest.fixture
def sample_chapter_outline():
    """Create a sample chapter outline for testing."""
    now = datetime.now(timezone.utc)
    return ChapterOutline(
        genre="netorare",
        story_id="story_001",
        name="Chapter 1 Outline",
        description="First chapter",
        created_at=now,
        modified_at=now,
        parent_id="book_001",
        chapter_number=1,
        phase=1,
        title="The Setup",
        goal="Establish the initial situation",
        conflict="Internal doubt vs external pressure",
        turning_point="The temptation arrives",
        emotional_beat="comfort -> confusion",
    )


def _save_chapter(temp_project: Path, genre: str, chapter: ChapterOutline) -> None:
    outlines_dir = temp_project / ".auteur" / "outlines" / genre
    outlines_dir.mkdir(parents=True, exist_ok=True)
    OutlineLoader().save_outline(chapter, str(outlines_dir / "chapter_01.yaml"))


def _seed(temp_project: Path, genre: str, chapter: ChapterOutline) -> CliRealizationCommands:
    _save_chapter(temp_project, genre, chapter)
    commands = CliRealizationCommands(temp_project, genre)
    assert commands.seed_command(force=False) == 0
    return commands


def test_cli_realization_commands_init(temp_project):
    commands = CliRealizationCommands(temp_project, "netorare")
    assert commands.project_path == temp_project
    assert commands.genre == "netorare"
    assert commands.scenes_dir == temp_project / ".auteur" / "scenes" / "netorare"


def test_seed_command_no_chapters(temp_project):
    commands = CliRealizationCommands(temp_project, "netorare")
    assert commands.seed_command(force=False) == 1


def test_seed_command_with_chapters(temp_project, sample_chapter_outline):
    commands = _seed(temp_project, "netorare", sample_chapter_outline)
    scene_files = list(commands.scenes_dir.glob("**/*.yaml"))
    assert scene_files


def test_seed_command_force_overwrite(temp_project, sample_chapter_outline):
    commands = _seed(temp_project, "netorare", sample_chapter_outline)
    assert commands.seed_command(force=False) == 1
    assert commands.seed_command(force=True) == 0


def test_inspect_command_no_scenes(temp_project):
    commands = CliRealizationCommands(temp_project, "netorare")
    assert commands.inspect_command() == 1


def test_inspect_command_with_scenes(temp_project, sample_chapter_outline):
    commands = _seed(temp_project, "netorare", sample_chapter_outline)
    assert commands.inspect_command() == 0


def test_validate_command_no_scenes(temp_project):
    commands = CliRealizationCommands(temp_project, "netorare")
    assert commands.validate_command() == 2


def test_validate_command_with_scenes(temp_project, sample_chapter_outline):
    commands = _seed(temp_project, "netorare", sample_chapter_outline)
    assert commands.validate_command() in (0, 1)


def test_graph_command_no_scenes(temp_project):
    commands = CliRealizationCommands(temp_project, "netorare")
    assert commands.graph_command("text") == 1


def test_graph_command_text_format(temp_project, sample_chapter_outline):
    commands = _seed(temp_project, "netorare", sample_chapter_outline)
    assert commands.graph_command("text") == 0


def test_graph_command_dot_format(temp_project, sample_chapter_outline):
    commands = _seed(temp_project, "netorare", sample_chapter_outline)
    assert commands.graph_command("dot") == 0


def test_handle_realization_seed(temp_project, sample_chapter_outline):
    _save_chapter(temp_project, "netorare", sample_chapter_outline)
    assert handle_realization_seed(temp_project, "netorare", force=False) == 0


def test_handle_realization_validate(temp_project, sample_chapter_outline):
    _seed(temp_project, "netorare", sample_chapter_outline)
    assert handle_realization_validate(temp_project, "netorare") in (0, 1)


def test_handle_realization_inspect(temp_project, sample_chapter_outline):
    _seed(temp_project, "netorare", sample_chapter_outline)
    assert handle_realization_inspect(temp_project, "netorare") == 0


def test_handle_realization_graph(temp_project, sample_chapter_outline):
    _seed(temp_project, "netorare", sample_chapter_outline)
    assert handle_realization_graph(temp_project, "netorare", "text") == 0


def test_genre_routing_mystery(temp_project):
    now = datetime.now(timezone.utc)
    chapter = ChapterOutline(
        genre="mystery",
        story_id="mystery_001",
        name="Chapter 1",
        description="Crime scene",
        created_at=now,
        modified_at=now,
        parent_id="book_001",
        chapter_number=1,
        phase=1,
        title="The Murder",
        goal="Discover the crime",
        conflict="Limited clues",
        turning_point="First suspect found",
        emotional_beat="shock -> confusion",
    )
    commands = _seed(temp_project, "mystery", chapter)
    assert commands.genre == "mystery"


def test_genre_routing_gentlefemdom(temp_project):
    now = datetime.now(timezone.utc)
    chapter = ChapterOutline(
        genre="gentlefemdom",
        story_id="gfd_001",
        name="Chapter 1",
        description="First date",
        created_at=now,
        modified_at=now,
        parent_id="book_001",
        chapter_number=1,
        phase=1,
        title="Attraction",
        goal="Explore desires",
        conflict="Fear of judgment",
        turning_point="First touch",
        emotional_beat="hesitation -> connection",
    )
    commands = _seed(temp_project, "gentlefemdom", chapter)
    assert commands.genre == "gentlefemdom"


def test_multiple_chapters(temp_project):
    now = datetime.now(timezone.utc)
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    for i in range(1, 4):
        chapter = ChapterOutline(
            genre="netorare",
            story_id="story_multi",
            name=f"Chapter {i}",
            description=f"Chapter {i} description",
            created_at=now,
            modified_at=now,
            parent_id="book_001",
            chapter_number=i,
            phase=i,
            title=f"Chapter {i}",
            goal=f"Objective {i}",
            conflict=f"Conflict {i}",
            turning_point=f"Turning point {i}",
            emotional_beat=f"emotion {i}",
        )
        loader.save_outline(chapter, str(outlines_dir / f"chapter_{i:02d}.yaml"))

    commands = CliRealizationCommands(temp_project, "netorare")
    assert commands.seed_command(force=False) == 0
    for i in range(1, 4):
        chapter_dir = commands.scenes_dir / f"chapter_{i:02d}"
        assert chapter_dir.exists()
        assert list(chapter_dir.glob("*.yaml"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
