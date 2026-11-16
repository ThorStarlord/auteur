"""Prepare the Working Book 26 request for the Auteur arm."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_store import CanvasStore
from auteur.series.working_book_architecture import book_prepare


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    store = CanvasStore(target, "t10-auteur")
    status = book_prepare(store, 26)
    request = status["request"]
    out = target / "qualification" / "book26"
    out.mkdir(parents=True, exist_ok=True)
    (out / "request.json").write_text(
        json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    (out / "system.txt").write_text(request["system"], encoding="utf-8")
    (out / "user.json").write_text(
        json.dumps(json.loads(request["user"]), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "request_sha256": request["request_sha256"],
        "status": status["status"],
        "user_chars": len(request["user"]),
        "system_chars": len(request["system"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
