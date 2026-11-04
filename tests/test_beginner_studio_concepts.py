"""Provisional story concepts stay reusable working notes, never shared ontology."""
from __future__ import annotations

import hashlib
import json
from importlib.resources import files

import pytest
from pydantic import ValidationError

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    main, project_architecture_resume,
)
from auteur.beginner.studio_concepts import (
    ProvisionalNarrativeConcept, list_provisional_concepts,
    record_provisional_concept,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.narrative_ontology.loader.ontology_loader import OntologyLoader


def working_store(tmp_path):
    store = CanvasStore(tmp_path, "story-one")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {
            "id": "story-vision", "kind": "note", "title": "Story Vision",
            "content": "A mystery about maps that erase memory.",
        }, "position": {"x": 20, "y": 50}},
    )
    return store


def concept(name="Memory Cartography"):
    return ProvisionalNarrativeConcept(
        name=name,
        definition="A map that stores a memory by removing it from the person who supplied it.",
        motivating_story_use="Makes accurate knowledge carry an intimate cost.",
        why_existing_concepts_insufficient=(
            "Setup and Payoff describe structure, but not a reusable object whose "
            "truth is purchased with autobiographical loss."
        ),
        related_concepts=["Setup", "Payoff", "Theme"],
        proposed_relations=[
            "Memory Cartography specializes Setup by making the cost of knowledge concrete.",
            "Memory Cartography creates tension with Theme when memory is identity.",
        ],
        compatibility_concerns=[
            "Do not imply that every setting permits supernatural memory transfer.",
        ],
    )


def ontology_hash(filename="base_ontology.yaml"):
    return hashlib.sha256(
        files("auteur.data.ontology").joinpath(filename).read_bytes()
    ).hexdigest()


def test_provisional_concept_survives_fresh_process_and_stays_noncanonical(tmp_path):
    store = working_store(tmp_path)
    before = ontology_hash()
    recorded = record_provisional_concept(
        store, concept(), expected_revision=store.load().revision,
        command_id="concept-1",
    )
    assert recorded.revision == store.load().revision
    reloaded = list_provisional_concepts(CanvasStore(tmp_path, "story-one"))
    assert len(reloaded) == 1
    assert reloaded[0].name == "Memory Cartography"
    assert reloaded[0].status == "provisional"
    assert reloaded[0].proposed_relations[0].startswith("Memory Cartography specializes")
    assert reloaded[0].compatibility_concerns
    assert ontology_hash() == before
    assert not (tmp_path / "story_identity.yaml").exists()


def test_duplicate_command_id_is_idempotent_and_duplicate_concept_rejected(tmp_path):
    store = working_store(tmp_path)
    first = record_provisional_concept(
        store, concept(), expected_revision=store.load().revision,
        command_id="concept-1",
    )
    replay = record_provisional_concept(
        store, concept(), expected_revision=999, command_id="concept-1",
    )
    assert replay.revision == first.revision
    assert len(list_provisional_concepts(store)) == 1
    with pytest.raises(ValueError, match="already exists"):
        record_provisional_concept(
            store, concept(), expected_revision=store.load().revision,
            command_id="concept-2",
        )
    assert len(list_provisional_concepts(store)) == 1


def test_conflicting_revision_and_invalid_structure_do_not_overwrite(tmp_path):
    store = working_store(tmp_path)
    record_provisional_concept(
        store, concept(), expected_revision=store.load().revision,
        command_id="concept-1",
    )
    with pytest.raises(BeginnerConcurrencyError):
        record_provisional_concept(
            store, concept("Another concept"), expected_revision=0,
            command_id="concept-2",
        )
    with pytest.raises(ValidationError):
        ProvisionalNarrativeConcept.model_validate({"name": "Incomplete"})
    assert [item.name for item in list_provisional_concepts(store)] == [
        "Memory Cartography",
    ]


def test_concept_is_visible_in_resume_without_becoming_accepted_ontology(tmp_path):
    store = working_store(tmp_path)
    record_provisional_concept(
        store, concept(), expected_revision=store.load().revision,
        command_id="concept-1",
    )
    resume = project_architecture_resume(CanvasStore(tmp_path, "story-one"))
    assert resume["accepted_story_identity"] is None
    assert resume["provisional_concepts"][0]["name"] == "Memory Cartography"
    assert resume["provisional_concepts"][0]["status"] == "provisional"
    ontology_names = {
        item["name"] for item in resume["ontology_guidance"]["concepts"]
    }
    assert "Memory Cartography" not in ontology_names
    assert "Memory Cartography" not in OntologyLoader().get_concept_names()


def test_concept_is_not_a_shared_loader_concept_or_accepted_resource(tmp_path):
    store = working_store(tmp_path)
    before = ontology_hash()
    before_mystery = ontology_hash("mystery_ontology.yaml")
    record_provisional_concept(
        store, concept(), expected_revision=store.load().revision,
        command_id="concept-1",
    )
    assert "Memory Cartography" not in OntologyLoader().get_concept_names("mystery")
    assert ontology_hash() == before
    assert ontology_hash("mystery_ontology.yaml") == before_mystery


def test_architecture_request_labels_provisional_concepts_as_noncanonical(tmp_path):
    from auteur.beginner.studio_architecture import prepare_architecture

    store = working_store(tmp_path)
    record_provisional_concept(
        store, concept(), expected_revision=store.load().revision,
        command_id="concept-1",
    )
    waiting = prepare_architecture(store)
    user = json.loads(waiting["request"]["user"])
    items = user["working_context"]["working_items"]
    provisional = [
        item for item in items if item.get("group") == "provisional-concepts"
    ]
    assert len(provisional) == 1
    assert "Memory Cartography" in provisional[0]["content"]
    system = " ".join(waiting["request"]["system"].split())
    assert "provisional-concepts" in system
    assert "not shared ontology definitions" in system
    assert "not author commitments" in system


def architecture_candidate():
    return {
        "schema_version": 2,
        "summary": "A mystery about maps that erase memory.",
        "nodes": [
            {"id": "engine", "title": "Memory economy", "category": "engine",
             "summary": "Knowledge costs memory."},
            {"id": "genre", "title": "Literary mystery", "category": "genre",
             "summary": "The inquiry governs."},
        ],
        "links": [{"id": "engine-genre", "source": "engine", "target": "genre",
                   "function": "drives the inquiry"}],
        "phases": [{"id": "opening", "title": "Opening", "order": 0,
                    "narrative_function": "Establish the cost."}],
    }


def complete_first_architecture(store):
    from auteur.beginner.studio_architecture import (
        complete_architecture, prepare_architecture,
    )
    from auteur.host_agent import HostAgentRequest, build_host_agent_response

    waiting = prepare_architecture(store)
    request = HostAgentRequest(**waiting["request"])
    reply = build_host_agent_response(
        request, json.dumps(architecture_candidate()),
        runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()
    return complete_architecture(store, reply)


def test_recording_provisional_concept_does_not_stale_author_architecture(tmp_path):
    from auteur.beginner.studio_architecture import project_architecture

    store = working_store(tmp_path)
    complete_first_architecture(store)
    assert project_architecture(store)["status"] == "ready"
    record_provisional_concept(
        store, concept(), expected_revision=store.load().revision,
        command_id="concept-1",
    )
    projection = project_architecture(store)
    assert projection["status"] == "ready"
    assert projection["candidate"]["summary"] == architecture_candidate()["summary"]
    resume = project_architecture_resume(CanvasStore(tmp_path, "story-one"))
    assert resume["architecture_status"] == "ready"
    assert resume["provisional_concepts"][0]["name"] == "Memory Cartography"


def test_provisional_concept_does_not_displace_author_working_source(tmp_path):
    from auteur.beginner.studio_architecture import prepare_architecture

    store = working_store(tmp_path)
    for index in range(25):
        store.apply(
            "create-item", expected_revision=store.load().revision,
            command_id=f"author-item-{index}",
            payload={"item": {
                "id": f"author-item-{index}", "kind": "note",
                "title": f"Author note {index}", "content": f"Author note {index}.",
            }, "position": {"x": 30 + index, "y": 70 + index}},
        )
    record_provisional_concept(
        store, concept(), expected_revision=store.load().revision,
        command_id="concept-1",
    )
    waiting = prepare_architecture(store)
    working = json.loads(waiting["request"]["user"])["working_context"]
    items = working["working_items"]
    author_items = [item for item in items if item.get("group") != "provisional-concepts"]
    concept_items = [item for item in items if item.get("group") == "provisional-concepts"]
    assert len(author_items) == 24
    assert len(concept_items) == 1
    assert working["omitted_working_item_count"] == 1
    assert working["provisional_concept_item_count"] == 1


def test_record_concept_cli_writes_only_working_notes(tmp_path, capsys):
    store = working_store(tmp_path)
    source = tmp_path / "concept.json"
    source.write_text(json.dumps(concept().model_dump(mode="json")), encoding="utf-8")
    result = main([
        "--project", str(tmp_path), "--canvas", "story-one",
        "record-concept", "--concept", str(source),
    ])
    assert result == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "provisional"
    assert output["authority"] == "working_noncanonical"
    assert output["concept"]["name"] == "Memory Cartography"
    assert [item.name for item in list_provisional_concepts(store)] == [
        "Memory Cartography",
    ]
    assert not (tmp_path / "story_identity.yaml").exists()
    assert not (tmp_path / "blueprint.yaml").exists()
