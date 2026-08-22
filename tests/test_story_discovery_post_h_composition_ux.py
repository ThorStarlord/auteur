"""R2b controls for writer-facing dual composition hierarchy."""

from __future__ import annotations

from pathlib import Path

import yaml

from auteur.cli import main
from auteur.story_discovery_brief import DiscoveryBrief
from auteur.story_discovery_guided_compose import dispatch_story_discovery_guided_compose


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _profile(key: str, pressure: str = "mutual suspicion") -> dict:
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


def _impact() -> dict:
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
        "composability": "compatible_as_secondary",
        "composition_note": "Keep family conflict subordinate to the investigation.",
        "primary_risk": "Family conflict could become the emotional center.",
        "evidence_gaps": [],
        "primary_candidate_id": "candidate_1",
        "compared_candidate_id": "candidate_2",
        "primary_evidence_key": "aaaaaaaa11111111",
        "compared_evidence_key": "bbbbbbbb22222222",
    }


def _write_project(root: Path) -> None:
    discovery = root / "story_discovery"
    brief_payload = {
        "premise": "Six strangers are trapped with a murder that should be impossible.",
        "story_type": {"genre": "mystery", "target_audience": "adult"},
        "target_experience": {"primary_emotional_promise": "claustrophobic suspicion"},
    }
    _write_yaml(discovery / "brief.yaml", brief_payload)
    declared = DiscoveryBrief.from_yaml(discovery / "brief.yaml").declared_intent()
    _write_yaml(
        discovery / "candidate_1.yaml",
        {"title": "The Closed Circle", "target_experience": brief_payload["target_experience"]},
    )
    _write_yaml(
        discovery / "candidate_2.yaml",
        {"title": "Blood Obligations", "target_experience": brief_payload["target_experience"]},
    )
    causal = {
        "schema_version": 1,
        "status": "qualified",
        "profiles": {
            "candidate_1": _profile("aaaaaaaa11111111"),
            "candidate_2": _profile("bbbbbbbb22222222", "family obligation"),
        },
        "pairwise_assessments": [],
    }
    craft = {
        "schema_version": 1,
        "status": "complete",
        "primary_candidate_id": "candidate_1",
        "impacts": {"candidate_2": _impact()},
        "unavailable_reason": None,
    }
    run = {
        "intent_mode": "intent_aware",
        "declared_author_intent": declared,
        "causal_analysis": causal,
        "craft_analysis": craft,
        "recommended_candidate_id": "candidate_1",
        "recommendation_rationale": "The investigation keeps suspicion governing.",
    }
    _write_yaml(discovery / "discovery_set.yaml", run)
    _write_yaml(discovery / "discovery_report.yaml", run)


def _v2_report() -> dict:
    return {
        "schema_version": 2,
        "status": "candidate_only",
        "primary_candidate_id": "candidate_1",
        "borrowed": [
            {
                "candidate_id": "candidate_2",
                "mechanism": "family obligation",
                "job": "Use family pressure to complicate testimony and increase dramatic irony.",
                "forbidden_ownership": [
                    "governing external objective",
                    "decisive reversal chain",
                    "climax",
                    "governing reader-experience promise",
                ],
            }
        ],
        "primary_evidence_key": "aaaaaaaa11111111",
        "borrowed_evidence_keys": {"candidate_2": "bbbbbbbb22222222"},
        "hierarchy_assessment": {
            "classification": "primary_preserved",
            "rationale": "Both hierarchy dimensions remain subordinate.",
            "primary_mechanics_preserved": ["investigation"],
            "borrowed_mechanics_subordinate": ["family conflict"],
            "risks": ["Do not let family reconciliation become the practical climax."],
            "causal": {
                "classification": "primary_preserved",
                "rationale": "The investigation still owns decisive reversals and the climax.",
                "primary_evidence_preserved": ["forced reconstruction remains the climax"],
                "borrowed_evidence_subordinate": ["family pressure only changes testimony"],
                "risks": [],
            },
            "experiential": {
                "classification": "primary_preserved",
                "rationale": "Claustrophobic suspicion remains the recurring emotional center.",
                "primary_evidence_preserved": ["suspicion organizes recurring scenes"],
                "borrowed_evidence_subordinate": ["relational ache remains supporting texture"],
                "risks": ["Do not let reconciliation become the audience's main anticipation."],
            },
        },
        "composed_causal_profile": _profile("cccccccc33333333"),
        "output_candidate": "story_discovery/composed_candidate.yaml",
    }


def test_v2_review_surfaces_plot_experience_and_borrow_boundaries(tmp_path: Path, capsys) -> None:
    _write_project(tmp_path)
    _write_yaml(
        tmp_path / "story_discovery" / "composed_candidate.yaml",
        {"title": "The Closed Circle, With Blood Debts"},
    )
    _write_yaml(tmp_path / "story_discovery" / "composition_report.yaml", _v2_report())

    assert main(["story-discovery", "review", "--project", str(tmp_path)]) == 0
    rendered = capsys.readouterr().out

    assert "Why the primary still governs the plot" in rendered
    assert "Why it still governs the reader experience" in rendered
    assert "Claustrophobic suspicion remains the recurring emotional center" in rendered
    assert "Job: Use family pressure to complicate testimony" in rendered
    assert "It may not take ownership of:" in rendered
    assert "governing reader-experience promise" in rendered
    assert "Remaining displacement risks" in rendered
    assert "Nothing canonical has changed." in rendered


def test_legacy_v1_report_keeps_legacy_review_surface(tmp_path: Path, capsys) -> None:
    _write_project(tmp_path)
    _write_yaml(tmp_path / "story_discovery" / "composed_candidate.yaml", {"title": "Legacy Compose"})
    report = _v2_report()
    report["schema_version"] = 1
    report["borrowed"] = [{"candidate_id": "candidate_2", "mechanism": "family obligation"}]
    hierarchy = report["hierarchy_assessment"]
    hierarchy.pop("causal")
    hierarchy.pop("experiential")
    _write_yaml(tmp_path / "story_discovery" / "composition_report.yaml", report)

    assert main(["story-discovery", "review", "--project", str(tmp_path)]) == 0
    rendered = capsys.readouterr().out
    assert "Why the primary still governs" in rendered
    assert "Why the primary still governs the plot" not in rendered
    assert "Job:" not in rendered


def test_guided_compose_asks_only_what_to_borrow_and_leaves_hierarchy_internal(
    tmp_path: Path, monkeypatch
) -> None:
    _write_project(tmp_path)
    calls = []
    prompts: list[str] = []
    outputs: list[str] = []
    answers = iter(["yes", "1", "hidden repairs that pressure testimony"])

    def fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr(
        "auteur.story_discovery_compose.dispatch_story_discovery_compose",
        lambda args: calls.append(args) or 0,
    )
    args = type("Args", (), {"project": tmp_path, "provider": "anthropic", "model": None})()

    assert dispatch_story_discovery_guided_compose(
        args,
        input_fn=fake_input,
        output_fn=outputs.append,
    ) == 0
    assert calls[0].borrow == ["candidate_2:hidden repairs that pressure testimony"]
    prompt_text = " ".join(prompts).lower()
    assert "causal ownership" not in prompt_text
    assert "experiential ownership" not in prompt_text
    assert "forbidden ownership" not in prompt_text
