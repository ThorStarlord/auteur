"""Studio traceability qualification: freeze the brief and prepare the real request."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_store import CanvasStore

VISION = """A fourteen-Book optimistic series about a guild of bridge-wards who certify that a
bridge is sound. A ward's signature is what makes a span legal; the crown cannot
certify and cannot overrule. The intended reader experience is earned trust in a
certification you cannot verify yourself: every crossing is an act of faith in a
stranger's judgement.

Author commitments:
1. The guild's authority comes from the ward's signature, not from the crown.
2. Every Book must change who bears the risk of a wrong certificate.
3. The series must not resolve by declaring that certification is meaningless.

The governing criterion: a bridge is sound only if a person who did not build it
will cross it.

Book 12 must decide whether to close the Old Span, whose certificate was signed by
a ward later shown to have been paid by the contractor who built it. The crossing
public has used that bridge daily for forty years."""


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    store = CanvasStore(target, "trace01")
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
        "system_chars": len(request["system"]),
        "mentions_interpretations": "interpretations" in request["system"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
