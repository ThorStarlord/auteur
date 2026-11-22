"""Seed a disposable project with two recorded Architecture candidates for the Atelier study.

The candidates are genuine recorded agent output already kept in the repository as
qualification evidence. They enter a canvas through the same host-agent request and
completion path the Studio uses, so the study reads them exactly as it reads an author's
working Architecture. Nothing is accepted as story canon, and no provider is called.

Usage:
    PYTHONPATH=src python scripts/seed_atelier_study.py --project <disposable dir> [--port 8793]

Then serve the project and open the printed URLs:
    PYTHONPATH=src python -m auteur.beginner.server --project <disposable dir> --port 8793
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
SPECIMENS = {
    # 18 nodes, 4 phases, 3 genre contracts: a relatively small whole-story Architecture.
    "atelier-small": {
        "candidate": REPO / "docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json",
        "vision": "A coastal mystery about maps that erase memory. Wonder, dread, and earned hope.",
    },
    # 47 nodes, 9 phases, 7 genre contracts: a dense fourteen-Book series Architecture.
    "atelier-dense": {
        "candidate": REPO / "qualification/studio-trace/artifacts/candidate-2.json",
        "vision_file": REPO / "qualification/studio-trace/artifacts/story_vision.txt",
    },
    # Constructed counterexample for the story-structure comparison: the small specimen with only its
    # governing and supporting contract roles exchanged. No relationship is added or removed, so the
    # recorded governing genre (Fantasy, 14 relationships) is less connected than a supporting one
    # (Literary mystery, 20). The phases keep their own recorded roles. A test fixture, not a story.
    "atelier-counterexample": {
        "candidate": REPO / "docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json",
        "vision": ("A coastal mystery about maps that erase memory. Wonder, dread, and earned hope. "
                   "(Test fixture: the genre contracts' governing and supporting roles are exchanged.)"),
        "exchange_roles": ("governing", "supporting"),
    },
}


def exchange_roles(candidate: dict, roles: tuple[str, str]) -> dict:
    """Swap two genre-contract roles; every other record, including phase roles, is left as recorded."""
    first, second = roles
    swap = {first: second, second: first}
    for contract in candidate.get("genre_contracts", []):
        if contract.get("role") in swap:
            contract["role"] = swap[contract["role"]]
    return candidate


def seed(project: Path, canvas_id: str, spec: dict) -> None:
    candidate = json.loads(spec["candidate"].read_text(encoding="utf-8"))
    if spec.get("exchange_roles"):
        candidate = exchange_roles(candidate, spec["exchange_roles"])
    vision = spec.get("vision") or spec["vision_file"].read_text(encoding="utf-8").strip()
    store = CanvasStore(project, canvas_id)
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id=f"{canvas_id}-vision",
        payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision",
                          "content": vision}, "position": {"x": 20, "y": 50}},
    )
    waiting = prepare_architecture(store)
    request = HostAgentRequest(**waiting["request"])
    reply = build_host_agent_response(
        request, json.dumps(candidate), runtime="atelier-study-seed",
    ).model_dump()
    complete_architecture(store, reply)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", required=True, type=Path, help="disposable project directory")
    parser.add_argument("--port", type=int, default=8793)
    args = parser.parse_args()
    project = args.project.resolve()
    project.mkdir(parents=True, exist_ok=True)
    for canvas_id, spec in SPECIMENS.items():
        if (project / ".auteur/beginner/studio/canvases" / canvas_id).exists():
            print(f"{canvas_id}: already seeded")
        else:
            seed(project, canvas_id, spec)
            print(f"{canvas_id}: seeded from {spec['candidate'].relative_to(REPO)}")
    for canvas_id in SPECIMENS:
        for treatment in "ABC":
            print(f"  http://127.0.0.1:{args.port}/studio.html?canvas={canvas_id}&atelier={treatment}")


if __name__ == "__main__":
    main()
