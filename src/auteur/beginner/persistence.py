"""Durable working-state persistence for the Beginner Workspace slice."""

from __future__ import annotations

import os
import re
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_core import PydanticSerializationError

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
    acquisition_outcome: Literal["new_owner", "existing_in_progress", "existing_completed"] = Field(
        default="new_owner", exclude=True
    )

    @property
    def acquired(self) -> bool:
        return self.acquisition_outcome == "new_owner"

    @property
    def outcome(self) -> str:
        return self.acquisition_outcome

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CommandReceipt):
            return NotImplemented
        return self.model_dump() == other.model_dump()


_SAFE_SEGMENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")


def _safe_segment(value: str, label: str) -> str:
    if not isinstance(value, str) or _SAFE_SEGMENT.fullmatch(value) is None:
        raise ValueError(f"{label} must be a safe single path segment")
    return value


def _contained_path(root: Path, *parts: str) -> Path:
    candidate = (root / Path(*parts)).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"resolved path escapes intended root {root}") from exc
    return candidate


def _serialize_receipt(receipt: CommandReceipt) -> str:
    try:
        return receipt.model_dump_json()
    except (TypeError, ValueError, PydanticSerializationError) as exc:
        raise BeginnerPersistenceError(f"could not serialize command receipt: {exc}") from exc


def _atomic_write(path: Path, payload: str) -> None:
    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
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


def _atomic_create(path: Path, payload: str) -> bool:
    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
        try:
            os.link(temporary_path, path)
        except FileExistsError:
            return False
        return True
    except OSError as exc:
        raise BeginnerPersistenceError(f"atomic create failed for {path}: {exc}") from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


class _FilesystemLock:
    def __init__(self, path: Path, timeout: float = 10.0) -> None:
        self.path = path
        self.timeout = timeout
        self._file_descriptor: int | None = None

    def __enter__(self) -> _FilesystemLock:
        deadline = time.monotonic() + self.timeout
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            while True:
                try:
                    self._file_descriptor = os.open(
                        self.path,
                        os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    )
                    return self
                except FileExistsError:
                    if time.monotonic() >= deadline:
                        raise BeginnerPersistenceError(f"timed out acquiring session lock {self.path}")
                    time.sleep(0.005)
        except BeginnerPersistenceError:
            raise
        except OSError as exc:
            raise BeginnerPersistenceError(f"could not acquire session lock {self.path}: {exc}") from exc

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        if self._file_descriptor is not None:
            os.close(self._file_descriptor)
            self._file_descriptor = None
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise BeginnerPersistenceError(f"could not release session lock {self.path}: {exc}") from exc


class BeginnerSessionStore:
    """Store the mutable session and immutable revision-session snapshots."""

    def __init__(self, project_root: Path, workspace_id: str) -> None:
        self.workspace_root = Path(project_root)
        self.workspace_id = _safe_segment(workspace_id, "workspace_id")
        workspace_root = _contained_path(self.workspace_root / ".auteur" / "beginner" / "workspaces", self.workspace_id)
        self._workspace_path = workspace_root
        self.session_path = _contained_path(workspace_root, "session.json")
        self._session_lock = _contained_path(workspace_root, ".session.lock")
        self._instance_lock = threading.RLock()

    def revision_session_path(self, revision_id: str) -> Path:
        revision = _safe_segment(revision_id, "revision_id")
        return _contained_path(self._workspace_path / "revisions", revision, "session.json")

    def load(self) -> SessionEnvelope:
        return self._load_session(self.session_path)

    @staticmethod
    def _load_session(path: Path) -> SessionEnvelope:
        try:
            payload = path.read_text(encoding="utf-8")
            return SessionEnvelope.model_validate_json(payload, strict=True)
        except (OSError, ValueError, ValidationError) as exc:
            raise BeginnerPersistenceError(f"could not load session from {path}: {exc}") from exc

    def create(self, session: SessionEnvelope) -> SessionEnvelope:
        with self._instance_lock, _FilesystemLock(self._session_lock):
            if self.session_path.exists():
                raise BeginnerPersistenceError(f"session already exists at {self.session_path}")
            saved = session.model_copy(update={"session_version": session.session_version + 1})
            if not _atomic_create(self.session_path, saved.model_dump_json()):
                raise BeginnerPersistenceError(f"session already exists at {self.session_path}")
            return saved

    def save(self, session: SessionEnvelope, expected_session_version: int | None = None) -> SessionEnvelope:
        with self._instance_lock, _FilesystemLock(self._session_lock):
            if self.session_path.exists():
                current = self.load()
                if expected_session_version is None or current.session_version != expected_session_version:
                    raise BeginnerConcurrencyError(
                        f"session version mismatch: expected {expected_session_version}, found {current.session_version}"
                    )
                next_version = current.session_version + 1
            else:
                next_version = session.session_version + 1
            saved = SessionEnvelope.model_validate({**session.model_dump(mode="python"), "session_version": next_version})
            if self.session_path.exists():
                _atomic_write(self.session_path, saved.model_dump_json())
            elif not _atomic_create(self.session_path, saved.model_dump_json()):
                raise BeginnerPersistenceError(f"session already exists at {self.session_path}")
            return saved

    def create_revision(self, revision_id: str, session: SessionEnvelope) -> SessionEnvelope:
        return self.save_revision(revision_id, session)

    def save_revision(self, revision_id: str, session: SessionEnvelope) -> SessionEnvelope:
        path = self.revision_session_path(revision_id)
        if path.exists():
            raise BeginnerPersistenceError(f"revision already exists at {path}")
        if not _atomic_create(path, session.model_dump_json()):
            raise BeginnerPersistenceError(f"revision already exists at {path}")
        return session

    def load_revision(self, revision_id: str) -> SessionEnvelope:
        return self._load_session(self.revision_session_path(revision_id))

    def update(self, expected_session_version: int, mutator: Callable[[SessionEnvelope], SessionEnvelope]) -> SessionEnvelope:
        with self._instance_lock, _FilesystemLock(self._session_lock):
            current = self.load()
            if current.session_version != expected_session_version:
                raise BeginnerConcurrencyError(
                    f"session version mismatch: expected {expected_session_version}, found {current.session_version}"
                )
            updated = mutator(current)
            next_version = current.session_version + 1
            persisted = SessionEnvelope.model_validate(
                {**updated.model_dump(mode="python"), "session_version": next_version}
            )
            _atomic_write(self.session_path, persisted.model_dump_json())
            return persisted


class CommandReceiptStore:
    """Persist command execution receipts for replay and crash recovery."""

    def __init__(self, project_root: Path, workspace_id: str) -> None:
        self.workspace_root = Path(project_root)
        self.workspace_id = _safe_segment(workspace_id, "workspace_id")
        workspace_root = _contained_path(self.workspace_root / ".auteur" / "beginner" / "workspaces", self.workspace_id)
        self.receipts_path = _contained_path(workspace_root, "commands")

    def receipt_path(self, command_id: str) -> Path:
        command = _safe_segment(command_id, "command_id")
        return _contained_path(self.receipts_path, f"{command}.json")

    def load(self, command_id: str) -> CommandReceipt:
        path = self.receipt_path(command_id)
        try:
            return CommandReceipt.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, ValidationError) as exc:
            raise BeginnerPersistenceError(f"could not load command receipt from {path}: {exc}") from exc

    def begin(self, command_id: str) -> CommandReceipt:
        path = self.receipt_path(command_id)
        receipt = CommandReceipt(command_id=command_id, status="in_progress")
        if _atomic_create(path, _serialize_receipt(receipt)):
            return receipt
        existing = self.load(command_id)
        outcome = "existing_completed" if existing.status == "complete" else "existing_in_progress"
        return existing.model_copy(update={"acquisition_outcome": outcome})

    def complete(self, receipt_or_command_id: CommandReceipt | str, result: Any) -> CommandReceipt:
        command_id = receipt_or_command_id.command_id if isinstance(receipt_or_command_id, CommandReceipt) else receipt_or_command_id
        path = self.receipt_path(command_id)
        if path.exists():
            existing = self.load(command_id)
            if existing.status == "complete":
                return existing
        completed = CommandReceipt(command_id=command_id, status="complete", result=result)
        _atomic_write(path, _serialize_receipt(completed))
        return completed

    def replay(self, command_id: str) -> Any | None:
        receipt = self.load(command_id)
        return receipt.result if receipt.status == "complete" else None
