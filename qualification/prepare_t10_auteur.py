"""Prepare the Auteur arm of the frozen desert-archive comparison.

Step 1 (this script): create the workspace with the identical author goal,
accepted commitments and starting material, then prepare the Series request.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_store import CanvasStore

GOAL = (
    "A forty-Book series about a desert archive that decides which lives are recorded. "
    "The orders that keep the archive neutral are the only thing preventing a memory war. "
    "The intended experience is unease at how much order depends on forgetting."
)
COMMITMENTS = (
    "Accepted commitments that must not be contradicted:\n"
    "1. Book 26 ends the Warden's long campaign in victory.\n"
    "2. The archive's neutrality is the orders' justification, not a natural fact.\n"
    "3. The Series must eventually face what it owes the erased."
)
SOURCE = (
    "Book 26 source: the Warden's long campaign against the archive finally ends in "
    "victory. The orders that depended on having an enemy must now justify themselves "
    "to the people whose lives the archive never recorded."
)


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    store = CanvasStore(target, "t10-auteur")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={
            "item": {
                "id": "story-vision", "kind": "note", "title": "Story Vision",
                "content": GOAL + "\n\n" + COMMITMENTS,
            },
            "position": {"x": 20, "y": 50},
        },
    )
    store.apply(
        "create-item", expected_revision=store.load().revision,
        command_id="book-26-source",
        payload={"item": {
            "id": "book-26-source", "kind": "note", "title": "Book 26 source",
            "group": "book-26", "content": SOURCE},
            "position": {"x": 20, "y": 200}},
    )
    status = prepare_architecture(store)
    request = status["request"]
    out = target / "qualification"
    out.mkdir(exist_ok=True)
    (out / "system.txt").write_text(request["system"], encoding="utf-8")
    (out / "user.json").write_text(
        json.dumps(json.loads(request["user"]), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "workspace": str(target),
        "request_sha256": request["request_sha256"],
        "status": status["status"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
