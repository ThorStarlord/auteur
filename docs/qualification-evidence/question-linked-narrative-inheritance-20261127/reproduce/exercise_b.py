"""Exercise B: the historical continuity of a question association across Series changes, in a disposable study.

Run on a copy of the Exercise A study after its association is applied. Every change goes through the owner that owns it:
Series changes through the Studio's Architecture review path (`revise_architecture`), Book changes through the Working Book
owner's prepare, complete and apply. Each step records the association's standing and binding, the Book's other elements,
and the question reading, to show: the original binding stays readable and correct; nothing silently moves to a replacement
question; unrelated elements are preserved; and a later Book revision can add a new association, bound to the current version.

Steps:
    B1 reorder    the conversion question and its neighbour swap positions (Series revision)
    B2 reword     the conversion question's wording changes (Series revision)
    B3 preserve   a targeted Book revision of an unrelated element; the association and the other elements are unchanged
    B4 retire     the conversion question is retired (Series revision)
    B5 introduce  a later Book revision adds an association to the Mill Compact question (current identity)

Usage:
    PYTHONPATH=src python exercise_b.py --study <copy of the Exercise A study's discovery directory> --out <evidence dir>
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import seed_book_impact_study as impact  # noqa: E402
import seed_book_discovery_study as discovery  # noqa: E402
from test_persistent_narrative_questions import identity_for  # noqa: E402

from auteur.beginner.studio_architecture import _candidate  # noqa: E402
from auteur.beginner.studio_architecture_question_projection import project_architecture_questions  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402
from auteur.series.working_book_architecture import (  # noqa: E402
    _book_root,
    _digest,
    _read,
    book_apply_review,
    book_complete,
    book_prepare,
    book_project,
    book_series_references,
)

BOOK = 24
CONVERSION = identity_for(5)
COMPACT = identity_for(6)
BLIND_SPOT = "cons-conversion-blind-spot"
UNRELATED = "eng-ledger-source"  # an engine element that cites no question; the Book revision targets it in B3
NEW_HOME = "agent-mill-compact"  # an agent element that engages the Compact question; the association is new in B5


def element_rows(store: CanvasStore, element_id: str) -> list[dict]:
    return [row for row in book_series_references(store, BOOK)["element_question_references"]
            if row["element_id"] == element_id]


def stored(store: CanvasStore) -> dict:
    return _read(_book_root(store, BOOK) / "current.json")


def element_hashes(store: CanvasStore, exclude: set[str]) -> dict[str, str]:
    artifact = stored(store)["artifact"]
    out = {}
    for collection, value in artifact.items():
        items = value if isinstance(value, list) else [value] if isinstance(value, dict) and "id" in value else []
        if collection == "choice" and isinstance(value, dict):
            items = [value]
        for item in items:
            if isinstance(item, dict) and item.get("id") and item["id"] not in exclude:
                out[item["id"]] = _digest(item)
    return out


def snapshot(store: CanvasStore, label: str) -> dict:
    reading = next((q for q in project_architecture_questions(store)["questions"] if q.get("id") == CONVERSION), None)
    if reading is None:
        reading = next((q for q in project_architecture_questions(store)["no_longer_open"] if q.get("id") == CONVERSION), None)
    rows = element_rows(store, BLIND_SPOT)
    return {
        "step": label,
        "architecture_request_sha256": _candidate(store)["request_sha256"],
        "book_request_sha256": stored(store)["request_sha256"],
        "association": rows,
        "conversion_question": None if reading is None else {
            "standing": reading["standing"], "index": reading.get("index"), "text": reading.get("text"),
            "engagements": [{k: e.get(k) for k in ("element_id", "collection", "state", "recorded")} for e in reading.get("engagements", [])],
            "decisions": [{k: d.get(k) for k in ("decision_id", "state")} for d in reading.get("books", [])],
        },
        "compact_question_engagements": [
            {"element_id": row["element_id"], "state": row["state"], "recorded_index": row["recorded_index"]}
            for row in book_series_references(store, BOOK)["element_question_references"] if row["question_id"] == COMPACT
        ],
    }


def revise_architecture(store: CanvasStore, instruction: str, edit) -> None:
    impact.revise_architecture(store, instruction, edit)


def swap_with_neighbour(candidate: dict) -> None:
    i = candidate["open_question_ids"].index(CONVERSION)
    for listing in (candidate["open_questions"], candidate["open_question_ids"]):
        listing[i], listing[i + 1] = listing[i + 1], listing[i]


def reword(candidate: dict) -> None:
    i = candidate["open_question_ids"].index(CONVERSION)
    candidate["open_questions"][i] = candidate["open_questions"][i].replace(
        "Is the Book 20 hands-to-draw conversion a lasting settlement",
        "Is the Book 20 hands-to-draw conversion, with its blind spot, a lasting settlement")


def retire(candidate: dict) -> None:
    i = candidate["open_question_ids"].index(CONVERSION)
    del candidate["open_questions"][i]
    del candidate["open_question_ids"][i]


def book_revision(store: CanvasStore, instruction: str, targets: tuple[str, ...], edit) -> None:
    prepared = book_prepare(store, BOOK, instruction=instruction, targets=targets)
    artifact = copy.deepcopy(stored(store)["artifact"])
    edit(artifact)
    response = build_host_agent_response(HostAgentRequest(**prepared["request"]), json.dumps(artifact),
                                         runtime="exercise-b-owner-edit").model_dump()
    book_complete(store, BOOK, response)
    result = book_apply_review(store, BOOK, prepared["pending_request_sha256"])
    if result["result"] != "applied":
        raise SystemExit(f"Book revision not applied: {result}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--study", required=True, type=Path, help="a copy of the Exercise A discovery study")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    store = CanvasStore(args.study, discovery.SPRING)
    steps = [snapshot(store, "start")]

    revise_architecture(store, "Swap the conversion question with its neighbour.", swap_with_neighbour)
    steps.append(snapshot(store, "B1 reorder"))

    revise_architecture(store, "Reword the conversion question to name its blind spot.", reword)
    steps.append(snapshot(store, "B2 reword"))

    before = element_hashes(store, exclude={UNRELATED})
    association_before = element_rows(store, BLIND_SPOT)

    def reword_unrelated(artifact: dict) -> None:
        engine = next(item for item in artifact["engines"] if item["id"] == UNRELATED)
        engine["text"] = engine["text"] + " Revised in a later Book revision: the ledger now also records hours."

    book_revision(store, "Revise the unrelated ledger engine's wording; change nothing else.", (UNRELATED,), reword_unrelated)
    after = element_hashes(store, exclude={UNRELATED})
    steps.append(snapshot(store, "B3 preserve"))
    steps[-1]["unrelated_elements_unchanged"] = all(before.get(k) == after.get(k) for k in before)
    steps[-1]["association_unchanged_by_book_revision"] = element_rows(store, BLIND_SPOT) == association_before

    revise_architecture(store, "Retire the conversion question.", retire)
    steps.append(snapshot(store, "B4 retire"))

    def add_compact(artifact: dict) -> None:
        element = next(item for item in artifact["agents"] if item["id"] == NEW_HOME)
        if element.get("provenance") is not None:  # a changed element uses the explicit form, as the owner requires
            element.pop("provenance")
            element["attribution"], element["epistemic_status"] = "agent_proposed", "asserted"
        element.setdefault("refs", []).append({"kind": "series_question", "id": COMPACT})

    book_revision(store, "Record that the Mill Compact agent engages the Compact question.", (NEW_HOME,), add_compact)
    steps.append(snapshot(store, "B5 introduce"))

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "steps.json").write_text(json.dumps(steps, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps([{k: s[k] for k in s if k in ("step",)} for s in steps], indent=2))
    print(json.dumps({"unrelated_elements_unchanged": steps[3].get("unrelated_elements_unchanged"),
                      "association_unchanged_by_book_revision": steps[3].get("association_unchanged_by_book_revision")}))


if __name__ == "__main__":
    main()
