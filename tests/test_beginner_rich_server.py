from __future__ import annotations

import json
from contextlib import contextmanager
from urllib.request import Request, urlopen

from auteur.beginner.server import BeginnerRuntimeDependencies, BeginnerWorkspaceServer
from tests.fixtures.beginner_hybrid_mystery import (
    CountingDiscoveryRecommender,
    HYBRID_ANALYSIS,
    HYBRID_DISCOVERY,
    HYBRID_MYSTERY_PREMISE,
    StaticArchitectureAnalyzer,
)


@contextmanager
def running_rich_server(tmp_path):
    dependencies = BeginnerRuntimeDependencies(
        architecture_analyzer=StaticArchitectureAnalyzer(HYBRID_ANALYSIS),
        discovery_recommender=CountingDiscoveryRecommender(HYBRID_DISCOVERY),
    )
    server = BeginnerWorkspaceServer(tmp_path, port=0, dependencies=dependencies)
    thread = server.start_in_thread()
    try:
        yield server
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def _base(server) -> str:
    return f"http://127.0.0.1:{server.port}"


def post_json(server, path: str, payload: dict):
    request = Request(
        f"{_base(server)}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def hybrid_create_payload(
    command_id: str = "create-hybrid-rich",
    workspace_id: str = "hybrid-rich",
) -> dict[str, object]:
    return {
        "command_id": command_id,
        "workspace_id": workspace_id,
        "project_id": "hybrid-project",
        "guidance_genre": "mystery",
        "premise": HYBRID_MYSTERY_PREMISE,
    }


def command(server, workspace_id: str, slug: str, projection: dict, payload: dict):
    return post_json(
        server,
        f"/api/beginner/workspaces/{workspace_id}/commands/{slug}",
        {
            "workspace_id": workspace_id,
            "expected_session_version": projection["session_version"],
            "command_id": f"{slug}-{projection['session_version']}",
            "payload": payload,
        },
    )[1]


def test_http_fresh_workspace_returns_story_orientation_before_decision_card(tmp_path) -> None:
    with running_rich_server(tmp_path) as server:
        _, projection = post_json(
            server,
            "/api/beginner/workspaces",
            hybrid_create_payload(),
        )
        assert projection["primary_surface"] == "architecture"
        assert projection["story_orientation"]["heading"] == "Here is what Auteur sees"
        assert projection["decision_card"] is None


def test_http_rich_routes_reach_discovery_and_identity_candidate(tmp_path) -> None:
    with running_rich_server(tmp_path) as server:
        _, projection = post_json(
            server,
            "/api/beginner/workspaces",
            hybrid_create_payload(),
        )
        projection = command(server, "hybrid-rich", "continue-architecture", projection, {})
        assert projection["primary_surface"] == "discovery"
        projection = command(
            server,
            "hybrid-rich",
            "select-direction",
            projection,
            {"direction_id": "direction-investigative-betrayal"},
        )
        projection = command(server, "hybrid-rich", "accept-direction", projection, {})
        assert projection["primary_surface"] == "story_identity"
        assert projection["identity_candidate"]["title"] == "The Hero Who Needs the Truth"


def test_http_architecture_refinement_route_is_noncanonical(tmp_path) -> None:
    with running_rich_server(tmp_path) as server:
        _, projection = post_json(
            server,
            "/api/beginner/workspaces",
            hybrid_create_payload(),
        )
        component = next(
            item
            for facet in projection["story_orientation"]["story_map_facets"]
            for item in facet["components"]
            if item["label"] == "Superhero fiction"
        )
        projection = command(
            server,
            "hybrid-rich",
            "suppress-architecture-component",
            projection,
            {
                "component_id": component["component_id"],
                "rationale": "Keep superhero material in the background.",
            },
        )
        assert projection["canonical_refs"] == []
        changed = next(
            item
            for facet in projection["story_orientation"]["story_map_facets"]
            for item in facet["components"]
            if item["component_id"] == component["component_id"]
        )
        assert changed["activation"] == "suppressed"
