"""Tests for file-based JSON session state management."""

import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from auteur.netorare.session import SessionManager, SessionError


class TestSessionCreation:
    """Tests for creating new sessions."""

    def test_create_session_creates_session_directory(self, tmp_path):
        """Creating a session creates the session directory."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")

        assert (project_path / "netorare").exists()
        assert (project_path / "netorare" / "session.json").exists()

    def test_create_session_returns_manager_instance(self, tmp_path):
        """create_session returns a SessionManager instance."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")

        assert isinstance(session, SessionManager)

    def test_create_session_generates_unique_id(self, tmp_path):
        """Creating multiple sessions generates unique IDs."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session1 = SessionManager.create_session(project_path, "classic_humiliation")
        # Create another session directory for second session
        project_path2 = tmp_path / "project2"
        project_path2.mkdir()
        session2 = SessionManager.create_session(project_path2, "horror")

        state1 = session1.get_state()
        state2 = session2.get_state()
        assert state1["id"] != state2["id"]

    def test_create_session_stores_core_id(self, tmp_path):
        """Creating a session stores the core_id."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        state = session.get_state()

        assert state["core_id"] == "classic_humiliation"

    def test_create_session_status_incomplete(self, tmp_path):
        """New sessions start with status 'incomplete'."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "horror")
        state = session.get_state()

        assert state["status"] == "incomplete"

    def test_create_session_empty_choices(self, tmp_path):
        """New sessions start with empty choices."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "mystery")
        state = session.get_state()

        assert state["choices"] == {}

    def test_create_session_has_timestamp(self, tmp_path):
        """New sessions have a timestamp."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        before = datetime.now(timezone.utc).isoformat()
        session = SessionManager.create_session(project_path, "classic_humiliation")
        after = datetime.now(timezone.utc).isoformat()
        state = session.get_state()

        assert "timestamp" in state
        # Timestamp should be between before and after
        assert before <= state["timestamp"] <= after


class TestSessionPersistence:
    """Tests for reading/writing session state to disk."""

    def test_session_persists_to_json_file(self, tmp_path):
        """Session state is persisted to session.json."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session_file = project_path / "netorare" / "session.json"

        assert session_file.exists()
        with open(session_file) as f:
            data = json.load(f)
        assert data["core_id"] == "classic_humiliation"

    def test_session_json_is_valid_json(self, tmp_path):
        """session.json is valid JSON (not corrupted)."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "horror")
        session_file = project_path / "netorare" / "session.json"

        # Should not raise
        with open(session_file) as f:
            json.load(f)

    def test_session_json_is_inspectable(self, tmp_path):
        """session.json contains human-readable, inspectable state."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "mystery")
        session_file = project_path / "netorare" / "session.json"

        with open(session_file) as f:
            content = f.read()

        # Should be readable (not minified)
        assert "\n" in content  # Has newlines
        assert "core_id" in content
        assert "status" in content
        assert "choices" in content


class TestSessionLoading:
    """Tests for loading existing sessions from disk."""

    def test_load_session_reads_from_file(self, tmp_path):
        """load_session reads session from disk."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        # Create a session
        session1 = SessionManager.create_session(project_path, "classic_humiliation")
        session_id = session1.get_state()["id"]

        # Load it back
        session2 = SessionManager.load_session(project_path / "netorare" / "session.json")
        state2 = session2.get_state()

        assert state2["id"] == session_id

    def test_load_session_preserves_all_fields(self, tmp_path):
        """load_session preserves all fields from disk."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session1 = SessionManager.create_session(project_path, "horror")
        state1 = session1.get_state()

        session2 = SessionManager.load_session(project_path / "netorare" / "session.json")
        state2 = session2.get_state()

        # All fields should match
        assert state1["id"] == state2["id"]
        assert state1["core_id"] == state2["core_id"]
        assert state1["status"] == state2["status"]
        assert state1["timestamp"] == state2["timestamp"]

    def test_load_session_raises_on_missing_file(self, tmp_path):
        """load_session raises SessionError if file doesn't exist."""
        with pytest.raises(SessionError):
            SessionManager.load_session(tmp_path / "nonexistent.json")

    def test_load_session_raises_on_corrupted_json(self, tmp_path):
        """load_session raises SessionError if JSON is corrupted."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json")

        with pytest.raises(SessionError):
            SessionManager.load_session(bad_file)

    def test_load_session_raises_on_missing_required_fields(self, tmp_path):
        """load_session raises SessionError if required fields are missing."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text(json.dumps({"id": "123"}))  # Missing core_id, status, etc.

        with pytest.raises(SessionError):
            SessionManager.load_session(bad_file)


class TestSessionStateUpdate:
    """Tests for updating session state."""

    def test_update_choices_adds_phase_choices(self, tmp_path):
        """update_choices adds choices for a phase."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity", "change": "change-accept"})
        state = session.get_state()

        assert state["choices"][4] == {"want": "want-dignity", "change": "change-accept"}

    def test_update_choices_merges_with_existing(self, tmp_path):
        """update_choices merges with existing choices for a phase."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity"})
        session.update_choices(4, {"change": "change-accept"})
        state = session.get_state()

        # Both should be present
        assert state["choices"][4]["want"] == "want-dignity"
        assert state["choices"][4]["change"] == "change-accept"

    def test_update_choices_overwrites_existing_field(self, tmp_path):
        """update_choices overwrites existing field values."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity"})
        session.update_choices(4, {"want": "want-prove-love"})
        state = session.get_state()

        # Should have the new value
        assert state["choices"][4]["want"] == "want-prove-love"

    def test_update_choices_persists_to_disk(self, tmp_path):
        """update_choices writes changes to disk."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity"})
        session.write_to_file()

        # Load from disk and verify
        session2 = SessionManager.load_session(project_path / "netorare" / "session.json")
        state2 = session2.get_state()
        assert state2["choices"][4]["want"] == "want-dignity"

    def test_update_choices_accepts_multiple_phases(self, tmp_path):
        """update_choices can be called for different phases."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity"})
        session.update_choices(5, {"theme": "theme-1"})
        session.update_choices(7, {"pacing": "pacing-accelerating"})
        state = session.get_state()

        assert 4 in state["choices"]
        assert 5 in state["choices"]
        assert 7 in state["choices"]


class TestSessionCompletion:
    """Tests for marking and checking session completion."""

    def test_mark_complete_changes_status(self, tmp_path):
        """mark_complete changes status to 'complete'."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.mark_complete()
        state = session.get_state()

        assert state["status"] == "complete"

    def test_is_complete_returns_false_initially(self, tmp_path):
        """is_complete returns False for new sessions."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "horror")

        assert not session.is_complete()

    def test_is_complete_returns_true_after_mark_complete(self, tmp_path):
        """is_complete returns True after mark_complete."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "mystery")
        session.mark_complete()

        assert session.is_complete()

    def test_mark_complete_persists_to_disk(self, tmp_path):
        """mark_complete writes status to disk."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.mark_complete()
        session.write_to_file()

        # Load from disk and verify
        session2 = SessionManager.load_session(project_path / "netorare" / "session.json")
        assert session2.is_complete()


class TestSessionGetChoices:
    """Tests for retrieving accumulated choices."""

    def test_get_choices_returns_all_choices(self, tmp_path):
        """get_choices returns all accumulated choices."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity", "change": "change-accept"})
        session.update_choices(5, {"theme": "theme-1"})

        choices = session.get_choices()

        assert 4 in choices
        assert 5 in choices
        assert choices[4]["want"] == "want-dignity"
        assert choices[5]["theme"] == "theme-1"

    def test_get_choices_returns_empty_dict_initially(self, tmp_path):
        """get_choices returns empty dict for new sessions."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "horror")
        choices = session.get_choices()

        assert choices == {}

    def test_get_choices_is_dict_type(self, tmp_path):
        """get_choices returns a dict."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "mystery")
        choices = session.get_choices()

        assert isinstance(choices, dict)


class TestSessionWriteToFile:
    """Tests for explicit write_to_file method."""

    def test_write_to_file_persists_current_state(self, tmp_path):
        """write_to_file persists current state to disk."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity"})
        session.write_to_file()

        session_file = project_path / "netorare" / "session.json"
        with open(session_file) as f:
            data = json.load(f)

        # JSON converts integer keys to strings
        assert data["choices"]["4"]["want"] == "want-dignity"

    def test_write_to_file_overwrites_existing(self, tmp_path):
        """write_to_file overwrites existing session.json."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session1 = SessionManager.create_session(project_path, "classic_humiliation")
        session1.update_choices(4, {"want": "want-dignity"})
        session1.write_to_file()

        # Load and modify
        session2 = SessionManager.load_session(project_path / "netorare" / "session.json")
        session2.update_choices(4, {"want": "want-prove-love"})
        session2.write_to_file()

        # Verify the new value was written
        session3 = SessionManager.load_session(project_path / "netorare" / "session.json")
        state3 = session3.get_state()
        assert state3["choices"][4]["want"] == "want-prove-love"


class TestSessionEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_session_handles_empty_update(self, tmp_path):
        """update_choices with empty dict doesn't break."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {})  # Empty dict
        state = session.get_state()

        # Should have empty phase dict
        assert 4 in state["choices"]
        assert state["choices"][4] == {}

    def test_session_handles_string_keys_in_phases(self, tmp_path):
        """Session converts string keys to integers internally."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {"want": "want-dignity"})
        state = session.get_state()

        # Phase key should be int
        assert 4 in state["choices"]

    def test_session_preserves_choice_values_as_strings(self, tmp_path):
        """Session preserves choice values exactly as provided."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        session.update_choices(4, {
            "want": "want-dignity",
            "change": "change-accept",
            "nested": "value-with-dashes"
        })
        state = session.get_state()

        assert state["choices"][4]["want"] == "want-dignity"
        assert state["choices"][4]["nested"] == "value-with-dashes"

    def test_session_state_keys_are_immutable_after_get(self, tmp_path):
        """Modifications to returned state don't affect session (defensive copy)."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "classic_humiliation")
        state1 = session.get_state()
        state1["choices"][99] = {"hacked": "true"}

        state2 = session.get_state()
        assert 99 not in state2["choices"]  # Original session unaffected

    def test_multiple_sessions_in_same_project_error(self, tmp_path):
        """Creating a second session in the same project should raise."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session1 = SessionManager.create_session(project_path, "classic_humiliation")
        # Attempting to create another in the same project should error
        with pytest.raises(SessionError):
            session2 = SessionManager.create_session(project_path, "horror")


class TestSessionIntegration:
    """Integration tests for full session workflow."""

    def test_full_session_workflow(self, tmp_path):
        """Complete workflow: create → update choices → complete → reload."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        # 1. Create session
        session = SessionManager.create_session(project_path, "classic_humiliation")
        session_id = session.get_state()["id"]

        # 2. Add choices across multiple phases
        session.update_choices(4, {
            "want": "want-dignity",
            "resistance": "resistance-inadequacy",
            "change": "change-accept"
        })
        session.update_choices(5, {"theme": "theme-1"})
        session.update_choices(7, {"pacing": "pacing-accelerating"})

        # 3. Mark complete
        session.mark_complete()

        # 4. Persist
        session.write_to_file()

        # 5. Reload from disk
        session2 = SessionManager.load_session(project_path / "netorare" / "session.json")

        # 6. Verify all state
        state2 = session2.get_state()
        assert state2["id"] == session_id
        assert state2["core_id"] == "classic_humiliation"
        assert state2["status"] == "complete"
        assert state2["choices"][4]["want"] == "want-dignity"
        assert state2["choices"][5]["theme"] == "theme-1"
        assert state2["choices"][7]["pacing"] == "pacing-accelerating"

    def test_cli_creates_session_before_browser_launch(self, tmp_path):
        """Simulates CLI creating session for browser to read."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        # CLI creates session
        session = SessionManager.create_session(project_path, "horror")
        session.write_to_file()

        # Browser reads session.json
        session_json = project_path / "netorare" / "session.json"
        assert session_json.exists()

        # Browser can load it
        browser_session = SessionManager.load_session(session_json)
        assert browser_session.get_state()["core_id"] == "horror"

    def test_cli_polls_for_completion(self, tmp_path):
        """Simulates CLI polling is_complete() until browser finishes."""
        project_path = tmp_path / "project"
        project_path.mkdir()

        session = SessionManager.create_session(project_path, "mystery")

        # Simulate CLI polling
        assert not session.is_complete()

        # Simulate browser updating choices and marking complete
        session.update_choices(4, {"want": "want-truth", "change": "change-participant"})
        session.mark_complete()
        session.write_to_file()

        # CLI reloads and checks
        session_reloaded = SessionManager.load_session(project_path / "netorare" / "session.json")
        assert session_reloaded.is_complete()
        choices = session_reloaded.get_choices()
        assert choices[4]["want"] == "want-truth"
