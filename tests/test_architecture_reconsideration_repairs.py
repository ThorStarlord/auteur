"""Repairs to the consequence reconsideration owner, on the Spring Ledger study.

Evidence admission: a citation resolves only to evidence this request supplies or the owner recovered. Standing: a reconsideration of
an analysis that is no longer the latest is historical, even while its proposal is live. Recovery: the selected creative alternative
and the revision instruction come back in full from the revision request they were adopted in, validated by lineage. Handoff: an
accepted reconsideration can be carried, with its identities, judgement, evidence freshness and standing, into later creative work.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import _candidate, _root as architecture_root, complete_architecture, prepare_architecture
from auteur.beginner.studio_architecture_consequence import (
    _root as consequence_root, complete_architecture_consequence, prepare_architecture_consequence,
)
from auteur.beginner.studio_architecture_reconsideration import (
    AUTHORITY, complete_consequence_reconsideration, prepare_consequence_reconsideration, project_consequence_reconsiderations,
    reconsideration_handoff, selected_alternative_problems,
)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_architecture_consequence import INSTRUCTION, base, packet_of, project, propose, pristine, replay, store_for  # noqa: E402,F401
from test_architecture_consequence_v3 import compact_under_retained_terms, mechanism_answer  # noqa: E402
from test_architecture_reconsideration import supplied_for  # noqa: E402

CHANGE = "Make the Mill Compact's labour duty apply in every season."
LONG_DESCRIPTION = ("What changes: the declined share's unkept water is routed into the refusing household's own holding. " * 6
                    + "The reader must weigh whether refusal is a real option when only households with spare hands can "
                      "absorb a flooded holding.")


def consequence_analysis(project_dir, instruction=CHANGE, edit=compact_under_retained_terms):
    """A pending revision analysed on the Spring Ledger study. Returns (store, analysis request sha, packet)."""
    store = store_for(project_dir)
    propose(store, instruction, edit)
    prepared = prepare_architecture_consequence(store)
    packet = packet_of(prepared)
    complete_architecture_consequence(store, replay(prepared["request"], mechanism_answer(packet)))
    return store, prepared["request"]["request_sha256"], packet


def adopted_alternative_analysis(project_dir):
    """A pending revision that adopts a long inquiry alternative, then analysed. Returns (store, analysis sha, packet)."""
    store = store_for(project_dir)
    inquiry_sha = "d" * 64
    folder = architecture_root(store) / "inquiries" / "requests" / inquiry_sha
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result.json").write_text(json.dumps({
        "baseline_candidate_request_sha256": _candidate(store)["request_sha256"],
        "intent": {"operation": "compare", "author_text": "Consider the declined share.", "anchors": []},
        "hypotheses": [{"id": "h1", "title": "Refusal drains to the refuser's own ground", "description": LONG_DESCRIPTION,
                        "divergence_axis": "causal_engine"}],
    }), encoding="utf-8")
    revised = copy.deepcopy(_candidate(store)["candidate"])
    compact_under_retained_terms(revised)
    waiting = prepare_architecture(store, instruction=CHANGE,
                                   selected_alternative={"inquiry_request_sha256": inquiry_sha, "hypothesis_id": "h1"})
    complete_architecture(store, base._reply(waiting["request"], revised, "consequence-test"))
    prepared = prepare_architecture_consequence(store)
    packet = packet_of(prepared)
    alternative_id = next(item["id"] for item in packet["evidence"] if item["kind"] == "selected_alternative")
    answer = mechanism_answer(packet)
    # The analysis names the alternative in its first concern, so a claim that rests on it can be reconsidered.
    answer["concerns"][0]["evidence"] = answer["concerns"][0]["evidence"] + [alternative_id]
    complete_architecture_consequence(store, replay(prepared["request"], answer))
    return store, prepared["request"]["request_sha256"], packet, waiting["request"]["request_sha256"]


def reach_answer(packet, **overrides):
    evidence = [item["id"] for item in packet["evidence"]][:2]
    base_answer = {"schema_version": 1, "disposition": "retained",
                   "new_consideration": "The reach was weighed against the recovered revision record.",
                   "reconsidered_judgment": "The reach stands as the analysis stated it.",
                   "evidence": evidence, "criticism_assessments": [], "remaining_uncertainty": [], "downstream": []}
    base_answer.update(overrides)
    return base_answer


# --- Evidence admission ---------------------------------------------------------------------------------------------------------

def test_a_citation_to_evidence_the_request_does_not_supply_is_refused_as_unsupplied(project):
    store, analysis_sha, packet = consequence_analysis(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "concern", "ref": 0},
        instruction="Check the concern against its own evidence.")
    claim_evidence = set(prepared["reconsideration"]["claim"]["evidence"])
    outside = next(item["id"] for item in packet["evidence"] if item["id"] not in claim_evidence)
    answer = {"schema_version": 1, "disposition": "retained", "new_consideration": "Checked.",
              "reconsidered_judgment": "Stands.", "evidence": [outside], "criticism_assessments": [],
              "remaining_uncertainty": [], "downstream": []}
    with pytest.raises(ValueError, match=f"the answer cites {outside}, whose content is not supplied to this reconsideration"):
        complete_consequence_reconsideration(store, replay(prepared["request"], answer))


def test_the_request_names_what_it_supplies_and_what_the_analysis_merely_read(project):
    store, analysis_sha, packet = consequence_analysis(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "concern", "ref": 0}, instruction="Check the concern.")
    user = json.loads(prepared["request"]["user"])
    supplied = {item["id"] for item in user["original_evidence"]} | set(user["recovered_evidence"])
    assert set(user["allowed_evidence"]) == supplied
    assert set(user["historically_available"]) == {item["id"] for item in packet["evidence"]} - {
        item["id"] for item in user["original_evidence"]}
    assert not set(user["allowed_evidence"]) & set(user["historically_available"])


# --- Standing --------------------------------------------------------------------------------------------------------------------

def test_a_reconsideration_of_an_analysis_that_is_no_longer_the_latest_is_historical_while_its_proposal_is_live(project):
    store, analysis_sha, _packet = consequence_analysis(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "concern", "ref": 0}, instruction="Check the concern.")
    assert prepared["reconsideration"]["standing"] == "current"
    prepare_architecture_consequence(store, contract_version=2)  # a later analysis of the same live proposal
    rows = project_consequence_reconsiderations(store, analysis_sha)
    assert rows[0]["analysis_standing"] == "superseded"
    assert rows[0]["standing"] == "historical"
    assert rows[0]["claim"]["kind"] == "concern", "the historical judgement keeps its claim"


# --- Recovery of the selected creative alternative and its instruction ----------------------------------------------------

def test_a_reach_reconsideration_recovers_the_selected_alternative_in_full_from_the_request_it_was_adopted_in(project):
    store, analysis_sha, packet, review_sha = adopted_alternative_analysis(project)
    item = next(i for i in packet["evidence"] if i["kind"] == "selected_alternative")
    assert len(item["text"]) < len(LONG_DESCRIPTION), "the packet clipped the alternative the reconsideration must recover"
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "reach", "ref": None},
        instruction="Does the reach keep the alternative's reader experience?")
    records = {row["record_kind"]: row for row in json.loads(prepared["request"]["user"])["recovery"]["records"]}
    alternative = records["selected_alternative"]
    assert alternative["source"] == "recovered" and alternative["freshness"] == "as_analysed"
    assert alternative["version_sha256"] == review_sha, "the version is the revision request the alternative was adopted in"
    assert alternative["text"] == f"Refusal drains to the refuser's own ground. {LONG_DESCRIPTION}"
    assert alternative["truncated"] is False
    instruction = records["revision_instruction"]
    assert instruction["text"] == CHANGE


def test_the_lineage_of_a_recovered_alternative_must_match_the_packet_that_names_it():
    item = {"inquiry_request_sha256": "a" * 64, "hypothesis_id": "h1", "text": "Title. The description begins here and"
                                                                                       " continues…"}
    full = "Title. The description begins here and continues for the reader."
    selected = {"inquiry_request_sha256": "a" * 64, "hypothesis_id": "h1"}
    assert selected_alternative_problems(selected, item, full) == []
    assert selected_alternative_problems({**selected, "inquiry_request_sha256": "b" * 64}, item, full) == [
        "its inquiry is not the inquiry the analysis read"]
    assert selected_alternative_problems({**selected, "hypothesis_id": "h2"}, item, full) == [
        "its hypothesis is not the one the analysis read"]
    assert selected_alternative_problems(selected, item, "Title. A different text entirely.") == [
        "its full text does not begin with the text the analysis read"]
    assert selected_alternative_problems(None, item, full) == ["the revision request holds no selected creative alternative"]


# --- Handoff of an accepted reconsideration -------------------------------------------------------------------------------

def test_an_accepted_reconsideration_hands_off_its_identities_judgement_freshness_and_standing(project):
    store, analysis_sha, packet = consequence_analysis(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "concern", "ref": 0}, instruction="Check the concern.")
    complete_consequence_reconsideration(store, replay(prepared["request"], reach_answer(
        packet, evidence=supplied_for(prepared))))
    request_sha = prepared["request"]["request_sha256"]
    handoff = reconsideration_handoff(store, request_sha)
    assert handoff["authority"] == AUTHORITY
    assert handoff["analysis_request_sha256"] == analysis_sha
    assert len(handoff["analysis_result_sha256"]) == 64
    assert handoff["reconsideration_request_sha256"] == request_sha
    assert handoff["claim"]["kind"] == "concern" and len(handoff["claim"]["claim_sha256"]) == 64
    assert handoff["disposition"] == "retained"
    assert handoff["reconsidered_judgment"] == "The reach stands as the analysis stated it."
    assert handoff["standing"] == "current" and handoff["analysis_standing"] == "current"
    assert handoff["evidence"] and all(row["freshness"] and row["owner"] for row in handoff["evidence"])
    assert handoff["remaining_uncertainty"] == [] and handoff["downstream"] == []


def test_a_reconsideration_still_awaiting_its_answer_is_not_handed_off(project):
    store, analysis_sha, _packet = consequence_analysis(project)
    prepared = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "concern", "ref": 0}, instruction="Check the concern.")
    with pytest.raises(ValueError, match="no completed reconsideration"):
        reconsideration_handoff(store, prepared["request"]["request_sha256"])


def test_a_claim_that_names_the_selected_alternative_recovers_it_in_full_as_well(project):
    store, analysis_sha, packet, _review_sha = adopted_alternative_analysis(project)
    alternative_id = next(item["id"] for item in packet["evidence"] if item["kind"] == "selected_alternative")
    result = json.loads((consequence_root(store) / "requests" / analysis_sha / "result.json").read_text(encoding="utf-8"))
    named = [("concern", index) for index, row in enumerate(result.get("concerns") or []) if alternative_id in row.get("evidence", [])]
    named += [("connection", index) for index, row in enumerate(result.get("connections") or [])
              if alternative_id in row.get("evidence", [])]
    assert named, "the adopted analysis has a claim that names the selected alternative"
    kind, ref = named[0]
    prepared = prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha, selection={"kind": kind, "ref": ref},
                                                   instruction="Read the claim against the alternative it came from.")
    records = {row["record_kind"]: row for row in json.loads(prepared["request"]["user"])["recovery"]["records"]}
    assert records["selected_alternative"]["text"].endswith("absorb a flooded holding.")
    assert records["selected_alternative"]["source"] == "recovered"
