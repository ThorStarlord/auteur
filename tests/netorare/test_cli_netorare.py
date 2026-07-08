"""Tests for the netorare CLI command orchestration."""

import json
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from auteur.cli_netorare import NetorareCommand, NetorareError, handle_netorare_init


class TestNetorareCommandInitialization:
    """Tests for NetorareCommand initialization."""

    def test_init_creates_command_with_defaults(self, tmp_path):
        """NetorareCommand initializes with default parameters."""
        cmd = NetorareCommand(tmp_path / "project")

        assert cmd.project_path == tmp_path / "project"
        assert cmd.core_id == "classic_humiliation"
        assert cmd.provider == "anthropic"
        assert cmd.port == 8765
        assert cmd.timeout == 3600.0
        assert cmd.debug is False

    def test_init_with_custom_parameters(self, tmp_path):
        """NetorareCommand initializes with custom parameters."""
        cmd = NetorareCommand(
            tmp_path / "project",
            core_id="horror",
            provider="openai",
            port=9000,
            timeout=1800.0,
            debug=True,
        )

        assert cmd.core_id == "horror"
        assert cmd.provider == "openai"
        assert cmd.port == 9000
        assert cmd.timeout == 1800.0
        assert cmd.debug is True

    def test_init_sets_correct_paths(self, tmp_path):
        """NetorareCommand sets up correct directory paths."""
        cmd = NetorareCommand(tmp_path / "myproject")

        assert cmd.project_path == tmp_path / "myproject"
        assert cmd.netorare_dir == tmp_path / "myproject" / "netorare"
        assert cmd.session_file == tmp_path / "myproject" / "netorare" / "session.json"
        assert cmd.identity_file == tmp_path / "myproject" / "story_identity.yaml"


class TestProjectPathValidation:
    """Tests for project path validation."""

    def test_validate_creates_nonexistent_path(self, tmp_path):
        """Validation creates project path if it doesn't exist."""
        cmd = NetorareCommand(tmp_path / "newproject")
        cmd._validate_project_path()

        assert cmd.project_path.exists()

    def test_validate_accepts_existing_path(self, tmp_path):
        """Validation accepts existing project path."""
        project_path = tmp_path / "existing"
        project_path.mkdir()

        cmd = NetorareCommand(project_path)
        cmd._validate_project_path()  # Should not raise

        assert cmd.project_path.exists()

    def test_validate_rejects_file_path(self, tmp_path):
        """Validation rejects path that is a file."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test")

        cmd = NetorareCommand(file_path)
        with pytest.raises(NetorareError, match="must be a directory"):
            cmd._validate_project_path()


class TestProjectStructureCreation:
    """Tests for project structure creation."""

    def test_create_structure_creates_directories(self, tmp_path):
        """Project structure creation creates necessary directories."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()

        assert (tmp_path / "project").exists()
        assert (tmp_path / "project" / "netorare").exists()
        assert (tmp_path / "project" / ".auteur").exists()

    def test_create_structure_idempotent(self, tmp_path):
        """Project structure creation is idempotent."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()
        cmd._create_project_structure()  # Call twice

        assert (tmp_path / "project").exists()
        assert (tmp_path / "project" / "netorare").exists()


class TestSessionCreation:
    """Tests for session creation."""

    def test_create_session_succeeds(self, tmp_path):
        """Session creation succeeds with valid project."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()
        cmd._create_session()

        assert cmd.session_manager is not None
        assert cmd.session_file.exists()

        # Verify session file content
        with open(cmd.session_file) as f:
            session_data = json.load(f)

        assert session_data["core_id"] == "classic_humiliation"
        assert session_data["status"] == "incomplete"
        assert session_data["choices"] == {}

    def test_create_session_rejects_existing_session(self, tmp_path):
        """Session creation rejects existing session."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()
        cmd._create_session()

        # Try to create another session
        cmd2 = NetorareCommand(tmp_path / "project")
        with pytest.raises(NetorareError, match="Session already exists"):
            cmd2._create_session()

    def test_create_session_stores_correct_core_id(self, tmp_path):
        """Session creation stores the specified core_id."""
        for core_id in ["classic_humiliation", "horror", "mystery"]:
            project_path = tmp_path / f"project_{core_id}"
            cmd = NetorareCommand(project_path, core_id=core_id)
            cmd._create_project_structure()
            cmd._create_session()

            with open(cmd.session_file) as f:
                session_data = json.load(f)

            assert session_data["core_id"] == core_id


class TestChoicesValidation:
    """Tests for choices validation."""

    def test_validate_valid_humiliation_choices(self, tmp_path):
        """Validation accepts valid humiliation choices."""
        cmd = NetorareCommand(tmp_path / "project", core_id="classic_humiliation")
        cmd._create_project_structure()
        cmd._create_session()

        # Create valid choices
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-inadequacy",
                "change": "change-accept",
                "stakes": "stakes-honor",
            },
            7: {"pacing": "pacing-slow-burn"},
        }

        # Update the session manager with valid choices
        cmd.session_manager._state["choices"] = choices
        cmd.session_manager._state["status"] = "complete"

        result = cmd._read_and_validate_choices()
        assert result == choices

    def test_validate_rejects_invalid_humiliation_choices(self, tmp_path):
        """Validation rejects invalid humiliation choices."""
        cmd = NetorareCommand(tmp_path / "project", core_id="classic_humiliation")
        cmd._create_project_structure()
        cmd._create_session()

        # Create invalid choices: want == change (forbidden)
        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-inadequacy",
                "change": "want-dignity",  # Same as want - invalid
                "stakes": "stakes-honor",
            },
        }

        cmd.session_manager._state["choices"] = choices
        cmd.session_manager._state["status"] = "complete"

        with pytest.raises(NetorareError, match="validation failed"):
            cmd._read_and_validate_choices()

    def test_validate_empty_choices_fails(self, tmp_path):
        """Validation fails when no choices provided."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()
        cmd._create_session()

        # Session has empty choices
        cmd.session_manager._state["choices"] = {}
        cmd.session_manager._state["status"] = "complete"

        with pytest.raises(NetorareError, match="No choices found"):
            cmd._read_and_validate_choices()


class TestIdentityGeneration:
    """Tests for identity generation."""

    def test_generate_identity_creates_yaml_content(self, tmp_path):
        """Identity generation creates valid YAML content."""
        cmd = NetorareCommand(tmp_path / "project", core_id="classic_humiliation")
        cmd._create_project_structure()
        cmd._create_session()

        choices = {
            4: {
                "want": "want-dignity",
                "resistance": "resistance-inadequacy",
                "change": "change-accept",
                "stakes": "stakes-honor",
            },
            7: {"pacing": "pacing-slow-burn"},
        }

        yaml_content = cmd._generate_identity(choices)

        assert isinstance(yaml_content, str)
        assert "title:" in yaml_content
        assert "core_answer:" in yaml_content
        assert "central_engine:" in yaml_content

    def test_generate_identity_includes_story_type(self, tmp_path):
        """Generated identity includes story_type information."""
        cmd = NetorareCommand(tmp_path / "project", core_id="horror")
        cmd._create_project_structure()
        cmd._create_session()

        choices = {
            4: {
                "want": "want-prevent",
                "resistance": "resistance-inescapable",
                "change": "change-transform",
                "stakes": "stakes-existence",
            },
        }

        yaml_content = cmd._generate_identity(choices)

        assert "story_type:" in yaml_content
        assert "genre:" in yaml_content

    def test_generate_identity_rejects_invalid_choices(self, tmp_path):
        """Identity generation rejects invalid choices."""
        cmd = NetorareCommand(tmp_path / "project", core_id="classic_humiliation")

        invalid_choices = {
            4: {
                "want": "unknown-want",  # Invalid want
                "resistance": "resistance-inadequacy",
                "change": "change-accept",
            },
        }

        with pytest.raises(NetorareError, match="Failed to generate identity"):
            cmd._generate_identity(invalid_choices)


class TestIdentityPersistence:
    """Tests for saving generated identity."""

    def test_save_identity_writes_file(self, tmp_path):
        """Saving identity writes file to disk."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()

        yaml_content = "title: Test Story\ncore_answer: A test story"
        cmd._save_identity(yaml_content)

        assert cmd.identity_file.exists()
        assert cmd.identity_file.read_text() == yaml_content

    def test_save_identity_overwrites_existing(self, tmp_path):
        """Saving identity overwrites existing file."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()

        # Write first version
        cmd._save_identity("title: First")
        # Write second version
        cmd._save_identity("title: Second")

        content = cmd.identity_file.read_text()
        assert content == "title: Second"

    def test_save_identity_fails_on_permission_error(self, tmp_path):
        """Saving identity raises error on permission failure."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd.identity_file = Path("/root/cannot/write/here/story_identity.yaml")

        with pytest.raises(NetorareError, match="Failed to save"):
            cmd._save_identity("content")


class TestBrowserServerStartup:
    """Tests for browser server startup."""

    @patch("subprocess.Popen")
    def test_start_browser_server_launches_process(self, mock_popen, tmp_path):
        """Starting browser server launches subprocess."""
        # Mock the subprocess
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process still running
        mock_popen.return_value = mock_process

        cmd = NetorareCommand(tmp_path / "project", port=9000)
        cmd._create_project_structure()
        cmd._create_session()

        cmd._start_browser_server()

        assert cmd.server_process is not None
        mock_popen.assert_called_once()
        # Verify port is passed to subprocess
        call_args = mock_popen.call_args
        assert "NETORARE_PORT" in call_args.kwargs["env"]
        assert call_args.kwargs["env"]["NETORARE_PORT"] == "9000"

    @patch("subprocess.Popen")
    def test_start_browser_server_fails_if_process_exits(self, mock_popen, tmp_path):
        """Starting browser server fails if subprocess exits immediately."""
        # Mock the subprocess that exits immediately
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process exited with code 1
        mock_process.communicate.return_value = ("", "Server startup failed")
        mock_popen.return_value = mock_process

        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()
        cmd._create_session()

        with pytest.raises(NetorareError, match="failed to start"):
            cmd._start_browser_server()

    @patch("subprocess.Popen")
    def test_start_browser_server_sets_environment_variables(self, mock_popen, tmp_path):
        """Starting browser server sets correct environment variables."""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        cmd = NetorareCommand(tmp_path / "project", port=8888)
        cmd._create_project_structure()
        cmd._create_session()

        cmd._start_browser_server()

        call_args = mock_popen.call_args
        env = call_args.kwargs["env"]

        assert env["NETORARE_SESSION_FILE"] == str(cmd.session_file)
        assert env["NETORARE_PORT"] == "8888"
        assert env["PYTHONUNBUFFERED"] == "1"


class TestCleanup:
    """Tests for cleanup operations."""

    @patch("subprocess.Popen")
    def test_cleanup_terminates_server(self, mock_popen, tmp_path):
        """Cleanup terminates the server subprocess."""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()
        cmd._create_session()
        cmd._start_browser_server()

        cmd._cleanup()

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()

    @patch("subprocess.Popen")
    def test_cleanup_kills_server_if_terminate_fails(self, mock_popen, tmp_path):
        """Cleanup kills server if terminate times out."""
        import subprocess as subprocess_module

        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = subprocess_module.TimeoutExpired("test", 5)
        mock_popen.return_value = mock_process

        cmd = NetorareCommand(tmp_path / "project")
        cmd._create_project_structure()
        cmd._create_session()
        cmd._start_browser_server()

        cmd._cleanup()

        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()

    def test_cleanup_handles_no_server(self, tmp_path):
        """Cleanup handles case where server was never started."""
        cmd = NetorareCommand(tmp_path / "project")
        cmd._cleanup()  # Should not raise


class TestPollingForCompletion:
    """Tests for polling session completion."""

    def test_poll_returns_when_complete(self, tmp_path):
        """Polling returns when session is marked complete."""
        cmd = NetorareCommand(tmp_path / "project", timeout=10.0)
        cmd._create_project_structure()
        cmd._create_session()

        # Mark session as complete
        cmd.session_manager.mark_complete()
        cmd.session_manager.write_to_file()

        # This should return immediately
        start = time.time()
        cmd._poll_for_completion()
        elapsed = time.time() - start

        assert elapsed < 2.0  # Should be much faster

    def test_poll_timeout_on_incomplete(self, tmp_path):
        """Polling times out if session never completes."""
        cmd = NetorareCommand(tmp_path / "project", timeout=0.5)
        cmd._create_project_structure()
        cmd._create_session()

        # Session is not marked complete
        with pytest.raises(NetorareError, match="did not complete"):
            cmd._poll_for_completion()

    def test_poll_reloads_session_from_disk(self, tmp_path):
        """Polling reloads session state from disk each iteration."""
        cmd = NetorareCommand(tmp_path / "project", timeout=5.0)
        cmd._create_project_structure()
        cmd._create_session()

        # Start with incomplete session
        assert not cmd.session_manager.is_complete()

        # Simulate browser marking session complete (via separate process)
        # We'll do this by manually updating the file
        def mark_complete_later():
            import time
            time.sleep(0.5)
            manager = cmd.session_manager
            manager.mark_complete()
            manager.write_to_file()

        import threading
        thread = threading.Thread(target=mark_complete_later, daemon=True)
        thread.start()

        # Poll should detect completion
        start = time.time()
        cmd._poll_for_completion()
        elapsed = time.time() - start

        assert elapsed < 3.0  # Should complete within reasonable time
        assert cmd.session_manager.is_complete()

        thread.join(timeout=2.0)


class TestHandleNetorareInit:
    """Tests for the handle_netorare_init entry point."""

    @patch.object(NetorareCommand, "run")
    def test_handle_netorare_init_returns_command_result(self, mock_run, tmp_path):
        """handle_netorare_init returns the command's exit code."""
        mock_run.return_value = 0

        result = handle_netorare_init(tmp_path / "project")

        assert result == 0

    @patch.object(NetorareCommand, "run")
    def test_handle_netorare_init_passes_parameters(self, mock_run, tmp_path):
        """handle_netorare_init passes parameters to NetorareCommand."""
        mock_run.return_value = 0

        handle_netorare_init(
            tmp_path / "project",
            core_id="horror",
            provider="openai",
            port=9999,
            timeout=1800.0,
            debug=True,
        )

        # The command should have been created with these parameters
        # We can't directly verify construction, but run should have been called
        mock_run.assert_called_once()


class TestFullPipeline:
    """Integration tests for the complete pipeline."""

    @patch("webbrowser.open")
    @patch("subprocess.Popen")
    def test_full_pipeline_with_mocked_subprocess(
        self, mock_popen, mock_browser, tmp_path
    ):
        """Full pipeline completes with mocked subprocess."""
        # Mock subprocess
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        # Mock browser
        mock_browser.return_value = True

        cmd = NetorareCommand(tmp_path / "project")

        # Simulate browser completing the session by updating choices via file
        def simulate_user_completion(*args, **kwargs):
            # Update session with choices and mark complete
            session_mgr = cmd.session_manager
            choices = {
                4: {
                    "want": "want-dignity",
                    "resistance": "resistance-inadequacy",
                    "change": "change-accept",
                    "stakes": "stakes-honor",
                },
                7: {"pacing": "pacing-slow-burn"},
            }
            session_mgr.update_choices(4, choices[4])
            session_mgr.update_choices(7, choices[7])
            session_mgr.mark_complete()
            session_mgr.write_to_file()

        # Patch poll_for_completion to simulate immediate completion
        with patch.object(cmd, "_poll_for_completion", side_effect=simulate_user_completion):
            # Run the full pipeline
            exit_code = cmd.run()

        assert exit_code == 0
        assert cmd.identity_file.exists()
        assert "title:" in cmd.identity_file.read_text()
