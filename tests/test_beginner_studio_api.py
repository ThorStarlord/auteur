"""HTTP integration exercises actual canvas command dispatch and recovery."""
from __future__ import annotations

import json

import pytest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from auteur.beginner.server import BeginnerWorkspaceServer


def call(base, method, route, body=None):
    request = Request(base + route, method=method,
                      data=None if body is None else json.dumps(body).encode("utf-8"),
                      headers={"Content-Type": "application/json"})
    with urlopen(request) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_canvas_http_roundtrip_and_stale_conflict(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        url = "/api/beginner/studio/canvases"
        code, empty = call(base, "POST", url, {"canvas_id": "my-notes"})
        assert code == 201 and empty["revision"] == 0
        mutation = {"command_id": "create-first", "expected_revision": 0,
                    "payload": {"item": {"id": "first", "kind": "note", "title": "A fragment", "content": "Opening idea"},
                                "position": {"x": 40, "y": 50}}}
        code, updated = call(base, "POST", url + "/my-notes/commands/create-item", mutation)
        assert code == 200 and updated["revision"] == 1
        code, reloaded = call(base, "GET", url + "/my-notes")
        assert reloaded["items"][0]["content"] == "Opening idea"
        code, retry = call(base, "POST", url + "/my-notes/commands/create-item", mutation)
        assert retry["revision"] == 1 and len(retry["items"]) == 1
        mutation["command_id"] = "stale-new"
        with pytest.raises(HTTPError) as error:
            call(base, "POST", url + "/my-notes/commands/create-item", mutation)
        assert error.value.code == 409
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
