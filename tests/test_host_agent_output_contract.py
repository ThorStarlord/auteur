"""R03: a versioned, generated output contract without breaking historical identity."""
from __future__ import annotations

import hashlib
import json

import pytest

from auteur.beginner.studio_architecture import ArchitectureCandidate
from auteur.host_agent import (
    OUTPUT_CONTRACT_SCHEMA, build_host_agent_request, load_host_agent_request,
    model_output_contract, write_host_agent_request,
)
from auteur.series.working_book_architecture import WorkingBookArchitecture


def _request(**overrides):
    values = {
        "candidate_id": "studio-abc",
        "role": "studio_architecture",
        "system": "system text",
        "user": '{"a": 1}',
        "settings": {"mode": "develop"},
        "created_at": "2026-11-16T00:00:00+00:00",
    }
    values.update(overrides)
    return build_host_agent_request(**values)


def _historical_fingerprint(**values) -> str:
    body = {
        "schema": "auteur_host_agent_request_v1",
        "candidate_id": values["candidate_id"],
        "role": values["role"],
        "system": values["system"],
        "user": values["user"],
        "settings": values["settings"],
    }
    return hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def test_a_request_without_a_contract_keeps_its_historical_fingerprint():
    request = _request()
    assert request.output_contract is None
    assert request.request_sha256 == _historical_fingerprint(
        candidate_id="studio-abc", role="studio_architecture",
        system="system text", user='{"a": 1}', settings={"mode": "develop"},
    )
    # The key is absent from the dumped packet, exactly as historical packets were.
    assert "output_contract" not in request.model_dump()


def test_supplying_a_contract_changes_the_fingerprint_and_is_recorded():
    plain = _request()
    contracted = _request(output_contract=model_output_contract(ArchitectureCandidate))
    assert contracted.request_sha256 != plain.request_sha256
    assert contracted.output_contract["schema"] == OUTPUT_CONTRACT_SCHEMA
    dumped = contracted.model_dump()
    assert dumped["output_contract"]["model"] == "ArchitectureCandidate"


def test_a_historical_packet_without_the_key_still_loads(tmp_path):
    request = _request()
    path = tmp_path / "request.json"
    write_host_agent_request(path, request)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "output_contract" not in payload
    loaded = load_host_agent_request(path)
    assert loaded.request_sha256 == request.request_sha256


def test_a_contracted_packet_round_trips_through_disk(tmp_path):
    request = _request(output_contract=model_output_contract(WorkingBookArchitecture))
    path = tmp_path / "request.json"
    write_host_agent_request(path, request)
    loaded = load_host_agent_request(path)
    assert loaded.request_sha256 == request.request_sha256
    assert loaded.output_contract == request.output_contract


def test_tampering_with_the_contract_breaks_the_fingerprint(tmp_path):
    request = _request(output_contract=model_output_contract(ArchitectureCandidate))
    path = tmp_path / "request.json"
    write_host_agent_request(path, request)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["output_contract"]["json_schema"]["title"] = "Something else"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        load_host_agent_request(path)


def test_the_contract_represents_required_fields_enums_and_bounds():
    contract = model_output_contract(ArchitectureCandidate)
    schema = contract["json_schema"]
    assert schema["additionalProperties"] is False
    assert "schema_version" in schema["required"]
    assert schema["properties"]["nodes"]["maxItems"] == 80
    assert schema["properties"]["schema_version"]["enum"] == [1, 2]
    # Nested models are represented rather than flattened away.
    items = schema["properties"]["nodes"]["items"]
    assert "$ref" in items or items.get("type") == "object"
    assert "ArchitectureNode" in json.dumps(schema)
    assert "emotion" in json.dumps(schema)


def test_the_contract_is_generated_not_hand_maintained():
    """The schema must come from the model, so it cannot drift from the validator."""
    contract = model_output_contract(ArchitectureCandidate)
    assert contract["json_schema"] == ArchitectureCandidate.model_json_schema()
    assert contract["json_schema_sha256"] == hashlib.sha256(
        json.dumps(
            ArchitectureCandidate.model_json_schema(), ensure_ascii=False,
            sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
