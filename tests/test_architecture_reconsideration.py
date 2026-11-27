"""Evidence-grounded reconsideration of an accepted consequence analysis.

A reconsideration binds to one claim of a saved analysis and to that analysis's result. It recovers exact source wording from
the version the analysis read, and the exact coverage of Working Book elements. It is stored beside the analysis and never
rewrites it. The Spring Ledger study is the specimen.
"""
import hashlib
import json
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture_consequence import (
    _digest, _root, complete_architecture_consequence, prepare_architecture_consequence, project_architecture_consequence,
)
from auteur.beginner.studio_architecture_reconsideration import (
    ReconsiderationAnswer, complete_consequence_reconsideration, prepare_consequence_reconsideration,
    project_consequence_reconsiderations, reconsideration_standing,
)
from auteur.host_agent import load_host_agent_request, model_output_contract

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_architecture_consequence import (  # noqa: E402,F401 - the fixtures and helpers of the owner suite
    packet_of, pristine, project, propose, replay, store_for,
)
from test_architecture_consequence_v3 import compact_under_retained_terms, mechanism_answer  # noqa: E402

CHANGE = "Make the Mill Compact's labour duty apply in every season."
COMPACT = "l_compact_hands_in_kind"


def analysed(project_dir):
    """A pending revision analysed on the Spring Ledger study. Returns (store, analysis request sha, packet)."""
    store = store_for(project_dir)
    propose(store, CHANGE, compact_under_retained_terms)
    prepared = prepare_architecture_consequence(store)
    packet = packet_of(prepared)
    complete_architecture_consequence(store, replay(prepared["request"], mechanism_answer(packet)))
    return store, prepared["request"]["request_sha256"], packet


def result_bytes(store, analysis_sha):
    return (_root(store) / "requests" / analysis_sha / "result.json").read_bytes()


def mechanism_id(packet, record_id):
    return next(item["id"] for item in packet["evidence"]
                if item["kind"] == "mechanism" and item.get("record_id") == record_id)


def answer(packet, **overrides):
    evidence = [item["id"] for item in packet["evidence"]][:2]
    base = {"schema_version": 1, "disposition": "retained",
            "new_consideration": "The concern was weighed against the recorded labour duty and its counterevidence.",
            "reconsidered_judgment": "The concern stands as written; the recorded duty still names only Alternative B.",
            "evidence": evidence, "criticism_assessments": [], "remaining_uncertainty": [], "downstream": []}
    base.update(overrides)
    return base


def supplied_for(prepared):
    """The identifiers this request admits: what its claim supplies and what the owner recovered. An answer may cite nothing else."""
    return json.loads(prepared["request"]["user"])["allowed_evidence"][:2]


def concern_selection():
    return {"kind": "concern", "ref": 0}


# --- Binding and contract ------------------------------------------------------------------------------------------------------

def test_a_reconsideration_binds_one_claim_of_the_analysis_and_the_result_it_reads(project):
    store, analysis_sha, _ = analysed(project)
    before = result_bytes(store, analysis_sha)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection=concern_selection(),
        instruction="Check whether the labour-duty concern is still supported by the recorded duty.")
    request = prepared["request"]
    settings = request["settings"]
    assert settings["analysis_request_sha256"] == analysis_sha
    assert settings["analysis_result_sha256"] == hashlib.sha256(before).hexdigest()
    assert settings["claim_kind"] == "concern" and settings["claim_ref"] == 0
    assert request["output_contract"] == model_output_contract(ReconsiderationAnswer)
    assert request["output_contract"]["model"] == "ReconsiderationAnswer"


def test_preparing_the_same_reconsideration_twice_gives_the_same_request(project):
    store, analysis_sha, _ = analysed(project)
    first = prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha, selection=concern_selection(),
                                                instruction="Check the concern.")["request"]["request_sha256"]
    second = prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha, selection=concern_selection(),
                                                 instruction="Check the concern.")["request"]["request_sha256"]
    assert first == second


def test_reconsidering_a_claim_never_rewrites_the_original_analysis(project):
    store, analysis_sha, packet = analysed(project)
    before = result_bytes(store, analysis_sha)
    prepared = prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha, selection=concern_selection(),
                                                   instruction="Check the concern.")
    complete_consequence_reconsideration(store, replay(prepared["request"], answer(packet, evidence=supplied_for(prepared))))
    assert result_bytes(store, analysis_sha) == before


def test_a_claim_the_analysis_does_not_contain_is_refused(project):
    store, analysis_sha, _ = analysed(project)
    with pytest.raises(ValueError, match="has no concern 9"):
        prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha,
                                            selection={"kind": "concern", "ref": 9}, instruction="Check.")


# --- Exact evidence recovery ----------------------------------------------------------------------------------------------------

def test_recovery_gives_the_exact_record_from_the_version_the_analysis_read(project):
    store, analysis_sha, packet = analysed(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha,
        selection={"kind": "mechanism", "ref": mechanism_id(packet, COMPACT)}, instruction="Check the Compact link.")
    payload = json.loads(prepared["request"]["user"])
    link = next(row for row in payload["recovery"]["records"] if row["record_id"] == COMPACT and row["side"] == "proposed")
    assert link["freshness"] == "as_analysed"
    assert link["truncated"] is False
    record = json.loads(link["text"])
    assert record["id"] == COMPACT and "in every season" in record["function"]
    analysis_request = load_host_agent_request(_root(store) / "requests" / analysis_sha / "request.json")
    assert link["version_sha256"] == _digest(json.loads(analysis_request.user)["proposed_candidate"])


def test_coverage_recovery_counts_the_book_elements_the_packet_supplied_and_the_ones_it_read(project):
    from auteur.series.working_book_architecture import book_elements, book_numbers

    store, analysis_sha, packet = analysed(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "reach", "ref": None},
        instruction="Check whether any later Book element cites the change.")
    payload = json.loads(prepared["request"]["user"])
    coverage = payload["recovery"]["coverage"]
    read = sum(len(book_elements(store, number)) for number in book_numbers(store))
    assert coverage["elements_read"] == read
    # The three counts are distinct: every element read, the elements the packet's rule considered, and those it supplied.
    assert coverage["elements_considered_by_packet"] == packet["limits"]["book_elements_considered"]
    assert coverage["elements_supplied_to_analysis"] == packet["limits"]["book_elements_shown"]
    assert coverage["elements_supplied_to_analysis"] <= coverage["elements_considered_by_packet"] <= coverage["elements_read"]
    assert isinstance(coverage["citing_claim_nodes"], list)
    assert coverage["listing_truncated"] == (coverage["citing_count"] > len(coverage["citing_claim_nodes"]))
    assert len(coverage["citing_claim_nodes"]) == min(coverage["citing_count"], 24)


# --- Completion ----------------------------------------------------------------------------------------------------------------

def test_a_completed_reconsideration_is_stored_beside_the_analysis_and_is_current_while_it_is(project):
    store, analysis_sha, packet = analysed(project)
    prepared = prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha, selection=concern_selection(),
                                                   instruction="Check the concern.")
    completed = complete_consequence_reconsideration(store, replay(prepared["request"], answer(packet, evidence=supplied_for(prepared))))
    assert completed["status"] == "ready" and completed["answer"]["disposition"] == "retained"
    (row,) = project_consequence_reconsiderations(store, analysis_sha)
    assert row == completed
    assert row["standing"] == "current"
    assert row["claim"]["original_text"]["title"]


def test_an_answer_citing_an_identifier_the_request_does_not_give_is_refused_by_name(project):
    store, analysis_sha, packet = analysed(project)
    prepared = prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha, selection=concern_selection(),
                                                   instruction="Check the concern.")
    with pytest.raises(ValueError, match="E999"):
        complete_consequence_reconsideration(store, replay(prepared["request"], answer(packet, evidence=["E999"])))


def test_a_correction_must_rest_on_recovered_source_not_on_the_clipped_packet(project):
    store, analysis_sha, packet = analysed(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "mechanism", "ref": mechanism_id(packet, COMPACT)},
        instruction="Check the Compact link.")
    with pytest.raises(ValueError, match="a correction must rest on recovered source"):
        complete_consequence_reconsideration(store, replay(prepared["request"], answer(
            packet, disposition="corrected", evidence=[mechanism_id(packet, COMPACT)])))


def test_criticism_is_assessed_only_where_the_request_supplied_it_and_each_assessment_gives_a_reason(project):
    store, analysis_sha, packet = analysed(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection=concern_selection(), instruction="Check the concern.",
        criticism=["The duty may be a clarification rather than an extension."])
    with pytest.raises(ValueError, match="c2 is not a criticism this request supplied"):
        complete_consequence_reconsideration(store, replay(prepared["request"], answer(
            packet, evidence=supplied_for(prepared), criticism_assessments=[{"criticism": "c2", "verdict": "rejected", "reason": "No such criticism."}])))
    complete_consequence_reconsideration(store, replay(prepared["request"], answer(
        packet, evidence=supplied_for(prepared), criticism_assessments=[{"criticism": "c1", "verdict": "rejected", "reason": "The text says every season."}])))


def test_a_refused_reconsideration_is_kept_beside_its_message_and_leaves_the_analysis_standing(project):
    store, analysis_sha, packet = analysed(project)
    before = result_bytes(store, analysis_sha)
    prepared = prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha, selection=concern_selection(),
                                                   instruction="Check the concern.")
    with pytest.raises(ValueError):
        complete_consequence_reconsideration(store, replay(prepared["request"], {"schema_version": 1}))
    directory = _root(store) / "reconsiderations" / prepared["request"]["request_sha256"] / "refused"
    assert list(directory.glob("*.refusal.txt")) and list(directory.glob("*.json"))
    assert result_bytes(store, analysis_sha) == before
    assert project_architecture_consequence(store)["standing"] == "current"


def test_a_reconsideration_of_an_analysis_no_longer_current_is_historical():
    assert reconsideration_standing("current") == "current"
    assert reconsideration_standing("applied") == "historical"
    assert reconsideration_standing("superseded") == "historical"
    assert reconsideration_standing("stale_context") == "historical"


def test_the_reconsideration_instruction_names_the_dispositions_and_forbids_restating_the_original():
    from auteur.beginner.studio_architecture_reconsideration import _SYSTEM_RECONSIDERATION

    for phrase in ("retained", "corrected", "withdrawn", "recovered", "do not restate"):
        assert phrase in _SYSTEM_RECONSIDERATION.lower(), phrase
