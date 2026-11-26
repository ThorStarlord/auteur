"""Agent-directed opportunity discovery: the owner contract, on the Spring Ledger study.

The discovery is explicit, bounded and advisory. Every reference an answer makes must resolve inside its own request;
a possibility is transferable only while its questions are still continuing and is never rebound to another question; a
stale baseline retains the answer; a decline changes no narrative record.
"""
import json
import shutil
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from auteur.beginner.studio_architecture import _candidate, _root
from auteur.beginner.studio_architecture_discovery import (
    _SYSTEM, DiscoveryAnswer, discovery_origin, prepare_architecture_discovery, complete_architecture_discovery,
    project_architecture_discoveries, record_possibility_decision,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry, project_architecture_inquiry,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

Q_A = identity_for(12)
Q_B = identity_for(13)
Q_GATE = identity_for(14)
BOOK = 24


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("discovery") / "discovery"
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


def narrative_files(project: Path) -> dict[str, bytes]:
    """Every file the narrative owns: the Architecture and the Books, but not the discovery or inquiry folders."""
    root = _root(store_for(project)).parent
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and not any(part in ("discoveries", "inquiries") for part in path.parts):
            out[str(path.relative_to(root))] = path.read_bytes()
    return out


def possibility(candidate, questions, *, evidence=None, basis="grounded", title="Hours and the tally", **extra):
    row = {
        "title": title, "kind": "shared_mechanism",
        "possibility": "The ledger's hours could decide who is counted, so one mechanism develops both questions.",
        "significance": "It would make the tally a story consequence rather than a side detail.",
        "questions": list(questions),
        "evidence": evidence if evidence is not None else [
            {"ref_kind": "node", "ref_id": "eng_ledger", "note": "The ledger records hours worked."}],
        "basis": basis, "assumptions": ["The Council reads the ledger as the tally."],
        "counterevidence": ["The Book decision may need a separate count."],
        "gains": "One mechanism with two payoffs.", "costs": "The questions stop being independent.",
        "next_investigation": "Ask whether the hours column is the tally the Council keeps.",
    }
    row.update(extra)
    return row


def answer(possibilities=None, reason=None, **extra):
    body = {"schema_version": 1, "coverage_note": "I read every continuing question and the ledger's recorded structure.",
            "possibilities": possibilities or [], "no_possibility_reason": reason, "uncertainties": ["Whether the Books depend on it."]}
    body.update(extra)
    return body


def prepare(store, goal=None):
    projection = prepare_architecture_discovery(store, goal=goal)
    return projection["pending"]["request"]


def complete(store, request, body):
    response = build_host_agent_response(HostAgentRequest(**request), json.dumps(body), runtime="discovery-test")
    return complete_architecture_discovery(store, response.model_dump())


def only_discovery(store):
    projection = project_architecture_discoveries(store)
    return projection["discoveries"][0]


def test_the_request_is_explicit_and_its_orientation_is_bounded(project):
    store = store_for(project)
    candidate_before = json.dumps(_candidate(store)["candidate"], sort_keys=True)
    request = prepare(store, goal="Where do the tally and the gate need each other?")
    user = json.loads(request["user"])
    assert request["role"] == "studio_architecture_discovery"
    assert user["discovery_packet"]["stage"] == "A_orientation"
    assert user["discovery_packet"]["author_goal"].startswith("Where do the tally")
    shown = {question["id"] for question in user["discovery_packet"]["questions"]}
    assert {Q_A, Q_B, Q_GATE} <= shown
    for question in user["discovery_packet"]["questions"]:
        assert len(question["book_decisions"]) <= 2
    assert set(user["discovery_packet"]["limits"]["book_decisions_omitted"]) == {Q_A, Q_B, Q_GATE} | set(
        user["discovery_packet"]["limits"]["book_decisions_omitted"])
    assert request["settings"]["discovery_evidence_sha256"] == user["discovery_packet"]["evidence_sha256"]
    assert json.dumps(_candidate(store)["candidate"], sort_keys=True) == candidate_before


def test_a_grounded_possibility_resolves_and_is_stored_as_advisory_only(project):
    store = store_for(project)
    before = narrative_files(project)
    request = prepare(store)
    complete(store, request, answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B])]))

    row = only_discovery(store)
    assert row["baseline"] == "current" and len(row["possibilities"]) == 1
    item = row["possibilities"][0]
    assert item["id"] == "p1" and item["status"]["state"] == "transferable" and item["status"]["transferable"]
    assert item["evidence"][0]["present_now"] is True
    assert item["applied"] is False and item["investigations"] == []
    assert narrative_files(project) == before, "a discovery writes nothing into the Architecture or a Book"


@pytest.mark.parametrize("label,mutate,message", [
    ("an unknown question", lambda c: possibility(c, [Q_A, "q-never-recorded"]), "not a continuing open question"),
    ("a question that is no longer open", lambda c: possibility(c, [Q_A, "q-no-longer-here"]), "not a continuing open question"),
    ("an unknown node", lambda c: possibility(c, [Q_A, Q_B], evidence=[{"ref_kind": "node", "ref_id": "nope", "note": "x"}]),
     "is not in this request"),
    ("a book reference the packet does not show", lambda c: possibility(
        c, [Q_A, Q_B], evidence=[{"ref_kind": "book_decision", "ref_id": "dec-missing", "book_number": 24, "note": "x"}]),
     "is not in this request"),
    ("a grounded claim with only wording and Book evidence", lambda c: possibility(
        c, [Q_A, Q_B], evidence=[{"ref_kind": "question", "ref_id": Q_A, "note": "x"}]),
     "cites no recorded mechanism"),
])
def test_a_reference_that_does_not_resolve_refuses_the_whole_answer(project, label, mutate, message):
    store = store_for(project)
    request = prepare(store)
    with pytest.raises(Exception, match=message):
        complete(store, request, answer([mutate(_candidate(store)["candidate"])]))
    folder = _root(store) / "discoveries" / "requests" / request["request_sha256"]
    assert not (folder / "result.json").exists(), f"{label}: a refused answer is not stored"


def test_a_speculative_possibility_is_allowed_only_when_labelled(project):
    store = store_for(project)
    request = prepare(store)
    body = answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B], basis="speculative",
                               evidence=[{"ref_kind": "question", "ref_id": Q_A, "note": "The wording invites it."}])])
    complete(store, request, body)
    item = only_discovery(store)["possibilities"][0]
    assert item["basis"] == "speculative"


def test_an_empty_answer_must_say_why_and_is_stored_as_such(project):
    store = store_for(project)
    request = prepare(store)
    with pytest.raises(ValidationError):
        DiscoveryAnswer.model_validate(answer([], reason=None))
    complete(store, request, answer([], reason="Nothing in the recorded mechanisms supports a stronger possibility."))
    row = only_discovery(store)
    assert row["possibilities"] == [] and "stronger possibility" in row["no_possibility_reason"]


def test_a_possibility_is_transferred_only_on_its_own_questions(project):
    store = store_for(project)
    complete(store, prepare(store), answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B])]))
    origin = {"request_sha256": only_discovery(store)["request_sha256"], "possibility_id": "p1"}
    with pytest.raises(ValueError, match="exactly the questions the possibility names"):
        discovery_origin(store, origin, [Q_A, Q_GATE])
    summary = discovery_origin(store, origin, [Q_A, Q_B])
    assert summary["possibility_id"] == "p1" and summary["status_at_transfer"] == "transferable"


def test_an_investigation_from_a_possibility_carries_its_origin_in_the_request_and_the_result(project):
    store = store_for(project)
    complete(store, prepare(store), answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B])]))
    origin = {"request_sha256": only_discovery(store)["request_sha256"], "possibility_id": "p1"}
    prepare_architecture_inquiry(store, {
        "version": 1, "canvas_id": store.canvas_id, "operation": "compare", "target": "current",
        "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
        "anchors": [{"kind": "question", "id": Q_A}, {"kind": "question", "id": Q_B}],
        "author_text": "Do the tally and the hours share one mechanism?", "from_discovery": origin})
    pending = project_architecture_inquiry(store)
    user = json.loads(pending["request"]["user"])
    assert user["from_discovery"]["possibility_id"] == "p1"
    assert pending["request"]["settings"]["from_discovery"]["possibility_sha256"]
    response = build_host_agent_response(HostAgentRequest(**pending["request"]), json.dumps({
        "schema_version": 1, "analysis": "They share the ledger.", "recorded_observations": [],
        "hypotheses": [], "uncertainties": []}), runtime="discovery-test")
    complete_architecture_inquiry(store, response.model_dump())
    result = project_architecture_inquiry(store)["result"]
    assert result["from_discovery"]["request_sha256"] == origin["request_sha256"]
    row = only_discovery(store)
    assert row["possibilities"][0]["investigations"][0]["operation"] == "compare"


def test_a_question_that_is_no_longer_open_blocks_transfer_and_is_never_rebound(project):
    store = store_for(project)
    complete(store, prepare(store), answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B])]))
    def drop_b(candidate):
        index = candidate["open_question_ids"].index(Q_B)
        del candidate["open_questions"][index]
        del candidate["open_question_ids"][index]
    impact.revise_architecture(store, "Drop the second question.", drop_b)
    item = only_discovery(store)["possibilities"][0]
    assert item["status"]["state"] == "not_transferable" and not item["status"]["transferable"]
    assert Q_B in item["status"]["note"]
    origin = {"request_sha256": only_discovery(store)["request_sha256"], "possibility_id": "p1"}
    with pytest.raises(ValueError, match="no longer open"):
        discovery_origin(store, origin, [Q_A, Q_B])


def test_a_reworded_question_stays_transferable_and_says_so(project):
    store = store_for(project)
    complete(store, prepare(store), answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B])]))
    def reword(candidate):
        index = candidate["open_question_ids"].index(Q_A)
        candidate["open_questions"][index] += " Revised: the tally is counted in hours."
    impact.revise_architecture(store, "Reword the first question.", reword)
    item = only_discovery(store)["possibilities"][0]
    assert item["status"]["state"] == "reworded" and item["status"]["transferable"]
    assert "earlier wording" in item["status"]["note"]


def test_a_stale_baseline_retains_the_answer_and_the_earlier_result_stays_readable(project):
    store = store_for(project)
    complete(store, prepare(store), answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B])]))
    request = prepare(store)
    def touch_a_summary(c):
        node = next(n for n in c["nodes"] if isinstance(n.get("summary"), str))
        node["summary"] += " Revised."
    impact.revise_architecture(store, "Say how reading is taught.", touch_a_summary)
    with pytest.raises(Exception, match="changed since this discovery was prepared"):
        complete(store, request, answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B])]))
    stale = list((_root(store) / "discoveries" / "requests" / request["request_sha256"]).glob("stale_response.json"))
    assert stale, "the stale response is retained as evidence"
    earlier = [row for row in project_architecture_discoveries(store)["discoveries"]
               if row["request_sha256"] != request["request_sha256"]]
    assert earlier and earlier[0]["baseline"] == "earlier_architecture"


def test_declining_a_possibility_changes_no_narrative_record(project):
    store = store_for(project)
    complete(store, prepare(store), answer([possibility(_candidate(store)["candidate"], [Q_A, Q_B])]))
    sha = only_discovery(store)["request_sha256"]
    before = narrative_files(project)
    record_possibility_decision(store, sha, "p1", "declined", reason="The tally is settled elsewhere.")
    item = only_discovery(store)["possibilities"][0]
    assert item["decision"] == {"decision": "declined", "reason": "The tally is settled elsewhere."}
    assert narrative_files(project) == before
    record_possibility_decision(store, sha, "p1", "reopened")
    assert only_discovery(store)["possibilities"][0]["decision"] is None


def test_the_instruction_names_the_keys_the_answer_requires():
    for key in ("schema_version=1", "coverage_note", "possibilities", "no_possibility_reason", "uncertainties"):
        assert key in _SYSTEM, key
    for key in ("title", "kind", "possibility", "significance", "questions", "evidence", "basis",
                "assumptions", "counterevidence", "gains", "costs", "next_investigation"):
        assert f'"{key}"' in _SYSTEM, key
    for key in ("ref_kind", "ref_id", "book_number", "note"):
        assert f'"{key}"' in _SYSTEM, key


def test_the_instruction_states_the_limits_the_model_enforces():
    """The first exercise's two answers were refused for length, because the instruction stated no limit. The limits are
    now named once, and the instruction is generated from them: each stated number is the one the model enforces."""
    from auteur.beginner.studio_architecture_discovery import (
        COVERAGE_LIMIT, ITEM_LIMIT, NEXT_LIMIT, POSSIBILITY_LIMIT, DiscoveredPossibility,
    )

    assert f"coverage_note {COVERAGE_LIMIT}" in _SYSTEM
    assert f"possibility {POSSIBILITY_LIMIT}" in _SYSTEM
    assert f"next_investigation {NEXT_LIMIT}" in _SYSTEM
    assert f"{ITEM_LIMIT}" in _SYSTEM
    base = {"coverage_note": "x", "schema_version": 1, "possibilities": [], "no_possibility_reason": "none"}
    DiscoveryAnswer.model_validate({**base, "coverage_note": "x" * COVERAGE_LIMIT})
    with pytest.raises(ValidationError):
        DiscoveryAnswer.model_validate({**base, "coverage_note": "x" * (COVERAGE_LIMIT + 1)})
    with pytest.raises(ValidationError):
        DiscoveredPossibility.model_validate({
            "title": "t", "possibility": "x" * (POSSIBILITY_LIMIT + 1), "significance": "s",
            "questions": ["q-a", "q-b"], "evidence": [{"ref_kind": "node", "ref_id": "n", "note": "n"}],
            "basis": "grounded", "next_investigation": "n"})
