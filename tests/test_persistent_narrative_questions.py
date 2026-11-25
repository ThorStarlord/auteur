"""Persistent narrative questions through the real owners, on the Spring Ledger study.

The journey: a Series-wide open question that Book 24 records a decision about gains a stable identity; a later
Architecture revision reorders and rewords it (keeping the identity); Book 24's decision still names the wording it was
written against; the question-only revision is reviewable; and an inquiry can be grounded on the question, both
directly and through the Book's own decision, with the agent's answer advisory and nothing settled.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402

from auteur.beginner.studio_architecture import _candidate, architecture_revision_chain, project_architecture  # noqa: E402
from auteur.beginner.studio_architecture_inquiry import (  # noqa: E402
    complete_architecture_inquiry, prepare_architecture_inquiry,
)
from auteur.beginner.studio_architecture_questions import question_history  # noqa: E402
from auteur.series.working_book_architecture import book_element_evidence, book_series_references  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402

# Stable identities for the questions Book 24 records a decision about; others get a positional-free identity too.
SLUGS = {2: "finale-mechanism", 4: "right-revocable", 5: "conversion-settlement", 6: "compact-settlement",
         7: "surge-route", 9: "hesper-motive", 12: "reform-stance", 13: "plurality", 14: "gate-table"}
GATE = "gate-table"


def identity_for(index):
    return f"q-{SLUGS.get(index, f'other-{index}')}"


def open_questions(store):
    return _candidate(store)["candidate"]["open_questions"]


def assign_identities(candidate):
    candidate["open_question_ids"] = [identity_for(i) for i in range(len(candidate["open_questions"]))]


def decision(store_project_value, book=24, decision_id="dec-gate-table"):
    references = book_series_references(store_project_value, book)["question_references"]
    return next(item for item in references if item["decision_id"] == decision_id)


@pytest.fixture
def ledger(tmp_path):
    project = tmp_path / "discovery"
    store = discovery.seed_discovery(project)
    return project, store


def test_a_legacy_question_keeps_its_wording_reference_and_no_invented_identity(ledger):
    project, store = ledger
    assert _candidate(store)["candidate"].get("open_question_ids") is None
    gate = decision(store)
    assert gate["state"] == "identity_not_established"
    assert gate["question_id"] is None
    assert gate["recorded_index"] == 14
    assert gate["recorded_text"] == open_questions(store)[14]


def test_identity_is_introduced_then_survives_reordering_and_rewording(ledger):
    project, store = ledger

    def introduce(candidate):
        assign_identities(candidate)

    impact.revise_architecture(store, "Give each open question a stable identity.", introduce)
    assert _candidate(store)["candidate"]["open_question_ids"][14] == identity_for(14)

    # Book 24 is written against the identity-bearing version: its decision now names the question's identity.
    discovery.reconcile_book_24(project)
    book_gate = decision(store)
    assert book_gate["state"] == "current_wording"
    assert book_gate["question_id"] == identity_for(14)

    # A question-only revision: the gate question moves to the front and is reworded; its identity is kept.
    nodes_before = json.dumps(_candidate(store)["candidate"]["nodes"], sort_keys=True)
    reworded = open_questions(store)[14] + " Whether the Gate Table is open to the Council as well."

    def reorder_and_reword(candidate):
        questions = candidate["open_questions"]
        identities = candidate["open_question_ids"]
        index = identities.index(identity_for(14))
        questions[index] = reworded
        candidate["open_questions"] = [questions[index]] + [q for i, q in enumerate(questions) if i != index]
        candidate["open_question_ids"] = [identities[index]] + [x for i, x in enumerate(identities) if i != index]

    impact.revise_architecture(store, "Reword and move the Gate Table question.", reorder_and_reword)
    assert json.dumps(_candidate(store)["candidate"]["nodes"], sort_keys=True) == nodes_before  # question-only

    changes = project_architecture(store)["question_changes"]
    gate_row = next(row for row in changes["questions"] if row["id"] == identity_for(14))
    assert gate_row["status"] == "moved_and_reworded"
    assert gate_row["previous_index"] == 14 and gate_row["index"] == 0

    # The Book's decision still names the wording and version it was written against; it is not silently rebound.
    still = decision(store)
    assert still["version_request_sha256"] == book_gate["version_request_sha256"]
    assert still["state"] == "moved_and_reworded"
    assert still["current_index"] == 0
    assert still["recorded_text"] == book_gate["recorded_text"]


def test_a_removed_question_is_recorded_as_removed_and_never_as_answered(ledger):
    project, store = ledger
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)

    def drop_gate(candidate):
        identities = candidate["open_question_ids"]
        index = identities.index(identity_for(14))
        del candidate["open_questions"][index]
        del identities[index]

    impact.revise_architecture(store, "Drop the Gate Table question.", drop_gate)
    changes = project_architecture(store)["question_changes"]
    assert changes["removed"] == [{"id": identity_for(14), "previous_index": 14,
                                   "previous_text": changes["removed"][0]["previous_text"]}]
    # Removal is never recorded as settlement: no status or key says the question was answered or resolved.
    assert not any(key in changes for key in ("answered", "resolved"))
    assert not any(row["status"] in ("answered", "resolved") for row in changes["questions"])


def test_a_retired_identity_cannot_name_a_different_question_at_the_owner_boundary(ledger):
    project, store = ledger
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)

    def drop_gate(candidate):
        identities = candidate["open_question_ids"]
        index = identities.index(identity_for(14))
        del candidate["open_questions"][index]
        del identities[index]

    impact.revise_architecture(store, "Drop the Gate Table question.", drop_gate)
    before = _candidate(store)["request_sha256"]

    def recycle(candidate):
        candidate["open_questions"].append("A different question that takes the retired identity?")
        candidate["open_question_ids"].append(identity_for(14))

    with pytest.raises(ValueError, match="already used by an earlier version"):
        impact.revise_architecture(store, "Reuse the retired identity.", recycle)
    assert _candidate(store)["request_sha256"] == before  # nothing was applied


def test_history_resolves_each_identity_to_its_exact_recorded_versions(ledger):
    project, store = ledger
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)

    def reword(candidate):
        index = candidate["open_question_ids"].index(identity_for(14))
        candidate["open_questions"][index] += " Revised."

    impact.revise_architecture(store, "Reword the Gate Table question.", reword)
    from auteur.beginner.studio_architecture import architecture_versions
    versions = list(architecture_versions(store))
    history = question_history(versions)
    gate_versions = history[identity_for(14)]
    assert [entry["text"].endswith("Revised.") for entry in gate_versions] == [False, True]
    assert gate_versions[0]["request_sha256"] != gate_versions[1]["request_sha256"]
    assert architecture_revision_chain(store)["complete"] is True


def test_an_inquiry_grounded_on_a_question_is_advisory_and_settles_nothing(ledger):
    project, store = ledger
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    before = json.dumps(_candidate(store)["candidate"], sort_keys=True)
    sha = _candidate(store)["request_sha256"]
    view = prepare_architecture_inquiry(store, {
        "canvas_id": store.canvas_id, "target": "current", "operation": "explore",
        "expected_candidate_request_sha256": sha,
        "anchors": [{"kind": "question", "id": identity_for(14)}],
        "author_text": "Does the earlier formulation remain appropriate, or should the question be clarified?",
    })
    result = {
        "schema_version": 1,
        "analysis": "The question asks whether the Gate Table is accepted; the wording leaves its standing open.",
        "recorded_observations": [{"kind": "question", "id": identity_for(14),
                                   "claim": "The Architecture records this question as open."}],
        "hypotheses": [
            {"title": "A standing question", "divergence_axis": "social_scale",
             "description": "The Gate Table stays open for the Council; the question is about standing."},
            {"title": "A mechanism question", "divergence_axis": "causal_engine",
             "description": "The Gate Table is a mechanism whose acceptance decides which hands may pass."},
        ],
        "uncertainties": ["Whether any Book depends on the Gate Table being accepted."],
    }
    payload = build_host_agent_response(HostAgentRequest(**view["request"]), json.dumps(result),
                                        runtime="test-agent").model_dump()
    complete_architecture_inquiry(store, payload)
    assert json.dumps(_candidate(store)["candidate"], sort_keys=True) == before  # the inquiry changed nothing


def test_an_unknown_question_anchor_is_refused_before_anything_is_asked(ledger):
    project, store = ledger
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    with pytest.raises(ValueError, match="not an open question"):
        prepare_architecture_inquiry(store, {
            "canvas_id": store.canvas_id, "target": "current", "operation": "explore",
            "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
            "anchors": [{"kind": "question", "id": "q-invented"}],
            "author_text": "A question the Architecture never recorded.",
        })


def test_a_legacy_decision_cannot_ground_a_question_inquiry_until_its_identity_is_established(ledger):
    project, store = ledger
    evidence = book_element_evidence(store, 24, "dec-gate-table")
    assert evidence["decision_question"]["state"] == "identity_not_established"
    with pytest.raises(ValueError):
        prepare_architecture_inquiry(store, {
            "canvas_id": store.canvas_id, "target": "current", "operation": "explore",
            "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
            "anchors": [{"kind": "question", "id": identity_for(14)}],
            "author_text": "Ask about the Gate Table through the Book's own decision.",
            "book_evidence": {"book_number": 24, "element_id": "dec-gate-table",
                              "expected_book_request_sha256": evidence["book_request_sha256"],
                              "expected_element_content_sha256": evidence["element"]["content_sha256"]},
        })


def test_a_book_decision_grounds_an_inquiry_on_its_question_once_the_identity_is_established(ledger):
    project, store = ledger
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    discovery.reconcile_book_24(project)
    evidence = book_element_evidence(store, 24, "dec-gate-table")
    assert evidence["decision_question"]["state"] == "current_wording"
    view = prepare_architecture_inquiry(store, {
        "canvas_id": store.canvas_id, "target": "current", "operation": "explore",
        "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
        "anchors": [{"kind": "question", "id": identity_for(14)}],
        "author_text": "Does the Book's decision still name the question the Architecture now asks?",
        "book_evidence": {"book_number": 24, "element_id": "dec-gate-table",
                          "expected_book_request_sha256": evidence["book_request_sha256"],
                          "expected_element_content_sha256": evidence["element"]["content_sha256"]},
    })
    assert view["request"] is not None
    # The Book's wording is evidence, separate from the author's question.
    request_user = json.loads(view["request"]["user"])
    assert request_user["book_evidence"]["book"]["book_number"] == 24
    assert "Whether the Hollow Gate" in json.dumps(request_user["book_evidence"])


def test_question_references_survive_a_fresh_process_reading_the_same_records(ledger):
    project, store = ledger
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    discovery.reconcile_book_24(project)
    before = decision(store)
    from auteur.beginner.studio_store import CanvasStore
    fresh = CanvasStore(project, store.canvas_id)
    assert decision(fresh) == before


def test_an_inquiry_prepared_before_a_question_changed_is_refused_as_stale(ledger):
    project, store = ledger
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    stale_sha = _candidate(store)["request_sha256"]
    prepare_architecture_inquiry(store, {
        "canvas_id": store.canvas_id, "target": "current", "operation": "explore",
        "expected_candidate_request_sha256": stale_sha,
        "anchors": [{"kind": "question", "id": identity_for(14)}],
        "author_text": "Ask before the question is reworded.",
    })

    def reword(candidate):
        candidate["open_questions"][candidate["open_question_ids"].index(identity_for(14))] += " Reworded."

    impact.revise_architecture(store, "Reword the Gate Table question.", reword)
    with pytest.raises(ValueError):
        prepare_architecture_inquiry(store, {
            "canvas_id": store.canvas_id, "target": "current", "operation": "explore",
            "expected_candidate_request_sha256": stale_sha,
            "anchors": [{"kind": "question", "id": identity_for(14)}],
            "author_text": "The earlier request names a version that is no longer current.",
        })
