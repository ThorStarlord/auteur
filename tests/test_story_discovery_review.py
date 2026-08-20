"""G3a deterministic Story Discovery review controls."""

from __future__ import annotations

from pathlib import Path

import yaml

from auteur.cli import main, parse_args
from auteur.story_discovery_brief import DiscoveryBrief
from auteur.story_discovery_review import dispatch_story_discovery_review


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _brief(root: Path) -> dict:
    payload = {
        "premise": "Six strangers are trapped with a murder that should be impossible.",
        "story_type": {"genre": "mystery", "target_audience": "adult"},
        "target_experience": {"primary_emotional_promise": "claustrophobic suspicion"},
    }
    path = root / "story_discovery" / "brief.yaml"
    _write_yaml(path, payload)
    return DiscoveryBrief.from_yaml(path).declared_intent()


def _profile(key: str, *, pressure: str = "mutual suspicion") -> dict:
    return {
        "primary_strategy": "investigation under social pressure",
        "causal_owner": "ensemble",
        "external_action_pattern": ["interrogate", "test alibis"],
        "pressure_system": pressure,
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
            "candidate_2": _profile("bbbbbbbb22222222", pressure="family obligation"),
        },
        "pairwise_assessments": [],
    }


def _impact(composability: str = "compatible_as_secondary") -> dict:
    return {
        "craft_layers_changed": ["scene_families"],
        "causal_ownership_shift": None,
        "external_action_shift": {"add_or_emphasize": [], "de_emphasize": []},
        "scene_family_shift": ["family confrontation"],
        "pressure_texture_shift": "more intimate pressure",
        "reader_experience_shift": {
            "primary_promise_effect": "preserved",
            "secondary_palette_effect": ["relational ache"],
            "trajectory_effect": None,
        },
        "thematic_effect": "trust becomes personally costly",
        "gain": "relational intimacy",
        "give_up": "some procedural austerity",
        "composability": composability,
        "composition_note": "Keep family conflict subordinate to the investigation.",
        "primary_risk": None,
        "evidence_gaps": [],
        "primary_candidate_id": "candidate_1",
        "compared_candidate_id": "candidate_2",
        "primary_evidence_key": "aaaaaaaa11111111",
        "compared_evidence_key": "bbbbbbbb22222222",
    }


def _craft(composability: str = "compatible_as_secondary") -> dict:
    return {
        "schema_version": 1,
        "status": "complete",
        "primary_candidate_id": "candidate_1",
        "impacts": {"candidate_2": _impact(composability)},
        "unavailable_reason": None,
    }


def _write_candidate(root: Path, candidate_id: str, title: str) -> None:
    payload = {
        "title": title,
        "target_experience": {"primary_emotional_promise": "claustrophobic suspicion"},
    }
    _write_yaml(root / "story_discovery" / f"{candidate_id}.yaml", payload)


def _run(
    root: Path,
    *,
    status: str = "qualified",
    craft: dict | None = None,
    winner: str | None = "candidate_1",
) -> None:
    brief = _brief(root)
    _write_candidate(root, "candidate_1", "The Closed Circle")
    _write_candidate(root, "candidate_2", "Blood Obligations")
    payload = {
        "intent_mode": "intent_aware",
        "declared_author_intent": brief,
        "causal_analysis": _causal(status),
    }
    if winner is not None:
        payload["recommended_candidate_id"] = winner
        payload["recommendation_rationale"] = (
            "The investigation keeps suspicion as the governing reader experience."
        )
    if craft is not None:
        payload["craft_analysis"] = craft
    _write_yaml(root / "story_discovery" / "discovery_set.yaml", payload)


def _composition_report() -> dict:
    return {
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
    }


def test_review_parser_is_a_dedicated_cli_adapter(tmp_path: Path) -> None:
    args = parse_args(["story-discovery", "review", "--project", str(tmp_path)])
    assert args.command == "story-discovery"
    assert args.story_discovery_command == "review"
    assert args.project == tmp_path


def test_recommendation_review_reconstructs_writer_facing_evidence(
    tmp_path: Path,
    capsys,
) -> None:
    _run(tmp_path, craft=_craft())

    result = main(["story-discovery", "review", "--project", str(tmp_path)])
    rendered = capsys.readouterr().out

    assert result == 0
    assert "Recommended story direction" in rendered
    assert "The Closed Circle" in rendered
    assert "investigation under social pressure" in rendered
    assert "mutual suspicion" in rendered
    assert "claustrophobic suspicion" in rendered
    assert "relational intimacy" in rendered
    assert "some procedural austerity" in rendered
    assert "candidate_2" in rendered
    assert "Nothing canonical has changed." in rendered
    assert "story-discovery accept story_discovery/candidate_1.yaml" in rendered


def test_non_adjudicable_review_refuses_to_invent_a_winner(tmp_path: Path, capsys) -> None:
    _run(tmp_path, status="not_adjudicable_near_duplicate", winner="candidate_1")

    result = main(["story-discovery", "review", "--project", str(tmp_path)])
    rendered = capsys.readouterr().out

    assert result == 0
    assert "does not have a defensible recommendation" in rendered
    assert "too causally similar" in rendered
    assert "story-discovery accept" not in rendered
    assert "Generate a genuinely different search space" in rendered


def test_noncompatible_craft_never_becomes_a_safe_composition_offer(tmp_path: Path, capsys) -> None:
    _run(tmp_path, craft=_craft("requires_reframing"))

    result = main(["story-discovery", "review", "--project", str(tmp_path)])
    rendered = capsys.readouterr().out

    assert result == 0
    assert "Composition fit: requires_reframing" in rendered
    assert "Explore a compatible composition" not in rendered


def test_composed_review_explains_borrows_and_preserved_primary(tmp_path: Path, capsys) -> None:
    _run(tmp_path, craft=_craft())
    _write_yaml(
        tmp_path / "story_discovery" / "composed_candidate.yaml",
        {"title": "The Closed Circle, With Blood Debts"},
    )
    _write_yaml(
        tmp_path / "story_discovery" / "composition_report.yaml",
        _composition_report(),
    )

    result = main(["story-discovery", "review", "--project", str(tmp_path)])
    rendered = capsys.readouterr().out

    assert result == 0
    assert "Composed story direction" in rendered
    assert "The Closed Circle, With Blood Debts" in rendered
    assert "family obligation" in rendered
    assert "investigation still governs decisive causation" in rendered
    assert "story_discovery/composed_candidate.yaml" in rendered
    assert "story_discovery/candidate_1.yaml" in rendered


def test_review_is_read_only_and_provider_free(tmp_path: Path, monkeypatch, capsys) -> None:
    _run(tmp_path, craft=_craft())
    before = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    import auteur.llm.factory

    def _explode(*args, **kwargs):
        raise AssertionError("review must not construct an LLM provider")

    monkeypatch.setattr(auteur.llm.factory, "build_client", _explode)
    result = main(["story-discovery", "review", "--project", str(tmp_path)])
    capsys.readouterr()
    after = {
        path.relative_to(tmp_path): path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }

    assert result == 0
    assert before == after


def test_unreviewable_state_fails_with_recovery_instead_of_guessing(tmp_path: Path, capsys) -> None:
    args = type("Args", (), {"project": tmp_path})()
    result = dispatch_story_discovery_review(args)
    captured = capsys.readouterr()

    assert result == 1
    assert "No Story Discovery brief or recommendation" in captured.err
