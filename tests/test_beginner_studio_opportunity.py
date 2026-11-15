"""Incidental creative opportunities stay optional and never displace requested work.

T02: Auteur can notice a promising cross-Book possibility during ordinary
architecture work without turning it into a defect, an author decision or canon.
"""
from __future__ import annotations

import json

from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


VISION = (
    "A fifty-Book series about a city that survives by forgetting. Each generation "
    "inherits an institution built on deliberate amnesia, and the series asks whether "
    "a society can be kind and honest at the same time."
)


def store_for(tmp_path):
    store = CanvasStore(tmp_path, "story-one")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {
            "id": "story-vision", "kind": "note", "title": "Story Vision",
            "content": VISION,
        }, "position": {"x": 20, "y": 50}},
    )
    return store


def candidate_with_opportunity():
    return {
        "schema_version": 2,
        "summary": "Forgetting is the city's price for survival.",
        "nodes": [
            {"id": "amnesia-engine", "title": "Amnesia engine", "category": "engine",
             "summary": "Each generation must forget to keep the city habitable."},
            {"id": "honesty-thread", "title": "Honesty thread", "category": "thread",
             "summary": "A minority records what the city deletes."},
        ],
        "links": [{"id": "amnesia-to-honesty", "source": "amnesia-engine",
                   "target": "honesty-thread", "function": "creates moral cost"}],
        "open_questions": ["Who owns the archive?"],
        "opportunities": [{
            "id": "archive-city",
            "title": "The archive becomes a city of its own",
            "why_it_matters": (
                "A late Book could reveal that the keepers of deleted memory have "
                "built an institution with its own legitimacy problem."
            ),
            "scope": "series",
        }],
    }


def candidate_without_opportunity():
    data = candidate_with_opportunity()
    data.pop("opportunities")
    return data


def response(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data), runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def _assert_no_canon(store):
    assert not (store.project_root / "story_identity.yaml").exists()
    assert not (store.project_root / "blueprint.yaml").exists()


def test_incidental_opportunity_surfaces_without_displacing_requested_work(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate_with_opportunity()))

    projection = project_architecture(store)
    assert projection["status"] == "ready"

    opportunities = projection["opportunities"]
    assert opportunities["authority"] == "noncanonical_opportunity"
    assert opportunities["count"] == 1
    assert opportunities["items"][0]["id"] == "archive-city"
    assert "not accepted narrative meaning" in opportunities["note"]

    # The requested primary development result remains available and unchanged.
    candidate = projection["candidate"]
    assert [node["id"] for node in candidate["nodes"]] == [
        "amnesia-engine", "honesty-thread",
    ]
    assert candidate["summary"] == "Forgetting is the city's price for survival."
    _assert_no_canon(store)


def test_ordinary_task_without_consequential_opportunity_invents_nothing(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate_without_opportunity()))

    opportunities = project_architecture(store)["opportunities"]
    assert opportunities["count"] == 0
    assert opportunities["items"] == []
    assert opportunities["authority"] == "noncanonical_opportunity"


def test_opportunity_is_neither_acceptance_nor_an_author_decision(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate_with_opportunity()))

    projection = project_architecture(store)
    status = projection["premise_status"]

    # Not accepted, not author-expressed, not promoted to an unresolved question.
    assert status["accepted"]["source"] is None
    assert status["author_expressed"]["emotion_targets"] == []
    assert status["unresolved"]["open_questions"] == ["Who owns the archive?"]
    assert "archive-city" not in status["unresolved"]["open_questions"]
    assert "archive-city" not in status["provisional_agent_interpretation"]["nodes"]
    _assert_no_canon(store)


def test_request_prompt_asks_for_bounded_optional_opportunities(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    system = waiting["request"]["system"]
    assert "opportunities" in system
    assert "never manufacture novelty" in system
    assert "not a defect" in system
