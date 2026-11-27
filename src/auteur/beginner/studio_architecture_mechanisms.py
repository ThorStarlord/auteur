"""Version-qualified recorded mechanisms and Working Book inheritance evidence for a consequence analysis.

A consequence analysis may cite what the Architecture records, not only what changed. This module is pure: it takes the
baseline and proposed candidates, the applied revisions before the baseline, and the Working Book references and elements
the caller has read, and returns the bounded, provenance-qualified items the packet cites. It reads no store, writes nothing
and judges nothing about meaning.

Provenance is an identity fact, computed by comparing the recorded records: ``preserved`` (same identifier, identical record
on both sides), ``transformed`` (same identifier, the recorded content differs), ``removed``, ``introduced``, or ``historical``
(recorded in an earlier applied version and absent from both sides). A mechanism that keeps its identifier is not thereby
unchanged in function; a ``preserved`` record is only one whose recorded content is identical.

Relevance is not ranked here. Membership in the inventory says why a record is present (its ``routes``), and the agent judges
what it means. The seeds are the records the proposal changes, the nodes a readable Working Book references, and the records
of earlier applied versions; the only expansion is one hop along recorded links and genre interactions from a seed node.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from .studio_architecture_review import _COMPONENT_FIELDS, _summary, _title

MAX_MECHANISMS = 80
MAX_HISTORICAL_VERSIONS = 6
MAX_BOOK_ELEMENTS = 24
MAX_BOOK_ELEMENT_TEXT = 240
MECHANISM_TEXT_LIMIT = 260

PROVENANCE = ("preserved", "transformed", "removed", "introduced", "historical")
PROVENANCE_MEANING = {
    "preserved": "Recorded in both the applied baseline and the proposal with identical content. What it means in relation to "
                 "the proposal is an interpretation.",
    "transformed": "Recorded on both sides under the same identifier, with different recorded content (changed_fields).",
    "removed": "Recorded in the applied baseline and absent from the proposal.",
    "introduced": "Absent from the applied baseline and recorded in the proposal.",
    "historical": "Absent from the baseline and the proposal, but recorded in an earlier applied version: no longer current.",
}
ROUTE_MEANING = {
    "changed_by_proposal": "the proposal changes this record",
    "referenced_by_working_book": "a readable Working Book references this node",
    "historical_in_revision": "an earlier applied version recorded it",
    "adjacent_to": "one recorded link or interaction away from a seed node",
}

# Working Book element classes, each with a reserved share of the cap so that no class crowds out another: a Book's recorded
# inheritance declarations (``inherited``), its forward-looking records (``later_possibilities``, ``series_consequences``) and
# the rest. ``open_author_decisions`` are not elements: they are cited through their book_decision items.
# Reserved shares of MAX_BOOK_ELEMENTS, in the order a share left unused is given away. An element that references an examined
# Series question (by its identity) is question-linked, whatever its collection. It is listed last, so a question association
# can never take slots that inherited developments or later possibilities leave unused: it has its own reserved share only.
_ELEMENT_CLASSES: tuple[tuple[str, int, frozenset[str]], ...] = (
    ("inherited", 8, frozenset({"inherited"})),
    ("forward", 6, frozenset({"later_possibilities", "series_consequences"})),
    ("other", 4, frozenset()),
    ("question_linked", 6, frozenset()),
)
_CLASS_INDEX = {name: index for index, (name, _, _) in enumerate(_ELEMENT_CLASSES)}
_EXCLUDED_COLLECTIONS = {"open_author_decisions"}
_EDGE_KINDS = {"link": ("source", "target"), "genre_interaction": ("source_genre_id", "target_genre_id")}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _index(candidate: dict | None) -> dict[tuple[str, str], dict]:
    """Every recorded record of a candidate, by (record kind, identifier)."""
    indexed: dict[tuple[str, str], dict] = {}
    if not candidate:
        return indexed
    for field, key, label, _ in _COMPONENT_FIELDS:
        for entry in candidate.get(field, []) or []:
            identifier = entry.get(key)
            if isinstance(identifier, str):
                indexed.setdefault((label, identifier), entry)
    return indexed


def _rendering(label: str, identifier: str, entry: dict | None) -> str | None:
    if entry is None:
        return None
    return _clip(f"{_title(label, identifier, entry)}: {_summary(label, entry)}", MECHANISM_TEXT_LIMIT)


def _changed_fields(before: dict, after: dict) -> list[str]:
    return sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))


def _provenance(before: dict | None, after: dict | None) -> str:
    if before is not None and after is not None:
        return "preserved" if before == after else "transformed"
    return "removed" if before is not None else "introduced"


def _endpoints(label: str, identifier: str, entry: dict | None) -> list[str]:
    """The node identifiers a record involves: a node is its own endpoint; a link or interaction has two."""
    if label == "node":
        return [identifier]
    if label == "link" and entry:
        return sorted({str(entry.get("source")), str(entry.get("target"))})
    if label == "genre_interaction" and entry:
        return sorted({str(entry.get("source_genre_id")), str(entry.get("target_genre_id"))})
    return []


def _book_numbers_of(routes: list[str]) -> set[int]:
    numbers: set[int] = set()
    for route in routes:
        if route.startswith("referenced_by_working_book:"):
            numbers.update(int(part) for part in route.split(":", 1)[1].split(",") if part)
    return numbers


def mechanism_inventory(
    baseline: dict, proposed: dict, *, book_nodes: dict[str, list[int]],
    historical: Iterable[tuple[str, dict]] = (), limit: int = MAX_MECHANISMS,
) -> dict[str, Any]:
    """The bounded, provenance-qualified records the consequence packet may cite.

    ``book_nodes`` maps a node identifier to the Working Book numbers that reference it. ``historical`` is the applied versions
    before the baseline, newest first, as ``(request_sha256, candidate)``. Returns ``items`` (in citation order), ``considered``
    (distinct records found before the cap) and ``omitted`` (records the cap left out).
    """
    old, new = _index(baseline), _index(proposed)
    found: dict[tuple[str, str], dict[str, Any]] = {}

    def add(key: tuple[str, str], route: str, *, version: str | None = None, entry: dict | None = None) -> None:
        if key in found:
            found[key]["routes"].append(route)
            return
        label, identifier = key
        before, after = (entry, None) if entry is not None else (old.get(key), new.get(key))
        fields = _changed_fields(before, after) if before is not None and after is not None else []
        historical = version is not None
        found[key] = {
            "record_kind": label, "record_id": identifier,
            "provenance": "historical" if historical else _provenance(before, after),
            "changed_fields": fields if before is not None and after is not None else [],
            "routes": [route], "endpoints": _endpoints(label, identifier, after or before),
            # Each text and digest describes the side the record is on, and no other. A historical record is on no side of
            # the baseline or the proposal: its text and digest come from the earlier applied version it names.
            "baseline_text": None if historical else _rendering(label, identifier, before),
            "proposed_text": None if historical else _rendering(label, identifier, after),
            "baseline_sha256": None if historical or before is None else _digest(before),
            "proposed_sha256": None if historical or after is None else _digest(after),
            "historical_text": _rendering(label, identifier, before) if historical else None,
            "historical_sha256": _digest(before) if historical and before is not None else None,
            "version_request_sha256": version,
        }

    # 1. Records the proposal changes, in the owner's collection order.
    for _, _, label, _ in _COMPONENT_FIELDS:
        keys = sorted({key for key in set(old) | set(new) if key[0] == label})
        for key in keys:
            if old.get(key) != new.get(key):
                add(key, "changed_by_proposal")
    # 2. Nodes a readable Working Book references, changed or not. Those the current Architecture no longer has are not records.
    for identifier in sorted(book_nodes):
        key = ("node", identifier)
        if key in old or key in new:
            add(key, "referenced_by_working_book:" + ",".join(str(n) for n in sorted(book_nodes[identifier])))
    # 3. Records earlier applied versions recorded that neither side now has (the most recent version that has them).
    history: list[tuple[str, dict]] = list(historical)[:MAX_HISTORICAL_VERSIONS]
    for version_sha, version_candidate in history:
        for key, entry in sorted(_index(version_candidate).items()):
            if key in old or key in new or key in found:
                continue
            add(key, "historical_in_revision", version=version_sha, entry=entry)
    # 4. One hop from a seed node along recorded links and genre interactions. Nothing is expanded from an expansion.
    seed_nodes = {identifier for (label, identifier), row in found.items() if label == "node"}
    for label, (source_key, target_key) in _EDGE_KINDS.items():
        for key in sorted(k for k in set(old) | set(new) if k[0] == label):
            if key in found:
                continue
            entry = new.get(key) or old.get(key)
            touched = sorted(end for end in {entry.get(source_key), entry.get(target_key)} if end in seed_nodes)
            if touched:
                add(key, "adjacent_to:" + ",".join(touched))

    ordered = list(found.values())
    kept = ordered[:limit]
    for index, row in enumerate(kept, start=1):
        row["index"] = index
        row["book_references"] = sorted(_book_numbers_of(row["routes"]))
    return {"items": kept, "considered": len(ordered), "omitted": max(0, len(ordered) - limit)}


def seed_node_identifiers(inventory: dict[str, Any]) -> set[str]:
    """Node identifiers selected by a seed route (not only by adjacency): the nodes Working Book elements may cite."""
    return {row["record_id"] for row in inventory["items"] if row["record_kind"] == "node"
            and any(not route.startswith("adjacent_to:") for route in row["routes"])}


def _element_class(collection: str, question_linked: bool = False) -> int:
    if question_linked:
        return _CLASS_INDEX["question_linked"]
    for index, (_, _, collections) in enumerate(_ELEMENT_CLASSES):
        if collections and collection in collections:
            return index
    return _CLASS_INDEX["other"]


def book_element_candidates(
    books: dict[int, list[dict]], seed_nodes: set[str], present_nodes: set[str], limit: int = MAX_BOOK_ELEMENTS,
    question_ids: Iterable[str] = (),
) -> dict[str, Any]:
    """Working Book elements that cite a seed node or an examined question, under reserved class shares.

    ``books`` maps a Book number to its element rows as the Book owner reads them. Each element names every node it cites and
    whether that node is present in the current Architecture, so an element that cites a removed record says so. An element
    that references an examined Series question (``question_ids``, by identity) is question-linked and takes the first class.
    A question association records engagement, not inheritance: the row says so by carrying the question's identity only.
    Within a class the elements are taken round by round, one Book at a time, in the Book's own order. Each class first takes
    its reserved share; any share it does not use is then given to the classes that still have elements, in class order.
    """
    examined = set(question_ids)
    queues: dict[tuple[int, int], list[dict[str, Any]]] = {}
    considered = 0
    for number in sorted(books):
        for row in books[number]:
            collection = row.get("collection") or ""
            if collection in _EXCLUDED_COLLECTIONS:
                continue
            refs = [node for node in row.get("series_refs") or [] if isinstance(node, str)]
            cited = [node for node in refs if node in seed_nodes]
            questions = [item for item in row.get("question_refs") or [] if isinstance(item, str)]
            examined_questions = [item for item in questions if item in examined]
            if not cited and not examined_questions:
                continue
            considered += 1
            queues.setdefault((_element_class(collection, bool(examined_questions)), number), []).append({
                "book_number": number, "element_id": row.get("id"), "collection": collection,
                "text": _clip(str(row.get("text") or row.get("title") or ""), MAX_BOOK_ELEMENT_TEXT),
                "attribution": row.get("attribution"), "epistemic_status": row.get("epistemic_status"),
                "cites": [{"node_id": node, "present": node in present_nodes} for node in refs],
                "cited_seed_nodes": cited,
                "question_refs": questions,
                "examined_question_ids": examined_questions,
            })
    chosen: list[dict[str, Any]] = []

    def take(share: int, classes: list[int]) -> None:
        pending = {key: list(queue) for key, queue in queues.items() if key[0] in classes}
        taken = 0
        while taken < share and any(pending.values()):
            for key in sorted(pending, key=lambda item: (item[0], item[1])):
                if pending[key] and taken < share and len(chosen) < limit:
                    chosen.append(pending[key].pop(0))
                    taken += 1
            # Drop what was taken from the shared queues so a later share cannot take it again.
        for key, queue in pending.items():
            queues[key] = queue

    for index, (_, share, _) in enumerate(_ELEMENT_CLASSES):
        take(min(share, limit - len(chosen)), [index])
    for index in range(len(_ELEMENT_CLASSES)):
        take(limit - len(chosen), [index])
    for index, row in enumerate(chosen, start=1):
        row["index"] = index
    return {"items": chosen, "considered": considered, "omitted": max(0, considered - len(chosen))}


def provenance_summary(item: dict[str, Any]) -> dict[str, Any]:
    """What a reader or an investigation carries of one mechanism: identity, provenance, routes and changed fields."""
    return {"record_kind": item["record_kind"], "record_id": item["record_id"], "provenance": item["provenance"],
            "routes": list(item["routes"]), "changed_fields": list(item.get("changed_fields") or [])}
