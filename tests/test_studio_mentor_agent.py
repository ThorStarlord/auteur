"""Contract and authority tests for the scoped Studio host-agent mentorship lane."""
import json
import pytest

from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_store import CanvasStore
from auteur.beginner.studio_mentor import (
    MentorAdvice, complete_mentor, prepare_mentor, project_mentor,
)


def working(tmp_path):
    store = CanvasStore(tmp_path, "mentor-test")
    store.create()
    vision = {"id": "story-vision", "kind": "note", "title": "Story Vision",
              "content": "Hope, generosity, companion agency"}
    store.apply("create-item", expected_revision=0, command_id="vision",
                payload={"item": vision, "position": {"x": 10, "y": 20}})
    hero = {"id": "hero", "kind": "note", "title": "Generous hero",
            "content": "Helping others become independent", "architecture_role": "theme"}
    store.apply("create-item", expected_revision=1, command_id="hero",
                payload={"item": hero, "position": {"x": 40, "y": 60}})
    return store


def packet(request, *, kind="explore", source_refs=None, directions=None, **overrides):
    doc = {"schema_version": 1, "focus_id": "hero", "kind": kind,
           "summary": "Generosity can cause several narrative transformations.",
           "explanation": "Working story interpretation, not accepted canon.",
           "question": "How can independence grow without making help meaningless?",
           "challenge": None, "challenge_basis": "conditional_hypothesis",
           "author_reply_interpretation": None,
           "directions": directions if directions is not None else [
               {"id": "social", "title": "Community restoration",
                "mechanism": "Help scales through shared institutions.",
                "consequence": "New people can help others.",
                "tradeoff": "The hero must share agency.",
                "divergence_axis": "social_scale",
                "source_status": "agent_hypothesis", "source_refs": []}],
           "source_refs": source_refs or [], "limitation": "A creative hypothesis only."}
    doc.update(overrides)
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(doc)).model_dump()


def test_prepare_uses_actual_working_context_without_mutating_canvas(tmp_path):
    store = working(tmp_path)
    before = store.load().model_dump(mode="json")
    pending = prepare_mentor(store, "hero", "working", "explore")
    assert pending["status"] == "awaiting_host_agent"
    request = pending["request"]
    assert request["role"] == "studio_mentor"
    assert "No accepted" in request["system"]
    ctx = json.loads(request["user"])
    assert ctx["working_context"]["accepted_identity_status"] == "not_bound"
    assert ctx["working_context"]["author_story_vision"].startswith("Hope")
    assert ctx["working_context"]["focus"]["authority"] == "author_working"
    assert store.load().model_dump(mode="json") == before


def test_valid_advice_is_noncanonical_and_replay_idempotent(tmp_path):
    store = working(tmp_path)
    request = prepare_mentor(store, "hero", "working")["request"]
    payload = packet(request)
    before = store.load().model_dump(mode="json")
    ready = complete_mentor(store, payload)
    assert ready["status"] == "ready"
    assert ready["advice"]["directions"][0]["divergence_axis"] == "social_scale"
    assert complete_mentor(store, payload)["advice"] == ready["advice"]
    assert store.load().model_dump(mode="json") == before


def test_stale_reply_is_retained_as_stale_not_shown_as_fresh(tmp_path):
    store = working(tmp_path)
    request = prepare_mentor(store, "hero", "working", "followup", "Keep hopeful.")["request"]
    updated = store.load()
    original = next(i for i in updated.items if i.id == "hero")
    store.apply("update-item", expected_revision=updated.revision, command_id="edit-hero",
                payload={"item": {**original.model_dump(), "content": "A changed direction"}})
    with pytest.raises(BeginnerConcurrencyError, match="stale"):
        complete_mentor(store, packet(request))
    assert project_mentor(store)["status"] == "stale"
    assert project_mentor(store)["advice"] is None


def test_wrong_focus_and_fabricated_source_are_rejected(tmp_path):
    store = working(tmp_path)
    request = prepare_mentor(store, "hero", "working")["request"]
    with pytest.raises(ValueError, match="focus"):
        complete_mentor(store, packet(request, focus_id="someone-else"))
    with pytest.raises(ValueError, match="unavailable"):
        complete_mentor(store, packet(request, source_refs=["links/999"]))


def test_source_bound_alternative_needs_real_source(tmp_path):
    store = working(tmp_path)
    request = prepare_mentor(store, "hero", "working")["request"]
    direction = {"id": "better", "title": "Independence",
                 "mechanism": "Help develops agency.", "consequence": "New choices.",
                 "tradeoff": "Less direct control.", "divergence_axis": "character_agency",
                 "source_status": "source_bound_proposal", "source_refs": []}
    with pytest.raises(ValueError, match="provenance"):
        complete_mentor(store, packet(request, directions=[direction]))
    direction["source_refs"] = ["canvas/items/hero"]
    assert complete_mentor(store, packet(request, directions=[direction]))["status"] == "ready"


def test_challenge_cannot_claim_proposal_tension_without_tension_edge(tmp_path):
    store = working(tmp_path)
    request = prepare_mentor(store, "hero", "working", "challenge")["request"]
    with pytest.raises(ValueError, match="tension"):
        complete_mentor(store, packet(request, kind="challenge",
            challenge="Does generosity undermine agency?", challenge_basis="proposed_tension",
            source_refs=["canvas/items/hero"], directions=[]))


def test_empty_exploration_and_inconsistent_nonintervention_rejected():
    with pytest.raises(ValueError, match="direction"):
        MentorAdvice.model_validate({
            "focus_id": "hero", "kind": "explore", "summary": "Only a repeated idea.",
            "directions": []})
    with pytest.raises(ValueError, match="no_intervention"):
        MentorAdvice.model_validate({
            "focus_id": "hero", "kind": "no_intervention", "summary": "Nothing needed.",
            "challenge": "Yet you must change your story."})


def test_unknown_focus_invalid_kind_and_overlong_reply_fail_closed(tmp_path):
    store = working(tmp_path)
    for args in [("missing", "working", "explore", ""),
                 ("hero", "candidate", "explore", ""),
                 ("hero", "working", "explore", "x" * 2001)]:
        with pytest.raises(ValueError):
            prepare_mentor(store, *args)
    assert project_mentor(store)["status"] == "not_started"
