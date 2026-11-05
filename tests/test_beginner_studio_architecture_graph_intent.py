"""Typed source-verified graph intent: no invented relationships or stale source IDs."""
from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from auteur.beginner.studio_architecture_graph_intent import GraphIntent, resolve_graph_intent


SHA = "a" * 64
NEXT = "b" * 64


def candidate():
    return {
        "schema_version": 2,
        "summary": "Wonder and its cost.",
        "nodes": [
            {"id": "engine", "title": "Memory Economy", "category": "engine",
             "summary": "Every discovery costs a memory.", "parent_id": None},
            {"id": "mystery", "title": "Mystery", "category": "genre",
             "summary": "Every discovery raises questions.", "parent_id": "engine"},
            {"id": "mystery_2", "title": "Mystery", "category": "genre",
             "summary": "A different role.", "parent_id": None},
        ],
        "links": [{"id": "cost_link", "source": "engine", "target": "mystery",
                   "function": "raises personal cost"}],
        "genre_interactions": [],
        "emotion_targets": [{"id": "wonder", "emotion": "joy", "role": "primary",
                             "intended_effect": "Awe", "provenance": "author_declared"}],
        "complex_emotions": [],
        "genre_contracts": [{"genre_node_id": "mystery", "role": "governing",
                             "emotion_target_ids": ["wonder"],
                             "complex_emotion_ids": [],
                             "narrative_engine": "Discovery"}],
        "phases": [{"id": "opening", "genre_activations":
                    [{"genre_node_id": "mystery", "structural_function": "Establish"}],
                    "parallel_with": []}],
    }


def intent(anchors, operation="explore", **overrides):
    value = {
        "version": 1, "canvas_id": "story-one", "operation": operation,
        "expected_candidate_request_sha256": SHA,
        "anchors": anchors, "author_text": "Could this mechanism produce more wonder?",
    }
    value.update(overrides)
    return value


def resolve(anchors, operation="explore", source=None, **overrides):
    return resolve_graph_intent(source or candidate(), SHA, intent(anchors, operation, **overrides))


def test_link_selection_is_exact_and_directional():
    result = resolve([{"kind": "link", "id": "cost_link"}])
    anchor = result["anchors"][0]
    assert anchor["sourceRef"] == "links/0"
    assert anchor["kind"] == "link"
    assert anchor["id"] == "cost_link"
    assert result["recorded_relations"][0]["source"] == "engine"
    assert result["recorded_relations"][0]["target"] == "mystery"


def test_same_title_never_substitutes_for_selected_id():
    value = resolve([{"kind": "node", "id": "mystery_2"}])
    assert value["anchors"][0]["sourceRef"] == "nodes/2"
    with pytest.raises(ValueError, match="not found"):
        resolve([{"kind": "node", "id": "a_title_only"}])


def test_reordering_array_updates_exact_source_reference():
    reordered = candidate()
    reordered["nodes"].reverse()
    value = resolve([{"kind": "node", "id": "engine"}], source=reordered)
    assert value["anchors"][0]["sourceRef"] == "nodes/2"


def test_component_field_returns_actual_recorded_value():
    value = resolve([{"kind": "emotion_target", "id": "wonder",
                      "field": "intended_effect"}])
    assert value["anchors"][0]["fieldValue"] == "Awe"
    with pytest.raises(ValueError, match="field not recorded"):
        resolve([{"kind": "emotion_target", "id": "wonder",
                  "field": "invented_causal_power"}])


def test_genre_contract_reference_is_recorded_but_not_an_architecture_link():
    value = resolve([{"kind": "genre_contract", "id": "mystery",
                      "reference": {"field": "emotion_target_ids",
                                    "target_kind": "emotion_target",
                                    "target_id": "wonder"}}])
    assert value["anchors"][0]["reference"]["kind"] == "recorded_reference"
    assert value["anchors"][0]["sourceRef"] == "genre_contracts/0"


def test_ambiguous_repeated_reference_fails_closed():
    source = candidate()
    source["genre_contracts"][0]["emotion_target_ids"].append("wonder")
    with pytest.raises(ValueError, match="ambiguous"):
        resolve([{"kind": "genre_contract", "id": "mystery",
                  "reference": {"field": "emotion_target_ids",
                                "target_kind": "emotion_target",
                                "target_id": "wonder"}}], source=source)


def test_engine_and_emotion_pair_has_no_fabricated_direct_relation():
    value = resolve([{"kind": "node", "id": "engine"},
                     {"kind": "emotion_target", "id": "wonder"}], "connect_to_ask")
    assert value["between"]["status"] == "no_recorded_relation"
    assert value["between"]["relations"] == []


def test_explicit_link_between_two_nodes_is_detected():
    value = resolve([{"kind": "node", "id": "engine"},
                     {"kind": "node", "id": "mystery"}], "connect_to_ask")
    assert value["between"]["status"] == "recorded"
    assert value["between"]["relations"][0]["id"] == "cost_link"


def test_stale_source_sha_is_rejected():
    with pytest.raises(ValueError, match="SHA mismatch"):
        resolve_graph_intent(candidate(), NEXT,
            intent([{"kind": "node", "id": "engine"}]))


def test_invalid_action_cardinality_and_duplicate_anchor_fail_validation():
    with pytest.raises(ValidationError):
        GraphIntent.model_validate(intent([{"kind": "node", "id": "engine"}],
                                         operation="connect_to_ask"))
    with pytest.raises(ValidationError):
        GraphIntent.model_validate(intent([{"kind": "node", "id": "engine"}],
                                         operation="compare"))
    with pytest.raises(ValidationError):
        GraphIntent.model_validate(intent([{"kind": "node", "id": "engine"}] * 2))
    with pytest.raises(ValidationError):
        GraphIntent.model_validate(intent([{"kind": "node", "id": "engine"}],
                                         author_text="x" * 4001))


def test_client_source_ref_claim_is_rejected():
    with pytest.raises(ValidationError):
        GraphIntent.model_validate(intent([{"kind": "node", "id": "engine",
                                           "sourceRef": "nodes/999"}]))


def test_reference_target_must_exist_and_be_of_correct_kind():
    with pytest.raises(ValueError, match="reference target not found"):
        source = candidate()
        source["emotion_targets"].clear()
        resolve([{"kind": "genre_contract", "id": "mystery",
                  "reference": {"field": "emotion_target_ids",
                                "target_kind": "emotion_target",
                                "target_id": "wonder"}}], source=source)
    with pytest.raises(ValueError, match="reference field or target type"):
        resolve([{"kind": "genre_contract", "id": "mystery",
                  "reference": {"field": "emotion_target_ids",
                                "target_kind": "node",
                                "target_id": "engine"}}])
