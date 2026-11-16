"""Prepare the consequential revision of Working Book 26 for the Auteur arm."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_store import CanvasStore
from auteur.series.working_book_architecture import book_prepare

INSTRUCTION = (
    "Make one consequential revision: the victory must change later Books rather than "
    "add episodes. Show what the revision opens and closes for Books 27-30, what the "
    "source cannot establish, and what would require a new author decision."
)


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    store = CanvasStore(target, "t10-auteur")
    status = book_prepare(store, 26, instruction=INSTRUCTION, holistic=True)
    request = status["request"]
    out = target / "qualification" / "book26-rev"
    out.mkdir(parents=True, exist_ok=True)
    (out / "request.json").write_text(
        json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    (out / "system.txt").write_text(request["system"], encoding="utf-8")
    (out / "user.json").write_text(
        json.dumps(json.loads(request["user"]), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "instruction.txt").write_text(INSTRUCTION, encoding="utf-8")
    print(json.dumps({
        "request_sha256": request["request_sha256"],
        "status": status["status"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
