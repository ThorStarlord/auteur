"""Claim-basis verification exercises: list a synthesis's claims, prepare one claim's verification, and complete it with a fresh agent's
unedited answer. Each stage runs through the owner that owns it. A refused judgement is kept with the owner's refusal.

Stages:
    claims      list every checkable claim of a completed synthesis, with the claims that others depend on
    prepare     write the verification request a fresh agent reads, for one claim
    complete    complete it with a fresh agent's unedited answer

Run against a copy of a study that holds the Architecture, the Working Book and the completed synthesis. No provider is called and
nothing is applied.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import consequence_exercise as ce  # noqa: E402

from auteur.beginner.studio_architecture_synthesis import synthesis_record  # noqa: E402
from auteur.beginner.studio_architecture_verification import (  # noqa: E402
    claims_of, complete_claim_verification, dependents_of, prepare_claim_verification,
)

RUNTIME = "fresh-subagent-claim-verification-exercise"


def claims(study: Path, synthesis: str) -> None:
    store = ce.store_at(study)
    record = synthesis_record(store, synthesis)
    listed = claims_of(record["answer"])
    uses = dependents_of(record["answer"], listed)
    rows = [{"claim": ref, "kind": info["kind"], "basis": info["basis"], "cites": info["evidence"],
             "used_by": uses[ref]["used_by"], "load_bearing": uses[ref]["load_bearing"]} for ref, info in listed.items()]
    print(json.dumps({"synthesis": synthesis, "standing": record["standing"], "claims": rows}, indent=2, ensure_ascii=False))


def prepare(study: Path, synthesis: str, claim: str, out: Path) -> None:
    store = ce.store_at(study)
    prepared = prepare_claim_verification(store, synthesis_request_sha256=synthesis, claim=claim)
    ce.write(out, f"request-verification-{claim}.json", prepared["request"])
    print(json.dumps({"claim": claim, "request_sha256": prepared["request"]["request_sha256"],
                      "standing": prepared["verification"]["standing"], "load_bearing": prepared["verification"]["load_bearing"]},
                     indent=2, ensure_ascii=False))


def complete(study: Path, request_path: Path, answer: Path, out: Path, attempt: int) -> None:
    store = ce.store_at(study)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    text = answer.read_text(encoding="utf-8")
    claim = request["settings"]["claim"]
    try:
        row = complete_claim_verification(store, ce.envelope(request, text, RUNTIME))
    except ValueError as refusal:
        ce.write(out, f"verification-{claim}-attempt-{attempt}-refused.json", text)
        ce.write(out, f"verification-{claim}-attempt-{attempt}-refusal.txt", str(refusal))
        print(json.dumps({"claim": claim, "refused": True, "owner_message": str(refusal)}, indent=2, ensure_ascii=False))
        raise SystemExit(2)
    ce.write(out, f"verification-{claim}-attempt-{attempt}-unedited.json", text)
    ce.write(out, f"verification-{claim}-result.json", row)
    print(json.dumps({"claim": claim, "accepted": True, "standing": row["standing"], "judgment": row["result"]["judgment"],
                      "refused_attempts": row["refused_attempts"]}, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="stage", required=True)
    sub = commands.add_parser("claims")
    sub.add_argument("--study", required=True, type=Path)
    sub.add_argument("--synthesis", required=True)
    sub = commands.add_parser("prepare")
    sub.add_argument("--study", required=True, type=Path)
    sub.add_argument("--synthesis", required=True)
    sub.add_argument("--claim", required=True)
    sub.add_argument("--out", required=True, type=Path)
    sub = commands.add_parser("complete")
    sub.add_argument("--study", required=True, type=Path)
    sub.add_argument("--request", required=True, type=Path)
    sub.add_argument("--answer", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub.add_argument("--attempt", required=True, type=int)
    args = parser.parse_args()
    if args.stage == "claims":
        claims(args.study, args.synthesis)
    elif args.stage == "prepare":
        prepare(args.study, args.synthesis, args.claim, args.out)
    else:
        complete(args.study, args.request, args.answer, args.out, args.attempt)


if __name__ == "__main__":
    main()
