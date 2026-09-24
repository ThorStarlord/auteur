"""Synthetic browser E2E walkthrough for the Beginner action-hierarchy claims.

Owner-directed synthetic acceptance: launches the real no-provider Beginner
server, drives the documented HTTP command contract end to end with the owner's
young-aspiring-superhero premise, fetches the served browser bundle, and asserts
the four experiential claims programmatically:

1. transition salience after Whole-Story Structure acceptance;
2. a single obvious primary next action;
3. integrated narrative explanation with honest unknowns;
4. credible deterministic fallback with explicit author choice.

This is synthetic/agent evidence. It does not claim that a human finds the
workflow useful, understandable, or creatively satisfying; it replaces the
manual walkthrough gate only because the owner explicitly authorized synthetic
acceptance for this package.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from urllib.request import Request, urlopen

from auteur.beginner.server import (
    BeginnerRuntimeDependencies,
    BeginnerWorkspaceServer,
    default_runtime_dependencies,
)

PREMISE = (
    "A young aspiring superhero grows up believing that courage, loyalty, and doing "
    "the right thing will eventually earn him the life he dreams of. As he builds his "
    "identity and relationships, strange inconsistencies begin appearing around the "
    "people closest to him. What initially seems like ordinary romantic and social "
    "tension gradually becomes a mystery about betrayal, hidden identities, and forces "
    "operating beyond his understanding."
)

CONTINUATION_ACTIONS = {
    "propose-outline",
    "accept-outline",
    "propose-chapter-plan",
    "accept-chapter-plan",
    "propose-scene-plans",
    "accept-scene-plans",
    "prepare-draft-handoff",
    "review-chapter-1",
    "review-stale-continuation",
}


@contextmanager
def _running_server(tmp_path: Path):
    dependencies: BeginnerRuntimeDependencies = default_runtime_dependencies()
    server = BeginnerWorkspaceServer(tmp_path, port=0, dependencies=dependencies)
    thread = server.start_in_thread()
    try:
        yield server
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def _get(server: BeginnerWorkspaceServer, path: str) -> tuple[str, str]:
    with urlopen(f"http://127.0.0.1:{server.port}{path}") as response:
        assert response.status == 200
        return response.headers.get("Content-Type", ""), response.read().decode("utf-8")


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
            "command_id": f"synthetic-{slug}-{projection['session_version']}",
            "payload": payload or {},
        },
    )


def _answer_stage(
    server: BeginnerWorkspaceServer,
    workspace_id: str,
    projection: dict[str, object],
    stage: str,
) -> dict[str, object]:
    while True:
        entry = next(item for item in projection["navigator"] if item["stage"] == stage)
        if entry["review_available"]:
            return projection
        card = projection["decision_card"]
        assert card is not None and card["stage"] == stage
        projection = _command(
            server,
            workspace_id,
            "select",
            projection,
            {"card_id": card["card_id"], "option": card["recommendation"]},
        )
        entry = next(item for item in projection["navigator"] if item["stage"] == stage)
        if entry["review_available"]:
            return projection
        projection = _command(
            server,
            workspace_id,
            "continue",
            projection,
            {"card_id": card["card_id"]},
        )


def test_synthetic_walkthrough_covers_the_four_experiential_claims(tmp_path: Path) -> None:
    workspace_id = "synthetic-walkthrough"
    with _running_server(tmp_path) as server:
        # The served bundle must wire the action-hierarchy surface the walkthrough asserts.
        index_type, index_html = _get(server, "/")
        _, app_js = _get(server, "/app.js")
        _, styles_css = _get(server, "/styles.css")
        assert "text/html" in index_type
        assert "app.js" in index_html and "styles.css" in index_html
        for marker in (
            "primary-next-action",
            "phase-complete-banner",
            "Next: outline your story",
            "How these parts work together",
            "review-action primary-action",
            "story-lens-grid",
            "renderStoryLensInspector",
            "storyLensLayoutKey",
        ):
            assert marker in app_js, f"served app.js missing action-hierarchy marker: {marker}"
        assert ".review-action.primary-action" in styles_css
        assert "focus-visible" in styles_css

        projection = _post(
            server,
            "/api/beginner/workspaces",
            {
                "command_id": "synthetic-create",
                "workspace_id": workspace_id,
                "project_id": "synthetic-walkthrough",
                "guidance_genre": "mystery",
                "premise": PREMISE,
            },
        )

        # Claim 3: integrated narrative explanation with honest unknowns.
        orientation = projection["story_orientation"]
        composition = orientation["composition"]
        synthesis = composition["synthesis"]
        assert "Investigation and revelation" in composition["main_story_machinery"]
        assert "Secret identity" in composition["trope_families"]
        assert composition["aesthetic_framing"] == []
        assert "not yet established" in synthesis.lower()
        assert "Relationship betrayal" in synthesis
        assert "Romance" not in synthesis

        # First-screen Story Lens contract: useful interpretation before decisions,
        # with honest unknowns and no canonical mutation.
        lenses = {lens["lens_id"]: lens for lens in orientation["story_lenses"]}
        assert tuple(lens["lens_id"] for lens in orientation["story_lenses"]) == (
            "story_engine",
            "aesthetic_framing",
            "common_tropes",
            "structural_shape",
            "reader_experience",
        )
        assert lenses["story_engine"]["summary"] == "Investigation and revelation"
        assert lenses["aesthetic_framing"]["state"] == "unestablished"
        assert "Secret identity" in {
            item["label"] for item in lenses["common_tropes"]["items"]
        }
        assert lenses["structural_shape"]["summary"] == "Progressive revelation"
        assert lenses["reader_experience"]["summary"].startswith("Curiosity")
        assert all(lens["authority_status"] == "DERIVED / NOT CANON" for lens in lenses.values())
        diagnostics = orientation["lens_diagnostics"]
        assert diagnostics["source_mode"] == "deterministic_fallback"
        assert diagnostics["stale"] is False
        assert "aesthetic_framing" in diagnostics["unestablished_lens_ids"]
        assert projection["canonical_refs"] == []

        projection = _command(server, workspace_id, "continue-architecture", projection)

        # Claim 4: credible deterministic fallback with explicit author choice.
        discovery = projection["discovery"]
        assert discovery["status"] == "needs_author_choice"
        assert discovery["recommended_direction_id"] is None
        assert discovery["authority_status"] == "DERIVED / NOT CANON"
        directions = discovery["directions"]
        assert len(directions) >= 2
        assert len({item["title"] for item in directions}) == len(directions)

        projection = _command(
            server,
            workspace_id,
            "select-direction",
            projection,
            {"direction_id": directions[0]["direction_id"]},
        )
        projection = _command(server, workspace_id, "accept-direction", projection)

        for dimension in projection["working_composition"]["dimensions"]:
            if dimension["status"] != "CONFIRMED":
                projection = _command(
                    server,
                    workspace_id,
                    "confirm-dimension",
                    projection,
                    {"dimension_id": dimension["dimension_id"], "rationale": "Confirmed for the synthetic walkthrough."},
                )

        projection = _answer_stage(server, workspace_id, projection, "story_identity")
        projection = _command(server, workspace_id, "open-review", projection, {"stage": "story_identity"})
        assert projection["mapping_preview"]["ready_to_accept"] is True
        projection = _command(server, workspace_id, "accept-identity", projection)

        projection = _answer_stage(server, workspace_id, projection, "story_structure")
        projection = _command(server, workspace_id, "open-review", projection, {"stage": "story_structure"})
        projection = _command(server, workspace_id, "accept-structure", projection)

        # Claim 1: transition salience after Whole-Story Structure acceptance.
        assert projection["primary_surface"] == "complete"
        assert {ref["milestone_id"] for ref in projection["canonical_refs"]} == {
            "story_direction",
            "story_identity",
            "whole_story_structure",
        }
        assert (projection.get("revision") or {}).get("active_revision_id") is None
        structure_entry = next(item for item in projection["navigator"] if item["stage"] == "story_structure")
        assert structure_entry["lifecycle"] == "complete"
        assert structure_entry["review_available"] is True

        # Claim 2: a single obvious primary next action, no stale accept controls.
        available = projection["available_actions"]
        assert "accept-direction" not in available
        assert "accept-identity" not in available
        assert "accept-structure" not in available
        continuation_actions = [action for action in available if action in CONTINUATION_ACTIONS]
        assert continuation_actions == ["propose-outline"]
        assert projection["primary_action"] == {
            "action_id": "propose-outline",
            "label": "Create outline proposal",
            "kind": "continuation",
            "reason": "Continue the current accepted story state through the next bounded planning step.",
        }

        # Outline transition remains reachable through the same primary surface.
        projection = _command(server, workspace_id, "propose-outline", projection)
        assert "accept-outline" in projection["available_actions"]
        assert projection["primary_action"]["action_id"] == "accept-outline"
        assert projection["continuation"]["outline_proposal"] is not None
