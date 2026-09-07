"""Bounded, relevance-ranked context reconstruction for later Books."""
from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ContextItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    kind: Literal["character", "conflict", "promise", "relationship", "theme", "decision", "institution"]
    summary: str
    book_number: int = Field(ge=1)
    relevance: Literal["direct", "active", "recent", "requested"]
    why_included: str
    source_ref: str
    stale: bool = False


class SeriesContextSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_id: str
    target_book: int = Field(gt=1)
    items: list[ContextItem] = Field(default_factory=list)
    unresolved_promises: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"


def reconstruct_series_context(records: list[dict[str, object]], *, target_book: int, requested_ids: set[str] | None = None) -> SeriesContextSnapshot:
    requested_ids = requested_ids or set()
    selected: list[ContextItem] = []
    for record in records:
        item_id = str(record["item_id"])
        book_number = int(record.get("book_number", 1))
        dependencies = {str(item) for item in record.get("dependent_books", [])}
        status = str(record.get("status", "active"))
        if item_id in requested_ids:
            relevance, why = "requested", "explicitly requested by the author"
        elif target_book in dependencies:
            relevance, why = "direct", "directly affects the target Book"
        elif status in {"active", "open", "unresolved"}:
            relevance, why = "active", "remains unresolved or active"
        elif book_number >= target_book - 1:
            relevance, why = "recent", "comes from the immediately preceding Book"
        else:
            continue
        selected.append(ContextItem(
            item_id=item_id,
            kind=str(record["kind"]),
            summary=str(record["summary"]),
            book_number=book_number,
            relevance=relevance,
            why_included=why,
            source_ref=str(record.get("source_ref", item_id)),
            stale=bool(record.get("stale", False)),
        ))
    selected.sort(key=lambda item: ({"direct": 0, "active": 1, "requested": 2, "recent": 3}[item.relevance], item.item_id))
    unresolved = [item.item_id for item in selected if item.kind == "promise" and not item.stale]
    warnings = [f"{item.item_id} is stale." for item in selected if item.stale]
    payload = {"target_book": target_book, "items": [item.model_dump() for item in selected]}
    snapshot_id = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return SeriesContextSnapshot(snapshot_id=snapshot_id, target_book=target_book, items=selected, unresolved_promises=unresolved, warnings=warnings)
