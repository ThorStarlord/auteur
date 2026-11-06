"""Typed narrative anchors as source-grounded creative context for Story Realization.

An emotional target or recorded relationship is design guidance for concrete possibilities. It never
becomes a node identity, a required event, or accepted story canon, and node-only callers are unchanged.
"""
from __future__ import annotations

import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_realization import (
    complete_realization, main as realization_main, prepare_realization, project_realization,
)

from test_beginner_studio_architecture_inquiry import seeded_store
from test_beginner_studio_architecture_review import response


def _source(projection):
    return json.loads(projection["request"]["user"])["source"]


def _scene(anchor_refs=None, architecture_refs=None):
    return {
        "schema_version": 1,
        "summary": "A scene possibility grounded in the selected emotional target.",
        "elements": [{
            "id": "scene_choice",
            "kind": "scene",
            "title": "The surveyor chooses a map",
            "description": "The surveyor weighs an accurate record against a kinder omission.",
            "architecture_refs": architecture_refs or ["wonder-engine"],
            "anchor_refs": anchor_refs or [],
        }],
        "links": [],
        "architecture_feedback": [],
        "open_questions": [],
    }


def test_emotion_target_anchor_carries_its_recorded_meaning(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_realization(store, [], "", [{"kind": "emotion_target", "id": "dread"}])
    source = _source(pending)
    anchor = source["creative_anchors"][0]
    assert (anchor["kind"], anchor["id"], anchor["ref"]) == ("emotion_target", "dread", "emotion_target:dread")
    assert anchor["sourceRef"] == "emotion_targets/1"
    assert "intended_effect" in anchor["recordedSupport"]
    assert source["focus_ids"] == []
    assert "never claim" in pending["request"]["system"].lower()


def test_recorded_relationship_anchor_carries_endpoints_and_function(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_realization(store, [], "", [{"kind": "link", "id": "wonder-to-dread"}])
    anchor = _source(pending)["creative_anchors"][0]
    assert anchor["ref"] == "link:wonder-to-dread"
    assert "wonder-engine" in anchor["recordedSupport"]
    assert "raises the cost of wonder" in anchor["recordedSupport"]


def test_component_anchor_carries_the_selected_field_value(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_realization(
        store, [], "", [{"kind": "emotion_target", "id": "dread", "field": "intended_effect"}],
    )
    anchor = _source(pending)["creative_anchors"][0]
    assert anchor["ref"] == "emotion_target:dread@intended_effect"
    assert anchor["fieldValue"] == "Fear of what discovery costs."


def test_node_only_callers_are_unchanged(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_realization(store, ["wonder-engine"])
    source = _source(pending)
    assert source["focus_ids"] == ["wonder-engine"]
    assert "creative_anchors" not in source


def test_element_may_cite_a_supplied_anchor(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_realization(store, [], "",
                                  [{"kind": "emotion_target", "id": "dread"}])
    ready = complete_realization(store, response(pending, _scene(["emotion_target:dread"])))
    assert ready["status"] == "ready"
    assert ready["candidate"]["elements"][0]["anchor_refs"] == ["emotion_target:dread"]


def test_element_cannot_cite_an_unsupplied_anchor(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_realization(store, [], "",
                                  [{"kind": "emotion_target", "id": "dread"}])
    with pytest.raises(ValueError, match="supplied creative anchors"):
        complete_realization(store, response(pending, _scene(["emotion_target:wonder"])))
    assert project_realization(store)["status"] == "awaiting_host_agent"


def test_unknown_or_cross_canvas_anchor_fails_before_a_request_is_written(tmp_path):
    store = seeded_store(tmp_path)
    before = project_realization(store)
    with pytest.raises(ValueError, match="not found"):
        prepare_realization(store, [], "", [{"kind": "emotion_target", "id": "not_recorded"}])
    with pytest.raises(ValueError, match="one to three"):
        prepare_realization(store, [], "", [])
    assert project_realization(store) == before


def test_changed_source_makes_anchored_realization_stale(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_realization(store, [], "",
                                  [{"kind": "emotion_target", "id": "dread"}])
    canvas = store.load()
    vision = next(item for item in canvas.items if item.id == "story-vision").model_dump(mode="json")
    vision["content"] += " The author now wants the cost shared."
    store.apply("update-item", expected_revision=canvas.revision,
                command_id="change-vision-after-anchor", payload={"item": vision})
    with pytest.raises(BeginnerConcurrencyError, match="stale realization"):
        complete_realization(store, response(pending, _scene(["emotion_target:dread"])))


def test_cli_prepares_an_emotion_anchor(tmp_path, capsys):
    store = seeded_store(tmp_path)
    realization_main(["--project", str(tmp_path), "--canvas", "story-one", "prepare",
                      "--anchor", "emotion_target:dread"])
    projection = json.loads(capsys.readouterr().out)
    assert projection["status"] == "awaiting_host_agent"
    assert _source(projection)["creative_anchors"][0]["ref"] == "emotion_target:dread"
    assert store.canvas_id == "story-one"
