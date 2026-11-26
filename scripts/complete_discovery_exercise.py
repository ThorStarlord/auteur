"""Complete one arm of the opportunity-discovery exercise through the discovery owner's contract.

The fresh coding agent writes its answer as the JSON object the request's instructions require. This script wraps that
answer as the host-agent response for the pending discovery request and completes it with
``complete_architecture_discovery``, which validates every reference against the request before it stores anything. The
unedited answer is kept beside the stored result.

Usage:
    PYTHONPATH=src python scripts/complete_discovery_exercise.py --project <arm dir> --response <answer.json> \
        --label B-grounded --out <record dir>
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import seed_book_impact_study as impact  # noqa: E402

from auteur.beginner.studio_architecture_discovery import complete_architecture_discovery, project_architecture_discoveries  # noqa: E402
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
    pending = project_architecture_discoveries(store)["pending"]
    if not pending or not pending.get("request"):
        raise SystemExit(f"no pending discovery to complete: {pending}")
    request = HostAgentRequest(**pending["request"])
    answer_text = args.response.read_text(encoding="utf-8")
    json.loads(answer_text)  # the answer must be JSON before the owner validates it
    envelope = build_host_agent_response(request, answer_text, runtime="fresh-subagent-discovery-exercise")
    projection = complete_architecture_discovery(store, envelope.model_dump())
    newest = projection["discoveries"][0]
    args.out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.response, args.out / f"answer-{args.label}-unedited.json")
    record = {"label": args.label, "request_sha256": newest["request_sha256"], "result": newest}
    (args.out / f"result-{args.label}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"label": args.label, "possibilities": len(newest["possibilities"]),
                      "no_possibility_reason": newest.get("no_possibility_reason")}, indent=2))


if __name__ == "__main__":
    main()
