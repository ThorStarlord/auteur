"""Long-horizon creative synthesis, on the Spring Ledger study.

A synthesis reads one to three developments, the Working Book elements that cite them, the links among them and any accepted
reconsiderations offered as handoffs. It is bounded, explicit, advisory and stored beside its request. Every citation must resolve to
evidence the request carries; a stage's basis must rest on cited evidence; a follow-up carries its earlier judgement as text only.
Standing is current, superseded or stale, read from a recomputed evidence fingerprint. No record changes.
"""
import json
import sys
from pathlib import Path

import pytest

from auteur.beginner import studio_architecture as arch
from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture_reconsideration import (
    complete_consequence_reconsideration, prepare_consequence_reconsideration,
)
from auteur.beginner.studio_architecture_synthesis import (
    SynthesisAnswer, complete_architecture_synthesis, prepare_architecture_synthesis, project_architecture_synthesis,
)
from auteur.host_agent import HostAgentRequest, build_host_agent_response, model_output_contract
from auteur.series.working_book_architecture import book_elements, book_numbers

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_architecture_consequence import edit_vision, pristine, project, store_for  # noqa: E402,F401
from test_architecture_reconsideration import analysed  # noqa: E402

COMPACT_QUESTION = "q-compact-settlement"
MECHANISM = "th_maintenance"


def replay(request: dict, payload: dict) -> dict:
    """The owner's response envelope for this request and an agent's unedited answer (what the host would return)."""
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(payload), runtime="synthesis-test").model_dump()


def question_selection(ref=COMPACT_QUESTION):
    return {"kind": "question", "ref": ref}


def valid_answer(user: dict, **overrides) -> dict:
    """A well-formed synthesis that cites the first development and never invents a Book."""
    cited = user["developments"][0]["evidence"]
    answer = {
        "schema_version": 1,
        "trajectory": [
            {"book": 24, "horizon": "existing_book", "development": "The compact's grain-labour duty is first met by a named household.",
             "becomes_available": "The labour duty is recorded as owed to the rebuild.", "changes": "It makes the settlement a question of who carries the duty.",
             "basis": "recorded", "evidence": [cited]},
            {"book": None, "horizon": "proposed_book", "development": "A later Book tests whether the settlement holds under a poor harvest.",
             "becomes_available": "The settlement has been carried by a household for a full season.",
             "changes": "It turns the settlement from a promise into a practice the reader can judge.",
             "basis": "proposed", "evidence": [cited]},
        ],
        "relations": [],
        "culmination": None,
        "alternative_paths": [{"ordering": "If the settlement comes after the harvest test, the duty reads as a remedy.",
                               "effect": "The reader meets the failure before the remedy.", "viability": "viable", "evidence": []}],
        "opportunities": [],
        "reader_experience": "The reader feels the settlement as a debt that has to be paid in person.",
        "open_decisions": ["Who carries the duty when the household cannot."],
        "uncertainty": [],
        "criticism_assessments": [],
        "changes_from_prior": [],
    }
    answer.update(overrides)
    return answer


def prepared(store, **overrides):
    arguments = {"question": "How might the compact's settlement develop across the next Books without becoming repetitive?",
                 "developments": [question_selection()]}
    arguments.update(overrides)
    return prepare_architecture_synthesis(store, **arguments)


# --- Binding, admission and determinism -------------------------------------------------------------------------------------------

def test_a_synthesis_is_prepared_bound_to_its_developments_and_the_evidence_it_admits(project):
    store = store_for(project)
    result = prepared(store)
    request = result["request"]
    user = json.loads(request["user"])
    assert request["settings"]["operation"] == "synthesize_architecture_development"
    assert request["output_contract"] == model_output_contract(SynthesisAnswer)
    development = user["developments"][0]
    assert development["kind"] == "question" and development["ref"] == COMPACT_QUESTION
    evidence = {item["id"]: item for item in user["evidence"]}
    assert evidence[development["evidence"]]["kind"] == "development"
    assert evidence[development["evidence"]]["text"].startswith("Does the Compact accept grain-labour")
    assert user["allowed_evidence"] == list(evidence), "every identifier the request names is supplied in full"
    assert result["synthesis"]["standing"] == "current" and result["synthesis"]["status"] == "awaiting_host_agent"


def test_the_same_inputs_prepare_the_same_synthesis(project):
    store = store_for(project)
    first = prepared(store)["request"]["request_sha256"]
    second = prepared(store)["request"]["request_sha256"]
    assert first == second


def test_the_coverage_counts_are_exact_and_the_excerpts_are_bounded(project):
    store = store_for(project)
    user = json.loads(prepared(store)["request"]["user"])
    coverage = next(item["coverage"] for item in user["evidence"] if item["kind"] == "coverage")
    total = sum(len(book_elements(store, number)) for number in book_numbers(store))
    expected = sum(1 for number in book_numbers(store) for element in book_elements(store, number)
                   if COMPACT_QUESTION in (element.get("question_refs") or []))
    assert coverage["elements_read"] == total
    assert coverage["citing_elements_by_development"]["d1"]["citing"] == expected
    excerpted = [item for item in user["evidence"] if item["kind"] == "book_element"]
    assert len(excerpted) == min(expected, 12) and all(len(item["text"]) <= 400 for item in excerpted)


def test_a_mechanism_development_reads_its_record_and_the_elements_that_cite_it(project):
    store = store_for(project)
    user = json.loads(prepared(store, developments=[{"kind": "mechanism", "ref": MECHANISM}])["request"]["user"])
    record = next(item for item in user["evidence"] if item["id"] == user["developments"][0]["evidence"])
    assert record["kind"] == "development" and MECHANISM in record["text"]
    citing = [item for item in user["evidence"] if item["kind"] == "book_element"]
    assert citing and all(item["cites"] == ["d1"] for item in citing)


def test_developments_the_architecture_does_not_hold_are_refused_by_name(project):
    store = store_for(project)
    with pytest.raises(ValueError, match="the current Architecture has no question 'q-missing'"):
        prepared(store, developments=[question_selection("q-missing")])
    with pytest.raises(ValueError, match="the current Architecture has no mechanism 'th_missing'"):
        prepared(store, developments=[{"kind": "mechanism", "ref": "th_missing"}])
    with pytest.raises(ValueError, match="one to 3 developments"):
        prepared(store, developments=[])


def test_a_follow_up_must_continue_the_same_developments(project):
    store = store_for(project)
    first = prepared(store)["request"]
    complete(store, first, valid_answer(json.loads(first["user"])))
    with pytest.raises(ValueError, match="a follow-up continues the same developments"):
        prepared(store, developments=[{"kind": "mechanism", "ref": MECHANISM}], prior_request_sha256=first["request_sha256"])
    with pytest.raises(ValueError, match="not completed"):
        prepared(store, question="Not yet answered.", prior_request_sha256=prepared(
            store, question="A request awaiting its answer.")["request"]["request_sha256"])


# --- Owner refusals ---------------------------------------------------------------------------------------------------------------

def complete(store, request, answer):
    return complete_architecture_synthesis(store, replay(request, answer))


def test_a_valid_synthesis_is_stored_as_a_judgement_and_changes_no_record(project):
    store = store_for(project)
    before_items = [item.model_dump(mode="json") for item in store.load().items]
    before_candidate = arch._candidate(store)
    request = prepared(store)["request"]
    row = complete(store, request, valid_answer(json.loads(request["user"])))
    assert row["status"] == "ready" and row["standing"] == "current"
    assert row["result"]["trajectory"][0]["basis"] == "recorded"
    assert [item.model_dump(mode="json") for item in store.load().items] == before_items, "no working item changed"
    assert arch._candidate(store) == before_candidate, "the Architecture is unchanged"


def test_an_answer_citing_evidence_the_request_does_not_carry_is_refused_by_name(project):
    store = store_for(project)
    request = prepared(store)["request"]
    with pytest.raises(ValueError, match="the answer cites E999, which is not in this request"):
        complete(store, request, valid_answer(json.loads(request["user"]), alternative_paths=[{
            "ordering": "x", "effect": "y", "viability": "viable", "evidence": ["E999"]}]))


def test_a_stage_that_names_no_book_that_exists_or_that_is_proposed_with_a_book_is_refused(project):
    store = store_for(project)
    request = prepared(store)["request"]
    user = json.loads(request["user"])
    answer = valid_answer(user)
    answer["trajectory"][0]["book"] = 26
    with pytest.raises(ValueError, match="s1 names Book 26, which is not a Working Book of this Architecture"):
        complete(store, request, answer)
    answer = valid_answer(user)
    answer["trajectory"][1]["book"] = 25
    with pytest.raises(ValueError, match="s2 is a proposed Book and must not name a Book number"):
        complete(store, request, answer)


def test_a_recorded_or_inferred_stage_must_rest_on_cited_evidence(project):
    store = store_for(project)
    request = prepared(store)["request"]
    answer = valid_answer(json.loads(request["user"]))
    answer["trajectory"][0]["evidence"] = []
    with pytest.raises(ValueError, match="s1 is recorded and cites no evidence"):
        complete(store, request, answer)


def test_a_relation_or_opportunity_must_refer_to_a_development_or_stage_of_this_synthesis(project):
    store = store_for(project)
    request = prepared(store)["request"]
    user = json.loads(request["user"])
    answer = valid_answer(user, relations=[{"kind": "preparation", "between": ["s1", "s4"], "dependence": "causal",
                                            "reason": "x", "evidence": []}])
    with pytest.raises(ValueError, match="a relation refers to s4, which is not a development or stage of this synthesis"):
        complete(store, request, answer)


def test_a_named_culmination_must_be_reasoned_about(project):
    store = store_for(project)
    request = prepared(store, culmination="The household that refuses the rota is the one the finale must answer.")["request"]
    with pytest.raises(ValueError, match="the author named a culmination; the answer must reason about it"):
        complete(store, request, valid_answer(json.loads(request["user"])))
    culminating = valid_answer(json.loads(request["user"]), culmination={
        "statement": "The finale answers the refusing household.", "necessary": [
            {"text": "The duty has been carried once in full.", "evidence": [json.loads(request["user"])["developments"][0]["evidence"]]}],
        "enrichment": [], "standalone_value": "Books 24 and 25 keep their own reckoning of the duty."})
    assert complete(store, request, culminating)["result"]["culmination"]["statement"].startswith("The finale")


def test_changes_from_prior_needs_an_earlier_judgement(project):
    store = store_for(project)
    request = prepared(store)["request"]
    with pytest.raises(ValueError, match="changes_from_prior names a change from an earlier judgement"):
        complete(store, request, valid_answer(json.loads(request["user"]), changes_from_prior=["The duty is narrower."]))


def test_a_refused_synthesis_is_kept_beside_its_message_and_is_not_the_synthesis(project):
    store = store_for(project)
    request = prepared(store)["request"]
    folder = arch._root(store) / "synthesis" / "requests" / request["request_sha256"]
    with pytest.raises(ValueError):
        complete(store, request, valid_answer(json.loads(request["user"]), changes_from_prior=["x"]))
    assert list((folder / "refused").glob("*.refusal.txt")) and list((folder / "refused").glob("*.json"))
    assert not (folder / "result.json").exists()
    assert project_architecture_synthesis(store)["result"] is None


# --- Standing ----------------------------------------------------------------------------------------------------------------------

def test_a_later_synthesis_supersedes_an_earlier_one_and_an_edited_vision_makes_the_current_one_stale(project):
    store = store_for(project)
    first = prepared(store)["request"]
    complete(store, first, valid_answer(json.loads(first["user"])))
    second = prepared(store, question="A different question on the same development.")
    assert second["synthesis"]["standing"] == "current"
    history = {row["request_sha256"]: row for row in project_architecture_synthesis(store)["history"]}
    assert history[first["request_sha256"]]["standing"] == "superseded"
    edit_vision(store)
    projection = project_architecture_synthesis(store)
    assert projection["standing"] == "stale" and projection["status"] == "unanswered"


def test_a_stale_request_refuses_a_response_that_would_describe_changed_material(project):
    store = store_for(project)
    request = prepared(store)["request"]
    edit_vision(store)
    with pytest.raises(BeginnerConcurrencyError, match="has changed since it was prepared"):
        complete(store, request, valid_answer(json.loads(request["user"])))


# --- Follow-up and handoff -----------------------------------------------------------------------------------------------------

def test_a_follow_up_carries_the_earlier_judgement_as_text_and_weighs_the_criticism_it_is_given(project):
    store = store_for(project)
    first = prepared(store)["request"]
    complete(store, first, valid_answer(json.loads(first["user"])))
    follow = prepared(store, prior_request_sha256=first["request_sha256"],
                      criticism=["The settlement is a promise the record does not yet show anyone keeping."])
    user = json.loads(follow["request"]["user"])
    assert user["prior_judgement"]["request_sha256"] == first["request_sha256"]
    assert "not evidence" in user["prior_judgement"]["note"]
    answer = valid_answer(user, criticism_assessments=[{"criticism": "c1", "verdict": "partly_accepted",
                                                        "reason": "The record shows the duty owed, not yet kept."}],
                          changes_from_prior=["The stage that tests the settlement is now marked as a proposal, not a record."])
    row = complete(store, follow["request"], answer)
    assert row["result"]["criticism_assessments"][0]["verdict"] == "partly_accepted"
    current = project_architecture_synthesis(store)
    assert current["request_sha256"] == follow["request"]["request_sha256"] and current["standing"] == "current"


def test_an_accepted_reconsideration_is_carried_as_a_handoff_with_its_standing(project):
    store, analysis_sha, packet = analysed(project)
    prepared_reconsideration = prepare_consequence_reconsideration(
        store, analysis_request_sha256=analysis_sha, selection={"kind": "concern", "ref": 0}, instruction="Check the concern.")
    admitted = json.loads(prepared_reconsideration["request"]["user"])["allowed_evidence"][:2]
    complete_consequence_reconsideration(store, replay(prepared_reconsideration["request"], {
        "schema_version": 1, "disposition": "retained", "new_consideration": "Weighed against the recorded duty.",
        "reconsidered_judgment": "The concern stands as the analysis stated it.", "evidence": admitted,
        "criticism_assessments": [], "remaining_uncertainty": [], "downstream": []}))
    handoff_sha = prepared_reconsideration["request"]["request_sha256"]
    result = prepared(store, handoffs=[handoff_sha])
    user = json.loads(result["request"]["user"])
    handoff = next(item for item in user["evidence"] if item["kind"] == "handoff")
    assert handoff["reconsideration_request_sha256"] == handoff_sha
    assert handoff["freshness"] == "current" and handoff["source"] == "reconsideration"
    assert user["handoffs"][0]["evidence"] == handoff["id"]
    answer = valid_answer(user)
    answer["trajectory"][0]["evidence"] = [handoff["id"]]
    assert complete(store, result["request"], answer)["result"]["trajectory"][0]["evidence"] == [handoff["id"]]


def test_the_answer_schema_is_strict_about_unknown_fields():
    with pytest.raises(Exception):
        SynthesisAnswer.model_validate({"schema_version": 1, "unexpected": True})


def test_the_coverage_states_which_cited_elements_carry_the_same_text_in_another_book(project):
    store = store_for(project)
    user = json.loads(prepared(store, developments=[{"kind": "mechanism", "ref": MECHANISM}])["request"]["user"])
    coverage = next(item["coverage"] for item in user["evidence"] if item["kind"] == "coverage")
    pairs = {(row["book"], row["element_id"]): row["same_text_in_books"] for row in coverage["same_text_elsewhere"]["listed"]}
    assert pairs[(24, "agent-lineages")] == [25] and pairs[(25, "agent-lineages")] == [24]
    assert len(pairs) == 10, "five elements repeat across the two Books, each reported from both sides"
    assert (24, "later-cohort-seat") not in pairs, "an element whose text appears once is not reported as repeated"


def test_a_synthesis_of_other_developments_does_not_supersede_an_earlier_one(project):
    store = store_for(project)
    first = prepared(store)["request"]
    complete(store, first, valid_answer(json.loads(first["user"])))
    other = prepared(store, developments=[{"kind": "mechanism", "ref": MECHANISM}], question="A different development.")
    assert other["synthesis"]["standing"] == "current"
    history = {row["request_sha256"]: row for row in project_architecture_synthesis(store)["history"]}
    assert history[first["request_sha256"]]["standing"] == "current", "superseded only by a later reading of the same developments"
