"""Prepare the two requests of the narrative-deliberation exercise on the Spring Ledger study.

Exercise A (baseline) is a cross-question inquiry given only the current formulations, the current working Architecture
and the anchors, as the desk sends it when no history is attached. Exercise B (historically grounded) is the same inquiry
with the owner's recorded-history packet. Both are prepared against the same Architecture, one after the other, and each
request is written out for a fresh coding agent to answer. No provider is called; the answers are completed through the
owner contract (``complete_architecture_inquiry``) by ``complete_deliberation_exercise.py``.

Usage:
    PYTHONPATH=src python scripts/prepare_deliberation_exercise.py --root <disposable dir> --out <record dir>
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

from auteur.beginner.studio_architecture import _candidate  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.beginner.studio_architecture_inquiry import prepare_architecture_inquiry, project_architecture_inquiry  # noqa: E402

BOOK = 24
GATE = 14

# The Gate Table question (history: introduced, then reworded) with the two questions that name the Gate Table's stance.
QUESTION_INDEXES = [12, 13, GATE]
CREATIVE_QUESTION = (
    "These three questions each name the Gate Table, or the stance it stands for. Do they share one creative problem? "
    "Does the Gate Table develop reform from within and the plurality of practice together, as one mechanism, or does it "
    "warn against one of them and so pull the questions apart? Say what each possibility would make possible and what it "
    "would cost the Series, and say plainly if the questions should remain independent."
)
OPERATION = "compare"


def reword_gate(candidate):
    index = candidate["open_question_ids"].index(identity_for(GATE))
    candidate["open_questions"][index] += " Revised: whether the Council may pass through it."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"{root} is not empty; choose a fresh directory")
    out.mkdir(parents=True, exist_ok=True)

    store = discovery.seed_discovery(root / "discovery")
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, root / "discovery", BOOK)
    impact.revise_architecture(store, "Reword the Gate Table question.", reword_gate)

    identifiers = [identity_for(index) for index in QUESTION_INDEXES]
    anchors = [{"kind": "question", "id": identifier} for identifier in identifiers]
    # Each arm is its own copy of the same study, so neither answer can reach the other as a prior exchange.
    arms = {"A-current": (root / "arm-A", False), "B-historical": (root / "arm-B", True)}
    results = {}
    for label, (arm_root, history) in arms.items():
        shutil.copytree(root / "discovery", arm_root)
        arm_store = CanvasStore(arm_root, discovery.SPRING)
        intent = {"version": 1, "canvas_id": arm_store.canvas_id, "operation": OPERATION, "target": "current",
                  "expected_candidate_request_sha256": _candidate(arm_store)["request_sha256"], "anchors": anchors,
                  "author_text": CREATIVE_QUESTION}
        prepare_architecture_inquiry(arm_store, intent, question_history=history)
        pending = project_architecture_inquiry(arm_store)
        request = pending["request"]
        packet = {"request_sha256": pending["request_sha256"], "system": request["system"],
                  "user": request["user"], "settings": request["settings"]}
        (out / f"request-{label}.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / f"request-{label}-full.json").write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
        results[label] = {"project": str(arm_root), "request_sha256": pending["request_sha256"],
                          "user_bytes": len(request["user"]),
                          "has_deliberation": "deliberation" in json.loads(request["user"]),
                          "prior_exchanges": len(json.loads(request["user"]).get("prior_exchanges", []))}
    (out / "prepared.json").write_text(json.dumps({"identities": identifiers, "questions": QUESTION_INDEXES,
                                                   "book": BOOK, "creative_question": CREATIVE_QUESTION,
                                                   "results": results}, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "results": results}, indent=2))


if __name__ == "__main__":
    main()
