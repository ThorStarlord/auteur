"""VLS-01 Stage 2: complete and apply the revised architecture."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, project_architecture,
    project_architecture_resume,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import load_host_agent_request, build_host_agent_response


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    request_path = Path(sys.argv[2]).resolve()
    candidate_path = Path(sys.argv[3]).resolve()
    apply = len(sys.argv) > 4 and sys.argv[4] == "apply"
    store = CanvasStore(target, "vls01")
    request = load_host_agent_request(request_path)
    response = build_host_agent_response(
        request, candidate_path.read_text(encoding="utf-8"),
        runtime="opencode-general-subagent", model="deepseek-v4.1-flash",
    ).model_dump()
    out = request_path.parent
    (out / "response.json").write_text(
        json.dumps(response, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    complete_architecture(store, response)
    projection = project_architecture(store)
    (out / "projection.json").write_text(
        json.dumps(projection, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    review = projection.get("review") or {}
    summary = {
        "status": projection["status"],
        "changes": {k: len(v) if isinstance(v, list) else v
                    for k, v in (review.get("changes") or {}).items()
                    if k in ("nodes", "links", "phases", "interpretations")},
        "added": len((review.get("changes") or {}).get("nodes", {}).get("added", [])),
        "changed": len((review.get("changes") or {}).get("nodes", {}).get("changed", [])),
        "preserved": (review.get("preserved") or {}).get("count"),
    }
    if apply and review.get("request_sha256"):
        applied = apply_architecture_review(store, review["request_sha256"])
        summary["applied"] = applied.get("result")
        (out / "resume_after_apply.json").write_text(
            json.dumps(project_architecture_resume(store), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
