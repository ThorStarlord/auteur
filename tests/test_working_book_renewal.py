"""T09: a consequential Book revision renews later Books instead of adding episodes.

End-to-end journey over the highest available integrated seam: a source-grounded
Series direction, a Working Book 26, a specific consequential revision, and the
resulting downstream options - with no silent canon change.
"""
from __future__ import annotations

import hashlib
import json

from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import (
    book_apply_review, book_complete, book_prepare, book_project, book_resume,
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


SERIES_QUESTIONS = [
    "Who is permitted to be remembered?",
    "What does the archive owe the erased?",
]

SERIES_VISION = (
    "A forty-Book series about a desert archive that decides which lives are recorded. "
    "The orders that keep the archive neutral are the only thing preventing a memory war. "
    "The intended experience is unease at how much order depends on forgetting."
)

BOOK_SOURCE = (
    "Book 26: the Warden's long campaign against the archive finally ends in victory. "
    "The orders that depended on having an enemy must now justify themselves to the "
    "people whose lives the archive never recorded."
)


def series_candidate():
    return {
        "schema_version": 2,
        "summary": "The archive's neutrality depends on an order built to have enemies.",
        "nodes": [
            {"id": "eng_archive", "title": "The archive",
             "category": "engine",
             "summary": "Recording a life grants it standing; omission erases standing."},
            {"id": "inst_orders", "title": "The orders",
             "category": "other",
             "summary": "The orders guarantee neutrality by refusing to record conflict."},
            {"id": "str_return", "title": "The long return",
             "category": "structure",
             "summary": "What was erased is owed a return the Series must eventually face."},
        ],
        "links": [{"id": "archive_to_orders", "source": "eng_archive",
                   "target": "inst_orders", "function": "the orders police the archive"}],
        "phases": [],
        "open_questions": list(SERIES_QUESTIONS),
        "emotion_targets": [],
        "complex_emotions": [],
        "genre_contracts": [],
        "genre_interactions": [],
    }


def book_26():
    return {
        "schema_version": 1,
        "book_number": 26,
        "title": "The Warden's Peace",
        "function": {
            "id": "fn-question", "provenance": "derived",
            "text": "Book 26 ends the Warden's campaign and leaves the orders without an enemy.",
            "question": "Can the orders survive winning?",
            "pressure": "The archive's neutrality was justified by a threat that is now gone.",
            "refs": [{"kind": "series_node", "id": "inst_orders"},
                     {"kind": "source_item", "id": "book-26-source"}],
        },
        "inherited": [{
            "id": "inh-orders", "provenance": "derived",
            "text": "The orders refuse to record any conflict they are party to.",
            "refs": [{"kind": "series_node", "id": "inst_orders"}],
        }],
        "engines": [{
            "id": "eng-victory", "provenance": "agent_proposed",
            "text": "Victory removes the justification the orders relied on.",
            "condition": "The Warden is defeated publicly.",
            "consequence": "The orders must defend their neutrality without an enemy.",
            "changed_state": "Neutrality becomes an argument rather than a guarantee.",
            "refs": [{"kind": "series_node", "id": "inst_orders"}],
        }],
        "agents": [{
            "id": "agent-warden", "provenance": "derived",
            "text": "The Warden wants the archive to record only what can be defended.",
            "refs": [{"kind": "series_node", "id": "inst_orders"}],
        }],
        "choice": {
            "id": "choice-peace", "provenance": "agent_proposed",
            "text": "The orders choose how to hold neutrality after victory.",
            "options": [
                {"id": "opt-open", "provenance": "agent_proposed",
                 "text": "Open the record to the erased."},
                {"id": "opt-closed", "provenance": "agent_proposed",
                 "text": "Keep the record closed."},
            ],
            "chosen_option_id": "opt-open",
            "costs_kept_visible": [{"id": "cost-orders", "provenance": "derived",
                                    "text": "Opening the record ends the orders' monopoly."}],
            "transformation": {"id": "trans-legitimacy", "provenance": "agent_proposed",
                               "text": "Legitimacy moves from the orders to the recorded."},
        },
        "local_resolution": [{"id": "res-peace", "provenance": "agent_proposed", "closure": True,
                              "text": "The Warden's campaign ends; the orders must answer publicly."}],
        "series_consequences": [{
            "id": "cons-orders", "provenance": "derived", "kind": "changes",
            "text": "The orders now depend on the people they excluded.",
            "refs": [{"kind": "series_node", "id": "inst_orders"}],
        }],
        "later_possibilities": [{"id": "later-legitimacy", "provenance": "agent_proposed",
                                 "kind": "enabled",
                                 "text": "Later Books may contest who authorizes the record."}],
        "assumptions": [{"id": "assume-quiet", "provenance": "agent_proposed",
                         "text": "The orders accept public accountability without armed resistance.",
                         "reversal": "Reverse if the orders resist with force within one Book."}],
        "alternatives": [{"id": "alt-delay", "provenance": "hypothetical",
                          "title": "The orders defer the question",
                          "status": "hypothetical",
                          "text": "The orders postpone accountability to Book 30.",
                          "rationale": "Buys time but leaves the erased unaddressed."}],
        "unresolved": [{"id": "unk-records", "provenance": "unresolved",
                        "text": "The source does not say how many lives were never recorded."}],
        "open_author_decisions": [{
            "id": "dec-remember", "provenance": "unresolved",
            "text": "The author decides who counts as a person for the record.",
            "series_question_index": 0,
            "series_question_sha256": _sha(SERIES_QUESTIONS[0]),
        }],
        "typed_edges": [{"id": "edge-orders", "source": "cons-orders",
                         "target": {"kind": "series_node", "id": "inst_orders"},
                         "dependency": "pressures",
                         "function": "The end of the campaign pressures the orders."}],
    }


def respond(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(
        request, json.dumps(data), runtime="integration-test", model="UNAVAILABLE",
    ).model_dump()


def make_store(tmp_path):
    store = CanvasStore(tmp_path, "renewal-canvas")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision",
                          "content": SERIES_VISION},
                 "position": {"x": 20, "y": 50}},
    )
    store.apply(
        "create-item", expected_revision=store.load().revision,
        command_id="book-26-source",
        payload={"item": {"id": "book-26-source", "kind": "note",
                          "title": "Book 26 source", "group": "book-26",
                          "content": BOOK_SOURCE},
                 "position": {"x": 20, "y": 200}},
    )
    status = prepare_architecture(store)
    complete_architecture(store, respond(status, series_candidate()))
    status = book_prepare(store, 26)
    book_complete(store, 26, respond(status, book_26()))
    return store


def test_a_consequential_victory_renews_later_books(tmp_path):
    store = make_store(tmp_path)

    status = book_prepare(
        store, 26,
        instruction="Show the orders losing their enemy and what that opens.",
        holistic=True,
    )
    revised = json.loads(json.dumps(book_26()))

    consequence = revised["series_consequences"][0]
    consequence.pop("provenance", None)
    consequence["attribution"] = "derived"
    consequence["epistemic_status"] = "asserted"
    consequence["kind"] = "complicates"
    consequence["text"] = (
        "With the Warden gone, the orders' neutrality is contested by the recorded, "
        "and legitimacy becomes the Series' live pressure."
    )
    revised["later_possibilities"] = [
        {
            "id": "later-legitimacy", "provenance": "agent_proposed",
            "kind": "enabled",
            "text": "Later Books may contest who authorizes the record.",
        },
        {
            "id": "later-audit-of-erasure", "attribution": "agent_proposed",
            "epistemic_status": "hypothetical", "kind": "enabled",
            "text": "A later Book may audit the archive's omissions rather than its entries.",
        },
    ]
    revised["alternatives"].append({
        "id": "alt-replace-orders", "attribution": "agent_proposed",
        "epistemic_status": "hypothetical",
        "title": "Replace the orders with an assembly of the recorded",
        "status": "hypothetical",
        "text": "The orders are dissolved and replaced by those who were excluded.",
        "rationale": "A different Series purpose, not a continuation of Book 26.",
        "responsibility": "alternative_responsibility",
    })
    book_complete(store, 26, respond(status, revised))
    book_apply_review(store, 26, status["request"]["request_sha256"])

    resume = book_resume(store, 26)
    artifact = resume["artifact"]

    # Renewal through changed state, not added episodes.
    assert artifact["series_consequences"][0]["kind"] == "complicates"
    kinds = {item["id"]: item["kind"] for item in artifact["later_possibilities"]}
    assert kinds["later-legitimacy"] == "enabled"
    assert kinds["later-audit-of-erasure"] == "enabled"
    assert len(artifact["later_possibilities"]) == 2

    # The review keeps the four categories distinct.
    responsibility = resume["responsibility"]
    assert responsibility["delegated"]["book_number"] == 26
    assert responsibility["progress"]["revision_number"] == 1
    assert [item["id"] for item in responsibility["alternative_responsibilities"]] == [
        "alt-replace-orders"
    ]
    assert responsibility["unresolved"]["author_decisions"] == ["dec-remember"]

    # Accepted meaning and non-Book canvas state stay untouched.
    assert not (store.project_root / "story_identity.yaml").exists()
    assert not (store.project_root / "blueprint.yaml").exists()


def test_renewal_review_reports_inspection_and_preserved_commitments(tmp_path):
    store = make_store(tmp_path)
    status = book_prepare(
        store, 26, instruction="End the campaign and keep the orders intact.",
        holistic=True,
    )
    revised = json.loads(json.dumps(book_26()))
    consequence = revised["series_consequences"][0]
    consequence.pop("provenance", None)
    consequence["attribution"] = "derived"
    consequence["epistemic_status"] = "asserted"
    consequence["kind"] = "complicates"
    consequence["text"] = "The orders outlive the enemy that justified them."
    book_complete(store, 26, respond(status, revised))

    projection = book_project(store, 26)
    review = projection["review"]

    # Preserved accepted commitments remain identified.
    assert review["preserved"]["count"] >= 1
    # Effects that still need source inspection are labelled as such.
    flagged = [
        item for item in review["series_consequences"]
        if item["status"] == "inspection_recommended"
    ]
    assert [item["series_node_id"] for item in flagged] == ["inst_orders"]
    # The review is a working proposal, not acceptance.
    assert review["authority"] == "working_revision_review_not_acceptance"
