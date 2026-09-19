"""Task 13: sanitized hybrid premise-to-architecture end-to-end qualification."""

from __future__ import annotations

import json
from contextlib import contextmanager
from urllib.request import Request, urlopen

from auteur.beginner.contracts import DecisionStage, LifecycleStatus, StageAvailability
from auteur.beginner.guidance import guidance_for
from auteur.beginner.server import BeginnerRuntimeDependencies, BeginnerWorkspaceServer
from auteur.identity import StoryIdentity
from tests.fixtures.beginner_hybrid_mystery import (
    CountingDiscoveryRecommender,
    HYBRID_ANALYSIS,
    HYBRID_DISCOVERY,
    HYBRID_MYSTERY_PREMISE,
    HYBRID_SELECTED_IDENTITY,
    StaticArchitectureAnalyzer,
    create_hybrid_app,
)


@contextmanager
def _running_server(tmp_path):
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


def _post(server, path: str, payload: dict[str, object]) -> dict[str, object]:
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
    server,
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
            "command_id": f"{slug}-{projection['session_version']}",
            "payload": payload or {},
        },
    )


def _answer_structure(server, workspace_id: str, projection: dict[str, object]) -> dict[str, object]:
    seen: set[str] = set()
    while True:
        review = projection["reviews"]["story_structure"]
        if review["review_available"]:
            return projection
        card = projection["decision_card"]
        assert card is not None
        assert card["stage"] == "story_structure"
        card_id = card["card_id"]
        assert card_id not in seen
        seen.add(card_id)
        projection = _command(
            server,
            workspace_id,
            "select",
            projection,
            {
                "card_id": card_id,
                "option": card["recommendation"],
            },
        )
        if projection["reviews"]["story_structure"]["review_available"]:
            return projection
        projection = _command(
            server,
            workspace_id,
            "continue",
            projection,
            {"card_id": card_id},
        )


def test_sanitized_hybrid_premise_reaches_accepted_structure_through_real_http(tmp_path) -> None:
    workspace_id = "hybrid-e2e"
    with _running_server(tmp_path) as server:
        projection = _post(
            server,
            "/api/beginner/workspaces",
            {
                "command_id": "create-hybrid-e2e",
                "workspace_id": workspace_id,
                "project_id": "hybrid-project",
                "guidance_genre": "mystery",
                "premise": HYBRID_MYSTERY_PREMISE,
            },
        )

        assert projection["primary_surface"] == "architecture"
        assert projection["decision_card"] is None
        assert projection["canonical_refs"] == []
        orientation = projection["story_orientation"]
        assert orientation["heading"] == "Here is what Auteur sees"
        expanded = {
            component["label"]: component
            for facet in orientation["story_map_facets"]
            for component in facet["components"]
        }
        assert expanded["Erotic betrayal melodrama"]["activation"] == "suppressed"

        # Resolve the consequential framing ambiguity explicitly before Discovery.
        projection = _command(
            server,
            workspace_id,
            "choose-architecture-alternative",
            projection,
            {
                "component_id": expanded["Erotic betrayal melodrama"]["component_id"],
                "alternative_label": "Campy erotic melodrama",
                "rationale": "Use the heightened theatrical reading for this qualification.",
            },
        )
        assert projection["canonical_refs"] == []
        assert not (tmp_path / "story_identity.yaml").exists()

        projection = _command(server, workspace_id, "continue-architecture", projection)
        assert projection["primary_surface"] == "discovery"
        assert projection["discovery"]["recommended_direction_id"] == "direction-investigative-betrayal"
        assert len(projection["discovery"]["directions"]) == 3

        projection = _command(
            server,
            workspace_id,
            "select-direction",
            projection,
            {"direction_id": "direction-investigative-betrayal"},
        )
        assert projection["canonical_refs"] == []
        projection = _command(server, workspace_id, "accept-direction", projection)
        assert [ref["milestone_id"] for ref in projection["canonical_refs"]] == ["story_direction"]
        assert projection["primary_surface"] == "story_identity"
        assert projection["identity_candidate"]["title"] == HYBRID_SELECTED_IDENTITY.title
        assert not (tmp_path / "story_identity.yaml").exists()

        preview = projection["mapping_preview"]
        assert preview["ready_to_accept"] is True
        projection = _command(server, workspace_id, "accept-identity", projection)
        assert {ref["milestone_id"] for ref in projection["canonical_refs"]} == {
            "story_direction",
            "story_identity",
        }
        accepted_identity = StoryIdentity.from_yaml(tmp_path / "story_identity.yaml")
        assert accepted_identity.core_answer == HYBRID_SELECTED_IDENTITY.core_answer
        assert accepted_identity.central_engine == HYBRID_SELECTED_IDENTITY.central_engine
        assert projection["primary_surface"] == "structure"

        projection = _answer_structure(server, workspace_id, projection)
        assert projection["reviews"]["story_structure"]["review_available"] is True
        projection = _command(
            server,
            workspace_id,
            "open-review",
            projection,
            {"stage": "story_structure"},
        )
        assert projection["reviews"]["story_structure"]["ready_to_accept"] is True
        projection = _command(server, workspace_id, "accept-structure", projection)

        assert {ref["milestone_id"] for ref in projection["canonical_refs"]} == {
            "story_direction",
            "story_identity",
            "whole_story_structure",
        }
        structure = next(
            row for row in projection["navigator"] if row["stage"] == "story_structure"
        )
        assert structure["answered_cards"] == structure["total_cards"] == 3
        assert structure["stale"] is False
        assert structure["ready_to_accept"] is True


def test_hybrid_architecture_changes_structure_guidance_differentially(tmp_path) -> None:
    hybrid = create_hybrid_app(tmp_path)
    framing = next(
        component
        for component in hybrid.session_store.load().architecture_analysis.components
        if component.label == "Erotic betrayal melodrama"
    )
    hybrid.choose_architecture_alternative(
        component_id=framing.component_id,
        alternative_label="Campy erotic melodrama",
        rationale="Activate the framing for the differential guidance check.",
        command_id="activate-campy-guidance",
        expected_session_version=hybrid.projection().session_version,
    )
    source_session = hybrid.session_store.load()
    stages = dict(source_session.stages)
    stages[DecisionStage.STORY_STRUCTURE] = stages[DecisionStage.STORY_STRUCTURE].model_copy(
        update={
            "availability": StageAvailability.AVAILABLE,
            "lifecycle": LifecycleStatus.WORKING,
        }
    )
    hybrid_session = source_session.model_copy(update={"stages": stages})
    baseline_session = hybrid_session.model_copy(update={"working_composition": None})

    baseline = guidance_for("structure.clue-distribution", baseline_session)
    enriched = guidance_for("structure.clue-distribution", hybrid_session)

    assert enriched.context_guidance != baseline.context_guidance
    assert enriched.option_impacts != baseline.option_impacts
    assert "Superhero public identity" in enriched.context_guidance.patterns
    assert "Relationship betrayal" in enriched.context_guidance.patterns
    assert "Campy erotic melodrama" in enriched.context_guidance.patterns
    assert "Superhero public identity" not in baseline.context_guidance.patterns
    assert "Campy erotic melodrama" not in baseline.context_guidance.patterns
