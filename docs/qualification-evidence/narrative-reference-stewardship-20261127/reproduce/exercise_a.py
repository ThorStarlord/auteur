"""Exercise A: reference stewardship for Book 25, through the Working Book owner, in a disposable study.

Stages (each runs through the owner that owns it; nothing edits a persisted Book record):
    seed          seed the Spring Ledger discovery study, give its open questions identities through a disposable Architecture
                  revision, replay PR #648's applied Book 24 association (the coding agent's unedited answer recorded in that
                  evidence), and bring Book 25 up to date with the Architecture (a whole-Book revision that stops citing the concept
                  the Architecture removed; study setup, not an association). Records Book 25's positional observation.
    prepare       ask for Book 25's association exactly as the served control does: an element and a current question, by identity.
                  Writes the request a coding agent reads, and the observation the author saw.
    complete      validate the coding agent's unedited Book object through the owner and store the review. Nothing is applied.
    apply         apply the reviewed request through the owner, then read the question-centred reading back.

No provider is called. The coding agent for `complete` is a fresh sub-agent that is given only the request file.

Usage (each stage with the same --root):
    PYTHONPATH=src python exercise_a.py seed --root <fresh dir> --out <evidence dir>
    PYTHONPATH=src python exercise_a.py prepare --root <dir> --out <evidence dir>
    PYTHONPATH=src python exercise_a.py complete --root <dir> --candidate <json> --out <evidence dir>
    PYTHONPATH=src python exercise_a.py apply --root <dir> --out <evidence dir>
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))

import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_beginner_studio_book_impact import reconciled  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402

from auteur.beginner.studio_architecture import _candidate  # noqa: E402
from auteur.beginner.studio_architecture_question_projection import project_architecture_questions  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402
from auteur.series.working_book_architecture import (  # noqa: E402
    book_apply_review,
    book_complete,
    book_observation_stewardship,
    book_prepare,
    book_project,
    book_series_references,
)

PRIOR = REPO / "docs/qualification-evidence/question-linked-narrative-inheritance-20261127/reproduce/exercise-a"
PRIOR_CANDIDATE = PRIOR / "candidate-book24-unedited.json"
BOOK_ASSOCIATED, BOOK = 24, 25
BLIND_SPOT = "cons-conversion-blind-spot"
CONVERSION = identity_for(5)  # open question 6 in one-based prose
PRIOR_INSTRUCTION = "Check which open questions this element engages."  # the PR #648 instruction, replayed unchanged
PRIOR_TARGETS = (BLIND_SPOT,)


def store_at(root: Path) -> CanvasStore:
    return CanvasStore(root / "discovery", discovery.SPRING)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def seed(root: Path, out: Path) -> None:
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"{root} is not empty; choose a fresh directory")
    store = discovery.seed_discovery(root / "discovery")
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    # PR #648's applied association for Book 24, replayed from its unedited coding-agent answer.
    prepared = book_prepare(store, BOOK_ASSOCIATED, instruction=PRIOR_INSTRUCTION, targets=PRIOR_TARGETS)
    book_complete(store, BOOK_ASSOCIATED, build_host_agent_response(
        HostAgentRequest(**prepared["request"]), PRIOR_CANDIDATE.read_text(encoding="utf-8"),
        runtime="pr648-exercise-a-replay").model_dump())
    assert book_apply_review(store, BOOK_ASSOCIATED, prepared["pending_request_sha256"])["result"] == "applied"
    # Book 25 cites the concept the Architecture removed: a whole-Book revision brings it up to date (study setup).
    artifact = reconciled(root / "discovery", BOOK)
    prepared = book_prepare(store, BOOK, instruction="Stop citing the concept the working Architecture removed.", holistic=True)
    book_complete(store, BOOK, build_host_agent_response(HostAgentRequest(**prepared["request"]), json.dumps(artifact),
                                                         runtime="exercise-a-setup").model_dump())
    assert book_apply_review(store, BOOK, prepared["pending_request_sha256"])["result"] == "applied"
    questions = project_architecture_questions(store)
    write_json(out / "seed-summary.json", {
        "series_request_sha256": _candidate(store)["request_sha256"],
        "conversion_question": {"id": CONVERSION, "index": 5, "text": _candidate(store)["candidate"]["open_questions"][5]},
        "book_24_association": element_references(store, BOOK_ASSOCIATED),
        "book_25_observation": [row for row in book_observation_stewardship(store, BOOK)["observations"]
                                if row["element_id"] == BLIND_SPOT],
        "question_engagements_after_seed": {row["id"]: len(row.get("engagements") or []) for row in questions["questions"]},
    })


def element_references(store: CanvasStore, number: int) -> list[dict]:
    return [row for row in book_series_references(store, number)["element_question_references"]
            if row["element_id"] == BLIND_SPOT]


def prepare(root: Path, out: Path) -> None:
    store = store_at(root)
    observed = [row for row in book_observation_stewardship(store, BOOK)["observations"] if row["element_id"] == BLIND_SPOT]
    write_json(out / "observation-book25.json", observed)
    # The same body the served control sends: the element and the question the author chose, by identity.
    prepared = book_prepare(store, BOOK, associations=({"element_id": BLIND_SPOT, "question_id": CONVERSION},))
    write_json(out / "request-book25.json", prepared["request"])
    write_json(out / "book25-current-record.json", book_project(store, BOOK)["artifact"])
    print("request", prepared["request"]["request_sha256"])


def complete(root: Path, candidate: Path, out: Path) -> None:
    store = store_at(root)
    view = book_project(store, BOOK)
    result = book_complete(store, BOOK, build_host_agent_response(
        HostAgentRequest(**view["request"]), candidate.read_text(encoding="utf-8"),
        runtime="fresh-sub-agent").model_dump())
    write_json(out / "review-book25.json", book_project(store, BOOK)["review"])
    print("status", book_project(store, BOOK)["status"], json.dumps(result.get("review", {}).get("applicable")))


def apply(root: Path, out: Path) -> None:
    store = store_at(root)
    review = book_project(store, BOOK)["review"]
    result = book_apply_review(store, BOOK, review["request_sha256"])
    write_json(out / "apply-result-book25.json", {"result": result["result"], "currentness": result.get("currentness")})
    write_json(out / "element-references-after-apply.json", {
        BOOK_ASSOCIATED: element_references(store, BOOK_ASSOCIATED), BOOK: element_references(store, BOOK)})
    reading = next(row for row in project_architecture_questions(store)["questions"] if row["id"] == CONVERSION)
    write_json(out / "question-reading-after-apply.json", {
        "engagements": reading["engagements"], "positional_leads": reading["positional_leads"]})
    print("applied", result["result"], "engagements", [(row["book_number"], row["element_id"]) for row in reading["engagements"]])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stage", choices=["seed", "prepare", "complete", "apply"])
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    if args.stage == "seed":
        seed(root, out)
    elif args.stage == "prepare":
        prepare(root, out)
    elif args.stage == "complete":
        complete(root, args.candidate.resolve(), out)
    else:
        apply(root, out)


if __name__ == "__main__":
    main()
