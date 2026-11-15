"""T03: a selected opportunity becomes a reviewable alternative, never canon."""
from __future__ import annotations

import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture,
    project_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


VISION = (
    "An optimistic forty-Book series about a coastal federation that keeps peace by "
    "ritual. Every generation renews the ritual, and the series asks what the peace "
    "cost and who pays for it."
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
    data = {
        "schema_version": 2,
        "summary": "Peace is renewed by ritual with a hidden cost.",
        "nodes": [
            {"id": "ritual-engine", "title": "Ritual engine", "category": "engine",
             "summary": "The ritual restores peace by deferring an unpaid cost."},
            {"id": "cost-thread", "title": "Cost thread", "category": "thread",
             "summary": "Someone always absorbs what the ritual defers."},
        ],
        "links": [{"id": "ritual-to-cost", "source": "ritual-engine",
                   "target": "cost-thread", "function": "assigns the deferred cost"}],
        "open_questions": ["Who is allowed to refuse the ritual?"],
        "opportunities": [{
            "id": "refusal-archive",
            "title": "The archive of refusals",
            "why_it_matters": "A later Book could reveal who refused and disappeared.",
            "scope": "series",
        }],
    }
    return data


def response(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data), runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def _develop(store):
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate()))
    return project_architecture(store)


def _assert_no_canon(store):
    assert not (store.project_root / "story_identity.yaml").exists()
    assert not (store.project_root / "blueprint.yaml").exists()


def test_exploring_a_selected_opportunity_produces_a_review_without_canon(tmp_path):
    store = store_for(tmp_path)
    projection = _develop(store)
    baseline_sha = projection["candidate_request_sha256"]

    revision = prepare_architecture(
        store,
        instruction="Explore whether the refusal archive can carry a later Book.",
        selected_opportunity={
            "candidate_request_sha256": baseline_sha,
            "opportunity_id": "refusal-archive",
        },
    )
    user = json.loads(revision["request"]["user"])
    assert user["selected_opportunity"]["authority"] == "noncanonical_opportunity"
    assert user["selected_opportunity"]["opportunity"]["id"] == "refusal-archive"

    explored = candidate()
    explored["summary"] = "The archive of refusals becomes a rival institution."
    explored["nodes"].append(
        {"id": "archive-institution", "title": "Archive institution",
         "category": "engine",
         "summary": "Refusals are preserved by an institution with its own claims."}
    )
    explored["links"].append(
        {"id": "archive-to-ritual", "source": "archive-institution",
         "target": "ritual-engine", "function": "exposes what the ritual hides"}
    )
    complete_architecture(store, response(revision, explored))

    projection = project_architecture(store)
    assert projection["status"] == "review_ready"
    assert projection["review"]["selected_opportunity"]["opportunity"]["id"] == (
        "refusal-archive"
    )
    assert projection["review"]["authority"] == (
        "working_architecture_comparison_not_story_impact"
    )
    _assert_no_canon(store)


def test_opportunity_from_a_superseded_candidate_is_rejected(tmp_path):
    store = store_for(tmp_path)
    _develop(store)
    with pytest.raises(BeginnerConcurrencyError):
        prepare_architecture(
            store,
            instruction="Explore the archive.",
            selected_opportunity={
                "candidate_request_sha256": "0" * 64,
                "opportunity_id": "refusal-archive",
            },
        )


def test_unknown_opportunity_is_rejected(tmp_path):
    store = store_for(tmp_path)
    baseline_sha = _develop(store)["candidate_request_sha256"]
    with pytest.raises(ValueError):
        prepare_architecture(
            store,
            instruction="Explore the archive.",
            selected_opportunity={
                "candidate_request_sha256": baseline_sha,
                "opportunity_id": "not-an-opportunity",
            },
        )


def test_selected_opportunity_requires_a_revision_instruction(tmp_path):
    store = store_for(tmp_path)
    baseline_sha = _develop(store)["candidate_request_sha256"]
    with pytest.raises(ValueError):
        prepare_architecture(
            store,
            selected_opportunity={
                "candidate_request_sha256": baseline_sha,
                "opportunity_id": "refusal-archive",
            },
        )


def test_governing_direction_survives_until_the_author_applies(tmp_path):
    store = store_for(tmp_path)
    baseline = _develop(store)
    baseline_sha = baseline["candidate_request_sha256"]

    revision = prepare_architecture(
        store,
        instruction="Explore the refusal archive.",
        selected_opportunity={
            "candidate_request_sha256": baseline_sha,
            "opportunity_id": "refusal-archive",
        },
    )
    explored = candidate()
    explored["summary"] = "The archive of refusals becomes a rival institution."
    complete_architecture(store, response(revision, explored))

    # Merely exploring changes nothing about the current working architecture.
    projection = project_architecture(store)
    assert projection["candidate"]["summary"] == (
        "Peace is renewed by ritual with a hidden cost."
    )

    # Applying a reviewed working revision still never touches accepted story.
    review_sha = projection["review"]["request_sha256"]
    apply_architecture_review(store, review_sha)
    applied = project_architecture(store)
    assert applied["status"] == "ready"
    assert applied["candidate"]["summary"] == (
        "The archive of refusals becomes a rival institution."
    )
    _assert_no_canon(store)
