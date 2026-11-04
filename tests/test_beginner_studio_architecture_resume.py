"""A new coding agent recovers working narrative meaning from project state alone."""
from __future__ import annotations

import hashlib
import json

from auteur.beginner.studio_architecture import (
    complete_architecture, main, prepare_architecture, project_architecture,
    project_architecture_resume,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


def working_store(tmp_path, canvas_id="story-one", vision=None):
    store = CanvasStore(tmp_path, canvas_id)
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {
            "id": "story-vision", "kind": "note", "title": "Story Vision",
            "content": vision or (
                "A mystery about a cartographer whose maps erase memories. "
                "Wonder, unease, and earned hope."
            ),
        }, "position": {"x": 20, "y": 50}},
    )
    return store


def candidate(summary="Wonder survives a costly cartography."):
    return {
        "schema_version": 2,
        "summary": summary,
        "nodes": [
            {"id": "wonder-engine", "title": "Wonder engine", "category": "engine",
             "summary": "Maps widen the world and erase memory."},
            {"id": "wonder-genre", "title": "Wonder", "category": "genre",
             "summary": "Wonder governs discovery."},
        ],
        "links": [{"id": "engine-genre", "source": "wonder-engine",
                   "target": "wonder-genre", "function": "creates wonder"}],
        "phases": [
            {"id": "opening", "title": "Opening", "order": 0,
             "narrative_function": "Establish the map's promise.",
             "reader_experience": "Open wonder."},
        ],
        "open_questions": ["How much memory should the ending restore?"],
    }


def response(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data), runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def snapshot(root):
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def test_resume_recovers_architecture_and_provenance_from_fresh_store(tmp_path):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    ready = complete_architecture(store, response(waiting, candidate()))
    before = snapshot(store.directory)
    resume = project_architecture_resume(CanvasStore(tmp_path, "story-one"))
    assert snapshot(store.directory) == before
    assert resume["kind"] == "studio_architecture_resume"
    assert resume["authority"] == "working_noncanonical"
    assert resume["canvas_id"] == "story-one"
    assert resume["story_vision"].startswith("A mystery about a cartographer")
    assert resume["architecture"] == ready["candidate"]
    assert resume["architecture_status"] == "ready"
    assert resume["candidate_request_sha256"] == waiting["request"]["request_sha256"]
    assert resume["accepted_story_identity"] is None
    assert resume["open_questions"] == candidate()["open_questions"]
    assert resume["provisional_concepts"] == []
    guidance = resume["ontology_guidance"]
    assert guidance["authority"] == "derived_ontology_guidance"
    assert guidance["origin"] == "request"
    assert guidance["request_sha256"] == waiting["request"]["request_sha256"]
    assert any("base_ontology.yaml" in ref for ref in guidance["source_refs"])
    assert any("mystery_ontology.yaml" in ref for ref in guidance["source_refs"])
    names = {concept["name"] for concept in guidance["concepts"]}
    assert {"Theme", "Conflict", "MysteryProblem"} <= names


def test_resume_does_not_borrow_another_canvas_architecture(tmp_path):
    first = working_store(tmp_path, "first")
    waiting = prepare_architecture(first)
    complete_architecture(first, response(waiting, candidate()))
    second = working_store(tmp_path, "second", "A quiet story about two sisters.")
    resume = project_architecture_resume(second)
    assert resume["architecture"] is None
    assert resume["architecture_status"] == "not_started"
    assert resume["candidate_request_sha256"] is None
    assert resume["open_questions"] == []
    assert resume["ontology_guidance"]["origin"] == "current_derived"


def test_resume_reports_pending_review_without_replacing_current_architecture(tmp_path):
    store = working_store(tmp_path)
    first = prepare_architecture(store)
    baseline = complete_architecture(store, response(first, candidate()))
    revision = prepare_architecture(store, "Make wonder dominate fear.")
    updated = candidate("Wonder dominates fear without erasing its cost.")
    finished = complete_architecture(store, response(revision, updated))
    resume = project_architecture_resume(CanvasStore(tmp_path, "story-one"))
    assert resume["architecture"] == baseline["candidate"]
    assert resume["architecture_status"] == "review_ready"
    assert resume["pending_review"]["candidate"] == finished["review"]["candidate"]
    assert resume["pending_review"]["requested_change"] == "Make wonder dominate fear."
    assert resume["pending_request_sha256"] == revision["request"]["request_sha256"]


def test_resume_reports_bounded_source_visibility_and_omission(tmp_path):
    store = working_store(tmp_path)
    long_scene = "The map erased the first memory at dawn. " + "x" * 1100
    for index in range(25):
        store.apply(
            "create-item", expected_revision=store.load().revision,
            command_id=f"scene-{index}",
            payload={"item": {
                "id": f"working-scene-{index}", "kind": "scene",
                "title": f"Manuscript source {index}",
                "content": long_scene if index == 0 else f"Scene {index}.",
            }, "position": {"x": 30 + index, "y": 90 + index}},
        )
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate()))
    resume = project_architecture_resume(CanvasStore(tmp_path, "story-one"))
    visibility = resume["source_visibility"]
    assert visibility["working_item_count"] == 24
    assert visibility["omitted_working_item_count"] == 1
    truncated = visibility["truncated_items"][0]
    assert truncated["id"] == "working-scene-0"
    assert truncated["content_characters"] == len(long_scene)
    assert truncated["content_is_excerpt"] is True
    assert len(truncated["full_content_sha256"]) == 64
    assert len(visibility["omitted_working_items_sha256"]) == 64
    assert "fabricated" not in json.dumps(resume).lower()


def test_resume_cli_is_machine_readable_and_read_only(tmp_path, capsys):
    store = working_store(tmp_path)
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate()))
    before = snapshot(store.directory)
    arguments = ["--project", str(tmp_path), "--canvas", "story-one", "resume"]
    assert main(arguments) == 0
    packet = json.loads(capsys.readouterr().out)
    assert packet["kind"] == "studio_architecture_resume"
    assert packet["architecture"] == project_architecture(store)["candidate"]
    assert snapshot(store.directory) == before


def test_resume_includes_accepted_identity_only_when_it_exists(tmp_path):
    from auteur.identity import StoryIdentity

    store = working_store(tmp_path)
    identity = StoryIdentity.model_validate({
        "title": "The remembering map",
        "core_answer": "Accurate memory requires chosen loss.",
        "story_type": {"genre": "mystery"},
        "central_engine": {
            "want": "Map the coast", "resistance": "Each map steals a memory",
            "conflict": "Truth against belonging", "stakes": "The town's past",
            "change": "A chosen record",
        },
        "hard_constraints": ["No map is harmless"],
    })
    identity.to_yaml(tmp_path / "story_identity.yaml")
    waiting = prepare_architecture(store)
    complete_architecture(store, response(waiting, candidate()))
    resume = project_architecture_resume(CanvasStore(tmp_path, "story-one"))
    accepted = resume["accepted_story_identity"]
    assert accepted["authority"] == "accepted_story_identity"
    assert accepted["hard_constraints"] == ["No map is harmless"]
    assert resume["ontology_guidance"]["selection"]["genre_extensions"][0]["source"] == (
        "accepted_story_identity"
    )
