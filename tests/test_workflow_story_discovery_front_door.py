"""Phase C controls for routing fresh projects through Story Discovery."""

from __future__ import annotations

from pathlib import Path

import yaml

from auteur.ui.dashboard import format_dashboard
from auteur.workflow.engine import WorkflowEngine
from auteur.workflow.models import AuthorityLevel, WorkflowStage
from auteur.workflow.rules import detect_stages, recommend_actions


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _write_recommendation(root: Path, winner: str = "candidate_2") -> None:
    discovery = root / "story_discovery"
    _write_yaml(
        discovery / "discovery_set.yaml",
        {"recommended_candidate_id": winner},
    )
    _write_yaml(discovery / f"{winner}.yaml", {"title": "Recommended direction"})


def test_fresh_project_recommends_story_discovery(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()

    stages = detect_stages(root)
    actions = recommend_actions(stages, project_root=root)

    assert stages[0].stage == WorkflowStage.IDENTITY
    assert not stages[0].is_complete
    assert actions[0].label == "Discover story direction"
    assert actions[0].authority == AuthorityLevel.CANDIDATE_GENERATION
    assert actions[0].command == (
        "auteur story-discovery run <premise-or-file> --recommend "
        "--output story_discovery --project ."
    )
    assert "identity recommend" not in actions[0].command


def test_fresh_project_execute_refuses_unfilled_premise_placeholder(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    engine = WorkflowEngine(root)
    action = engine.analyze().actions[0]

    result = engine.execute(action)

    assert action.label == "Discover story direction"
    assert result["executed"] is False
    assert result["exit_code"] == 2
    assert "placeholders" in result["error"]


def test_existing_recommendation_routes_to_explicit_acceptance(tmp_path: Path) -> None:
    root = tmp_path / "recommended"
    root.mkdir()
    _write_recommendation(root, "candidate_2")

    stages = detect_stages(root)
    actions = recommend_actions(stages, project_root=root)

    assert actions[0].label == "Choose recommended story direction"
    assert actions[0].authority == AuthorityLevel.AUTHORITY_BEARING
    assert actions[0].command == (
        "auteur story-discovery accept story_discovery/candidate_2.yaml "
        "--output story_identity.yaml"
    )
    assert "story-discovery run" not in actions[0].command


def test_acceptance_action_cannot_auto_promote_canon(tmp_path: Path) -> None:
    root = tmp_path / "recommended"
    root.mkdir()
    _write_recommendation(root)
    engine = WorkflowEngine(root)
    action = engine.analyze().actions[0]

    result = engine.execute(action)

    assert action.authority == AuthorityLevel.AUTHORITY_BEARING
    assert result["executed"] is False
    assert result["exit_code"] == 4
    assert "requires author decision" in result["error"]
    assert not (root / "story_identity.yaml").exists()


def test_unusable_recommendation_falls_back_to_discovery(tmp_path: Path) -> None:
    root = tmp_path / "stale-discovery"
    root.mkdir()
    _write_yaml(
        root / "story_discovery" / "discovery_set.yaml",
        {"recommended_candidate_id": "candidate_9"},
    )

    actions = recommend_actions(detect_stages(root), project_root=root)

    assert actions[0].label == "Discover story direction"
    assert "story-discovery run" in actions[0].command


def test_accepted_identity_continues_to_structure_unchanged(tmp_path: Path) -> None:
    root = tmp_path / "accepted"
    _write_yaml(root / "story_identity.yaml", {"title": "Accepted Story"})

    stages = detect_stages(root)
    actions = recommend_actions(stages)

    assert stages[0].is_complete
    assert stages[1].stage == WorkflowStage.STRUCTURE
    assert not stages[1].is_complete
    assert actions[0].label == "Diagnose structure"
    assert all("story-discovery" not in action.command for action in actions)


def test_dashboard_inherits_workflow_front_door_label(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    rendered = format_dashboard(
        {
            "project": str(root),
            "status": {},
            "lifecycle": {},
            "alerts": [],
            "commitment": {},
        }
    )

    assert "## Recommended Actions" in rendered
    assert "-> Discover story direction" in rendered
