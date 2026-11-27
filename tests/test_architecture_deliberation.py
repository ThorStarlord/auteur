"""Narrative deliberation: the recorded history of two or three open questions, given to one cross-question inquiry.

The packet is read through the owners, bounded, labelled by basis, and frozen into the inquiry request. Each Working Book
decision says how it reached its question (recorded by the decision, or resolved by the Book owner from the version it
names). Reading changes nothing. The baseline inquiry, without history, is the comparison the exercise uses.
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

from auteur.beginner.studio_architecture import _candidate, _root
from auteur.beginner.studio_architecture_deliberation import (
    MAX_HISTORY_ITEMS, build_question_deliberation, deliberation_standing,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry, project_architecture_inquiry,
)
from auteur.beginner.studio_architecture_questions import text_digest
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import book_series_references

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

GATE = 14
GATE_ID = identity_for(GATE)
OTHER_ID = identity_for(0)
BOOK = 24
ANALYSIS = {"schema_version": 1, "analysis": "Both questions bear on the Ledger's hours column.",
            "recorded_observations": [], "hypotheses": [], "uncertainties": []}


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("deliberation") / "discovery"
    discovery.seed_discovery(root)
    return root


@pytest.fixture
def project(pristine, tmp_path):
    target = tmp_path / "discovery"
    shutil.copytree(pristine, target)
    return target


def ledger_store(project: Path) -> CanvasStore:
    return CanvasStore(project, discovery.SPRING)


def reword_gate(candidate, note="Revised: whether the Council may pass through it."):
    index = candidate["open_question_ids"].index(GATE_ID)
    candidate["open_questions"][index] += " " + note


def snapshot(directory: Path) -> dict[str, bytes]:
    return {str(path.relative_to(directory)): path.read_bytes()
            for path in sorted(directory.rglob("*")) if path.is_file()}


def question(packet, identifier):
    return next(q for q in packet["questions"] if q["id"] == identifier)


def pair_intent(store, text="Do these two questions conceal one creative problem?"):
    return {"version": 1, "canvas_id": store.canvas_id, "operation": "compare", "target": "current",
            "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
            "anchors": [{"kind": "question", "id": GATE_ID}, {"kind": "question", "id": OTHER_ID}],
            "author_text": text}


def complete_inquiry(store, pending):
    return complete_architecture_inquiry(store, build_host_agent_response(
        HostAgentRequest(**pending["request"]), json.dumps(ANALYSIS), runtime="deliberation-test").model_dump())


def test_the_packet_gives_each_question_its_recorded_history_and_the_reason_recorded_for_each_change(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, project, BOOK)
    impact.revise_architecture(store, "Reword the Gate Table question.", reword_gate)

    packet = build_question_deliberation(store, [GATE_ID, OTHER_ID])
    gate = question(packet, GATE_ID)

    assert gate["current"]["basis"] == "current_wording"
    assert gate["current"]["text_sha256"] == text_digest(_candidate(store)["candidate"]["open_questions"][GATE])
    assert gate["history_complete"] is True
    changes = [item for item in gate["history"] if item["basis"] == "recorded_change"]
    assert [item["change"] for item in changes] == ["introduced", "reworded"]
    introduced, reworded = changes
    assert introduced["reason"]["basis"] == "recorded_reason"
    assert introduced["reason"]["authority"] == "author_instruction_recorded"
    assert introduced["reason"]["instruction"] == "Give each open question a stable identity."
    assert reworded["reason"]["instruction"] == "Reword the Gate Table question."
    assert reworded["previous"]["text"] != reworded["text"]
    assert reworded["request_sha256"] != introduced["request_sha256"]
    # Every basis an item carries is one the packet's legend defines, so no item is unlabelled.
    used = {item["basis"] for q in packet["questions"] for item in q["history"] + q["books"]}
    assert used <= set(packet["basis_legend"]), used - set(packet["basis_legend"])


def test_each_book_decision_says_how_it_reached_its_question_as_the_owner_read_it(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, project, BOOK)
    impact.revise_architecture(store, "Reword the Gate Table question.", reword_gate)

    packet = build_question_deliberation(store, [GATE_ID, OTHER_ID])
    gate_books = question(packet, GATE_ID)["books"]
    assert gate_books, "the Gate Table decision of Book 24 must reach its question"
    owner_view = book_series_references(store, BOOK)
    for item in gate_books:
        owner = next(ref for ref in owner_view["question_references"] if ref["decision_id"] == item["decision_id"])
        expected = ("recorded_by_decision" if owner["decision_records_identity"]
                    else "resolved_by_owner_from_recorded_version")
        assert item["identity_basis"] == expected
        assert item["authority"] == "working_book_proposal_noncanonical"
        assert item["state"] == owner["state"]
        assert item["decision_text_sha256"] == text_digest(owner["decision_text"])
        assert item["book_request_sha256"] == owner_view["request_sha256"]


def test_history_is_bounded_and_the_omitted_middle_is_counted_not_inlined(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    for number in range(1, MAX_HISTORY_ITEMS + 2):
        impact.revise_architecture(
            store, f"Reword the Gate Table question, round {number}.",
            lambda candidate, n=number: reword_gate(candidate, f"Round {n}."))

    packet = build_question_deliberation(store, [GATE_ID, OTHER_ID])
    gate = question(packet, GATE_ID)
    recorded = [item for item in gate["history"] if item["basis"] != "named_gap"]
    assert len(recorded) <= MAX_HISTORY_ITEMS
    assert packet["limits"]["omitted"][GATE_ID]["history_items"] > 0
    # The introduction is kept, and so is the most recent change with its own recorded reason.
    changes = [item for item in gate["history"] if item["basis"] == "recorded_change"]
    assert changes[0]["change"] == "introduced"
    assert changes[-1]["reason"]["instruction"] == f"Reword the Gate Table question, round {MAX_HISTORY_ITEMS + 1}."
    # The two legacy revisions that named no identity are stated, not inlined as this question's wording.
    legacy = next(item for item in gate["history"] if item.get("gap") == "no_identity_before")
    assert legacy["versions"] == 2


def test_a_selection_must_be_two_or_three_distinct_continuing_questions(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    with pytest.raises(ValueError, match="two or three"):
        build_question_deliberation(store, [GATE_ID])
    with pytest.raises(ValueError, match="two or three"):
        build_question_deliberation(store, [GATE_ID, GATE_ID])
    with pytest.raises(ValueError, match="not a continuing open question"):
        build_question_deliberation(store, [GATE_ID, "q-never-recorded"])


def test_reading_the_packet_changes_nothing_on_disk(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    before = snapshot(project)
    build_question_deliberation(store, [GATE_ID, OTHER_ID])
    assert snapshot(project) == before


def test_a_prepared_inquiry_carries_the_frozen_packet_and_a_baseline_without_it(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    impact.revise_architecture(store, "Reword the Gate Table question.", reword_gate)

    prepare_architecture_inquiry(store, pair_intent(store))
    pending = project_architecture_inquiry(store)
    frozen = pending["request_sha256"]
    packet = json.loads(pending["request"]["user"])["deliberation"]
    assert packet["evidence_sha256"] == build_question_deliberation(store, [GATE_ID, OTHER_ID])["evidence_sha256"]
    assert pending["request"]["settings"]["deliberation_evidence_sha256"] == packet["evidence_sha256"]
    assert "deliberation is the recorded history" in pending["request"]["system"]

    complete_inquiry(store, pending)
    done = project_architecture_inquiry(store)
    assert done["status"] == "ready"
    assert done["result"]["deliberation"]["evidence_sha256"] == packet["evidence_sha256"]
    decisions = [row for row in done["result"]["deliberation_standing"] if row["kind"] == "book_decision"]
    assert all(row["standing"] in {"current", "book_revised", "decision_changed", "decision_gone", "unreadable"}
               for row in decisions)

    # A later revision moves the record on. The stored request keeps the packet it was asked with.
    impact.revise_architecture(store, "Reword the Gate Table question again.", reword_gate)
    stored = json.loads((_root(store) / "inquiries" / "requests" / frozen / "request.json").read_text(encoding="utf-8"))
    assert json.loads(stored["user"])["deliberation"]["evidence_sha256"] == packet["evidence_sha256"]
    later = project_architecture_inquiry(store)
    assert later["status"] == "stale" and later["result"] is None

    # Without history the same question is asked as before: no packet, and no settings key.
    prepare_architecture_inquiry(store, pair_intent(store, "Ask again without the history."), question_history=False)
    baseline = project_architecture_inquiry(store)["request"]
    assert "deliberation" not in json.loads(baseline["user"])
    assert "deliberation_evidence_sha256" not in baseline["settings"]


def test_a_book_revised_after_the_answer_is_reported_and_the_answer_stays_ready(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, project, BOOK)
    prepare_architecture_inquiry(store, pair_intent(store))
    pending = project_architecture_inquiry(store)
    complete_inquiry(store, pending)
    packet = json.loads(pending["request"]["user"])["deliberation"]

    reconcile(store, project, BOOK)

    standing = {(row["book_number"], row["decision_id"]): row["standing"]
                for row in deliberation_standing(store, packet) if row["kind"] == "book_decision"}
    gate_items = question(packet, GATE_ID)["books"]
    assert gate_items, "the packet must include the Gate Table decision of the reconciled Book"
    for item in gate_items:
        assert standing[(item["book_number"], item["decision_id"])] != "current"
    assert project_architecture_inquiry(store)["status"] == "ready"


def test_a_decision_reaches_the_packet_only_through_a_recorded_identity_or_the_owner_resolution(project):
    store = ledger_store(project)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, project, BOOK)
    packet = build_question_deliberation(store, [GATE_ID, OTHER_ID])
    for q in packet["questions"]:
        for item in q["books"]:
            assert item["identity_basis"] in ("recorded_by_decision", "resolved_by_owner_from_recorded_version")
            assert item["state"] != "identity_not_established"


def test_the_inquiry_instruction_names_the_keys_the_owner_requires():
    """Both coding agents of the first narrative-deliberation exercise wrote source_kind and source_id, because the
    instruction said "source kind, id". The owner rejected both answers. The instruction must name the owner's keys."""
    from auteur.beginner.studio_architecture_inquiry import _SYSTEM, InquiryHypothesis, InquiryObservation

    assert set(InquiryObservation.model_fields) == {"kind", "id", "claim"}
    for key in InquiryObservation.model_fields:
        assert f'"{key}"' in _SYSTEM, key
    for key in ("title", "description", "divergence_axis"):
        assert key in InquiryHypothesis.model_fields and f'"{key}"' in _SYSTEM, key
    assert "source kind" not in _SYSTEM
