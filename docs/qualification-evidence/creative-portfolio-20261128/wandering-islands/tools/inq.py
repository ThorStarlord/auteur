"""Native ordinary-inquiry arm: prepare and complete an Architecture inquiry through its own owner (same developments, same question)."""
import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry, _inquiry_root,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

CANVAS = "wandering-islands"
ARCH_SHA = "ec7f3d8127683a001ffb99cca40737a1c69f6c6d2639610aa8c6c56c986d465a"


def main(argv):
    cmd = argv[0]
    if cmd == "prepare":
        project, spec_path, prep = argv[1], argv[2], argv[3]
        spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
        store = CanvasStore(Path(project), CANVAS)
        intent = {"canvas_id": CANVAS, "operation": spec["operation"], "expected_candidate_request_sha256": ARCH_SHA,
                  "anchors": spec["anchors"], "author_text": spec["author_text"]}
        prepare_architecture_inquiry(store, intent)
        base = _inquiry_root(store)
        sha = json.loads((base / "latest_request.json").read_text(encoding="utf-8"))["request_sha256"]
        request = json.loads((base / "requests" / sha / "request.json").read_text(encoding="utf-8"))
        Path(prep).write_text(json.dumps({"request": request}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"request_sha256": sha, "prep": prep}, indent=2))
    elif cmd == "complete":
        project, prep, answer = argv[1], argv[2], argv[3]
        store = CanvasStore(Path(project), CANVAS)
        request = HostAgentRequest(**json.loads(Path(prep).read_text(encoding="utf-8"))["request"])
        text = Path(answer).read_text(encoding="utf-8")
        json.loads(text)
        reply = build_host_agent_response(request, text, runtime="wandering-islands-fresh-agent").model_dump()
        complete_architecture_inquiry(store, reply)
        print(json.dumps({"completed": True}))
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main(sys.argv[1:])
