"""Seed a disposable project for the Book-discovery-to-Architecture study.

It is the state the Architecture-to-Book impact study ended in (#635), rebuilt through the owners:

1. Spring Ledger W6 with working Books 24 and 25 (``seed_book_impact_study.seed_current``).
2. A working Architecture revision, applied through the Studio's review path, that rewords the Ledger engine
   (it now also records hours) and removes the Gate Table.
3. Book 24 reconciled through its own owner: a whole-Book revision whose answer is the coding agent's
   recorded candidate from the #635 authentic run
   (``docs/qualification-evidence/atelier-book-impact-20261123/authentic/coding-agent-candidate.json``),
   reviewed and applied. Book 24 is then current; Book 25 is not.

That candidate recorded, among others, an unresolved element ``unk-tally-hours`` that cites the Ledger engine
(``eng_ledger``): whether the stewardship tally the Council keeps is the ledger's hours column or a separate
count. That is a Book-level question resting on an Architecture-level decision, recorded by the Book owner.

Nothing is accepted as story canon and no provider is called.

Usage:
    PYTHONPATH=src python scripts/seed_book_discovery_study.py --root <disposable dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import seed_book_impact_study as impact  # noqa: E402

from auteur.beginner.studio_book_development import (  # noqa: E402
    apply_book_revision, complete_book_revision, prepare_book_revision, project_book_development,
)
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402

SPRING = impact.SPRING
RECORDED_CANDIDATE = REPO / "docs/qualification-evidence/atelier-book-impact-20261123/authentic/coding-agent-candidate.json"
RECORDED_INSTRUCTION = REPO / "docs/qualification-evidence/atelier-book-impact-20261123/authentic/instruction.txt"
DISCOVERY = "unk-tally-hours"   # Book 24's unresolved question about the Ledger engine
LEDGER = "eng_ledger"


def reconcile_book_24(project: Path) -> None:
    view = project_book_development(project, SPRING, 24)
    view = prepare_book_revision(project, SPRING, 24, {
        "instruction": RECORDED_INSTRUCTION.read_text(encoding="utf-8").strip()[:3900], "holistic": True,
        "expected_book_request_sha256": view["book"]["request_sha256"]})
    candidate = RECORDED_CANDIDATE.read_text(encoding="utf-8")
    view = complete_book_revision(project, SPRING, 24, build_host_agent_response(
        HostAgentRequest(**view["request"]), candidate, runtime="book-discovery-seed").model_dump())
    apply_book_revision(project, SPRING, 24, {"request_sha256": view["pending"]["request_sha256"]})


def seed_discovery(project: Path) -> CanvasStore:
    store = impact.seed_current(project)
    impact.reword_and_remove(store)
    reconcile_book_24(project)
    return store


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path, help="disposable directory for the project")
    args = parser.parse_args()
    root = args.root.resolve()
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"{root} is not empty; choose a fresh directory")
    root.mkdir(parents=True, exist_ok=True)
    seed_discovery(root / "discovery")
    print(json.dumps({"discovery": str(root / "discovery"), "canvas": SPRING}, indent=2))


if __name__ == "__main__":
    main()
