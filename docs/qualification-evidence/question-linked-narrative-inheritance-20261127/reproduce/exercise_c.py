"""Exercise C: a fresh reasoning agent examines a pending Series proposal, using question-linked Book evidence.

The proposal is authored study material, disclosed as such: it rewords the conversion question (identity unchanged) in a
disposable copy of the Exercise A study. It is left pending, as a reviewed proposal is. The consequence analysis is the
existing owner (`studio_architecture_consequence`); this script only drives its stages. The fresh reasoning agent is given
the request alone, with a neutral instruction, and its unedited answer is passed through the owner.

Stages:
    propose               prepare and complete a Series revision that rewords the conversion question, leaving it pending
    consequence-prepare   prepare the consequence analysis of the pending proposal; writes the request
    consequence-complete  complete it with the fresh agent's unedited answer; writes the result

Usage:
    PYTHONPATH=src python exercise_c.py propose --study <copy of the Exercise A discovery study> --out <dir>
    PYTHONPATH=src python exercise_c.py consequence-prepare --study <dir> --out <dir>
    PYTHONPATH=src python exercise_c.py consequence-complete --study <dir> --answer <json> --out <dir>
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import seed_book_discovery_study as discovery  # noqa: E402
from test_persistent_narrative_questions import identity_for  # noqa: E402

from auteur.beginner.studio_architecture import (  # noqa: E402
    _candidate, complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_architecture_consequence import (  # noqa: E402
    complete_architecture_consequence, prepare_architecture_consequence, project_architecture_consequence,
)
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402

CONVERSION = identity_for(5)
PROPOSAL_INSTRUCTION = ("Make the conversion question name the hand-light households whose draw it is meant to restore, "
                        "without changing what it asks.")
RUNTIME = "fresh-subagent-question-linked-exercise"


def envelope(request: dict, text: str) -> dict:
    json.loads(text)  # the answer must be JSON before the owner validates it
    return build_host_agent_response(HostAgentRequest(**request), text, runtime=RUNTIME).model_dump()


def write(out: Path, name: str, data) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    path.write_text(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def propose(study: Path, out: Path) -> None:
    store = CanvasStore(study, discovery.SPRING)
    candidate = copy.deepcopy(_candidate(store)["candidate"])
    index = candidate["open_question_ids"].index(CONVERSION)
    wording = candidate["open_questions"][index]
    candidate["open_questions"][index] = wording.replace(
        "Is the Book 20 hands-to-draw conversion", "Is the Book 20 hands-to-draw conversion for hand-light households")
    if candidate["open_questions"][index] == wording:
        raise SystemExit("the proposal changed no wording; the conversion question's text has changed")
    waiting = prepare_architecture(store, instruction=PROPOSAL_INSTRUCTION)
    complete_architecture(store, envelope(waiting["request"], json.dumps(candidate)))
    review = project_architecture(store)["review"]
    write(out, "proposal-candidate.json", candidate)
    write(out, "proposal-pending-review.json", review)
    print(json.dumps({"pending": review["question_changes"]["questions"][index]["status"]}, indent=2))


def consequence_prepare(study: Path, out: Path) -> None:
    store = CanvasStore(study, discovery.SPRING)
    projection = prepare_architecture_consequence(store)
    write(out, "request-consequence.json", projection["request"])
    print(json.dumps({"request_sha256": projection["request_sha256"], "standing": projection["standing"]}, indent=2))


def consequence_complete(study: Path, answer: Path, out: Path) -> None:
    store = CanvasStore(study, discovery.SPRING)
    pending = project_architecture_consequence(store)
    text = answer.read_text(encoding="utf-8")
    projection = complete_architecture_consequence(store, envelope(pending["request"], text))
    write(out, "answer-consequence-unedited.json", text)
    write(out, "result-consequence.json", projection["result"])
    print(json.dumps({"status": projection["status"], "standing": projection["standing"]}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="stage", required=True)
    for name in ("propose", "consequence-prepare", "consequence-complete"):
        sub = commands.add_parser(name)
        sub.add_argument("--study", required=True, type=Path)
        sub.add_argument("--out", required=True, type=Path)
        if name == "consequence-complete":
            sub.add_argument("--answer", required=True, type=Path)
    args = parser.parse_args()
    if args.stage == "propose":
        propose(args.study, args.out)
    elif args.stage == "consequence-prepare":
        consequence_prepare(args.study, args.out)
    else:
        consequence_complete(args.study, args.answer, args.out)


if __name__ == "__main__":
    main()
