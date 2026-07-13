"""Tests for Layer 3 CLI realization commands.

Tests the integration of scene management commands with the CLI:
- seed: Create template scenes from chapter outlines
- validate: Run all validators
- inspect: Display scene coverage
- graph: Visualize scene sequence
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from auteur.narrative_realization.cli_realization import (
    CliRealizationCommands,
    handle_realization_seed,
    handle_realization_validate,
    handle_realization_inspect,
    handle_realization_graph,
)
from auteur.narrative_blueprint.schema.chapter_outline import ChapterOutline
from auteur.narrative_blueprint.loader.outline_loader import OutlineLoader
from auteur.narrative_realization.schema.scene_outline import SceneOutline


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


def test_cli_realization_commands_init(temp_project):
    """Test CliRealizationCommands initialization."""
    commands = CliRealizationCommands(temp_project, "netorare")
    assert commands.project_path == temp_project
    assert commands.genre == "netorare"
    assert commands.scenes_dir == temp_project / ".auteur" / "scenes" / "netorare"


def test_seed_command_no_chapters(temp_project):
    """Test seed command with no chapter outlines."""
    commands = CliRealizationCommands(temp_project, "netorare")
    result = commands.seed_command(force=False)
    assert result == 1  # Should fail


def test_seed_command_with_chapters(temp_project, sample_chapter_outline):
    """Test seed command with valid chapter outlines."""
    # Save sample chapter
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    result = commands.seed_command(force=False)
    assert result == 0

    # Verify scenes were created
    scenes_dir = temp_project / ".auteur" / "scenes" / "netorare"
    assert scenes_dir.exists()
    scene_files = list(scenes_dir.glob("**/*.yaml"))
    assert len(scene_files) > 0


def test_seed_command_force_overwrite(temp_project, sample_chapter_outline):
    """Test seed command with force flag."""
    # Save sample chapter
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")

    # First seed
    result1 = commands.seed_command(force=False)
    assert result1 == 0

    # Second seed without force should fail
    result2 = commands.seed_command(force=False)
    assert result2 == 1

    # Second seed with force should succeed
    result3 = commands.seed_command(force=True)
    assert result3 == 0


def test_inspect_command_no_scenes(temp_project):
    """Test inspect command with no scenes."""
    commands = CliRealizationCommands(temp_project, "netorare")
    result = commands.inspect_command()
    assert result == 1  # Should fail


def test_inspect_command_with_scenes(temp_project, sample_chapter_outline):
    """Test inspect command with valid scenes."""
    # Create scenes
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    commands.seed_command(force=False)

    # Now inspect should work
    result = commands.inspect_command()
    assert result == 0


def test_validate_command_no_scenes(temp_project):
    """Test validate command with no scenes."""
    commands = CliRealizationCommands(temp_project, "netorare")
    result = commands.validate_command()
    assert result == 2  # No scenes found


def test_validate_command_with_scenes(temp_project, sample_chapter_outline):
    """Test validate command with valid scenes."""
    # Create scenes
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    commands.seed_command(force=False)

    # Validate should work
    result = commands.validate_command()
    # Should pass (0) or have issues (1), but not crash (2)
    assert result in (0, 1)


def test_graph_command_no_scenes(temp_project):
    """Test graph command with no scenes."""
    commands = CliRealizationCommands(temp_project, "netorare")
    result = commands.graph_command("text")
    assert result == 1


def test_graph_command_text_format(temp_project, sample_chapter_outline):
    """Test graph command with text format."""
    # Create scenes
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    commands.seed_command(force=False)

    result = commands.graph_command("text")
    assert result == 0


def test_graph_command_dot_format(temp_project, sample_chapter_outline):
    """Test graph command with DOT format."""
    # Create scenes
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    commands.seed_command(force=False)

    result = commands.graph_command("dot")
    assert result == 0


def test_handle_realization_seed(temp_project, sample_chapter_outline):
    """Test handle_realization_seed handler function."""
    # Create sample chapter
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    result = handle_realization_seed(temp_project, "netorare", force=False)
    assert result == 0


def test_handle_realization_validate(temp_project, sample_chapter_outline):
    """Test handle_realization_validate handler function."""
    # Create sample chapter and scenes
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    commands.seed_command(force=False)

    result = handle_realization_validate(temp_project, "netorare")
    assert result in (0, 1)  # Pass or fail, but not error


def test_handle_realization_inspect(temp_project, sample_chapter_outline):
    """Test handle_realization_inspect handler function."""
    # Create sample chapter and scenes
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    commands.seed_command(force=False)

    result = handle_realization_inspect(temp_project, "netorare")
    assert result == 0


def test_handle_realization_graph(temp_project, sample_chapter_outline):
    """Test handle_realization_graph handler function."""
    # Create sample chapter and scenes
    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(sample_chapter_outline, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    commands.seed_command(force=False)

    result = handle_realization_graph(temp_project, "netorare", "text")
    assert result == 0


def test_genre_routing_mystery(temp_project):
    """Test that commands work for mystery genre."""
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

    outlines_dir = temp_project / ".auteur" / "outlines" / "mystery"
    outlines_dir.mkdir(parents=True)
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(chapter, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "mystery")
    result = commands.seed_command(force=False)
    assert result == 0
    assert commands.genre == "mystery"


def test_genre_routing_gentlefemdom(temp_project):
    """Test that commands work for gentlefemdom genre."""
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

    outlines_dir = temp_project / ".auteur" / "outlines" / "gentlefemdom"
    outlines_dir.mkdir(parents=True)
    loader = OutlineLoader()
    chapter_path = outlines_dir / "chapter_01.yaml"
    loader.save_outline(chapter, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "gentlefemdom")
    result = commands.seed_command(force=False)
    assert result == 0
    assert commands.genre == "gentlefemdom"


def test_multiple_chapters(temp_project):
    """Test seed command with multiple chapters."""
    now = datetime.now(timezone.utc)
    chapters = []
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
        chapters.append(chapter)

    outlines_dir = temp_project / ".auteur" / "outlines" / "netorare"
    loader = OutlineLoader()
    for chapter in chapters:
        chapter_path = outlines_dir / f"chapter_{chapter.chapter_number:02d}.yaml"
        loader.save_outline(chapter, str(chapter_path))

    commands = CliRealizationCommands(temp_project, "netorare")
    result = commands.seed_command(force=False)
    assert result == 0

    # Verify scenes for each chapter
    scenes_dir = temp_project / ".auteur" / "scenes" / "netorare"
    for i in range(1, 4):
        chapter_dir = scenes_dir / f"chapter_{i:02d}"
        assert chapter_dir.exists()
        scene_files = list(chapter_dir.glob("*.yaml"))
        assert len(scene_files) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
