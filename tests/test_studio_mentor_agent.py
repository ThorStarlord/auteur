"""Contract and authority tests for the scoped Studio host-agent mentorship lane."""
import json
import pytest

from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_store import CanvasStore
from auteur.beginner.studio_mentor import (
    MentorAdvice, _context, complete_mentor, prepare_mentor, project_mentor,
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
                "distinguishing_factor": "An institutional ripple instead of personal strength.",
                "divergence_axis": "social_scale",
                "source_status": "agent_hypothesis", "source_refs": []}],
           "source_refs": source_refs or [], "limitation": "A creative hypothesis only."}
    doc.update(overrides)
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(doc)).model_dump()



def test_mentor_request_never_converts_author_virtue_to_mandatory_flaw(tmp_path):
    store = working(tmp_path)
    pending = prepare_mentor(store, "hero", "working", "explore")
    system = pending["request"]["system"]
    assert "Do not turn an author-declared virtue into a mandatory starting flaw" in system
    assert "growth without an initial moral failure" in system
    assert "optional dramatic tension" in system

def test_prepare_uses_actual_working_context_without_mutating_canvas(tmp_path):
    store = working(tmp_path)
    before = store.load().model_dump(mode="json")
    pending = prepare_mentor(store, "hero", "working", "explore")
    assert pending["status"] == "awaiting_host_agent"
    request = pending["request"]
    assert request["role"] == "studio_mentor"
    assert "Never claim accepted Identity exists" in request["system"]
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
                 "tradeoff": "Less direct control.",
                 "distinguishing_factor": "Companion agency rather than community scale.",
                 "divergence_axis": "character_agency",
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

def test_explore_rejects_relabelled_duplicate_mechanisms():
    example = {"focus_id": "hero", "kind": "explore", "summary": "Two directions",
               "directions": [
                   {"id": "one", "title": "Institutional generosity",
                    "mechanism": "Helpers establish mutual-aid institutions",
                    "consequence": "Distributed support", "tradeoff": "Less direct power",
                    "distinguishing_factor": "Social institutions", "divergence_axis": "social_scale"},
                   {"id": "two", "title": "Community support",
                    "mechanism": "Helpers establish mutual-aid institutions",
                    "consequence": "Distributed support", "tradeoff": "Less direct power",
                    "distinguishing_factor": "Collective agency", "divergence_axis": "social_scale"},
               ]}
    with pytest.raises(ValueError, match="same mechanism"):
        MentorAdvice.model_validate(example)
    example["directions"][1]["mechanism"] = "Helpers challenge their old leader"
    example["directions"][1]["distinguishing_factor"] = ""
    with pytest.raises(ValueError, match="differentiator"):
        MentorAdvice.model_validate(example)


def test_disclosed_working_sources_are_the_only_citable_canvas_sources(tmp_path):
    store = working(tmp_path)
    for i in range(13):
        current = store.load()
        store.apply(
            "create-item", expected_revision=current.revision,
            command_id=f"extra-{i}",
            payload={"item": {"id": f"extra-{i}", "kind": "note",
                              "title": f"Idea {i}", "content": f"Private detail {i}"},
                     "position": {"x": 20, "y": 40}},
        )
    snapshot = _context(store, "hero", "working")
    seen = snapshot["context"]["working_ideas"]
    assert len(seen) == 10
    assert "canvas/items/hero" in snapshot["allowed_refs"]
    assert "canvas/items/story-vision" in snapshot["allowed_refs"]
    assert "canvas/items/extra-12" not in snapshot["allowed_refs"]
    assert len([r for r in snapshot["allowed_refs"] if r.startswith("canvas/items/")]) == 11


def test_stale_candidate_never_contributes_proposals_or_refs(tmp_path, monkeypatch):
    store = working(tmp_path)
    candidate = {
        "nodes": [
            {"id": "n1", "title": "False genre rule", "summary": "Stale proposal"},
            {"id": "n2", "title": "Another rule", "summary": "Old idea"},
        ],
        "links": [{"source": "n1", "target": "n2", "function": "contrasts"}],
        "open_questions": ["Old question"],
    }
    monkeypatch.setattr(
        "auteur.beginner.studio_mentor.project_architecture",
        lambda _store: {"status": "stale", "candidate": candidate,
                        "candidate_request_sha256": "b" * 64},
    )
    snapshot = _context(store, "hero", "working")
    ctx = snapshot["context"]
    assert ctx["candidate_status"] == "stale"
    assert ctx["candidate_request_sha256"] is None
    assert ctx["proposed_relations"] == []
    assert ctx["proposed_questions"] == []
    assert "links/0" not in snapshot["allowed_refs"]
    assert "open_questions/0" not in snapshot["allowed_refs"]
    assert "nodes/n1" not in snapshot["allowed_refs"]


def test_ready_candidate_cites_only_disclosed_neighbor_links_and_questions(tmp_path, monkeypatch):
    store = working(tmp_path)
    candidate = {
        "nodes": [
            {"id": "focus", "title": "Heroism", "summary": "Generous heroism"},
            {"id": "agency", "title": "Independence", "summary": "Agency"},
            {"id": "unrelated", "title": "Unrelated", "summary": "Not shown"},
        ],
        "links": [{"source": "focus", "target": "agency", "function": "contrasts"}],
        "open_questions": [f"Question {i}" for i in range(11)],
    }
    monkeypatch.setattr(
        "auteur.beginner.studio_mentor.project_architecture",
        lambda _store: {"status": "ready", "candidate": candidate,
                        "candidate_request_sha256": "c" * 64},
    )
    snapshot = _context(store, "focus", "candidate")
    ctx = snapshot["context"]
    assert ctx["candidate_request_sha256"] == "c" * 64
    assert ctx["proposed_relations"][0]["other_title"] == "Independence"
    assert ctx["proposed_relations"][0]["authority"] == "agent_candidate"
    assert len(ctx["proposed_questions"]) == 8
    assert "open_questions/7" in snapshot["allowed_refs"]
    assert "open_questions/10" not in snapshot["allowed_refs"]
    assert "links/0" in snapshot["allowed_refs"]
    assert "nodes/agency" in snapshot["allowed_refs"]
    assert "nodes/unrelated" not in snapshot["allowed_refs"]


def test_missing_response_envelope_fields_are_400_class_errors(tmp_path):
    store = working(tmp_path)
    prepare_mentor(store, "hero", "working")
    with pytest.raises(ValueError, match="malformed mentor host-agent response"):
        complete_mentor(store, {"schema": "auteur_host_agent_response_v1"})
    assert project_mentor(store)["status"] == "awaiting_host_agent"

def test_working_id_collision_does_not_inherit_candidate_edges(tmp_path, monkeypatch):
    store = working(tmp_path)
    # Both owner namespaces independently use "hero"; equality of spelling
    # is not evidence that the author working note is the AI candidate node.
    candidate = {
        "nodes": [
            {"id": "hero", "title": "Agent's unrelated hero", "summary": "Other concept"},
            {"id": "other", "title": "Agent's other node", "summary": "No working link"},
        ],
        "links": [{"source": "hero", "target": "other", "function": "contrasts"}],
        "open_questions": ["Question about the candidate, not the note"],
    }
    monkeypatch.setattr(
        "auteur.beginner.studio_mentor.project_architecture",
        lambda _store: {"status": "ready", "candidate": candidate,
                        "candidate_request_sha256": "d" * 64},
    )
    snapshot = _context(store, "hero", "working")
    assert snapshot["context"]["focus"]["authority"] == "author_working"
    assert snapshot["context"]["proposed_relations"] == []
    assert snapshot["context"]["proposed_questions"] == []
    assert "links/0" not in snapshot["allowed_refs"]
    assert "nodes/other" not in snapshot["allowed_refs"]
    assert "open_questions/0" not in snapshot["allowed_refs"]

@pytest.mark.parametrize("field,bad", [
    ("text", None),
    ("elapsed_seconds", "not-a-number"),
])
def test_malformed_host_agent_values_do_not_become_server_errors(tmp_path, field, bad):
    store = working(tmp_path)
    pending = prepare_mentor(store, "hero", "working")
    request = HostAgentRequest(**pending["request"])
    envelope = build_host_agent_response(request, "{}").model_dump()
    envelope[field] = bad
    with pytest.raises(ValueError, match="malformed mentor host-agent response"):
        complete_mentor(store, envelope)
    assert project_mentor(store)["status"] == "awaiting_host_agent"
    assert store.load().revision == 2
