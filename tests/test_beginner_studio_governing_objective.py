"""The working proposal names the author's objective and the status of each premise.

T01: an author must be able to tell the delegated creative objective apart from
agent interpretation, accepted commitments and unresolved questions, without any
of it becoming canonical.
"""
from __future__ import annotations

import json

from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


LONG_SERIES_VISION = (
    "An optimistic seventy-Book science-fiction series about a civilization that "
    "learns to repair the climate it ruined. Each Book is a generation: repair "
    "succeeds unevenly, creates new obligations, and the founding hope that "
    "cooperation beats extraction must survive prosperity, betrayal, and its own "
    "success. The intended experience is earned hope, not triumph; no Book may "
    "resolve the series' central question by declaring the argument over."
)


def working_store(tmp_path, vision=LONG_SERIES_VISION):
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


def series_candidate():
    return {
        "schema_version": 2,
        "summary": "Repair succeeds unevenly and each generation inherits its cost.",
        "nodes": [
            {"id": "repair-engine", "title": "Repair engine", "category": "engine",
             "summary": "Cooperative repair creates new obligations each generation."},
            {"id": "legitimacy-engine", "title": "Legitimacy engine",
             "category": "engine",
             "summary": "Whoever allocates repair capacity gains and loses authority."},
            {"id": "earned-hope", "title": "Earned hope", "category": "reader_experience",
             "summary": "Hope is re-earned by consequence, never asserted."},
        ],
        "links": [
            {"id": "repair-to-legitimacy", "source": "repair-engine",
             "target": "legitimacy-engine", "function": "turns repair into political cost"},
            {"id": "legitimacy-to-hope", "source": "legitimacy-engine",
             "target": "earned-hope", "function": "makes hope conditional on conduct"},
        ],
        "phases": [
            {"id": "first-generation", "title": "First generation", "order": 1,
             "genres": [{"genre": "science_fiction", "role": "governing"}],
             "narrative_function": "Establish repair as shared, costly work."},
            {"id": "prosperity", "title": "Prosperity", "order": 2,
             "genres": [{"genre": "science_fiction", "role": "governing"}],
             "narrative_function": "Success redistributes power and creates new debt.",
             "parallel_with": ["first-generation"]},
        ],
        "emotion_targets": [
            {"id": "earned-hope", "emotion": "joy", "role": "primary",
             "intended_effect": "Hope feels earned by consequence.",
             "eliciting_condition": "A generation pays for an earlier gain.",
             "aesthetic_strategy": "Long-delayed payoff across Books.",
             "provenance": "author_declared"},
            {"id": "repair-grief", "emotion": "sadness", "role": "supporting",
             "intended_effect": "Loss is not erased by progress.",
             "eliciting_condition": "Repair cannot restore what extraction destroyed.",
             "aesthetic_strategy": "Concrete, local detail.",
             "provenance": "agent_proposed"},
        ],
        "open_questions": [
            "Does Book 12's prosperity arc end the founding engine or transform it?",
        ],
    }


def response(status, data=None):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data if data is not None else series_candidate()),
        runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def _assert_no_canon(store):
    assert not (store.project_root / "story_identity.yaml").exists()
    assert not (store.project_root / "blueprint.yaml").exists()


def test_develop_projection_names_the_author_objective_without_claiming_acceptance(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting))

    projection = project_architecture(store)
    assert projection["status"] == "ready"
    objective = projection["governing_objective"]
    assert objective["authority"] == "author_expressed"
    assert objective["story_vision"] == LONG_SERIES_VISION
    assert objective["instruction"] is None
    assert "not accepted Story Identity" in objective["note"]
    _assert_no_canon(store)


def test_premise_status_separates_author_accepted_provisional_and_unresolved(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting))

    status = project_architecture(store)["premise_status"]
    assert status["authority"] == "working_architecture_not_canon"

    author = status["author_expressed"]
    assert author["emotion_targets"] == ["earned-hope"]
    assert "not acceptance" in author["note"]

    provisional = status["provisional_agent_interpretation"]
    assert "repair-engine" in provisional["nodes"]
    assert "repair-to-legitimacy" in provisional["links"]
    assert provisional["summary"] is True
    assert "repair-grief" not in provisional["nodes"]

    unresolved = status["unresolved"]["open_questions"]
    assert unresolved == series_candidate()["open_questions"]

    # Nothing in the working proposal is reported as accepted author choice.
    assert status["accepted"]["source"] is None
    assert status["accepted"]["commitments"] == {}


def test_revision_review_carries_the_objective_and_premise_status(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting))

    revision = prepare_architecture(
        store, instruction="Make the legitimacy engine costlier after prosperity.",
    )
    revised = series_candidate()
    revised["summary"] = "Prosperity makes repair a question of legitimacy."
    revised["nodes"][1]["summary"] = (
        "Allocating repair capacity becomes the central political struggle."
    )
    complete_architecture(store, response(revision, revised))

    projection = project_architecture(store)
    assert projection["status"] == "review_ready"
    review = projection["review"]
    assert review["governing_objective"]["authority"] == "author_expressed"
    assert review["governing_objective"]["instruction"] == (
        "Make the legitimacy engine costlier after prosperity."
    )
    assert review["premise_status"]["authority"] == "working_architecture_not_canon"
    assert review["authority"] == "working_architecture_comparison_not_story_impact"
    _assert_no_canon(store)


def test_long_series_vision_remains_intelligible_and_noncanonical(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    user = json.loads(waiting["request"]["user"])
    assert user["working_context"]["vision"] == LONG_SERIES_VISION

    complete_architecture(store, response(waiting))
    projection = project_architecture(store)

    candidate = projection["candidate"]
    assert len(candidate["nodes"]) >= 3
    assert len(candidate["phases"]) >= 2
    assert projection["governing_objective"]["story_vision"] == LONG_SERIES_VISION
    assert projection["premise_status"]["unresolved"]["open_questions"]
    _assert_no_canon(store)
