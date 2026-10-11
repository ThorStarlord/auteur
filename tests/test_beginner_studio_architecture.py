"""Source-bound Studio architecture proposals: host handoff, validation, staleness, HTTP."""
from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from pydantic import ValidationError

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import (
    ArchitectureCandidate, complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


def working_store(tmp_path):
    store = CanvasStore(tmp_path, "story-one")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision-created",
                payload={"item": {
                    "id": "story-vision", "kind": "note", "title": "Story Vision",
                    "content": "A long fantasy: awe, mystery, romance, local horror, and hope.",
                }, "position": {"x": 20, "y": 50}})
    return store


def candidate():
    return {
        "schema_version": 1,
        "summary": "Wonder survives shifting genres.",
        "nodes": [
            {"id": "engine", "title": "Discovery engine", "category": "engine",
             "summary": "Discovery creates new costs and choices."},
            {"id": "emotion", "title": "Awe", "category": "reader_experience",
             "summary": "Keep discovery wondrous."},
        ],
        "links": [{"id": "link", "source": "engine", "target": "emotion",
                   "function": "supports"}],
        "phases": [
            {"id": "investigation", "title": "Investigation", "order": 1,
             "genres": [{"genre": "mystery", "role": "locally_dominant"}],
             "narrative_function": "Establish the central question."},
            {"id": "horror", "title": "Incursion", "order": 2,
             "genres": [{"genre": "horror", "role": "locally_dominant"}],
             "narrative_function": "Turn knowledge into risk.",
             "parallel_with": ["investigation"]},
        ],
        "open_questions": ["What makes the discovery costly?"],
    }


def response(status, data=None):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data if data is not None else candidate()),
        runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def test_no_premise_host_agent_proposal_reopen_and_no_canon(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    assert waiting["status"] == "awaiting_host_agent"
    assert waiting["request"]["role"] == "studio_architecture"
    assert "awe" in waiting["request"]["user"].lower()
    ready = complete_architecture(store, response(waiting))
    assert ready["status"] == "ready"
    assert len(ready["candidate"]["nodes"]) == 2
    assert len(ready["candidate"]["phases"]) == 2
    assert project_architecture(CanvasStore(tmp_path, "story-one"))["candidate"] == ready["candidate"]
    assert not (tmp_path / "story_identity.yaml").exists()
    assert not (tmp_path / "blueprint.yaml").exists()


def test_vision_edit_rejects_stale_response_and_keeps_evidence(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    canvas = store.load()
    changed = canvas.items[0].model_copy(update={"content": "A darker story, no awe."})
    store.apply("update-item", expected_revision=canvas.revision, command_id="change-intent",
                payload={"item": changed.model_dump(mode="json")})
    with pytest.raises(BeginnerConcurrencyError, match="source vision"):
        complete_architecture(store, response(waiting))
    assert project_architecture(store)["candidate"] is None
    source = store.directory / "architecture" / "requests" / waiting["request"]["request_sha256"]
    assert (source / "stale_response.json").exists()


def test_invalid_edges_and_cycles_rejected_without_persistence(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    bad = candidate()
    bad["links"][0]["target"] = "nonexistent"
    with pytest.raises(ValidationError):
        complete_architecture(store, response(waiting, bad))
    assert project_architecture(store)["candidate"] is None
    bad = candidate()
    bad["nodes"][0]["parent_id"] = "emotion"
    bad["nodes"][1]["parent_id"] = "engine"
    with pytest.raises(ValidationError):
        ArchitectureCandidate.model_validate(bad)


def test_revision_preserves_prior_candidate_and_idempotent_response(tmp_path):
    store = working_store(tmp_path)
    first = prepare_architecture(store)
    first_reply = response(first)
    complete_architecture(store, first_reply)
    assert complete_architecture(store, first_reply)["status"] == "ready"
    revised = prepare_architecture(store, "Give horror a stronger structural function.")
    assert revised["status"] == "awaiting_host_agent"
    assert "Give horror" in revised["request"]["user"]
    assert revised["candidate"]["summary"] == candidate()["summary"]
    update = candidate()
    update["nodes"][0]["summary"] = "Discovery repeatedly brings a horror cost."
    finished = complete_architecture(store, response(revised, update))
    assert finished["candidate"]["nodes"][0]["summary"].endswith("cost.")
    history = store.directory / "architecture" / "requests" / first["request"]["request_sha256"]
    assert (history / "response.json").exists()


def _call(base, method, route, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(base + route, data=data, method=method,
                  headers={"Content-Type": "application/json"})
    with urlopen(req) as result:
        return result.status, json.loads(result.read().decode("utf-8"))


def test_http_prepare_complete_and_missing_canvas(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        prefix = "/api/beginner/studio/canvases/story-one/architecture"
        with pytest.raises(HTTPError) as missing:
            _call(base, "GET", prefix)
        assert missing.value.code == 404
        working_store(tmp_path)
        code, waiting = _call(base, "POST", prefix + "/prepare", {})
        assert code == 202 and waiting["status"] == "awaiting_host_agent"
        code, ready = _call(base, "POST", prefix + "/host-agent-response", response(waiting))
        assert code == 200 and ready["status"] == "ready"
        _, saved = _call(base, "GET", prefix)
        assert saved["candidate"] == ready["candidate"]
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
