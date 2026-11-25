"""Persistent identity for the working Architecture's open questions: pure rules, no persistence.

The Narrative Architecture owner (``studio_architecture``) stores and applies candidates; this module decides what a
question identity may and may not mean. It never reads a store, never infers identity from wording, and never
rewrites history.

Four things are kept distinct:

* identity: the continuing creative problem, declared by the coding agent in ``open_question_ids`` and validated here;
* version: the exact recorded wording of that question at one applied version (``text`` and ``text_sha256``);
* semantic continuity: whether a later wording still asks the same problem. Not decided here: a changed wording stays
  ``reworded`` in the review, for the author to judge;
* authority: nothing here settles a question. Removal is recorded as ``removed``, never as answered.

Legacy candidates (``open_question_ids`` absent) have no identities. A later version may introduce identities for its
questions; those begin at that version and no earlier history is claimed for them.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Iterable

QUESTION_ID_PATTERN = r"^q-[a-z0-9][a-z0-9_-]{0,60}$"
_QUESTION_ID = re.compile(QUESTION_ID_PATTERN)


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ids(candidate: dict | None) -> list[str] | None:
    if not candidate:
        return None
    ids = candidate.get("open_question_ids")
    return list(ids) if isinstance(ids, list) else None


def identity_problems(
    proposal: dict,
    prior: dict | None,
    history: Iterable[dict | None],
) -> list[str]:
    """Reasons a proposed version's question identities cannot be accepted. Empty when they can.

    ``prior`` is the immediately preceding applied version (None for the first). ``history`` holds every earlier
    version's candidate, ``None`` where a record cannot be read. A new identity must not already belong to any
    earlier version, because removing a question does not free its identity for another question.
    """
    problems: list[str] = []
    ids = _ids(proposal)
    questions = proposal.get("open_questions") or []
    prior_ids = _ids(prior) or []
    if ids is None:
        if prior_ids:
            problems.append(
                "the earlier open questions have identities; keep open_question_ids so each question that "
                "continues keeps its identity"
            )
        return problems
    if len(ids) != len(questions):
        problems.append("open_question_ids must list one id for each open question, in the same order")
    for identifier in ids:
        if not isinstance(identifier, str) or not _QUESTION_ID.fullmatch(identifier):
            problems.append(f"{identifier!r} is not a valid open question id")
    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    if duplicates:
        problems.append("an open question id is used more than once: " + ", ".join(duplicates))
    prior_set = set(prior_ids)
    introduced = [identifier for identifier in ids if identifier not in prior_set]
    if introduced:
        history = list(history)
        if any(entry is None for entry in history) and introduced:
            problems.append(
                "an earlier version cannot be read, so its identities cannot be checked before new ids are "
                "introduced: " + ", ".join(introduced)
            )
        seen: set[str] = set()
        for entry in history:
            seen.update(_ids(entry) or [])
        reused = sorted(identifier for identifier in introduced if identifier in seen)
        if reused:
            problems.append(
                "an identity already used by an earlier version cannot name a different question: "
                + ", ".join(reused)
            )
    return problems


def question_changes(prior: dict | None, proposed: dict) -> dict:
    """What changed among the open questions, for review. Only observable differences are reported.

    Statuses per question present in the proposal: ``introduced`` (no identity earlier), ``unchanged``,
    ``moved`` (same wording at another position), ``reworded`` (same position, new wording),
    ``moved_and_reworded``. Earlier questions missing from the proposal are ``removed``; a removal is never presented
    as an answer.
    """
    prior_questions = list((prior or {}).get("open_questions") or [])
    prior_ids = _ids(prior) or []
    proposed_questions = list(proposed.get("open_questions") or [])
    proposed_ids = _ids(proposed)
    identity_introduced = proposed_ids is not None and not prior_ids
    rows: list[dict[str, Any]] = []
    if proposed_ids is None:
        for index, text in enumerate(proposed_questions):
            rows.append({"id": None, "index": index, "text": text, "status": "no_identity"})
        return {"identity_introduced": False, "questions": rows, "removed": []}
    for index, (identifier, text) in enumerate(zip(proposed_ids, proposed_questions)):
        if identifier in prior_ids:
            previous = prior_ids.index(identifier)
            before = prior_questions[previous]
            if before == text and previous == index:
                status = "unchanged"
            elif before == text:
                status = "moved"
            elif previous == index:
                status = "reworded"
            else:
                status = "moved_and_reworded"
            rows.append({"id": identifier, "index": index, "text": text, "status": status,
                         "previous_index": previous, "previous_text": before})
        else:
            rows.append({"id": identifier, "index": index, "text": text, "status": "introduced"})
    removed = [
        {"id": identifier, "previous_index": index, "previous_text": prior_questions[index]}
        for index, identifier in enumerate(prior_ids)
        if identifier not in proposed_ids
    ]
    return {"identity_introduced": identity_introduced, "questions": rows, "removed": removed}


def question_history(versions: Iterable[tuple[str, dict | None]]) -> dict[str, list[dict[str, Any]]]:
    """Each identity's recorded versions, oldest first, from applied versions given newest first.

    ``versions`` yields ``(request_sha256, candidate)``; unreadable versions contribute nothing and are not guessed
    at. Identical wording under different identities is never merged.
    """
    ordered = list(versions)[::-1]
    history: dict[str, list[dict[str, Any]]] = {}
    for sha, candidate in ordered:
        ids = _ids(candidate)
        if candidate is None or ids is None:
            continue
        for index, (identifier, text) in enumerate(zip(ids, candidate.get("open_questions") or [])):
            history.setdefault(identifier, []).append({
                "request_sha256": sha, "index": index, "text": text, "text_sha256": text_digest(text),
            })
    return history


def relate_to_current(identifier: str | None, recorded: dict, current: dict | None) -> dict[str, Any]:
    """How a recorded question version relates to the current Architecture. Identity is never inferred from wording.

    ``recorded`` is ``{"index", "text"}`` as the version stored it. Without an identifier the reference stays a
    recorded wording reference: nothing here says it is the same question as anything current.
    """
    if not identifier:
        return {"status": "identity_not_established", "current_index": None, "current_text": None}
    ids = _ids(current) or []
    questions = (current or {}).get("open_questions") or []
    if identifier not in ids:
        return {"status": "removed", "current_index": None, "current_text": None}
    index = ids.index(identifier)
    text = questions[index]
    if text == recorded["text"] and index == recorded["index"]:
        status = "current_wording"
    elif text == recorded["text"]:
        status = "moved"
    elif index == recorded["index"]:
        status = "reworded"
    else:
        status = "moved_and_reworded"
    return {"status": status, "current_index": index, "current_text": text}
