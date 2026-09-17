"""Task 6: local Beginner Workspace HTTP surface tests (TDD failing first)."""

from __future__ import annotations

import json
from contextlib import contextmanager
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from auteur.beginner.server import BeginnerWorkspaceServer

SEALED_ELEVATOR_PREMISE = "A sealed elevator opens on an empty shaft."


@contextmanager
def running_server(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        yield server
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def base(server) -> str:
    return f"http://127.0.0.1:{server.port}"


def post_json(server, path: str, payload: dict):
    request = Request(
        f"{base(server)}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def get_json(server, path: str):
    with urlopen(f"{base(server)}{path}") as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def command_json(server, workspace_id: str, slug: str, projection: dict, payload: dict):
    body = {
        "workspace_id": workspace_id,
        "expected_session_version": projection["session_version"],
        "command_id": f"http-{slug}-{projection['session_version']}",
        "payload": payload,
    }
    _, result = post_json(server, f"/api/beginner/workspaces/{workspace_id}/commands/{slug}", body)
    return result


def create_payload(command_id="create-1", workspace_id="workspace-1"):
    return {
        "command_id": command_id,
        "workspace_id": workspace_id,
        "project_id": "project-1",
        "guidance_genre": "mystery",
        "premise": SEALED_ELEVATOR_PREMISE,
    }


def test_create_and_read_beginner_workspace(tmp_path):
    with running_server(tmp_path) as server:
        status, body = post_json(server, "/api/beginner/workspaces", create_payload())
        assert status == 201
        assert body["decision_card"]["stage"] == "discover"
        workspace_id = body["workspace"]["workspace_id"]
        assert workspace_id == "workspace-1"

        read_status, read_body = get_json(server, f"/api/beginner/workspaces/{workspace_id}")
        assert read_status == 200
        assert read_body["workspace"]["session_version"] == body["workspace"]["session_version"]
        assert read_body["decision_card"]["card_id"] == body["decision_card"]["card_id"]


def test_http_projection_exposes_composed_decision_and_inspector_views(tmp_path):
    with running_server(tmp_path) as server:
        _, created = post_json(server, "/api/beginner/workspaces", create_payload())
        workspace_id = created["workspace"]["workspace_id"]
        card = created["decision_card"]
        status, body = post_json(
            server,
            f"/api/beginner/workspaces/{workspace_id}/commands/select",
            {
                "workspace_id": workspace_id,
                "expected_session_version": created["session_version"],
                "command_id": "select-composed-http-1",
                "payload": {"card_id": card["card_id"], "option": card["options"][0]},
            },
        )

        assert status == 200
        assert body["decision_workspace"]["current_focus"]["question"] == card["question"]
        assert body["decision_workspace"]["options"][0]["selected"] is True
        assert body["guidance_inspector"]["authority_status"] == "DERIVED / NOT CANON"
        assert body["guidance_inspector"]["narrative_consequences"]
        assert body["guidance_inspector"]["narrative_consequences"][0]["semantic_area"] in {
            "Identity", "Structure", "Realization", "Expression"
        }


def test_root_serves_beginner_browser_entrypoint(tmp_path):
    with running_server(tmp_path) as server:
        with urlopen(f"{base(server)}/") as response:
            body = response.read().decode("utf-8")
            assert response.status == 200
            assert response.headers["Content-Type"].startswith("text/html")
            assert "Auteur Beginner Workspace" in body

        with urlopen(f"{base(server)}/app.js") as response:
            assert response.status == 200
            assert response.headers["Content-Type"].startswith("text/javascript")


def test_stale_command_returns_conflict(tmp_path):
    with running_server(tmp_path) as server:
        _, created = post_json(server, "/api/beginner/workspaces", create_payload())
        workspace_id = created["workspace"]["workspace_id"]
        version = created["workspace"]["session_version"]
        card_id = created["decision_card"]["card_id"]
        option = created["decision_card"]["options"][0]

        with _assert_http_error(409):
            post_json(
                server,
                f"/api/beginner/workspaces/{workspace_id}/commands/select",
                {
                    "workspace_id": workspace_id,
                    "expected_session_version": version - 1,
                    "command_id": "stale-1",
                    "payload": {"card_id": card_id, "option": option},
                },
            )


def test_http_surface_completes_beginner_milestones_in_order(tmp_path):
    with running_server(tmp_path) as server:
        _, projection = post_json(server, "/api/beginner/workspaces", create_payload())
        workspace_id = projection["workspace"]["workspace_id"]
        for stage, accept_slug in (("discover", "accept-direction"), ("story_identity", "accept-identity"), ("story_structure", "accept-structure")):
            while True:
                card = projection["decision_card"]
                if card is None or card["stage"] != stage:
                    break
                stage_entry = next(item for item in projection["navigator"] if item["stage"] == stage)
                if stage_entry["review_available"]:
                    break
                projection = command_json(server, workspace_id, "select", projection, {"card_id": card["card_id"], "option": card["options"][0]})
                projection = command_json(server, workspace_id, "continue", projection, {"card_id": card["card_id"]})
            projection = command_json(server, workspace_id, "open-review", projection, {"stage": stage})
            assert f"{accept_slug}" in projection["available_actions"]
            projection = command_json(server, workspace_id, accept_slug, projection, {})
        assert {ref["milestone_id"] for ref in projection["canonical_refs"]} == {
            "story_direction", "story_identity", "whole_story_structure"
        }


def test_select_command_round_trip_autosaves_without_advancing(tmp_path):
    with running_server(tmp_path) as server:
        _, created = post_json(server, "/api/beginner/workspaces", create_payload())
        workspace_id = created["workspace"]["workspace_id"]
        version = created["workspace"]["session_version"]
        card_id = created["decision_card"]["card_id"]
        option = created["decision_card"]["options"][0]

        status, body = post_json(
            server,
            f"/api/beginner/workspaces/{workspace_id}/commands/select",
            {
                "workspace_id": workspace_id,
                "expected_session_version": version,
                "command_id": "select-1",
                "payload": {"card_id": card_id, "option": option},
            },
        )
        assert status == 200
        assert body["workspace"]["session_version"] == version + 1
        assert body["decision_card"]["card_id"] == card_id
        assert body["decision_card"]["selected_option"] == option


def test_http_revision_select_is_exploratory_and_focuses_target_stage(tmp_path):
    with running_server(tmp_path) as server:
        _, projection = post_json(server, "/api/beginner/workspaces", create_payload())
        workspace_id = projection["workspace"]["workspace_id"]
        # Complete Discover through the real HTTP boundary.
        while projection["navigator"][0]["review_available"] is False:
            card = projection["decision_card"]
            projection = command_json(
                server, workspace_id, "select", projection,
                {"card_id": card["card_id"], "option": card["options"][0]},
            )
            projection = command_json(
                server, workspace_id, "continue", projection, {"card_id": card["card_id"]},
            )
        projection = command_json(server, workspace_id, "open-review", projection, {"stage": "discover"})
        projection = command_json(server, workspace_id, "accept-direction", projection, {})
        canonical = projection["canonical_refs"]
        discover_card = projection["decision_card"]
        projection = command_json(
            server, workspace_id, "open-revision", projection,
            {"revision_id": "http-revision-focus", "stage": "discover"},
        )
        assert projection["revision"]["target_stage"] == "discover"
        assert projection["decision_card"]["stage"] == "discover"
        alternate = next(option for option in discover_card["options"] if option != discover_card["selected_option"])
        projection = command_json(
            server, workspace_id, "select", projection,
            {"card_id": discover_card["card_id"], "option": alternate},
        )
        assert projection["decision_card"]["is_exploratory"] is True
        assert projection["canonical_refs"] == canonical


def test_malformed_envelope_returns_400(tmp_path):
    with running_server(tmp_path) as server:
        _, created = post_json(server, "/api/beginner/workspaces", create_payload())
        workspace_id = created["workspace"]["workspace_id"]
        with _assert_http_error(400):
            post_json(
                server,
                f"/api/beginner/workspaces/{workspace_id}/commands/select",
                {
                    "workspace_id": workspace_id,
                    # missing expected_session_version and command_id
                    "payload": {"card_id": "discover.story-experience"},
                },
            )


def test_domain_rejection_returns_422(tmp_path):
    with running_server(tmp_path) as server:
        _, created = post_json(server, "/api/beginner/workspaces", create_payload())
        workspace_id = created["workspace"]["workspace_id"]
        version = created["workspace"]["session_version"]
        # Review cannot open before every card is answered.
        with _assert_http_error(422) as payload:
            post_json(
                server,
                f"/api/beginner/workspaces/{workspace_id}/commands/open-review",
                {
                    "workspace_id": workspace_id,
                    "expected_session_version": version,
                    "command_id": "review-early",
                    "payload": {"stage": "discover"},
                },
            )
        assert "error" in payload


def test_idempotency_conflict_returns_409(tmp_path):
    with running_server(tmp_path) as server:
        _, created = post_json(server, "/api/beginner/workspaces", create_payload())
        workspace_id = created["workspace"]["workspace_id"]
        version = created["workspace"]["session_version"]
        card_id = created["decision_card"]["card_id"]
        option = created["decision_card"]["options"][0]

        status, _ = post_json(
            server,
            f"/api/beginner/workspaces/{workspace_id}/commands/select",
            {
                "workspace_id": workspace_id,
                "expected_session_version": version,
                "command_id": "dup-1",
                "payload": {"card_id": card_id, "option": option},
            },
        )
        assert status == 200
        # Reusing the same command_id for a different command kind is a receipt mismatch.
        with _assert_http_error(409):
            post_json(
                server,
                f"/api/beginner/workspaces/{workspace_id}/commands/continue",
                {
                    "workspace_id": workspace_id,
                    "expected_session_version": version + 1,
                    "command_id": "dup-1",
                    "payload": {"card_id": card_id},
                },
            )


@contextmanager
def _assert_http_error(expected_status: int):
    payload: dict = {}
    try:
        yield payload
    except HTTPError as exc:
        assert exc.code == expected_status, f"expected {expected_status}, got {exc.code}"
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            body = {}
        if isinstance(body, dict):
            payload.update(body)
        return
    raise AssertionError(f"expected HTTP {expected_status}, request succeeded")
