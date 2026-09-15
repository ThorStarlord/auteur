"""Durable working-state persistence for the Beginner Workspace slice."""

from __future__ import annotations

import errno
import json
import os
import re
import secrets
import tempfile
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO, Callable, Literal, TypeAlias, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from pydantic_core import PydanticSerializationError
from typing_extensions import TypeAliasType

from .contracts import SessionEnvelope

if os.name == "nt":
    import msvcrt
else:
    import fcntl  # type: ignore[import-not-found]


class BeginnerPersistenceError(RuntimeError):
    """Raised when a Beginner Workspace artifact cannot be read or written."""


class BeginnerConcurrencyError(BeginnerPersistenceError):
    """Raised when a mutation was based on an obsolete session version."""


class _BeginnerLockTimeout(BeginnerPersistenceError):
    """Internal signal for a bounded advisory-lock wait."""


class BeginnerReceiptOwnershipError(BeginnerConcurrencyError):
    """Raised when a command receipt is completed by a non-owner."""


if TYPE_CHECKING:
    JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
else:
    JsonValue = TypeAliasType(
        "JsonValue", None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
    )
JsonObject: TypeAlias = dict[str, JsonValue]


def _normalize_json_value(value: JsonValue, label: str) -> JsonValue:
    _validate_json_value(value, label)
    try:
        return cast(JsonValue, json.loads(json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":"))))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{label} must be JSON-compatible") from exc


def _validate_json_value(value: object, label: str) -> None:
    if value is None or type(value) in {bool, int, float, str}:
        return
    if type(value) is list:
        for item in cast(list[object], value):
            _validate_json_value(item, label)
        return
    if type(value) is dict:
        for key, item in cast(dict[object, object], value).items():
            if type(key) is not str:
                raise ValueError(f"{label} must be JSON-compatible")
            _validate_json_value(item, label)
        return
    raise ValueError(f"{label} must be JSON-compatible")


class CommandReceipt(BaseModel):
    """A durable record of a command's in-progress or completed execution."""

    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(min_length=1)
    status: Literal["in_progress", "complete"]
    result: JsonValue = None
    owner_token: str | None = Field(default=None, min_length=1)
    command_type: str = Field(default="unknown", min_length=1)
    target_milestone: str | None = Field(default=None, min_length=1)
    promotion_intent: JsonObject | None = None
    domain_result_reference: JsonObject | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_raw_json_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for field_name, label in (
                ("result", "receipt result"),
                ("promotion_intent", "promotion intent"),
                ("domain_result_reference", "domain result reference"),
            ):
                if field_name in data and data[field_name] is not None:
                    _validate_json_value(data[field_name], label)
        return data

    @model_validator(mode="after")
    def validate_durable_state(self) -> CommandReceipt:
        self.result = _normalize_json_value(self.result, "receipt result") if self.result is not None else None
        self.promotion_intent = (
            cast(JsonObject, _normalize_json_value(self.promotion_intent, "promotion intent"))
            if self.promotion_intent is not None
            else None
        )
        self.domain_result_reference = (
            cast(JsonObject, _normalize_json_value(self.domain_result_reference, "domain result reference"))
            if self.domain_result_reference is not None
            else None
        )
        if self.status == "in_progress":
            if self.owner_token is None:
                raise ValueError("in_progress receipt must have an owner_token")
            if self.result is not None:
                raise ValueError("in_progress receipt must not have a result")
        elif self.owner_token is None:
            raise ValueError("complete receipt must have an owner_token")
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CommandReceipt):
            return NotImplemented
        return self.model_dump() == other.model_dump()


class ReceiptAcquisition(BaseModel):
    """Validated result of attempting to claim a command receipt."""

    model_config = ConfigDict(extra="forbid")

    command_id: str = Field(min_length=1)
    status: Literal["in_progress", "complete"]
    outcome: Literal["owner_claim", "existing_in_progress", "completed_replay"]
    owner_token: str | None = Field(default=None, min_length=1)
    result: JsonValue = None
    command_type: str = Field(default="unknown", min_length=1)
    target_milestone: str | None = Field(default=None, min_length=1)
    promotion_intent: JsonObject | None = None
    domain_result_reference: JsonObject | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_raw_json_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for field_name, label in (
                ("result", "acquisition result"),
                ("promotion_intent", "promotion intent"),
                ("domain_result_reference", "domain result reference"),
            ):
                if field_name in data and data[field_name] is not None:
                    _validate_json_value(data[field_name], label)
        return data

    @model_validator(mode="after")
    def validate_acquisition(self) -> ReceiptAcquisition:
        self.result = _normalize_json_value(self.result, "acquisition result") if self.result is not None else None
        self.promotion_intent = (
            cast(JsonObject, _normalize_json_value(self.promotion_intent, "promotion intent"))
            if self.promotion_intent is not None
            else None
        )
        self.domain_result_reference = (
            cast(JsonObject, _normalize_json_value(self.domain_result_reference, "domain result reference"))
            if self.domain_result_reference is not None
            else None
        )
        if self.outcome == "owner_claim":
            if self.status != "in_progress" or self.owner_token is None or self.result is not None:
                raise ValueError("owner_claim must be an in-progress claim with a token and no result")
        elif self.outcome == "existing_in_progress":
            if self.status != "in_progress" or self.owner_token is not None or self.result is not None:
                raise ValueError("existing_in_progress must have no token or result")
        elif self.status != "complete" or self.owner_token is not None:
            raise ValueError("completed_replay must be complete and expose no owner token")
        return self

    @property
    def acquired(self) -> bool:
        return self.outcome == "owner_claim"

_SAFE_SEGMENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
_WINDOWS_DEVICE_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{index}" for index in range(1, 10)), *(f"LPT{index}" for index in range(1, 10))}


def _safe_segment(value: str, label: str) -> str:
    if not isinstance(value, str) or _SAFE_SEGMENT.fullmatch(value) is None:
        raise ValueError(f"{label} must be a safe single path segment")
    if value.split(".", 1)[0].upper() in _WINDOWS_DEVICE_NAMES:
        raise ValueError(f"{label} must not be a Windows reserved device name")
    if value != value.lower():
        raise BeginnerPersistenceError(f"{label} must use canonical lowercase form")
    return value


def _contained_path(root: Path, *parts: str, containment_root: Path | None = None) -> Path:
    resolved_root = root.resolve()
    resolved_containment_root = containment_root.resolve() if containment_root is not None else None
    try:
        if resolved_root != root.absolute():
            raise ValueError("root is redirected")
        if resolved_containment_root is not None:
            resolved_root.relative_to(resolved_containment_root)
        candidate = (resolved_root / Path(*parts)).resolve()
        candidate.relative_to(resolved_root)
        if resolved_containment_root is not None:
            candidate.relative_to(resolved_containment_root)
    except ValueError as exc:
        raise ValueError(f"resolved path escapes intended root {root}") from exc
    return candidate


def _serialize_receipt(receipt: CommandReceipt) -> str:
    try:
        return receipt.model_dump_json()
    except (TypeError, ValueError, PydanticSerializationError) as exc:
        raise BeginnerPersistenceError(f"could not serialize command receipt: {exc}") from exc


def _validate_session(session: SessionEnvelope) -> SessionEnvelope:
    try:
        return SessionEnvelope.model_validate(session.model_dump(mode="python"), strict=True)
    except ValidationError as exc:
        raise BeginnerPersistenceError(f"invalid session envelope: {exc}") from exc


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


_SESSION_LOCK_TIMEOUT = 10.0


class _FilesystemLock:
    def __init__(self, path: Path, timeout: float | None = None) -> None:
        self.path = path
        self.timeout = _SESSION_LOCK_TIMEOUT if timeout is None else timeout
        self._file: BinaryIO | None = None

    def __enter__(self) -> _FilesystemLock:
        deadline = time.monotonic() + self.timeout
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise BeginnerPersistenceError(f"could not acquire session lock {self.path}: {exc}") from exc

        while True:
            try:
                self._file = self.path.open("a+b")
                file = self._file
                if file.tell() == 0:
                    file.write(b"\0")
                    file.flush()
                try:
                    file.seek(0)
                    if os.name == "nt":
                        msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[attr-defined]
                    return self
                except OSError as exc:
                    raise exc
            except OSError as exc:
                self._close_file()
                if not _is_lock_contention(exc):
                    raise BeginnerPersistenceError(f"could not acquire session lock {self.path}: {exc}") from exc
                if time.monotonic() >= deadline:
                    raise _BeginnerLockTimeout(f"timed out acquiring session lock {self.path}")
                time.sleep(0.005)

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        if self._file is not None:
            file = self._file
            try:
                file.seek(0)
                if os.name == "nt":
                    msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(file.fileno(), fcntl.LOCK_UN)  # type: ignore[attr-defined]
            finally:
                self._close_file()

    def _close_file(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None


def _is_lock_contention(exc: OSError) -> bool:
    return exc.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}


class BeginnerSessionStore:
    """Store the mutable session and immutable revision-session snapshots."""

    def __init__(self, project_root: Path, workspace_id: str) -> None:
        self.workspace_root = Path(project_root).resolve()
        self.workspace_id = _safe_segment(workspace_id, "workspace_id")
        workspace_root = _contained_path(
            self.workspace_root / ".auteur" / "beginner" / "workspaces",
            self.workspace_id,
            containment_root=self.workspace_root,
        )
        self._workspace_path = workspace_root
        self.session_path = _contained_path(workspace_root, "session.json", containment_root=workspace_root)
        self._session_lock = _contained_path(workspace_root, ".session.lock", containment_root=workspace_root)
        self._instance_lock = threading.RLock()

    def _session_path_for_io(self) -> Path:
        return _contained_path(self._workspace_path, "session.json", containment_root=self._workspace_path)

    def _session_lock_for_io(self) -> Path:
        return _contained_path(self._workspace_path, ".session.lock", containment_root=self._workspace_path)

    def revision_session_path(self, revision_id: str) -> Path:
        revision = _safe_segment(revision_id, "revision_id")
        return _contained_path(
            self._workspace_path / "revisions", revision, "session.json", containment_root=self._workspace_path
        )

    def load(self) -> SessionEnvelope:
        return self._load_session(self._session_path_for_io())

    @staticmethod
    def _load_session(path: Path) -> SessionEnvelope:
        try:
            payload = path.read_text(encoding="utf-8")
            return SessionEnvelope.model_validate_json(payload, strict=True)
        except (OSError, ValueError, ValidationError) as exc:
            raise BeginnerPersistenceError(f"could not load session from {path}: {exc}") from exc

    def create(self, session: SessionEnvelope, expected_session_version: int | None = None) -> SessionEnvelope:
        validated = _validate_session(session)
        with self._instance_lock, _FilesystemLock(self._session_lock_for_io()):
            session_path = self._session_path_for_io()
            if expected_session_version not in (None, 0):
                raise BeginnerConcurrencyError(
                    f"cannot create session with expected version {expected_session_version}; initial version is 0"
                )
            if session_path.exists():
                raise BeginnerPersistenceError(f"session already exists at {session_path}")
            if validated.session_version != 0:
                raise BeginnerPersistenceError("initial session version must be 0")
            saved = validated.model_copy(update={"session_version": validated.session_version + 1})
            if not _atomic_create(session_path, saved.model_dump_json()):
                raise BeginnerPersistenceError(f"session already exists at {session_path}")
            return saved

    def save(self, session: SessionEnvelope, expected_session_version: int | None = None) -> SessionEnvelope:
        validated = _validate_session(session)
        with self._instance_lock, _FilesystemLock(self._session_lock_for_io()):
            session_path = self._session_path_for_io()
            if session_path.exists():
                current = self.load()
                if expected_session_version is None or current.session_version != expected_session_version:
                    raise BeginnerConcurrencyError(
                        f"session version mismatch: expected {expected_session_version}, found {current.session_version}"
                    )
                next_version = current.session_version + 1
            else:
                if expected_session_version not in (None, 0):
                    raise BeginnerConcurrencyError(
                        f"cannot create session with expected version {expected_session_version}; initial version is 0"
                    )
                if session.session_version != 0:
                    raise BeginnerPersistenceError("initial session version must be 0")
                next_version = validated.session_version + 1
            saved = SessionEnvelope.model_validate({**validated.model_dump(mode="python"), "session_version": next_version}, strict=True)
            if session_path.exists():
                _atomic_write(session_path, saved.model_dump_json())
            elif not _atomic_create(session_path, saved.model_dump_json()):
                raise BeginnerPersistenceError(f"session already exists at {session_path}")
            return saved

    def create_revision(self, revision_id: str, session: SessionEnvelope) -> SessionEnvelope:
        return self.save_revision(revision_id, session)

    def save_revision(self, revision_id: str, session: SessionEnvelope) -> SessionEnvelope:
        validated = _validate_session(session)
        path = self.revision_session_path(revision_id)
        if path.exists():
            raise BeginnerPersistenceError(f"revision already exists at {path}")
        if not _atomic_create(path, validated.model_dump_json()):
            raise BeginnerPersistenceError(f"revision already exists at {path}")
        return validated

    def load_revision(self, revision_id: str) -> SessionEnvelope:
        return self._load_session(self.revision_session_path(revision_id))

    def update(self, expected_session_version: int, mutator: Callable[[SessionEnvelope], SessionEnvelope]) -> SessionEnvelope:
        try:
            with self._instance_lock, _FilesystemLock(self._session_lock_for_io()):
                current = self.load()
                if current.session_version != expected_session_version:
                    raise BeginnerConcurrencyError(
                        f"session version mismatch: expected {expected_session_version}, found {current.session_version}"
                    )
                updated = mutator(current)
                normalized = updated.model_copy(update={"session_version": current.session_version})
                validated = _validate_session(normalized)
                next_version = current.session_version + 1
                persisted = validated.model_copy(update={"session_version": next_version})
                _atomic_write(self._session_path_for_io(), persisted.model_dump_json())
                return persisted
        except _BeginnerLockTimeout as exc:
            try:
                current = self.load()
            except BeginnerPersistenceError:
                raise exc
            if current.session_version != expected_session_version:
                raise BeginnerConcurrencyError(
                    f"session version mismatch: expected {expected_session_version}, found {current.session_version}"
                ) from exc
            raise exc


class CommandReceiptStore:
    """Persist command execution receipts for replay and crash recovery."""

    def __init__(self, project_root: Path, workspace_id: str) -> None:
        self.workspace_root = Path(project_root).resolve()
        self.workspace_id = _safe_segment(workspace_id, "workspace_id")
        workspace_root = _contained_path(
            self.workspace_root / ".auteur" / "beginner" / "workspaces",
            self.workspace_id,
            containment_root=self.workspace_root,
        )
        self.receipts_path = _contained_path(workspace_root, "commands", containment_root=workspace_root)

    def receipt_path(self, command_id: str) -> Path:
        command = _safe_segment(command_id, "command_id")
        return _contained_path(self.receipts_path, f"{command}.json", containment_root=self.receipts_path.parent)

    def load(self, command_id: str) -> CommandReceipt:
        path = self.receipt_path(command_id)
        try:
            receipt = CommandReceipt.model_validate_json(path.read_text(encoding="utf-8"), strict=True)
            if receipt.command_id != command_id:
                raise BeginnerPersistenceError(
                    f"receipt command_id {receipt.command_id!r} does not match requested command_id {command_id!r}"
                )
            return receipt
        except (OSError, ValueError, ValidationError) as exc:
            raise BeginnerPersistenceError(f"could not load command receipt from {path}: {exc}") from exc

    def begin(
        self,
        command_id: str,
        command_type: str | None = None,
        target_milestone: str | None = None,
        promotion_intent: JsonObject | None = None,
        domain_result_reference: JsonObject | None = None,
    ) -> ReceiptAcquisition:
        path = self.receipt_path(command_id)
        receipt = CommandReceipt(
            command_id=command_id,
            status="in_progress",
            owner_token=secrets.token_urlsafe(32),
            command_type=command_type if command_type is not None else "unknown",
            target_milestone=target_milestone,
            promotion_intent=promotion_intent,
            domain_result_reference=domain_result_reference,
        )
        if _atomic_create(path, _serialize_receipt(receipt)):
            return ReceiptAcquisition(
                command_id=command_id,
                status="in_progress",
                outcome="owner_claim",
                owner_token=receipt.owner_token,
                command_type=receipt.command_type,
                target_milestone=receipt.target_milestone,
                promotion_intent=receipt.promotion_intent,
                domain_result_reference=receipt.domain_result_reference,
            )
        existing = self.load(command_id)
        if (
            existing.command_type != receipt.command_type
            or existing.target_milestone != receipt.target_milestone
            or existing.promotion_intent != receipt.promotion_intent
            or (
                existing.status == "in_progress"
                and existing.domain_result_reference != receipt.domain_result_reference
            )
        ):
            raise BeginnerPersistenceError(f"command intent conflict for existing command_id {command_id}")
        if existing.status == "complete":
            return ReceiptAcquisition(
                command_id=command_id,
                status="complete",
                outcome="completed_replay",
                result=existing.result,
                command_type=existing.command_type,
                target_milestone=existing.target_milestone,
                promotion_intent=existing.promotion_intent,
                domain_result_reference=existing.domain_result_reference,
            )
        return ReceiptAcquisition(
            command_id=command_id,
            status="in_progress",
            outcome="existing_in_progress",
            command_type=existing.command_type,
            target_milestone=existing.target_milestone,
            promotion_intent=existing.promotion_intent,
            domain_result_reference=existing.domain_result_reference,
        )

    def complete(
        self,
        receipt: CommandReceipt | ReceiptAcquisition,
        result: JsonValue,
        domain_result_reference: JsonObject | None = None,
    ) -> CommandReceipt:
        if isinstance(receipt, ReceiptAcquisition):
            if receipt.outcome == "completed_replay":
                owner_token = None
            elif receipt.outcome == "owner_claim":
                owner_token = receipt.owner_token
            else:
                raise BeginnerReceiptOwnershipError("only an owner claim can complete an in-progress receipt")
        else:
            owner_token = receipt.owner_token
        if owner_token is None and not (
            isinstance(receipt, ReceiptAcquisition) and receipt.outcome == "completed_replay"
        ):
            raise BeginnerReceiptOwnershipError("receipt owner token is required")
        command_id = receipt.command_id
        path = self.receipt_path(command_id)
        with _FilesystemLock(path.with_name(f".{path.name}.lock")):
            if not path.exists():
                raise BeginnerPersistenceError(f"command was never begun: {command_id}")
            existing = self.load(command_id)
            if existing.status == "complete":
                return existing
            if existing.owner_token != owner_token:
                raise BeginnerReceiptOwnershipError("receipt owner token does not match")
            try:
                completed = CommandReceipt(
                    command_id=command_id,
                    status="complete",
                    result=result,
                    owner_token=existing.owner_token,
                    command_type=existing.command_type,
                    target_milestone=existing.target_milestone,
                    promotion_intent=existing.promotion_intent,
                    domain_result_reference=(
                        domain_result_reference
                        if domain_result_reference is not None
                        else existing.domain_result_reference
                    ),
                )
            except ValidationError as exc:
                raise BeginnerPersistenceError(f"could not normalize receipt completion: {exc}") from exc
            _atomic_write(path, _serialize_receipt(completed))
            return completed

    def replay(self, command_id: str) -> ReceiptAcquisition | None:
        receipt = self.load(command_id)
        if receipt.status != "complete":
            return None
        return ReceiptAcquisition(
            command_id=command_id,
            status="complete",
            outcome="completed_replay",
            result=receipt.result,
            command_type=receipt.command_type,
            target_milestone=receipt.target_milestone,
            promotion_intent=receipt.promotion_intent,
            domain_result_reference=receipt.domain_result_reference,
        )
