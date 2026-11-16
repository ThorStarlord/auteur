"""Prepare the R09-E post-repair qualification request."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_store import CanvasStore

VISION = (
    "A twelve-Book optimistic series about a monastery that copies books whose authors "
    "are unknown. The monks must decide, generation after generation, whether an "
    "anonymous book can be authoritative. The intended experience is earned trust in "
    "incomplete knowledge: authority is extended before it can be verified, and the "
    "series should make that extension feel both necessary and dangerous. The series "
    "must not resolve its central question by declaring anonymity either fatal or "
    "irrelevant. The ending, whenever it comes, must be chosen rather than exhausted."
)


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    store = CanvasStore(target, "qualification-r09")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {
            "id": "story-vision", "kind": "note", "title": "Story Vision",
            "content": VISION,
        }, "position": {"x": 20, "y": 50}},
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
    (out / "output_contract.json").write_text(
        json.dumps(request["output_contract"], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    schema = request["output_contract"]["json_schema"]
    print(json.dumps({
        "request_sha256": request["request_sha256"],
        "status": status["status"],
        "contract_has_interpretations": "interpretations" in schema.get("properties", {}),
        "contract_schema_sha": request["output_contract"]["json_schema_sha256"][:16],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
