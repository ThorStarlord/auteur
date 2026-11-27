"""Reconsideration exercises: prepare and complete one reconsideration of a saved consequence analysis, in a disposable study.

Stages (each runs through the owner that owns it; a responding agent's unedited answer is written beside the result):
    prepare     bind one claim of a saved analysis and write the request a fresh agent reads
    complete    complete it with a fresh agent's unedited answer; a refused answer is kept with the owner's refusal

Run against a copy of a study that holds an accepted consequence analysis. No provider is called.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import consequence_exercise as ce  # noqa: E402

from auteur.beginner.studio_architecture_reconsideration import (  # noqa: E402
    complete_consequence_reconsideration, prepare_consequence_reconsideration,
)

RUNTIME = "fresh-subagent-reconsideration-exercise"


def prepare(study: Path, analysis_sha: str, selection: dict, instruction: str, criticism: list[str], out: Path) -> None:
    store = ce.store_at(study)
    prepared = prepare_consequence_reconsideration(store, analysis_request_sha256=analysis_sha, selection=selection,
                                                   instruction=instruction, criticism=criticism)
    ce.write(out, "request-reconsideration.json", prepared["request"])
    print(json.dumps({"reconsideration_request_sha256": prepared["request"]["request_sha256"],
                      "claim": prepared["reconsideration"]["claim"]["kind"],
                      "recovered": [row["id"] for row in json.loads(prepared["request"]["user"])["recovery"]["records"]]},
                     indent=2))


def complete(study: Path, request_path: Path, answer: Path, out: Path, attempt: int) -> None:
    store = ce.store_at(study)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    text = answer.read_text(encoding="utf-8")
    try:
        row = complete_consequence_reconsideration(store, ce.envelope(request, text, RUNTIME))
    except ValueError as refusal:
        ce.write(out, f"answer-reconsideration-attempt-{attempt}-refused.json", text)
        ce.write(out, f"refusal-reconsideration-attempt-{attempt}.txt", str(refusal))
        print(json.dumps({"refused": True, "owner_message": str(refusal)}, indent=2))
        raise SystemExit(2)
    ce.write(out, f"answer-reconsideration-attempt-{attempt}-unedited.json", text)
    ce.write(out, "result-reconsideration.json", row)
    print(json.dumps({"accepted": True, "disposition": row["answer"]["disposition"],
                      "criticism": [(a["criticism"], a["verdict"]) for a in row["answer"]["criticism_assessments"]],
                      "evidence": row["answer"]["evidence"], "refused_attempts": row["refused_attempts"]},
                     indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="stage", required=True)
    sub = commands.add_parser("prepare")
    sub.add_argument("--study", required=True, type=Path)
    sub.add_argument("--analysis", required=True)
    sub.add_argument("--selection", required=True, help='JSON {"kind": ..., "ref": ...}')
    sub.add_argument("--instruction-file", required=True, type=Path)
    sub.add_argument("--criticism-file", type=Path, default=None, help="one criticism per non-empty line")
    sub.add_argument("--out", required=True, type=Path)
    sub = commands.add_parser("complete")
    sub.add_argument("--study", required=True, type=Path)
    sub.add_argument("--request", required=True, type=Path)
    sub.add_argument("--answer", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    if args.stage == "prepare":
        criticism = []
        if args.criticism_file:
            criticism = [line.strip() for line in args.criticism_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        prepare(args.study, args.analysis, json.loads(args.selection),
                args.instruction_file.read_text(encoding="utf-8").strip(), criticism, args.out)
    else:
        complete(args.study, args.request, args.answer, args.out, args.attempt)


if __name__ == "__main__":
    main()
