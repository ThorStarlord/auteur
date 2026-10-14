"""Provisional concrete story elements must remain linked and source-bound."""
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_store import CanvasStore
from auteur.beginner.studio_architecture import prepare_architecture, complete_architecture
from auteur.beginner.studio_realization import (
    RealizationCandidate, apply_realization_review, complete_realization,
    prepare_realization, project_realization,
)
from auteur.host_agent import HostAgentRequest, build_host_agent_response


def store_with_architecture(tmp_path):
    store = CanvasStore(tmp_path, "realization-one")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision-start",
                payload={"item": {"id": "story-vision", "kind": "note",
                                  "title": "Story Vision",
                                  "content": "Heroic paladin progression fantasy."},
                         "position": {"x": 40, "y": 50}})
    pending = prepare_architecture(store)
    architecture = {
        "schema_version": 1, "summary": "Progression supports heroic generosity.",
        "nodes": [
            {"id": "growth", "title": "Progression", "category": "engine",
             "summary": "New capability creates new ethical pressures."},
            {"id": "generosity", "title": "Generosity", "category": "theme",
             "summary": "Costly mercy and care matter."},
        ],
        "links": [{"id": "a", "source": "growth", "target": "generosity",
                   "function": "enables"}],
    }
    complete_architecture(store, respond(pending, architecture))
    return store


def respond(state, payload):
    request = HostAgentRequest(**state["request"])
    return build_host_agent_response(request, json.dumps(payload),
                                     runtime="integration-test",
                                     model="UNAVAILABLE").model_dump()


def candidate():
    return {
        "schema_version": 1,
        "summary": "A specific embodiment of a general design.",
        "elements": [
            {"id": "paladin", "kind": "character", "title": "Paladin candidate",
             "description": "A character who must decide how to use new power.",
             "architecture_refs": ["growth", "generosity"]},
            {"id": "settlement", "kind": "location", "title": "Settlement candidate",
             "description": "A location where generosity has concrete consequences.",
             "architecture_refs": ["generosity"]},
        ],
        "links": [{"id": "protects", "source": "paladin", "target": "settlement",
                   "function": "protects"}],
        "architecture_feedback": [
            {"id": "feedback", "architecture_node_id": "growth",
             "observation": "The new concrete dynamic suggests a limitation.",
             "proposed_change": "Consider making ethical responsibility scale with capability."},
        ],
    }


def test_realization_is_created_only_after_architecture_and_preserves_owner(tmp_path):
    store = CanvasStore(tmp_path, "realization-one")
    store.create()
    with pytest.raises(ValueError, match="develop Narrative Architecture"):
        prepare_realization(store)
    store = store_with_architecture(tmp_path / "ready")
    pending = prepare_realization(store, ["growth"])
    assert pending["request"]["role"] == "studio_realization"
    assert "focus_ids" in pending["request"]["user"]
    ready = complete_realization(store, respond(pending, candidate()))
    assert ready["status"] == "ready"
    assert ready["candidate"]["elements"][0]["architecture_refs"] == ["growth", "generosity"]
    assert project_realization(CanvasStore(tmp_path / "ready", "realization-one"))["candidate"] == ready["candidate"]
    assert not (tmp_path / "ready" / "story_identity.yaml").exists()
    assert not (tmp_path / "ready" / "blueprint.yaml").exists()


def test_realization_rejects_invalid_links_and_unsupported_architecture_refs(tmp_path):
    store = store_with_architecture(tmp_path)
    pending = prepare_realization(store, ["growth"])
    bad = candidate()
    bad["links"][0]["target"] = "missing"
    with pytest.raises(ValidationError):
        complete_realization(store, respond(pending, bad))
    bad = candidate()
    bad["elements"][0]["architecture_refs"] = ["nonexistent"]
    with pytest.raises(ValueError, match="existing architecture nodes"):
        complete_realization(store, respond(pending, bad))
    assert project_realization(store)["candidate"] is None


def test_realization_stale_when_author_changes_working_vision(tmp_path):
    store = store_with_architecture(tmp_path)
    pending = prepare_realization(store)
    doc = store.load()
    edited = doc.items[0].model_copy(update={"content": "A different genre promise."})
    store.apply("update-item", expected_revision=doc.revision, command_id="changed-vision",
                payload={"item": edited.model_dump(mode="json")})
    with pytest.raises(BeginnerConcurrencyError, match="stale realization"):
        complete_realization(store, respond(pending, candidate()))
    assert project_realization(store)["candidate"] is None


def test_realization_revision_is_staged_and_explicitly_applied(tmp_path):
    store = store_with_architecture(tmp_path)
    first = prepare_realization(store, ["growth"])
    complete_realization(store, respond(first, candidate()))
    next_request = prepare_realization(store, ["growth"], "Strengthen the moral dilemma.")
    changed = candidate()
    changed["elements"][0]["description"] = "The paladin confronts difficult mercy."
    review = complete_realization(store, respond(next_request, changed))
    assert review["status"] == "review_ready"
    assert review["candidate"]["elements"][0]["description"] == candidate()["elements"][0]["description"]
    assert review["review"]["changes"]["elements"]["changed"] == ["paladin"]
    applied = apply_realization_review(store, review["review"]["request_sha256"])
    assert applied["status"] == "ready"
    assert applied["candidate"]["elements"][0]["description"] == "The paladin confronts difficult mercy."
    assert applied["candidate"]["architecture_feedback"][0]["architecture_node_id"] == "growth"


def test_realization_projection_reports_stale_but_retains_concrete_proposal(tmp_path):
    store = store_with_architecture(tmp_path)
    pending = prepare_realization(store)
    complete_realization(store, respond(pending, candidate()))
    doc = store.load()
    changed = doc.items[0].model_copy(update={"content": "A new author intent."})
    store.apply("update-item", expected_revision=doc.revision, command_id="vision-revision",
                payload={"item": changed.model_dump(mode="json")})
    old = project_realization(store)
    assert old["status"] == "stale"
    assert old["candidate"]["elements"][0]["id"] == "paladin"


def test_realization_cli_wraps_raw_candidate_without_faking_agent_output(tmp_path, capsys):
    from auteur.beginner.studio_realization import main
    store_with_architecture(tmp_path)
    args = ["--project", str(tmp_path), "--canvas", "realization-one"]
    assert main(args + ["prepare", "--focus", "growth"]) == 0
    packet = json.loads(capsys.readouterr().out)
    assert packet["request"]["role"] == "studio_realization"
    output = tmp_path / "concrete-proposal.json"
    output.write_text(json.dumps(candidate()), encoding="utf-8")
    assert main(args + ["complete-file", "--candidate", str(output)]) == 0
    completed = json.loads(capsys.readouterr().out)
    assert completed["status"] == "ready"
    assert completed["candidate"]["elements"][0]["architecture_refs"] == ["growth", "generosity"]


def test_stale_architecture_blocks_new_concrete_realization(tmp_path):
    store = store_with_architecture(tmp_path)
    doc = store.load()
    updated = doc.items[0].model_copy(update={"content": "Revised core narrative vision."})
    store.apply("update-item", expected_revision=doc.revision, command_id="vision-edited",
                payload={"item": updated.model_dump(mode="json")})
    with pytest.raises(ValueError, match="architecture is stale"):
        prepare_realization(store)


def test_local_http_realization_handoff_and_review(tmp_path):
    from urllib.request import Request, urlopen
    from auteur.beginner.server import BeginnerWorkspaceServer
    store_with_architecture(tmp_path)
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}/api/beginner/studio/canvases/realization-one/realization"
        def call(path, body=None):
            payload = None if body is None else json.dumps(body).encode("utf-8")
            req = Request(base + path, data=payload,
                          method="POST" if body is not None else "GET",
                          headers={"Content-Type": "application/json"})
            with urlopen(req) as result:
                return result.status, json.loads(result.read().decode("utf-8"))
        status, pending = call("/prepare", {"focus_ids": ["growth"]})
        assert status == 202 and pending["status"] == "awaiting_host_agent"
        status, ready = call("/host-agent-response", respond(pending, candidate()))
        assert status == 200 and ready["status"] == "ready"
        assert call("")[1]["candidate"]["elements"][0]["id"] == "paladin"
        _, revision = call("/prepare", {"focus_ids": ["growth"], "instruction": "Adjust stakes."})
        _, review = call("/host-agent-response", respond(revision, candidate()))
        assert review["status"] == "review_ready"
        _, result = call("/apply", {"request_sha256": review["review"]["request_sha256"]})
        assert result["status"] == "ready"
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
