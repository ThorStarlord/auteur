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


class AcceptanceJournal:
    """Durable intent/completion journal for authority-bearing operations."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.path = Path(project_root).resolve() / ".auteur" / "acceptance" / "journal.json" if project_root else None
        self._records: list[dict[str, Any]] = []
        if self.path and self.path.exists():
            self._records = json.loads(self.path.read_text(encoding="utf-8"))

    def record(self, *, operation_id: str, target_artifact_id: str, candidate_id: str, status: str, error: str = "") -> None:
        self._records.append({
            "operation_id": operation_id,
            "target_artifact_id": target_artifact_id,
            "candidate_id": candidate_id,
            "status": status,
            "error": error,
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


class AcceptanceRegistry:
    """Resolve exactly one canonical acceptance owner for a target."""

    def __init__(self, project_root: Path | None = None) -> None:
        self._owners: list[AcceptanceOwner] = []
        self.journal = AcceptanceJournal(project_root)

    def register(self, owner: AcceptanceOwner) -> None:
        self._owners.append(owner)

    def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> Any:
        matches = [owner for owner in self._owners if owner.can_accept(target_artifact_id)]
        if not matches:
            raise ValueError(f"No acceptance owner registered for artifact: {target_artifact_id}")
        if len(matches) > 1:
            raise ValueError(f"Multiple acceptance owners registered for artifact: {target_artifact_id}")
        operation_id = uuid.uuid4().hex
        self.journal.record(
            operation_id=operation_id,
            target_artifact_id=target_artifact_id,
            candidate_id=candidate_id,
            status="started",
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
            )
            raise
        self.journal.record(
            operation_id=operation_id,
            target_artifact_id=target_artifact_id,
            candidate_id=candidate_id,
            status="completed",
        )
        return result
