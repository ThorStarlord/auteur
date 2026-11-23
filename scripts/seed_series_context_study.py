"""Seed disposable projects for the Atelier Series-context study.

Every record enters through its own owner, exactly as an author's project would hold it:

* ``linked``: the Spring Ledger working Series architecture (W6) and its Book 24 working Book
  architecture, both rebuilt from the qualification evidence kept on main
  (``docs/qualification-evidence/working-book-architecture-20261112``). The Book's typed
  references to W6 nodes are the only recorded links between an Architecture concept and a Book plan.
* ``context``: the dense fourteen-Book proposal (``atelier-dense``), a full Series plan
  (``series_identity.yaml``, the repository's Ash Empire test trilogy with setups and a payoff), and the
  Archive of Lies Series and Book Directions accepted through the Series journey, with the Series
  Direction revised after Book 1 was accepted. None of these records refers to the others.
* ``none``: the small proposal (``atelier-small``) and no Series or Book plan.
* ``damaged``: the Spring Ledger with Book 24, after a working Architecture revision removed a node the
  Book refers to; a malformed ``series_identity.yaml``; and an accepted Series Direction edited by hand
  after acceptance.

Nothing is accepted as story canon by the Studio and no provider is called. The Series Direction and
Book Direction acceptances are made through the Series journey service, the owner's own path.

Usage:
    PYTHONPATH=src python scripts/seed_series_context_study.py --root <disposable dir>
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from seed_atelier_study import SPECIMENS, seed as seed_atelier  # noqa: E402

from auteur.beginner.studio_architecture import (  # noqa: E402
    apply_architecture_review, complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from auteur.host_agent import HostAgentRequest, build_host_agent_response  # noqa: E402
from auteur.series.vertical_slice_models import BookDirection, SeriesDirection  # noqa: E402
from auteur.series.vertical_slice_service import SeriesVerticalSliceService  # noqa: E402
from auteur.series.working_book_architecture import book_complete, book_prepare  # noqa: E402

EVIDENCE = REPO / "docs/qualification-evidence/working-book-architecture-20261112"
SPARSE = REPO / "tests/fixtures/archive_of_lies_vertical_slice"
FULL_PLAN = REPO / "tests/fixtures/studio_series_context/series_identity.yaml"
SPRING = "spring-ledger"
# A W6 node the Book 24 record refers to; the damaged project's Architecture revision removes it.
REMOVED_NODE = "inst_gate_table"


def _reply(request: dict, payload: dict, runtime: str) -> dict:
    return build_host_agent_response(HostAgentRequest(**request), json.dumps(payload), runtime=runtime).model_dump()


def seed_spring(project: Path) -> CanvasStore:
    packet = json.loads(json.loads((EVIDENCE / "book24-prepare-request.json").read_text(encoding="utf-8"))
                        ["request"]["user"])
    source, w6 = packet["author_source"], packet["series_architecture"]["candidate"]
    store = CanvasStore(project, SPRING)
    store.create()
    items = [{**item, "kind": "note"} for item in source["story_vision"]]
    items += [{**item, "kind": "note"} for item in source["book_source"]]
    items += [{"id": item["id"], "kind": "note", "title": item["title"], "group": "Creative intentions",
               "content": item["content"], "intention_status": item["status"]}
              for item in source["creative_intentions"]]
    for i, item in enumerate(items):
        store.apply("create-item", expected_revision=store.load().revision, command_id=f"seed-{item['id']}",
                    payload={"item": item, "position": {"x": 20, "y": 40 + 160 * i}})
    waiting = prepare_architecture(store)
    complete_architecture(store, _reply(waiting["request"], w6, "series-context-seed"))
    book = book_prepare(store, 24)
    candidate = json.loads((EVIDENCE / "as-qualified/book-24-candidate.json").read_text(encoding="utf-8"))
    book_complete(store, 24, _reply(book["request"], candidate, "series-context-seed"))
    return store


def remove_node(store: CanvasStore, node_id: str) -> None:
    """A working Architecture revision, applied through the Studio's review path, that drops one node."""
    current = json.loads((store.directory / "architecture" / "current.json").read_text(encoding="utf-8"))
    revised = copy.deepcopy(current["candidate"])
    revised["nodes"] = [n for n in revised["nodes"] if n["id"] != node_id]
    revised["links"] = [link for link in revised.get("links", [])
                        if node_id not in (link.get("source"), link.get("target"))]
    waiting = prepare_architecture(store, instruction=f"Remove {node_id} from the working Architecture.")
    sha = waiting["request"]["request_sha256"]
    complete_architecture(store, _reply(waiting["request"], revised, "series-context-seed"))
    apply_architecture_review(store, sha)


def seed_sparse(project: Path) -> None:
    service = SeriesVerticalSliceService(project)
    load = lambda name: yaml.safe_load((SPARSE / name).read_text(encoding="utf-8"))  # noqa: E731
    series = SeriesDirection.model_validate(load("series_direction.yaml"))
    proposal = service.propose_series_direction(series)
    service.accept_series_direction(proposal.proposal_id, accepted_by="author (study seed)",
                                    rationale="Representative sparse Series planning fixture.")
    book = service.propose_book_direction(BookDirection.model_validate(load("book_1_direction.yaml")))
    service.accept_book_direction(book.proposal_id, accepted_by="author (study seed)")
    # The author later revises the Series Direction; Book 1 stays accepted against revision 1.
    revised = series.model_copy(update={
        "pressure": series.pressure + " Each erased witness also erases a family's claim to its own history."})
    proposal = service.propose_series_direction(revised)
    service.accept_series_direction(proposal.proposal_id, accepted_by="author (study seed)",
                                    rationale="Sharpened the Series pressure.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", required=True, type=Path, help="disposable directory for the projects")
    args = parser.parse_args()
    root = args.root.resolve()
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"{root} is not empty; choose a fresh directory")
    root.mkdir(parents=True, exist_ok=True)

    linked = root / "linked"
    seed_spring(linked)

    context = root / "context"
    seed_atelier(context, "atelier-dense", SPECIMENS["atelier-dense"])
    shutil.copyfile(FULL_PLAN, context / "series_identity.yaml")
    seed_sparse(context)

    none = root / "none"
    seed_atelier(none, "atelier-small", SPECIMENS["atelier-small"])

    damaged = root / "damaged"
    remove_node(seed_spring(damaged), REMOVED_NODE)
    (damaged / "series_identity.yaml").write_text("title: Unfinished\nbook_plans: [\n", encoding="utf-8")
    seed_sparse(damaged)
    accepted = damaged / ".auteur/series/vertical-slice/accepted/series-direction.yaml"
    accepted.write_text(accepted.read_text(encoding="utf-8").replace("Archive of Lies", "Archive of Truths"),
                        encoding="utf-8")

    for name, canvas in (("linked", SPRING), ("context", "atelier-dense"), ("none", "atelier-small"),
                         ("damaged", SPRING)):
        print(f"{name}: {root / name}  canvas={canvas}")
    print("Serve one:  PYTHONPATH=src python -m auteur.beginner.server --project <dir> --port 8796")
    print("Open:       http://127.0.0.1:8796/studio.html?canvas=<canvas>&atelier")


if __name__ == "__main__":
    main()
