"""Graph-anchored holistic revision lifecycle (the revision contract planned for PR #517 Task 4).

These are characterization tests of the existing prepare/complete/review/apply owner. They protect the
authority boundary: a selected anchor qualifies context for an explicit whole-working revision, and it
never grants canon, skips whole-candidate validation, or rebinds a title to a different record.
"""
from __future__ import annotations

import copy
import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture, project_architecture,
)

from test_beginner_studio_architecture_review import response, valid_candidate
from test_beginner_studio_architecture_inquiry import seeded_store


INSTRUCTION = "Make the wonder engine carry more of the dread."


def _intent(store, *, operation="revise", anchors=None, sha=None, canvas_id=None, author_text=INSTRUCTION):
    return {
        "version": 1,
        "canvas_id": canvas_id or store.canvas_id,
        "operation": operation,
        "expected_candidate_request_sha256": sha or project_architecture(store)["candidate_request_sha256"],
        "anchors": anchors or [{"kind": "node", "id": "wonder-engine"}],
        "author_text": author_text,
    }


def _revised():
    revised = copy.deepcopy(valid_candidate())
    revised["summary"] = "Wonder carries more of the dread."
    return revised


def test_graph_anchored_revision_records_validated_focus_in_request_and_review(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture(store, INSTRUCTION, _intent(store))
    request_user = json.loads(pending["request"]["user"])
    anchor = request_user["graph_intent"]["anchors"][0]
    assert (anchor["kind"], anchor["id"], anchor["sourceRef"]) == ("node", "wonder-engine", "nodes/0")
    ready = complete_architecture(store, response(pending, _revised()))
    assert ready["status"] == "review_ready"
    receipt = ready["review"]["graph_intent_receipt"]
    assert receipt["operation"] == "revise"
    assert receipt["anchors"][0]["id"] == "wonder-engine"


def test_legacy_revision_without_graph_context_is_unchanged(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture(store, INSTRUCTION)
    assert "graph_intent" not in json.loads(pending["request"]["user"])


def test_stale_candidate_identity_is_rejected_before_a_request_is_written(tmp_path):
    store = seeded_store(tmp_path)
    before = project_architecture(store)
    with pytest.raises(ValueError, match="SHA mismatch"):
        prepare_architecture(store, INSTRUCTION, _intent(store, sha="f" * 64))
    assert project_architecture(store) == before


def test_cross_canvas_intent_is_rejected(tmp_path):
    store = seeded_store(tmp_path)
    with pytest.raises(ValueError, match="another canvas"):
        prepare_architecture(store, INSTRUCTION, _intent(store, canvas_id="someone-else"))


def test_intent_text_must_match_the_submitted_instruction(tmp_path):
    store = seeded_store(tmp_path)
    with pytest.raises(ValueError, match="must exactly match"):
        prepare_architecture(store, INSTRUCTION, _intent(store, author_text="A different request."))


def test_only_explicit_revise_may_prepare_a_working_architecture(tmp_path):
    store = seeded_store(tmp_path)
    with pytest.raises(ValueError, match="only an explicit Revise"):
        prepare_architecture(store, INSTRUCTION, _intent(store, operation="explain"))


def test_anchor_matched_by_title_never_rebinds_to_another_record(tmp_path):
    store = seeded_store(tmp_path)
    with pytest.raises(ValueError, match="not found"):
        prepare_architecture(store, INSTRUCTION, _intent(store, anchors=[
            {"kind": "node", "id": "Wonder engine"},
        ]))


def test_stale_source_refuses_graph_context(tmp_path):
    store = seeded_store(tmp_path)
    intent = _intent(store)
    working = store.load()
    item = working.items[0].model_dump(mode="json")
    item["content"] += " Changed after the architecture was accepted."
    store.apply("update-item", expected_revision=working.revision,
                command_id="stale-source-before-graph-revision", payload={"item": item})
    with pytest.raises(BeginnerConcurrencyError, match="stale"):
        prepare_architecture(store, INSTRUCTION, intent)


def test_completed_revision_stays_working_and_never_writes_story_identity(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture(store, INSTRUCTION, _intent(store))
    complete_architecture(store, response(pending, _revised()))
    applied = apply_architecture_review(store, pending["request"]["request_sha256"])
    assert applied["candidate"]["summary"] == "Wonder carries more of the dread."
    assert not (store.project_root / "story_identity.yaml").exists()


def test_revision_cannot_target_a_pending_review_proposal(tmp_path):
    store = seeded_store(tmp_path)
    intent = _intent(store)
    intent["target"] = "pending_review"
    with pytest.raises(ValueError, match="target the current working architecture"):
        prepare_architecture(store, INSTRUCTION, intent)
    assert project_architecture(store)["status"] == "ready"
