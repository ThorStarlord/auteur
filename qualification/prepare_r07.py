"""Prepare a held-out Studio request for the post-repair qualification (R07)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_store import CanvasStore

VISION = (
    "An optimistic thirty-Book series about a court of translators who must render a "
    "peace treaty between two languages that cannot express the same obligations. "
    "One language has a word for a promise that can be inherited; the other has a "
    "word for a promise that cannot be forgiven. Every generation of translators "
    "inherits a treaty whose meaning has drifted. The intended experience is earned "
    "hope about being understood: comprehension is costly, partial, and worth the "
    "cost. The series should never resolve its central question by declaring that "
    "translation is impossible, and it should never resolve it by declaring that "
    "translation is easy."
)


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    store = CanvasStore(target, "qualification-r07")
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
    print(json.dumps({
        "request_sha256": request["request_sha256"],
        "status": status["status"],
        "contract_model": request["output_contract"]["model"],
        "contract_schema_sha": request["output_contract"]["json_schema_sha256"][:16],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
