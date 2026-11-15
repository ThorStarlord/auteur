"""T08: a retained opportunity survives a fresh session and is withheld when stale."""
from __future__ import annotations

import json

from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture, project_architecture_resume,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


VISION = (
    "A thirty-Book series about a guild that licenses grief. Mourning must be "
    "purchased, and the guild decides whose loss is worth recording."
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
        "summary": "Grief is licensed and therefore rationed.",
        "nodes": [
            {"id": "grief-engine", "title": "Grief engine", "category": "engine",
             "summary": "Licensed mourning turns loss into an entitlement."},
            {"id": "unlicensed-thread", "title": "Unlicensed grief",
             "category": "thread",
             "summary": "People who cannot pay mourn privately and illegally."},
        ],
        "links": [{"id": "grief-to-unlicensed", "source": "grief-engine",
                   "target": "unlicensed-thread", "function": "creates the excluded"}],
        "open_questions": ["Who audits the guild's valuations?"],
        "opportunities": [{
            "id": "guild-schism",
            "title": "The guild splits over who may be mourned",
            "why_it_matters": (
                "A middle Book could turn the licensing engine against itself."
            ),
            "scope": "series",
            "relationship": "deepens",
        }],
    }


def response(status):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(candidate()), runtime="integration-test",
        model="UNAVAILABLE",
    ).model_dump()


def _develop(store):
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting))


def test_resume_recovers_the_opportunity_with_its_rationale_and_source(tmp_path):
    store = store_for(tmp_path)
    _develop(store)

    resume = project_architecture_resume(store)
    opportunities = resume["working_opportunities"]
    assert opportunities["authority"] == "noncanonical_opportunity"
    assert opportunities["freshness"] == "ready"
    assert opportunities["withheld"] is False
    assert opportunities["retained_item_count"] == 1

    item = opportunities["items"][0]
    assert item["id"] == "guild-schism"
    assert "licensing engine against itself" in item["why_it_matters"]
    # The working version the idea came from stays identifiable.
    assert resume["candidate_request_sha256"]


def test_resume_keeps_speculation_distinct_from_accepted_identity(tmp_path):
    store = store_for(tmp_path)
    _develop(store)

    resume = project_architecture_resume(store)
    assert resume["working_opportunities"]["authority"] == (
        "noncanonical_opportunity"
    )
    assert resume["accepted_story_identity"] is None
    assert not (store.project_root / "story_identity.yaml").exists()


def test_a_changed_source_withholds_retained_opportunities(tmp_path):
    store = store_for(tmp_path)
    _develop(store)
    assert project_architecture_resume(store)["working_opportunities"]["withheld"] is False

    store.apply(
        "create-item", expected_revision=store.load().revision,
        command_id="new-source",
        payload={"item": {
            "id": "new-working-note", "kind": "note", "title": "New direction",
            "content": "The guild should not exist until Book 4.",
        }, "position": {"x": 60, "y": 90}},
    )

    opportunities = project_architecture_resume(store)["working_opportunities"]
    assert opportunities["freshness"] == "stale"
    assert opportunities["withheld"] is True
    assert opportunities["items"] == []
    # Retained, not deleted, and not promoted merely because it was saved.
    assert opportunities["retained_item_count"] == 1


def test_resume_is_read_only(tmp_path):
    store = store_for(tmp_path)
    _develop(store)
    before = store.load().revision
    project_architecture_resume(store)
    assert store.load().revision == before
    assert not (store.project_root / "blueprint.yaml").exists()
