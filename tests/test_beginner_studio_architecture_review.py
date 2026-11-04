"""Architecture revisions explain changed meanings without inventing causality."""
from __future__ import annotations

import copy
import json

from auteur.beginner.studio_architecture import (
    ArchitectureCandidate, complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_architecture_review import build_architecture_review
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


def working_store(tmp_path):
    store = CanvasStore(tmp_path, "story-one")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {
            "id": "story-vision", "kind": "note", "title": "Story Vision",
            "content": "Wonder gives way to dread, then earned hope.",
        }, "position": {"x": 20, "y": 50}},
    )
    return store


def candidate():
    return {
        "schema_version": 2,
        "summary": "Wonder survives contact with dread.",
        "nodes": [
            {"id": "wonder-engine", "title": "Wonder engine", "category": "engine",
             "summary": "Discovery creates awe."},
            {"id": "dread-engine", "title": "Dread engine", "category": "engine",
             "summary": "Threat turns discovery into danger."},
            {"id": "wonder-genre", "title": "Wonder genre", "category": "genre",
             "summary": "Wonder governs the opening."},
        ],
        "links": [{"id": "wonder-to-dread", "source": "wonder-engine",
                   "target": "dread-engine", "function": "raises the cost of wonder"}],
        "emotion_targets": [
            {"id": "wonder", "emotion": "joy", "role": "primary",
             "intended_effect": "Awe at a larger world.",
             "eliciting_condition": "Discovery reveals a wider possibility.",
             "aesthetic_strategy": "Scale and delayed revelation.",
             "provenance": "author_declared"},
            {"id": "dread", "emotion": "fear", "role": "supporting",
             "intended_effect": "Fear of what discovery costs.",
             "eliciting_condition": "A discovery reveals danger.",
             "aesthetic_strategy": "Intimate sensory contrast.",
             "provenance": "agent_proposed"},
        ],
        "complex_emotions": [
            {"id": "tragic-wonder", "title": "Tragic wonder",
             "basic_emotions": ["joy", "sadness"],
             "context": "A beautiful discovery carries loss."},
        ],
        "genre_contracts": [
            {"genre_node_id": "wonder-genre", "role": "governing",
             "emotion_target_ids": ["wonder"], "complex_emotion_ids": [],
             "trope_functions": ["The forbidden discovery"],
             "narrative_engine": "Discovery keeps widening the world.",
             "structural_pattern": "Discovery, awe, consequence.",
             "aesthetic_strategies": ["Vast scale against intimate cost."],
             "payoff_expectations": ["Wonder survives loss."]},
        ],
        "genre_interactions": [
            {"id": "genres-tension", "source_genre_id": "wonder-genre",
             "target_genre_id": "wonder-genre", "kind": "creates_tension",
             "mechanism": "Wonder resists explanation."},
        ],
        "phases": [
            {"id": "opening", "title": "Opening wonder", "order": 0,
             "narrative_function": "Establish awe.",
             "reader_experience": "Open wonder.",
             "transition": "A discovery turns costly."},
        ],
        "open_questions": ["How much wonder should survive the ending?"],
    }


def valid_candidate():
    result = candidate()
    result["genre_interactions"][0]["target_genre_id"] = "wonder-genre"
    result["nodes"].append({
        "id": "dread-genre", "title": "Dread genre", "category": "genre",
        "summary": "Dread pressures wonder.",
    })
    result["genre_contracts"].append({
        "genre_node_id": "dread-genre", "role": "supporting",
        "emotion_target_ids": ["dread"], "complex_emotion_ids": ["tragic-wonder"],
        "trope_functions": ["The cost of knowledge"],
        "narrative_engine": "Knowledge makes the world more dangerous.",
        "structural_pattern": "Discovery, threat, costly choice.",
        "aesthetic_strategies": ["Intimate menace."],
        "payoff_expectations": ["Wonder survives fear."],
    })
    result["genre_interactions"][0]["target_genre_id"] = "dread-genre"
    return result


def response(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data), runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def test_review_names_each_affected_component_with_before_after_meaning():
    previous = valid_candidate()
    proposed = copy.deepcopy(previous)
    proposed["summary"] = "Wonder becomes the dominant experience."
    proposed["emotion_targets"][0]["intended_effect"] = (
        "Wonder dominates fear without erasing its cost."
    )
    proposed["genre_contracts"][0]["narrative_engine"] = (
        "Discovery repeatedly restores wonder after fear."
    )
    proposed["genre_interactions"][0]["mechanism"] = (
        "Dread deepens wonder by making discovery costly."
    )
    proposed["phases"][0]["narrative_function"] = (
        "Establish wonder as the story's governing promise."
    )
    review = build_architecture_review(
        previous, proposed, "Make wonder dominate fear, preserving mystery.",
    )
    assert review["requested_change"] == "Make wonder dominate fear, preserving mystery."
    assert review["authority"] == "working_architecture_comparison_not_story_impact"
    changed = {(item["kind"], item["id"]): item for item in review["changed_components"]}
    for key in (
        ("summary", "summary"),
        ("emotion_target", "wonder"),
        ("genre_contract", "wonder-genre"),
        ("genre_interaction", "genres-tension"),
        ("phase", "opening"),
    ):
        assert key in changed, key
        assert changed[key]["before"] != changed[key]["after"]
    assert "Wonder dominates fear" in changed[("emotion_target", "wonder")]["after"]
    assert "Awe at a larger world" in changed[("emotion_target", "wonder")]["before"]
    assert review["changes"]["emotion_targets"]["changed"] == ["wonder"]
    assert review["proposed_rationale"] == {
        "status": "provided", "source": "candidate.summary",
        "text": "Wonder becomes the dominant experience.",
    }
    assert "causal" not in json.dumps(review).lower()


def test_review_preserves_author_declared_emotions_and_accepted_constraints():
    previous = valid_candidate()
    proposed = copy.deepcopy(previous)
    proposed["nodes"][0]["summary"] = "Discovery deepens wonder rather than replacing it."
    identity = {
        "hard_constraints": ["The story contains no supernatural events"],
        "not_this": ["A grimdark tone"],
        "target_experience": {"primary_emotional_promise": "wonder"},
    }
    review = build_architecture_review(
        previous, proposed, "Clarify the wonder engine.", accepted_identity=identity,
    )
    assert review["preserved"]["author_declared_emotion_targets"] == [
        {"id": "wonder", "emotion": "joy", "role": "primary", "status": "preserved"},
    ]
    assert review["preserved"]["accepted_constraints"] == [
        "The story contains no supernatural events",
    ]
    assert review["preserved"]["accepted_not_this"] == ["A grimdark tone"]
    assert review["preserved"]["ids"]["nodes"] == ["dread-engine", "dread-genre", "wonder-genre"]


def test_changed_author_declared_emotion_is_visible_not_hidden_as_preserved():
    previous = valid_candidate()
    proposed = copy.deepcopy(previous)
    proposed["emotion_targets"][0]["role"] = "supporting"
    review = build_architecture_review(previous, proposed, "Make dread primary.")
    assert review["preserved"]["author_declared_emotion_targets"] == []
    changes = review["preserved"]["author_declared_emotion_changes"]
    assert changes[0]["id"] == "wonder"
    assert changes[0]["before"] == "primary"
    assert changes[0]["after"] == "supporting"
    assert changes[0]["changed_fields"] == ["role"]


def test_author_declared_emotion_meaning_change_reports_changed_fields():
    previous = valid_candidate()
    proposed = copy.deepcopy(previous)
    proposed["emotion_targets"][0]["intended_effect"] = "Awe that survives loss."
    review = build_architecture_review(previous, proposed, "Deepen wonder.")
    changes = review["preserved"]["author_declared_emotion_changes"]
    assert changes[0]["id"] == "wonder"
    assert changes[0]["before"] == changes[0]["after"] == "primary"
    assert changes[0]["changed_fields"] == ["intended_effect"]


def test_review_does_not_invent_rationale_when_summary_missing():
    previous = valid_candidate()
    proposed = copy.deepcopy(previous)
    proposed["summary"] = "   "
    proposed["nodes"][0]["summary"] = "Changed meaning."
    review = build_architecture_review(previous, proposed, "Revise the engine.")
    assert review["proposed_rationale"]["status"] == "missing"
    assert review["proposed_rationale"]["text"] is None
    assert "none was invented" in review["proposed_rationale"]["note"]


def test_complete_revision_review_exposes_new_fields_and_keeps_legacy_diff(tmp_path):
    store = working_store(tmp_path)
    first = prepare_architecture(store)
    baseline = complete_architecture(store, response(first, valid_candidate()))
    revision = prepare_architecture(store, "Make wonder dominant over fear.")
    updated = copy.deepcopy(valid_candidate())
    updated["summary"] = "Wonder dominates fear while keeping its cost."
    updated["emotion_targets"][1]["role"] = "contrasting"
    finished = complete_architecture(store, response(revision, updated))
    assert finished["status"] == "review_ready"
    review = finished["review"]
    assert review["candidate"] == ArchitectureCandidate.model_validate(
        updated,
    ).model_dump(mode="json")
    assert review["requested_change"] == "Make wonder dominant over fear."
    assert review["changes"]["emotion_targets"]["changed"] == ["dread"]
    assert any(
        item["kind"] == "emotion_target" and item["id"] == "dread"
        for item in review["changed_components"]
    )
    assert review["preserved"]["author_declared_emotion_targets"][0]["id"] == "wonder"
    assert review["proposed_rationale"]["text"] == (
        "Wonder dominates fear while keeping its cost."
    )
    assert finished["candidate"] == baseline["candidate"]
    assert not (tmp_path / "story_identity.yaml").exists()
