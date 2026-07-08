"""File-based JSON session state management for netorare pipeline."""

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any


class SessionError(Exception):
    """Raised when session operations fail."""
    pass


class SessionManager:
    """Manages file-based JSON session state for netorare interactive authoring.

    Sessions persist user choices and track completion status. State is stored as
    human-readable JSON for inspection and debugging.

    Typical workflow:
        1. CLI creates session: SessionManager.create_session(project_path, core_id)
        2. Browser reads session.json, updates choices
        3. Browser marks session complete
        4. CLI polls is_complete() and reads final choices

    Session state structure:
        {
            "id": "uuid-string",
            "core_id": "classic_humiliation|horror|mystery",
            "choices": {
                4: {"want": "...", "change": "...", ...},
                5: {"theme": "...", ...},
                ...
            },
            "status": "incomplete|complete",
            "timestamp": "2024-07-07T12:34:56.789012"
        }
    """

    def __init__(self, session_path: Path):
        """Initialize SessionManager with a session directory path.

        Args:
            session_path: Path to the netorare session directory (contains session.json)
        """
        self.session_path = Path(session_path)
        self.session_file = self.session_path / "session.json"
        self._state: Dict[str, Any] = {}

    @staticmethod
    def create_session(project_path: Path, core_id: str) -> "SessionManager":
        """Create a new session in the project's netorare directory.

        Creates project_path/netorare/ directory if needed, initializes session.json
        with a unique ID and empty choices.

        Args:
            project_path: Path to the project root
            core_id: Core template ID: "classic_humiliation", "horror", or "mystery"

        Returns:
            SessionManager instance for the new session

        Raises:
            SessionError: If session already exists in this project
        """
        netorare_path = Path(project_path) / "netorare"

        # Check if session already exists
        if netorare_path.exists() and (netorare_path / "session.json").exists():
            raise SessionError(
                f"Session already exists at {netorare_path / 'session.json'}. "
                "Only one active session per project is allowed."
            )

        # Create directory
        netorare_path.mkdir(parents=True, exist_ok=True)

        # Create session manager
        manager = SessionManager(netorare_path)

        # Initialize state
        manager._state = {
            "id": str(uuid.uuid4()),
            "core_id": core_id,
            "choices": {},
            "status": "incomplete",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Write to disk
        manager.write_to_file()

        return manager

    @staticmethod
    def load_session(session_file_path: Path) -> "SessionManager":
        """Load an existing session from session.json.

        Args:
            session_file_path: Path to session.json file

        Returns:
            SessionManager instance with loaded state

        Raises:
            SessionError: If file doesn't exist, is corrupted, or missing required fields
        """
        session_file = Path(session_file_path)

        # Check file exists
        if not session_file.exists():
            raise SessionError(f"Session file not found: {session_file}")

        # Parse JSON
        try:
            with open(session_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SessionError(f"Session file is corrupted (invalid JSON): {e}")

        # Validate required fields
        required_fields = {"id", "core_id", "choices", "status", "timestamp"}
        if not required_fields.issubset(data.keys()):
            missing = required_fields - set(data.keys())
            raise SessionError(f"Session file missing required fields: {missing}")

        # Create manager
        manager = SessionManager(session_file.parent)
        manager._state = data

        # Convert choice keys to integers if they're strings
        if manager._state.get("choices"):
            choices_dict = {}
            for key, value in manager._state["choices"].items():
                # JSON always deserializes dict keys as strings; convert back to int
                try:
                    int_key = int(key)
                    choices_dict[int_key] = value
                except (ValueError, TypeError):
                    # If key can't be converted to int, keep as string
                    choices_dict[key] = value
            manager._state["choices"] = choices_dict

        return manager

    def get_state(self) -> Dict[str, Any]:
        """Get the current session state.

        Returns a defensive copy to prevent accidental modifications.

        Returns:
            Dict with keys: id, core_id, choices, status, timestamp
        """
        # Return a defensive copy
        return {
            "id": self._state["id"],
            "core_id": self._state["core_id"],
            "choices": dict(self._state["choices"]),  # Shallow copy of choices dict
            "status": self._state["status"],
            "timestamp": self._state["timestamp"]
        }

    def update_choices(self, phase: int, choices: Dict[str, str]) -> None:
        """Update choices for a specific phase.

        Merges with existing choices for the phase (overwrites conflicting keys).

        Args:
            phase: Phase number (typically 1-9)
            choices: Dict mapping field names to choice values
        """
        if phase not in self._state["choices"]:
            self._state["choices"][phase] = {}

        self._state["choices"][phase].update(choices)

    def mark_complete(self) -> None:
        """Mark the session as complete.

        Does not automatically persist to disk; call write_to_file() to save.
        """
        self._state["status"] = "complete"

    def is_complete(self) -> bool:
        """Check if the session is marked complete.

        Returns:
            True if status is "complete", False otherwise
        """
        return self._state.get("status") == "complete"

    def get_choices(self) -> Dict[int, Dict[str, str]]:
        """Get all accumulated choices across all phases.

        Returns a defensive copy.

        Returns:
            Dict mapping phase (int) to choices dict
        """
        return dict(self._state["choices"])

    def write_to_file(self) -> None:
        """Persist current state to session.json.

        Ensures directory exists and writes indented JSON for readability.

        Raises:
            SessionError: If write fails
        """
        try:
            self.session_path.mkdir(parents=True, exist_ok=True)

            with open(self.session_file, "w") as f:
                # Convert integer keys to strings for JSON serialization
                state_to_write = dict(self._state)
                choices_for_json = {}
                for phase, phase_choices in self._state["choices"].items():
                    choices_for_json[str(phase)] = phase_choices
                state_to_write["choices"] = choices_for_json

                json.dump(state_to_write, f, indent=2)
        except Exception as e:
            raise SessionError(f"Failed to write session to {self.session_file}: {e}")
