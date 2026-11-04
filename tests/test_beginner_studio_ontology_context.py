"""Studio architecture requests carry bounded, source-referenced ontology meanings."""
from __future__ import annotations

import json

from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_ontology_context import build_relevant_ontology_context
from auteur.beginner.studio_store import CanvasStore


def working_store(tmp_path, vision="A story about two sisters rebuilding trust."):
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


def test_context_contains_reusable_meanings():
    result = build_relevant_ontology_context("A mystery about knowledge", None)
    concepts = {item["name"]: item for item in result["concepts"]}
    assert result["authority"] == "derived_ontology_guidance"
    assert "Theme" in concepts and concepts["Theme"]["definition"]
    assert "Conflict" in concepts and concepts["Conflict"]["relationships"]


def test_context_carries_relationship_directions_for_core_design_concepts():
    result = build_relevant_ontology_context("A story about consequence.", None)
    concepts = {item["name"]: item for item in result["concepts"]}
    for name in (
        "Theme", "Conflict", "Arc", "Setup", "Payoff", "Revelation", "Reversal",
    ):
        assert name in concepts, name
        assert concepts[name]["definition"].strip(), name
        assert isinstance(concepts[name]["relationships"], list), name
    assert any(
        relationship.get("source_concept") == "Setup"
        and relationship.get("target_concept") == "Payoff"
        for relationship in concepts["Setup"]["relationships"]
    )
    assert result["source_refs"]
    assert result["selection"]["rationale"]


def test_sparse_vision_does_not_manufacture_genre_or_author_preference():
    result = build_relevant_ontology_context(
        "A story about two sisters rebuilding trust after a family rupture.", None,
    )
    names = {item["name"] for item in result["concepts"]}
    assert not names.intersection({"MysteryProblem", "InvestigativeArc", "Clue", "RedHerring"})
    assert result["selection"]["genre_extensions"] == []
    assert "accepted_story_identity" not in result
    assert "architecture_preferences" not in result
    assert "not declarations of author preference" in result["selection"]["not_story_intent"]


def test_explicit_mystery_adds_installed_genre_definitions_and_source_refs():
    result = build_relevant_ontology_context(
        "A coastal mystery about a cartographer who erases memories.", None,
    )
    concepts = {item["name"]: item for item in result["concepts"]}
    assert "MysteryProblem" in concepts
    assert concepts["MysteryProblem"]["genre_extension"] == "mystery"
    assert any("mystery_ontology.yaml" in ref for ref in result["source_refs"])
    extensions = result["selection"]["genre_extensions"]
    assert extensions[0]["genre"] == "mystery"


def test_accepted_identity_genre_is_an_explicit_selection_source():
    result = build_relevant_ontology_context(
        "A story about a locked room.", {"story_type": {"genre": "mystery"}},
    )
    concepts = {item["name"]: item for item in result["concepts"]}
    assert "MysteryProblem" in concepts
    assert result["selection"]["genre_extensions"][0]["source"] == "accepted_story_identity"


def test_architecture_request_nests_inspectable_ontology_meanings(tmp_path):
    store = working_store(
        tmp_path,
        "A mystery about a cartographer whose maps erase memories. Wonder, unease, earned hope.",
    )
    waiting = prepare_architecture(store)
    user = json.loads(waiting["request"]["user"])
    ontology = user["narrative_design_context"]["ontology_context"]
    assert ontology["authority"] == "derived_ontology_guidance"
    assert ontology["source_refs"]
    names = {item["name"] for item in ontology["concepts"]}
    assert {"Theme", "Conflict", "Arc", "Setup", "Payoff", "Revelation", "Reversal"} <= names
    assert "MysteryProblem" in names
    encoded = json.dumps(ontology, ensure_ascii=False).encode("utf-8")
    assert len(encoded) < 65536
    assert "validation_rules" not in encoded.decode("utf-8")
    assert "Read narrative_design_context" in waiting["request"]["system"]
    assert "ontology_context" in waiting["request"]["system"]


def test_unsupported_genre_mentions_do_not_add_ontology_extensions():
    result = build_relevant_ontology_context(
        "A story about competitive underwater basket weaving.", None,
    )
    assert result["selection"]["genre_extensions"] == []
    names = {item["name"] for item in result["concepts"]}
    assert "MysteryProblem" not in names
    assert "Clue" not in names
