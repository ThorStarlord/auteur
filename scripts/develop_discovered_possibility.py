"""Carry one discovered possibility through the existing deliberation and revision workflow, in a disposable study.

Stages, each run once, each through the owner that owns it:

- ``investigate``: prepare the deliberation inquiry for the possibility's own questions, with the discovery reference
  (``prepare_architecture_inquiry`` with ``from_discovery``). The author's sentence is the possibility's next
  investigation, supplied as the exercise author's text.
- ``revise-prepare``: after an alternative is chosen from the answered inquiry, prepare the revision it leads to
  (``prepare_architecture`` with ``selected_alternative``) and write the waiting request for a fresh coding agent.
- ``revise-complete``: complete the revision with the revised candidate that agent wrote, through
  ``complete_architecture``, then apply the reviewed working revision with ``apply_architecture_review``.

Usage:
    PYTHONPATH=src python scripts/develop_discovered_possibility.py --stage investigate --project <arm dir> \
        --discovery <request sha> --possibility p1 --out <dir>
    PYTHONPATH=src python scripts/develop_discovered_possibility.py --stage revise-prepare --project <arm dir> \
        --inquiry <inquiry sha> --hypothesis h2 --instruction <file> --out <dir>
    PYTHONPATH=src python scripts/develop_discovered_possibility.py --stage revise-complete --project <arm dir> \
        --candidate <revised candidate.json> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import seed_book_impact_study as impact  # noqa: E402

from auteur.beginner.studio_architecture import (  # noqa: E402
    _candidate, apply_architecture_review, complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_architecture_discovery import project_architecture_discoveries  # noqa: E402
from auteur.beginner.studio_architecture_inquiry import prepare_architecture_inquiry, project_architecture_inquiry  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402


def investigate(store: CanvasStore, discovery_sha: str, possibility_id: str, out: Path) -> None:
    discovery = next(row for row in project_architecture_discoveries(store, limit=50)["discoveries"]
                     if row["request_sha256"] == discovery_sha)
    possibility = next(row for row in discovery["possibilities"] if row["id"] == possibility_id)
    anchors = [{"kind": "question", "id": identifier} for identifier in possibility["questions"]]
    intent = {"version": 1, "canvas_id": store.canvas_id, "operation": "compare", "target": "current",
              "expected_candidate_request_sha256": _candidate(store)["request_sha256"], "anchors": anchors,
              "author_text": possibility["next_investigation"],
              "from_discovery": {"request_sha256": discovery_sha, "possibility_id": possibility_id}}
    prepare_architecture_inquiry(store, intent)
    pending = project_architecture_inquiry(store)
    (out / "inquiry-request.json").write_text(json.dumps(pending["request"], ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"stage": "investigate", "inquiry_request_sha256": pending["request_sha256"],
                      "from_discovery": json.loads(pending["request"]["user"]).get("from_discovery")}, indent=2))


def revise_prepare(store: CanvasStore, inquiry_sha: str, hypothesis_id: str, instruction: str, out: Path) -> None:
    prepared = prepare_architecture(store, instruction=instruction,
                                    selected_alternative={"inquiry_request_sha256": inquiry_sha,
                                                          "hypothesis_id": hypothesis_id})
    waiting = prepared["request"]
    (out / "revision-request.json").write_text(json.dumps(waiting, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"stage": "revise-prepare", "revision_request_sha256": waiting["request_sha256"]}, indent=2))


def revise_complete(store: CanvasStore, candidate_path: Path, out: Path) -> None:
    waiting = project_architecture(store)["request"]
    request = HostAgentRequest(**waiting)
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    envelope = build_host_agent_response(request, json.dumps(candidate), runtime="fresh-subagent-development-exercise")
    complete_architecture(store, envelope.model_dump())
    review = project_architecture(store)
    apply_architecture_review(store, waiting["request_sha256"])
    after = project_architecture(store)
    (out / "revision-review.json").write_text(json.dumps(review.get("review"), ensure_ascii=False, indent=2, default=str),
                                              encoding="utf-8")
    print(json.dumps({"stage": "revise-complete", "applied": waiting["request_sha256"],
                      "status_after": after.get("status")}, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stage", required=True, choices=("investigate", "revise-prepare", "revise-complete"))
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--discovery")
    parser.add_argument("--possibility")
    parser.add_argument("--inquiry")
    parser.add_argument("--hypothesis")
    parser.add_argument("--instruction", type=Path)
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    store = CanvasStore(args.project, impact.SPRING)
    if args.stage == "investigate":
        investigate(store, args.discovery, args.possibility, args.out)
    elif args.stage == "revise-prepare":
        revise_prepare(store, args.inquiry, args.hypothesis, args.instruction.read_text(encoding="utf-8").strip(), args.out)
    else:
        revise_complete(store, args.candidate, args.out)


if __name__ == "__main__":
    main()
