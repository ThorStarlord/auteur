"""T04: an ambiguous delegation keeps the expressed purpose governing.

A conflicting alternative may be explored and compared, but it stays
noncanonical and anything that would replace the author's purpose requires an
explicit author decision.
"""
from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from auteur.beginner.studio_architecture import (
    ArchitectureOpportunity, complete_architecture, prepare_architecture,
    project_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


VISION = (
    "An optimistic series about a city that learns to share water. The intended "
    "experience is earned hope: cooperation is hard, costly and worth it. The "
    "series should never conclude that hope was naive."
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


def candidate(opportunity):
    return {
        "schema_version": 2,
        "summary": "Shared water makes cooperation expensive and durable.",
        "nodes": [
            {"id": "water-engine", "title": "Water engine", "category": "engine",
             "summary": "Shared scarcity forces cooperation that must be renewed."},
            {"id": "hope-thread", "title": "Earned hope", "category": "reader_experience",
             "summary": "Hope is re-earned by cost, never asserted."},
        ],
        "links": [{"id": "water-to-hope", "source": "water-engine",
                   "target": "hope-thread", "function": "makes hope costly"}],
        "open_questions": ["Who may refuse the water compact?"],
        "opportunities": [opportunity],
    }


def governing_opportunity(**overrides):
    data = {
        "id": "tragic-replacement",
        "title": "The compact fails and hope was naive",
        "why_it_matters": "A tragic frame may produce sharper institutional pressure.",
        "scope": "series",
        "relationship": "replaces",
        "artistic_potential": "Tragedy can make the cost of cooperation unbearable.",
        "intention_fidelity": (
            "It negates the stated experience of earned hope, so it is a different "
            "series rather than a sharper version of this one."
        ),
        "requires_author_decision": True,
    }
    data.update(overrides)
    return data


def response(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data), runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def _assert_no_canon(store):
    assert not (store.project_root / "story_identity.yaml").exists()
    assert not (store.project_root / "blueprint.yaml").exists()


def test_conflicting_alternative_coexists_with_the_governing_architecture(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate(governing_opportunity())))

    projection = project_architecture(store)
    # The author's expressed purpose still governs the working architecture.
    assert projection["candidate"]["summary"] == (
        "Shared water makes cooperation expensive and durable."
    )
    assert projection["governing_objective"]["authority"] == "author_expressed"

    comparison = projection["opportunities"]["comparison"]
    assert comparison["governing_purpose_authority"] == "author_expressed"
    assert comparison["requires_author_decision"] == ["tragic-replacement"]
    assert comparison["alternatives"][0]["relationship"] == "replaces"
    _assert_no_canon(store)


def test_a_replacement_without_an_author_decision_is_rejected():
    with pytest.raises(ValidationError):
        ArchitectureOpportunity(
            id="silent-replacement",
            title="Replace the purpose silently",
            why_it_matters="This must not be representable.",
            relationship="replaces",
        )


def test_a_deepening_alternative_needs_no_author_decision(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(
        store,
        response(waiting, candidate(governing_opportunity(
            id="darker-middle",
            relationship="deepens",
            requires_author_decision=False,
            intention_fidelity=(
                "A devastating Book lets the same optimistic purpose survive a cost "
                "it chose to accept."
            ),
            artistic_potential="Darker events can make the eventual hope load-bearing.",
        ))),
    )
    comparison = project_architecture(store)["opportunities"]["comparison"]
    assert comparison["requires_author_decision"] == []
    assert comparison["alternatives"][0]["relationship"] == "deepens"


def test_artistic_potential_and_intention_fidelity_stay_separate(tmp_path):
    store = store_for(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate(governing_opportunity())))

    item = project_architecture(store)["opportunities"]["items"][0]
    assert "unbearable" in item["artistic_potential"]
    assert "different series" in item["intention_fidelity"]
    assert item["artistic_potential"] != item["intention_fidelity"]


def test_ambiguous_delegation_prompt_keeps_the_expressed_purpose_governing(tmp_path):
    store = store_for(tmp_path)
    system = prepare_architecture(store)["request"]["system"]
    assert "has not delegated replacing their" in system
    assert "governing working direction" in system
    assert "requires_author_decision" in system
    assert "merely because it was expressed first" in system
    assert "Darker events may deepen an optimistic" in system
