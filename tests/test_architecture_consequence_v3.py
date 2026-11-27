"""Mechanism-centred consequence analysis (version 3): alternatives on mechanisms alone, and relations checked against the graph.

The pure parts are tested on small candidates. The owner's checks, the stored analysis and the investigation hand-off are tested on
the Spring Ledger study, the specimen the consequence analysis is proven on. The motivating case is PR #647's Exercise B: a recorded
relation (``l_compact_hands_in_kind``) changes and no question does, so an alternative that must name a question cannot exist. A
version 3 alternative may name the mechanism alone; it still keeps the record it names, on the side its approach keeps.
"""
import copy
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from auteur.beginner.studio_architecture import (
    SelectedCreativeAlternative, _candidate, _root as _architecture_root, _selected_alternative_context,
)
from auteur.beginner.studio_architecture_consequence import (
    SCHEMA_V3, ConsequenceAnswerV3, _SYSTEM_V3, _check_answer_v3, _root, complete_architecture_consequence, consequence_origin,
    prepare_architecture_consequence, project_architecture_consequence,
)
from auteur.beginner.studio_architecture_inquiry import prepare_architecture_inquiry
from auteur.beginner.studio_architecture_mechanisms import RELATION_MEANINGS, relation_status

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_architecture_consequence import (  # noqa: E402,F401 - the fixtures and helpers of the owner suite
    INSTRUCTION, Q_CONVERSION, evidence_id, packet_of, pristine, project, propose, replay, reword_conversion, store_for,
    valid_answer,
)

COMPACT = "l_compact_hands_in_kind"
TRADE = "l_trade_draws_without_return"
MILL = "inst_mill_compact"
MAINTENANCE = "th_maintenance"
SOURCE = "eng_source"


def compact_under_retained_terms(candidate: dict) -> None:
    """The motivating change: one recorded relation changes, and no question does (PR #647 Exercise B)."""
    for row in candidate["links"]:
        if row["id"] == COMPACT:
            row["function"] = "in every season, purchased draw owes grain-labour to the rebuild"


def mechanism(packet: dict, record_id: str) -> str:
    return next(item["id"] for item in packet["evidence"]
                if item["kind"] == "mechanism" and item["record_id"] == record_id)


# --- Pure: the recorded graph, read from the candidates -------------------------------------------------------------------------

def test_the_relation_between_two_mechanisms_is_read_from_the_graph_not_from_their_names():
    baseline = {"nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}],
                "links": [{"id": "l12", "source": "n1", "target": "n2", "function": "f"}],
                "genre_interactions": []}
    proposed = {"nodes": [], "links": [], "genre_interactions": []}
    joined = relation_status(["n1"], ["n2"], [baseline, proposed])
    assert joined["status"] == "joined_by_link" and joined["record"] == {"kind": "link", "id": "l12"}
    assert joined["side"] == "baseline"
    shared = relation_status(["n2"], ["n2", "n3"], [baseline, proposed])
    assert shared["status"] == "shared_endpoint" and shared["record"] == {"kind": "node", "id": "n2"}
    # A link whose ends are n1 and n2, against the node n2 and a third node: the link touches n2, so the two share it.
    assert relation_status(["n1", "n2"], ["n2", "n3"], [baseline, proposed])["status"] == "shared_endpoint"
    none = relation_status(["n3"], ["n1"], [baseline, proposed])
    assert none["status"] == "no_recorded_relation" and none["record"] is None
    assert set(RELATION_MEANINGS) == {"joined_by_link", "shared_endpoint", "adjacent_by_link", "no_recorded_relation"}


def test_an_adjacency_one_recorded_link_away_is_reported_as_adjacency_and_never_as_a_relation_between_the_two():
    baseline = {"nodes": [{"id": "n1"}, {"id": "n2"}],
                "links": [{"id": "l12", "source": "n1", "target": "n2", "function": "f"}]}
    # ``lX`` joins n1 to x; n2 is one recorded link from n1, so the record reads as adjacency. The link is a mechanism of the pair
    # when it is excluded from its own reading.
    adjacent = relation_status(["n1", "x"], ["n2"], [baseline], exclude=["lX"])
    assert adjacent["status"] == "adjacent_by_link" and adjacent["record"] == {"kind": "link", "id": "l12"}
    assert relation_status(["n1", "x"], ["n2"], [{"nodes": [], "links": []}])["status"] == "no_recorded_relation"


def test_a_relation_recorded_only_in_the_proposal_is_still_recorded_and_says_which_side():
    baseline = {"nodes": [], "links": []}
    proposed = {"nodes": [], "links": [{"id": "l9", "source": "n4", "target": "n5", "function": "f"}]}
    found = relation_status(["n4"], ["n5"], [baseline, proposed])
    assert found["status"] == "joined_by_link" and found["side"] == "proposed"


# --- The version 3 answer: shape, not owner state ---------------------------------------------------------------------------

def base_answer(**overrides) -> dict:
    base = {"schema_version": 3, "reading": "r", "reach": "local", "no_concern_reason": "none", "concerns": [],
            "mechanisms": [], "inheritance": [], "trajectories": [], "alternatives": [], "connections": [],
            "not_established": []}
    base.update(overrides)
    return base


def test_a_mechanism_only_alternative_is_a_valid_answer_and_an_alternative_with_no_anchor_is_not():
    ConsequenceAnswerV3.model_validate(base_answer(alternatives=[{
        "approach": "defer", "title": "Hold the Compact's labour duty", "summary": "Keep the recorded duty until settled.",
        "questions": [], "mechanisms": ["E4"], "keeps": ["E4"], "gains": "g", "costs": "c", "next_investigation": "n"}]))
    with pytest.raises(ValidationError, match="names at least one question or mechanism"):
        ConsequenceAnswerV3.model_validate(base_answer(alternatives=[{
            "approach": "defer", "title": "Nothing", "summary": "No anchor.", "questions": [], "mechanisms": [], "keeps": ["E4"],
            "gains": "g", "costs": "c", "next_investigation": "n"}]))


def test_an_alternative_names_at_most_three_anchors_because_an_investigation_takes_no_more():
    with pytest.raises(ValidationError):
        ConsequenceAnswerV3.model_validate(base_answer(alternatives=[{
            "approach": "integrate", "title": "Too many", "summary": "s", "questions": ["q-a", "q-b"],
            "mechanisms": ["E4", "E5"], "keeps": ["E1", "E2", "E3", "E4"], "gains": "g", "costs": "c", "next_investigation": "n"}]))


@pytest.mark.parametrize("connection, message", [
    ({"standing": "inferred", "text": "t", "between": ["E4", "E5"], "assumptions": ["a"]}, "reasoning"),
    ({"standing": "inferred", "text": "t", "between": ["E4", "E5"], "reasoning": "r"}, "assumption"),
    ({"standing": "hypothetical", "text": "t", "between": ["E4", "E5"], "assumptions": ["a"]}, "worth_developing"),
    ({"standing": "unestablished", "text": "t", "between": ["E4", "E5"]}, "basis"),
    ({"standing": "recorded", "text": "t", "between": ["E4", "E5"], "basis": "graph_miss"}, "basis"),
    ({"standing": "recorded", "text": "t", "between": ["E4", "E4"]}, "distinct"),
])
def test_each_standing_states_exactly_the_basis_it_needs(connection, message):
    with pytest.raises(ValidationError, match=message):
        ConsequenceAnswerV3.model_validate(base_answer(connections=[connection]))


# --- The owner's checks on a small packet ---------------------------------------------------------------------------------------

def small_packet():
    return {
        "baseline_question_ids": [Q_CONVERSION],
        "evidence": [
            {"id": "E1", "kind": "instruction"},
            {"id": "E2", "kind": "baseline_wording", "question_id": Q_CONVERSION},
            {"id": "E3", "kind": "proposed_wording", "question_id": Q_CONVERSION},
            {"id": "E4", "kind": "mechanism", "record_kind": "link", "record_id": "lA", "provenance": "transformed",
             "endpoints": ["n1", "n2"]},
            {"id": "E5", "kind": "mechanism", "record_kind": "node", "record_id": "n2", "provenance": "removed",
             "endpoints": ["n2"]},
            {"id": "E6", "kind": "mechanism", "record_kind": "node", "record_id": "n3", "provenance": "introduced",
             "endpoints": ["n3"]},
            {"id": "E7", "kind": "mechanism", "record_kind": "node", "record_id": "n1", "provenance": "preserved",
             "endpoints": ["n1"]},
            {"id": "E8", "kind": "mechanism", "record_kind": "node", "record_id": "n9", "provenance": "historical",
             "endpoints": ["n9"]},
        ],
    }


def candidates():
    baseline = {"nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n9"}],
                "links": [{"id": "lA", "source": "n1", "target": "n2", "function": "before"}]}
    proposed = {"nodes": [{"id": "n1"}, {"id": "n3"}], "links": [{"id": "lA", "source": "n1", "target": "n2",
                                                                  "function": "after"}]}
    return baseline, proposed


def check(**overrides):
    answer = ConsequenceAnswerV3.model_validate(base_answer(**overrides))
    baseline, proposed = candidates()
    return _check_answer_v3(answer, small_packet(), baseline, proposed)


def alternative(approach, anchors_q=(), anchors_m=(), keeps=()):
    return {"approach": approach, "title": f"{approach} {'-'.join(anchors_m) or 'q'}", "summary": "s",
            "questions": list(anchors_q), "mechanisms": list(anchors_m), "keeps": list(keeps), "gains": "g", "costs": "c",
            "next_investigation": "n"}


def test_an_earlier_side_mechanism_is_kept_for_retention_and_a_removed_one_for_acceptance():
    check(alternatives=[alternative("keep_baseline", anchors_m=["E4"], keeps=["E4"])])
    check(alternatives=[alternative("accept_proposal", anchors_m=["E5"], keeps=["E5"])])
    check(alternatives=[alternative("retire", anchors_m=["E5"], keeps=["E5"])])


def test_an_alternative_refuses_a_mechanism_it_keeps_on_the_wrong_side_or_does_not_keep_at_all():
    with pytest.raises(ValueError, match="must keep the baseline record"):
        check(alternatives=[alternative("keep_baseline", anchors_m=["E6"], keeps=["E6"])])
    with pytest.raises(ValueError, match="keeps no record of"):
        check(alternatives=[alternative("defer", anchors_m=["E4"], keeps=["E7"])])
    with pytest.raises(ValueError, match="keeps an item that is not"):
        check(alternatives=[alternative("defer", anchors_m=["E4"], keeps=["E4", "E7"])])


def test_a_historical_record_is_never_an_anchor_and_a_question_alternative_still_keeps_its_wording():
    with pytest.raises(ValueError, match="is not a current mechanism"):
        check(alternatives=[alternative("defer", anchors_m=["E8"], keeps=["E8"])])
    check(alternatives=[alternative("defer", anchors_q=[Q_CONVERSION], keeps=["E2"])])
    with pytest.raises(ValueError, match="must keep the baseline wording"):
        check(alternatives=[alternative("keep_baseline", anchors_q=[Q_CONVERSION], keeps=["E3"])])


def test_an_alternative_names_only_continuing_baseline_questions():
    with pytest.raises(ValueError, match="which is not a continuing question"):
        check(alternatives=[alternative("reframe", anchors_q=["q-not-open"], keeps=["E2"])])


def connection(standing, between, **extra):
    row = {"standing": standing, "between": list(between), "text": "t", **extra}
    return row


def test_a_recorded_connection_is_checked_against_the_graph_and_its_owner_reading_is_stored():
    baseline, proposed = candidates()
    answer = ConsequenceAnswerV3.model_validate(base_answer(connections=[connection("recorded", ["E4", "E5"])]))
    graph = _check_answer_v3(answer, small_packet(), baseline, proposed)
    # E4 (link n1-n2) and E5 (node n2) share the endpoint n2: the Architecture records the touch.
    assert graph == [{"status": "shared_endpoint", "record": {"kind": "node", "id": "n2"}, "side": "both"}]


def test_a_recorded_connection_the_graph_does_not_show_is_refused_and_a_graph_miss_is_not_offered_where_the_graph_joins():
    baseline, proposed = candidates()
    unjoined = ConsequenceAnswerV3.model_validate(base_answer(connections=[connection("recorded", ["E6", "E7"])]))
    with pytest.raises(ValueError, match="records no relation between"):
        _check_answer_v3(unjoined, small_packet(), baseline, proposed)
    miss = ConsequenceAnswerV3.model_validate(base_answer(connections=[connection("unestablished", ["E4", "E5"],
                                                                                 basis="graph_miss")]))
    with pytest.raises(ValueError, match="records a relation between them"):
        _check_answer_v3(miss, small_packet(), baseline, proposed)
    honest = ConsequenceAnswerV3.model_validate(base_answer(connections=[connection("unestablished", ["E6", "E7"],
                                                                                   basis="graph_miss")]))
    assert _check_answer_v3(honest, small_packet(), baseline, proposed)[0]["status"] == "no_recorded_relation"


def test_an_inferred_or_hypothetical_connection_is_stored_as_the_agents_and_may_differ_from_the_graph():
    baseline, proposed = candidates()
    answer = ConsequenceAnswerV3.model_validate(base_answer(connections=[
        connection("inferred", ["E6", "E7"], reasoning="The introduced node takes over the link's role.",
                   assumptions=["The author keeps n3 as the successor."]),
        connection("hypothetical", ["E4", "E6"], worth_developing="Could make the duty answer to the new node.",
                   assumptions=["The rebuild is staffed."])]))
    graph = _check_answer_v3(answer, small_packet(), baseline, proposed)
    assert [row["status"] for row in graph] == ["no_recorded_relation", "no_recorded_relation"]


def test_a_connection_between_the_same_pair_twice_is_refused():
    baseline, proposed = candidates()
    answer = ConsequenceAnswerV3.model_validate(base_answer(connections=[
        connection("inferred", ["E4", "E5"], reasoning="r", assumptions=["a"]),
        connection("hypothetical", ["E5", "E4"], worth_developing="w", assumptions=["a"])]))
    with pytest.raises(ValueError, match="same pair"):
        _check_answer_v3(answer, small_packet(), baseline, proposed)


def test_the_version_three_instruction_names_the_retire_approach_and_each_standing_the_owner_enforces():
    flat = " ".join(_SYSTEM_V3.split())
    assert "retire" in flat
    for standing in ("recorded", "inferred", "hypothetical", "unestablished"):
        assert f"{standing}" in flat
    for basis in ("graph_miss", "competing_readings", "incomplete_evidence", "productive_independence"):
        assert basis in flat
    assert "A mechanism that keeps its identifier is not thereby unchanged in function" in flat
    assert "at most three anchors" in flat


# --- The stored analysis on the Spring Ledger study ------------------------------------------------------------------------

def mechanism_answer(packet: dict) -> dict:
    compact = mechanism(packet, COMPACT)
    trade = mechanism(packet, TRADE)
    return {
        "schema_version": 3,
        "reading": ("The recorded Mill Compact duty changes from 'under B' to 'in every season'. No question changes, so the "
                    "proposal is a change to one recorded relation alone."),
        "reach": "local",
        "concerns": [{
            "title": "Whether the Compact's labour duty is seasonal", "status": "transformed",
            "earlier": "Purchased draw owes labour under the rebuild only.", "proposed": "Purchased draw owes labour in every season.",
            "reading": "The relation is still in play, but its scope is wider.", "evidence": [compact],
            "intent": "not_established"}],
        "mechanisms": [{"evidence": compact,
                        "reading": "The recorded link says purchased draw owes grain-labour to the rebuild.",
                        "transformation": "The duty no longer waits for the rebuild and applies in every season."}],
        "trajectories": [],
        "alternatives": [{"approach": "defer", "title": "Hold the duty until the rebuild is settled",
                          "summary": "Keep the recorded duty as it is until the author decides what the rebuild requires.",
                          "questions": [], "mechanisms": [compact], "keeps": [compact],
                          "gains": "The record stays as the author wrote it.",
                          "costs": "The seasonal reading is not tried.", "next_investigation": "Examine the Compact's labour duty."}],
        "connections": [{"standing": "recorded", "between": [compact, trade],
                         "text": "Both recorded links leave the Mill Compact, so the relation between the duty and the draw is recorded.",
                         "evidence": [compact, trade]}],
        "not_established": ["Whether the Compact's duty should apply in every season."],
    }


def test_a_mechanism_only_change_is_analysed_under_version_three_and_its_alternative_needs_no_question(project):
    store = store_for(project)
    propose(store, "Make the Mill Compact's labour duty apply in every season.", compact_under_retained_terms)
    prepared = prepare_architecture_consequence(store)
    assert json.loads(prepared["request"]["user"])["consequence_packet"]["proposal"]["revision_request_sha256"]
    assert prepared["request"]["settings"]["consequence_schema_version"] == 3
    packet = packet_of(prepared)
    assert packet["baseline_question_ids"] and not any(
        item["kind"] in ("proposed_wording", "removed") for item in packet["evidence"])
    projection = complete_architecture_consequence(store, replay(prepared["request"], mechanism_answer(packet)))
    result = projection["result"]
    assert result["schema"] == SCHEMA_V3
    (alt,) = result["alternatives"]
    assert alt["questions"] == []
    assert alt["mechanism_views"][0]["label"].startswith("link l_compact_hands_in_kind")
    (connection,) = result["connections"]
    assert connection["graph"]["status"] == "shared_endpoint"
    assert connection["graph"]["record"] == {"kind": "node", "id": MILL}
    assert connection["standing_meaning"] and connection["between_views"][0]["label"].startswith("link l_compact")


def test_a_version_two_answer_is_refused_for_a_version_three_request_and_the_refusal_is_kept(project):
    store = store_for(project)
    propose(store, "Make the Mill Compact's labour duty apply in every season.", compact_under_retained_terms)
    prepared = prepare_architecture_consequence(store)
    version_two = {"schema_version": 2, "reading": "r", "reach": "local", "no_concern_reason": "none", "concerns": [],
                   "mechanisms": [], "inheritance": [], "trajectories": [], "alternatives": [], "not_established": []}
    with pytest.raises(ValueError):
        complete_architecture_consequence(store, replay(prepared["request"], version_two))
    refusals = list(_root(store).rglob("refused/*.json"))
    assert refusals, "the refused answer is retained as evidence"
    assert project_architecture_consequence(store)["result"] is None


def test_a_mechanism_only_alternative_is_investigated_on_its_current_anchors_and_its_origin_is_carried(project):
    store = store_for(project)
    propose(store, "Make the Mill Compact's labour duty apply in every season.", compact_under_retained_terms)
    prepared = prepare_architecture_consequence(store)
    projection = complete_architecture_consequence(store, replay(prepared["request"], mechanism_answer(packet_of(prepared))))
    alt = projection["result"]["alternatives"][0]
    origin_ref = {"request_sha256": projection["request_sha256"], "alternative_id": alt["id"]}
    with pytest.raises(ValueError, match="exactly the questions and mechanisms"):
        consequence_origin(store, origin_ref, [])
    origin = consequence_origin(store, origin_ref, [{"kind": "link", "id": COMPACT}])
    assert origin["questions"] == [] and origin["mechanisms"][0]["record_id"] == COMPACT
    intent = {"version": 1, "canvas_id": store.canvas_id, "operation": "explain", "target": "current",
              "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
              "anchors": [{"kind": "link", "id": COMPACT}], "author_text": alt["next_investigation"],
              "from_consequence": origin_ref}
    inquiry = prepare_architecture_inquiry(store, dict(intent))
    assert inquiry["request"]["settings"]["from_consequence"]["approach"] == "defer"
    assert json.loads(inquiry["request"]["user"])["from_consequence"]["mechanisms"][0]["record_id"] == COMPACT


def introduce_office(candidate: dict) -> None:
    """A proposal that adds a node and a recorded relation to the Mill Compact: both are introduced, neither is in the baseline."""
    candidate["nodes"].append({"id": "inst_rebuild_office", "title": "Rebuild office", "category": "structure",
                               "summary": "A new office that schedules the rebuild.", "scope": "whole_story", "parent_id": None})
    candidate["links"].append({"id": "l_office_schedules_compact", "source": "inst_rebuild_office", "target": MILL,
                               "function": "the office sets when the duty applies"})


def test_an_alternative_on_a_mechanism_the_proposal_introduces_is_accepted_as_proposed_but_not_investigated_on_the_current_architecture(
        project):
    store = store_for(project)
    propose(store, "Add a rebuild office that schedules the Compact's duty.", introduce_office)
    prepared = prepare_architecture_consequence(store)
    packet = packet_of(prepared)
    office = mechanism(packet, "inst_rebuild_office")
    assert next(item for item in packet["evidence"] if item["id"] == office)["provenance"] == "introduced"
    payload = {"schema_version": 3, "reading": "The proposal adds an office that schedules the duty.", "reach": "local",
               "concerns": [{"title": "Who schedules the duty", "status": "introduced",
                             "reading": "A new office now sets when the duty applies.", "evidence": [office]}],
               "mechanisms": [{"evidence": office, "reading": "A new office in the Architecture.",
                               "transformation": "It schedules the Compact's duty, which it did not do before."}],
               "trajectories": [], "alternatives": [{
                   "approach": "accept_proposal", "title": "Accept the office as written",
                   "summary": "Accept the office and its scheduling of the duty.", "questions": [],
                   "mechanisms": [office], "keeps": [office], "gains": "The schedule has an owner.",
                   "costs": "One more institution to keep consistent.", "next_investigation": "Read the office's schedule."}],
               "connections": [], "not_established": ["Whether the office is meant to schedule the duty."]}
    projection = complete_architecture_consequence(store, replay(prepared["request"], payload))
    alt = projection["result"]["alternatives"][0]
    assert alt["approach"] == "accept_proposal" and alt["questions"] == []
    with pytest.raises(ValueError, match="introduced by this proposal"):
        consequence_origin(store, {"request_sha256": projection["request_sha256"], "alternative_id": alt["id"]},
                           [{"kind": "node", "id": "inst_rebuild_office"}])


def valid_answer_v3(packet: dict) -> dict:
    """The Spring Ledger reading of version 2, restated under version 3. Its alternative names its question and the mechanism it
    concerns, so it keeps both: the wording of the question and the recorded conversion."""
    payload = valid_answer(packet)
    payload["schema_version"] = 3
    conversion = evidence_id(packet, "mechanism", record_kind="link", record_id="l_conversion_sets_draw")
    (alternative,) = payload["alternatives"]
    alternative["mechanisms"] = [conversion]
    alternative["keeps"] = [evidence_id(packet, "baseline_wording", question_id=Q_CONVERSION), conversion]
    return payload


def test_an_alternative_names_the_anchors_an_investigation_takes_from_the_owner_not_from_the_page(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store)
    projection = complete_architecture_consequence(store, replay(prepared["request"], valid_answer_v3(packet_of(prepared))))
    (alternative,) = projection["result"]["alternatives"]
    assert alternative["investigation_anchors"] == [
        {"kind": "question", "id": Q_CONVERSION}, {"kind": "link", "id": "l_conversion_sets_draw"}]
    baseline_text = next(item["text"] for item in packet_of(prepared)["evidence"]
                         if item["kind"] == "baseline_wording" and item["question_id"] == Q_CONVERSION)
    assert alternative["question_views"] == [{"id": Q_CONVERSION, "label": baseline_text}]
    assert projection["vocabulary"]["approaches_v3"]["retire"]


def test_a_revision_made_from_a_mechanism_investigation_states_the_mechanisms_it_concerned_and_no_question_it_did_not(project):
    store = store_for(project)
    inquiry_sha = "c" * 64
    folder = _architecture_root(store) / "inquiries" / "requests" / inquiry_sha
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result.json").write_text(json.dumps({
        "baseline_candidate_request_sha256": _candidate(store)["request_sha256"],
        "intent": {"operation": "explain", "author_text": "Read the Compact's labour duty.",
                   "anchors": [{"kind": "link", "id": COMPACT, "sourceRef": "links/3"}]},
        "hypotheses": [{"id": "h1", "title": "Seasonal duty", "description": "The duty applies in every season."}],
    }), encoding="utf-8")
    context = _selected_alternative_context(
        store, _candidate(store), SelectedCreativeAlternative(inquiry_request_sha256=inquiry_sha, hypothesis_id="h1"))
    assert context["considered_mechanisms"] == [{"kind": "link", "id": COMPACT}]
    assert "considered_questions" not in context


def test_the_version_three_instruction_lists_the_exact_key_names_and_cites_mechanisms_by_evidence_identifier():
    # Generated from the owner's models: a key the contract does not have is named nowhere, and a required one is named everywhere.
    assert "- mechanisms[]: evidence, reading, transformation, conditional_consequence, counterevidence, unresolved" in _SYSTEM_V3
    assert "- inheritance[]: kind, from, to, text, evidence" in _SYSTEM_V3
    assert "- concerns[]: title, status, earlier, proposed, reading, evidence, intent, counterevidence, competing_reading" in _SYSTEM_V3
    assert "- connections[]: between, standing, text, reasoning, worth_developing, basis, assumptions, counterevidence, evidence" \
        in _SYSTEM_V3
    flat = " ".join(_SYSTEM_V3.split())
    assert "A mechanism is cited by its EVIDENCE identifier" in flat
    assert "A record identifier such as l_compact_hands_in_kind is the record's own name" in flat
