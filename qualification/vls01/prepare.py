"""VLS-01: freeze the author brief and prepare the real Studio request."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_store import CanvasStore

VISION = """An optimistic hundred-Book series about a profession of witnesses who testify to
events they did not see, reconstructing them from physical traces. A testimony is
admissible only if the witness can be shown to have been wrong at least once.

Intended reader experience: earned trust in testimony that is openly fallible. The
reader should feel the cost of relying on someone who has already been wrong, and
should never be given the comfort that a perfectly reliable witness exists.

Author commitments:
1. A witness who has never been shown wrong is not yet admissible.
2. The profession survives by being auditable, not by being trusted.
3. Success must transform the profession rather than merely defeating a rival.

Intentional ambiguity: what counts as "shown to have been wrong" is never fixed by
the author. Whether error must be proven publicly, admitted privately, or inferred
from a later correction is left open.

Forbidden trivial resolution: the series must not resolve its question by declaring
that all testimony is equally unreliable, nor by producing a witness who is finally
and completely right.

Aim for roughly one hundred Books. The engines, transformations, macro periods and
ending are yours to invent. If a shorter horizon would be artistically stronger,
say so and show what you would cut."""


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    store = CanvasStore(target, "vls01")
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
    for name, payload in (
        ("story_vision.txt", VISION),
        ("request.json", json.dumps(request, indent=2, ensure_ascii=False)),
        ("system.txt", request["system"]),
        ("user.json", json.dumps(json.loads(request["user"]), indent=2, ensure_ascii=False)),
        ("output_contract.json", json.dumps(request["output_contract"], indent=2, ensure_ascii=False)),
    ):
        (out / name).write_text(payload + "\n", encoding="utf-8")
    print(json.dumps({
        "request_sha256": request["request_sha256"],
        "status": status["status"],
        "node_cap": request["output_contract"]["json_schema"]["properties"]["nodes"]["maxItems"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
