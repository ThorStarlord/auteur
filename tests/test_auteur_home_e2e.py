from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from urllib.request import Request, urlopen

from auteur.beginner.server import BeginnerWorkspaceServer


@contextmanager
def running_server(tmp_path: Path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        yield server
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def _base(server: BeginnerWorkspaceServer) -> str:
    return f"http://127.0.0.1:{server.port}"


def _get_json(server: BeginnerWorkspaceServer, path: str) -> dict:
    with urlopen(_base(server) + path) as response:
        assert response.status == 200
        return json.loads(response.read().decode("utf-8"))


def _post_json(server: BeginnerWorkspaceServer, path: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        _base(server) + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def test_home_to_new_story_to_story_architecture_round_trip(tmp_path: Path) -> None:
    premise = (
        "A young superhero begins noticing impossible inconsistencies around the "
        "people closest to him and starts investigating what they are hiding."
    )
    with running_server(tmp_path) as server:
        with urlopen(_base(server) + "/") as response:
            html = response.read().decode("utf-8")
            assert response.status == 200
            assert "<title>Auteur</title>" in html
            assert "What story do you want to tell?" in html
            assert 'id="new-story-form"' in html
            assert "Workspace ID" in html  # retained only in the advanced disclosure

        assert _get_json(server, "/api/beginner/health") == {
            "app": "auteur",
            "surface": "beginner",
            "status": "ok",
        }
        assert _get_json(server, "/api/beginner/workspaces") == {"workspaces": []}

        status, created = _post_json(
            server,
            "/api/beginner/workspaces",
            {
                "command_id": "home-create-1",
                "premise": premise,
            },
        )

        assert status == 201
        workspace_id = created["workspace"]["workspace_id"]
        assert workspace_id.startswith("workspace-")
        assert created["primary_surface"] == "architecture"
        assert created["canonical_refs"] == []

        recent = _get_json(server, "/api/beginner/workspaces")["workspaces"]
        assert len(recent) == 1
        assert recent[0]["workspace_id"] == workspace_id
        assert recent[0]["project_id"] == workspace_id
        assert recent[0]["title"].startswith("A young superhero")
        assert recent[0]["accepted_milestones"] == []

        reopened = _get_json(server, f"/api/beginner/workspaces/{workspace_id}")
        assert reopened["workspace"]["workspace_id"] == workspace_id
        assert reopened["primary_surface"] == "architecture"


def test_recent_story_index_skips_damaged_workspace_without_blocking_home(tmp_path: Path) -> None:
    with running_server(tmp_path) as server:
        _, created = _post_json(
            server,
            "/api/beginner/workspaces",
            {"command_id": "healthy", "premise": "A courier finds a map that changes each night."},
        )
        healthy_id = created["workspace"]["workspace_id"]

        damaged = tmp_path / ".auteur" / "beginner" / "workspaces" / "damaged"
        damaged.mkdir(parents=True)
        (damaged / "session.json").write_text("{not-json", encoding="utf-8")

        recent = _get_json(server, "/api/beginner/workspaces")["workspaces"]
        assert [item["workspace_id"] for item in recent] == [healthy_id]
