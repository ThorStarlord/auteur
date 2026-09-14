"""Durable working-state persistence for the Beginner Workspace slice."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .contracts import SessionEnvelope


class BeginnerPersistenceError(RuntimeError):
    """Raised when a Beginner Workspace artifact cannot be read or written."""


class BeginnerConcurrencyError(BeginnerPersistenceError):
    """Raised when a mutation was based on an obsolete session version."""


class CommandReceipt(BaseModel):
    """A durable record of a command's in-progress or completed execution."""

    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(min_length=1)
    status: Literal["in_progress", "complete"]
    result: Any = None


def _atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    except OSError as exc:
        raise BeginnerPersistenceError(f"atomic write failed for {path}: {exc}") from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


class BeginnerSessionStore:
    """Store the mutable session and immutable revision-session snapshots."""

    def __init__(self, project_root: Path, workspace_id: str) -> None:
        self.workspace_root = Path(project_root)
        self.workspace_id = workspace_id
        self.session_path = self.workspace_root / ".auteur" / "beginner" / "workspaces" / workspace_id / "session.json"

    def revision_session_path(self, revision_id: str) -> Path:
        return self.session_path.parent / "revisions" / revision_id / "session.json"

    def load(self) -> SessionEnvelope:
        try:
            payload = self.session_path.read_text(encoding="utf-8")
            return SessionEnvelope.model_validate_json(payload)
        except (OSError, ValueError, ValidationError) as exc:
            raise BeginnerPersistenceError(f"could not load session from {self.session_path}: {exc}") from exc

    def save(self, session: SessionEnvelope) -> SessionEnvelope:
        saved = session.model_copy(update={"session_version": session.session_version + 1})
        _atomic_write(self.session_path, saved.model_dump_json())
        return saved

    def update(self, expected_session_version: int, mutator: Callable[[SessionEnvelope], SessionEnvelope]) -> SessionEnvelope:
        current = self.load()
        if current.session_version != expected_session_version:
            raise BeginnerConcurrencyError(
                f"session version mismatch: expected {expected_session_version}, found {current.session_version}"
            )
        updated = mutator(current)
        return self.save(updated)


class CommandReceiptStore:
    """Persist command execution receipts for replay and crash recovery."""

    def __init__(self, project_root: Path, workspace_id: str) -> None:
        self.workspace_root = Path(project_root)
        self.workspace_id = workspace_id
        self.receipts_path = (
            self.workspace_root / ".auteur" / "beginner" / "workspaces" / workspace_id / "commands"
        )

    def receipt_path(self, command_id: str) -> Path:
        return self.receipts_path / f"{command_id}.json"

    def load(self, command_id: str) -> CommandReceipt:
        path = self.receipt_path(command_id)
        try:
            return CommandReceipt.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, ValidationError) as exc:
            raise BeginnerPersistenceError(f"could not load command receipt from {path}: {exc}") from exc

    def begin(self, command_id: str) -> CommandReceipt:
        path = self.receipt_path(command_id)
        if path.exists():
            return self.load(command_id)
        receipt = CommandReceipt(command_id=command_id, status="in_progress")
        _atomic_write(path, receipt.model_dump_json())
        return receipt

    def complete(self, receipt_or_command_id: CommandReceipt | str, result: Any) -> CommandReceipt:
        command_id = receipt_or_command_id.command_id if isinstance(receipt_or_command_id, CommandReceipt) else receipt_or_command_id
        path = self.receipt_path(command_id)
        if path.exists():
            existing = self.load(command_id)
            if existing.status == "complete":
                return existing
        completed = CommandReceipt(command_id=command_id, status="complete", result=result)
        _atomic_write(path, completed.model_dump_json())
        return completed

    def replay(self, command_id: str) -> Any | None:
        receipt = self.load(command_id)
        return receipt.result if receipt.status == "complete" else None
