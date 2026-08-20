"""Story Discovery front-door controls across generic rules and derived routing."""

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


def _profile(key: str) -> dict:
    return {
        "primary_strategy": "investigation under social pressure",
        "causal_owner": "ensemble",
        "external_action_pattern": ["interrogate", "test alibis"],
        "pressure_system": "mutual suspicion",
        "reversal_mechanics": ["evidence reframes motive"],
        "climax_mechanic": "forced reconstruction",
        "scene_families": ["interrogations", "locked-room tests"],
        "evidence_gaps": [],
        "evidence_key": key,
    }


def _causal(status: str) -> dict:
    return {
        "schema_version": 1,
        "status": status,
        "profiles": {
            "candidate_1": _profile("aaaaaaaa11111111"),
            "candidate_2": _profile("bbbbbbbb22222222"),
        },
        "pairwise_assessments": [],
    }


def _write_recommendation(
    root: Path,
    winner: str = "candidate_2",
    *,
    brief: DiscoveryBrief | None = None,
    causal_status: str | None = None,
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
    if causal_status is not None:
        payload["causal_analysis"] = _causal(causal_status)
    _write_yaml(discovery / "discovery_set.yaml", payload)
    _write_yaml(discovery / f"{winner}.yaml", {"title": "Recommended direction"})


def _write_composition(root: Path) -> None:
    _write_yaml(root / "story_discovery" / "composed_candidate.yaml", {"title": "Composed"})
    _write_yaml(
        root / "story_discovery" / "composition_report.yaml",
        {
            "schema_version": 1,
            "status": "candidate_only",
            "primary_candidate_id": "candidate_1",
            "borrowed": [{"candidate_id": "candidate_2", "mechanism": "family obligation"}],
            "primary_evidence_key": "aaaaaaaa11111111",
            "borrowed_evidence_keys": {"candidate_2": "bbbbbbbb22222222"},
            "hierarchy_assessment": {
                "classification": "primary_preserved",
                "rationale": "The investigation still governs decisive causation.",
                "primary_mechanics_preserved": ["investigation"],
                "borrowed_mechanics_subordinate": ["family conflict"],
                "risks": [],
            },
            "composed_causal_profile": _profile("cccccccc33333333"),
            "output_candidate": "story_discovery/composed_candidate.yaml",
        },
    )


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


def test_existing_raw_recommendation_routes_to_read_only_review(tmp_path: Path) -> None:
    root = tmp_path / "recommended"
    root.mkdir()
    _write_recommendation(root, "candidate_2")

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Review recommended story direction"
    assert action.authority == AuthorityLevel.READ_ONLY
    assert action.command == "auteur story-discovery review --project ."


def test_review_routing_never_surfaces_an_acceptance_command(tmp_path: Path) -> None:
    root = tmp_path / "recommended"
    root.mkdir()
    _write_recommendation(root)
    engine = WorkflowEngine(root)
    action = engine.analyze().actions[0]

    assert engine.can_execute(action) is True
    assert "story-discovery accept" not in action.command
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


def test_matching_intent_aware_recommendation_routes_to_review(tmp_path: Path) -> None:
    root = tmp_path / "matching"
    root.mkdir()
    brief = _write_brief(root)
    _write_recommendation(root, brief=brief)

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Review recommended story direction"
    assert action.authority == AuthorityLevel.READ_ONLY


def test_non_adjudicable_run_routes_to_explanatory_review(tmp_path: Path) -> None:
    root = tmp_path / "non-adjudicable"
    root.mkdir()
    brief = _write_brief(root)
    _write_recommendation(
        root,
        brief=brief,
        causal_status="not_adjudicable_uncertain",
    )

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Review why Auteur cannot recommend a direction yet"
    assert action.command == "auteur story-discovery review --project ."
    assert action.authority == AuthorityLevel.READ_ONLY


def test_current_composed_candidate_routes_to_composed_review(tmp_path: Path) -> None:
    root = tmp_path / "composed"
    root.mkdir()
    brief = _write_brief(root)
    _write_yaml(root / "story_discovery" / "candidate_2.yaml", {"title": "Secondary"})
    _write_recommendation(root, winner="candidate_1", brief=brief, causal_status="qualified")
    _write_composition(root)

    action = WorkflowEngine(root).analyze().actions[0]

    assert action.label == "Review composed story direction"
    assert action.command == "auteur story-discovery review --project ."
    assert action.authority == AuthorityLevel.READ_ONLY


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
