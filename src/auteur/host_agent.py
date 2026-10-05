"""Neutral request/response handoff for host coding-agent generation.

The module deliberately knows nothing about Claude Code, Codex, ChatGPT, Cursor,
OpenCode, or any other agent vendor. Auteur owns the request contract and
validation; the surrounding host supplies the actual reasoning/generation.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUEST_SCHEMA = "auteur_host_agent_request_v1"
RESPONSE_SCHEMA = "auteur_host_agent_response_v1"
UNAVAILABLE = "UNAVAILABLE"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


@dataclass(frozen=True)
class HostAgentRequest:
    schema: str
    request_id: str
    candidate_id: str
    role: str
    created_at: str
    system: str
    user: str
    settings: dict[str, Any]
    request_sha256: str

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HostAgentResponse:
    schema: str
    request_id: str
    candidate_id: str
    request_sha256: str
    text: str
    backend: str
    runtime: str
    model: str
    completed_at: str
    elapsed_seconds: float | None = None

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)


def build_host_agent_request(
    *,
    candidate_id: str,
    role: str,
    system: str,
    user: str,
    settings: dict[str, Any],
    created_at: str | None = None,
) -> HostAgentRequest:
    if not candidate_id.strip():
        raise ValueError("candidate_id must not be empty")
    if not role.strip():
        raise ValueError("role must not be empty")
    if not system.strip() or not user.strip():
        raise ValueError("host-agent request prompts must not be empty")
    body = {
        "schema": REQUEST_SCHEMA,
        "candidate_id": candidate_id,
        "role": role,
        "system": system,
        "user": user,
        "settings": settings,
    }
    fingerprint = hashlib.sha256(_canonical_bytes(body)).hexdigest()
    return HostAgentRequest(
        schema=REQUEST_SCHEMA,
        request_id=f"{candidate_id}:{fingerprint[:16]}",
        candidate_id=candidate_id,
        role=role,
        created_at=created_at or _now(),
        system=system,
        user=user,
        settings=settings,
        request_sha256=fingerprint,
    )


def write_host_agent_request(path: Path, request: HostAgentRequest) -> None:
    _atomic_json_write(path, request.model_dump())


def load_host_agent_request(path: Path) -> HostAgentRequest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("host-agent request packet must be a JSON object")
    request = HostAgentRequest(**payload)
    expected = build_host_agent_request(
        candidate_id=request.candidate_id,
        role=request.role,
        system=request.system,
        user=request.user,
        settings=request.settings,
        created_at=request.created_at,
    )
    if request.schema != REQUEST_SCHEMA:
        raise ValueError("unsupported host-agent request schema")
    if request.request_id != expected.request_id:
        raise ValueError("host-agent request ID does not match request contents")
    if request.request_sha256 != expected.request_sha256:
        raise ValueError("host-agent request fingerprint does not match request contents")
    return request


def build_host_agent_response(
    request: HostAgentRequest,
    text: str,
    *,
    backend: str = "host-agent",
    runtime: str = UNAVAILABLE,
    model: str = UNAVAILABLE,
    elapsed_seconds: float | None = None,
    completed_at: str | None = None,
) -> HostAgentResponse:
    if not text.strip():
        raise ValueError("host-agent response text must not be empty")
    if elapsed_seconds is not None and elapsed_seconds < 0:
        raise ValueError("elapsed_seconds must be non-negative")
    return HostAgentResponse(
        schema=RESPONSE_SCHEMA,
        request_id=request.request_id,
        candidate_id=request.candidate_id,
        request_sha256=request.request_sha256,
        text=text,
        backend=backend.strip() or "host-agent",
        runtime=runtime.strip() or UNAVAILABLE,
        model=model.strip() or UNAVAILABLE,
        completed_at=completed_at or _now(),
        elapsed_seconds=elapsed_seconds,
    )


def validate_host_agent_response(
    request: HostAgentRequest,
    payload: HostAgentResponse | dict[str, Any],
) -> HostAgentResponse:
    response = payload if isinstance(payload, HostAgentResponse) else HostAgentResponse(**payload)
    if response.schema != RESPONSE_SCHEMA:
        raise ValueError("unsupported host-agent response schema")
    if response.request_id != request.request_id:
        raise ValueError("host-agent response belongs to a different request")
    if response.candidate_id != request.candidate_id:
        raise ValueError("host-agent response belongs to a different candidate")
    if response.request_sha256 != request.request_sha256:
        raise ValueError("host-agent response fingerprint does not match request")
    if not response.text.strip():
        raise ValueError("host-agent response text must not be empty")
    if response.elapsed_seconds is not None and response.elapsed_seconds < 0:
        raise ValueError("elapsed_seconds must be non-negative")
    return response


def write_host_agent_response(path: Path, response: HostAgentResponse) -> None:
    _atomic_json_write(path, response.model_dump())


__all__ = [
    "HostAgentRequest",
    "HostAgentResponse",
    "REQUEST_SCHEMA",
    "RESPONSE_SCHEMA",
    "UNAVAILABLE",
    "build_host_agent_request",
    "build_host_agent_response",
    "load_host_agent_request",
    "validate_host_agent_response",
    "write_host_agent_request",
    "write_host_agent_response",
]
