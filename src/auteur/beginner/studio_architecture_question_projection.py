"""Read-only projection of the working Architecture's open questions: continuing identities, their recorded
formulations and the Working Book decisions that refer to them.

Nothing here stores or decides anything. Each fact is read from the owner that holds it: the applied revision chain and
each version from ``studio_architecture``, identity and wording rules from ``studio_architecture_questions``, and each
Book's references from the Working Book owner (``auteur.series.working_book_architecture``).

Four things stay apart, as in the owners: identity (the continuing problem), version (the exact wording at one applied
revision), semantic continuity (never decided here: a changed wording is shown beside its recorded reason, for the author
to judge) and authority (a removed question is ``no_longer_open``, never answered).

History is presented as recorded. Consecutive versions with the same recorded state form one span, and the span keeps
every version it covers. A version that cannot be read stays in the list as an ``unreadable`` span, and every such gap is
named in ``history``. A reason for a change is shown only when the revision's own request records it (the author's
instruction, or the inquiry alternative the author chose). No reason is ever inferred from wording.
"""
from __future__ import annotations

import json
from typing import Any

from auteur.beginner.studio_architecture import _candidate, _root, architecture_revision_chain, architecture_versions
from auteur.beginner.studio_architecture_questions import text_digest
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import load_host_agent_request
from auteur.series.working_book_architecture import book_numbers, book_series_references

SCHEMA = "studio-architecture-questions/1"
AUTHORITY = "read_only_owner_records"
# The Book owner's reference states under which a decision's question can still be asked about.
ANCHORABLE_STATES = ("current_wording", "moved", "reworded", "moved_and_reworded")
CHANGE_WITH_REASON = ("introduced", "moved", "reworded", "moved_and_reworded", "removed")


def _ids(candidate: dict | None) -> list[str] | None:
    if candidate is None:
        return None
    ids = candidate.get("open_question_ids")
    return list(ids) if isinstance(ids, list) else None


def _reason(store: CanvasStore, request_sha256: str) -> dict[str, Any]:
    """What one applied version's own request records as its reason: the author's instruction and any inquiry
    alternative the author chose. Nothing is inferred from wording; an unreadable request says so."""
    try:
        request = load_host_agent_request(_root(store) / "requests" / request_sha256 / "request.json")
        submitted = json.loads(request.user)
    except (OSError, ValueError, TypeError, AttributeError):
        return {"readable": False, "instruction": None, "selected_alternative": None}
    instruction = str(submitted.get("revision_instruction") or "").strip() or None
    alternative = submitted.get("selected_creative_alternative")
    chosen = None
    if isinstance(alternative, dict):
        chosen = {
            "title": alternative.get("title"),
            "description": alternative.get("description"),
            "hypothesis_id": alternative.get("hypothesis_id"),
            "inquiry_request_sha256": alternative.get("inquiry_request_sha256"),
        }
    return {"readable": True, "instruction": instruction, "selected_alternative": chosen}


def _state(row: dict, identifier: str) -> tuple[str, tuple[int, str] | None]:
    """One identity's standing in one version: present at an index with wording, absent, no identity recorded
    (a legacy version), or unreadable."""
    if not row["readable"]:
        return "unreadable", None
    ids = row["ids"]
    if ids is None:
        return "no_identity", None
    if identifier in ids:
        index = ids.index(identifier)
        questions = row["candidate"].get("open_questions") or []
        return "present", (index, questions[index] if index < len(questions) else "")
    return "absent", None


def _version(row: dict) -> dict[str, Any]:
    return {"request_sha256": row["request_sha256"], "revision_number": row["revision_number"]}


def _change(previous: dict | None, span: dict, first_in_chain: bool, chain_complete: bool) -> str | None:
    """What changed at the start of a span, judged only against the span before it that was actually read."""
    if span["kind"] == "present":
        if previous is None:
            # Nothing earlier is readable. The first version of a complete chain is the introduction; otherwise the
            # earlier history is not known, so the introduction is not claimed.
            return "introduced" if first_in_chain and chain_complete else "unverified"
        if previous["kind"] == "no_identity":
            return "introduced"
        if previous["kind"] == "present":
            before, after = previous["_detail"], span["_detail"]
            if before[1] == after[1]:
                return "moved"
            if before[0] == after[0]:
                return "reworded"
            return "moved_and_reworded"
        return "unverified"
    if span["kind"] == "absent" and previous is not None and previous["kind"] == "present":
        return "removed"
    return None


def _spans(rows: list[dict], identifier: str, chain_complete: bool, reasons: dict[str, dict]) -> list[dict[str, Any]]:
    """Consecutive versions with one recorded state, oldest first. Each span keeps every version it covers."""
    spans: list[dict[str, Any]] = []
    for row in rows:
        kind, detail = _state(row, identifier)
        last = spans[-1] if spans else None
        if last is not None and kind != "unreadable" and last["kind"] == kind and last["_detail"] == detail:
            last["versions"].append(_version(row))
            last["to_revision"] = row["revision_number"]
            continue
        spans.append({"kind": kind, "_detail": detail, "versions": [_version(row)],
                      "from_revision": row["revision_number"], "to_revision": row["revision_number"],
                      "index": detail[0] if detail else None, "text": detail[1] if detail else None,
                      "text_sha256": text_digest(detail[1]) if detail else None,
                      "change": None, "previous": None, "reason": None})
    previous = None
    for position, span in enumerate(spans):
        span["change"] = _change(previous, span, position == 0, chain_complete)
        if span["change"] in ("moved", "reworded", "moved_and_reworded", "removed"):
            span["previous"] = {"index": previous["_detail"][0], "text": previous["_detail"][1]}
        if span["change"] in CHANGE_WITH_REASON:
            span["reason"] = reasons.get(span["versions"][0]["request_sha256"])
        previous = span
    for span in spans:
        del span["_detail"]
    return spans


def _history(spans: list[dict], chain_complete: bool) -> dict[str, Any]:
    present = [position for position, span in enumerate(spans) if span["kind"] == "present"]
    first = present[0] if present else None
    before = spans[:first] if first is not None else spans
    within = spans[first:] if first is not None else []
    gaps: list[str] = []
    if not chain_complete:
        gaps.append("chain_incomplete")
    if any(span["kind"] == "unreadable" for span in before):
        gaps.append("unreadable_before_first_recorded")
    if any(span["kind"] == "unreadable" for span in within):
        gaps.append("unreadable_within")
    return {
        "complete": not gaps,
        "gaps": gaps,
        "first_recorded_in": spans[first]["versions"][0] if first is not None else None,
        "introduced_in_recorded_history": bool(first is not None and spans[first]["change"] == "introduced"),
        "legacy_versions_before": sum(len(span["versions"]) for span in before if span["kind"] == "no_identity"),
        "unreadable_versions": sum(len(span["versions"]) for span in spans if span["kind"] == "unreadable"),
    }


def _book_entry(book: dict, ref: dict, revision_of: dict[str, int | None]) -> dict[str, Any]:
    version = ref.get("version_request_sha256")
    return {
        "book_number": book["book_number"],
        "title": book["title"],
        "freshness": book["freshness"],
        "book_request_sha256": book.get("request_sha256"),
        "decision_id": ref["decision_id"],
        "decision_text": ref.get("decision_text"),
        # False when the decision names no identity itself: its identity is then the one the version it names carries at
        # the decision's position, which the owner resolves exactly (index and digest), never by wording.
        "records_identity": bool(ref.get("decision_records_identity")),
        "state": ref["state"],
        "question_id": ref.get("question_id"),
        "anchorable": ref["state"] in ANCHORABLE_STATES,
        "recorded": {
            "index": ref.get("recorded_index"),
            "text": ref.get("recorded_text"),
            "version_request_sha256": version,
            "revision_number": revision_of.get(version),
        },
        "current": ({"index": ref.get("current_index"), "text": ref.get("current_text")}
                    if ref.get("current_index") is not None else None),
    }


def _wording_only_item(index: int, text: str, rows: list[dict]) -> dict[str, Any]:
    legacy = sum(1 for row in rows if row["readable"] and row["ids"] is None)
    unreadable = sum(1 for row in rows if not row["readable"])
    gaps = ["no_identity"] + (["unreadable_within"] if unreadable else [])
    return {"id": None, "standing": "wording_only", "index": index, "text": text, "text_sha256": text_digest(text),
            "spans": [], "books": [],
            "history": {"complete": False, "gaps": gaps, "first_recorded_in": None,
                        "introduced_in_recorded_history": False, "legacy_versions_before": legacy,
                        "unreadable_versions": unreadable}}


def project_architecture_questions(store: CanvasStore) -> dict[str, Any]:
    """The working Architecture's open questions as recorded: continuing ones, legacy wording, and those no longer open,
    with the Book decisions that refer to each. Read-only. A damaged version or Book is reported, not raised."""
    current = _candidate(store)
    if current is None:
        return {"schema": SCHEMA, "authority": AUTHORITY, "canvas_id": store.canvas_id, "available": False,
                "current": None, "history": None, "questions": [], "no_longer_open": [],
                "books": {"unreadable": [], "wording_only_references": [], "unattributed_references": []}}
    chain = architecture_revision_chain(store)
    versions = list(architecture_versions(store, requests=chain["requests"]))
    numbered = bool(chain["complete"])
    rows = []
    for position, (sha, candidate) in enumerate(reversed(versions)):
        rows.append({"request_sha256": sha, "revision_number": position + 1 if numbered else None,
                     "readable": candidate is not None, "candidate": candidate, "ids": _ids(candidate)})
    reasons = {row["request_sha256"]: _reason(store, row["request_sha256"]) for row in rows}
    revision_of = {row["request_sha256"]: row["revision_number"] for row in rows}
    newest = rows[-1]
    current_ids = newest["ids"]
    current_questions = list(newest["candidate"].get("open_questions") or [])

    # Book references, read through the Working Book owner and joined only by a recorded identity.
    by_identity: dict[str, list[dict]] = {}
    wording_only: list[dict] = []
    unattributed: list[dict] = []
    unreadable_books: list[dict] = []
    for number in book_numbers(store):
        try:
            view = book_series_references(store, number, versions=versions)
        except Exception as exc:  # noqa: BLE001 - one Book's damage stays with that Book
            unreadable_books.append({"book_number": number, "reason": type(exc).__name__})
            continue
        book = {"book_number": number, "title": view["title"], "freshness": view["freshness"],
                "request_sha256": view["request_sha256"]}
        for ref in view["question_references"]:
            entry = _book_entry(book, ref, revision_of)
            if ref.get("question_id"):
                by_identity.setdefault(ref["question_id"], []).append(entry)
            elif ref["state"] == "identity_not_established":
                wording_only.append(entry)
            else:
                unattributed.append(entry)

    questions: list[dict[str, Any]] = []
    for index, text in enumerate(current_questions):
        identifier = current_ids[index] if current_ids is not None else None
        if identifier is None:
            questions.append(_wording_only_item(index, text, rows))
            continue
        spans = _spans(rows, identifier, chain["complete"], reasons)
        questions.append({"id": identifier, "standing": "continuing", "index": index, "text": text,
                          "text_sha256": text_digest(text), "spans": spans,
                          "history": _history(spans, chain["complete"]),
                          "books": by_identity.get(identifier, [])})

    # Identities recorded in an earlier version and absent now, most recently present first. Never shown as answered.
    current_identities = set(current_ids or [])
    absent: list[str] = []
    for row in reversed(rows):
        for identifier in row["ids"] or []:
            if identifier not in current_identities and identifier not in absent:
                absent.append(identifier)
    no_longer_open: list[dict[str, Any]] = []
    for identifier in absent:
        spans = _spans(rows, identifier, chain["complete"], reasons)
        last = [span for span in spans if span["kind"] == "present"][-1]
        no_longer_open.append({"id": identifier, "standing": "no_longer_open", "index": last["index"],
                               "text": last["text"], "text_sha256": last["text_sha256"], "spans": spans,
                               "history": _history(spans, chain["complete"]),
                               "books": by_identity.get(identifier, [])})

    unreadable_count = sum(1 for row in rows if not row["readable"])
    return {
        "schema": SCHEMA,
        "authority": AUTHORITY,
        "canvas_id": store.canvas_id,
        "available": True,
        "current": {
            "request_sha256": newest["request_sha256"],
            "revision_number": newest["revision_number"],
            "revision_count": len(rows),
            "numbered": numbered,
        },
        "history": {
            "chain_complete": bool(chain["complete"]),
            "versions_read": len(rows) - unreadable_count,
            "unreadable_versions": unreadable_count,
        },
        "questions": questions,
        "no_longer_open": no_longer_open,
        "books": {
            "unreadable": unreadable_books,
            "wording_only_references": wording_only,
            "unattributed_references": unattributed,
        },
    }
