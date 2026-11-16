"""Complete one prepared Studio request from a host-agent candidate file.

Captures the projection, review and fresh-process resume so the evidence keeps
what actually happened rather than a summary of it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import (
    complete_architecture, project_architecture, project_architecture_resume,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

RUNTIME = "opencode-general-subagent"
MODEL = "deepseek-v4.1-flash"


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    canvas_id = sys.argv[2]
    candidate_path = Path(sys.argv[3]).resolve()
    store = CanvasStore(target, canvas_id)
    request_payload = json.loads(
        (target / "qualification" / "request.json").read_text(encoding="utf-8")
    )
    request = HostAgentRequest(**request_payload)
    response = build_host_agent_response(
        request, candidate_path.read_text(encoding="utf-8"),
        runtime=RUNTIME, model=MODEL,
    ).model_dump()

    out = target / "qualification"
    (out / "response.json").write_text(
        json.dumps(response, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    try:
        complete_architecture(store, response)
    except Exception as error:  # recorded, never hidden
        (out / "completion_error.txt").write_text(
            f"{type(error).__name__}: {error}\n", encoding="utf-8",
        )
        print(json.dumps({"status": "REJECTED", "error": f"{type(error).__name__}: {error}"}))
        return 1

    projection = project_architecture(store)
    (out / "projection.json").write_text(
        json.dumps(projection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    if projection.get("review"):
        (out / "review.json").write_text(
            json.dumps(projection["review"], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    (out / "resume.json").write_text(
        json.dumps(project_architecture_resume(store), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    candidate = projection["candidate"]
    print(json.dumps({
        "status": projection["status"],
        "nodes": len(candidate["nodes"]),
        "links": len(candidate["links"]),
        "phases": len(candidate["phases"]),
        "open_questions": len(candidate["open_questions"]),
        "opportunities": len(candidate.get("opportunities") or []),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
