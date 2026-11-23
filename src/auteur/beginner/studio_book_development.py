"""Studio adapter for developing one working Book architecture through its own owner.

The Working Book Architecture owner (`auteur.series.working_book_architecture`) keeps the records and the
whole revision lifecycle: prepare, host-agent completion, review, explicit apply, lineage and every
stale, superseded and unexpected-change guard. This module only exposes that lifecycle to the Studio:

* a read projection that says which step the Book is at, in the owner's own terms;
* prepare, which adds two author-facing guards before the owner's prepare: the Book must still be the
  revision the author was reading, and a request still waiting is replaced only when the author says so;
* host-agent completion and apply, passed straight to the owner, which revalidates at the write.

Nothing here writes a Book record itself, decides applicability, accepts canon, or touches the working
Narrative Architecture, the Series plan or the Directions. The browser never calls a model.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_store import CanvasStore
from auteur.series.working_book_architecture import (
    book_apply_review,
    book_complete,
    book_elements,
    book_pending_state,
    book_prepare,
    book_project,
    book_review_elements,
    book_revision_scope,
    book_series_references,
)

SCHEMA = "studio-book-development/1"
OWNER_MODULE = "auteur.series.working_book_architecture"
_SHA = re.compile(r"[0-9a-f]{64}")


def book_number_from_path(raw: str) -> int:
    if not raw.isdigit() or not 1 <= int(raw) <= 60:
        raise ValueError("book number must be an integer from 1 to 60")
    return int(raw)


def _store(project_root: Path, canvas_id: str) -> CanvasStore:
    store = CanvasStore(project_root, canvas_id)
    store.load()  # FileNotFoundError: the route answers 404
    return store


def _handoff(project_root: Path, canvas_id: str, book_number: int) -> dict:
    base = f'python -m {OWNER_MODULE} --project "{Path(project_root).resolve()}" --canvas {canvas_id}'
    return {
        "show": f"{base} book-show --book {book_number}",
        "complete": f"{base} book-complete-file --book {book_number} --candidate <revised-book.json>",
        "resume": f"{base} book-resume --book {book_number}",
        "guide": "docs/agents/studio-architecture-bridge.md#working-book-revision-withdrawal-and-apply",
        "note": ("The coding agent reads the pending request with book-show, writes the complete revised Book "
                 "as one JSON object, and submits it with book-complete-file. Submitting stores a review; it "
                 "never changes the working Book. Only Apply, after you review it, does."),
    }


def _phase(owner: dict, pending: dict | None) -> str:
    if pending is None:
        return "none"
    if pending["book_changed"] or pending["context_changed"]:
        return "stale"
    if owner["status"] == "review_ready":
        return "review_ready"
    if owner["status"] == "review_blocked":
        return "review_blocked"
    return "awaiting_coding_agent"


def project_book_development(project_root: Path, canvas_id: str, book_number: int) -> dict:
    """Read-only: one Book's working record, its elements, and where its revision lifecycle stands."""
    store = _store(project_root, canvas_id)
    out: dict[str, Any] = {
        "schema": SCHEMA, "authority": "working_noncanonical", "canvas_id": canvas_id,
        "book_number": book_number, "owner": OWNER_MODULE,
    }
    try:
        owner = book_project(store, book_number)
        pending = book_pending_state(store, book_number)["pending"]
        refs = book_series_references(store, book_number)
        elements = book_elements(store, book_number)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        # A damaged record is reported for this Book alone; nothing from it is shown or offered.
        out.update({"state": "unreadable", "reason": f"{type(exc).__name__}: {exc}"[:300]})
        return out
    if refs.get("status") == "not_started":
        out.update({"state": "no_book", "phase": _phase(owner, pending), "pending": pending,
                    "handoff": _handoff(project_root, canvas_id, book_number) if pending else None,
                    "request": owner.get("request")})
        return out
    phase = _phase(owner, pending)
    out.update({
        "state": "working",
        "book": {key: refs[key] for key in (
            "title", "question", "pressure", "freshness", "series_changed", "source_changed", "semantic_impact",
            "request_sha256", "series_request_sha256", "content_sha256", "revision_number",
            "open_author_decisions", "last_applied")},
        "elements": elements,
        "phase": phase,
        "pending": pending,
        "review": owner.get("review") if pending is not None else None,
        # The reviewed candidate's own elements, so the review can show what each change says.
        "review_elements": book_review_elements(store, book_number) if pending is not None and owner.get("review") else None,
        "request": owner.get("request") if phase in ("awaiting_coding_agent", "stale") else None,
        "handoff": _handoff(project_root, canvas_id, book_number) if pending is not None else None,
    })
    return out


def _string_list(value: Any, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{name} must be a list of element ids")
    return tuple(value)


def preview_book_scope(project_root: Path, canvas_id: str, book_number: int, payload: dict) -> dict:
    """Read-only: the elements a targeted revision of these targets would permit (the owner's own rule)."""
    store = _store(project_root, canvas_id)
    return book_revision_scope(store, book_number, _string_list(payload.get("targets"), "targets"))


def prepare_book_revision(project_root: Path, canvas_id: str, book_number: int, payload: dict) -> dict:
    """Prepare a reviewed revision through the owner. Calls no model; changes no working Book."""
    store = _store(project_root, canvas_id)
    instruction = payload.get("instruction")
    if not isinstance(instruction, str):
        raise ValueError("instruction must be a string")
    targets = _string_list(payload.get("targets"), "targets")
    holistic = payload.get("holistic", False)
    if not isinstance(holistic, bool):
        raise ValueError("holistic must be true or false")
    expected = payload.get("expected_book_request_sha256")
    if not isinstance(expected, str) or not _SHA.fullmatch(expected):
        raise ValueError("expected_book_request_sha256 must name the Book revision you were reading")
    refs = book_series_references(store, book_number)
    if refs.get("status") == "not_started":
        raise ValueError(f"Book {book_number} has no working architecture to revise")
    if refs["request_sha256"] != expected:
        raise BeginnerConcurrencyError(
            f"the working Book {book_number} changed since you read it (it is now revision "
            f"{refs['revision_number']}); read it again before preparing a revision"
        )
    pending = book_pending_state(store, book_number)["pending"]
    if pending is not None and payload.get("replace_pending_request_sha256") != pending["request_sha256"]:
        raise BeginnerConcurrencyError(
            "another Book request is still waiting for review or for the coding agent; "
            "confirm that this request replaces it"
        )
    book_prepare(store, book_number, instruction=instruction, targets=targets, holistic=holistic)
    return project_book_development(project_root, canvas_id, book_number)


def complete_book_revision(project_root: Path, canvas_id: str, book_number: int, payload: dict) -> dict:
    """Manual fallback: validate a pasted HostAgentResponse through the owner. Stores a review only."""
    store = _store(project_root, canvas_id)
    if not isinstance(payload, dict):
        raise ValueError("the response must be one HostAgentResponse JSON object")
    try:
        book_complete(store, book_number, payload)
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error['loc']) or 'response'}: {error['msg']}"
            for error in exc.errors()[:6]
        )
        raise ValueError(f"the response does not match the Working Book contract: {details}") from None
    return project_book_development(project_root, canvas_id, book_number)


def apply_book_revision(project_root: Path, canvas_id: str, book_number: int, payload: dict) -> dict:
    """Apply exactly the reviewed request. The owner revalidates freshness and applicability at the write."""
    store = _store(project_root, canvas_id)
    sha = payload.get("request_sha256")
    if not isinstance(sha, str) or not _SHA.fullmatch(sha):
        raise ValueError("request_sha256 must be the 64-character identity of the review you read")
    result = book_apply_review(store, book_number, sha)
    return {"application": {"result": result["result"], "request_sha256": sha},
            **project_book_development(project_root, canvas_id, book_number)}
