"""Owner-mediated steps for the Wandering Islands study (disposable project outside the repository).

Commands:
  seed-architecture <project> <vision.txt> <prep.json>
      create the canvas, record the author's Story Vision, prepare the Architecture request (the owner writes it),
      and save the exact request the owner returned.
  complete-architecture <project> <prep.json> <answer.json>
      complete the stored request through the owner with the agent's unedited answer.
  prepare-synthesis <project> <spec.json> <prep.json>
      prepare a synthesis through the owner. spec.json: {"question": ..., "developments": [...], "culmination": ... or null,
      "handoffs": [...] (optional), "criticism": [...] (optional), "prior": sha (optional)}
  complete-synthesis <project> <prep.json> <answer.json>
  prepare-verification <project> <synthesis_sha> <claim> <prep.json>
  complete-verification <project> <prep.json> <answer.json>
  project <project>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture, project_architecture
from auteur.beginner.studio_architecture_synthesis import (
    complete_architecture_synthesis, prepare_architecture_synthesis, project_architecture_synthesis,
)
from auteur.beginner.studio_architecture_verification import (
    complete_claim_verification, prepare_claim_verification, project_claim_verifications,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

CANVAS = "wandering-islands"


def store_for(project: str) -> CanvasStore:
    return CanvasStore(Path(project), CANVAS)


def save_prep(path: str, request: dict, extra: dict | None = None) -> None:
    body = {"request": request, **(extra or {})}
    Path(path).write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")


def load_prep(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def reply_for(request: dict, answer_path: str) -> dict:
    text = Path(answer_path).read_text(encoding="utf-8")
    json.loads(text)  # refuse answers that are not JSON before the owner sees them
    return build_host_agent_response(HostAgentRequest(**request), text, runtime="wandering-islands-fresh-agent").model_dump()


def main(argv: list[str]) -> None:
    cmd, rest = argv[0], argv[1:]
    if cmd == "seed-architecture":
        project, vision_path, prep = rest
        store = store_for(project)
        store.create()
        vision = Path(vision_path).read_text(encoding="utf-8").strip()
        store.apply("create-item", expected_revision=0, command_id="wi-vision",
                    payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision", "content": vision},
                             "position": {"x": 20, "y": 50}})
        waiting = prepare_architecture(store)
        save_prep(prep, waiting["request"])
        print(json.dumps({"request_sha256": waiting["request"]["request_sha256"], "prep": prep}, indent=2))
    elif cmd == "complete-architecture":
        project, prep, answer = rest
        store = store_for(project)
        view = complete_architecture(store, reply_for(load_prep(prep)["request"], answer))
        print(json.dumps({"completed": True, "keys": sorted(view.keys())[:12]}, indent=2))
    elif cmd == "prepare-synthesis":
        project, spec_path, prep = rest
        spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
        store = store_for(project)
        kwargs = {k: spec[k] for k in ("culmination", "handoffs", "criticism", "prior") if spec.get(k) is not None}
        waiting = prepare_architecture_synthesis(store, question=spec["question"], developments=spec["developments"], **kwargs)
        save_prep(prep, waiting["request"], {"developments": spec["developments"], "question": spec["question"]})
        print(json.dumps({"request_sha256": waiting["request"]["request_sha256"], "prep": prep}, indent=2))
    elif cmd == "complete-synthesis":
        project, prep, answer = rest
        store = store_for(project)
        view = complete_architecture_synthesis(store, reply_for(load_prep(prep)["request"], answer))
        print(json.dumps({"completed": True}, indent=2))
    elif cmd == "prepare-verification":
        project, sha, claim, prep = rest
        store = store_for(project)
        waiting = prepare_claim_verification(store, synthesis_request_sha256=sha, claim=claim)
        save_prep(prep, waiting["request"])
        print(json.dumps({"request_sha256": waiting["request"]["request_sha256"], "prep": prep}, indent=2))
    elif cmd == "complete-verification":
        project, prep, answer = rest
        store = store_for(project)
        complete_claim_verification(store, reply_for(load_prep(prep)["request"], answer))
        print(json.dumps({"completed": True}, indent=2))
    elif cmd == "project":
        store = store_for(rest[0])
        print(json.dumps(project_architecture_synthesis(store), ensure_ascii=False, indent=2)[:3000])
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main(sys.argv[1:])
