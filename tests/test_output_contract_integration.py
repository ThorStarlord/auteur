"""R04: the authoritative output contract reaches the real preparation paths."""
from __future__ import annotations

import copy
import json

import pytest

import test_series_working_book_architecture as harness

from auteur.beginner.studio_architecture import (
    ArchitectureCandidate, complete_architecture, prepare_architecture,
)
from auteur.series.working_book_architecture import (
    WorkingBookArchitecture, book_complete, book_prepare,
)


def test_studio_request_carries_the_architecture_contract(tmp_path):
    store = harness.make_store(tmp_path, series=False)
    status = prepare_architecture(store)
    contract = status["request"]["output_contract"]
    assert contract["model"] == "ArchitectureCandidate"
    assert contract["json_schema"] == ArchitectureCandidate.model_json_schema()
    # The evidence from the historical run is addressable in the contract itself.
    assert "opportunities" in contract["json_schema"]["properties"]


def test_book_develop_request_carries_the_book_contract(tmp_path):
    store = harness.make_store(tmp_path)
    status = book_prepare(store, 2)
    contract = status["request"]["output_contract"]
    assert contract["model"] == "WorkingBookArchitecture"
    assert contract["json_schema"] == WorkingBookArchitecture.model_json_schema()
    assert "inherited" in contract["json_schema"]["properties"]


def test_book_revision_request_carries_the_book_contract(tmp_path):
    store = harness.make_store(tmp_path)
    harness.develop_book(store)
    status = book_prepare(store, 2, instruction="Revise the trust engine.", holistic=True)
    contract = status["request"]["output_contract"]
    assert contract["model"] == "WorkingBookArchitecture"


def test_the_contract_is_context_not_a_substitute_for_validation(tmp_path):
    """A supplied contract must not cause a malformed candidate to be admitted."""
    store = harness.make_store(tmp_path)
    status = book_prepare(store, 2)
    artifact = copy.deepcopy(harness.book_artifact())
    artifact["agents"][0]["motives"] = "Not a permitted field."
    with pytest.raises(Exception):
        book_complete(store, 2, harness.respond(status, artifact))


def test_studio_rejects_an_invented_field_even_with_a_contract(tmp_path):
    store = harness.make_store(tmp_path, series=False)
    status = prepare_architecture(store)
    candidate = harness.series_candidate()
    candidate["opportunities"] = [{
        "id": "opp-x", "title": "A possibility", "why_it_matters": "Because.",
        "description": "The field the historical run invented.",
    }]
    with pytest.raises(Exception):
        complete_architecture(store, harness.respond(status, candidate))


def test_request_and_response_identity_stay_bound(tmp_path):
    store = harness.make_store(tmp_path, series=False)
    status = prepare_architecture(store)
    response = harness.respond(status, harness.series_candidate())
    assert response["request_sha256"] == status["request"]["request_sha256"]
    complete_architecture(store, response)
    assert not (store.project_root / "story_identity.yaml").exists()
