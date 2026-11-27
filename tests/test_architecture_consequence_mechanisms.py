"""Mechanism-grounded consequence analysis (version 2): recorded mechanisms, inheritance and trajectories.

The inventory and the element selection are pure, so they are tested on small candidates. The packet, the owner's checks and the
investigation carry-through are tested on the Spring Ledger study, the same specimen the consequence analysis is proven on, with
the same propose-and-prepare path the owner uses. A mechanism that keeps its identifier is never called unchanged in function:
the provenance tests assert identity and recorded content, not meaning.
"""
import copy
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture_consequence import (
    APPROACH_MEANINGS, ConsequenceAnswerV2, _check_answer_v2, _SYSTEM_V2, complete_architecture_consequence,
    consequence_origin, prepare_architecture_consequence, project_architecture_consequence,
)
from auteur.beginner.studio_architecture_mechanisms import (
    MAX_BOOK_ELEMENTS, MAX_MECHANISMS, _ELEMENT_CLASSES as ELEMENT_CLASSES, book_element_candidates, mechanism_inventory,
    seed_node_identifiers,
)
from auteur.beginner.studio_store import CanvasStore

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_architecture_consequence import (  # noqa: E402,F401 - the fixtures and helpers of the owner suite
    BOOK, INSTRUCTION, Q_COMPACT, Q_CONVERSION, evidence_id, packet_of, pristine, project, propose, replay,
    reword_conversion, store_for, valid_answer,
)


def node(identifier, summary="s", **extra):
    return {"id": identifier, "title": identifier.upper(), "category": "structure", "summary": summary, **extra}


def link(identifier, source, target, function="f"):
    return {"id": identifier, "source": source, "target": target, "function": function}


# --- The inventory: provenance is an identity fact, and every record says why it is present --------------------------------

def test_the_inventory_names_each_provenance_from_the_records_themselves():
    baseline = {"nodes": [node("n1"), node("n2"), node("n6", "gone in proposal")],
                "links": [link("l1", "n1", "n2"), link("l2", "n2", "n6", "f2")]}
    proposed = {"nodes": [node("n1", "reworded summary"), node("n3")],
                "links": [link("l1", "n1", "n2"), link("l3", "n3", "n1", "f3")]}
    inventory = mechanism_inventory(baseline, proposed, book_nodes={}, historical=[])
    by_id = {(row["record_kind"], row["record_id"]): row for row in inventory["items"]}

    assert by_id[("node", "n1")]["provenance"] == "transformed"
    assert by_id[("node", "n1")]["changed_fields"] == ["summary"]
    assert by_id[("node", "n6")]["provenance"] == "removed"
    assert by_id[("node", "n3")]["provenance"] == "introduced"
    assert by_id[("link", "l2")]["provenance"] == "removed"
    assert by_id[("link", "l3")]["provenance"] == "introduced"
    # An unchanged record that touches a changed node is present by one hop, and is preserved, not transformed.
    assert by_id[("link", "l1")]["provenance"] == "preserved"
    assert by_id[("link", "l1")]["routes"] == ["adjacent_to:n1,n2"]
    assert by_id[("node", "n1")]["baseline_sha256"] != by_id[("node", "n1")]["proposed_sha256"]


def test_a_preserved_record_is_identical_on_both_sides_and_carries_both_digests():
    candidate = {"nodes": [node("n1")], "links": []}
    inventory = mechanism_inventory(candidate, copy.deepcopy(candidate), book_nodes={"n1": [24]}, historical=[])
    (row,) = inventory["items"]
    assert row["provenance"] == "preserved"
    assert row["routes"] == ["referenced_by_working_book:24"]
    assert row["book_references"] == [24]
    assert row["baseline_sha256"] == row["proposed_sha256"]


def test_an_earlier_applied_version_gives_a_historical_record_that_is_no_longer_current():
    baseline = {"nodes": [node("n1")], "links": []}
    earlier = {"nodes": [node("n1"), node("n9", "retired in Book 22")], "links": []}
    inventory = mechanism_inventory(baseline, baseline, book_nodes={}, historical=[("req-old", earlier)])
    (row,) = inventory["items"]
    assert row["record_id"] == "n9" and row["provenance"] == "historical"
    assert row["routes"] == ["historical_in_revision"]
    assert row["version_request_sha256"] == "req-old"
    assert row["proposed_sha256"] is None and row["baseline_sha256"] is None
    assert row["baseline_text"] is None and row["proposed_text"] is None
    assert row["historical_text"] and row["historical_sha256"]
    assert row["endpoints"] == ["n9"]


def test_a_book_reference_to_a_record_the_architecture_no_longer_has_is_not_a_record():
    baseline = {"nodes": [node("n1")], "links": []}
    inventory = mechanism_inventory(baseline, baseline, book_nodes={"gone": [25]}, historical=[])
    assert inventory["items"] == [], "a reference to a record that no longer exists names no mechanism"


def test_the_cap_keeps_seeds_before_expansion_and_counts_what_it_leaves_out():
    baseline = {"nodes": [node(f"n{i}") for i in range(4)], "links": [link(f"l{i}", "n3", "n0") for i in range(6)]}
    proposed = copy.deepcopy(baseline)
    proposed["nodes"][3]["summary"] = "changed"
    inventory = mechanism_inventory(baseline, proposed, book_nodes={}, historical=[], limit=3)
    assert inventory["considered"] == 1 + 6 and inventory["omitted"] == 4
    assert [row["record_id"] for row in inventory["items"]] == ["n3", "l0", "l1"]


# --- Working Book elements: reserved shares, every Book represented, and the presence of what an element cites -------------

def element(identifier, collection, refs, text="t"):
    return {"id": identifier, "collection": collection, "series_refs": refs, "text": text, "attribution": "agent",
            "epistemic_status": "working_proposal"}


def test_each_class_keeps_its_reserved_share_and_open_decisions_are_not_elements():
    rows = [element(f"inh{i}", "inherited", ["n1"]) for i in range(12)]
    rows += [element(f"fwd{i}", "later_possibilities", ["n1"]) for i in range(12)]
    rows += [element(f"oth{i}", "engines", ["n1"]) for i in range(12)]
    rows += [element("dec", "open_author_decisions", ["n1"])]
    rows += [element("uncited", "later_possibilities", ["n9"])]
    selected = book_element_candidates({24: rows}, {"n1"}, {"n1"})
    counts = {}
    for row in selected["items"]:
        counts[row["collection"]] = counts.get(row["collection"], 0) + 1
    # Reserved shares: inherited 8, forward 6, other 4. The question-linked share goes unused here and is given away in
    # class order, inherited first: 4 more inherited, then 2 more forward, to fill the cap.
    assert counts == {"inherited": 12, "later_possibilities": 8, "engines": 4}
    assert all(row["element_id"] != "dec" for row in selected["items"])
    assert selected["considered"] == 36 and selected["omitted"] == 36 - MAX_BOOK_ELEMENTS


def test_the_reserved_shares_fill_the_cap_exactly():
    assert sum(share for _, share, _ in ELEMENT_CLASSES) == MAX_BOOK_ELEMENTS


def test_an_element_that_references_an_examined_question_takes_the_question_linked_share():
    # Inherited evidence is plentiful, so it would fill the cap alone. The reserved question-linked share still holds six
    # slots: the leftover pass is given to inherited evidence first and to question associations last.
    rows = [element(f"inh{i}", "inherited", ["n1"]) for i in range(30)]
    rows += [element(f"q{i}", "engines", [], text=f"association {i}") for i in range(10)]
    for row in rows[30:]:
        row["question_refs"] = ["q-conversion"]
    selected = book_element_candidates({24: rows}, {"n1"}, {"n1"}, question_ids=["q-conversion"])
    linked = [row for row in selected["items"] if row["examined_question_ids"]]
    assert len(linked) == 6
    assert all(row["examined_question_ids"] == ["q-conversion"] for row in linked)
    assert selected["items"][0]["collection"] == "inherited"  # class order: inherited keeps the first reserved share


def test_a_question_association_to_an_unexamined_question_is_not_selected_for_that_reason():
    rows = [element("q1", "engines", [])]
    rows[0]["question_refs"] = ["q-other"]
    assert book_element_candidates({24: rows}, {"n1"}, {"n1"}, question_ids=["q-conversion"])["items"] == []


def test_a_question_linked_element_is_reported_with_its_identities_and_what_it_establishes_nothing_more():
    rows = [element("q1", "series_consequences", ["n1"])]
    rows[0]["question_refs"] = ["q-conversion"]
    (row,) = book_element_candidates({24: rows}, {"n1"}, {"n1"}, question_ids=["q-conversion"])["items"]
    assert row["question_refs"] == ["q-conversion"]
    assert row["examined_question_ids"] == ["q-conversion"]
    assert row["cited_seed_nodes"] == ["n1"]


def test_every_readable_book_with_a_citing_element_is_represented_within_the_cap():
    crowded = [element(f"a{i}", "later_possibilities", ["n1"]) for i in range(30)]
    other = [element("b0", "later_possibilities", ["n1"])]
    selected = book_element_candidates({24: crowded, 25: other}, {"n1"}, {"n1"}, limit=4)
    assert {row["book_number"] for row in selected["items"]} == {24, 25}


def test_an_element_names_each_node_it_cites_and_whether_that_node_is_present():
    rows = [element("e1", "series_consequences", ["n1", "gone"])]
    (row,) = book_element_candidates({25: rows}, {"n1"}, {"n1"})["items"]
    assert row["cited_seed_nodes"] == ["n1"]
    assert row["cites"] == [{"node_id": "n1", "present": True}, {"node_id": "gone", "present": False}]


def test_seed_identifiers_exclude_adjacency_only_nodes():
    baseline = {"nodes": [node("n1"), node("n2")], "links": [link("l1", "n1", "n2")]}
    inventory = mechanism_inventory(baseline, baseline, book_nodes={"n1": [24]}, historical=[])
    assert seed_node_identifiers(inventory) == {"n1"}


# --- The version 2 owner checks on a small packet ------------------------------------------------------------------------

def small_packet():
    return {
        "baseline_question_ids": [Q_CONVERSION],
        "evidence": [
            {"id": "E1", "kind": "instruction"},
            {"id": "E2", "kind": "baseline_wording", "question_id": Q_CONVERSION},
            {"id": "E3", "kind": "proposed_wording", "question_id": Q_CONVERSION},
            {"id": "E4", "kind": "mechanism", "record_kind": "link", "record_id": "l1", "provenance": "transformed",
             "endpoints": ["n1", "n2"]},
            {"id": "E5", "kind": "mechanism", "record_kind": "node", "record_id": "n9", "provenance": "removed"},
            {"id": "E6", "kind": "mechanism", "record_kind": "node", "record_id": "n3", "provenance": "introduced"},
            {"id": "E7", "kind": "mechanism", "record_kind": "node", "record_id": "n1", "provenance": "preserved"},
            {"id": "E8", "kind": "book_element", "book_number": 24, "element_id": "x", "collection": "inherited",
             "cites": [{"node_id": "n1", "present": True}]},
            {"id": "E10", "kind": "book_element", "book_number": 24, "element_id": "y", "collection": "inherited",
             "cites": [{"node_id": "n9", "present": True}]},
            {"id": "E9", "kind": "working_book", "book_number": 25, "text": "Book 25: Title"},
        ],
    }


def answer(**overrides):
    # A reach is stated by every answer, and an answer that records an inheritance is conditional on it unless it says otherwise.
    reach = "conditional_inheritance" if overrides.get("inheritance") else "local"
    base = {"schema_version": 2, "reading": "r", "reach": reach, "no_concern_reason": "none", "concerns": [],
            "mechanisms": [], "inheritance": [], "trajectories": [], "alternatives": [], "not_established": []}
    base.update(overrides)
    return ConsequenceAnswerV2.model_validate(base)


def test_a_transformed_record_needs_its_transformation_and_a_stated_one_is_accepted():
    refused = answer(mechanisms=[{"evidence": "E4", "reading": "It carries draw."}])
    with pytest.raises(ValueError, match="transformation must be stated"):
        _check_answer_v2(refused, small_packet())
    accepted = answer(mechanisms=[{"evidence": "E4", "reading": "It carries draw.", "transformation": "It now names labour."}])
    _check_answer_v2(accepted, small_packet())


def test_a_removed_mechanism_supports_a_possible_displacement_and_an_introduced_one_a_new_concern():
    packet = small_packet()
    _check_answer_v2(answer(concerns=[
        {"title": "A removed record", "status": "possibly_displaced", "reading": "It may be displaced.",
         "evidence": ["E5"], "intent": "not_established"},
        {"title": "A new record", "status": "introduced", "reading": "It is new.", "evidence": ["E6"]},
    ], no_concern_reason=None), packet)


def test_a_book_title_never_supports_a_recorded_or_plausible_inheritance_and_a_recorded_one_needs_an_inherited_element():
    packet = small_packet()
    with pytest.raises(ValueError, match="not a Book title"):
        _check_answer_v2(answer(inheritance=[{"kind": "plausible_inheritance", "from": "E4", "to": "E9", "text": "t",
                                               "evidence": []}]), packet)
    with pytest.raises(ValueError, match="must cite a Book's own inherited element"):
        _check_answer_v2(answer(inheritance=[{"kind": "recorded_inheritance", "from": "E4", "to": "E9", "text": "t",
                                               "evidence": []}]), packet)
    _check_answer_v2(answer(inheritance=[{"kind": "recorded_inheritance", "from": "E4", "to": "E8", "text": "t",
                                           "evidence": ["E8"]}]), packet)


def test_a_recorded_inheritance_needs_a_book_element_that_cites_a_node_the_mechanism_involves():
    packet = small_packet()
    _check_answer_v2(answer(inheritance=[{"kind": "recorded_inheritance", "from": "E4", "to": "E8", "text": "t",
                                           "evidence": ["E8"]}]), packet)
    with pytest.raises(ValueError, match="cites a node the mechanism involves"):
        _check_answer_v2(answer(inheritance=[{"kind": "recorded_inheritance", "from": "E4", "to": "E10", "text": "t",
                                               "evidence": ["E10"]}]), packet)
    with pytest.raises(ValueError, match="must come from a recorded mechanism"):
        _check_answer_v2(answer(inheritance=[{"kind": "recorded_inheritance", "from": "E2", "to": "E8", "text": "t",
                                               "evidence": ["E8"]}]), packet)


def test_a_proposed_inheritance_may_name_a_title_because_it_is_stored_as_proposed():
    _check_answer_v2(answer(inheritance=[{"kind": "proposed_inheritance", "from": "E4", "to": "E9", "text": "t",
                                           "evidence": []}]), small_packet())


def test_the_approach_names_are_the_owners_table_and_the_retired_name_is_refused():
    assert set(APPROACH_MEANINGS) == {"keep_baseline", "accept_proposal", "replace", "integrate", "separate", "defer",
                                      "reframe"}
    with pytest.raises(ValueError):
        answer(alternatives=[{"approach": "retain", "title": "t", "summary": "s", "questions": [Q_CONVERSION],
                              "keeps": ["E2"], "gains": "g", "costs": "c", "next_investigation": "n"}])


def test_a_local_reach_refuses_a_long_horizon_step():
    step = {"stage": "long_horizon", "text": "A later Book could test it.", "evidence": [], "basis": "speculative"}
    with pytest.raises(ValueError, match="a local change has no long-horizon"):
        _check_answer_v2(answer(reach="local", trajectories=[{"title": "T", "steps": [step, step]}]), small_packet())


# --- The Spring Ledger study: the packet, the owner's refusals and the carry-through ---------------------------------------

MOTIVATING_LINKS = ("l_conversion_sets_draw", "l_trade_draws_without_return", "l_compact_hands_in_kind")


def test_the_packet_cites_the_unchanged_mechanisms_the_motivating_case_turns_on(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    packet = packet_of(prepare_architecture_consequence(store, contract_version=2))
    # Version 3 reserves a question-linked share of the Book elements; version 2 analyses keep their own meaning.
    assert packet["packet_version"] == 3
    cited = {item["record_id"]: item for item in packet["evidence"] if item["kind"] == "mechanism"}
    for identifier in MOTIVATING_LINKS:
        assert identifier in cited, identifier
        assert cited[identifier]["provenance"] == "preserved", "the proposal changes no component"
    assert cited["l_compact_hands_in_kind"]["routes"] == ["adjacent_to:inst_mill_compact,th_maintenance"]
    assert {item["provenance"] for item in cited.values()} <= {"preserved", "historical"}
    assert packet["limits"]["mechanisms_omitted"] == 0
    assert packet["limits"]["mechanism_cap"] == MAX_MECHANISMS


def test_a_book_element_of_each_readable_book_is_cited_by_its_identity_and_collection(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    packet = packet_of(prepare_architecture_consequence(store, contract_version=2))
    elements = [item for item in packet["evidence"] if item["kind"] == "book_element"]
    assert {item["book_number"] for item in elements} >= {BOOK, 25}
    assert any(item["collection"] == "inherited" and item["element_id"] == "inh-uneven-draw" for item in elements)
    assert all(item["attribution"] and item["epistemic_status"] for item in elements)


def test_a_transformed_link_is_refused_without_its_transformation_and_accepted_with_it(project):
    store = store_for(project)

    def change_purchase(candidate):
        reword_conversion(candidate)
        for row in candidate["links"]:
            if row["id"] == "l_trade_draws_without_return":
                row["function"] = "purchased shares draw labour in kind under the rebuild"

    propose(store, INSTRUCTION, change_purchase)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    packet = packet_of(prepared)
    purchased = next(item for item in packet["evidence"] if item["kind"] == "mechanism"
                     and item["record_id"] == "l_trade_draws_without_return")
    assert purchased["provenance"] == "transformed"
    assert purchased["changed_fields"] == ["function"]
    base = valid_answer(packet)
    base["mechanisms"][1]["evidence"] = purchased["id"]
    with pytest.raises(ValueError, match="transformation must be stated"):
        complete_architecture_consequence(store, replay(prepared["request"], base))
    base["mechanisms"][1]["transformation"] = "The link now names labour in kind, not draw without return."
    projection = complete_architecture_consequence(store, replay(prepared["request"], base))
    stored = projection["result"]["mechanisms"][1]
    assert stored["record"]["provenance"] == "transformed" and stored["record"]["changed_fields"] == ["function"]


def test_a_completed_analysis_stores_provenance_and_hypothetical_trajectories_read_from_the_evidence(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    projection = complete_architecture_consequence(store, replay(prepared["request"], valid_answer(packet_of(prepared))))
    result = projection["result"]
    assert result["schema"] == "studio-revision-consequence/2"
    assert result["reach"] == "conditional_inheritance" and result["reach_meaning"]
    assert result["trajectories"][0]["status"] == "hypothetical"
    assert result["inheritance"][0]["to_view"]["label"].startswith("Book 24 · inh-uneven-draw")
    assert result["inheritance"][0]["from_view"]["kind"] == "mechanism"
    assert result["alternatives"][0]["approach_meaning"] == APPROACH_MEANINGS["separate"]
    assert result["alternatives"][0]["keeps_views"][0]["kind"] == "baseline_wording"
    assert projection["vocabulary"]["approaches"] == APPROACH_MEANINGS
    assert "retain" not in projection["vocabulary"]["approaches"]


def test_an_alternative_carries_its_kept_wording_and_mechanisms_into_an_investigation_without_widening_it(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    projection = complete_architecture_consequence(store, replay(prepared["request"], valid_answer(packet_of(prepared))))
    alternative = projection["result"]["alternatives"][0]
    origin = consequence_origin(store, {"request_sha256": projection["request_sha256"],
                                        "alternative_id": alternative["id"]},
                                list(alternative["questions"]))
    assert origin["mechanisms"] and origin["mechanisms"][0]["record_id"] == "l_conversion_sets_draw"
    assert origin["mechanisms"][0]["provenance"] == "preserved"
    assert origin["keeps"][0]["evidence_kind"] == "baseline_wording"
    assert origin["keeps"][0]["question_id"] == Q_CONVERSION


def test_the_version_two_instruction_names_the_provenance_meanings_the_owner_uses(project):
    from auteur.beginner.studio_architecture_mechanisms import PROVENANCE_MEANING
    for name, meaning in PROVENANCE_MEANING.items():
        assert name in _SYSTEM_V2
        assert meaning in _SYSTEM_V2
    flat = " ".join(_SYSTEM_V2.split())
    assert "A mechanism that keeps its identifier is not thereby unchanged in function" in flat
    assert "A book_element is a Working Book element" in flat
