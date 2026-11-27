"""Consequence analysis of a pending working revision: the owner contract, on the Spring Ledger study.

The analysis is explicit, bounded and advisory. It examines one exact pending revision: its evidence names every fact the
agent may cite, an answer may cite only those facts, and every stated basis must be the one the evidence shows. It changes no
narrative record, never gates Apply, is stale once the proposal it examined is no longer pending on the same baseline, and an
alternative it proposes is investigated only on its own continuing questions.
"""
import copy
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import (
    SelectedCreativeAlternative, _candidate, _root, _selected_alternative_context, apply_architecture_review,
    complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_architecture_consequence import (
    ConsequenceAnswer, _SYSTEM_V2 as _SYSTEM, complete_architecture_consequence, consequence_origin,
    prepare_architecture_consequence, project_architecture_consequence,
)
from auteur.beginner.studio_architecture_inquiry import prepare_architecture_inquiry
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
import seed_series_context_study as base  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

Q_CONVERSION = identity_for(5)
Q_COMPACT = identity_for(6)
Q_FINALE = identity_for(2)
BOOK = 24
CONVERSION_INDEX = 5
NARROWED = ("Does the Book 20 hands-to-draw conversion reach the shares the Mill Compact purchased, or do those shares "
            "stay outside it? Not decided.")
INSTRUCTION = "Ask whether the Book 20 conversion reaches the shares the Mill Compact purchased."


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("consequence") / "discovery"
    store = discovery.seed_discovery(root)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, root, BOOK)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "discovery"
    shutil.copytree(pristine, target)
    return target


def store_for(project: Path) -> CanvasStore:
    return CanvasStore(project, discovery.SPRING)


def snapshot(project: Path) -> dict[str, bytes]:
    """Every file that is narrative state: the canvas, the applied Architecture and the Working Books. The analysis's own
    folder and its pointer are excluded, because writing them is the only thing an analysis does."""
    files = {}
    for path in sorted(project.rglob("*")):
        if not path.is_file() or path.name.endswith(".lock"):
            continue
        relative = path.relative_to(project)
        if "consequences" in relative.parts:
            continue
        files[str(relative)] = path.read_bytes()
    return files


def propose(store, instruction: str, edit) -> str:
    """A pending working revision: prepared and completed, never applied. Returns its request sha."""
    revised = copy.deepcopy(_candidate(store)["candidate"])
    edit(revised)
    waiting = prepare_architecture(store, instruction=instruction)
    sha = waiting["request"]["request_sha256"]
    complete_architecture(store, base._reply(waiting["request"], revised, "consequence-test"))
    return sha


def reword_conversion(candidate: dict) -> None:
    candidate["open_questions"][CONVERSION_INDEX] = NARROWED


def remove_compact(candidate: dict) -> None:
    index = candidate["open_question_ids"].index(Q_COMPACT)
    del candidate["open_questions"][index]
    del candidate["open_question_ids"][index]


def remove_conversion(candidate: dict) -> None:
    index = candidate["open_question_ids"].index(Q_CONVERSION)
    del candidate["open_questions"][index]
    del candidate["open_question_ids"][index]


def replay(request: dict, payload: dict) -> dict:
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(payload), runtime="consequence-test").model_dump()


def packet_of(projection: dict) -> dict:
    return json.loads(projection["request"]["user"])["consequence_packet"]


def evidence_id(packet: dict, kind: str, **match) -> str:
    return next(item["id"] for item in packet["evidence"]
                if item["kind"] == kind and all(item.get(key) == value for key, value in match.items()))


def valid_answer(packet: dict) -> dict:
    """A version 2 answer that cites only what the packet gives, and states every basis the evidence shows."""
    instruction = evidence_id(packet, "instruction")
    baseline = evidence_id(packet, "baseline_wording", question_id=Q_CONVERSION)
    proposed = evidence_id(packet, "proposed_wording", question_id=Q_CONVERSION)
    decision = evidence_id(packet, "book_decision", question_id=Q_CONVERSION)
    conversion = evidence_id(packet, "mechanism", record_kind="link", record_id="l_conversion_sets_draw")
    purchased = evidence_id(packet, "mechanism", record_kind="link", record_id="l_trade_draws_without_return")
    inherited = evidence_id(packet, "book_element", element_id="inh-uneven-draw", book_number=BOOK)
    later = evidence_id(packet, "book_element", element_id="cons-conversion-blind-spot", book_number=BOOK)
    return {
        "schema_version": 2,
        "reading": ("The instruction narrows the Book 20 conversion question to the shares the Mill Compact purchased. The "
                    "proposed wording keeps its identity and drops the earlier question about settlement durability."),
        "reach": "conditional_inheritance",
        "concerns": [
            {"title": "Whether the conversion is a lasting settlement", "status": "possibly_displaced",
             "earlier": "A lasting settlement, or a stage the finale must revisit.",
             "proposed": "Reach to the purchased shares; the settlement question is not asked.",
             "reading": "The narrowed wording no longer asks the durability question the finale would have to answer.",
             "evidence": [baseline, proposed, instruction], "intent": "instruction_names_it",
             "counterevidence": ["The author may keep the durability question in another question."]},
            {"title": "Whether the purchased shares stay outside the conversion", "status": "introduced",
             "reading": "The narrowed wording opens the purchased-share question as its own uncertainty.",
             "evidence": [proposed]},
        ],
        "mechanisms": [
            {"evidence": conversion,
             "reading": "The recorded link sets draw from hands a household cannot return (Book 20).",
             "conditional_consequence": "If the conversion reaches the purchased shares, their draw would follow hands owed.",
             "counterevidence": [{"text": "The record does not say the conversion applies to purchased shares.",
                                  "evidence": [proposed]}],
             "unresolved": ["Whether the author means the conversion to reach purchased shares."]},
            {"evidence": purchased,
             "reading": "The recorded link says purchased shares draw without return labour."},
        ],
        "inheritance": [
            {"kind": "recorded_inheritance", "from": conversion, "to": inherited,
             "text": "Book 24 records that hand-light draw has fallen since the conversion.", "evidence": [inherited]},
            {"kind": "plausible_inheritance", "from": baseline, "to": later,
             "text": "Book 24 names later pressure on the conversion for Books 25 and 26; whether they carry the durability "
                     "question is not recorded.", "evidence": [later]},
        ],
        "trajectories": [
            {"title": "The purchased shares carry the conversion question",
             "steps": [
                 {"stage": "local_decision", "text": "The proposal narrows the question to purchased shares.",
                  "evidence": [proposed], "basis": "interpreted"},
                 {"stage": "mechanism_transformation",
                  "text": "If adopted, draw for purchased shares is set by hands owed rather than by the Compact's labour.",
                  "evidence": [purchased], "basis": "interpreted"},
                 {"stage": "inheritance", "text": "Books 25 and 26 could test the conversion against purchased shares.",
                  "evidence": [later], "basis": "speculative"},
             ],
             "assumptions": ["The author keeps the conversion as recorded."]},
        ],
        "alternatives": [
            {"approach": "separate", "title": "Keep the settlement question beside the purchased-share question",
             "summary": "Keep the earlier durability question and ask the purchased-share question beside it.",
             "questions": [Q_CONVERSION], "keeps": [baseline], "mechanisms": [conversion],
             "gains": "Both concerns stay visible.", "costs": "Two questions to hold open.",
             "next_investigation": "Compare the two readings of the conversion."},
        ],
        "not_established": ["Whether the author intends the durability question to be dropped."],
    }


def completed(store, project: Path, instruction: str = INSTRUCTION, edit=reword_conversion) -> tuple[str, dict]:
    sha = propose(store, instruction, edit)
    projection = prepare_architecture_consequence(store, contract_version=2)
    complete_architecture_consequence(store, replay(projection["request"], valid_answer(packet_of(projection))))
    return sha, project_architecture_consequence(store)


def test_the_packet_names_the_reworded_question_and_its_book_decision_without_applying(project):
    store = store_for(project)
    sha = propose(store, INSTRUCTION, reword_conversion)
    before = snapshot(project)
    projection = prepare_architecture_consequence(store, contract_version=2)
    assert projection["status"] == "awaiting_host_agent"
    assert projection["standing"] == "current"
    assert projection["revision_request_sha256"] == sha
    packet = packet_of(projection)
    row = next(item for item in packet["examined_questions"] if item["id"] == Q_CONVERSION)
    assert row["proposal_status"] == "reworded"
    evidence = {item["id"]: item for item in packet["evidence"]}
    kinds = {evidence[identifier]["kind"] for identifier in row["baseline_evidence"] + row["proposed_evidence"]}
    assert {"baseline_wording", "proposed_wording", "book_decision"} <= kinds
    decision = next(evidence[identifier] for identifier in row["baseline_evidence"]
                    if evidence[identifier]["kind"] == "book_decision")
    assert decision["book_number"] == BOOK and decision["proposal_status"] == "reworded"
    assert decision["standing"] == "current"
    assert BOOK in packet["coverage"]["books_with_decisions_on_examined_questions"]
    assert snapshot(project) == before, "preparing an analysis changed narrative state"


def test_a_removed_question_is_examined_before_the_positions_its_removal_shifts(project):
    """A removal moves every later question one place. Those position-only shifts are not changes of wording, and they must not
    crowd the removed question out of the examined set (the second exercise did exactly that)."""
    store = store_for(project)

    def retire_conversion(candidate: dict) -> None:
        index = candidate["open_question_ids"].index(Q_CONVERSION)
        del candidate["open_questions"][index]
        del candidate["open_question_ids"][index]

    propose(store, "Retire the conversion question.", retire_conversion)
    packet = packet_of(prepare_architecture_consequence(store, contract_version=2))
    rows = {row["id"]: row for row in packet["examined_questions"]}
    assert Q_CONVERSION in rows, "the retired question must be examined"
    assert rows[Q_CONVERSION]["proposal_status"] == "removed"
    evidence = {item["id"]: item for item in packet["evidence"]}
    decisions = [evidence[i] for i in rows[Q_CONVERSION]["baseline_evidence"] if evidence[i]["kind"] == "book_decision"]
    assert decisions and decisions[0]["book_number"] == BOOK and decisions[0]["proposal_status"] == "removed"
    assert any(evidence[i]["kind"] == "baseline_wording" for i in rows[Q_CONVERSION]["baseline_evidence"])


def test_every_fact_the_request_cites_has_a_stable_identifier_in_order(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    packet = packet_of(prepare_architecture_consequence(store, contract_version=2))
    identifiers = [item["id"] for item in packet["evidence"]]
    assert identifiers == [f"E{index}" for index in range(1, len(identifiers) + 1)]
    assert packet["evidence_sha256"] and packet["proposal"]["proposal_sha256"]
    for row in packet["examined_questions"]:
        for identifier in row["baseline_evidence"] + row["proposed_evidence"]:
            assert identifier in identifiers


def test_a_valid_answer_is_stored_as_current_for_its_proposal_and_changes_no_record(project):
    store = store_for(project)
    sha = propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    before = snapshot(project)
    projection = complete_architecture_consequence(store, replay(prepared["request"], valid_answer(packet_of(prepared))))
    assert projection["status"] == "ready"
    assert projection["standing"] == "current"
    result = projection["result"]
    assert result["revision_request_sha256"] == sha
    assert result["authority"].startswith("noncanonical")
    assert [row["id"] for row in result["alternatives"]] == ["a1"]
    assert snapshot(project) == before


def test_apply_is_never_gated_and_the_analysis_then_describes_an_applied_change(project):
    store = store_for(project)
    sha, projection = completed(store, project)
    assert projection["standing"] == "current"
    apply_architecture_review(store, sha)
    applied = project_architecture_consequence(store)
    assert applied["standing"] == "applied"
    assert applied["result"] is not None, "a completed analysis stays readable after its revision is applied"


def test_a_later_revision_supersedes_the_analysis_and_its_result_is_not_presented_as_current(project):
    store = store_for(project)
    completed(store, project)
    propose(store, "Say what the Gate Table is for.",
            lambda c: c["open_questions"].__setitem__(7, c["open_questions"][7] + " Revised."))
    projection = project_architecture_consequence(store)
    assert projection["status"] == "ready"
    assert projection["standing"] == "superseded"
    assert projection["result"] is not None, "the earlier analysis stays readable, labelled as earlier"


def test_a_response_for_a_proposal_that_is_no_longer_pending_is_retained_as_stale_and_refused(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    propose(store, "Say how reading is taught.", lambda c: c["nodes"][0].__setitem__("summary", c["nodes"][0]["summary"] + " Revised."))
    folder = _root(store) / "consequences" / "requests" / prepared["request_sha256"]
    with pytest.raises(Exception, match="changed since this analysis was prepared"):
        complete_architecture_consequence(store, replay(prepared["request"], valid_answer(packet_of(prepared))))
    assert (folder / "stale_response.json").is_file()
    assert not (folder / "result.json").exists()


def test_a_refused_answer_is_preserved_and_a_corrected_one_completes(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    bad = valid_answer(packet_of(prepared))
    bad["concerns"][0]["evidence"] = ["E999"]
    with pytest.raises(ValueError, match="E999"):
        complete_architecture_consequence(store, replay(prepared["request"], bad))
    refused = list((_root(store) / "consequences" / "requests" / prepared["request_sha256"] / "refused").glob("*.json"))
    assert len(refused) == 1
    projection = complete_architecture_consequence(store, replay(prepared["request"], valid_answer(packet_of(prepared))))
    assert projection["status"] == "ready"


def _mutated(mutate):
    def build(packet):
        answer = valid_answer(packet)
        mutate(answer, packet)
        return answer
    return build


REFUSALS = {
    # label: (answer mutation, the message the owner must give, so a refusal is refused for the stated reason)
    "an unknown evidence identifier": (_mutated(lambda a, p: a["concerns"][0].__setitem__("evidence", ["E999"])), "E999"),
    "an instruction basis without the instruction": (_mutated(
        lambda a, p: a["concerns"][0].__setitem__("evidence", [evidence_id(p, "baseline_wording", question_id=Q_CONVERSION)])),
        "names it but cites no instruction"),
    "a displacement with no earlier formulation": (_mutated(
        lambda a, p: a["concerns"][0].update(intent="not_established",
                                             evidence=[evidence_id(p, "proposed_wording", question_id=Q_CONVERSION)])),
        "may be displaced but cites no earlier"),
    "an introduced concern with no proposed wording": (_mutated(
        lambda a, p: a["concerns"][1].__setitem__("evidence", [evidence_id(p, "baseline_wording", question_id=Q_CONVERSION)])),
        "introduced but cites no proposed"),
    "a transformed concern citing only one side": (_mutated(
        lambda a, p: a["concerns"].__setitem__(0, {**a["concerns"][0], "status": "transformed", "intent": "not_established",
                                                   "evidence": [evidence_id(p, "baseline_wording", question_id=Q_CONVERSION)]})),
        "must cite both"),
    "a recorded inheritance that does not cite a Book's own inherited element": (_mutated(
        lambda a, p: a["inheritance"][0].__setitem__("to", evidence_id(p, "book_decision", question_id=Q_CONVERSION))),
        "must cite a Book's own inherited element"),
    "a plausible inheritance that cites only a Working Book title": (_mutated(
        lambda a, p: a["inheritance"][1].__setitem__("to", evidence_id(p, "working_book", book_number=25))),
        "not a Book title"),
    "an inheritance whose source is not an earlier development": (_mutated(
        lambda a, p: a["inheritance"][1].__setitem__("from", evidence_id(p, "proposed_wording", question_id=Q_CONVERSION))),
        "must name an earlier development"),
    "a mechanism read twice": (_mutated(
        lambda a, p: a["mechanisms"].append(dict(a["mechanisms"][0]))), "is read twice"),
    "a mechanism reading that cites a non-mechanism": (_mutated(
        lambda a, p: a["mechanisms"][0].__setitem__("evidence", evidence_id(p, "baseline_wording", question_id=Q_CONVERSION))),
        "is not a recorded mechanism"),
    "a counterevidence item with no evidence": (_mutated(
        lambda a, p: a["mechanisms"][0]["counterevidence"][0].__setitem__("evidence", [])), "at least 1"),
    "a local reach with a long-horizon trajectory step": (_mutated(
        lambda a, p: (a.__setitem__("reach", "local"),
                      a["trajectories"][0]["steps"][2].__setitem__("stage", "long_horizon"))),
        "a local change has no long-horizon"),
    "a long-horizon reach with no long-horizon or inheritance step": (_mutated(
        lambda a, p: (a.__setitem__("reach", "long_horizon"), a.__setitem__("trajectories", []),
                      a.__setitem__("inheritance", []))), "needs a long-horizon or inheritance step"),
    "a recorded trajectory step that cites nothing": (_mutated(
        lambda a, p: a["trajectories"][0]["steps"][0].update(basis="recorded", evidence=[])), "must cite evidence"),
    "an alternative over a question the baseline does not hold": (_mutated(
        lambda a, p: a["alternatives"][0].__setitem__("questions", [Q_CONVERSION, "q-not-a-question"])),
        "not a continuing question of the baseline"),
    "a recorded step that cites only the proposal": (_mutated(
        lambda a, p: a["trajectories"][0]["steps"][0].update(basis="recorded", evidence=[evidence_id(p, "proposed_wording", question_id=Q_CONVERSION)])),
        "not the proposal"),
    "a recorded inheritance whose Book element cites no node the mechanism involves": (_mutated(
        lambda a, p: a["inheritance"][0].__setitem__("to", evidence_id(p, "book_element", element_id="inh-date", book_number=BOOK))),
        "cites a node the mechanism involves"),
    "counterevidence that is only the mechanism itself": (_mutated(
        lambda a, p: a["mechanisms"][0]["counterevidence"][0].__setitem__("evidence", [evidence_id(p, "mechanism", record_kind="link", record_id="l_conversion_sets_draw")])),
        "other than the mechanism itself"),
    "a local reach that records a later development": (_mutated(
        lambda a, p: a.__setitem__("reach", "local")), "records no later development"),
    "a not established reach that rests on a recorded inheritance": (_mutated(
        lambda a, p: a.__setitem__("reach", "not_established")), "cannot rest on a recorded inheritance"),
    "a conditional reach with only an unknown inheritance": (_mutated(
        lambda a, p: (a.__setitem__("inheritance", [{"kind": "unknown_inheritance", "from": evidence_id(p, "baseline_wording", question_id=Q_CONVERSION),
                                                    "to": evidence_id(p, "book_decision", question_id=Q_CONVERSION), "text": "t", "evidence": []}]))),
        "needs an inheritance other than unknown"),
    "an alternative whose keeps omit one of its named questions": (_mutated(
        lambda a, p: a["alternatives"][0].__setitem__("questions", [Q_CONVERSION, "q-other-1"])), "keeps no wording of q-other-1"),
    "an accepted proposal that keeps baseline wording as well": (_mutated(
        lambda a, p: a["alternatives"][0].update(approach="accept_proposal", keeps=[
            evidence_id(p, "proposed_wording", question_id=Q_CONVERSION), evidence_id(p, "baseline_wording", question_id=Q_CONVERSION)])),
        "keeps only proposal-side wording"),
    "an alternative that keeps the wording of another question": (_mutated(
        lambda a, p: (a["alternatives"][0].__setitem__("questions", [Q_CONVERSION]),
                      a["alternatives"][0].__setitem__("keeps", [evidence_id(p, "instruction")]))),
        "is not wording of its own questions"),
    "a keep_baseline alternative that keeps only the proposal": (_mutated(
        lambda a, p: a["alternatives"][0].update(approach="keep_baseline",
                                                 keeps=[evidence_id(p, "proposed_wording", question_id=Q_CONVERSION)])),
        "must keep the baseline wording"),
    "an accept_proposal alternative that keeps no proposal-side item": (_mutated(
        lambda a, p: a["alternatives"][0].update(approach="accept_proposal")), "keeps no proposal-side item"),
    "two concerns with one title": (_mutated(
        lambda a, p: a["concerns"][1].__setitem__("title", a["concerns"][0]["title"])), "share the title"),
    "intent stated for a preserved concern": (_mutated(
        lambda a, p: a["concerns"][1].__setitem__("intent", "not_established")), "intent applies only"),
    "an empty concern list without a reason": (_mutated(
        lambda a, p: (a.__setitem__("concerns", []), a.__setitem__("no_concern_reason", None))), "no_concern_reason"),
    "the retired approach name": (_mutated(
        lambda a, p: a["alternatives"][0].__setitem__("approach", "retain")), "retain"),
}


@pytest.mark.parametrize("label", list(REFUSALS))
def test_the_owner_refuses_an_answer_that_states_a_basis_the_evidence_does_not_show(project, label):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    mutate, message = REFUSALS[label]
    answer = mutate(packet_of(prepared))
    with pytest.raises(ValueError, match=re.escape(message)):
        complete_architecture_consequence(store, replay(prepared["request"], answer))
    assert project_architecture_consequence(store)["status"] == "awaiting_host_agent"


def test_the_instruction_names_every_field_value_and_limit_the_owner_enforces(project):
    from auteur.beginner import studio_architecture_consequence as module

    for field in ("schema_version", "reading", "reach", "concerns", "no_concern_reason", "mechanisms", "inheritance",
                  "trajectories", "alternatives", "not_established", "title", "status", "earlier", "proposed", "evidence",
                  "intent", "counterevidence", "competing_reading", "approach", "questions", "keeps", "gains", "costs",
                  "next_investigation", "conditional_consequence", "transformation", "unresolved", "steps", "stage",
                  "basis", "assumptions", "comparison", "from", "to"):
        assert field in _SYSTEM, field
    # The evidence rules the owner enforces are stated to the agent, so a refusal is never a surprise.
    flat = " ".join(_SYSTEM.split()).lower()
    for rule in ("preserved needs at least one cited item", "introduced needs a proposed_wording",
                 "possibly_displaced needs an earlier-side item", "transformed needs an earlier-side item",
                 "concern titles are distinct", "mechanism readings cite distinct mechanisms",
                 "required for transformed, removed and introduced", "a step with basis recorded must cite a recorded item",
                 "a working_book title never supports a recorded or plausible inheritance"):
        assert rule in flat, rule
    for value in ("preserved", "transformed", "possibly_displaced", "introduced", "instruction_names_it",
                  "selected_alternative_names_it", "not_established", "removed", "historical",
                  "keep_baseline", "accept_proposal", "replace", "integrate", "separate", "defer", "reframe",
                  "local", "conditional_inheritance", "long_horizon", "recorded_inheritance", "plausible_inheritance",
                  "proposed_inheritance", "unknown_inheritance", "local_decision", "mechanism_transformation",
                  "tension", "opportunity", "inheritance", "recorded", "interpreted", "speculative"):
        assert value in _SYSTEM, value
    # The approach names are the owner's table, and the retired name is not offered.
    assert set(module.APPROACH_MEANINGS) == {"keep_baseline", "accept_proposal", "replace", "integrate", "separate",
                                             "defer", "reframe"}
    for name, meaning in module.APPROACH_MEANINGS.items():
        assert meaning in _SYSTEM, name
    for limit in (module.READING_LIMIT, module.CONCERN_TITLE_LIMIT, module.CONCERN_READING_LIMIT,
                  module.CONCERN_SIDE_LIMIT, module.COUNTER_LIMIT, module.APPROACH_TITLE_LIMIT,
                  module.APPROACH_SUMMARY_LIMIT, module.APPROACH_GAINS_LIMIT, module.APPROACH_COSTS_LIMIT,
                  module.NEXT_LIMIT, module.NOT_ESTABLISHED_LIMIT, module.NO_CONCERN_LIMIT, module.MAX_CONCERNS,
                  module.MAX_MECHANISM_READINGS, module.MAX_INHERITANCE, module.MAX_TRAJECTORIES,
                  module.MAX_TRAJECTORY_STEPS, module.READING_ITEM_LIMIT, module.TRANSFORMATION_LIMIT,
                  module.STEP_TEXT_LIMIT, module.INHERITANCE_TEXT_LIMIT):
        assert str(limit) in _SYSTEM, limit
    # The model, not only the prompt, enforces the same bound.
    with pytest.raises(ValueError):
        module.ConsequenceAnswerV2.model_validate({"schema_version": 2, "reading": "x" * (module.READING_LIMIT + 1),
                                                   "reach": "local", "concerns": [], "no_concern_reason": "none"})


def test_an_alternative_is_investigated_on_its_own_continuing_questions_and_never_rebound(project):
    store = store_for(project)
    sha, projection = completed(store, project)
    alternative = projection["result"]["alternatives"][0]
    origin = {"request_sha256": projection["request_sha256"], "alternative_id": alternative["id"]}
    summary = consequence_origin(store, origin, list(alternative["questions"]))
    assert summary["questions"] == [Q_CONVERSION]
    with pytest.raises(ValueError, match="exactly the questions"):
        consequence_origin(store, origin, [Q_COMPACT])
    with pytest.raises(ValueError, match="not completed|not recorded"):
        consequence_origin(store, {"request_sha256": "0" * 64, "alternative_id": "a1"}, [Q_CONVERSION, Q_COMPACT])


def test_an_alternative_whose_question_is_later_removed_is_refused_not_rebound(project):
    store = store_for(project)
    completed(store, project)
    projection = project_architecture_consequence(store)
    alternative = projection["result"]["alternatives"][0]
    origin = {"request_sha256": projection["request_sha256"], "alternative_id": alternative["id"]}
    sha = propose(store, "Set the conversion question aside.", remove_conversion)
    apply_architecture_review(store, sha)
    with pytest.raises(ValueError, match="no longer open"):
        consequence_origin(store, origin, list(alternative["questions"]))


def test_an_investigation_takes_one_origin_and_carries_the_alternative_it_came_from(project):
    store = store_for(project)
    completed(store, project)
    projection = project_architecture_consequence(store)
    alternative = projection["result"]["alternatives"][0]
    origin = {"request_sha256": projection["request_sha256"], "alternative_id": alternative["id"]}
    intent = {"version": 1, "canvas_id": store.canvas_id, "operation": "explain", "target": "current",
              "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
              "anchors": [{"kind": "question", "id": Q_CONVERSION}],
              "author_text": alternative["next_investigation"], "from_consequence": origin}
    inquiry = prepare_architecture_inquiry(store, dict(intent))
    request = json.loads(inquiry["request"]["user"])
    assert request["from_consequence"]["alternative_id"] == alternative["id"]
    assert inquiry["request"]["settings"]["from_consequence"]["title"] == alternative["title"]
    with pytest.raises(ValueError, match="one origin"):
        prepare_architecture_inquiry(store, {**intent, "from_discovery": {"request_sha256": "0" * 64,
                                                                         "possibility_id": "p1"}})


def test_a_selected_alternative_keeps_the_consequence_origin_it_came_from(project):
    store = store_for(project)
    completed(store, project)
    projection = project_architecture_consequence(store)
    alternative = projection["result"]["alternatives"][0]
    inquiry_sha = "b" * 64
    folder = _root(store) / "inquiries" / "requests" / inquiry_sha
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "result.json").write_text(json.dumps({
        "baseline_candidate_request_sha256": _candidate(store)["request_sha256"],
        "intent": {"operation": "compare", "author_text": alternative["next_investigation"],
                   "anchors": [{"kind": "question", "id": Q_CONVERSION}, {"kind": "question", "id": Q_COMPACT}]},
        "hypotheses": [{"title": "Keep both", "description": "Two questions, two mechanisms."}],
        "from_consequence": {"request_sha256": projection["request_sha256"], "alternative_id": alternative["id"],
                             "title": alternative["title"]},
    }), encoding="utf-8")
    context = _selected_alternative_context(
        store, _candidate(store), SelectedCreativeAlternative(inquiry_request_sha256=inquiry_sha, hypothesis_id="h1"))
    assert context["from_consequence"]["alternative_id"] == alternative["id"]
    assert "from_discovery" not in context


def test_no_analysis_is_offered_without_a_pending_revision(project):
    store = store_for(project)
    assert project_architecture_consequence(store)["status"] == "not_started"
    with pytest.raises(ValueError, match="no pending architecture revision"):
        prepare_architecture_consequence(store, contract_version=2)


def edit_vision(store) -> None:
    """Change the Story Vision after a proposal was reviewed: the review's own working context changes with it."""
    item = next(i for i in store.load().items if i.id == "story-vision")
    edited = {**item.model_dump(mode="json"), "content": item.content + "\n\nRevised after the proposal."}
    store.apply("update-item", expected_revision=store.load().revision, command_id="vision-edit-test", payload={"item": edited})


def test_a_recorded_change_carries_the_authors_instruction_into_its_history_evidence(project):
    """The owner's reason for a recorded change reaches the agent as recorded_reason (it was always null before)."""
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    complete_revision_applied(store)
    propose(store, "Narrow the conversion question once more.",
            lambda c: c["open_questions"].__setitem__(CONVERSION_INDEX, NARROWED + " Narrowed again."))
    packet = packet_of(prepare_architecture_consequence(store, contract_version=2))
    evidence = {item["id"]: item for item in packet["evidence"]}
    row = next(r for r in packet["examined_questions"] if r["id"] == Q_CONVERSION)
    reworded = [evidence[i] for i in row["baseline_evidence"]
                if evidence[i]["kind"] == "recorded_history" and evidence[i].get("change") == "reworded"]
    assert reworded, "the earlier rewording is in the question's recorded history"
    assert reworded[0]["recorded_reason"] == INSTRUCTION


def complete_revision_applied(store) -> None:
    """Apply the pending revision (the analysis test above needs the earlier rewording on the record)."""
    apply_architecture_review(store, project_architecture_request(store))


def project_architecture_request(store) -> str:
    from auteur.beginner.studio_architecture import project_architecture
    return project_architecture(store)["review"]["request_sha256"]


def test_an_analysis_goes_stale_when_the_pending_review_context_changes_and_apply_refuses_it(project):
    store = store_for(project)
    sha = propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    complete_architecture_consequence(store, replay(prepared["request"], valid_answer(packet_of(prepared))))
    assert project_architecture_consequence(store)["standing"] == "current"
    edit_vision(store)
    projection = project_architecture_consequence(store)
    assert projection["standing"] == "stale_context", projection["standing"]
    with pytest.raises(Exception, match="working context changed"):
        apply_architecture_review(store, sha)


def test_a_second_analysis_of_the_same_proposal_makes_the_first_earlier_in_history(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    first = prepare_architecture_consequence(store, contract_version=2)
    complete_architecture_consequence(store, replay(first["request"], valid_answer(packet_of(first))))
    prepare_architecture_consequence(store, contract_version=2)
    projection = project_architecture_consequence(store)
    assert projection["standing"] == "current" and projection["status"] == "awaiting_host_agent"
    earlier = [row for row in projection["history"] if row["request_sha256"] == first["request_sha256"]]
    assert earlier and earlier[0]["standing"] == "superseded", "an earlier analysis is never current"


def test_a_damaged_result_is_named_and_the_projection_still_reads(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    complete_architecture_consequence(store, replay(prepared["request"], valid_answer(packet_of(prepared))))
    result = _root(store) / "consequences" / "requests" / prepared["request_sha256"] / "result.json"
    result.write_text("{ not json", encoding="utf-8")
    projection = project_architecture_consequence(store)
    assert projection["status"] == "unreadable"


def test_an_interrupted_completion_is_finished_by_the_same_response(project):
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    prepared = prepare_architecture_consequence(store, contract_version=2)
    payload = replay(prepared["request"], valid_answer(packet_of(prepared)))
    complete_architecture_consequence(store, payload)
    result = _root(store) / "consequences" / "requests" / prepared["request_sha256"] / "result.json"
    result.unlink()
    projection = complete_architecture_consequence(store, payload)
    assert projection["status"] == "ready" and result.is_file()


def test_an_alternative_of_an_earlier_analysis_cannot_be_investigated(project):
    store = store_for(project)
    completed(store, project)
    first = project_architecture_consequence(store)
    alternative = first["result"]["alternatives"][0]
    origin = {"request_sha256": first["request_sha256"], "alternative_id": alternative["id"]}
    propose(store, "Say what the Gate Table is for.",
            lambda c: c["open_questions"].__setitem__(7, c["open_questions"][7] + " Revised."))
    with pytest.raises(ValueError, match="latest analysis of the proposal on screen"):
        consequence_origin(store, origin, list(alternative["questions"]))


def test_a_question_introduced_by_a_removal_is_not_accepted_as_introduced(project):
    """A removal is never evidence that a concern was introduced: the rule the instruction states is the rule enforced."""
    from auteur.beginner.studio_architecture_consequence import _check_answer
    packet = {"evidence": [{"id": "E1", "kind": "removed", "text": "Old wording."},
                           {"id": "E2", "kind": "baseline_wording", "text": "Old wording."}],
              "baseline_question_ids": [Q_CONVERSION, Q_COMPACT]}
    answer = ConsequenceAnswer.model_validate({
        "schema_version": 1, "reading": "A question is removed.", "no_concern_reason": None,
        "concerns": [{"title": "A new uncertainty", "status": "introduced", "reading": "It is new.", "evidence": ["E1"]}],
        "prospective": [], "alternatives": [], "not_established": []})
    with pytest.raises(ValueError, match="introduced but cites no proposed"):
        _check_answer(answer, packet)
