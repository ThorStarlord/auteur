"""Staged reconstruction and reasoning exercise for consequence-aware development, in disposable studies.

Exercise A reconstructs the PR #645 motivating case through the owners, using the recorded authentic answers of that
development run: the discovery (grounded arm), the investigation of possibility p3, the h2 alternative, and the revised
candidate. It stops before Apply, so the Book 20 rewording is a pending proposal. Two fresh coding agents then examine that
exact proposal, each in its own study copy: the existing pending-review inquiry (the ordinary revision assistance), and the
consequence analysis. Exercise B prepares a second proposal from the same seeded baseline: a deliberate retirement of the
conversion question. A fresh coding agent writes its candidate, and the same consequence analysis examines it.

No provider is called. Each answer is completed through its owner, and the unedited answer is kept beside the result.

Stages (each run once, through the owner that owns it):
    seed                 seed the Spring Ledger study, assign identities, reconcile Book 24
    discover             prepare the discovery (full orientation) and complete it with the recorded answer
    investigate          prepare the deliberation inquiry for a possibility, with from_discovery
    inquiry-complete     complete that inquiry with the recorded deliberation answer
    revise-prepare       prepare the revision from the chosen alternative (no apply)
    revise-complete      complete the revision with the recorded candidate (no apply)
    explain-prepare      prepare the pending-review inquiry, the ordinary assistance arm (in its own copy)
    explain-complete     complete that inquiry with the arm's unedited answer
    consequence-prepare  prepare the consequence analysis of the pending proposal (in its own copy)
    consequence-complete complete it with the arm's unedited answer
    removal-prepare      prepare a plain revision that retires the conversion question (Exercise B)
    removal-complete     complete it with the fresh agent's candidate (no apply)

Usage:
    PYTHONPATH=src python scripts/consequence_exercise.py seed --root <fresh dir>
    PYTHONPATH=src python scripts/consequence_exercise.py discover --root <study> --answer <json> --out <dir>
    ...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

from auteur.beginner.studio_architecture import (  # noqa: E402
    _candidate, complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_architecture_consequence import (  # noqa: E402
    complete_architecture_consequence, prepare_architecture_consequence, project_architecture_consequence,
)
from auteur.beginner.studio_architecture_discovery import (  # noqa: E402
    complete_architecture_discovery, prepare_architecture_discovery, project_architecture_discoveries,
)
from auteur.beginner.studio_architecture_inquiry import (  # noqa: E402
    complete_architecture_inquiry, prepare_architecture_inquiry, project_architecture_inquiry,
)
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402

BOOK = 24
SPRING = discovery.SPRING
DISCOVERY_GOAL = "What promising creative opportunities am I overlooking?"
POSSIBILITY = "p3"
ALTERNATIVE = "h2"
ARM_QUESTION = ("What does this proposed change accomplish, and which earlier creative concerns does it keep, "
                "transform or displace?")
REMOVAL_INSTRUCTION = (
    "Retire the Book 20 hands-to-draw conversion question: the author has decided that the conversion is not a question "
    "this series will carry forward. Remove that question from the open questions and its identity from open_question_ids, "
    "and change nothing else.")
CONVERSION = "q-conversion-settlement"


def store_at(root: Path) -> CanvasStore:
    return CanvasStore(root, SPRING)


def write(out: Path, name: str, data) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) if not isinstance(data, str) else data, encoding="utf-8")
    return path


def envelope(request: dict, answer_text: str, runtime: str) -> dict:
    json.loads(answer_text)  # the answer must be JSON before the owner validates it
    return build_host_agent_response(HostAgentRequest(**request), answer_text, runtime=runtime).model_dump()


def seed(root: Path) -> None:
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"{root} is not empty; choose a fresh directory")
    store = discovery.seed_discovery(root / "discovery")
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, root / "discovery", BOOK)
    print(json.dumps({"study": str(root / "discovery"), "current": _candidate(store)["request_sha256"]}, indent=2))


def discover(project: Path, answer: Path, out: Path) -> None:
    store = store_at(project)
    prepare_architecture_discovery(store, goal=DISCOVERY_GOAL, orientation="full")
    pending = project_architecture_discoveries(store)["pending"]
    text = answer.read_text(encoding="utf-8")
    complete_architecture_discovery(store, envelope(pending["request"], text, "fresh-subagent-consequence-exercise"))
    newest = project_architecture_discoveries(store)["discoveries"][0]
    write(out, "answer-discovery-unedited.json", text)
    write(out, "result-discovery.json", newest)
    print(json.dumps({"discovery_request_sha256": newest["request_sha256"],
                      "possibilities": [p["id"] + " " + p["title"] for p in newest["possibilities"]]}, indent=2))


def investigate(project: Path, discovery_sha: str, out: Path) -> None:
    store = store_at(project)
    discovered = next(row for row in project_architecture_discoveries(store, limit=50)["discoveries"]
                      if row["request_sha256"] == discovery_sha)
    possibility = next(row for row in discovered["possibilities"] if row["id"] == POSSIBILITY)
    anchors = [{"kind": "question", "id": identifier} for identifier in possibility["questions"]]
    intent = {"version": 1, "canvas_id": store.canvas_id, "operation": "compare", "target": "current",
              "expected_candidate_request_sha256": _candidate(store)["request_sha256"], "anchors": anchors,
              "author_text": possibility["next_investigation"],
              "from_discovery": {"request_sha256": discovery_sha, "possibility_id": POSSIBILITY}}
    prepare_architecture_inquiry(store, intent)
    pending = project_architecture_inquiry(store)
    write(out, "inquiry-request-deliberation.json", pending["request"])
    print(json.dumps({"inquiry_request_sha256": pending["request_sha256"]}, indent=2))


def inquiry_complete(project: Path, answer: Path, out: Path) -> None:
    store = store_at(project)
    pending = project_architecture_inquiry(store)
    text = answer.read_text(encoding="utf-8")
    complete_architecture_inquiry(store, envelope(pending["request"], text, "fresh-subagent-consequence-exercise"))
    result = project_architecture_inquiry(store)
    write(out, "answer-deliberation-unedited.json", text)
    write(out, "result-deliberation.json", result["result"] if result.get("result") else result)
    print(json.dumps({"hypotheses": [h["id"] + " " + h["title"] for h in result["result"]["hypotheses"]]}, indent=2))


def revise_prepare(project: Path, inquiry_sha: str, instruction: str, out: Path) -> None:
    store = store_at(project)
    prepared = prepare_architecture(store, instruction=instruction,
                                    selected_alternative={"inquiry_request_sha256": inquiry_sha, "hypothesis_id": ALTERNATIVE})
    write(out, "revision-request.json", prepared["request"])
    print(json.dumps({"revision_request_sha256": prepared["request"]["request_sha256"]}, indent=2))


def revise_complete(project: Path, candidate: Path, out: Path) -> None:
    store = store_at(project)
    waiting = project_architecture(store)["request"]
    text = candidate.read_text(encoding="utf-8")
    complete_architecture(store, envelope(waiting, text, "fresh-subagent-consequence-exercise"))
    review = project_architecture(store)["review"]
    write(out, "revised-candidate-unedited.json", text)
    write(out, "pending-review.json", review)
    print(json.dumps({"pending_revision_request_sha256": review["request_sha256"],
                      "question_changes": review["question_changes"]["questions"]}, indent=2, default=str))


def explain_prepare(project: Path, out: Path) -> None:
    store = store_at(project)
    current = project_architecture(store)
    intent = {"version": 1, "canvas_id": store.canvas_id, "operation": "explain", "target": "pending_review",
              "expected_candidate_request_sha256": current["candidate_request_sha256"], "anchors": [],
              "author_text": ARM_QUESTION}
    prepare_architecture_inquiry(store, intent)
    pending = project_architecture_inquiry(store)
    write(out, "request-explain.json", pending["request"])
    print(json.dumps({"explain_request_sha256": pending["request_sha256"]}, indent=2))


def explain_complete(project: Path, answer: Path, out: Path) -> None:
    store = store_at(project)
    pending = project_architecture_inquiry(store)
    text = answer.read_text(encoding="utf-8")
    complete_architecture_inquiry(store, envelope(pending["request"], text, "fresh-subagent-consequence-exercise"))
    result = project_architecture_inquiry(store)
    write(out, "answer-explain-unedited.json", text)
    write(out, "result-explain.json", result.get("result") or result)
    print(json.dumps({"status": result["status"]}, indent=2))


def consequence_prepare(project: Path, out: Path) -> None:
    store = store_at(project)
    projection = prepare_architecture_consequence(store)
    write(out, "request-consequence.json", projection["request"])
    print(json.dumps({"consequence_request_sha256": projection["request_sha256"], "standing": projection["standing"]},
                     indent=2))


def consequence_complete(project: Path, answer: Path, out: Path) -> None:
    store = store_at(project)
    pending = project_architecture_consequence(store)
    text = answer.read_text(encoding="utf-8")
    projection = complete_architecture_consequence(store, envelope(pending["request"], text,
                                                                  "fresh-subagent-consequence-exercise"))
    write(out, "answer-consequence-unedited.json", text)
    write(out, "result-consequence.json", projection["result"])
    print(json.dumps({"status": projection["status"], "standing": projection["standing"],
                      "concerns": len(projection["result"]["concerns"]),
                      "alternatives": [row["id"] + " " + row["approach"] + " " + row["title"]
                                       for row in projection["result"]["alternatives"]]}, indent=2))


def removal_prepare(project: Path, out: Path) -> None:
    store = store_at(project)
    waiting = prepare_architecture(store, instruction=REMOVAL_INSTRUCTION)
    write(out, "removal-request.json", waiting["request"])
    print(json.dumps({"removal_request_sha256": waiting["request"]["request_sha256"]}, indent=2))


def removal_complete(project: Path, candidate: Path, out: Path) -> None:
    store = store_at(project)
    waiting = project_architecture(store)["request"]
    text = candidate.read_text(encoding="utf-8")
    complete_architecture(store, envelope(waiting, text, "fresh-subagent-consequence-exercise"))
    review = project_architecture(store)["review"]
    write(out, "removal-candidate-unedited.json", text)
    write(out, "removal-pending-review.json", review)
    print(json.dumps({"removed": review["question_changes"]["removed"]}, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="stage", required=True)
    commands.add_parser("seed").add_argument("--root", required=True, type=Path)
    for name in ("discover",):
        sub = commands.add_parser(name)
        sub.add_argument("--root", required=True, type=Path)
        sub.add_argument("--answer", required=True, type=Path)
        sub.add_argument("--out", required=True, type=Path)
    sub = commands.add_parser("investigate")
    sub.add_argument("--root", required=True, type=Path)
    sub.add_argument("--discovery-sha", required=True)
    sub.add_argument("--out", required=True, type=Path)
    for name in ("inquiry-complete", "explain-complete", "consequence-complete", "removal-complete"):
        sub = commands.add_parser(name)
        sub.add_argument("--root", required=True, type=Path)
        sub.add_argument("--answer" if name != "removal-complete" else "--candidate", required=True, type=Path)
        sub.add_argument("--out", required=True, type=Path)
    sub = commands.add_parser("revise-prepare")
    sub.add_argument("--root", required=True, type=Path)
    sub.add_argument("--inquiry-sha", required=True)
    sub.add_argument("--instruction-file", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    sub = commands.add_parser("revise-complete")
    sub.add_argument("--root", required=True, type=Path)
    sub.add_argument("--candidate", required=True, type=Path)
    sub.add_argument("--out", required=True, type=Path)
    for name in ("explain-prepare", "consequence-prepare", "removal-prepare"):
        sub = commands.add_parser(name)
        sub.add_argument("--root", required=True, type=Path)
        sub.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    if args.stage == "seed":
        seed(args.root.resolve())
    elif args.stage == "discover":
        discover(args.root.resolve(), args.answer, args.out.resolve())
    elif args.stage == "investigate":
        investigate(args.root.resolve(), args.discovery_sha, args.out.resolve())
    elif args.stage == "inquiry-complete":
        inquiry_complete(args.root.resolve(), args.answer, args.out.resolve())
    elif args.stage == "revise-prepare":
        revise_prepare(args.root.resolve(), args.inquiry_sha, args.instruction_file.read_text(encoding="utf-8").strip(),
                       args.out.resolve())
    elif args.stage == "revise-complete":
        revise_complete(args.root.resolve(), args.candidate, args.out.resolve())
    elif args.stage == "explain-prepare":
        explain_prepare(args.root.resolve(), args.out.resolve())
    elif args.stage == "explain-complete":
        explain_complete(args.root.resolve(), args.answer, args.out.resolve())
    elif args.stage == "consequence-prepare":
        consequence_prepare(args.root.resolve(), args.out.resolve())
    elif args.stage == "consequence-complete":
        consequence_complete(args.root.resolve(), args.answer, args.out.resolve())
    elif args.stage == "removal-prepare":
        removal_prepare(args.root.resolve(), args.out.resolve())
    elif args.stage == "removal-complete":
        removal_complete(args.root.resolve(), args.candidate, args.out.resolve())


if __name__ == "__main__":
    main()
