"""R09: a consequential reading is disclosed as a recommendation, not as author fact."""
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture, project_architecture,
    project_architecture_resume,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


VISION = (
    "A series about two languages that cannot express the same obligations. One has a "
    "word for a promise that can be inherited; the other has a word for a promise that "
    "cannot be forgiven. The intended experience is earned hope about being understood."
)


def store_for(tmp_path, vision=VISION):
    store = CanvasStore(tmp_path, "story-one")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {
            "id": "story-vision", "kind": "note", "title": "Story Vision",
            "content": vision,
        }, "position": {"x": 20, "y": 50}},
    )
    return store


def candidate(**overrides):
    data = {
        "schema_version": 2,
        "summary": "Two promise-kinds cannot be exchanged without loss.",
        "nodes": [
            {"id": "promise-kinds", "title": "Two promise-kinds", "category": "engine",
             "summary": "One promise survives its maker; the other cannot be forgiven."},
            {"id": "drift", "title": "Obligation drift", "category": "engine",
             "summary": "Meaning moves every time the text is used correctly."},
        ],
        "links": [{"id": "kinds-to-drift", "source": "promise-kinds",
                   "target": "drift", "function": "supplies the material"}],
        "emotion_targets": [
            {"id": "earned-hope", "emotion": "joy", "role": "primary",
             "intended_effect": "Comprehension is worth its cost.",
             "eliciting_condition": "A partial rendering is received as partial.",
             "aesthetic_strategy": "Restraint.", "provenance": "author_declared"},
            {"id": "drift-dread", "emotion": "fear", "role": "supporting",
             "intended_effect": "The text you relied on has moved.",
             "eliciting_condition": "A reused phrase means something else.",
             "aesthetic_strategy": "Repetition with variation.",
             "provenance": "agent_proposed"},
        ],
        "open_questions": ["What does a promise that cannot be forgiven require?"],
        "interpretations": [{
            "id": "forgiveness-terminates",
            "interpretation": (
                "A promise that cannot be forgiven terminates at the person who made "
                "it and cannot be transferred or absolved."
            ),
            "affects": ["promise-kinds"],
            "consequences": (
                "Inheritance becomes a source of intergenerational conflict rather than "
                "a neutral transfer."
            ),
            "alternative": (
                "The promise could instead persist beyond death and bind the dead "
                "person's estate."
            ),
            "author_decision_required": False,
        }],
    }
    data.update(overrides)
    return data


def response(status, data=None):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data if data is not None else candidate()),
        runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def _develop(store, data=None):
    status = prepare_architecture(store)
    complete_architecture(store, response(status, data))
    return project_architecture(store)


def test_a_consequential_reading_is_reported_as_a_recommendation(tmp_path):
    store = store_for(tmp_path)
    projection = _develop(store)

    block = projection["working_interpretations"]
    assert block["authority"] == "agent_interpretation"
    assert block["count"] == 1
    item = block["items"][0]
    assert item["id"] == "forgiveness-terminates"
    assert "cannot be transferred or absolved" in item["interpretation"]
    assert item["alternative"]
    assert "not author-established commitments" in block["note"]


def test_a_reserved_goal_reading_can_require_an_author_decision(tmp_path):
    store = store_for(tmp_path)
    data = candidate()
    data["interpretations"].append({
        "id": "partial-authority-resolution",
        "interpretation": (
            "The series resolves its central question by instituting openly partial, "
            "revisable interpretive authority."
        ),
        "affects": ["drift"],
        "consequences": "The series answers rather than defers its founding question.",
        "author_decision_required": True,
    })
    projection = _develop(store, data)
    assert projection["working_interpretations"]["requires_author_decision"] == [
        "partial-authority-resolution"
    ]


def test_a_reading_must_name_nodes_that_exist(tmp_path):
    store = store_for(tmp_path)
    data = candidate()
    data["interpretations"][0]["affects"] = ["no-such-node"]
    with pytest.raises(ValidationError):
        _develop(store, data)


def test_author_stated_and_agent_proposed_emotions_stay_distinct(tmp_path):
    store = store_for(tmp_path)
    projection = _develop(store)
    status = projection["premise_status"]
    assert status["author_expressed"]["emotion_targets"] == ["earned-hope"]
    assert "drift-dread" not in status["author_expressed"]["emotion_targets"]


def test_no_canonical_acceptance_occurs(tmp_path):
    store = store_for(tmp_path)
    _develop(store)
    assert not (store.project_root / "story_identity.yaml").exists()
    assert not (store.project_root / "blueprint.yaml").exists()


def test_readings_survive_a_fresh_session(tmp_path):
    store = store_for(tmp_path)
    _develop(store)
    resume = project_architecture_resume(store)
    block = resume["working_interpretations"]
    assert block["count"] == 1
    assert block["items"][0]["id"] == "forgiveness-terminates"


def test_a_historical_candidate_without_readings_still_parses(tmp_path):
    store = store_for(tmp_path)
    data = candidate()
    data.pop("interpretations")
    projection = _develop(store, data)
    assert projection["working_interpretations"]["count"] == 0


def test_an_author_described_experience_is_not_an_author_named_emotion(tmp_path):
    """The R09 failure: the author wrote "earned trust"; the agent labelled it joy."""
    store = store_for(
        tmp_path,
        "A series about two languages that cannot express the same obligations. "
        "The intended experience is earned trust in incomplete knowledge, extended "
        "before it can be verified.",
    )
    data = candidate()
    data["emotion_targets"] = [{
        "id": "earned-trust", "emotion": "joy", "role": "primary",
        "intended_effect": "Trust is extended before it can be verified.",
        "eliciting_condition": "A partial rendering is received as partial.",
        "aesthetic_strategy": "Restraint.", "provenance": "author_declared",
    }]
    rows = _develop(store, data)["author_emotion_grounding"]
    assert rows[0]["id"] == "earned-trust"
    assert rows[0]["experience_named_by_author"] is True
    assert rows[0]["emotion_named_by_author"] is False


def test_agent_proposed_emotions_are_not_reported_as_author_grounding(tmp_path):
    store = store_for(tmp_path)
    rows = _develop(store)["author_emotion_grounding"]
    assert [row["id"] for row in rows] == ["earned-hope"]
    assert "drift-dread" not in [row["id"] for row in rows]
