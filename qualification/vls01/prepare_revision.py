"""VLS-01 Stage 2: prepare the Book 24 counterfactual revision."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import prepare_architecture
from auteur.beginner.studio_store import CanvasStore

INSTRUCTION = (
    "Reconsider the whole Series architecture, but change only what this alteration "
    "actually affects. Counterfactual: Book 24 does not impose demonstrated defects on "
    "the auditors. Instead the profession resolves the audit regress by a constitutional "
    "exemption - certification authority cannot itself be certified - and defends it as "
    "the only thing preserving public trust. Trace the consequences through Book 50, "
    "Book 76 and Book 100. Keep the author's commitments: a witness never shown wrong is "
    "not admissible, the profession survives by being auditable, and success must "
    "transform it rather than defeat a rival. Say explicitly what is preserved, what is "
    "invalidated, and what becomes newly possible."
)


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    store = CanvasStore(target, "vls01")
    status = prepare_architecture(store, instruction=INSTRUCTION)
    request = status["request"]
    out = target / "qualification" / "revision"
    out.mkdir(parents=True, exist_ok=True)
    (out / "request.json").write_text(
        json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    (out / "instruction.txt").write_text(INSTRUCTION, encoding="utf-8")
    print(json.dumps({
        "request_sha256": request["request_sha256"], "status": status["status"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
