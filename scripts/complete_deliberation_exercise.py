"""Complete one arm of the narrative-deliberation exercise through the inquiry owner's contract.

A fresh coding agent writes its answer as the JSON object the prepared request's instructions require. This script wraps
that answer as the host-agent response for the pending request and completes it with ``complete_architecture_inquiry``,
which validates the response against the request, checks the anchors, and retains the result with its evidence. Nothing
is called from here; the answer's provenance is the agent that wrote it.

Usage:
    PYTHONPATH=src python scripts/complete_deliberation_exercise.py --project <arm dir> --response <answer.json> \
        --label A-current --out <record dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import seed_book_impact_study as impact  # noqa: E402

from auteur.beginner.studio_architecture_inquiry import complete_architecture_inquiry, project_architecture_inquiry  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    store = CanvasStore(args.project, impact.SPRING)
    pending = project_architecture_inquiry(store)
    if pending["status"] != "awaiting_host_agent" or not pending["request"]:
        raise SystemExit(f"no pending inquiry to complete: {pending['status']}")
    request = HostAgentRequest(**pending["request"])
    response_text = args.response.read_text(encoding="utf-8")
    json.loads(response_text)  # the agent's answer must at least be JSON before the owner validates it
    response = build_host_agent_response(request, response_text, runtime="fresh-subagent-exercise")
    projection = complete_architecture_inquiry(store, response.model_dump())
    args.out.mkdir(parents=True, exist_ok=True)
    record = {"label": args.label, "status": projection["status"], "request_sha256": projection.get("request_sha256"),
              "result": projection.get("result")}
    (args.out / f"result-{args.label}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"label": args.label, "status": projection["status"],
                      "hypotheses": len((projection.get("result") or {}).get("hypotheses") or [])}, indent=2))


if __name__ == "__main__":
    main()
