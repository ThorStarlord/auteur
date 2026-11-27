"""Exercises B and C: cross-Book deliberation and narrative opportunity discovery, through the production inquiry and discovery owners.

Both run on the study that Exercise A leaves behind (Book 24 and Book 25 each engage the conversion settlement question, and
Book 24's association is PR #648's). Each stage writes a request for a fresh coding agent or stores its unedited answer.

    deliberation-prepare  a comparison of the conversion settlement question with the Mill Compact question. The author text is
                          neutral: it asks whether the questions concern one problem, and it does not name an expected conclusion.
    deliberation-complete the fresh agent's unedited answer, through the inquiry owner. Stores the result and its standing.
    discovery-prepare     a discovery request with no author goal: the agent chooses what deserves investigation.
    discovery-complete    the fresh agent's unedited answer, through the discovery owner.

No provider is called. The fresh agents are sub-agents given only the request files.

Usage (the same --root throughout, after the Exercise A stages in reproduce/exercise_a.py):
    PYTHONPATH=src python exercise_bc.py deliberation-prepare --root <root> --out <dir>
    PYTHONPATH=src python exercise_bc.py deliberation-complete --root <root> --candidate <json> --out <dir>
    PYTHONPATH=src python exercise_bc.py discovery-prepare --root <root> --out <dir>
    PYTHONPATH=src python exercise_bc.py discovery-complete --root <root> --candidate <json> --out <dir>
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
from test_persistent_narrative_questions import identity_for  # noqa: E402

from auteur.beginner.studio_architecture import _candidate  # noqa: E402
from auteur.beginner.studio_architecture_deliberation import build_question_deliberation  # noqa: E402
from auteur.beginner.studio_architecture_discovery import (  # noqa: E402
    complete_architecture_discovery,
    prepare_architecture_discovery,
    project_architecture_discoveries,
)
from auteur.beginner.studio_architecture_inquiry import (  # noqa: E402
    complete_architecture_inquiry,
    prepare_architecture_inquiry,
)
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402

CONVERSION = identity_for(5)
COMPACT = identity_for(6)
AUTHOR_TEXT = ("Do these two open questions concern one problem in the story, or do the Working Books that engage them "
               "develop different parts of it? Say what the records support, and what they leave undecided.")


def store_at(root: Path) -> CanvasStore:
    return CanvasStore(root / "discovery", discovery.SPRING)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def deliberation_prepare(root: Path, out: Path) -> None:
    store = store_at(root)
    intent = {"version": 1, "canvas_id": store.canvas_id, "operation": "compare", "target": "current",
              "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
              "anchors": [{"kind": "question", "id": CONVERSION}, {"kind": "question", "id": COMPACT}],
              "author_text": AUTHOR_TEXT}
    request = prepare_architecture_inquiry(store, intent)["request"]
    write_json(out / "request-B.json", request)
    write_json(out / "packet-B.json", json.loads(request["user"])["deliberation"])
    print("B request", request["request_sha256"])


def deliberation_complete(root: Path, candidate: Path, out: Path) -> None:
    store = store_at(root)
    request = json.loads((out / "request-B.json").read_text(encoding="utf-8"))
    response = build_host_agent_response(HostAgentRequest(**request), candidate.read_text(encoding="utf-8"),
                                         runtime="fresh-sub-agent")
    complete_architecture_inquiry(store, response.model_dump())
    from auteur.beginner.studio_architecture_deliberation import deliberation_standing
    packet = json.loads(request["user"])["deliberation"]
    write_json(out / "standing-B.json", deliberation_standing(store, packet))
    print("B completed")


def discovery_prepare(root: Path, out: Path) -> None:
    store = store_at(root)
    request = prepare_architecture_discovery(store, goal=None)["pending"]["request"]
    write_json(out / "request-C.json", request)
    write_json(out / "packet-C.json", json.loads(request["user"])["discovery_packet"])
    print("C request", request["request_sha256"])


def discovery_complete(root: Path, candidate: Path, out: Path) -> None:
    store = store_at(root)
    request = json.loads((out / "request-C.json").read_text(encoding="utf-8"))
    response = build_host_agent_response(HostAgentRequest(**request), candidate.read_text(encoding="utf-8"),
                                         runtime="fresh-sub-agent")
    complete_architecture_discovery(store, response.model_dump())
    write_json(out / "result-C.json", project_architecture_discoveries(store)["discoveries"][0])
    print("C completed")


def possibility_prepare(root: Path, out: Path, discovery_sha: str, possibility_id: str) -> None:
    """Take one discovered possibility into the existing deliberation workflow, on exactly the questions it names."""
    store = store_at(root)
    discovery = next(row for row in project_architecture_discoveries(store)["discoveries"]
                     if row["request_sha256"] == discovery_sha)
    possibility = next(row for row in discovery["possibilities"] if row["id"] == possibility_id)
    intent = {"version": 1, "canvas_id": store.canvas_id, "operation": "challenge", "target": "current",
              "expected_candidate_request_sha256": _candidate(store)["request_sha256"],
              "anchors": [{"kind": "question", "id": question} for question in possibility["questions"]],
              "author_text": ("Test the discovered possibility against the recorded evidence: what does each element and "
                              "mechanism it cites actually record, what is interpretation, and what would the record have to "
                              "show for the possibility to hold?"),
              "from_discovery": {"request_sha256": discovery_sha, "possibility_id": possibility_id}}
    request = prepare_architecture_inquiry(store, intent)["request"]
    write_json(out / "request-C-possibility-deliberation.json", request)
    write_json(out / "packet-C-possibility-deliberation.json", json.loads(request["user"]).get("deliberation"))
    print("possibility deliberation request", request["request_sha256"])


def possibility_complete(root: Path, candidate: Path, out: Path) -> None:
    store = store_at(root)
    request = json.loads((out / "request-C-possibility-deliberation.json").read_text(encoding="utf-8"))
    response = build_host_agent_response(HostAgentRequest(**request), candidate.read_text(encoding="utf-8"),
                                         runtime="fresh-sub-agent")
    complete_architecture_inquiry(store, response.model_dump())
    print("possibility deliberation completed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stage", choices=["deliberation-prepare", "deliberation-complete", "discovery-prepare",
                                          "discovery-complete", "possibility-prepare", "possibility-complete"])
    parser.add_argument("--discovery", help="the discovery's request sha256 (possibility-prepare)")
    parser.add_argument("--possibility", help="the possibility id, for example p2 (possibility-prepare)")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    if args.stage == "deliberation-prepare":
        deliberation_prepare(root, out)
    elif args.stage == "deliberation-complete":
        deliberation_complete(root, args.candidate.resolve(), out)
    elif args.stage == "discovery-prepare":
        discovery_prepare(root, out)
    elif args.stage == "possibility-prepare":
        possibility_prepare(root, out, args.discovery, args.possibility)
    elif args.stage == "possibility-complete":
        possibility_complete(root, args.candidate.resolve(), out)
    else:
        discovery_complete(root, args.candidate.resolve(), out)


if __name__ == "__main__":
    main()
