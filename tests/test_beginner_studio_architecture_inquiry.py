"""Read-only, source-bound graph-agent inquiry lifecycle; never a working revision."""
from __future__ import annotations

import copy
import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry,
    project_architecture_inquiry,
)
from auteur.host_agent import HostAgentRequest, build_host_agent_response

from test_beginner_studio_architecture_review import (
    working_store, valid_candidate, response,
)


def seeded_store(tmp_path):
    store = working_store(tmp_path)
    first = prepare_architecture(store)
    complete_architecture(store, response(first, valid_candidate()))
    return store


def intent(store, operation="explore", anchors=None):
    projection = project_architecture(store)
    return {
        "version": 1,
        "canvas_id": store.canvas_id,
        "operation": operation,
        "expected_candidate_request_sha256": projection["candidate_request_sha256"],
        "anchors": anchors or [{"kind": "node", "id": "wonder-engine"}],
        "author_text": "What other narratives could this engine support?",
    }


def packet(projection, result=None):
    request = HostAgentRequest(**projection["request"])
    candidate = result or {
        "schema_version": 1,
        "analysis": "The engine might make discoveries restorative.",
        "recorded_observations": [
            {"kind": "node", "id": "wonder-engine", "claim": "Discovery creates awe."}
        ],
        "hypotheses": [
            {"title": "Restorative knowledge",
             "description": "Discovery may restore shared understanding."},
        ],
        "uncertainties": ["The existing candidate does not establish this effect."],
    }
    return build_host_agent_response(
        request, json.dumps(candidate), runtime="integration-test", model="UNAVAILABLE"
    ).model_dump()


def test_inquiry_prepare_does_not_replace_architecture_or_mark_review_ready(tmp_path):
    store = seeded_store(tmp_path)
    before = project_architecture(store)
    projection = prepare_architecture_inquiry(store, intent(store))
    assert projection["status"] == "awaiting_host_agent"
    assert projection["request"]["role"] == "studio_architecture_inquiry"
    assert projection["authority"] == "noncanonical_inquiry_not_working_architecture"
    assert project_architecture(store) == before


def test_completed_inquiry_returns_provenance_and_preserves_working_architecture(tmp_path):
    store = seeded_store(tmp_path)
    before = project_architecture(store)
    pending = prepare_architecture_inquiry(store, intent(store))
    after = complete_architecture_inquiry(store, packet(pending))
    assert after["status"] == "ready"
    assert after["result"]["hypotheses"][0]["title"] == "Restorative knowledge"
    observation = after["result"]["recorded_observations"][0]
    assert observation["sourceRef"] == "nodes/0"
    assert observation["interpretation_status"] == "agent_claim_not_causal_proof"
    assert project_architecture(store) == before


def test_inquiry_completion_is_idempotent_but_new_contents_conflict(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store))
    completed_packet = packet(pending)
    first = complete_architecture_inquiry(store, completed_packet)
    assert complete_architecture_inquiry(store, completed_packet) == first
    changed = dict(completed_packet, text=json.dumps({
        "schema_version": 1, "analysis": "Different interpretation",
        "recorded_observations": [], "hypotheses": [], "uncertainties": [],
    }))
    with pytest.raises(BeginnerConcurrencyError, match="different inquiry response"):
        complete_architecture_inquiry(store, changed)


def test_unsupported_recorded_observation_fails_closed(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store))
    bad = {
        "schema_version": 1, "analysis": "Some analysis",
        "recorded_observations": [
            {"kind": "link", "id": "invented_link", "claim": "A causal connection"}
        ],
        "hypotheses": [], "uncertainties": [],
    }
    with pytest.raises(ValueError, match="not found"):
        complete_architecture_inquiry(store, packet(pending, bad))
    assert project_architecture_inquiry(store)["status"] == "awaiting_host_agent"


def test_inquiry_wrong_canvas_or_revision_action_is_rejected(tmp_path):
    store = seeded_store(tmp_path)
    cross_canvas = intent(store)
    cross_canvas["canvas_id"] = "someone-else"
    with pytest.raises(ValueError, match="canvas ID mismatch"):
        prepare_architecture_inquiry(store, cross_canvas)
    with pytest.raises(ValueError, match="inquiry must not be a revision"):
        prepare_architecture_inquiry(store, intent(store, operation="revise"))


def test_inquiry_rejects_unverified_source_identity_before_writing_request(tmp_path):
    store = seeded_store(tmp_path)
    stale = intent(store)
    stale["expected_candidate_request_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="SHA mismatch"):
        prepare_architecture_inquiry(store, stale)
    assert project_architecture_inquiry(store)["status"] == "not_started"


def test_source_change_marks_prepared_inquiry_stale_and_rejects_completion(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store))
    working = store.load()
    item = working.items[0].model_dump(mode="json")
    item["content"] += " Changed source material."
    store.apply("update-item", expected_revision=working.revision,
                command_id="mutate-vision-after-inquiry", payload={"item": item})
    assert project_architecture_inquiry(store)["status"] == "stale"
    assert project_architecture_inquiry(store)["request"] is None
    with pytest.raises(BeginnerConcurrencyError, match="context changed"):
        complete_architecture_inquiry(store, packet(pending))
    assert project_architecture_inquiry(store)["status"] == "stale"


def test_superseding_inquiry_request_invalidates_old_response(tmp_path):
    store = seeded_store(tmp_path)
    first = prepare_architecture_inquiry(store, intent(store))
    another = intent(store)
    another["author_text"] = "What is a different alternative?"
    latest = prepare_architecture_inquiry(store, another)
    assert latest["request_sha256"] != first["request_sha256"]
    with pytest.raises(ValueError, match="different request"):
        complete_architecture_inquiry(store, packet(first))


def test_completed_inquiry_is_not_architecture_candidate(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store))
    bad = valid_candidate()
    with pytest.raises(Exception):
        complete_architecture_inquiry(store, packet(pending, bad))
    assert project_architecture(store)["status"] == "ready"
