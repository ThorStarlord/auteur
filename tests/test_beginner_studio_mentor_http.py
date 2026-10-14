"""HTTP contract: mentor preparation and advice never silently mutate the canvas."""
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_store import CanvasStore


def request(base, method, path, data=None):
    packet = None if data is None else json.dumps(data).encode("utf-8")
    req = Request(base + path, method=method, data=packet,
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=8) as response:
        return response.status, json.load(response)


def test_live_http_mentoring_roundtrip_and_canvas_authority(tmp_path):
    canvas = CanvasStore(tmp_path, "mentor-http")
    canvas.create()
    canvas.apply("create-item", expected_revision=0, command_id="create-first",
                 payload={"item": {"id": "hero", "kind": "note", "title": "Helpful hero",
                                   "content": "Growth through generosity"},
                          "position": {"x": 10, "y": 20}})
    before = canvas.load().model_dump(mode="json")
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    root = f"http://127.0.0.1:{server.port}"
    url = "/api/beginner/studio/canvases/mentor-http/mentor"
    try:
        assert request(root, "GET", url)[1]["status"] == "not_started"
        code, pending = request(root, "POST", url + "/prepare",
                                {"focus_id": "hero", "focus_kind": "working",
                                 "purpose": "question", "author_reply": "Keep him hopeful."})
        assert code == 202 and pending["status"] == "awaiting_host_agent"
        assert pending["author_reply"] == "Keep him hopeful."
        req = HostAgentRequest(**pending["request"])
        advice = {"schema_version": 1, "focus_id": "hero", "kind": "question",
                  "summary": "Consider companion independence.",
                  "question": "What decisions could only the companion make?",
                  "source_refs": ["canvas/items/hero"]}
        response = build_host_agent_response(req, json.dumps(advice)).model_dump()
        code, result = request(root, "POST", url + "/host-agent-response", response)
        assert code == 200 and result["status"] == "ready"
        assert result["advice"]["kind"] == "question"
        assert request(root, "GET", url)[1]["advice"] == result["advice"]
        assert canvas.load().model_dump(mode="json") == before
    finally:
        server.stop()
        thread.join(timeout=3)
        assert not thread.is_alive()


def test_live_http_rejects_unknown_focus_and_no_canvas(tmp_path):
    store = CanvasStore(tmp_path, "mentor-safety")
    store.create()
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    root = f"http://127.0.0.1:{server.port}"
    try:
        with pytest.raises(HTTPError) as failed:
            request(root, "POST", "/api/beginner/studio/canvases/mentor-safety/mentor/prepare",
                    {"focus_id": "missing", "focus_kind": "working"})
        assert failed.value.code == 400
        with pytest.raises(HTTPError) as failed:
            request(root, "GET", "/api/beginner/studio/canvases/does-not-exist/mentor")
        assert failed.value.code == 404
    finally:
        server.stop()
        thread.join(timeout=3)
        assert not thread.is_alive()
