"""Prepare the two arms of the opportunity-discovery exercise on the Spring Ledger study.

Both arms ask the same explicit question with no hint about any answer. The baseline arm (``current_state``) sees the
working Architecture and each question's current wording, without recorded reasons or Book decision texts. The grounded
arm (``full``) is the product's orientation, with the last recorded change and reason and the Book decision texts. Each arm
is its own copy of the same study, so neither can see the other. No provider is called; the answers are completed through
the discovery owner by ``complete_discovery_exercise.py``.

Usage:
    PYTHONPATH=src python scripts/prepare_discovery_exercise.py --root <fresh dir> --out <record dir>
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
from test_persistent_narrative_questions import assign_identities  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

from auteur.beginner.studio_architecture_discovery import prepare_architecture_discovery, project_architecture_discoveries  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402

BOOK = 24
AUTHOR_QUESTION = "What promising creative opportunities am I overlooking?"
ARMS = {"A-current-state": "current_state", "B-grounded": "full"}


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

    results = {}
    for label, orientation in ARMS.items():
        arm_root = root / f"arm-{label}"
        shutil.copytree(root / "discovery", arm_root)
        arm_store = CanvasStore(arm_root, discovery.SPRING)
        projection = prepare_architecture_discovery(arm_store, goal=AUTHOR_QUESTION, orientation=orientation)
        request = projection["pending"]["request"]
        packet = {"request_sha256": request["request_sha256"], "system": request["system"], "user": request["user"],
                  "settings": request["settings"]}
        (out / f"request-{label}.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / f"request-{label}-full.json").write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
        results[label] = {"project": str(arm_root), "orientation": orientation,
                          "request_sha256": request["request_sha256"], "user_bytes": len(request["user"]),
                          "continuing_questions": len(json.loads(request["user"])["discovery_packet"]["questions"])}
    (out / "prepared.json").write_text(json.dumps({"author_question": AUTHOR_QUESTION, "book": BOOK,
                                                   "results": results}, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
