"""Local, non-canonical Tutor session persistence and currentness checks."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from .models import AuthorAction, DecisionCard, SourceFingerprint


_SESSION_ID_RE = re.compile(r"^[0-9a-f]{16}$")
_FINGERPRINTS = TypeAdapter(dict[str, SourceFingerprint])
_RESOLVING_ACTIONS = {
    AuthorAction.CHOOSE,
    AuthorAction.KEEP_UNRESOLVED,
    AuthorAction.REJECT_FINDING,
}


class TutorSessionCurrentnessError(ValueError):
    """Current source evidence is missing or cannot establish freshness."""


class StaleTutorSessionError(ValueError):
    """A substantive response was attempted against stale Tutor advice."""


class ResolvedTutorSessionError(ValueError):
    """A substantive response was attempted against a resolved session."""


class TutorSession(BaseModel):
    """One local advisory interaction with a derived Decision Card.

    Tutor sessions are explicitly local/noncanonical. They record interaction
    with advice and never become accepted story state.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: int = Field(default=1, ge=1)
    session_id: str
    card_id: str
    card: DecisionCard
    source_fingerprints: dict[str, SourceFingerprint] = Field(default_factory=dict)
    status: Literal["active", "stale", "resolved"] = "active"
    stale_reason: str | None = None
    response_action: AuthorAction | None = None
    response_value: str | None = None
    authority_status: Literal["LOCAL / NONCANONICAL"] = "LOCAL / NONCANONICAL"

    @model_validator(mode="after")
    def validate_session_identity_and_lifecycle(self) -> "TutorSession":
        if self.card_id != self.card.card_id:
            raise ValueError("card_id does not match serialized Decision Card")
        expected = stable_session_id(self.card_id, self.source_fingerprints)
        if self.session_id != expected:
            raise ValueError("session_id does not match card/source identity")
        if self.status == "stale" and not self.stale_reason:
            raise ValueError("stale Tutor session requires stale_reason")
        if self.status != "stale" and self.stale_reason is not None:
            raise ValueError("stale_reason is valid only for stale Tutor sessions")
        if self.status == "resolved" and self.response_action not in _RESOLVING_ACTIONS:
            raise ValueError("resolved Tutor session requires a resolving response action")
        return self


def stable_session_id(
    card_id: str,
    source_fingerprints: Mapping[str, str],
) -> str:
    """Return the stable M1 session identity for card + source fingerprints."""

    normalized = _validated_fingerprints(source_fingerprints)
    payload = {
        "card_id": card_id,
        "source_fingerprints": dict(sorted(normalized.items())),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def source_fingerprints_from_card(card: DecisionCard) -> dict[str, SourceFingerprint]:
    """Derive the current M1 fingerprint map from the card's source binding."""

    binding = card.source_binding
    if binding is None:
        return {}
    return {binding.source_artifact: binding.source_fingerprint}


def create_session(
    card: DecisionCard,
    source_fingerprints: Mapping[str, str] | None = None,
) -> TutorSession:
    """Create an active, noncanonical session without writing repository state."""

    fingerprints = _validated_fingerprints(
        source_fingerprints
        if source_fingerprints is not None
        else source_fingerprints_from_card(card)
    )
    return TutorSession(
        session_id=stable_session_id(card.card_id, fingerprints),
        card_id=card.card_id,
        card=card,
        source_fingerprints=fingerprints,
    )


class TutorSessionStore:
    """Atomic storage for derived Tutor sessions beneath one project root."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.root = self.project_root / ".auteur" / "tutor" / "sessions"

    def _path(self, session_id: str) -> Path:
        _validate_session_id(session_id)
        return self.root / f"{session_id}.json"

    def save(self, session: TutorSession) -> Path:
        """Persist one session atomically and return its local advisory path."""

        self.root.mkdir(parents=True, exist_ok=True)
        target = self._path(session.session_id)
        payload = session.model_dump_json(indent=2) + "\n"
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{session.session_id}.",
            suffix=".tmp",
            dir=self.root,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        except BaseException:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise
        return target

    def load(self, session_id: str) -> TutorSession:
        """Load a session for inspection, including stale or resolved sessions."""

        return TutorSession.model_validate_json(
            self._path(session_id).read_text(encoding="utf-8")
        )

    def refresh_status(
        self,
        session_id: str,
        source_fingerprints: Mapping[str, str] | None,
    ) -> TutorSession:
        """Compare current source evidence and persist stale state when detected.

        Missing/incomplete/malformed currentness evidence never revives a stale
        session and cannot be treated as proof of freshness.
        """

        session = self.load(session_id)
        if session.status in {"stale", "resolved"}:
            return session
        if not session.source_fingerprints:
            return session

        current = _require_current_fingerprints(session, source_fingerprints)
        changed = _changed_sources(session.source_fingerprints, current)
        if not changed:
            return session

        session.status = "stale"
        session.stale_reason = "source_fingerprint_changed:" + ",".join(changed)
        self.save(session)
        return session

    def record_response(
        self,
        session_id: str,
        action: AuthorAction | str,
        value: str | None = None,
        *,
        current_source_fingerprints: Mapping[str, str] | None = None,
    ) -> TutorSession:
        """Record one advisory response after establishing currentness itself.

        This service method is intentionally fail-closed: callers cannot bypass
        source-currentness checks by omitting a prior refresh operation.
        """

        session = self.load(session_id)
        if session.status == "stale":
            raise StaleTutorSessionError("Cannot respond to a stale Tutor session")
        if session.status == "resolved":
            raise ResolvedTutorSessionError("Cannot respond to a resolved Tutor session")

        if session.source_fingerprints:
            current = _require_current_fingerprints(
                session,
                current_source_fingerprints,
            )
            changed = _changed_sources(session.source_fingerprints, current)
            if changed:
                session.status = "stale"
                session.stale_reason = "source_fingerprint_changed:" + ",".join(changed)
                self.save(session)
                raise StaleTutorSessionError(
                    "Cannot respond to stale Tutor advice; regenerate from current sources"
                )

        try:
            typed_action = action if isinstance(action, AuthorAction) else AuthorAction(action)
        except ValueError as exc:
            raise ValueError(f"Unknown Tutor response action: {action}") from exc
        if typed_action not in session.card.author_actions:
            raise ValueError(
                f"Tutor response action is not allowed by this Decision Card: {typed_action.value}"
            )

        session.response_action = typed_action
        session.response_value = value
        session.status = "resolved" if typed_action in _RESOLVING_ACTIONS else "active"
        session.stale_reason = None
        self.save(session)
        return session


def _validated_fingerprints(
    source_fingerprints: Mapping[str, str],
) -> dict[str, SourceFingerprint]:
    try:
        return _FINGERPRINTS.validate_python(dict(source_fingerprints))
    except Exception as exc:  # Pydantic exposes structured detail; service keeps one boundary.
        raise TutorSessionCurrentnessError("Malformed source fingerprint mapping") from exc


def _require_current_fingerprints(
    session: TutorSession,
    current: Mapping[str, str] | None,
) -> dict[str, SourceFingerprint]:
    if current is None:
        raise TutorSessionCurrentnessError(
            "Current source fingerprints are required before responding to this Tutor session"
        )
    normalized = _validated_fingerprints(current)
    missing = sorted(set(session.source_fingerprints) - set(normalized))
    if missing:
        raise TutorSessionCurrentnessError(
            "Current source fingerprints are incomplete: " + ", ".join(missing)
        )
    return normalized


def _changed_sources(
    stored: Mapping[str, str],
    current: Mapping[str, str],
) -> list[str]:
    return sorted(key for key, value in stored.items() if current[key] != value)


def _validate_session_id(session_id: str) -> None:
    if not _SESSION_ID_RE.fullmatch(session_id):
        raise ValueError("Tutor session_id must be a 16-character lowercase hex digest")
