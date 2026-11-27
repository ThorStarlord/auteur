"""Exercise A: establish a typed question association for Book 24 through the Working Book owner, in a disposable study.

Stages (each one runs through the owner that owns it; nothing edits a persisted Book record):
    seed          seed the Spring Ledger discovery study (Book 24 reconciled), then give the Series open questions
                  identities through a disposable Architecture revision, as the consequence exercise does. Records the
                  referent that Book 24's prose names, read from the exact Series version its record was written against.
    prepare       prepare a targeted revision of Book 24's blind-spot element with a neutral instruction, and write
                  the request and the Book's current record for the coding agent (the complete Book object is required).
    complete      validate the coding agent's unedited Book object through the owner and store the review (no Apply).
    apply         apply the reviewed request through the owner, then read the question-centred reading back.

No provider is called. The coding agent is a fresh sub-agent that is given only the request and the current record.

Usage (each stage with the same --root):
    PYTHONPATH=src python exercise_a.py seed --root <fresh dir>
    PYTHONPATH=src python exercise_a.py prepare --root <dir> --out <evidence dir>
    PYTHONPATH=src python exercise_a.py complete --root <dir> --candidate <json> --out <evidence dir>
    PYTHONPATH=src python exercise_a.py apply --root <dir> --out <evidence dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402

from auteur.beginner.studio_architecture import _candidate, architecture_versions  # noqa: E402
from auteur.beginner.studio_architecture_question_projection import project_architecture_questions  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402
from auteur.series.working_book_architecture import (  # noqa: E402
    _book_root,
    _read,
    book_apply_review,
    book_complete,
    book_positional_observations,
    book_prepare,
    book_project,
    book_series_references,
)

BOOK = 24
BLIND_SPOT = "cons-conversion-blind-spot"
# Neutral: it asks what the element engages, and does not name the question it might engage.
INSTRUCTION = ("Check which open questions of the working Architecture, if any, this element actually engages, and record "
               "each one as a question association by its identity. Leave the element otherwise as it is.")
CONVERSION_INDEX = 5


def store_at(root: Path) -> CanvasStore:
    return CanvasStore(root / "discovery", discovery.SPRING)


def write(out: Path, name: str, data) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    path.write_text(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def seed(root: Path, out: Path) -> None:
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"{root} is not empty; choose a fresh directory")
    root.mkdir(parents=True, exist_ok=True)
    store = discovery.seed_discovery(root / "discovery")
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    record = _read(_book_root(store, BOOK) / "current.json")
    versions = dict(architecture_versions(store))
    recorded = versions[record["series_request_sha256"]]
    current = _candidate(store)["candidate"]
    referent = {
        "book": BOOK,
        "recorded_against_architecture_request_sha256": record["series_request_sha256"],
        "recorded_version_has_identities": bool(recorded.get("open_question_ids")),
        "recorded_version_open_questions": len(recorded["open_questions"]),
        "position_six_one_based": recorded["open_questions"][CONVERSION_INDEX],
        "position_seven_one_based": recorded["open_questions"][CONVERSION_INDEX + 1],
        "current_architecture_request_sha256": _candidate(store)["request_sha256"],
        "current_identity_at_index_5": current["open_question_ids"][CONVERSION_INDEX],
        "current_wording_at_index_5": current["open_questions"][CONVERSION_INDEX],
        "positional_observations": book_positional_observations(store, BOOK)["observations"],
    }
    write(out, "referent-recovered.json", referent)
    print(json.dumps({"study": str(root / "discovery"), "referent": referent["current_identity_at_index_5"]}, indent=2))


def prepare(root: Path, out: Path) -> None:
    store = store_at(root)
    prepared = book_prepare(store, BOOK, instruction=INSTRUCTION, targets=(BLIND_SPOT,))
    record = _read(_book_root(store, BOOK) / "current.json")
    write(out, "request-book24.json", prepared["request"])
    write(out, "current-book24-record.json", record["artifact"])
    print(json.dumps({"pending_request_sha256": prepared["pending_request_sha256"], "status": prepared["status"]}, indent=2))


def complete(root: Path, candidate: Path, out: Path) -> None:
    store = store_at(root)
    pending = book_project(store, BOOK)
    text = candidate.read_text(encoding="utf-8")
    book_complete(store, BOOK, build_host_agent_response(HostAgentRequest(**pending["request"]), text,
                                                          runtime="fresh-subagent-question-association").model_dump())
    review = book_project(store, BOOK)["review"]
    write(out, "candidate-book24-unedited.json", text)
    write(out, "review-book24.json", review)
    print(json.dumps({"applicable": review["applicable"], "question_associations": review["question_associations"]},
                     indent=2, ensure_ascii=False))


def apply(root: Path, out: Path) -> None:
    store = store_at(root)
    sha = book_project(store, BOOK)["pending_request_sha256"]
    result = book_apply_review(store, BOOK, sha)
    reading = next(q for q in project_architecture_questions(store)["questions"] if q.get("id") == identity_for(CONVERSION_INDEX))
    write(out, "apply-result.json", {"request_sha256": sha, "result": result["result"], "currentness": result.get("currentness")})
    write(out, "question-reading-after-apply.json", reading)
    write(out, "element-references-after-apply.json", book_series_references(store, BOOK)["element_question_references"])
    print(json.dumps({"result": result["result"], "engagements": reading["engagements"]}, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="stage", required=True)
    for name in ("seed", "prepare", "apply"):
        sub = commands.add_parser(name)
        sub.add_argument("--root", required=True, type=Path)
        sub.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "exercise-a")
    complete_parser = commands.add_parser("complete")
    complete_parser.add_argument("--root", required=True, type=Path)
    complete_parser.add_argument("--candidate", required=True, type=Path)
    complete_parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "exercise-a")
    args = parser.parse_args()
    if args.stage == "seed":
        seed(args.root, args.out)
    elif args.stage == "prepare":
        prepare(args.root, args.out)
    elif args.stage == "complete":
        complete(args.root, args.candidate, args.out)
    else:
        apply(args.root, args.out)


if __name__ == "__main__":
    main()
