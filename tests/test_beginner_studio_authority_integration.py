"""Studio real HTTP boundaries do not silently create accepted narrative state."""
from __future__ import annotations

import json
from urllib.request import Request, urlopen

from auteur.beginner.server import BeginnerWorkspaceServer


def request(base, method, path, body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    with urlopen(Request(base + path, method=method, data=data,
                         headers={"Content-Type": "application/json"})) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_no_premise_to_provisional_scene_request_without_canon(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        root = "/api/beginner/studio/canvases"
        code, canvas = request(base, "POST", root, {"canvas_id": "free-notes"})
        assert code == 201 and canvas["revision"] == 0
        scene = {"id": "scene-1", "title": "Opening", "kind": "scene", "content": "",
                 "scene_premise": "A witness vanishes during questioning.",
                 "scene_intent": "Miller hears an unexpected confession."}
        code, canvas = request(base, "POST", root + "/free-notes/commands/create-item", {
            "expected_revision": 0, "command_id": "scene-first",
            "payload": {"item": scene, "position": {"x": 45, "y": 50}},
        })
        assert code == 200 and canvas["items"][0]["scene_intent"] == scene["scene_intent"]
        assert not (tmp_path / "story_identity.yaml").exists()
        code, staged = request(base, "POST", "/api/beginner/quick-draft", {
            "premise": scene["scene_premise"], "first_scene": scene["scene_intent"]
        })
        assert code == 202
        assert staged["draft"]["status"] == "awaiting_host_agent"
        assert staged["session_id"]
        assert not (tmp_path / "story_identity.yaml").exists()
        assert not (tmp_path / "relations.yaml").exists()
        code, loaded = request(base, "GET", root + "/free-notes")
        assert loaded["items"][0]["content"] == ""
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
