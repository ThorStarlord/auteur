"""Neutral request/response handoff for host coding-agent generation.

The module deliberately knows nothing about Claude Code, Codex, ChatGPT, Cursor,
OpenCode, or any other agent vendor. Auteur owns the request contract and
validation; the surrounding host supplies the actual reasoning/generation.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUEST_SCHEMA = "auteur_host_agent_request_v1"
OUTPUT_CONTRACT_SCHEMA = "auteur_host_agent_output_contract_v1"
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
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def contract_limit_lines(model: type) -> list[str]:
    """The owner-enforced bounds of a contract, read from the same JSON Schema that the output contract carries.

    Lengths, item counts, values, enumerations and patterns that JSON Schema can state are generated here, one line per bounded field, so
    an instruction cannot omit a bound that the validator enforces. A bound that JSON Schema cannot express is enforced separately and is
    not listed here.
    """
    schema = model.model_json_schema()
    definitions = schema.get("$defs", {})
    lines: list[str] = []

    def resolve(node: dict[str, Any]) -> dict[str, Any]:
        if "$ref" in node:
            return definitions.get(node["$ref"].rsplit("/", 1)[-1], {})
        return node

    def branches(node: dict[str, Any]) -> list[dict[str, Any]]:
        node = resolve(node)
        if "anyOf" in node:
            return [resolve(option) for option in node["anyOf"] if option.get("type") != "null"]
        return [node]

    def describe(path: str, node: dict[str, Any], depth: int) -> None:
        if depth > 8:
            return
        for option in branches(node):
            parts: list[str] = []
            if "maxLength" in option:
                parts.append(f"at most {option['maxLength']} characters")
            if option.get("minLength", 0) > 1:
                parts.append(f"at least {option['minLength']} characters")
            if option.get("type") == "array":
                if "maxItems" in option:
                    parts.append(f"at most {option['maxItems']} items")
                if option.get("minItems", 0) > 1:
                    parts.append(f"at least {option['minItems']} items")
            if "enum" in option:
                parts.append("one of " + ", ".join(repr(value) for value in option["enum"]))
            if "const" in option:
                parts.append(f"exactly {option['const']!r}")
            if "pattern" in option:
                parts.append(f"matching {option['pattern']}")
            if "minimum" in option:
                parts.append(f"at least {option['minimum']}")
            if "maximum" in option:
                parts.append(f"at most {option['maximum']}")
            if parts and path:
                lines.append(f"{path}: {'; '.join(parts)}")
            if option.get("type") == "array" and "items" in option:
                describe(f"{path}[]", option["items"], depth + 1)
            for name, child in option.get("properties", {}).items():
                describe(f"{path}.{name}" if path else name, child, depth + 1)

    describe("", schema, 0)
    return lines


def limits_instruction(model: type) -> str:
    """The instruction text that states a contract's owner-enforced bounds. An answer that exceeds one is refused whole."""
    lines = contract_limit_lines(model)
    header = "Limits, enforced by the owner (an answer that exceeds one is refused whole). Each line names a field and its bound:"
    return header + chr(10) + chr(10).join(f"- {line}" for line in lines)


def model_output_contract(model: type, *, title: str | None = None) -> dict[str, Any]:
    """Machine-readable output contract generated from the authoritative model.

    The JSON Schema is generated, never hand-maintained, so it cannot drift from
    the validator. Semantic rules that JSON Schema cannot express remain enforced
    by the existing post-generation validators; this contract is context, not
    proof that a model will comply.
    """
    schema = model.model_json_schema()
    return {
        "schema": OUTPUT_CONTRACT_SCHEMA,
        "version": 1,
        "model": title or model.__name__,
        "json_schema": schema,
        "json_schema_sha256": hashlib.sha256(_canonical_bytes(schema)).hexdigest(),
    }


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
    output_contract: dict[str, Any] | None = None

    def model_dump(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.output_contract is None:
            # Historical packets never carried this key; omit it so their bytes and
            # fingerprints keep their original meaning.
            payload.pop("output_contract", None)
        return payload


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
    output_contract: dict[str, Any] | None = None,
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
    if output_contract is not None:
        # Only present when supplied, so historical request fingerprints are stable.
        body["output_contract"] = output_contract
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
        output_contract=output_contract,
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
        output_contract=request.output_contract,
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
    if response.backend != "host-agent":
        raise ValueError("host-agent response backend must be 'host-agent'")
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
