"""T06: per-request initiative and emphasis assist the author without granting authority."""
from __future__ import annotations

import json

import pytest

from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture,
    project_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


VISION = (
    "A long series about a mountain monastery that sells its memory of the valley. "
    "I want the reader to feel the price of being remembered."
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


def candidate():
    return {
        "schema_version": 2,
        "summary": "Memory is sold by the monastery and paid for by the valley.",
        "nodes": [
            {"id": "memory-engine", "title": "Memory engine", "category": "engine",
             "summary": "Selling memory keeps the monastery alive and the valley poor."},
            {"id": "price-thread", "title": "Price thread", "category": "thread",
             "summary": "Every purchase changes who can remember."},
        ],
        "links": [{"id": "memory-to-price", "source": "memory-engine",
                   "target": "price-thread", "function": "assigns the price"}],
        "open_questions": ["Who is forbidden from selling?"],
        "opportunities": [{
            "id": "valley-revenge",
            "title": "The valley learns to buy back",
            "why_it_matters": "A later Book could invert who owns memory.",
            "scope": "series",
        }],
    }


def response(status, data=None):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data if data is not None else candidate()),
        runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def _assert_no_canon(store):
    assert not (store.project_root / "story_identity.yaml").exists()
    assert not (store.project_root / "blueprint.yaml").exists()


def test_default_request_carries_no_collaboration_preferences(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    assert "collaboration" not in json.loads(waiting["request"]["user"])


def test_preferences_reach_the_request_and_the_projection(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(
        store, initiative="focused", emphasis="teaching",
    )
    user = json.loads(waiting["request"]["user"])
    assert user["collaboration"] == {"initiative": "focused", "emphasis": "teaching"}

    complete_architecture(store, response(waiting))
    assert project_architecture(store)["collaboration"] == {
        "initiative": "focused", "emphasis": "teaching",
    }


def test_unknown_preferences_are_rejected(tmp_path):
    store = store_for(tmp_path)
    with pytest.raises(ValueError):
        prepare_architecture(store, initiative="relentless")
    with pytest.raises(ValueError):
        prepare_architecture(store, emphasis="poetic")


def test_prompt_describes_the_assistance_preferences_without_authority(tmp_path):
    store = store_for(tmp_path)
    system = prepare_architecture(store)["request"]["system"]
    for token in (
        "focused", "exploration_intensive", "teaching", "architecture",
        "unconventional",
    ):
        assert token in system, token
    assert "None grants canon" in system
    assert "may still notice an" in system


def test_a_focused_request_still_permits_opportunity_recognition(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store, initiative="focused")
    complete_architecture(store, response(waiting))
    projection = project_architecture(store)
    assert projection["opportunities"]["count"] == 1
    assert projection["opportunities"]["authority"] == "noncanonical_opportunity"


def test_contrasting_styles_keep_the_same_review_and_acceptance_path(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store, emphasis="unconventional")
    complete_architecture(store, response(waiting))

    revision = prepare_architecture(
        store,
        instruction="Challenge whether the monastery should survive at all.",
        initiative="exploration_intensive",
        emphasis="architecture",
    )
    revised = candidate()
    revised["summary"] = "The monastery is the valley's largest debtor."
    complete_architecture(store, response(revision, revised))

    projection = project_architecture(store)
    assert projection["status"] == "review_ready"
    assert projection["collaboration"] == {
        "initiative": "exploration_intensive", "emphasis": "architecture",
    }
    apply_architecture_review(store, projection["review"]["request_sha256"])
    assert project_architecture(store)["status"] == "ready"
    _assert_no_canon(store)
