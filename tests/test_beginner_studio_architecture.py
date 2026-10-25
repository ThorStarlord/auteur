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
    ArchitectureCandidate, ArchitectureLink, _digest, _source, _source_fingerprint,
    apply_architecture_review, complete_architecture,
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


def candidate(schema_version=2):
    return {
        "schema_version": schema_version,
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


def write_legacy_current(store, waiting, legacy_candidate):
    architecture = store.directory / "architecture"
    (architecture / "current.json").write_text(json.dumps({
        "request_sha256": waiting["request"]["request_sha256"],
        "source_sha256": waiting["request"]["settings"]["source_sha256"],
        "candidate": legacy_candidate,
    }), encoding="utf-8")


def test_prose_first_architecture_request_labels_truncated_and_omitted_sources(tmp_path):
    store = working_store(tmp_path)
    original_scene = "The rescue happened at the first bell. " + "a" * 1060
    for index in range(25):
        store.apply(
            "create-item", expected_revision=store.load().revision,
            command_id=f"source-{index}",
            payload={"item": {
                "id": f"working-scene-{index}", "kind": "scene",
                "title": f"Manuscript source {index}",
                "content": original_scene if index == 0 else f"Scene {index} is provisional.",
            }, "position": {"x": 40 + index, "y": 100 + index}},
        )

    prepared = prepare_architecture(store)
    user = json.loads(prepared["request"]["user"])
    working = user["working_context"]
    assert working["working_source_format"] == 2
    assert len(working["working_items"]) == 24
    assert working["omitted_working_item_count"] == 1
    assert len(working["omitted_working_items_sha256"]) == 64
    excerpt = working["working_items"][0]
    assert excerpt["id"] == "working-scene-0"
    assert excerpt["content"] == original_scene[:1000]
    assert excerpt["content_characters"] == len(original_scene)
    assert excerpt["content_is_excerpt"] is True
    assert len(excerpt["full_content_sha256"]) == 64
    assert "working item IDs" in prepared["request"]["system"]
    assert "missing text" in prepared["request"]["system"]

    # Same-length edits entirely outside the excerpt are still source changes.
    before = store.load()
    item = next(item for item in before.items if item.id == "working-scene-0")
    modified = item.model_copy(update={"content": item.content[:-1] + "b"})
    store.apply(
        "update-item", expected_revision=before.revision, command_id="edit-unread-tail",
        payload={"item": modified.model_dump(mode="json")},
    )
    assert _source_fingerprint(store, prepared["request"]["user"]) != (
        prepared["request"]["settings"]["source_sha256"]
    )


def test_legacy_architecture_request_fingerprint_uses_original_source_projection(tmp_path):
    store = working_store(tmp_path)
    scene = "n" * 1100
    store.apply(
        "create-item", expected_revision=store.load().revision,
        command_id="legacy-scene", payload={"item": {
            "id": "legacy-prose", "kind": "scene", "title": "Prior manuscript",
            "content": scene,
        }, "position": {"x": 70, "y": 110}},
    )
    prepared = prepare_architecture(store)
    user = json.loads(prepared["request"]["user"])
    legacy = _source(store, source_format=1)
    assert "working_source_format" not in legacy
    assert legacy["working_items"][0]["content"] == scene[:1000]
    assert "content_is_excerpt" not in legacy["working_items"][0]
    user["working_context"] = legacy
    expected = _digest({
        "working_context": legacy,
        "narrative_design_context": user["narrative_design_context"],
    })
    assert _source_fingerprint(store, json.dumps(user)) == expected


def test_architecture_request_carries_source_grounded_ontology_not_hidden_author_choices(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    request = json.loads(waiting["request"]["user"])
    guidance = request["narrative_design_context"]
    assert guidance["authority"] == "derived_guidance_not_author_intent"
    assert guidance["accepted_story_identity"] is None
    assert guidance["architecture_preference_vocabulary"]["complexity"] == [
        "focused", "layered", "maximalist",
    ]
    assert guidance["architecture_preference_vocabulary"]["causal_distribution"] == [
        "concentrated", "layered", "mixed",
    ]
    assert guidance["architecture_preference_vocabulary"]["engine_hierarchy"] == [
        "single_center", "primary_with_layers", "ensemble",
    ]
    refs = [source["source_ref"] for source in guidance["source_principles"]]
    assert "docs/narrative-architecture.md" in refs
    assert "docs/plans/story-discovery-intent-aware-architecture.md" in refs
    assert "docs/adr/008-rich-target-experience.md" in refs
    assert "data/ontology/base_ontology.yaml" in refs
    principle_three = guidance["source_principles"][2]["principle"]
    system_prompt = " ".join(waiting["request"]["system"].split())
    assert "a single center" in principle_three
    assert "a primary engine with subordinate layers" in principle_three
    assert "an ensemble of co-governing mechanisms" in principle_three
    assert "hierarchy or its deliberate absence" in principle_three
    assert "instead of treating all mechanisms as equally central" not in principle_three
    assert "instead of treating all mechanisms as equally central" not in system_prompt
    assert "accepted engine_hierarchy preference" in system_prompt
    assert "ensemble of co-governing mechanisms" in system_prompt
    assert "subordinate parts interact" not in system_prompt
    assert "label that organization as an agent proposal" in system_prompt
    assert "Never manufacture a dominant engine the material does not support" in system_prompt
    assert "ArchitectureLink.function must contain 1–120 characters" in system_prompt
    assert "concisely describe the relation from source to target" in system_prompt
    assert "Put longer explanatory prose in appropriate narrative description fields" in system_prompt
    function_schema = ArchitectureLink.model_json_schema()["properties"]["function"]
    assert function_schema["minLength"] == 1
    assert function_schema["maxLength"] == 120
    assert "UNKNOWN" in guidance["unknown_policy"]
    assert request["working_context"]["vision"].startswith("A long fantasy")
    assert waiting["request"]["settings"]["source_sha256"] == _source_fingerprint(
        store, waiting["request"]["user"],
    )


def test_accepted_story_preferences_and_target_experience_are_grounded(tmp_path):
    from auteur.identity import StoryIdentity

    store = working_store(tmp_path)
    identity = StoryIdentity.model_validate({
        "title": "Architecture source",
        "core_answer": "Shared inquiry changes what a community protects.",
        "story_type": {"genre": "mystery", "medium": "novel", "mode": "tragic"},
        "central_engine": {
            "want": "Protect everyone", "resistance": "Incomplete evidence",
            "conflict": "Care risks control", "stakes": "Trust and freedom",
            "change": "A revisable decision process",
        },
        "target_experience": {
            "primary_emotional_promise": "uncertain compassion",
            "secondary_palette": ["hope", "curiosity"],
            "emotional_trajectory": {
                "pattern": "deepening",
                "start": "unease", "midpoint": "ethical pressure",
                "ending": "earned hope",
            },
        },
        "architecture_preferences": {
            "complexity": "maximalist", "causal_distribution": "mixed",
        },
        "hard_constraints": ["No intervention guarantees safety"],
    })
    identity.to_yaml(tmp_path / "story_identity.yaml")
    prepared = prepare_architecture(store)
    packet = json.loads(prepared["request"]["user"])
    accepted = packet["narrative_design_context"]["accepted_story_identity"]
    assert accepted["source_ref"] == "story_identity.yaml"
    assert accepted["authority"] == "accepted_story_identity"
    assert accepted["architecture_preferences"] == {
        "complexity": "maximalist", "causal_distribution": "mixed",
    }
    assert accepted["target_experience"]["primary_emotional_promise"] == "uncertain compassion"
    assert accepted["target_experience"]["emotional_trajectory"]["ending"] == "earned hope"
    assert accepted["hard_constraints"] == ["No intervention guarantees safety"]
    assert "engine_hierarchy" not in accepted["architecture_preferences"]

    identity.hard_constraints.append("Refusal can change the process")
    identity.to_yaml(tmp_path / "story_identity.yaml")
    with pytest.raises(BeginnerConcurrencyError, match="story"):
        complete_architecture(store, response(prepared))
    assert project_architecture(store)["candidate"] is None
    sha = prepared["request"]["request_sha256"]
    assert (store.directory / "architecture" / "requests" / sha / "stale_response.json").exists()


def test_omitted_identity_defaults_are_not_attributed_to_author(tmp_path):
    store = working_store(tmp_path)
    minimal = {
        "title": "Only an explicit central engine",
        "core_answer": "Mutual responsibility matters.",
        "central_engine": {
            "want": "Act with care", "resistance": "Uncertainty",
            "conflict": "Care and control", "stakes": "Trust",
            "change": "Shared accountability",
        },
    }
    (tmp_path / "story_identity.yaml").write_text(json.dumps(minimal), encoding="utf-8")
    status = prepare_architecture(store)
    accepted = json.loads(status["request"]["user"])[
        "narrative_design_context"
    ]["accepted_story_identity"]
    assert accepted["core_answer"] == "Mutual responsibility matters."
    assert accepted["story_type"] is None
    assert accepted["target_experience"] is None
    assert accepted["architecture_preferences"] is None


def test_legacy_architecture_fingerprint_remains_readable(tmp_path):
    store = working_store(tmp_path)
    legacy_user = json.dumps({"working_context": {"previous_candidate": None}})
    assert _source_fingerprint(store, legacy_user) == _digest(_source(store, source_format=1))


def test_invalid_accepted_identity_is_not_silently_ignored(tmp_path):
    store = working_store(tmp_path)
    (tmp_path / "story_identity.yaml").write_text("title: incomplete", encoding="utf-8")
    with pytest.raises(ValidationError):
        prepare_architecture(store)


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


def test_new_develop_response_rejects_schema_v1_without_persisting(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    sha = waiting["request"]["request_sha256"]

    with pytest.raises(ValidationError, match="new Studio architecture responses must use schema_version 2"):
        complete_architecture(store, response(waiting, candidate(schema_version=1)))

    request_dir = store.directory / "architecture" / "requests" / sha
    assert not (request_dir / "response.json").exists()
    assert not (request_dir / "review.json").exists()
    assert not (store.directory / "architecture" / "current.json").exists()


def test_revision_response_rejects_schema_v1_and_preserves_v2_baseline(tmp_path):
    store = working_store(tmp_path)
    first = prepare_architecture(store)
    baseline = complete_architecture(store, response(first))
    revision = prepare_architecture(store, "Revise the supporting mechanism.")
    sha = revision["request"]["request_sha256"]

    with pytest.raises(ValidationError, match="new Studio architecture responses must use schema_version 2"):
        complete_architecture(store, response(revision, candidate(schema_version=1)))

    request_dir = store.directory / "architecture" / "requests" / sha
    assert not (request_dir / "response.json").exists()
    assert not (request_dir / "review.json").exists()
    current = project_architecture(store)
    assert current["candidate"] == baseline["candidate"]
    assert current["candidate_request_sha256"] == baseline["candidate_request_sha256"]


def test_stored_v1_current_and_review_artifacts_still_project_and_apply(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    legacy = ArchitectureCandidate.model_validate(
        candidate(schema_version=1)
    ).model_dump(mode="json")
    write_legacy_current(store, waiting, legacy)

    projection = project_architecture(store)
    assert projection["status"] == "ready"
    assert projection["candidate"]["schema_version"] == 1
    assert projection["candidate"]["summary"] == legacy["summary"]

    revision = prepare_architecture(store, "Revise this legacy proposal.")
    revised_legacy = {**legacy, "summary": "A revised legacy working proposal."}
    request_dir = store.directory / "architecture" / "requests" / revision["request"]["request_sha256"]
    (request_dir / "review.json").write_text(json.dumps({
        "request_sha256": revision["request"]["request_sha256"],
        "source_sha256": revision["request"]["settings"]["source_sha256"],
        "prior_request_sha256": waiting["request"]["request_sha256"],
        "candidate": revised_legacy,
        "changes": {},
    }), encoding="utf-8")

    applied = apply_architecture_review(store, revision["request"]["request_sha256"])

    assert applied["status"] == "ready"
    assert applied["candidate"]["schema_version"] == 1
    assert applied["candidate"]["summary"] == revised_legacy["summary"]


def test_identical_replay_of_stored_v1_response_remains_idempotent(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    sha = waiting["request"]["request_sha256"]
    legacy = candidate(schema_version=1)
    reply = response(waiting, legacy)
    request_dir = store.directory / "architecture" / "requests" / sha
    (request_dir / "response.json").write_text(json.dumps(reply), encoding="utf-8")
    write_legacy_current(
        store, waiting,
        ArchitectureCandidate.model_validate(legacy).model_dump(mode="json"),
    )

    replay = complete_architecture(store, reply)

    assert replay["status"] == "ready"
    assert replay["candidate"]["schema_version"] == 1



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


def test_http_rejects_new_v1_architecture_response_as_invalid_candidate(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        prefix = "/api/beginner/studio/canvases/story-one/architecture"
        working_store(tmp_path)
        _, waiting = _call(base, "POST", prefix + "/prepare", {})
        sha = waiting["request"]["request_sha256"]
        with pytest.raises(HTTPError) as rejected:
            _call(base, "POST", prefix + "/host-agent-response",
                  response(waiting, candidate(schema_version=1)))
        assert rejected.value.code == 400
        payload = json.loads(rejected.value.read().decode("utf-8"))
        assert "new Studio architecture responses must use schema_version 2" in payload["error"]
        request_dir = CanvasStore(tmp_path, "story-one").directory / "architecture" / "requests" / sha
        assert not (request_dir / "response.json").exists()
        assert not (request_dir / "review.json").exists()
        assert not (request_dir.parent.parent / "current.json").exists()
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

    baseline = output["candidate"]
    assert main(arguments + ["prepare", "--instruction", "Revise the engine."]) == 0
    capsys.readouterr()
    raw.write_text(json.dumps(candidate(schema_version=1)), encoding="utf-8")
    with pytest.raises(ValidationError, match="new Studio architecture responses must use schema_version 2"):
        main(arguments + ["complete-file", "--candidate", str(raw)])
    assert project_architecture(store)["candidate"] == baseline


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
    assert ArchitectureCandidate.model_validate(candidate(schema_version=1)).schema_version == 1


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


def test_design_context_fingerprint_tracks_principles_not_system_prompt(tmp_path, monkeypatch):
    import auteur.beginner.studio_architecture as studio_architecture

    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, emotion_first_candidate()))
    assert project_architecture(store)["status"] == "ready"

    monkeypatch.setattr(
        studio_architecture, "_SYSTEM",
        studio_architecture._SYSTEM + "\nAdditional operational instruction.",
    )
    assert project_architecture(store)["status"] == "ready"

    principles = list(studio_architecture._DESIGN_PRINCIPLES)
    source, principle = principles[2]
    principles[2] = (source, principle + " Keep the organization supported by evidence.")
    monkeypatch.setattr(studio_architecture, "_DESIGN_PRINCIPLES", tuple(principles))
    assert project_architecture(store)["status"] == "stale"
