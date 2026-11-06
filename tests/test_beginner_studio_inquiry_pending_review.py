"""Read-only examination of a pending, un-applied architecture revision.

The inquiry sees the applied baseline, the proposal, the requested change, the adopted alternative and
the recorded differences. It never modifies or applies the revision, and it becomes historical once the
revision is applied or superseded.
"""
from __future__ import annotations

import copy
import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture,
    prepare_architecture, project_architecture, project_architecture_resume,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, main as inquiry_main, prepare_architecture_inquiry,
    project_architecture_inquiry,
)

from test_beginner_studio_architecture_inquiry import intent, packet, seeded_store
from test_beginner_studio_architecture_review import response, valid_candidate


def _exploration(store):
    pending = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    complete_architecture_inquiry(store, packet(pending, {
        "schema_version": 1,
        "analysis": "Two different causal engines.",
        "recorded_observations": [],
        "hypotheses": [
            {"title": "Restorative knowledge", "divergence_axis": "causal_engine",
             "description": "Discovery restores shared understanding for the district."},
            {"title": "Consolation without knowledge", "divergence_axis": "reader_emotion",
             "description": "The community keeps comfort instead of the record of the loss."},
        ],
        "uncertainties": [],
    }))
    return pending["request_sha256"]


def _pending_review(store, *, extra_node=False):
    inquiry_sha = _exploration(store)
    pending = prepare_architecture(
        store, "Adopt consolation and rebalance the emotions.",
        selected_alternative={"inquiry_request_sha256": inquiry_sha, "hypothesis_id": "h2"},
    )
    proposed = copy.deepcopy(valid_candidate())
    proposed["summary"] = "Consolation keeps wonder alive while knowledge is withheld."
    if extra_node:
        proposed["nodes"].append({
            "id": "consolation_engine", "title": "Consolation engine", "category": "engine",
            "summary": "Comfort is maintained by withholding the record.",
        })
    complete_architecture(store, response(pending, proposed))
    return pending["request"]["request_sha256"]


def _review_intent(store, anchors=None, operation="challenge", text=None):
    return {
        "version": 1,
        "canvas_id": store.canvas_id,
        "target": "pending_review",
        "operation": operation,
        "expected_candidate_request_sha256": project_architecture(store)["candidate_request_sha256"],
        "anchors": anchors if anchors is not None else [{"kind": "node", "id": "wonder-engine"}],
        "author_text": text or "Does this revision strengthen the intended experience, or introduce problems?",
    }


def _review_answer(observations=None, hypotheses=None):
    return {
        "schema_version": 1,
        "analysis": "The proposal changes which experience governs.",
        "recorded_observations": observations or [],
        "hypotheses": hypotheses or [],
        "uncertainties": [],
    }


def test_packet_compares_applied_baseline_with_the_proposal(tmp_path):
    store = seeded_store(tmp_path)
    _pending_review(store)
    prepared = prepare_architecture_inquiry(store, _review_intent(store))
    assert prepared["status"] == "awaiting_host_agent"
    user = json.loads(prepared["request"]["user"])
    context = user["review_context"]
    assert context["authority"] == "pending_unapplied_working_revision"
    assert context["baseline_candidate"]["summary"] == valid_candidate()["summary"]
    assert context["proposed_candidate"]["summary"].startswith("Consolation keeps wonder")
    assert context["requested_change"].startswith("Adopt consolation")
    assert context["selected_creative_alternative"]["title"] == "Consolation without knowledge"
    assert [c["id"] for c in context["changed_components"]].count("summary") == 1
    assert user["working_candidate"]["summary"].startswith("Consolation keeps wonder")
    assert "pending_review" in prepared["request"]["system"]
    assert "recorded_change" in prepared["request"]["system"]


def test_result_is_read_only_and_labels_the_proposal_as_its_source(tmp_path):
    store = seeded_store(tmp_path)
    review_sha = _pending_review(store)
    before = project_architecture(store)
    prepared = prepare_architecture_inquiry(store, _review_intent(store))
    completed = complete_architecture_inquiry(store, packet(prepared, _review_answer([
        {"kind": "node", "id": "wonder-engine",
         "claim": "The recorded summary still governs the opening."},
    ])))
    assert completed["status"] == "ready"
    assert completed["result"]["inquiry_target"] == "pending_review"
    assert completed["result"]["review_request_sha256"] == review_sha
    observation = completed["result"]["recorded_observations"][0]
    assert observation["observed_in"] == "proposed_revision"
    assert project_architecture(store) == before
    assert project_architecture(store)["status"] == "review_ready"


def test_pending_review_inquiry_requires_an_unapplied_review(tmp_path):
    store = seeded_store(tmp_path)
    with pytest.raises(ValueError, match="no pending architecture revision"):
        prepare_architecture_inquiry(store, _review_intent(store))


def test_inquiry_becomes_historical_after_the_revision_is_applied(tmp_path):
    store = seeded_store(tmp_path)
    review_sha = _pending_review(store)
    prepared = prepare_architecture_inquiry(store, _review_intent(store))
    complete_architecture_inquiry(store, packet(prepared, _review_answer()))
    apply_architecture_review(store, review_sha)
    projection = project_architecture_inquiry(store)
    assert projection["status"] == "stale"
    assert projection["result"] is None
    resumed = project_architecture_resume(store)
    lineage = resumed["creative_deliberation"]["superseded_inquiry_history"]
    assert lineage[0]["target"] == "pending_review"
    assert lineage[0]["author_question"].startswith("Does this revision strengthen")


def test_anchor_is_resolved_against_the_proposal_not_the_applied_baseline(tmp_path):
    store = seeded_store(tmp_path)
    _pending_review(store, extra_node=True)
    prepared = prepare_architecture_inquiry(store, _review_intent(
        store, anchors=[{"kind": "node", "id": "consolation_engine"}],
    ))
    anchor = json.loads(prepared["request"]["user"])["graph_intent"]["anchors"][0]
    assert anchor["id"] == "consolation_engine"
    assert anchor["sourceRef"].startswith("nodes/")
    with pytest.raises(ValueError, match="not found"):
        prepare_architecture_inquiry(store, {
            **_review_intent(store, anchors=[{"kind": "node", "id": "consolation_engine"}]),
            "target": "current",
        })


def test_stale_proposal_rejects_the_answer_after_a_newer_revision(tmp_path):
    store = seeded_store(tmp_path)
    _pending_review(store)
    prepared = prepare_architecture_inquiry(store, _review_intent(store))
    # A newer revision supersedes the review the inquiry examined.
    newer = prepare_architecture(store, "Make the dread engine quieter.")
    quieter = copy.deepcopy(valid_candidate())
    quieter["summary"] = "A newer proposal."
    complete_architecture(store, response(newer, quieter))
    assert project_architecture_inquiry(store)["status"] == "stale"
    with pytest.raises(BeginnerConcurrencyError, match="baseline or design context changed"):
        complete_architecture_inquiry(store, packet(prepared, _review_answer()))


def test_cli_prepares_a_pending_review_inquiry_without_anchors(tmp_path, capsys):
    store = seeded_store(tmp_path)
    _pending_review(store)
    question = tmp_path / "question.txt"
    question.write_text("Does this revision strengthen the intended experience?", encoding="utf-8")
    inquiry_main(["--project", str(tmp_path), "--canvas", "story-one", "prepare",
                  "--target", "pending_review", "--op", "challenge",
                  "--text-file", str(question)])
    prepared = json.loads(capsys.readouterr().out)
    assert prepared["status"] == "awaiting_host_agent"
    assert json.loads(prepared["request"]["user"])["review_context"]["proposed_candidate"]


def test_pending_review_intent_must_bind_the_applied_baseline_sha(tmp_path):
    store = seeded_store(tmp_path)
    _pending_review(store)
    stale = _review_intent(store)
    stale["expected_candidate_request_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="SHA mismatch"):
        prepare_architecture_inquiry(store, stale)
