"""Story Discovery front-door controls across generic rules and G1a engine routing."""

from __future__ import annotations

from pathlib import Path

import yaml

from auteur.story_discovery_brief import DiscoveryBrief
from auteur.ui.dashboard import format_dashboard
from auteur.workflow.engine import WorkflowEngine
from auteur.workflow.models import AuthorityLevel, WorkflowStage
from auteur.workflow.rules import detect_stages, recommend_actions


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _write_brief(root: Path, *, experience: str = "claustrophobic suspicion") -> DiscoveryBrief:
    data = {
        "premise": "Six strangers are trapped with a murder that should be impossible.",
        "story_type": {"genre": "mystery", "target_audience": "adult"},
        "target_experience": {"primary_emotional_promise": experience},
    }
    path = root / "story_discovery" / "brief.yaml"
    _write_yaml(path, data)
    return DiscoveryBrief.from_yaml(path)


def _write_recommendation(
    root: Path,
    winner: str = "candidate_2",
    *,
    brief: DiscoveryBrief | None = None,
) -> None:
    discovery = root / "story_discovery"
    payload = {"recommended_candidate_id": winner}
    if brief is not None:
        payload.update(
            {
                "intent_mode": "intent_aware",
                "declared_author_intent": brief.declared_intent(),
            }
        )
    _write_yaml(discovery / "discovery_set.yaml", payload)
    _write_yaml(discovery / f"{winner}.yaml", {"title": "Recommended direction"})


def test_generic_rule_layer_preserves_legacy_raw_discovery_action(tmp_path: Path) -> None:
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


def test_fresh_project_engine_routes_to_guided_capture_and_refuses_auto_answer(
    tmp_path: Path,
) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    engine = WorkflowEngine(root)
    action = engine.analyze().actions[0]

    result = engine.execute(action)

    assert action.label == "Tell Auteur about your story"
    assert action.authority == AuthorityLevel.AUTHORITY_BEARING
    assert action.command == "auteur story-discovery start --project ."
    assert result["executed"] is False
    assert result["exit_code"] == 4
    assert "requires author decision" in result["error"]


def test_existing_raw_recommendation_still_routes_to_explicit_acceptance(tmp_path: Path) -> None:
    root = tmp_path / "recommended"
    root.mkdir()
    _write_recommendation(root, "candidate_2")

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Choose recommended story direction"
    assert action.authority == AuthorityLevel.AUTHORITY_BEARING
    assert action.command == (
        "auteur story-discovery accept story_discovery/candidate_2.yaml "
        "--output story_identity.yaml"
    )


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


def test_unusable_recommendation_without_brief_routes_to_guided_capture(tmp_path: Path) -> None:
    root = tmp_path / "stale-discovery"
    root.mkdir()
    _write_yaml(
        root / "story_discovery" / "discovery_set.yaml",
        {"recommended_candidate_id": "candidate_9"},
    )

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Tell Auteur about your story"
    assert action.command == "auteur story-discovery start --project ."


def test_invalid_brief_routes_to_repair_without_guessing(tmp_path: Path) -> None:
    root = tmp_path / "invalid"
    root.mkdir()
    path = root / "story_discovery" / "brief.yaml"
    path.parent.mkdir(parents=True)
    path.write_text("premise: [broken\n", encoding="utf-8")

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Repair your Story Discovery brief"
    assert action.authority == AuthorityLevel.AUTHORITY_BEARING


def test_incomplete_brief_routes_to_resume(tmp_path: Path) -> None:
    root = tmp_path / "incomplete"
    root.mkdir()
    _write_yaml(root / "story_discovery" / "brief.yaml", {"premise": "A premise."})

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Continue clarifying what you want"
    assert action.authority == AuthorityLevel.AUTHORITY_BEARING
    assert action.command == "auteur story-discovery start --project ."


def test_adequate_brief_routes_to_intent_aware_discovery(tmp_path: Path) -> None:
    root = tmp_path / "adequate"
    root.mkdir()
    _write_brief(root)

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Discover story directions against your intent"
    assert action.authority == AuthorityLevel.CANDIDATE_GENERATION
    assert action.command == (
        "auteur story-discovery run --brief story_discovery/brief.yaml "
        "--recommend --output story_discovery --project ."
    )


def test_current_brief_takes_precedence_over_legacy_exploratory_recommendation(
    tmp_path: Path,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    _write_brief(root)
    _write_recommendation(root)

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Discover story directions against your intent"


def test_changed_declared_intent_makes_prior_intent_run_stale(tmp_path: Path) -> None:
    root = tmp_path / "changed-intent"
    root.mkdir()
    brief = _write_brief(root)
    _write_recommendation(root, brief=brief)
    changed = _write_brief(root, experience="reconstructive relief")
    assert changed.declared_intent() != brief.declared_intent()

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Discover story directions against your intent"


def test_matching_intent_aware_recommendation_routes_to_acceptance(tmp_path: Path) -> None:
    root = tmp_path / "matching"
    root.mkdir()
    brief = _write_brief(root)
    _write_recommendation(root, brief=brief)

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Choose recommended story direction"


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


def test_dashboard_inherits_guided_workflow_front_door_label(tmp_path: Path) -> None:
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
    assert "-> Tell Auteur about your story" in rendered
