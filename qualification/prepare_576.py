"""Prepare a real Studio host-agent request for the #576 qualification run.

Never fabricates the candidate: it only prepares the request and writes the exact
payload the host agent must answer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_store import CanvasStore

VISION = (
    "An optimistic seventy-Book series about a civilization that discovers its "
    "founding hero was a fraud. The institutions built on that story - the oath, "
    "the archive of merit, the hereditary office - still work, and still do real "
    "good. Each generation inherits a different piece of the truth: a ledger, a "
    "letter, a witness, a forged coin. The series asks whether an institution "
    "founded on a lie can be made honest without being destroyed, and whether it "
    "is worth keeping once it is honest. The intended reader experience is earned "
    "hope: every Book should make honesty cost something that the previous Book "
    "made the reader value. Never resolve the series' central question by "
    "declaring the argument over. The ending, whenever it comes, must be chosen "
    "rather than exhausted."
)


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    store = CanvasStore(target, "qualification-576")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={
            "item": {
                "id": "story-vision", "kind": "note", "title": "Story Vision",
                "content": VISION,
            },
            "position": {"x": 20, "y": 50},
        },
    )
    status = prepare_architecture(store)
    request = status["request"]
    out = target / "qualification"
    out.mkdir(exist_ok=True)
    (out / "story_vision.txt").write_text(VISION, encoding="utf-8")
    (out / "request.json").write_text(
        json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    (out / "system.txt").write_text(request["system"], encoding="utf-8")
    (out / "user.json").write_text(
        json.dumps(json.loads(request["user"]), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "workspace": str(target),
        "request_sha256": request["request_sha256"],
        "candidate_id": request["candidate_id"],
        "status": status["status"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
