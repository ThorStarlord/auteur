"""Complete a prepared Working Book request from a host-agent artifact file."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import (
    book_complete, book_project, book_resume,
)

RUNTIME = "opencode-general-subagent"
MODEL = "deepseek-v4.1-flash"


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    book_number = int(sys.argv[2])
    artifact_path = Path(sys.argv[3]).resolve()
    folder = Path(sys.argv[4]) if len(sys.argv) > 4 else target / "qualification" / "book26"
    store = CanvasStore(target, "t10-auteur")
    request = HostAgentRequest(**json.loads(
        (folder / "request.json").read_text(encoding="utf-8")
    ))
    response = build_host_agent_response(
        request, artifact_path.read_text(encoding="utf-8"),
        runtime=RUNTIME, model=MODEL,
    ).model_dump()
    (folder / "response.json").write_text(
        json.dumps(response, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    try:
        book_complete(store, book_number, response)
    except Exception as error:
        (folder / "completion_error.txt").write_text(
            f"{type(error).__name__}: {error}\n", encoding="utf-8",
        )
        print(json.dumps({"status": "REJECTED", "error": f"{type(error).__name__}: {error}"}))
        return 1
    projection = book_project(store, book_number)
    (folder / "projection.json").write_text(
        json.dumps(projection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    if projection.get("review"):
        (folder / "review.json").write_text(
            json.dumps(projection["review"], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    (folder / "resume.json").write_text(
        json.dumps(book_resume(store, book_number), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": projection["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
