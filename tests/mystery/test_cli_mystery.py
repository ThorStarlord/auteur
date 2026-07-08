"""Integration tests for MysteryCommand CLI workflow."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from auteur.cli_mystery import MysteryCommand, MysteryError
from auteur.netorare.session import SessionManager, SessionError
from auteur.mystery.validation import validate_choices
from auteur.mystery.core_templates import get_template


class TestMysteryCommandBasics:
    """Test MysteryCommand initialization and path consistency."""

    def test_mystery_command_init_creates_correct_paths(self):
        """Test that MysteryCommand initializes with netorare directory paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            cmd = MysteryCommand(project_path, core_id="howdunit")

            assert cmd.netorare_dir == project_path / "netorare"
            assert cmd.session_file == project_path / "netorare" / "session.json"
            assert cmd.identity_file == project_path / "story_identity.yaml"

    def test_mystery_command_session_path_consistency_with_session_manager(self):
        """Test that CLI session path matches SessionManager expectations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create a session using SessionManager
            session_manager = SessionManager.create_session(project_path, "howdunit")

            # Verify session exists at netorare/session.json
            expected_path = project_path / "netorare" / "session.json"
            assert expected_path.exists()

            # Now create a MysteryCommand and verify it looks in the same place
            cmd = MysteryCommand(project_path, core_id="howdunit")
            assert cmd.session_file == expected_path

    def test_mystery_command_creates_netorare_directory(self):
        """Test that CLI creates netorare directory, not mystery directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            cmd = MysteryCommand(project_path, core_id="howdunit")
            cmd._create_project_structure()

            assert (project_path / "netorare").exists()
            assert not (project_path / "mystery").exists()

    def test_mystery_command_validates_project_path(self):
        """Test that CLI validates project path exists or can be created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "subdir" / "project"
            cmd = MysteryCommand(project_path, core_id="howdunit")
            cmd._validate_project_path()

            assert project_path.exists()
            assert project_path.is_dir()


class TestMysteryCommandSession:
    """Test MysteryCommand session management."""

    def test_mystery_command_create_session_sets_session_manager(self):
        """Test that CLI creates session and sets session_manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            cmd = MysteryCommand(project_path, core_id="howdunit")
            cmd._validate_project_path()
            cmd._create_project_structure()
            cmd._create_session()

            assert cmd.session_manager is not None
            assert cmd.session_file.exists()
            assert cmd.session_file == project_path / "netorare" / "session.json"

    def test_mystery_command_create_session_fails_if_exists(self):
        """Test that CLI raises error if session already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create first session
            cmd1 = MysteryCommand(project_path, core_id="howdunit")
            cmd1._validate_project_path()
            cmd1._create_project_structure()
            cmd1._create_session()

            # Try to create second session - should fail
            cmd2 = MysteryCommand(project_path, core_id="howdunit")
            cmd2._validate_project_path()
            cmd2._create_project_structure()

            with pytest.raises(MysteryError, match="Session already exists"):
                cmd2._create_session()


class TestMysteryCommandChoicesValidation:
    """Test MysteryCommand choices validation workflow."""

    @pytest.mark.parametrize("core_id", ["howdunit", "paranoia", "cozy"])
    def test_mystery_command_validates_choices_for_all_cores(self, core_id):
        """Test that validation works for all three mystery cores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create session
            session_manager = SessionManager.create_session(project_path, core_id)

            # Get template and create valid minimal choices
            template = get_template(core_id)
            choices = {
                2: {"genre_contract": "puzzle-box"},
                4: {"want": "find truth", "change": "gain wisdom"},
                5: {"narrator_reliability": "fully-reliable"},
                6: {"gaslighting_intensity": "none", "relationship_focus": "trio"},
                7: {"clue_distribution": "even", "paranoia_escalation": "steady", "violence_budget": "none"},
                8: {"truth_ambiguity": "mostly-revealed", "solution_density": "loose", "community_role": "protagonist-solves"},
            }

            # Validate using function
            is_valid, errors, warnings = validate_choices(template, choices)
            assert is_valid, f"Validation failed for {core_id}: {errors}"

    def test_mystery_command_rejects_invalid_choices_howdunit(self):
        """Test that CLI rejects invalid choices (Want = Change) for howdunit."""
        template = get_template("howdunit")
        choices = {
            2: {"genre_contract": "puzzle-box"},
            4: {"want": "find truth", "change": "find truth"},  # INVALID: same
            5: {"narrator_reliability": "fully-reliable"},
            7: {"clue_distribution": "late-heavy"},  # INVALID for tight solutions
            8: {"solution_density": "tight"},  # INVALID pairing
        }

        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert len(errors) > 0

    def test_mystery_command_rejects_invalid_choices_paranoia(self):
        """Test that CLI rejects invalid choices for paranoia."""
        template = get_template("paranoia")
        choices = {
            4: {"want": "survive", "change": "survive"},  # INVALID: same
            5: {"narrator_reliability": "highly-unreliable"},
            8: {"truth_ambiguity": "fully-revealed"},  # INVALID: contradicts unreliable narrator
        }

        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert len(errors) > 0

    def test_mystery_command_rejects_invalid_choices_cozy(self):
        """Test that CLI rejects invalid choices for cozy."""
        template = get_template("cozy")
        choices = {
            4: {"want": "solve mystery", "change": "find peace"},
            5: {"humor_level": "dark-undertone"},
            7: {"violence_budget": "graphic"},  # INVALID: too much for cozy
            9: {"warmth_confidence": "very-cozy"},  # INVALID: conflicts with dark humor
        }

        is_valid, errors, warnings = validate_choices(template, choices)
        assert not is_valid
        assert len(errors) > 0


class TestMysteryCommandAllCores:
    """Test MysteryCommand with all three cores."""

    @pytest.mark.parametrize("core_id", ["howdunit", "paranoia", "cozy"])
    def test_mystery_command_initializes_with_all_cores(self, core_id):
        """Test that MysteryCommand can be initialized with all three cores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            cmd = MysteryCommand(project_path, core_id=core_id)

            assert cmd.core_id == core_id
            assert cmd.project_path == project_path

    @pytest.mark.parametrize("core_id", ["howdunit", "paranoia", "cozy"])
    def test_mystery_command_session_creation_all_cores(self, core_id):
        """Test that sessions can be created for all three cores."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            cmd = MysteryCommand(project_path, core_id=core_id)
            cmd._validate_project_path()
            cmd._create_project_structure()
            cmd._create_session()

            assert cmd.session_manager is not None
            assert cmd.session_manager.get_state()["core_id"] == core_id
            assert cmd.session_file.exists()


class TestMysteryCommandErrorHandling:
    """Test MysteryCommand error handling."""

    def test_mystery_error_exception(self):
        """Test that MysteryError can be raised and caught."""
        with pytest.raises(MysteryError, match="Test error"):
            raise MysteryError("Test error")

    def test_mystery_command_handles_invalid_project_path(self):
        """Test that CLI handles non-directory project path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file instead of directory
            project_path = Path(tmpdir) / "file.txt"
            project_path.write_text("test")

            cmd = MysteryCommand(project_path, core_id="howdunit")
            with pytest.raises(MysteryError, match="Project path must be a directory"):
                cmd._validate_project_path()

    def test_mystery_command_missing_session_file_for_server(self):
        """Test that CLI raises error if session file missing when starting server."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            cmd = MysteryCommand(project_path, core_id="howdunit")
            cmd._validate_project_path()
            cmd._create_project_structure()
            # Don't create session

            with pytest.raises(MysteryError, match="Session file not found"):
                cmd._start_browser_server()
