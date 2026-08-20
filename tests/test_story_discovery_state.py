"""G2a derived Story Discovery project-state controls."""

from __future__ import annotations

from pathlib import Path

import yaml

from auteur.story_discovery_brief import DiscoveryBrief
from auteur.story_discovery_guidance import BriefLifecycleState
from auteur.story_discovery_state import StoryDiscoveryStateKind, classify_story_discovery_project


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _write_brief(root: Path, *, experience: str = "claustrophobic suspicion") -> dict:
    payload = {
        "premise": "Six strangers are trapped with a murder that should be impossible.",
        "story_type": {"genre": "mystery", "target_audience": "adult"},
        "target_experience": {"primary_emotional_promise": experience},
    }
    path = root / "story_discovery" / "brief.yaml"
    _write_yaml(path, payload)
    return DiscoveryBrief.from_yaml(path).declared_intent()


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


def _causal(status: str = "qualified") -> dict:
    return {
        "schema_version": 1,
        "status": status,
        "profiles": {
            "candidate_1": _profile("aaaaaaaa11111111"),
            "candidate_2": _profile("bbbbbbbb22222222"),
        },
        "pairwise_assessments": [],
    }


def _write_candidate(root: Path, candidate_id: str) -> None:
    _write_yaml(root / "story_discovery" / f"{candidate_id}.yaml", {"title": candidate_id})


def _write_run(
    root: Path,
    *,
    winner: str | None = "candidate_1",
    brief: dict | None = None,
    causal_status: str | None = None,
    craft: dict | None = None,
) -> None:
    payload: dict = {}
    if winner is not None:
        payload["recommended_candidate_id"] = winner
        _write_candidate(root, winner)
    if brief is not None:
        payload["intent_mode"] = "intent_aware"
        payload["declared_author_intent"] = brief
    if causal_status is not None:
        payload["causal_analysis"] = _causal(causal_status)
    if craft is not None:
        payload["craft_analysis"] = craft
    _write_yaml(root / "story_discovery" / "discovery_set.yaml", payload)


def _impact(candidate_id: str, composability: str) -> dict:
    return {
        "craft_layers_changed": ["scene_families"],
        "causal_ownership_shift": None,
        "external_action_shift": {"add_or_emphasize": [], "de_emphasize": []},
        "scene_family_shift": ["family confrontation"],
        "pressure_texture_shift": None,
        "reader_experience_shift": {
            "primary_promise_effect": "preserved",
            "secondary_palette_effect": [],
            "trajectory_effect": None,
        },
        "thematic_effect": None,
        "gain": "relational intimacy",
        "give_up": None,
        "composability": composability,
        "composition_note": None,
        "primary_risk": None,
        "evidence_gaps": [],
        "primary_candidate_id": "candidate_1",
        "compared_candidate_id": candidate_id,
        "primary_evidence_key": "aaaaaaaa11111111",
        "compared_evidence_key": "bbbbbbbb22222222",
    }


def _craft(composability: str = "compatible_as_secondary") -> dict:
    return {
        "schema_version": 1,
        "status": "complete",
        "primary_candidate_id": "candidate_1",
        "impacts": {"candidate_2": _impact("candidate_2", composability)},
        "unavailable_reason": None,
    }


def _composition_report() -> dict:
    return {
        "schema_version": 1,
        "status": "candidate_only",
        "primary_candidate_id": "candidate_1",
        "borrowed": [{"candidate_id": "candidate_2", "mechanism": "relational intimacy"}],
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
    }


def test_fresh_project_is_no_brief(tmp_path: Path) -> None:
    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.NO_BRIEF
    assert state.brief_state is BriefLifecycleState.ABSENT


def test_invalid_and_incomplete_briefs_take_precedence(tmp_path: Path) -> None:
    broken = tmp_path / "story_discovery" / "brief.yaml"
    broken.parent.mkdir(parents=True)
    broken.write_text("premise: [broken\n", encoding="utf-8")
    _write_run(tmp_path)
    assert classify_story_discovery_project(tmp_path).kind is StoryDiscoveryStateKind.INVALID_BRIEF

    _write_yaml(broken, {"premise": "Only a premise."})
    assert classify_story_discovery_project(tmp_path).kind is StoryDiscoveryStateKind.INCOMPLETE_BRIEF


def test_adequate_brief_without_current_run_is_ready(tmp_path: Path) -> None:
    _write_brief(tmp_path)
    assert classify_story_discovery_project(tmp_path).kind is StoryDiscoveryStateKind.READY_TO_DISCOVER


def test_exploratory_or_changed_intent_run_is_stale_for_current_brief(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_run(tmp_path)
    assert classify_story_discovery_project(tmp_path).kind is StoryDiscoveryStateKind.READY_TO_DISCOVER

    _write_run(tmp_path, brief=brief)
    _write_brief(tmp_path, experience="reconstructive relief")
    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.READY_TO_DISCOVER
    assert state.run_matches_current_brief is False


def test_matching_intent_run_and_legacy_raw_run_can_expose_recommendation(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_run(tmp_path, brief=brief)
    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE
    assert state.run_matches_current_brief is True

    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    _write_run(raw_root)
    raw = classify_story_discovery_project(raw_root)
    assert raw.kind is StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE
    assert raw.recommended_candidate_id == "candidate_1"


def test_non_adjudicable_causal_state_overrides_contradictory_winner(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_run(
        tmp_path,
        brief=brief,
        causal_status="not_adjudicable_near_duplicate",
    )
    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.NON_ADJUDICABLE
    assert state.recommended_candidate_id is None


def test_qualified_run_requires_usable_winner(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_run(tmp_path, brief=brief, winner=None, causal_status="qualified")
    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.DISCOVERY_INVALID


def test_unsafe_or_missing_winner_fails_closed(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    payload = {
        "recommended_candidate_id": "../candidate_1",
        "intent_mode": "intent_aware",
        "declared_author_intent": brief,
        "causal_analysis": _causal("qualified"),
    }
    _write_yaml(tmp_path / "story_discovery" / "discovery_set.yaml", payload)
    assert classify_story_discovery_project(tmp_path).kind is StoryDiscoveryStateKind.DISCOVERY_INVALID


def test_craft_is_optional_but_compatible_secondary_is_exposed(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_candidate(tmp_path, "candidate_2")
    _write_run(tmp_path, brief=brief, causal_status="qualified", craft=_craft())
    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE
    assert state.can_compose is True
    assert state.compatible_secondary_candidate_ids == ("candidate_2",)


def test_noncompatible_or_malformed_craft_does_not_erase_recommendation(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_candidate(tmp_path, "candidate_2")
    _write_run(
        tmp_path,
        brief=brief,
        causal_status="qualified",
        craft=_craft("requires_reframing"),
    )
    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE
    assert state.can_compose is False

    path = tmp_path / "story_discovery" / "discovery_set.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["craft_analysis"] = {"broken": True}
    _write_yaml(path, payload)
    malformed = classify_story_discovery_project(tmp_path)
    assert malformed.kind is StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE
    assert malformed.can_compose is False
    assert malformed.problems


def test_valid_current_composition_becomes_composed_state(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_candidate(tmp_path, "candidate_2")
    _write_run(tmp_path, brief=brief, causal_status="qualified", craft=_craft())
    _write_yaml(tmp_path / "story_discovery" / "composed_candidate.yaml", {"title": "Composed"})
    _write_yaml(tmp_path / "story_discovery" / "composition_report.yaml", _composition_report())

    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.COMPOSED_CANDIDATE_AVAILABLE
    assert state.has_composed_candidate is True


def test_stale_composition_is_ignored_without_erasing_recommendation(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_candidate(tmp_path, "candidate_2")
    _write_run(tmp_path, brief=brief, causal_status="qualified", craft=_craft())
    report = _composition_report()
    report["primary_evidence_key"] = "staleeeee1111111"
    _write_yaml(tmp_path / "story_discovery" / "composed_candidate.yaml", {"title": "Composed"})
    _write_yaml(tmp_path / "story_discovery" / "composition_report.yaml", report)

    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE
    assert state.has_composed_candidate is False
    assert "stale" in " ".join(state.problems)


def test_classification_is_deterministic_and_read_only(tmp_path: Path) -> None:
    brief = _write_brief(tmp_path)
    _write_run(tmp_path, brief=brief, causal_status="qualified")
    before = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    first = classify_story_discovery_project(tmp_path)
    second = classify_story_discovery_project(tmp_path)
    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert first == second
    assert before == after
