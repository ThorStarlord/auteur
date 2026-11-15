"""T05: explicitly delegated goal discovery may pick a provisional primary direction.

A working selection under delegation is still not Identity acceptance, and the
author can change it.
"""
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from auteur.beginner.studio_architecture import (
    ArchitectureCandidate, complete_architecture, prepare_architecture,
    project_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


VISION = (
    "A sketch: a generation ship where the crew votes every decade on whether to "
    "keep travelling. I am not sure whether this should be hopeful or a tragedy; "
    "find the strongest purpose for a long series."
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


def opportunity(identifier, title, relationship="reinterprets", provisional=False):
    return {
        "id": identifier,
        "title": title,
        "why_it_matters": "A different answer to what the voyage is for.",
        "scope": "series",
        "relationship": relationship,
        "artistic_potential": "Each frame produces different pressure.",
        "intention_fidelity": (
            "Deliberately different from the sketch, which is what was delegated."
        ),
        "requires_author_decision": False,
        "provisional_primary": provisional,
    }


def candidate():
    return {
        "schema_version": 2,
        "summary": "The vote is a machine for manufacturing consent.",
        "nodes": [
            {"id": "vote-engine", "title": "Vote engine", "category": "engine",
             "summary": "Each decade's vote redistributes hope and obligation."},
            {"id": "dissent-thread", "title": "Dissent thread", "category": "thread",
             "summary": "A minority keeps arguing for turning back."},
        ],
        "links": [{"id": "vote-to-dissent", "source": "vote-engine",
                   "target": "dissent-thread", "function": "manufactures legitimacy"}],
        "open_questions": ["Can the vote survive a generation that never chose it?"],
        "opportunities": [
            opportunity(
                "consent-tragedy", "The vote is a tragedy",
                relationship="replaces", provisional=True,
            ),
            opportunity("repair-comedy", "The vote becomes a repair ritual"),
        ],
    }


def response(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data), runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def _assert_no_canon(store):
    assert not (store.project_root / "story_identity.yaml").exists()
    assert not (store.project_root / "blueprint.yaml").exists()


def test_delegated_goal_discovery_yields_two_directions_and_a_provisional_primary(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate()))

    comparison = project_architecture(store)["opportunities"]["comparison"]
    assert comparison["alternative_count"] == 2
    assert comparison["provisional_primary"] == "consent-tragedy"
    assert [item["id"] for item in comparison["alternatives"]] == [
        "consent-tragedy", "repair-comedy",
    ]
    assert comparison["working_selection_is_not_acceptance"] is True
    _assert_no_canon(store)


def test_a_provisional_primary_needs_no_separate_author_decision(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate()))
    comparison = project_architecture(store)["opportunities"]["comparison"]
    # Replacing the sketch is legitimate here because goal discovery was delegated.
    assert comparison["requires_author_decision"] == []


def test_a_provisional_primary_never_accepts_identity(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate()))

    projection = project_architecture(store)
    assert projection["premise_status"]["accepted"]["source"] is None
    assert projection["governing_objective"]["authority"] == "author_expressed"
    _assert_no_canon(store)


def test_only_one_provisional_primary_is_representable():
    data = candidate()
    data["opportunities"][1]["provisional_primary"] = True
    with pytest.raises(ValidationError):
        ArchitectureCandidate.model_validate(
            data, context={"new_host_agent_response": True},
        )


def test_prompt_describes_delegated_goal_discovery(tmp_path):
    store = store_for(tmp_path)
    system = prepare_architecture(store)["request"]["system"]
    assert "explicitly delegates discovering the best artistic purpose" in system
    assert "provisional_primary" in system
    assert "never accepts Story Identity" in system
