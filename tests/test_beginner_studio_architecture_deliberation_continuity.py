"""Explicit revision from a selected noncanonical alternative, with fresh-session recovery.

A selected alternative is author-chosen working context for an explicit holistic revision. It is never
accepted canon and is only valid for the baseline on which the inquiry was answered.
"""
from __future__ import annotations

import copy
import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture,
    project_architecture, project_architecture_resume,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry,
)

from test_beginner_studio_architecture_inquiry import intent, packet, seeded_store
from test_beginner_studio_architecture_review import response, valid_candidate


def _answered_exploration(store):
    pending = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    complete_architecture_inquiry(store, packet(pending, {
        "schema_version": 1,
        "analysis": "Two different causal engines could carry the discovery.",
        "recorded_observations": [{"kind": "node", "id": "wonder-engine", "claim": "Discovery creates awe."}],
        "hypotheses": [
            {"title": "Restorative knowledge", "description": "Discovery restores shared understanding.",
             "divergence_axis": "causal_engine"},
            {"title": "Consolation without knowledge", "description": "The community keeps comfort instead of truth.",
             "divergence_axis": "reader_emotion"},
        ],
        "uncertainties": [],
    }))
    return pending["request_sha256"]


def _selection(store, sha, hypothesis_id="h2"):
    return {"inquiry_request_sha256": sha, "hypothesis_id": hypothesis_id}


def _supersede_baseline(store):
    """A real author-source change followed by a new development: the old inquiry's baseline is gone."""
    canvas = store.load()
    vision = next(item for item in canvas.items if item.id == "story-vision").model_dump(mode="json")
    vision["content"] += " The author now wants the cost to fall on a community."
    store.apply("update-item", expected_revision=canvas.revision,
                command_id="supersede-vision", payload={"item": vision})
    replacement = prepare_architecture(store)
    changed = valid_candidate()
    changed["summary"] = "A newer baseline."
    complete_architecture(store, response(replacement, changed))


def _revised_candidate():
    revised = copy.deepcopy(valid_candidate())
    revised["summary"] = "Consolation keeps wonder alive while knowledge is withheld."
    return revised


def test_revision_from_selected_alternative_records_provenance_in_request_and_review(tmp_path):
    store = seeded_store(tmp_path)
    inquiry_sha = _answered_exploration(store)
    pending = prepare_architecture(
        store, "Adopt the consolation alternative and rebalance the engine around it.",
        selected_alternative=_selection(store, inquiry_sha),
    )
    user = json.loads(pending["request"]["user"])
    selected = user["selected_creative_alternative"]
    assert selected["title"] == "Consolation without knowledge"
    assert selected["hypothesis_id"] == "h2"
    assert selected["inquiry_request_sha256"] == inquiry_sha
    assert selected["operation"] == "explore"
    ready = complete_architecture(store, response(pending, _revised_candidate()))
    assert ready["status"] == "review_ready"
    assert ready["review"]["selected_creative_alternative"]["title"] == "Consolation without knowledge"
    assert project_architecture(store)["candidate"]["summary"] == valid_candidate()["summary"]


def test_selected_alternative_requires_an_explicit_revision_instruction(tmp_path):
    store = seeded_store(tmp_path)
    inquiry_sha = _answered_exploration(store)
    with pytest.raises(ValueError, match="revision instruction"):
        prepare_architecture(store, "", selected_alternative=_selection(store, inquiry_sha))


def test_selected_alternative_from_a_superseded_baseline_is_refused(tmp_path):
    store = seeded_store(tmp_path)
    inquiry_sha = _answered_exploration(store)
    _supersede_baseline(store)
    with pytest.raises(BeginnerConcurrencyError, match="superseded"):
        prepare_architecture(
            store, "Adopt the consolation alternative.",
            selected_alternative=_selection(store, inquiry_sha),
        )


def test_unknown_alternative_or_inquiry_is_refused_before_a_request_is_written(tmp_path):
    store = seeded_store(tmp_path)
    inquiry_sha = _answered_exploration(store)
    with pytest.raises(ValueError, match="selected alternative not found"):
        prepare_architecture(store, "Adopt something.",
                             selected_alternative=_selection(store, inquiry_sha, "h9"))
    with pytest.raises(ValueError, match="selected inquiry not found"):
        prepare_architecture(store, "Adopt something.",
                             selected_alternative=_selection(store, "a" * 64))
    assert project_architecture(store)["status"] == "ready"


def test_fresh_resume_recovers_deliberation_and_adopted_alternative(tmp_path):
    store = seeded_store(tmp_path)
    inquiry_sha = _answered_exploration(store)
    pending = prepare_architecture(
        store, "Adopt the consolation alternative.",
        selected_alternative=_selection(store, inquiry_sha),
    )
    complete_architecture(store, response(pending, _revised_candidate()))
    apply_architecture_review(store, pending["request"]["request_sha256"])
    packet_data = project_architecture_resume(store)
    deliberation = packet_data["creative_deliberation"]
    assert deliberation["authority"] == "noncanonical_working_deliberation"
    # The applied revision is a new baseline: the exploration remains lineage, not current prompt context.
    assert deliberation["inquiry_history"] == []
    lineage = deliberation["superseded_inquiry_history"][0]
    assert lineage["author_question"] == "What other narratives could this engine support?"
    assert lineage["baseline_candidate_request_sha256"] != packet_data["candidate_request_sha256"]
    assert [h["title"] for h in lineage["hypotheses"]] == [
        "Restorative knowledge", "Consolation without knowledge",
    ]
    assert packet_data["adopted_creative_alternative"]["title"] == "Consolation without knowledge"
