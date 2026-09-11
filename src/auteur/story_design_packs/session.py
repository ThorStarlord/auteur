"""Local, non-canonical Tutor session persistence."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from .models import AuthorAction, DecisionCard, SourceFingerprint


SourceFingerprintMap = dict[str, SourceFingerprint]
_FINGERPRINT_MAP_ADAPTER = TypeAdapter(SourceFingerprintMap)
_RESOLVING_ACTIONS = {
    AuthorAction.CHOOSE,
    AuthorAction.KEEP_UNRESOLVED,
    AuthorAction.REJECT_FINDING,
}


class TutorSession(BaseModel):
    """One persisted interaction with derived Tutor advice."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(default=1, ge=1)
    session_id: str = Field(pattern=r"^[0-9a-f]{16}$")
    card_id: str = Field(min_length=1)
    card: DecisionCard
    source_fingerprints: SourceFingerprintMap = Field(default_factory=dict)
    status: Literal["active", "stale", "resolved"] = "active"
    stale_reason: str | None = None
    response_action: AuthorAction | None = None
    response_value: str | None = None
    authority_status: Literal["LOCAL / NONCANONICAL"] = "LOCAL / NONCANONICAL"

    @model_validator(mode="after")
    def ensure_card_identity(self) -> "TutorSession":
        if self.card_id != self.card.card_id:
            raise ValueError("card_id does not match persisted Decision Card")
        return self


def _normalized_fingerprints(
    source_fingerprints: Mapping[str, str] | None,
) -> SourceFingerprintMap:
    if source_fingerprints is None:
        return {}
    return _FINGERPRINT_MAP_ADAPTER.validate_python(dict(source_fingerprints))


def stable_session_id(card: DecisionCard, source_fingerprints: Mapping[str, str]) -> str:
    """Return a deterministic identifier for the card/source snapshot."""
    payload = {
        "card_id": card.card_id,
        "source_fingerprints": dict(sorted(source_fingerprints.items())),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def create_session(
    card: DecisionCard,
    source_fingerprints: Mapping[str, str] | None = None,
) -> TutorSession:
    """Create local advisory state without touching story authority."""
    fingerprints = _normalized_fingerprints(source_fingerprints)
    if not fingerprints and card.source_binding is not None:
        fingerprints = {
            card.source_binding.source_artifact: card.source_binding.source_fingerprint
        }
    return TutorSession(
        session_id=stable_session_id(card, fingerprints),
        card_id=card.card_id,
        card=card,
        source_fingerprints=fingerprints,
    )


class TutorSessionStore:
    """Atomic storage for advisory Tutor sessions under one project root."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.root = self.project_root / ".auteur" / "tutor" / "sessions"

    def _path(self, session_id: str) -> Path:
        if len(session_id) != 16 or any(char not in "0123456789abcdef" for char in session_id):
            raise ValueError("Invalid Tutor session ID")
        return self.root / f"{session_id}.json"

    def save(self, session: TutorSession) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        target = self._path(session.session_id)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{session.session_id}.", suffix=".json.tmp", dir=self.root
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(session.model_dump_json(indent=2))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
        return target

    def load(self, session_id: str) -> TutorSession:
        return TutorSession.model_validate_json(
            self._path(session_id).read_text(encoding="utf-8")
        )

    def refresh_status(
        self,
        session_id: str,
        current_source_fingerprints: Mapping[str, str],
    ) -> TutorSession:
        """Persist staleness when current source content differs."""
        session = self.load(session_id)
        if session.status == "stale":
            return session
        current = _normalized_fingerprints(current_source_fingerprints)
        if current != session.source_fingerprints:
            session.status = "stale"
            session.stale_reason = "source_fingerprint_changed"
            self.save(session)
        return session

    def _establish_currentness(
        self,
        session: TutorSession,
        current_source_fingerprints: Mapping[str, str] | None,
    ) -> TutorSession:
        if session.status == "stale":
            raise ValueError("Cannot respond to a stale Tutor session")
        if not session.source_fingerprints:
            return session
        if current_source_fingerprints is None:
            raise ValueError("Current source fingerprints are required before responding")
        try:
            current = _normalized_fingerprints(current_source_fingerprints)
        except Exception as exc:
            raise ValueError("Current source fingerprints are malformed") from exc
        if current != session.source_fingerprints:
            session.status = "stale"
            session.stale_reason = "source_fingerprint_changed"
            self.save(session)
            raise ValueError("Cannot respond to a stale Tutor session")
        return session

    def record_response(
        self,
        session_id: str,
        action: AuthorAction | str,
        value: str | None = None,
        *,
        current_source_fingerprints: Mapping[str, str] | None = None,
    ) -> TutorSession:
        """Record only a local advisory response after proving currentness."""
        session = self._establish_currentness(
            self.load(session_id), current_source_fingerprints
        )
        if session.status == "resolved":
            raise ValueError("Tutor session is already resolved")
        try:
            typed_action = AuthorAction(action)
        except ValueError as exc:
            raise ValueError(f"Unknown Tutor response action: {action}") from exc
        if typed_action not in session.card.author_actions:
            raise ValueError(f"Tutor response action is not allowed: {typed_action.value}")

        session.response_action = typed_action
        session.response_value = value
        session.status = "resolved" if typed_action in _RESOLVING_ACTIONS else "active"
        self.save(session)
        return session
