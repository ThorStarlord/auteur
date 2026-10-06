from __future__ import annotations

from pathlib import Path

import pytest

from auteur.host_agent import (
    UNAVAILABLE,
    build_host_agent_request,
    build_host_agent_response,
    load_host_agent_request,
    validate_host_agent_response,
    write_host_agent_request,
    write_host_agent_response,
)


def _request():
    return build_host_agent_request(
        candidate_id="quick-123",
        role="quick_draft_scene",
        system="Write a scene.",
        user="Premise: X\nFirst scene: Y",
        settings={"temperature": 0.85, "max_tokens": 1800},
        created_at="2026-10-05T00:00:00+00:00",
    )


def test_request_fingerprint_binds_candidate_prompt_and_settings() -> None:
    request = _request()
    changed = build_host_agent_request(
        candidate_id="quick-124",
        role=request.role,
        system=request.system,
        user=request.user,
        settings=request.settings,
        created_at=request.created_at,
    )
    assert request.request_sha256 != changed.request_sha256
    assert request.request_id != changed.request_id


def test_request_round_trip_detects_tampering(tmp_path: Path) -> None:
    path = tmp_path / "request.json"
    write_host_agent_request(path, _request())
    loaded = load_host_agent_request(path)
    assert loaded == _request()

    text = path.read_text(encoding="utf-8").replace(
        "First scene: Y",
        "First scene: silently changed",
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="fingerprint|ID"):
        load_host_agent_request(path)


def test_response_requires_exact_request_identity() -> None:
    request = _request()
    response = build_host_agent_response(
        request,
        "Generated scene.",
        runtime="current-coding-agent",
        model=UNAVAILABLE,
        elapsed_seconds=1.5,
    )
    validated = validate_host_agent_response(request, response)
    assert validated.runtime == "current-coding-agent"
    assert validated.model == UNAVAILABLE

    other = build_host_agent_request(
        candidate_id="quick-other",
        role=request.role,
        system=request.system,
        user=request.user,
        settings=request.settings,
    )
    with pytest.raises(ValueError, match="different request|different candidate|fingerprint"):
        validate_host_agent_response(other, response)


def test_response_packet_round_trip_is_inspectable(tmp_path: Path) -> None:
    request = _request()
    response = build_host_agent_response(request, "Generated scene.")
    path = tmp_path / "response.json"
    write_host_agent_response(path, response)
    payload = __import__("json").loads(path.read_text(encoding="utf-8"))
    assert payload["request_sha256"] == request.request_sha256
    assert payload["text"] == "Generated scene."
    assert payload["backend"] == "host-agent"



def test_response_cannot_masquerade_as_direct_provider() -> None:
    request = _request()
    response = build_host_agent_response(
        request,
        "Generated scene.",
        backend="openai",
    )
    with pytest.raises(ValueError, match="backend"):
        validate_host_agent_response(request, response)
