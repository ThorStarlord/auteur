"""Local, non-canonical Tutor session persistence."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from .models import DecisionCard


class TutorSession(BaseModel):
    schema_version: int = Field(default=1, ge=1)
    session_id: str
    card_id: str
    card: DecisionCard
    source_fingerprints: dict[str, str] = Field(default_factory=dict)
    status: Literal["active", "stale", "resolved"] = "active"
    stale_reason: str | None = None
    response_action: str | None = None
    response_value: str | None = None


def create_session(card: DecisionCard, source_fingerprints: dict[str, str]) -> TutorSession:
    payload = {
        "card_id": card.card_id,
        "source_fingerprints": dict(sorted(source_fingerprints.items())),
    }
    session_id = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return TutorSession(
        session_id=session_id,
        card_id=card.card_id,
        card=card,
        source_fingerprints=dict(source_fingerprints),
    )


class TutorSessionStore:
    """Atomic storage for derived Tutor sessions under a project root."""

    def __init__(self, project_root: Path) -> None:
        self.root = Path(project_root) / ".auteur" / "tutor" / "sessions"

    def _path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.json"

    def save(self, session: TutorSession) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        target = self._path(session.session_id)
        fd, temp_name = tempfile.mkstemp(prefix=f".{session.session_id}.", suffix=".tmp", dir=self.root)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(session.model_dump_json(indent=2))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def load(self, session_id: str) -> TutorSession:
        return TutorSession.model_validate_json(self._path(session_id).read_text(encoding="utf-8"))

    def refresh_status(self, session_id: str, source_fingerprints: dict[str, str]) -> TutorSession:
        session = self.load(session_id)
        if session.source_fingerprints != source_fingerprints:
            session.status = "stale"
            session.stale_reason = "source_fingerprint_changed"
            self.save(session)
        return session

    def record_response(self, session_id: str, action: str, value: str | None = None) -> TutorSession:
        session = self.load(session_id)
        if session.status == "stale":
            raise ValueError("Cannot respond to a stale Tutor session")
        session.response_action = action
        session.response_value = value
        session.status = "resolved" if action in {"choose", "keep_unresolved", "reject_finding"} else "active"
        self.save(session)
        return session
