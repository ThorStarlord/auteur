"""Bounded, labelled history of two or three open questions, for one cross-question inquiry.

Narrative deliberation asks a coding agent to relate continuing creative problems. It is given what the owners recorded
about each question, and nothing the owners did not record. This module is read-only: every fact comes from an owner
read (the question projection for the Architecture's recorded versions, reasons and Book decisions), and this module
decides only what an inquiry is given, how much of it, and what basis each item carries. It never changes a record,
never judges two questions related, and never decides a question is settled.

Each item names exactly one basis (see ``BASIS_LEGEND``), so the agent can keep what is recorded, what is a historical
interpretation, and what is a live proposal apart. The packet is frozen into the inquiry request; its digest is kept so
the packet a prepared inquiry was asked with can be inspected later, even after the record has moved on.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from auteur.series.working_book_architecture import book_series_references

from .studio_architecture_question_projection import project_architecture_questions
from .studio_architecture_questions import text_digest
from .studio_store import CanvasStore

SCHEMA = "studio-question-deliberation/1"
MAX_QUESTIONS = 3
# Per question: the first recorded item, then the most recent ones, so the agent sees how the problem was first put and
# how it has moved since. Items between them are counted, not inlined.
MAX_HISTORY_ITEMS = 4
MAX_BOOK_DECISIONS = 4
TEXT_LIMIT = 600
REASON_LIMIT = 400

BASIS_LEGEND = {
    "current_wording": "The working Architecture's wording of the question now.",
    "recorded_wording": "A formulation one applied version recorded, with no change claimed for it.",
    "recorded_change": "A change in recorded wording, judged only against the readable version before it.",
    "recorded_absence": "A readable applied version in which the question was not recorded.",
    "recorded_reason": "The author's own revision instruction for that version. It says what was asked, not that the "
                       "consequence was achieved.",
    "recorded_selected_alternative": "An alternative a coding agent proposed earlier and the author chose. It is a "
                                     "historical interpretation.",
    "book_decision": "A Working Book decision that refers to the question. It is a noncanonical working proposal; "
                     "identity_basis says whether the decision names the question itself or the Book owner resolved it "
                     "from the version the decision names.",
    "recorded_co_reference": "Two or more selected questions are referred to by one Book. This is a recorded reference, "
                             "not a relationship in the story.",
    "named_gap": "History or a Book that could not be read, or is incomplete. It must not be filled in.",
}

GAP_NOTES = {
    "chain_incomplete": "The revision history cannot be read whole, so no earlier version is numbered and no change "
                        "across an unread stretch is claimed.",
    "unreadable_before_first_recorded": "A version before this question's first recorded appearance cannot be read, so "
                                        "the question may have been recorded earlier.",
    "unreadable_within": "A version between recorded appearances cannot be read, so no change across it is claimed.",
}

NOTE = ("These items are the recorded history of the selected open questions, read through the owners. Identity "
        "continuity is what the Architecture recorded; it does not establish that two wordings are semantically the same. "
        "Nothing here settles a question or states a story relationship.")


def _clip(text: Any, limit: int = TEXT_LIMIT) -> str | None:
    if text is None:
        return None
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _reason_item(reason: dict | None) -> dict[str, Any] | None:
    if not reason:
        return None
    if not reason.get("readable"):
        return {"basis": "named_gap", "note": "The revision's request cannot be read, so its reason is not shown."}
    instruction = reason.get("instruction")
    chosen = reason.get("selected_alternative")
    item: dict[str, Any] = {
        "basis": "recorded_reason", "authority": "author_instruction_recorded",
        "instruction": _clip(instruction, REASON_LIMIT) if instruction else None,
        "instruction_sha256": text_digest(instruction) if instruction else None,
    }
    if chosen:
        item["selected_alternative"] = {
            "basis": "recorded_selected_alternative",
            "authority": "historical_agent_interpretation_selected_by_author",
            "hypothesis_id": chosen.get("hypothesis_id"),
            "title": _clip(chosen.get("title"), 200),
            "description": _clip(chosen.get("description"), REASON_LIMIT),
            "inquiry_request_sha256": chosen.get("inquiry_request_sha256"),
        }
    if not instruction and not chosen:
        item["note"] = "The record gives no reason for this change."
    return item


def _history_item(span: dict[str, Any]) -> dict[str, Any]:
    kind, change = span["kind"], span.get("change")
    if kind == "unreadable":
        basis = "named_gap"
    elif kind == "absent":
        basis = "recorded_absence"
    elif change == "unverified":
        # The wording is recorded; only the change across an unreadable version is not claimed.
        basis = "recorded_wording"
    elif change:
        basis = "recorded_change"
    else:
        basis = "recorded_wording"
    versions = span["versions"]
    item: dict[str, Any] = {
        "basis": basis,
        "authority": "historical_recorded" if basis in ("recorded_wording", "recorded_change", "recorded_absence") else
                     "unverified",
        "kind": kind,
        "change": change,
        "from_revision": span.get("from_revision"),
        "to_revision": span.get("to_revision"),
        "versions": len(versions),
        "request_sha256": versions[0]["request_sha256"],
        "index": span.get("index"),
        "text": _clip(span.get("text")),
        "text_sha256": span.get("text_sha256"),
    }
    if change == "unverified":
        item["note"] = ("The version before it cannot be read, so whether the wording changed is not shown.")
    if span.get("previous"):
        item["previous"] = {"index": span["previous"]["index"], "text": _clip(span["previous"]["text"])}
    if change in ("introduced", "moved", "reworded", "moved_and_reworded", "removed"):
        item["reason"] = _reason_item(span.get("reason"))
    return item


def _history_for(question: dict[str, Any]) -> tuple[list[dict], int]:
    """The question's recorded items, bounded: its introduction first, then the most recent items. Versions that name no
    identity are not formulations of this question, so they are stated as a count, never inlined."""
    spans = question["spans"]
    first_present = next((span for span in spans if span["kind"] == "present"), None)
    relevant = [span for span in spans if span["kind"] in ("present", "absent", "unreadable")
                and (span["kind"] != "present" or span.get("change") or span is first_present)]
    if len(relevant) > MAX_HISTORY_ITEMS:
        # The introduction, then the most recent items, kept in the order they were recorded.
        others = [span for span in relevant if span is not first_present]
        recent = others[-(MAX_HISTORY_ITEMS - (1 if first_present is not None else 0)):]
        kept = [span for span in relevant if span is first_present or any(span is r for r in recent)]
    else:
        kept = relevant
    items = [_history_item(span) for span in kept]
    legacy = question["history"]["legacy_versions_before"]
    if legacy:
        items.insert(0, {"basis": "named_gap", "gap": "no_identity_before", "versions": legacy,
                         "note": "Earlier revisions recorded no identities. No earlier wording is attached to this "
                                 "question, so it cannot be followed back before its identity was recorded."})
    for gap in question["history"]["gaps"]:
        items.append({"basis": "named_gap", "gap": gap, "note": GAP_NOTES[gap]})
    return items, len(relevant) - len(kept)


def _book_item(entry: dict[str, Any]) -> dict[str, Any]:
    decision = entry.get("decision_text")
    recorded, current = entry["recorded"], entry.get("current")
    return {
        "basis": "book_decision",
        "authority": "working_book_proposal_noncanonical",
        "book_number": entry["book_number"],
        "title": entry["title"],
        "decision_id": entry["decision_id"],
        "decision_text": _clip(decision),
        "decision_text_sha256": text_digest(decision or ""),
        "book_request_sha256": entry.get("book_request_sha256"),
        "state": entry["state"],
        "identity_basis": ("recorded_by_decision" if entry["records_identity"]
                           else "resolved_by_owner_from_recorded_version"),
        "recorded": {"index": recorded.get("index"), "text": _clip(recorded.get("text")),
                     "revision_number": recorded.get("revision_number"),
                     "version_request_sha256": recorded.get("version_request_sha256")},
        "current": ({"index": current.get("index"), "text": _clip(current.get("text"))} if current else None),
    }


def build_question_deliberation(store: CanvasStore, question_ids: list[str]) -> dict[str, Any]:
    """The bounded, labelled packet for two or three continuing questions. Read-only; raises ValueError if the
    selection is not two or three distinct continuing questions of the current working Architecture."""
    distinct = list(dict.fromkeys(question_ids))
    if not 2 <= len(distinct) <= MAX_QUESTIONS:
        raise ValueError(f"compare two or three open questions; {len(distinct)} were selected")
    view = project_architecture_questions(store)
    if not view["available"]:
        raise ValueError("no current working architecture")
    by_id = {question["id"]: question for question in view["questions"]}
    selected = []
    for identifier in distinct:
        question = by_id.get(identifier)
        if question is None:
            raise ValueError(f"question {identifier} is not a continuing open question of the current working architecture")
        selected.append(question)

    omitted: dict[str, dict[str, int]] = {}
    questions = []
    for question in selected:
        history, omitted_history = _history_for(question)
        books_all = sorted(question["books"], key=lambda entry: (entry["book_number"], entry["decision_id"]))
        books = [_book_item(entry) for entry in books_all[:MAX_BOOK_DECISIONS]]
        omitted[question["id"]] = {"history_items": omitted_history,
                                   "book_decisions": max(0, len(books_all) - MAX_BOOK_DECISIONS)}
        questions.append({
            "id": question["id"],
            "index": question["index"],
            "current": {"basis": "current_wording", "authority": "working_noncanonical",
                        "index": question["index"], "text": _clip(question["text"]),
                        "text_sha256": question["text_sha256"]},
            "history_complete": bool(question["history"]["complete"]),
            "history": history,
            "books": books,
        })

    # Working Books that refer to two or more selected questions. Counted over every decision, not only the shown ones.
    co_reference: dict[int, dict[str, Any]] = {}
    for question in selected:
        for entry in question["books"]:
            row = co_reference.setdefault(entry["book_number"], {"title": entry["title"], "questions": set(),
                                                                 "decisions": []})
            row["questions"].add(question["id"])
            row["decisions"].append(entry["decision_id"])
    co_references = [
        {"basis": "recorded_co_reference", "authority": "recorded_reference", "book_number": number,
         "title": row["title"], "question_ids": sorted(row["questions"]), "decision_ids": sorted(row["decisions"]),
         "note": "This Book records decisions about these questions. It does not say they are related in the story."}
        for number, row in sorted(co_reference.items()) if len(row["questions"]) >= 2
    ]

    named_gaps = []
    if view["books"]["unreadable"]:
        named_gaps.append({"basis": "named_gap", "books_unreadable": [row["book_number"] for row in view["books"]["unreadable"]],
                           "note": "These Working Books cannot be read, so any reference they make to these questions "
                                   "is not shown."})
    if not view["history"]["chain_complete"]:
        named_gaps.append({"basis": "named_gap", "gap": "chain_incomplete", "note": GAP_NOTES["chain_incomplete"]})

    packet: dict[str, Any] = {
        "schema": SCHEMA,
        "authority": "recorded_history_noncanonical",
        "note": NOTE,
        "basis_legend": BASIS_LEGEND,
        "current_architecture": {
            "request_sha256": view["current"]["request_sha256"],
            "revision_number": view["current"]["revision_number"],
            "revision_count": view["current"]["revision_count"],
            "numbered": view["current"]["numbered"],
            "history_chain_complete": view["history"]["chain_complete"],
        },
        "questions": questions,
        "co_references": co_references,
        "named_gaps": named_gaps,
        "limits": {
            "questions": MAX_QUESTIONS,
            "history_items_per_question": MAX_HISTORY_ITEMS,
            "book_decisions_per_question": MAX_BOOK_DECISIONS,
            "text_characters": TEXT_LIMIT,
            "reason_characters": REASON_LIMIT,
            "omitted": omitted,
        },
    }
    packet["evidence_sha256"] = _digest(packet)
    return packet


def deliberation_standing(store: CanvasStore, packet: dict[str, Any]) -> list[dict[str, Any]]:
    """Each Book decision in a packet as its owner reads it when the answer is completed, against what the inquiry was asked with.

    ``current``: the same decision in the same Book revision. ``book_revised``: the Book has been revised since, but this
    decision reads as it did. ``decision_changed`` / ``decision_gone``: the decision itself is no longer what it was.
    ``unreadable``: the Book cannot be read. The answer stays historical; nothing here marks it stale.
    """
    standing = []
    for question in packet["questions"]:
        for book in question["books"]:
            row = {"book_number": book["book_number"], "decision_id": book["decision_id"],
                   "question_id": question["id"]}
            try:
                live = book_series_references(store, book["book_number"])
            except Exception:  # noqa: BLE001 - one Book's damage is reported for that Book only
                standing.append({**row, "standing": "unreadable"})
                continue
            reference = next((ref for ref in live["question_references"]
                              if ref["decision_id"] == book["decision_id"]), None)
            if reference is None:
                value = "decision_gone"
            elif text_digest(reference["decision_text"] or "") != book["decision_text_sha256"]:
                value = "decision_changed"
            elif live["request_sha256"] != book["book_request_sha256"]:
                value = "book_revised"
            else:
                value = "current"
            standing.append({**row, "standing": value})
    return standing
