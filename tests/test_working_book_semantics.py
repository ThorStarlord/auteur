"""Semantic integrity of working Book elements: attribution, working status, and commitment authority stay distinct."""
from __future__ import annotations

import copy
import hashlib
import json

import pytest
from pydantic import ValidationError

from auteur.series.working_book_architecture import (
    WorkingBookArchitecture, _check_semantics, project_artifact,
)

QUESTION = "Does the finale keep mechanism A?"
QUESTION_SHA = hashlib.sha256(QUESTION.encode("utf-8")).hexdigest()


def element(identifier, text, *, attribution="agent_proposed", status="asserted", refs=(), **extra):
    return {"id": identifier, "text": text, "refs": list(refs), "attribution": attribution,
            "epistemic_status": status, **extra}


def node(identifier):
    return {"kind": "series_node", "id": identifier}


def book(**overrides) -> dict:
    artifact = {
        "schema_version": 1,
        "book_number": 2,
        "title": "The Gate Question",
        "function": element("fn-question", "Book two asks who may read the ledger.", attribution="derived",
                            refs=[node("str_long_return")], interpretation="The question is the agent's reading.",
                            question="Who may read the ledger?", pressure="Reading rights are unsettled."),
        "inherited": [],
        "engines": [{**element("eng-trust", "Reading rights turn trust into argument."),
                     "condition": "A child asks.", "consequence": "The council answers.",
                     "changed_state": "The gate loses its monopoly."}],
        "agents": [],
        "choice": {
            **element("choice-reading", "The council chooses reading rights."),
            "options": [element("opt-open", "Open the ledger."), element("opt-closed", "Keep it closed.")],
            "chosen_option_id": "opt-open",
            "costs_kept_visible": [element("cost-allotments", "Allotments shrink.")],
            "transformation": element("trans-access", "Access becomes public."),
        },
        "local_resolution": [{**element("res-heirs", "Heirs read the first entry."), "closure": True}],
        "series_consequences": [{**element("cons-return", "The return depends on reading rights."),
                                 "kind": "changes", "refs": [node("str_long_return")]}],
        "later_possibilities": [],
        "assumptions": [{**element("assume-access", "Heirs will read responsibly.", refs=[]),
                         "reversal": "Reverse if reading produces hoarding."}],
        "alternatives": [],
        "unresolved": [],
        "open_author_decisions": [],
        "typed_edges": [],
    }
    artifact.update(overrides)
    return artifact


def parse(data: dict) -> WorkingBookArchitecture:
    return WorkingBookArchitecture.model_validate_json(json.dumps(data))


def views(artifact: WorkingBookArchitecture) -> dict:
    return {view["id"]: view for view in project_artifact(artifact)["elements"]}


# --- historical records stay readable and ambiguous where they were ambiguous ----------------

def test_legacy_record_reads_with_its_original_meaning_and_exposes_unresolved_ambiguity():
    legacy = book()
    for item in (legacy["function"], legacy["engines"][0], legacy["choice"]["transformation"]):
        item.pop("attribution")
        item.pop("epistemic_status")
    legacy["function"].pop("interpretation")
    legacy["function"]["provenance"] = "derived"
    legacy["engines"][0]["provenance"] = "agent_proposed"
    legacy["choice"]["transformation"]["provenance"] = "unresolved"
    legacy["unresolved"] = [{"id": "unk-years", "provenance": "unresolved", "text": "How long is training?"}]
    artifact = parse(legacy)
    seen = views(artifact)
    assert seen["fn-question"]["form"] == "legacy"
    assert seen["fn-question"]["attribution"] == "derived"
    assert seen["eng-trust"]["epistemic_status"] == "asserted"
    assert seen["trans-access"]["attribution"] == "unknown_legacy"
    assert seen["trans-access"]["ambiguous"] is True
    assert seen["trans-access"]["commitment_authority"] == "undecided"
    assert project_artifact(artifact)["summary"]["form"]["legacy_ambiguous"] == 2


def test_legacy_and_explicit_forms_cannot_be_mixed_on_one_element():
    data = book()
    data["function"]["provenance"] = "derived"
    with pytest.raises(ValidationError, match="mixes the legacy provenance"):
        parse(data)


# --- Case 1: an untagged source assertion is not an unanswered fictional question --------------

def test_untagged_source_assertion_is_asserted_with_unknown_attribution_not_unresolved():
    data = book()
    data["inherited"] = [element(
        "inh-gate-independence",
        "Book two does not depend on whether the gate table is kept.",
        attribution="unattributed", status="asserted",
        refs=[node("inst_gate_table")],
    )]
    artifact = parse(data)
    view = views(artifact)["inh-gate-independence"]
    assert view["epistemic_status"] == "asserted"
    assert view["attribution"] == "unattributed"
    assert view["commitment_authority"] == "not_established"
    assert view["ambiguous"] is False


def test_an_asserted_statement_cannot_be_filed_as_an_open_question():
    data = book(unresolved=[element("unk-gate", "Whether the gate table stays.",
                                    attribution="unattributed", status="asserted")])
    with pytest.raises(ValueError, match="listed as unresolved"):
        _check_semantics(parse(data))


# --- Case 2: an assumption without a reversal keeps its provisional nature and its unknown reversal ---

def test_assumption_without_known_reversal_is_provisional_and_not_an_open_decision():
    data = book()
    data["assumptions"] = [{**element("assume-stones", "The stones resolve local return in aggregate."),
                            "reversal": None}]
    artifact = parse(data)
    view = views(artifact)["assume-stones"]
    assert view["epistemic_status"] == "asserted"
    assert view["provisional"] is True
    assert view["reversal_status"] == "unknown"
    assert view["commitment_authority"] == "agent_working"
    _check_semantics(artifact)


# --- Case 3: a genuine author decision stays unresolved and cannot be asserted through a dependent claim ---

def decision(identifier="dec-finale-a", status="unresolved", attribution="derived"):
    return {"id": identifier, "text": "Which finale mechanism does the author keep?",
            "refs": [], "attribution": attribution, "epistemic_status": status,
            "series_question_index": 0, "series_question_sha256": QUESTION_SHA}


def test_author_decision_is_reserved_and_never_asserted():
    data = book(open_author_decisions=[decision()])
    artifact = parse(data)
    assert views(artifact)["dec-finale-a"]["commitment_authority"] == "author_reserved"
    data = book(open_author_decisions=[decision(status="asserted")])
    with pytest.raises(ValidationError, match="must be derived from its Series question and unresolved"):
        parse(data)


def test_claim_that_depends_on_an_author_decision_must_be_conditional_not_asserted():
    asserted = book(open_author_decisions=[decision()])
    asserted["alternatives"] = []
    asserted["later_possibilities"] = [{**element("later-a", "Mechanism A carries the finale.",
                                                  refs=[{"kind": "book_element", "id": "dec-finale-a"}]),
                                        "kind": "enabled"}]
    with pytest.raises(ValueError, match="must be conditional on that decision"):
        _check_semantics(parse(asserted))
    conditional = copy.deepcopy(asserted)
    conditional["later_possibilities"][0].update(epistemic_status="conditional")
    _check_semantics(parse(conditional))
    assert views(parse(conditional))["later-a"]["commitment_authority"] == "agent_working"


def test_conditional_status_requires_a_reference_to_what_it_depends_on():
    data = book()
    data["later_possibilities"] = [{**element("later-b", "A possibility.", status="conditional"),
                                    "kind": "enabled"}]
    with pytest.raises(ValueError, match="needs a reference"):
        _check_semantics(parse(data))


# --- Case 4: a source-derived statement keeps its source relationship and the agent's contribution ----

def test_source_derived_statement_keeps_traceable_reference_and_separate_interpretation():
    data = book()
    data["inherited"] = [element(
        "inh-date", "The Long Return's date is public.", attribution="derived",
        refs=[node("str_long_return"), {"kind": "source_item", "id": "book-2-source"}],
        interpretation="The valley now knows how long it has, so the labour question cannot wait.",
    )]
    artifact = parse(data)
    view = views(artifact)["inh-date"]
    assert view["attribution"] == "derived"
    assert view["interpretation"].startswith("The valley now knows")
    assert view["commitment_authority"] == "agent_working"


def test_derived_statement_without_source_reference_is_rejected():
    data = book()
    data["inherited"] = [element("inh-x", "Claimed from the source.", attribution="derived", refs=[])]
    with pytest.raises(ValidationError, match="must cite a source reference"):
        parse(data)


def test_interpretation_is_only_recorded_on_source_derived_statements():
    data = book()
    data["inherited"] = [{**element("inh-y", "An agent claim.", attribution="agent_proposed"),
                          "interpretation": "Not derived."}]
    with pytest.raises(ValidationError, match="only on a source-derived element"):
        parse(data)


# --- unauthorized authority is refused; projection never grants it ----------------------------

@pytest.mark.parametrize("mutate", [
    lambda d: d["inherited"].append(element("inh-z", "Claim.", attribution="author_supplied")),
    lambda d: d["inherited"].append(element("inh-z", "Claim.", status="accepted")),
    lambda d: d["inherited"].append({**element("inh-z", "Claim.", refs=[node("str_long_return")]), "epistemic_status": "author_fixed"}),
    lambda d: d["inherited"].append({"id": "inh-z", "text": "Claim.", "refs": [], "provenance": "author_fixed"}),
    lambda d: d["inherited"].append({"id": "inh-z", "text": "Claim.", "refs": [], "provenance": "unlabelled"}),
])
def test_author_authority_cannot_be_written_by_an_agent(mutate):
    data = book()
    mutate(data)
    with pytest.raises(ValidationError):
        parse(data)


def test_no_projected_element_ever_carries_author_or_accepted_authority():
    data = book(open_author_decisions=[decision()])
    data["alternatives"] = [{**element("alt-closed", "Keep the ledger closed.", attribution="agent_proposed",
                                       status="hypothetical"),
                             "title": "Closed ledger", "status": "hypothetical", "rationale": "Stable but unexamined."}]
    data["unresolved"] = [element("unk-count", "How many heirs.", attribution="unattributed", status="unresolved")]
    authorities = {view["commitment_authority"] for view in project_artifact(parse(data))["elements"]}
    assert authorities <= {"agent_working", "undecided", "author_reserved", "not_adopted", "not_established", "withdrawn"}


def test_withdrawn_element_projects_as_withdrawn_without_becoming_a_new_truth():
    data = book()
    data["engines"][0]["epistemic_status"] = "rejected"
    view = views(parse(data))["eng-trust"]
    assert view["epistemic_status"] == "rejected"
    assert view["commitment_authority"] == "withdrawn"


def test_a_conditional_claim_may_not_depend_on_a_rejected_assumption():
    data = book()
    data["assumptions"].append({**element("assume-premise", "A working premise.", status="rejected"),
                                "reversal": None})
    data["later_possibilities"] = [{**element("later-x", "Depends on the premise.", status="conditional",
                                              refs=[{"kind": "book_element", "id": "assume-premise"}]),
                                    "kind": "enabled"}]
    with pytest.raises(ValueError, match="which is rejected"):
        _check_semantics(parse(data))


def test_interpretation_changes_are_interpretive_not_representation():
    from auteur.series.working_book_architecture import _classify_change
    before = {"text": "The return is promised.", "attribution": "derived", "epistemic_status": "asserted"}
    after = {**before, "interpretation": "Agent contribution: the valley now knows the date."}
    assert _classify_change(before, after) == "interpretive"
    relabelled = {**before, "attribution": "unattributed"}
    assert _classify_change(before, relabelled) == "representation"
