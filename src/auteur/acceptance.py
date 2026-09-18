"""Typed routing seam for authority-bearing artifact acceptance."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


class AcceptanceOwner(Protocol):
    """Artifact owner capable of accepting one of its candidates."""

    def can_accept(self, target_artifact_id: str) -> bool: ...

    def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> Any: ...

    def recover(self, target_artifact_id: str, candidate_id: str) -> Any | None: ...


class AcceptanceJournal:
    """Durable intent/completion journal for authority-bearing operations."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.path = Path(project_root).resolve() / ".auteur" / "acceptance" / "journal.json" if project_root else None
        self._records: list[dict[str, Any]] = []
        if self.path and self.path.exists():
            self._records = json.loads(self.path.read_text(encoding="utf-8"))

    def record(
        self,
        *,
        operation_id: str,
        target_artifact_id: str,
        candidate_id: str,
        status: str,
        error: str = "",
        command_id: str | None = None,
        result: Any = None,
    ) -> None:
        self._records.append({
            "operation_id": operation_id,
            "target_artifact_id": target_artifact_id,
            "candidate_id": candidate_id,
            "status": status,
            "error": error,
            "command_id": command_id,
            "result": _journal_result(result, operation_id),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self._records, indent=2), encoding="utf-8")
            temporary.replace(self.path)

    def history(self) -> list[dict[str, Any]]:
        return list(self._records)

    def recoverable(self) -> list[dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        for record in self._records:
            latest[record["operation_id"]] = record
        return [record for record in latest.values() if record["status"] in {"started", "failed"}]

    def recovery_report(self) -> dict[str, Any]:
        """Return explicit, non-mutating recovery state for interrupted work.

        Recovery is intentionally report-only. Replaying an acceptance without
        an owner-specific idempotency contract could duplicate a canonical
        mutation, so callers must inspect the operation and resolve it through
        the owning artifact workflow.
        """
        pending = self.recoverable()
        return {
            "status": "recovery_required" if pending else "clean",
            "operations": pending,
            "replay_allowed": False,
        }

    def find_completed(self, command_id: str) -> dict[str, Any] | None:
        """Return the latest completed record for an idempotency command, if any.

        Records written before the command_id seam existed carry
        ``command_id=None`` and never match, so legacy behavior is unchanged.
        """
        match: dict[str, Any] | None = None
        for record in self._records:
            if record.get("command_id") == command_id and record.get("status") == "completed":
                match = record
        return dict(match) if match is not None else None

    def find_started(self, command_id: str, target_artifact_id: str, candidate_id: str) -> dict[str, Any] | None:
        match: dict[str, Any] | None = None
        for record in self._records:
            if (
                record.get("command_id") == command_id
                and record.get("target_artifact_id") == target_artifact_id
                and record.get("candidate_id") == candidate_id
                and record.get("status") == "started"
            ):
                match = record
        return dict(match) if match is not None else None


def _journal_result(result: Any, operation_id: str) -> Any:
    """Normalize an idempotency-scoped result to a JSON-safe journal value."""
    if result is None:
        return None
    try:
        return json.loads(json.dumps(result, allow_nan=False, sort_keys=True, separators=(",", ":")))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"command-scoped acceptance result must be JSON-compatible: {operation_id}") from exc


class AcceptanceRegistry:
    """Resolve exactly one canonical acceptance owner for a target."""

    def __init__(self, project_root: Path | None = None) -> None:
        self._owners: list[AcceptanceOwner] = []
        self.journal = AcceptanceJournal(project_root)

    def register(self, owner: AcceptanceOwner) -> None:
        self._owners.append(owner)

    def accept(
        self,
        target_artifact_id: str,
        candidate_id: str,
        *,
        confirm: bool,
        command_id: str | None = None,
    ) -> Any:
        matches = [owner for owner in self._owners if owner.can_accept(target_artifact_id)]
        if not matches:
            raise ValueError(f"No acceptance owner registered for artifact: {target_artifact_id}")
        if len(matches) > 1:
            raise ValueError(f"Multiple acceptance owners registered for artifact: {target_artifact_id}")
        if command_id is not None:
            replayed = self.journal.find_completed(command_id)
            if (
                replayed is not None
                and replayed.get("target_artifact_id") == target_artifact_id
                and replayed.get("candidate_id") == candidate_id
            ):
                return replayed.get("result")
            started = self.journal.find_started(command_id, target_artifact_id, candidate_id)
            if started is not None:
                recover = getattr(matches[0], "recover", None)
                if callable(recover):
                    recovered = recover(target_artifact_id, candidate_id)
                    if recovered is not None:
                        self.journal.record(
                            operation_id=str(started["operation_id"]),
                            target_artifact_id=target_artifact_id,
                            candidate_id=candidate_id,
                            status="completed",
                            command_id=command_id,
                            result=recovered,
                        )
                        return recovered
                raise RuntimeError(f"acceptance command is already in progress: {command_id}")
        operation_id = uuid.uuid4().hex
        self.journal.record(
            operation_id=operation_id,
            target_artifact_id=target_artifact_id,
            candidate_id=candidate_id,
            status="started",
            command_id=command_id,
        )
        try:
            result = matches[0].accept(target_artifact_id, candidate_id, confirm=confirm)
        except Exception as exc:
            self.journal.record(
                operation_id=operation_id,
                target_artifact_id=target_artifact_id,
                candidate_id=candidate_id,
                status="failed",
                error=str(exc),
                command_id=command_id,
            )
            raise
        self.journal.record(
            operation_id=operation_id,
            target_artifact_id=target_artifact_id,
            candidate_id=candidate_id,
            status="completed",
            command_id=command_id,
            result=result,
        )
        return result
