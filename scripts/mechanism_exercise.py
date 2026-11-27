"""Mechanism-centred exercises for the consequence analysis (version 3), in disposable studies.

Exercise A replays PR #647's mechanism transformation (its Exercise B): one recorded relation, the Mill Compact's labour duty
(``l_compact_hands_in_kind``), changes, and no question does. The proposal is rebuilt through the owners from the recorded
unedited candidate, stopped before Apply, and then examined by a fresh coding agent under the version 3 contract. The owner
validates every answer; a refused answer is kept with the owner's refusal, and nothing edits a persisted record.

Stages (each runs through the owner that owns it; a coding agent's unedited answer is written beside the result):
    seed              seed the Spring Ledger study exactly as the consequence exercises do (reuses consequence_exercise.seed)
    baseline-check    compare the recorded baseline (PR #647) with the seeded baseline: the requests must match
    propose           prepare the revision with the recorded instruction and complete it with the recorded candidate (no apply)
    analyse-prepare   prepare the version 3 consequence analysis of the pending proposal (writes the request a fresh agent reads)
    analyse-complete  complete it with a fresh agent's unedited answer; a refused answer is kept beside the owner's refusal

No provider is called. Use a fresh --root for seed, then the same --root for the stages that follow.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import consequence_exercise as ce  # noqa: E402

from auteur.beginner.studio_architecture import (  # noqa: E402
    _candidate, complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_architecture_consequence import (  # noqa: E402
    complete_architecture_consequence, prepare_architecture_consequence, project_architecture_consequence,
)
from auteur.beginner.studio_architecture_inquiry import (  # noqa: E402
    complete_architecture_inquiry, prepare_architecture_inquiry, project_architecture_inquiry,
)

RECORDED = REPO / "docs/qualification-evidence/mechanism-grounded-prospective-reasoning-20261126/exercise-B"
RUNTIME = "fresh-subagent-mechanism-exercise"


def baseline_check(project: Path, out: Path) -> None:
    store = ce.store_at(project)
    pending_recorded = json.loads((RECORDED / "pending-review.json").read_text(encoding="utf-8"))
    current = _candidate(store)
    result = {"seeded_baseline_request_sha256": current["request_sha256"],
              "recorded_baseline_request_sha256": pending_recorded["prior_request_sha256"],
              "matches": current["request_sha256"] == pending_recorded["prior_request_sha256"]}
    ce.write(out, "baseline-check.json", result)
    print(json.dumps(result, indent=2))


def propose(project: Path, out: Path) -> None:
    store = ce.store_at(project)
    instruction = (RECORDED / "instruction-B.txt").read_text(encoding="utf-8").strip()
    candidate_text = (RECORDED / "candidate-unedited.json").read_text(encoding="utf-8")
    prepared = prepare_architecture(store, instruction=instruction)
    complete_architecture(store, ce.envelope(prepared["request"], candidate_text, RUNTIME))
    review = project_architecture(store)["review"]
    ce.write(out, "instruction.txt", instruction)
    ce.write(out, "candidate-recorded-unedited.json", candidate_text)
    ce.write(out, "pending-review.json", review)
    print(json.dumps({"pending_revision_request_sha256": review["request_sha256"],
                      "changed_components": review.get("changed_components"),
                      "question_changes": review["question_changes"]["questions"]}, indent=2, default=str))


def analyse_prepare(project: Path, out: Path) -> None:
    store = ce.store_at(project)
    prepared = prepare_architecture_consequence(store)
    ce.write(out, "request-analysis.json", prepared["request"])
    print(json.dumps({"analysis_request_sha256": prepared["request"]["request_sha256"],
                      "contract": prepared["request"]["settings"]["consequence_schema_version"]}, indent=2))


def analyse_complete(project: Path, answer: Path, out: Path, attempt: int) -> None:
    store = ce.store_at(project)
    request = project_architecture_consequence(store)["request"]
    text = answer.read_text(encoding="utf-8")
    try:
        complete_architecture_consequence(store, ce.envelope(request, text, RUNTIME))
    except ValueError as refusal:
        ce.write(out, f"answer-analysis-attempt-{attempt}-refused.json", text)
        ce.write(out, f"refusal-analysis-attempt-{attempt}.txt", str(refusal))
        print(json.dumps({"refused": True, "owner_message": str(refusal)}, indent=2))
        raise SystemExit(2)
    result = project_architecture_consequence(store)
    ce.write(out, f"answer-analysis-attempt-{attempt}-unedited.json", text)
    ce.write(out, "result-analysis.json", result["result"])
    print(json.dumps({"accepted": True, "reach": result["result"]["reach"],
                      "alternatives": [{"approach": a["approach"], "title": a["title"], "questions": a["questions"],
                                        "mechanisms": a.get("mechanisms", [])} for a in result["result"]["alternatives"]],
                      "connections": [{"standing": c["standing"], "graph": c["graph"]["status"]}
                                      for c in result["result"].get("connections", [])]}, indent=2))


def inquire_prepare(project: Path, anchors: list[dict], operation: str, author_text: str, out: Path,
                    from_consequence: dict | None) -> None:
    store = ce.store_at(project)
    intent = {"version": 1, "canvas_id": store.canvas_id, "operation": operation, "target": "current",
              "expected_candidate_request_sha256": _candidate(store)["request_sha256"], "anchors": anchors,
              "author_text": author_text}
    if from_consequence is not None:
        intent["from_consequence"] = from_consequence
    prepare_architecture_inquiry(store, intent)
    pending = project_architecture_inquiry(store)
    ce.write(out, "request-inquiry.json", pending["request"])
    print(json.dumps({"inquiry_request_sha256": pending["request_sha256"], "operation": operation,
                      "anchors": anchors}, indent=2))


def inquire_complete(project: Path, answer: Path, out: Path, attempt: int) -> None:
    store = ce.store_at(project)
    request = project_architecture_inquiry(store)["request"]
    text = answer.read_text(encoding="utf-8")
    try:
        complete_architecture_inquiry(store, ce.envelope(request, text, RUNTIME))
    except ValueError as refusal:
        ce.write(out, f"answer-inquiry-attempt-{attempt}-refused.json", text)
        ce.write(out, f"refusal-inquiry-attempt-{attempt}.txt", str(refusal))
        print(json.dumps({"refused": True, "owner_message": str(refusal)}, indent=2))
        raise SystemExit(2)
    result = project_architecture_inquiry(store)["result"]
    ce.write(out, f"answer-inquiry-attempt-{attempt}-unedited.json", text)
    ce.write(out, "result-inquiry.json", result)
    print(json.dumps({"accepted": True, "hypotheses": [{"id": h["id"], "title": h["title"],
                                                        "axis": h.get("divergence_axis")} for h in result["hypotheses"]]},
                     indent=2))


def revise_prepare(project: Path, inquiry_sha: str, hypothesis_id: str, instruction: str, out: Path) -> None:
    store = ce.store_at(project)
    prepared = prepare_architecture(store, instruction=instruction,
                                    selected_alternative={"inquiry_request_sha256": inquiry_sha,
                                                          "hypothesis_id": hypothesis_id})
    ce.write(out, "instruction.txt", instruction)
    ce.write(out, "request-revision.json", prepared["request"])
    print(json.dumps({"revision_request_sha256": prepared["request"]["request_sha256"]}, indent=2))


def revise_complete(project: Path, answer: Path, out: Path, attempt: int) -> None:
    store = ce.store_at(project)
    waiting = project_architecture(store)["request"]
    text = answer.read_text(encoding="utf-8")
    try:
        complete_architecture(store, ce.envelope(waiting, text, RUNTIME))
    except ValueError as refusal:
        ce.write(out, f"answer-revision-attempt-{attempt}-refused.json", text)
        ce.write(out, f"refusal-revision-attempt-{attempt}.txt", str(refusal))
        print(json.dumps({"refused": True, "owner_message": str(refusal)}, indent=2))
        raise SystemExit(2)
    review = project_architecture(store)["review"]
    ce.write(out, f"answer-revision-attempt-{attempt}-unedited.json", text)
    ce.write(out, "pending-review.json", review)
    print(json.dumps({"pending_revision_request_sha256": review["request_sha256"],
                      "changed_components": review.get("changed_components"),
                      "question_changes": review["question_changes"]["questions"],
                      "considered_mechanisms": (review.get("selected_creative_alternative") or {}).get("considered_mechanisms")},
                     indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="stage", required=True)
    commands.add_parser("seed").add_argument("--root", required=True, type=Path)
    for name in ("baseline-check", "propose", "analyse-prepare"):
        sub = commands.add_parser(name)
        sub.add_argument("--root", required=True, type=Path)
        sub.add_argument("--out", required=True, type=Path)
    sub = commands.add_parser("analyse-complete")
    sub.add_argument("--root", required=True, type=Path)
    sub.add_argument("--answer", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub.add_argument("--attempt", required=True, type=int)
    sub = commands.add_parser("inquire-prepare")
    sub.add_argument("--root", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub.add_argument("--anchors", required=True, help="JSON list of {kind, id} anchors")
    sub.add_argument("--operation", required=True, choices=["explain", "challenge", "explore", "compare", "connect_to_ask"])
    sub.add_argument("--author-file", required=True, type=Path)
    sub.add_argument("--from-consequence", default=None, help="JSON {request_sha256, alternative_id}")
    sub = commands.add_parser("inquire-complete")
    sub.add_argument("--root", required=True, type=Path)
    sub.add_argument("--answer", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub.add_argument("--attempt", required=True, type=int)
    sub = commands.add_parser("revise-prepare")
    sub.add_argument("--root", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub.add_argument("--inquiry-sha", required=True)
    sub.add_argument("--hypothesis", required=True)
    sub.add_argument("--instruction-file", required=True, type=Path)
    sub = commands.add_parser("revise-complete")
    sub.add_argument("--root", required=True, type=Path)
    sub.add_argument("--answer", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    if args.stage == "seed":
        ce.seed(args.root)
    elif args.stage == "baseline-check":
        baseline_check(args.root / "discovery", args.out)
    elif args.stage == "propose":
        propose(args.root / "discovery", args.out)
    elif args.stage == "analyse-prepare":
        analyse_prepare(args.root / "discovery", args.out)
    elif args.stage == "analyse-complete":
        analyse_complete(args.root / "discovery", args.answer, args.out, args.attempt)
    elif args.stage == "inquire-prepare":
        inquire_prepare(args.root / "discovery", json.loads(args.anchors), args.operation,
                        args.author_file.read_text(encoding="utf-8").strip(), args.out,
                        json.loads(args.from_consequence) if args.from_consequence else None)
    elif args.stage == "inquire-complete":
        inquire_complete(args.root / "discovery", args.answer, args.out, args.attempt)
    elif args.stage == "revise-prepare":
        revise_prepare(args.root / "discovery", args.inquiry_sha, args.hypothesis,
                       args.instruction_file.read_text(encoding="utf-8").strip(), args.out)
    elif args.stage == "revise-complete":
        revise_complete(args.root / "discovery", args.answer, args.out, args.attempt)


if __name__ == "__main__":
    main()
