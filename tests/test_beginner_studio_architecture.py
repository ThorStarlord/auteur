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
    ArchitectureCandidate, apply_architecture_review, complete_architecture,
    main, prepare_architecture, project_architecture,
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
    assert "coherent, revisable provisional defaults" in waiting["request"]["system"]
    assert "Reserve open_questions for genuinely authorial preferences" in waiting["request"]["system"]
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
    assert finished["status"] == "review_ready"
    assert finished["candidate"]["nodes"][0]["summary"] == candidate()["nodes"][0]["summary"]
    assert finished["review"]["changes"]["nodes"]["changed"] == ["engine"]
    assert finished["review"]["candidate"]["nodes"][0]["summary"].endswith("cost.")
    applied = apply_architecture_review(store, finished["review"]["request_sha256"])
    assert applied["status"] == "ready"
    assert applied["candidate"]["nodes"][0]["summary"].endswith("cost.")
    history = store.directory / "architecture" / "requests" / first["request"]["request_sha256"]
    assert (history / "response.json").exists()



def test_stale_review_apply_does_not_replace_working_architecture(tmp_path):
    store = working_store(tmp_path)
    first = prepare_architecture(store)
    complete_architecture(store, response(first))
    revision = prepare_architecture(store, "Make horror more prominent.")
    changed = candidate()
    changed["nodes"][0]["summary"] = "The supernatural threat overtakes the mystery."
    pending = complete_architecture(store, response(revision, changed))
    assert pending["status"] == "review_ready"
    canvas = store.load()
    altered = canvas.items[0].model_copy(update={"content": "A different author vision."})
    store.apply("update-item", expected_revision=canvas.revision,
                command_id="changed-since-review",
                payload={"item": altered.model_dump(mode="json")})
    with pytest.raises(BeginnerConcurrencyError, match="working context changed"):
        apply_architecture_review(store, pending["review"]["request_sha256"])
    assert project_architecture(store)["candidate"]["nodes"][0]["summary"] != changed["nodes"][0]["summary"]
    assert not (tmp_path / "story_identity.yaml").exists()

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
        _, revision = _call(base, "POST", prefix + "/prepare", {"instruction": "More dread."})
        _, review = _call(base, "POST", prefix + "/host-agent-response", response(revision))
        assert review["status"] == "review_ready"
        _, applied = _call(base, "POST", prefix + "/apply",
                           {"request_sha256": review["review"]["request_sha256"]})
        assert applied["status"] == "ready"
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def test_host_coding_agent_can_complete_raw_candidate_file_via_cli(tmp_path, capsys):
    store = working_store(tmp_path)
    arguments = ["--project", str(tmp_path), "--canvas", "story-one"]
    assert main(arguments + ["prepare"]) == 0
    assert project_architecture(store)["status"] == "awaiting_host_agent"
    packet = json.loads(capsys.readouterr().out)
    assert packet["request"]["role"] == "studio_architecture"
    raw = tmp_path / "candidate.json"
    raw.write_text(json.dumps(candidate()), encoding="utf-8")
    assert main(arguments + ["complete-file", "--candidate", str(raw)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "ready"
    assert output["candidate"]["nodes"][0]["id"] == "engine"


def emotion_first_candidate():
    """Architecture contracts describe mechanisms, not fictional instantiation."""
    return {
        "schema_version": 2,
        "summary": "Heroic generosity gives meaning to earned progression.",
        "nodes": [
            {"id": "progression", "title": "Progression Fantasy", "category": "genre",
             "summary": "New capability changes the range of possible action."},
            {"id": "heroic", "title": "Heroic Fantasy", "category": "genre",
             "summary": "Moral choices make growing power consequential."},
            {"id": "growth", "title": "Renewable growth", "category": "engine",
             "summary": "Each breakthrough changes the kinds of challenges available."},
        ],
        "links": [{"id": "growth_support", "source": "growth", "target": "progression",
                   "function": "supports"}],
        "emotion_targets": [
            {"id": "joy_growth", "emotion": "joy", "role": "primary",
             "intended_effect": "Satisfaction from earned progress.",
             "eliciting_condition": "A breakthrough changes what actions are possible.",
             "aesthetic_strategy": "Give effort and its consequence clear contrast.",
             "provenance": "agent_proposed"},
            {"id": "anger_injustice", "emotion": "anger", "role": "supporting",
             "intended_effect": "Opposition to consequential injustice.",
             "eliciting_condition": "A meaningful moral wrong creates pressure.",
             "aesthetic_strategy": "Contrast avoidable harm with principled action.",
             "provenance": "agent_proposed"},
        ],
        "complex_emotions": [
            {"id": "vindication", "title": "Righteous vindication",
             "basic_emotions": ["anger", "joy"],
             "context": "Justified opposition followed by consequential success."},
        ],
        "genre_contracts": [
            {"genre_node_id": "progression", "role": "governing",
             "emotion_target_ids": ["joy_growth"], "complex_emotion_ids": [],
             "trope_functions": ["Effort creates qualitative growth."],
             "narrative_engine": "Challenges demand changing capabilities.",
             "structural_pattern": "Challenge, attempt, growth, changed possibilities.",
             "aesthetic_strategies": ["Contrast uncertainty with competence."],
             "payoff_expectations": ["Earned transformation matters."]},
            {"genre_node_id": "heroic", "role": "supporting",
             "emotion_target_ids": ["anger_injustice"],
             "complex_emotion_ids": ["vindication"],
             "trope_functions": ["Mercy tests the use of power."],
             "narrative_engine": "Ethics are tested under changing pressure.",
             "structural_pattern": "Pressure, choice, consequence, renewed demand.",
             "aesthetic_strategies": ["Show tangible human stakes."],
             "payoff_expectations": ["Heroic choices produce meaningful outcomes."]},
        ],
        "genre_interactions": [
            {"id": "ethical_constraint", "source_genre_id": "heroic",
             "target_genre_id": "progression", "kind": "constrains",
             "mechanism": "The ethics of generosity prevent growth from reducing to domination.",
             "risk": "Increasing power can erase meaningful moral tension."},
        ],
        "phases": [
            {"id": "emerging_growth", "title": "Emerging growth", "order": 0,
             "narrative_function": "Connect new agency to moral responsibility.",
             "genre_activations": [
                 {"genre_node_id": "progression", "basic_emotions": ["joy"],
                  "trope_functions": ["Earned breakthrough"],
                  "structural_function": "Establish meaningful advancement."},
                 {"genre_node_id": "heroic", "basic_emotions": ["anger", "joy"],
                  "trope_functions": ["Protection and generosity"],
                  "structural_function": "Give advancements an ethical purpose."},
             ]},
        ],
        "open_questions": ["How much progression is public versus private?"],
    }


def test_v2_emotion_first_architecture_and_legacy_v1_remain_readable():
    modern = ArchitectureCandidate.model_validate(emotion_first_candidate())
    assert modern.schema_version == 2
    assert modern.complex_emotions[0].basic_emotions == ["anger", "joy"]
    assert modern.genre_interactions[0].kind == "constrains"
    assert ArchitectureCandidate.model_validate(candidate()).schema_version == 1


def test_v2_rejects_non_basic_emotions_and_premature_concrete_categories():
    bad = emotion_first_candidate()
    bad["emotion_targets"][0]["emotion"] = "awe"
    with pytest.raises(ValidationError):
        ArchitectureCandidate.model_validate(bad)
    bad = emotion_first_candidate()
    bad["nodes"][0]["category"] = "character"
    with pytest.raises(ValidationError, match="cannot instantiate"):
        ArchitectureCandidate.model_validate(bad)
    bad = emotion_first_candidate()
    bad["complex_emotions"][0]["basic_emotions"] = ["joy", "joy"]
    with pytest.raises(ValidationError, match="distinct"):
        ArchitectureCandidate.model_validate(bad)


def test_v2_rejects_dangling_genre_interactions_and_emotional_references():
    bad = emotion_first_candidate()
    bad["genre_interactions"][0]["target_genre_id"] = "absent"
    with pytest.raises(ValidationError, match="two distinct"):
        ArchitectureCandidate.model_validate(bad)
    bad = emotion_first_candidate()
    bad["genre_contracts"][0]["emotion_target_ids"] = ["absent"]
    with pytest.raises(ValidationError, match="unknown basic"):
        ArchitectureCandidate.model_validate(bad)
    bad = emotion_first_candidate()
    bad["phases"][0]["genre_activations"][0]["genre_node_id"] = "absent"
    with pytest.raises(ValidationError, match="unknown genre"):
        ArchitectureCandidate.model_validate(bad)


def test_v2_agent_request_and_candidate_are_source_bound(tmp_path):
    store = working_store(tmp_path)
    pending = prepare_architecture(store)
    assert "schema_version=2" in pending["request"]["system"]
    assert "Never invent names of characters" in pending["request"]["system"]
    result = complete_architecture(store, response(pending, emotion_first_candidate()))
    assert result["candidate"]["schema_version"] == 2
    assert result["candidate"]["genre_contracts"][0]["genre_node_id"] == "progression"
    assert not (tmp_path / "story_identity.yaml").exists()


def test_revision_diff_covers_emotions_genres_and_cross_genre_mechanisms():
    from auteur.beginner.studio_architecture import _candidate_diff
    old = emotion_first_candidate()
    import copy
    updated = copy.deepcopy(old)
    updated["emotion_targets"][0]["intended_effect"] = "Joy from more consequential progress."
    updated["genre_contracts"][0]["narrative_engine"] = "Each new ability changes the ethical conflict."
    updated["genre_interactions"][0]["mechanism"] = "Heroism actively reframes progression."
    updated["complex_emotions"].append({
        "id": "awe", "title": "Heroic awe", "basic_emotions": ["joy", "surprise"],
        "context": "Wonder and satisfaction accompany a consequential breakthrough.",
    })
    changes = _candidate_diff(old, updated)
    assert changes["emotion_targets"]["changed"] == ["joy_growth"]
    assert changes["genre_contracts"]["changed"] == ["progression"]
    assert changes["genre_interactions"]["changed"] == ["ethical_constraint"]
    assert changes["complex_emotions"]["added"] == ["awe"]
    assert not changes["nodes"]["changed"]


def test_architecture_becomes_stale_after_author_revises_vision(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, emotion_first_candidate()))
    doc = store.load()
    modified = doc.items[0].model_copy(update={"content": "New emotional goals."})
    store.apply("update-item", expected_revision=doc.revision, command_id="new-goals",
                payload={"item": modified.model_dump(mode="json")})
    old = project_architecture(store)
    assert old["status"] == "stale"
    assert old["candidate"]["schema_version"] == 2
