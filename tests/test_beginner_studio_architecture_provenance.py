"""Author-declared emotion labels: source-grounded claims, never authority by label alone.

`author_declared` in a working Studio architecture means: the author's own visible text
names this emotion. It does not record that the author accepted the agent's elaboration.
The validator admits the label only where that text supports it (or where the label was
already an author claim in the baseline the writer was shown). Revisions surface every
author-origin claim that is new, promoted, removed, or relabelled.
"""
from __future__ import annotations

import copy
import json

import pytest

from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_architecture_review import build_architecture_review
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

VISION = "Wonder gives way to dread, then earned hope."


def working_store(tmp_path, vision: str = VISION):
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


def base_candidate() -> dict:
    return {
        "schema_version": 2,
        "summary": "Wonder survives contact with dread.",
        "nodes": [
            {"id": "wonder-engine", "title": "Wonder engine", "category": "engine",
             "summary": "Discovery creates awe."},
            {"id": "dread-engine", "title": "Dread engine", "category": "engine",
             "summary": "Threat turns discovery into danger."},
        ],
        "links": [{"id": "wonder-to-dread", "source": "wonder-engine",
                   "target": "dread-engine", "function": "raises the cost of wonder"}],
        "emotion_targets": [
            {"id": "wonder", "emotion": "joy", "role": "primary",
             "intended_effect": "Awe at a larger world.",
             "eliciting_condition": "Discovery reveals a wider possibility.",
             "aesthetic_strategy": "Scale and delayed revelation.",
             "provenance": "author_declared"},
            {"id": "grief", "emotion": "sadness", "role": "supporting",
             "intended_effect": "Grief for what discovery takes.",
             "eliciting_condition": "A lost memory is named.",
             "aesthetic_strategy": "Quiet, slow reveal.",
             "provenance": "agent_proposed"},
        ],
        "complex_emotions": [],
        "genre_contracts": [],
        "genre_interactions": [],
        "phases": [],
        "open_questions": [],
    }


def response(status: dict, data: dict) -> dict:
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data), runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def set_provenance(candidate: dict, identifier: str, provenance: str) -> dict:
    for target in candidate["emotion_targets"]:
        if target["id"] == identifier:
            target["provenance"] = provenance
    return candidate


def add_target(candidate: dict, identifier: str, provenance: str) -> dict:
    candidate["emotion_targets"].append({
        "id": identifier, "emotion": "fear", "role": "local",
        "intended_effect": f"Effect of {identifier}.",
        "eliciting_condition": f"Condition for {identifier}.",
        "aesthetic_strategy": "Restraint.",
        "provenance": provenance,
    })
    return candidate


def revision_baseline(tmp_path):
    store = working_store(tmp_path)
    first = prepare_architecture(store)
    complete_architecture(store, response(first, base_candidate()))
    return store


# --- develop: the admission rule -------------------------------------------------------

def test_develop_admits_author_declared_target_the_author_named(tmp_path):
    store = working_store(tmp_path)
    status = prepare_architecture(store)
    finished = complete_architecture(store, response(status, base_candidate()))
    assert finished["status"] == "ready"
    labels = {t["id"]: t["provenance"] for t in finished["candidate"]["emotion_targets"]}
    assert labels == {"wonder": "author_declared", "grief": "agent_proposed"}


def test_develop_rejects_author_declared_target_absent_from_author_text(tmp_path):
    store = working_store(tmp_path)
    status = prepare_architecture(store)
    candidate = add_target(base_candidate(), "awe", "author_declared")
    with pytest.raises(ValueError, match="'awe' is not named"):
        complete_architecture(store, response(status, candidate))
    assert not (store.directory / "architecture" / "current.json").exists()
    assert not (store.directory / "architecture" / "requests" / status["request"]["request_sha256"] / "response.json").exists()
    assert project_architecture(store)["status"] == "awaiting_host_agent"


def test_agent_interpretation_may_be_labelled_agent_proposed_without_source(tmp_path):
    store = working_store(tmp_path)
    status = prepare_architecture(store)
    candidate = add_target(base_candidate(), "anger", "agent_proposed")
    finished = complete_architecture(store, response(status, candidate))
    assert finished["status"] == "ready"


# --- groundedness rule ------------------------------------------------------------------

@pytest.mark.parametrize(("identifier", "admitted"), [
    ("wonder", True),
    ("wonder-dread", True),
    ("wonder-tide", False),
    ("the", False),
    ("a-b", False),
])
def test_grounding_requires_every_significant_term_in_author_text(tmp_path, identifier, admitted):
    store = working_store(tmp_path)
    status = prepare_architecture(store)
    candidate = copy.deepcopy(base_candidate())
    candidate["emotion_targets"][0]["id"] = identifier
    if admitted:
        finished = complete_architecture(store, response(status, candidate))
        assert finished["candidate"]["emotion_targets"][0]["provenance"] == "author_declared"
    else:
        with pytest.raises(ValueError, match="not named"):
            complete_architecture(store, response(status, candidate))


def test_agent_working_notes_do_not_count_as_author_source(tmp_path):
    store = working_store(tmp_path)
    store.apply(
        "create-item", expected_revision=store.load().revision, command_id="concept-note",
        payload={"item": {
            "id": "concept-tide", "kind": "note", "title": "Concept",
            "content": "Tide-lit dread.", "group": "provisional-concepts",
        }, "position": {"x": 20, "y": 200}},
    )
    status = prepare_architecture(store)
    candidate = add_target(base_candidate(), "tide", "author_declared")
    with pytest.raises(ValueError, match="'tide' is not named"):
        complete_architecture(store, response(status, candidate))


# --- revision: no new claim by label alone ----------------------------------------------

def test_revision_may_not_introduce_unsupported_author_claim(tmp_path):
    store = revision_baseline(tmp_path)
    revision = prepare_architecture(store, "Add a stronger fear.")
    candidate = add_target(base_candidate(), "anger", "author_declared")
    with pytest.raises(ValueError, match="'anger' is not named"):
        complete_architecture(store, response(revision, candidate))
    assert not (store.directory / "architecture" / "review.json").exists()
    assert project_architecture(store)["status"] == "awaiting_host_agent"


def test_revision_may_not_promote_interpretation_without_author_text(tmp_path):
    store = revision_baseline(tmp_path)
    revision = prepare_architecture(store, "Make grief an author commitment.")
    candidate = set_provenance(base_candidate(), "grief", "author_declared")
    with pytest.raises(ValueError, match="'grief' is not named"):
        complete_architecture(store, response(revision, candidate))


def test_revision_may_promote_when_author_text_names_the_term_and_review_flags_it(tmp_path):
    store = working_store(tmp_path, vision="Wonder gives way to dread, then earned hope. Grief remains.")
    first = prepare_architecture(store)
    complete_architecture(store, response(first, base_candidate()))
    revision = prepare_architecture(store, "Make grief a stated author experience.")
    candidate = set_provenance(base_candidate(), "grief", "author_declared")
    finished = complete_architecture(store, response(revision, candidate))
    changes = finished["review"]["preserved"]["author_declared_emotion_changes"]
    assert [(c["id"], c["status"]) for c in changes] == [("grief", "promoted_to_author_declared")]


def test_historical_author_claim_survives_revision_without_source_in_packet(tmp_path):
    store = revision_baseline(tmp_path)
    record_path = store.directory / "architecture" / "current.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    add_target(record["candidate"], "legacy-hope", "author_declared")
    record_path.write_text(json.dumps(record), encoding="utf-8")
    revision = prepare_architecture(store, "Clarify wonder.")
    candidate = add_target(base_candidate(), "legacy-hope", "author_declared")
    finished = complete_architecture(store, response(revision, candidate))
    preserved = finished["review"]["preserved"]["author_declared_emotion_targets"]
    assert "legacy-hope" in {item["id"] for item in preserved}


def test_revision_relabelling_an_author_claim_is_surfaced_for_review(tmp_path):
    store = revision_baseline(tmp_path)
    revision = prepare_architecture(store, "Reclassify wonder as interpretation.")
    candidate = set_provenance(base_candidate(), "wonder", "agent_proposed")
    finished = complete_architecture(store, response(revision, candidate))
    changes = finished["review"]["preserved"]["author_declared_emotion_changes"]
    assert [(c["id"], c["status"]) for c in changes] == [("wonder", "label_removed")]


# --- review projection -------------------------------------------------------------------

def test_review_flags_new_author_claim_and_removed_author_claim():
    previous = base_candidate()
    proposed = copy.deepcopy(previous)
    proposed["emotion_targets"] = [
        t for t in proposed["emotion_targets"] if t["id"] != "wonder"
    ]
    add_target(proposed, "dread", "author_declared")
    review = build_architecture_review(previous, proposed, "Rework the emotional palette.")
    statuses = {(c["id"], c["status"])
                for c in review["preserved"]["author_declared_emotion_changes"]}
    assert statuses == {("wonder", "removed"), ("dread", "new_author_claim")}


def test_review_states_what_author_declared_means():
    review = build_architecture_review(base_candidate(), base_candidate(), "No change.")
    meaning = review["preserved"]["author_declared_label_meaning"]
    assert "not author acceptance" in meaning
