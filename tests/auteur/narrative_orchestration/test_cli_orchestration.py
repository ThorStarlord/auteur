"""Tests for CLI Orchestration Workflow (Task 11).

Validates that:
- seed command creates all outline artifacts from StoryIdentity
- validate command runs all 3 validators and reports results
- graph command visualizes outline structure
- status command shows comprehensive outline status
- Integration between commands works correctly
- Error handling for missing files and invalid input
- Commands work identically across all 3 genres
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from auteur.identity import StoryIdentity, HighLevelCentralEngine, StoryType
from auteur.blueprint import (
    Genre,
    StoryMode,
    StoryMedium,
    TargetAudience,
    TargetExperience,
)
from auteur.narrative_orchestration.cli_orchestration import (
    CliOrchestrationCommands,
    handle_orchestration_seed,
    handle_orchestration_validate,
    handle_orchestration_graph,
    handle_orchestration_status,
)


class TestCliOrchestrationSeeding:
    """Test seed command functionality."""

    @staticmethod
    def create_test_story_identity(genre: Genre) -> StoryIdentity:
        """Create a test StoryIdentity."""
        return StoryIdentity(
            title="Test Story",
            core_answer="A test narrative",
            target_experience=TargetExperience(
                primary="tension",
                progression="rising",
                avoid=[]
            ),
            story_type=StoryType(
                medium=StoryMedium.NOVEL,
                mode=StoryMode.TRAGIC,
                genre=genre,
                target_audience=TargetAudience.ADULT,
            ),
            central_engine=HighLevelCentralEngine(
                want="to solve the mystery",
                resistance="false clues and deception",
                conflict="truth vs perception",
                stakes="justice for the victim",
                change="understanding of human nature",
            ),
        )

    def test_seed_command_netorare(self):
        """Test seed command for netorare genre."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.NETORARE)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            commands = CliOrchestrationCommands(project_path, "netorare")
            exit_code = commands.seed_command(identity_path)

            assert exit_code == 0
            outlines_dir = project_path / ".auteur" / "outlines" / "netorare"
            assert outlines_dir.exists()
            assert (outlines_dir / "book_outline.yaml").exists()
            assert any("chapter" in f.name for f in outlines_dir.glob("*.yaml"))
            assert (outlines_dir / "character_arc.yaml").exists()
            assert (outlines_dir / "story_arc.yaml").exists()

    def test_seed_command_mystery(self):
        """Test seed command for mystery genre."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.MYSTERY)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            commands = CliOrchestrationCommands(project_path, "mystery")
            exit_code = commands.seed_command(identity_path)

            assert exit_code == 0
            outlines_dir = project_path / ".auteur" / "outlines" / "mystery"
            assert outlines_dir.exists()
            assert (outlines_dir / "book_outline.yaml").exists()

    def test_seed_command_gentlefemdom(self):
        """Test seed command for gentlefemdom genre."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.GENTLEFEMDOM)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            commands = CliOrchestrationCommands(project_path, "gentlefemdom")
            exit_code = commands.seed_command(identity_path)

            assert exit_code == 0
            outlines_dir = project_path / ".auteur" / "outlines" / "gentlefemdom"
            assert outlines_dir.exists()
            assert (outlines_dir / "book_outline.yaml").exists()

    def test_seed_command_missing_identity_file(self):
        """Test seed command with missing identity file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            missing_path = project_path / "nonexistent.yaml"

            commands = CliOrchestrationCommands(project_path, "netorare")
            exit_code = commands.seed_command(missing_path)

            assert exit_code == 1

    def test_seed_command_genre_mismatch(self):
        """Test seed command with genre mismatch."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.MYSTERY)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            # Try to seed with netorare command but mystery identity
            commands = CliOrchestrationCommands(project_path, "netorare")
            exit_code = commands.seed_command(identity_path)

            assert exit_code == 1

    def test_seed_command_force_overwrite(self):
        """Test seed command with --force flag to overwrite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.NETORARE)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            commands = CliOrchestrationCommands(project_path, "netorare")

            # First seed
            exit_code1 = commands.seed_command(identity_path)
            assert exit_code1 == 0

            # Second seed without force should fail
            exit_code2 = commands.seed_command(identity_path, force=False)
            assert exit_code2 == 1

            # Second seed with force should succeed
            exit_code3 = commands.seed_command(identity_path, force=True)
            assert exit_code3 == 0


class TestCliOrchestrationValidation:
    """Test validate command functionality."""

    @staticmethod
    def create_test_story_identity(genre: Genre) -> StoryIdentity:
        """Create a test StoryIdentity."""
        return StoryIdentity(
            title="Test Story",
            core_answer="A test narrative",
            target_experience=TargetExperience(
                primary="tension",
                progression="rising",
                avoid=[]
            ),
            story_type=StoryType(
                medium=StoryMedium.NOVEL,
                mode=StoryMode.TRAGIC,
                genre=genre,
                target_audience=TargetAudience.ADULT,
            ),
            central_engine=HighLevelCentralEngine(
                want="to solve the mystery",
                resistance="false clues and deception",
                conflict="truth vs perception",
                stakes="justice for the victim",
                change="understanding of human nature",
            ),
        )

    def test_validate_command_empty_outlines(self):
        """Test validate command with no outlines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            commands = CliOrchestrationCommands(project_path, "netorare")
            exit_code = commands.validate_command()

            # Should return exit code 2 (no outlines found)
            assert exit_code == 2

    def test_validate_command_valid_outlines(self):
        """Test validate command with valid outlines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.NETORARE)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            # Seed outlines first
            commands = CliOrchestrationCommands(project_path, "netorare")
            seed_exit = commands.seed_command(identity_path)
            assert seed_exit == 0

            # Now validate
            validate_exit = commands.validate_command()
            # Should pass validation (exit 0)
            assert validate_exit == 0


class TestCliOrchestrationGraph:
    """Test graph command functionality."""

    @staticmethod
    def create_test_story_identity(genre: Genre) -> StoryIdentity:
        """Create a test StoryIdentity."""
        return StoryIdentity(
            title="Test Story",
            core_answer="A test narrative",
            target_experience=TargetExperience(
                primary="tension",
                progression="rising",
                avoid=[]
            ),
            story_type=StoryType(
                medium=StoryMedium.NOVEL,
                mode=StoryMode.TRAGIC,
                genre=genre,
                target_audience=TargetAudience.ADULT,
            ),
            central_engine=HighLevelCentralEngine(
                want="to solve the mystery",
                resistance="false clues and deception",
                conflict="truth vs perception",
                stakes="justice for the victim",
                change="understanding of human nature",
            ),
        )

    def test_graph_command_no_outlines(self):
        """Test graph command with no outlines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            commands = CliOrchestrationCommands(project_path, "netorare")
            exit_code = commands.graph_command()

            assert exit_code == 1

    def test_graph_command_text_format(self):
        """Test graph command with text (ASCII) format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.NETORARE)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            commands = CliOrchestrationCommands(project_path, "netorare")
            seed_exit = commands.seed_command(identity_path)
            assert seed_exit == 0

            graph_exit = commands.graph_command(output_format="text")
            assert graph_exit == 0

    def test_graph_command_dot_format(self):
        """Test graph command with DOT (Graphviz) format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.NETORARE)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            commands = CliOrchestrationCommands(project_path, "netorare")
            seed_exit = commands.seed_command(identity_path)
            assert seed_exit == 0

            graph_exit = commands.graph_command(output_format="dot")
            assert graph_exit == 0


class TestCliOrchestrationStatus:
    """Test status command functionality."""

    @staticmethod
    def create_test_story_identity(genre: Genre) -> StoryIdentity:
        """Create a test StoryIdentity."""
        return StoryIdentity(
            title="Test Story",
            core_answer="A test narrative",
            target_experience=TargetExperience(
                primary="tension",
                progression="rising",
                avoid=[]
            ),
            story_type=StoryType(
                medium=StoryMedium.NOVEL,
                mode=StoryMode.TRAGIC,
                genre=genre,
                target_audience=TargetAudience.ADULT,
            ),
            central_engine=HighLevelCentralEngine(
                want="to solve the mystery",
                resistance="false clues and deception",
                conflict="truth vs perception",
                stakes="justice for the victim",
                change="understanding of human nature",
            ),
        )

    def test_status_command_no_outlines(self):
        """Test status command with no outlines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            commands = CliOrchestrationCommands(project_path, "netorare")
            exit_code = commands.status_command()

            assert exit_code == 1

    def test_status_command_with_outlines(self):
        """Test status command with valid outlines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.NETORARE)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            commands = CliOrchestrationCommands(project_path, "netorare")
            seed_exit = commands.seed_command(identity_path)
            assert seed_exit == 0

            status_exit = commands.status_command()
            assert status_exit == 0


class TestCliOrchestrationIntegration:
    """Test integration between commands."""

    @staticmethod
    def create_test_story_identity(genre: Genre) -> StoryIdentity:
        """Create a test StoryIdentity."""
        return StoryIdentity(
            title="Integration Test Story",
            core_answer="A test narrative",
            target_experience=TargetExperience(
                primary="tension",
                progression="rising",
                avoid=[]
            ),
            story_type=StoryType(
                medium=StoryMedium.NOVEL,
                mode=StoryMode.TRAGIC,
                genre=genre,
                target_audience=TargetAudience.ADULT,
            ),
            central_engine=HighLevelCentralEngine(
                want="to solve the mystery",
                resistance="false clues and deception",
                conflict="truth vs perception",
                stakes="justice for the victim",
                change="understanding of human nature",
            ),
        )

    def test_full_workflow_seed_status_validate_graph(self):
        """Test complete workflow: seed → status → validate → graph."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.MYSTERY)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            commands = CliOrchestrationCommands(project_path, "mystery")

            # 1. Seed outlines
            seed_exit = commands.seed_command(identity_path)
            assert seed_exit == 0

            # 2. Check status
            status_exit = commands.status_command()
            assert status_exit == 0

            # 3. Validate
            validate_exit = commands.validate_command()
            assert validate_exit == 0

            # 4. Generate graph
            graph_exit = commands.graph_command()
            assert graph_exit == 0

    def test_handler_functions(self):
        """Test handler functions for CLI integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            identity = self.create_test_story_identity(Genre.GENTLEFEMDOM)
            identity_path = project_path / "story_identity.yaml"
            identity.to_yaml(identity_path)

            # Test handler functions
            seed_exit = handle_orchestration_seed(project_path, "gentlefemdom", identity_path)
            assert seed_exit == 0

            validate_exit = handle_orchestration_validate(project_path, "gentlefemdom")
            assert validate_exit == 0

            status_exit = handle_orchestration_status(project_path, "gentlefemdom")
            assert status_exit == 0

            graph_exit = handle_orchestration_graph(project_path, "gentlefemdom")
            assert graph_exit == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
