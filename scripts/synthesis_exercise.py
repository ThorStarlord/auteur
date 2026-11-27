"""Staged creative synthesis exercises: prepare and complete one synthesis of selected developments, in a disposable study.

Stages (each runs through the owner that owns it; a responding agent's unedited answer is written beside the result):
    prepare     bind the selected developments, the author's question and any handoffs or criticism, and write the request
                a fresh agent reads
    complete    complete it with a fresh agent's unedited answer; a refused answer is kept with the owner's refusal

Run against a copy of a study that holds the Architecture and Working Book. No provider is called, nothing is applied.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import consequence_exercise as ce  # noqa: E402

from auteur.beginner.studio_architecture_synthesis import (  # noqa: E402
    complete_architecture_synthesis, prepare_architecture_synthesis,
)

RUNTIME = "fresh-subagent-synthesis-exercise"


def prepare(study: Path, question: str, developments: list[dict], culmination: str | None, handoffs: list[str],
            criticism: list[str], prior: str | None, out: Path) -> None:
    store = ce.store_at(study)
    prepared = prepare_architecture_synthesis(store, question=question, developments=developments, culmination=culmination,
                                              handoffs=handoffs, criticism=criticism, prior_request_sha256=prior)
    ce.write(out, "request-synthesis.json", prepared["request"])
    user = json.loads(prepared["request"]["user"])
    print(json.dumps({
        "synthesis_request_sha256": prepared["request"]["request_sha256"],
        "standing": prepared["synthesis"]["standing"],
        "developments": [(row["id"], row["kind"], row["ref"]) for row in user["developments"]],
        "evidence_items": len(user["evidence"]),
        "allowed_evidence": user["allowed_evidence"],
        "coverage": next(item["coverage"] for item in user["evidence"] if item["kind"] == "coverage"),
    }, indent=2, ensure_ascii=False))


def complete(study: Path, request_path: Path, answer: Path, out: Path, attempt: int) -> None:
    store = ce.store_at(study)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    text = answer.read_text(encoding="utf-8")
    try:
        row = complete_architecture_synthesis(store, ce.envelope(request, text, RUNTIME))
    except ValueError as refusal:
        ce.write(out, f"answer-synthesis-attempt-{attempt}-refused.json", text)
        ce.write(out, f"refusal-synthesis-attempt-{attempt}.txt", str(refusal))
        print(json.dumps({"refused": True, "owner_message": str(refusal)}, indent=2, ensure_ascii=False))
        raise SystemExit(2)
    ce.write(out, f"answer-synthesis-attempt-{attempt}-unedited.json", text)
    ce.write(out, "result-synthesis.json", row)
    print(json.dumps({"accepted": True, "standing": row["standing"], "refused_attempts": row["refused_attempts"],
                      "stages": [(stage["book"], stage["horizon"], stage["basis"]) for stage in row["result"]["trajectory"]]},
                     indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="stage", required=True)
    sub = commands.add_parser("prepare")
    sub.add_argument("--study", required=True, type=Path)
    sub.add_argument("--question-file", required=True, type=Path)
    sub.add_argument("--developments", required=True, help='JSON list of {"kind": ..., "ref": ...}')
    sub.add_argument("--culmination-file", type=Path, default=None)
    sub.add_argument("--handoff", action="append", default=[], help="a completed reconsideration request sha256")
    sub.add_argument("--criticism-file", type=Path, default=None, help="one criticism per non-empty line")
    sub.add_argument("--prior", default=None, help="a completed synthesis request sha256 to follow")
    sub.add_argument("--out", required=True, type=Path)
    sub = commands.add_parser("complete")
    sub.add_argument("--study", required=True, type=Path)
    sub.add_argument("--request", required=True, type=Path)
    sub.add_argument("--answer", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    if args.stage == "prepare":
        culmination = args.culmination_file.read_text(encoding="utf-8").strip() if args.culmination_file else None
        criticism = []
        if args.criticism_file:
            criticism = [line.strip() for line in args.criticism_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        prepare(args.study, args.question_file.read_text(encoding="utf-8").strip(), json.loads(args.developments),
                culmination or None, args.handoff, criticism, args.prior, args.out)
    else:
        complete(args.study, args.request, args.answer, args.out, args.attempt)


if __name__ == "__main__":
    main()
