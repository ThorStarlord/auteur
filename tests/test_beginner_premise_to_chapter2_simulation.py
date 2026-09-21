"""Simulation-first product probe for the Beginner premise-to-Chapter-2 journey.

This is mechanical/workflow evidence only. It does not claim that a real author
finds the workflow useful, understandable, or creatively satisfying.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from urllib.request import Request, urlopen

from auteur.beginner.application import BeginnerWorkspaceApplication
from auteur.beginner.continuation import build_contextual_chapter_plan
from auteur.beginner.post_draft import (
    accept_latest_chapter,
    project_chapter_outcome,
    project_draft_review,
)
from auteur.beginner.server import BeginnerRuntimeDependencies, BeginnerWorkspaceServer
from tests.fixtures.beginner_hybrid_mystery import (
    CountingDiscoveryRecommender,
    HYBRID_ANALYSIS,
    HYBRID_DISCOVERY,
    HYBRID_MYSTERY_PREMISE,
    StaticArchitectureAnalyzer,
)


@contextmanager
def _running_server(tmp_path: Path):
    dependencies = BeginnerRuntimeDependencies(
        architecture_analyzer=StaticArchitectureAnalyzer(HYBRID_ANALYSIS),
        discovery_recommender=CountingDiscoveryRecommender(HYBRID_DISCOVERY),
    )
    server = BeginnerWorkspaceServer(tmp_path, port=0, dependencies=dependencies)
    thread = server.start_in_thread()
    try:
        yield server, dependencies
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def _post(server: BeginnerWorkspaceServer, path: str, payload: dict[str, object]) -> dict[str, object]:
    request = Request(
        f"http://127.0.0.1:{server.port}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        assert response.status in {200, 201}
        return json.loads(response.read().decode("utf-8"))


def _command(
    server: BeginnerWorkspaceServer,
    workspace_id: str,
    slug: str,
    projection: dict[str, object],
    payload: dict[str, object] | None = None,
) -> dict[str, object]:
    return _post(
        server,
        f"/api/beginner/workspaces/{workspace_id}/commands/{slug}",
        {
            "workspace_id": workspace_id,
            "expected_session_version": projection["session_version"],
            "command_id": f"sim-{slug}-{projection['session_version']}",
            "payload": payload or {},
        },
    )


def _accept_foundation(
    server: BeginnerWorkspaceServer,
    workspace_id: str,
    projection: dict[str, object],
) -> dict[str, object]:
    orientation = projection["story_orientation"]
    component = next(
        item
        for facet in orientation["story_map_facets"]
        for item in facet["components"]
        if item["label"] == "Erotic betrayal melodrama"
    )
    projection = _command(
        server,
        workspace_id,
        "choose-architecture-alternative",
        projection,
        {
            "component_id": component["component_id"],
            "alternative_label": "Campy erotic melodrama",
            "rationale": "Scripted novice follows one explicit interpretation.",
        },
    )
    projection = _command(server, workspace_id, "continue-architecture", projection)
    direction_id = projection["discovery"]["recommended_direction_id"]
    projection = _command(
        server,
        workspace_id,
        "select-direction",
        projection,
        {"direction_id": direction_id},
    )
    projection = _command(server, workspace_id, "accept-direction", projection)
    assert projection["mapping_preview"]["ready_to_accept"] is True
    projection = _command(server, workspace_id, "accept-identity", projection)

    while not projection["reviews"]["story_structure"]["review_available"]:
        card = projection["decision_card"]
        assert card is not None
        projection = _command(
            server,
            workspace_id,
            "select",
            projection,
            {"card_id": card["card_id"], "option": card["recommendation"]},
        )
        if projection["reviews"]["story_structure"]["review_available"]:
            break
        projection = _command(
            server,
            workspace_id,
            "continue",
            projection,
            {"card_id": card["card_id"]},
        )

    projection = _command(
        server,
        workspace_id,
        "open-review",
        projection,
        {"stage": "story_structure"},
    )
    assert projection["reviews"]["story_structure"]["ready_to_accept"] is True
    return _command(server, workspace_id, "accept-structure", projection)


def test_scripted_novice_reaches_contextual_chapter_two_without_mechanical_dead_end(
    tmp_path: Path,
) -> None:
    workspace_id = "simulated-product-probe"

    with _running_server(tmp_path) as (server, dependencies):
        projection = _post(
            server,
            "/api/beginner/workspaces",
            {
                "command_id": "sim-create",
                "workspace_id": workspace_id,
                "project_id": "simulated-product-probe",
                "guidance_genre": "mystery",
                "premise": HYBRID_MYSTERY_PREMISE,
            },
        )
        projection = _accept_foundation(server, workspace_id, projection)

        assert {ref["milestone_id"] for ref in projection["canonical_refs"]} == {
            "story_direction",
            "story_identity",
            "whole_story_structure",
        }

        app = BeginnerWorkspaceApplication(
            tmp_path,
            workspace_id,
            architecture_analyzer=dependencies.architecture_analyzer,
            discovery_recommender=dependencies.discovery_recommender,
        )
        continuation = app.projection()

        steps = (
            ("propose-outline", app.propose_outline),
            ("accept-outline", app.accept_outline),
            ("propose-chapter-plan", app.propose_chapter_plan),
            ("accept-chapter-plan", app.accept_chapter_plan),
            ("propose-scene-plans", app.propose_scene_plans),
            ("accept-scene-plans", app.accept_scene_plans),
            ("prepare-draft-handoff", app.prepare_draft_handoff),
        )
        for index, (expected_action, transition) in enumerate(steps, start=1):
            assert expected_action in continuation.available_actions
            continuation = transition(
                expected_session_version=continuation.session_version,
                command_id=f"sim-continuation-{index}",
            )

        assert continuation.continuation.draft_handoff is not None
        assert continuation.continuation.draft_handoff.status == "ready"

        chapter_one = tmp_path / "chapters" / "01"
        chapter_one.mkdir(parents=True, exist_ok=True)
        draft = chapter_one / "draft_v1.md"
        draft.write_text(
            "Maya follows the hidden witness into the archive and discovers a contradiction.",
            encoding="utf-8",
        )
        (chapter_one / "validation_v1.json").write_text(
            json.dumps({"findings": []}),
            encoding="utf-8",
        )

        review = project_draft_review(tmp_path, 1)
        assert review.source_draft == "draft_v1.md"
        assert review.blocking_findings == []

        def simulated_owner(root: Path, chapter_index: int) -> dict[str, object]:
            chapter = root / "chapters" / f"{chapter_index:02d}"
            (chapter / "final.md").write_bytes((chapter / "draft_v1.md").read_bytes())
            return {"accepted": True, "evidence": "scripted-simulation"}

        acceptance = accept_latest_chapter(
            tmp_path,
            1,
            command_id="simulated-explicit-acceptance",
            owner=simulated_owner,
        )
        assert acceptance.chapter_index == 1

        outcome = project_chapter_outcome(tmp_path, 1)
        assert outcome["accepted_expression"] == "final.md"

        chapter_two = build_contextual_chapter_plan(tmp_path, 2)
        assert chapter_two.continuation.current_chapter_index == 2
        assert chapter_two.context["prior_accepted_chapters"] == [1]
        assert chapter_two.draft_handoff_ready is True

    browser = Path("src/auteur/beginner/browser/app.js").read_text(encoding="utf-8")
    assert "post-draft-plan-next" in browser
    assert "/api/beginner/chapters/" in browser
    assert "/plan" in browser
