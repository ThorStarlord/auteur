"""Post-H recommendation calibration controls for Story Discovery."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from auteur.cli import main
from auteur.story_discovery_brief import DiscoveryBrief
from auteur.story_discovery_recommend import _parse_judgment
from auteur.story_discovery_state import StoryDiscoveryStateKind, classify_story_discovery_project


def _response(
    *,
    status: str = "recommended",
    basis: str | None = "advisory_artistic_preference",
    winner: str | None = "candidate_1",
    tradeoffs: dict[str, str] | None = None,
) -> str:
    if tradeoffs is None:
        tradeoffs = {"candidate_2": "Offers a different but still viable pleasure."}
    return json.dumps(
        {
            "recommendation_status": status,
            "recommendation_basis": basis,
            "recommended_candidate_id": winner,
            "recommendation_rationale": "The deciding criterion is stated honestly.",
            "candidate_tradeoffs": tradeoffs,
        }
    )


def test_explicit_intent_fit_requires_structured_intent_context() -> None:
    judgment = _parse_judgment(
        _response(basis="explicit_intent_fit"),
        ["candidate_1", "candidate_2"],
        allow_explicit_intent_fit=True,
    )
    assert judgment.status == "recommended"
    assert judgment.basis == "explicit_intent_fit"
    assert judgment.recommended_candidate_id == "candidate_1"

    with pytest.raises(ValueError, match="structured declared-author-intent"):
        _parse_judgment(
            _response(basis="explicit_intent_fit"),
            ["candidate_1", "candidate_2"],
            allow_explicit_intent_fit=False,
        )


def test_advisory_close_call_is_explicitly_taste_not_author_intent() -> None:
    judgment = _parse_judgment(
        _response(basis="advisory_artistic_preference"),
        ["candidate_1", "candidate_2"],
        allow_explicit_intent_fit=True,
    )
    assert judgment.status == "recommended"
    assert judgment.basis == "advisory_artistic_preference"
    assert judgment.rejected_candidate_reasons == {
        "candidate_2": "Offers a different but still viable pleasure."
    }


def test_comparative_non_adjudicable_has_no_winner_and_covers_all_survivors() -> None:
    judgment = _parse_judgment(
        _response(
            status="not_adjudicable",
            basis=None,
            winner=None,
            tradeoffs={
                "candidate_1": "Optimizes intimate pressure.",
                "candidate_2": "Optimizes institutional scale.",
            },
        ),
        ["candidate_1", "candidate_2"],
    )
    assert judgment.status == "not_adjudicable"
    assert judgment.basis is None
    assert judgment.recommended_candidate_id is None


@pytest.mark.parametrize(
    "response,match",
    [
        (
            _response(
                status="not_adjudicable",
                basis=None,
                winner="candidate_1",
                tradeoffs={
                    "candidate_1": "One tradeoff.",
                    "candidate_2": "Another tradeoff.",
                },
            ),
            "must not select a winner",
        ),
        (
            _response(status="recommended", basis=None),
            "valid recommendation_basis",
        ),
        (
            _response(tradeoffs={"candidate_3": "Unknown candidate."}),
            "cover exactly every non-selected survivor",
        ),
    ],
)
def test_malformed_recommendation_basis_combinations_fail_closed(
    response: str,
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        _parse_judgment(response, ["candidate_1", "candidate_2"])


def test_legacy_judge_payload_is_conservatively_advisory() -> None:
    legacy = json.dumps(
        {
            "recommended_candidate_id": "candidate_1",
            "recommendation_rationale": "Old fixture preference.",
            "rejected_candidate_reasons": {"candidate_2": "Different tradeoff."},
        }
    )
    judgment = _parse_judgment(legacy, ["candidate_1", "candidate_2"])
    assert judgment.status == "recommended"
    assert judgment.basis == "advisory_artistic_preference"


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _brief(root: Path) -> dict:
    path = root / "story_discovery" / "brief.yaml"
    _write_yaml(
        path,
        {
            "premise": "Six strangers are trapped in an elevator with a murder.",
            "story_type": {"genre": "mystery", "target_audience": "adult"},
            "target_experience": {"primary_emotional_promise": "claustrophobic suspicion"},
        },
    )
    return DiscoveryBrief.from_yaml(path).declared_intent()


def _profile(key: str, pressure: str) -> dict:
    return {
        "primary_strategy": "reconstruct the sealed-space crime",
        "causal_owner": "ensemble investigation",
        "external_action_pattern": ["test alibis", "reconstruct positions"],
        "pressure_system": pressure,
        "reversal_mechanics": ["objective evidence changes interpretation"],
        "climax_mechanic": "live reconstruction",
        "scene_families": ["interrogations", "physical tests"],
        "evidence_gaps": [],
        "evidence_key": key,
    }


def _qualified_causal() -> dict:
    return {
        "schema_version": 1,
        "status": "qualified",
        "profiles": {
            "candidate_1": _profile("aaaaaaaa11111111", "social suspicion"),
            "candidate_2": _profile("bbbbbbbb22222222", "sensor ambiguity"),
        },
        "pairwise_assessments": [],
    }


def _write_candidates(root: Path) -> None:
    _write_yaml(
        root / "story_discovery" / "candidate_1.yaml",
        {
            "title": "Hidden Seconds",
            "target_experience": {"primary_emotional_promise": "claustrophobic suspicion"},
        },
    )
    _write_yaml(
        root / "story_discovery" / "candidate_2.yaml",
        {
            "title": "Weight of an Alibi",
            "target_experience": {"primary_emotional_promise": "claustrophobic suspicion"},
        },
    )


def test_qualified_comparative_non_adjudicable_is_a_valid_project_state(
    tmp_path: Path,
    capsys,
) -> None:
    declared = _brief(tmp_path)
    _write_candidates(tmp_path)
    _write_yaml(
        tmp_path / "story_discovery" / "discovery_set.yaml",
        {
            "intent_mode": "intent_aware",
            "declared_author_intent": declared,
            "causal_analysis": _qualified_causal(),
            "recommendation_status": "not_adjudicable",
            "recommendation_basis": None,
            "recommendation_rationale": (
                "The brief does not rank intimate reconstruction above elevator-specific mechanics."
            ),
            "candidate_tradeoffs": {
                "candidate_1": "More bodily, moment-by-moment reconstruction.",
                "candidate_2": "Makes elevator sensor mechanics the central forensic pleasure.",
            },
            "rejected_candidate_reasons": {},
        },
    )

    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.NON_ADJUDICABLE
    assert state.non_adjudicable_reason == "comparative_judgment"
    assert state.recommended_candidate_id is None

    result = main(["story-discovery", "review", "--project", str(tmp_path)])
    rendered = capsys.readouterr().out
    assert result == 0
    assert "does not have an honest preference" in rendered
    assert "Hidden Seconds" in rendered
    assert "Weight of an Alibi" in rendered
    assert "story-discovery accept story_discovery/candidate_1.yaml" in rendered
    assert "story-discovery accept story_discovery/candidate_2.yaml" in rendered
    assert "Nothing canonical has changed." in rendered
    assert not (tmp_path / "story_identity.yaml").exists()


def test_qualified_legacy_no_winner_remains_invalid(tmp_path: Path) -> None:
    declared = _brief(tmp_path)
    _write_candidates(tmp_path)
    _write_yaml(
        tmp_path / "story_discovery" / "discovery_set.yaml",
        {
            "intent_mode": "intent_aware",
            "declared_author_intent": declared,
            "causal_analysis": _qualified_causal(),
        },
    )
    state = classify_story_discovery_project(tmp_path)
    assert state.kind is StoryDiscoveryStateKind.DISCOVERY_INVALID


def test_persisted_advisory_basis_is_visible_in_review(tmp_path: Path, capsys) -> None:
    declared = _brief(tmp_path)
    _write_candidates(tmp_path)
    _write_yaml(
        tmp_path / "story_discovery" / "discovery_set.yaml",
        {
            "intent_mode": "intent_aware",
            "declared_author_intent": declared,
            "causal_analysis": _qualified_causal(),
            "recommendation_status": "recommended",
            "recommendation_basis": "advisory_artistic_preference",
            "recommended_candidate_id": "candidate_1",
            "recommendation_rationale": "Auteur prefers the tighter reconstruction rhythm.",
            "candidate_tradeoffs": {
                "candidate_2": "Elevator mechanics become more central instead."
            },
            "rejected_candidate_reasons": {
                "candidate_2": "Elevator mechanics become more central instead."
            },
        },
    )

    result = main(["story-discovery", "review", "--project", str(tmp_path)])
    rendered = capsys.readouterr().out
    assert result == 0
    assert "Auteur's advisory preference" in rendered
    assert "Why Auteur prefers it" in rendered
    assert "not an additional author requirement" in rendered


def test_persisted_explicit_intent_basis_is_visible_in_review(tmp_path: Path, capsys) -> None:
    declared = _brief(tmp_path)
    _write_candidates(tmp_path)
    _write_yaml(
        tmp_path / "story_discovery" / "discovery_set.yaml",
        {
            "intent_mode": "intent_aware",
            "declared_author_intent": declared,
            "causal_analysis": _qualified_causal(),
            "recommendation_status": "recommended",
            "recommendation_basis": "explicit_intent_fit",
            "recommended_candidate_id": "candidate_2",
            "recommendation_rationale": (
                "The declared requirement that elevator mechanics matter materially favors this direction."
            ),
            "candidate_tradeoffs": {"candidate_1": "Uses fewer elevator-specific mechanics."},
            "rejected_candidate_reasons": {"candidate_1": "Uses fewer elevator-specific mechanics."},
        },
    )

    result = main(["story-discovery", "review", "--project", str(tmp_path)])
    rendered = capsys.readouterr().out
    assert result == 0
    assert "Best fit to your declared intent" in rendered
    assert "Why this direction fits what you said you want" in rendered
