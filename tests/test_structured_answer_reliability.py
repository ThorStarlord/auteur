"""Structured-answer reliability for the consequence analysis: the authoritative contract reaches the responding agent, the
packet says which identifiers each field may take, every failing rule of one answer is reported together, and a refusal is kept
beside its owner message with a bounded correction. The owner's rules are unchanged; what changes is what the agent is given and
how a refusal is reported. The Spring Ledger study is the specimen; the pure parts use small candidates.
"""
import json
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture_consequence import (
    ConsequenceAnswerV2, ConsequenceAnswerV3, _SYSTEM_V3, _root, complete_architecture_consequence,
    consequence_correction_brief, prepare_architecture_consequence,
)
from auteur.host_agent import load_host_agent_request, model_output_contract

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_architecture_consequence import (  # noqa: E402,F401 - the fixtures and helpers of the owner suite
    INSTRUCTION, packet_of, pristine, project, propose, replay, store_for,
)
from test_architecture_consequence_v3 import (  # noqa: E402
    alternative, check, compact_under_retained_terms, mechanism_answer,
)

WRONG_SHAPE = {"schema_version": 2, "reading": "r", "reach": "local", "no_concern_reason": "none", "concerns": [],
               "mechanisms": [], "inheritance": [], "trajectories": [], "alternatives": [], "not_established": []}


def _request(store, prepared):
    sha = prepared["request"]["request_sha256"]
    return load_host_agent_request(_root(store) / "requests" / sha / "request.json")


# --- Contract delivery -----------------------------------------------------------------------------------------------------------

def test_a_version_three_request_carries_the_authoritative_output_contract_and_it_round_trips_through_disk(project):
    store = store_for(project)
    propose(store, INSTRUCTION, compact_under_retained_terms)
    prepared = prepare_architecture_consequence(store)
    assert prepared["request"]["output_contract"] == model_output_contract(ConsequenceAnswerV3)
    schema_text = json.dumps(prepared["request"]["output_contract"]["json_schema"])
    assert '"instruction_names_it"' in schema_text, "the schema states the literal values of intent"
    assert "^E[1-9][0-9]{0,2}$" in schema_text, "the schema states what an evidence identifier looks like"
    assert "disposition" not in schema_text, "the schema is generated from the owner's model, not a parallel vocabulary"
    assert _request(store, prepared).output_contract == prepared["request"]["output_contract"]


def test_a_version_two_request_carries_the_version_two_contract_and_only_when_it_is_asked_for(project):
    store = store_for(project)
    propose(store, INSTRUCTION, compact_under_retained_terms)
    default = prepare_architecture_consequence(store)["request"]
    assert default["output_contract"] == model_output_contract(ConsequenceAnswerV3)
    historical = prepare_architecture_consequence(store, contract_version=2)["request"]
    assert historical["settings"]["consequence_schema_version"] == 2
    assert historical["output_contract"] == model_output_contract(ConsequenceAnswerV2)


# --- Identifier usability ------------------------------------------------------------------------------------------------------

def test_the_packet_says_which_identifiers_each_field_may_take_and_offers_no_phase_as_an_inheritance_target(project):
    store = store_for(project)
    propose(store, INSTRUCTION, compact_under_retained_terms)
    packet = packet_of(prepare_architecture_consequence(store))
    index = packet["citation_index"]
    evidence = {item["id"]: item for item in packet["evidence"]}

    def ids(predicate):
        return {identifier for identifier, item in evidence.items() if predicate(item)}

    assert set(index["inheritance_to"]) == ids(
        lambda item: item["kind"] in ("book_element", "book_decision", "working_book"))
    assert not set(index["inheritance_to"]) & ids(
        lambda item: item["kind"] in ("recorded_phase", "recorded_history", "mechanism", "baseline_wording"))
    assert set(index["current_mechanisms"]) == ids(
        lambda item: item["kind"] == "mechanism" and item.get("provenance") != "historical")
    assert set(index["instruction"]) == ids(lambda item: item["kind"] == "instruction")
    assert set(index["question_wording"]) == ids(
        lambda item: item["kind"] in ("baseline_wording", "proposed_wording", "removed"))
    assert set(index["inheritance_to_recorded"]) <= set(index["inheritance_to"])


# --- Combined refusals ---------------------------------------------------------------------------------------------------------

def test_every_failing_rule_of_one_answer_is_reported_together_and_each_is_stated_once():
    with pytest.raises(ValueError) as refusal:
        check(alternatives=[alternative("defer", anchors_m=["E4"], keeps=["E7"]),
                            alternative("keep_baseline", anchors_m=["E6"], keeps=["E6"])])
    message = str(refusal.value)
    assert message.startswith("2 rules are not met")
    assert "1. alternative 'defer E4' keeps no record of E4" in message
    assert "2. alternative 'keep_baseline E6'" in message
    assert message.count("must keep the baseline record of E6") == 1


def test_a_single_failing_rule_keeps_its_own_wording_without_a_count():
    with pytest.raises(ValueError) as refusal:
        check(alternatives=[alternative("defer", anchors_m=["E4"], keeps=["E7"])])
    assert str(refusal.value).startswith("alternative 'defer E4' keeps no record of E4")


# --- Bounded correction --------------------------------------------------------------------------------------------------------

def test_a_refused_answer_keeps_the_owner_refusal_beside_it_and_an_accepted_correction_records_its_attempt(project):
    store = store_for(project)
    propose(store, INSTRUCTION, compact_under_retained_terms)
    prepared = prepare_architecture_consequence(store)
    packet = packet_of(prepared)
    with pytest.raises(ValueError) as refusal:
        complete_architecture_consequence(store, replay(prepared["request"], WRONG_SHAPE))
    directory = _root(store) / "requests" / prepared["request"]["request_sha256"] / "refused"
    sidecars = list(directory.glob("*.refusal.txt"))
    assert len(sidecars) == 1
    assert sidecars[0].read_text(encoding="utf-8").strip() == str(refusal.value).strip()
    assert list(directory.glob("*.json")), "the refused response itself is kept, unedited"
    projection = complete_architecture_consequence(store, replay(prepared["request"], mechanism_answer(packet)))
    assert projection["result"]["completion"] == {"attempt": 2, "refused_attempts": 1, "first_pass": False}


def test_a_first_pass_acceptance_is_recorded_as_first_pass(project):
    store = store_for(project)
    propose(store, INSTRUCTION, compact_under_retained_terms)
    prepared = prepare_architecture_consequence(store)
    projection = complete_architecture_consequence(store, replay(prepared["request"], mechanism_answer(packet_of(prepared))))
    assert projection["result"]["completion"] == {"attempt": 1, "refused_attempts": 0, "first_pass": True}


def test_the_correction_brief_quotes_the_refusal_unedited_and_asks_only_for_the_same_analysis(project):
    store = store_for(project)
    propose(store, INSTRUCTION, compact_under_retained_terms)
    prepared = prepare_architecture_consequence(store)
    request = _request(store, prepared)
    refusal = "2 rules are not met:\n1. concern 'X' says the instruction names it but cites no instruction\n2. inheritance"
    brief = consequence_correction_brief(request, refusal, attempt=2)
    assert refusal in brief
    assert request.request_id in brief
    assert "Return ONLY the JSON object" in brief
    assert "Do not add new claims" in brief


# --- Instruction shape rules the schema cannot state ---------------------------------------------------------------------------

def test_the_version_three_instruction_states_the_shapes_the_schema_cannot_express():
    for phrase in (
        "never a basis word",
        "plain strings",
        "each {text, evidence}",
        "omits intent",
        "citation_index",
        "never a recorded_phase",
    ):
        assert phrase in _SYSTEM_V3, phrase


# --- The inquiry path, which relational reasoning uses ------------------------------------------------------------------------

def test_an_inquiry_request_carries_the_authoritative_output_contract_of_the_answer_it_asks_for(project):
    from auteur.beginner.studio_architecture import project_architecture
    from auteur.beginner.studio_architecture_inquiry import ArchitectureInquiryResult, prepare_architecture_inquiry

    store = store_for(project)
    pending = prepare_architecture_inquiry(store, {
        "version": 1, "canvas_id": store.canvas_id, "operation": "explore", "target": "current",
        "expected_candidate_request_sha256": project_architecture(store)["candidate_request_sha256"],
        "anchors": [{"kind": "question", "id": "q-conversion-settlement"}],
        "author_text": "Explore whether the shared accounting of care could bind the conversion.",
    })
    assert pending["request"]["output_contract"] == model_output_contract(ArchitectureInquiryResult)
