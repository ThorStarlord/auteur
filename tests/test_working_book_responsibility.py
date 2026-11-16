"""T07: a delegated Book responsibility stays visible while investigations accumulate."""
from __future__ import annotations

import copy
import json

import test_series_working_book_architecture as harness

from auteur.series.working_book_architecture import (
    book_apply_review, book_complete, book_prepare, book_resume,
)


def _responsibility(store):
    return book_resume(store, 2)["responsibility"]


def _prepare(store, instruction="Explore a wider Series opportunity."):
    return book_prepare(store, 2, instruction=instruction, holistic=True)


def _alternative(identifier, title="A wider Series redesign"):
    return {
        "id": identifier,
        "attribution": "agent_proposed",
        "epistemic_status": "hypothetical",
        "title": title,
        "status": "hypothetical",
        "text": "Reorganize Books 27-50 around the ledger's collapse.",
        "rationale": "The collapse would change who can promise a return at all.",
        "responsibility": "alternative_responsibility",
    }


def _apply(store, status, artifact):
    harness.book_complete(store, 2, harness.respond(status, artifact))
    return book_apply_review(store, 2, status["request"]["request_sha256"])


def test_narrow_delegation_names_the_book_deliverable_and_its_progress(tmp_path):
    store = harness.make_store(tmp_path)
    harness.develop_book(store)

    responsibility = _responsibility(store)
    assert responsibility["authority"] == "working_noncanonical"
    assert responsibility["delegated"]["book_number"] == 2
    assert responsibility["delegated"]["question"] == (
        harness.book_artifact()["function"]["question"]
    )
    assert responsibility["progress"]["revision_number"] == 0
    assert responsibility["progress"]["local_resolution_count"] >= 1
    assert responsibility["alternative_responsibilities"] == []
    assert responsibility["cumulative_displacement"]["signal"] == "none"


def test_an_in_service_revision_reports_the_alternative_without_displacement(tmp_path):
    store = harness.make_store(tmp_path)
    harness.develop_book(store)

    status = _prepare(store)
    artifact = copy.deepcopy(harness.book_artifact())
    # The deliverable advances at the same time as a wider possibility is recorded.
    resolution = artifact["local_resolution"][0]
    resolution.pop("provenance", None)
    resolution["attribution"] = "agent_proposed"
    resolution["epistemic_status"] = "asserted"
    resolution["text"] = (
        "Heirs read the first open entry, and the council must answer in public."
    )
    artifact["alternatives"].append(_alternative("alt-wider"))
    _apply(store, status, artifact)

    responsibility = _responsibility(store)
    assert responsibility["progress"]["revision_number"] == 1
    assert responsibility["cumulative_displacement"]["signal"] == "in_service"
    assert responsibility["cumulative_displacement"][
        "revisions_advancing_deliverable"
    ] == 1
    assert [item["id"] for item in responsibility["alternative_responsibilities"]] == [
        "alt-wider"
    ]


def test_cumulative_drift_across_several_investigations_is_reported(tmp_path):
    store = harness.make_store(tmp_path)
    harness.develop_book(store)

    for index in range(1, 4):
        status = _prepare(store, f"Investigate Series option {index}.")
        artifact = json.loads(json.dumps(book_resume(store, 2)["artifact"]))
        artifact["alternatives"].append(
            _alternative(f"alt-wider-{index}", f"A wider Series redesign {index}")
        )
        _apply(store, status, artifact)

    responsibility = _responsibility(store)
    displacement = responsibility["cumulative_displacement"]
    assert displacement["revisions_adding_alternative_responsibility"] == 3
    assert displacement["revisions_advancing_deliverable"] == 0
    assert displacement["signal"] == "review_required"
    assert len(responsibility["alternative_responsibilities"]) == 3

    # The delegated deliverable is still present and reviewable, not silently replaced.
    assert responsibility["progress"]["local_resolution_count"] >= 1
    assert responsibility["delegated"]["book_number"] == 2
    assert responsibility["unresolved"]["author_decisions"] == ["dec-reading"]


def test_interrupted_revision_leaves_working_and_accepted_state_unchanged(tmp_path):
    store = harness.make_store(tmp_path)
    harness.develop_book(store)
    before = harness.snapshot(store)
    baseline = book_resume(store, 2)

    _prepare(store, "Prepare but never complete this investigation.")

    after = book_resume(store, 2)
    assert after["revision"]["number"] == baseline["revision"]["number"] == 0
    assert after["responsibility"]["cumulative_displacement"]["signal"] == "none"
    assert harness.snapshot(store) == before
