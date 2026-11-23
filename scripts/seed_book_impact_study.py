"""Seed disposable projects for the Architecture-to-Book impact study.

Every record enters through its own owner, exactly as an author's project would hold it. The Spring
Ledger working Architecture (W6) and its Book 24 working Book come from ``seed_series_context_study``;
the other Books are disposable siblings developed through the Working Book owner's own develop
lifecycle from Book 24's recorded candidate, each with its own Book source items in the canvas.

The canvas's Book source items are part of the working Architecture's own source, so every Book's
items are recorded before the Architecture is developed, and the edit to Book 25's source in step 5 is
followed by an Architecture revision, as the Studio requires.

``impact`` holds, in order:

1. Books 24 and 25, developed against W6.
2. A working Architecture revision, applied through the Studio's review path, that rewords the Ledger
   engine (``eng_ledger``) and removes the Gate table (``inst_gate_table``). Both Books record references
   to both.
3. Book 26, developed after that revision, without the removed concept.
4. An edit to Book 25's own source item, then a second, unrelated Architecture revision that rewords
   a concept no Book records (``th_reading``).
6. Book 27 with a prepared develop request and no working Book; Book 28 with source items only.
7. Book 29, developed and then damaged on disk.

``current`` holds Books 24 and 25, both developed against W6 and current: the starting point for an
Architecture revision the author makes in the Studio.

Nothing is accepted as story canon and no provider is called.

Usage:
    PYTHONPATH=src python scripts/seed_book_impact_study.py --root <disposable dir>
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import seed_series_context_study as base  # noqa: E402

from auteur.beginner.studio_architecture import (  # noqa: E402
    _candidate, apply_architecture_review, complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.series.working_book_architecture import book_complete, book_prepare  # noqa: E402

SPRING = base.SPRING
CHANGED_NODE = "eng_ledger"
REMOVED_NODE = base.REMOVED_NODE  # inst_gate_table
UNRELATED_NODE = "th_reading"
LEDGER_REWORDING = (" Revised: the ledger now also records the hours each hand worked beside the mark, "
                    "so a count of the draw can be read straight from it.")


def _book24_candidate() -> dict:
    return json.loads((base.EVIDENCE / "as-qualified/book-24-candidate.json").read_text(encoding="utf-8"))


def _swap_refs(node, mapping: dict[str, str], drop_node: str | None, fallback_node: str) -> None:
    """Point source-item refs at this Book's own items; replace refs to a concept the Architecture lost."""
    if isinstance(node, dict):
        refs = node.get("refs")
        if isinstance(refs, list):
            kept = []
            for ref in refs:
                if ref.get("kind") == "source_item" and ref.get("id") in mapping:
                    ref = {**ref, "id": mapping[ref["id"]]}
                if drop_node and ref.get("kind") == "series_node" and ref.get("id") == drop_node:
                    ref = {"kind": "series_node", "id": fallback_node}
                if ref not in kept:
                    kept.append(ref)
            node["refs"] = kept
        for key in ("name_source", "target"):
            ref = node.get(key)
            if isinstance(ref, dict) and ref.get("kind") == "source_item" and ref.get("id") in mapping:
                node[key] = {**ref, "id": mapping[ref["id"]]}
            if isinstance(ref, dict) and drop_node and ref.get("kind") == "series_node" and ref.get("id") == drop_node:
                node[key] = {"kind": "series_node", "id": fallback_node}
        for value in node.values():
            _swap_refs(value, mapping, drop_node, fallback_node)
    elif isinstance(node, list):
        for value in node:
            _swap_refs(value, mapping, drop_node, fallback_node)


def _sibling_ids(packet_source: list[dict], number: int) -> dict[str, str]:
    return {item["id"]: item["id"].replace("book-24", f"book-{number}") for item in packet_source}


def seed_canvas(project: Path, numbers: tuple[int, ...]) -> CanvasStore:
    """The Spring Ledger canvas with Book 24's source and a copy of it for each sibling Book, then W6."""
    packet = json.loads(json.loads((base.EVIDENCE / "book24-prepare-request.json").read_text(encoding="utf-8"))
                        ["request"]["user"])
    source, w6 = packet["author_source"], packet["series_architecture"]["candidate"]
    store = CanvasStore(project, SPRING)
    store.create()
    items = [{**item, "kind": "note"} for item in source["story_vision"]]
    items += [{**item, "kind": "note"} for item in source["book_source"]]
    for number in numbers:
        mapping = _sibling_ids(source["book_source"], number)
        items += [{**item, "kind": "note", "id": mapping[item["id"]], "group": f"book-{number}",
                   "title": item["title"].replace("24", str(number))} for item in source["book_source"]]
    items += [{"id": item["id"], "kind": "note", "title": item["title"], "group": "Creative intentions",
               "content": item["content"], "intention_status": item["status"]}
              for item in source["creative_intentions"]]
    for i, item in enumerate(items):
        store.apply("create-item", expected_revision=store.load().revision, command_id=f"seed-{item['id']}",
                    payload={"item": item, "position": {"x": 20 + 300 * (i // 8), "y": 40 + 120 * (i % 8)}})
    waiting = prepare_architecture(store)
    complete_architecture(store, base._reply(waiting["request"], w6, "book-impact-seed"))
    book = book_prepare(store, 24)
    book_complete(store, 24, base._reply(book["request"], _book24_candidate(), "book-impact-seed"))
    return store


def develop_sibling(store: CanvasStore, number: int, *, title: str, drop_node: str | None = None) -> None:
    """A disposable Book developed through the owner's own lifecycle from Book 24's recorded candidate."""
    sources = [item for item in store.load().items if item.group == "book-24"]
    mapping = {item.id: item.id.replace("book-24", f"book-{number}") for item in sources}
    candidate = _book24_candidate()
    candidate["book_number"] = number
    candidate["title"] = title
    _swap_refs(candidate, mapping, drop_node, "str_hollow_gate")
    prepared = book_prepare(store, number)
    book_complete(store, number, base._reply(prepared["request"], candidate, "book-impact-seed"))


def revise_architecture(store: CanvasStore, instruction: str, edit) -> str:
    """A working Architecture revision, applied through the Studio's own review path."""
    revised = copy.deepcopy(_candidate(store)["candidate"])
    edit(revised)
    waiting = prepare_architecture(store, instruction=instruction)
    sha = waiting["request"]["request_sha256"]
    complete_architecture(store, base._reply(waiting["request"], revised, "book-impact-seed"))
    apply_architecture_review(store, sha)
    return sha


def reword_and_remove(store: CanvasStore) -> str:
    def edit(candidate: dict) -> None:
        next(n for n in candidate["nodes"] if n["id"] == CHANGED_NODE)["summary"] += LEDGER_REWORDING
        candidate["nodes"] = [n for n in candidate["nodes"] if n["id"] != REMOVED_NODE]
        candidate["links"] = [link for link in candidate.get("links", [])
                              if REMOVED_NODE not in (link.get("source"), link.get("target"))]
    return revise_architecture(store, "Let the ledger record hours, and drop the Gate table.", edit)


def reword_unrelated(store: CanvasStore) -> str:
    def edit(candidate: dict) -> None:
        next(n for n in candidate["nodes"] if n["id"] == UNRELATED_NODE)["summary"] += " Revised: reading is taught aloud."
    return revise_architecture(store, "Say how reading is taught.", edit)


def edit_book_source(store: CanvasStore, number: int) -> None:
    item = next(i for i in store.load().items if i.group == f"book-{number}")
    edited = {**item.model_dump(mode="json"), "content": item.content + "\n\nAuthor's note: the crew count is twelve, not nine."}
    store.apply("update-item", expected_revision=store.load().revision, command_id=f"seed-edit-{item.id}",
                payload={"item": edited})


def seed_impact(project: Path) -> CanvasStore:
    store = seed_canvas(project, (25, 26, 27, 28, 29))
    develop_sibling(store, 25, title="The Counted Hands")
    reword_and_remove(store)
    develop_sibling(store, 26, title="After the Gate Table", drop_node=REMOVED_NODE)
    develop_sibling(store, 29, title="The Damaged Record", drop_node=REMOVED_NODE)
    book_prepare(store, 27)  # a develop request only: no working Book 27 yet. Book 28 has source items only.
    edit_book_source(store, 25)
    reword_unrelated(store)
    damaged = store.directory / "architecture/books/29/current.json"
    damaged.write_text(damaged.read_text(encoding="utf-8")[:400], encoding="utf-8")
    return store


def seed_current(project: Path) -> CanvasStore:
    store = seed_canvas(project, (25,))
    develop_sibling(store, 25, title="The Counted Hands")
    return store


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path, help="disposable directory for the projects")
    args = parser.parse_args()
    root = args.root.resolve()
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"{root} is not empty; choose a fresh directory")
    root.mkdir(parents=True, exist_ok=True)
    seed_impact(root / "impact")
    seed_current(root / "current")
    print(json.dumps({"impact": str(root / "impact"), "current": str(root / "current"), "canvas": SPRING}, indent=2))


if __name__ == "__main__":
    main()
