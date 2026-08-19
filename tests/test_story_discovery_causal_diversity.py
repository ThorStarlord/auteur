from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from auteur.llm import LLMRequest, LLMResponse
from auteur.story_discovery_causality import (
    CausalAnalysis,
    CausalGuidanceClient,
    CausalProfileRecord,
    PairwiseAssessment,
    assess_causal_diversity,
    build_causal_diversity_request,
    non_adjudicable_surface_lines,
    parse_causal_diversity,
    persist_causal_analysis,
)


def _profile(
    key: str,
    *,
    strategy: str,
    actions: list[str],
    pressure: str,
    climax: str,
) -> CausalProfileRecord:
    return CausalProfileRecord(
        evidence_key=key,
        primary_strategy=strategy,
        causal_owner="protagonist-led",
        external_action_pattern=actions,
        pressure_system=pressure,
        reversal_mechanics=[f"reversal through {strategy}"],
        climax_mechanic=climax,
        scene_families=[f"{action} scene" for action in actions[:3]],
        evidence_gaps=[],
    )


def _profiles() -> dict[str, CausalProfileRecord]:
    return {
        "candidate_1": _profile(
            "aaaaaaaa111111111111",
            strategy="retrieve and authenticate provenance evidence",
            actions=["retrieve", "authenticate", "connect", "disclose"],
            pressure="evidentiary burden and restricted records",
            climax="publicly prove the director's ownership claim cannot survive",
        ),
        "candidate_2": _profile(
            "bbbbbbbb222222222222",
            strategy="weaponize incompatible institutional procedures",
            actions=["schedule", "trigger", "constrain", "force choice"],
            pressure="conflicting institutional obligations",
            climax="force the director to violate one of his own procedures publicly",
        ),
        "candidate_3": _profile(
            "cccccccc333333333333",
            strategy="stage truthful social pressure that provokes self-exposure",
            actions=["stage", "frame truthfully", "provoke", "expose"],
            pressure="audience inference and the director's need to control appearances",
            climax="provoke the director into publicly incriminating himself",
        ),
    }


class _AssessmentClient:
    def __init__(self, classification: str = "distinct"):
        self.classification = classification
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        pairs = json.loads(request.user.split("CAUSAL PROFILE PAIRS\n", 1)[1])
        return LLMResponse(
            text=json.dumps(
                {
                    "assessments": [
                        {
                            "left_evidence_key": pair["left_evidence_key"],
                            "right_evidence_key": pair["right_evidence_key"],
                            "classification": self.classification,
                            "shared_causal_mechanics": ["same premise and external objective"],
                            "material_differences": (
                                ["different action pattern and climax mechanic"]
                                if self.classification == "distinct"
                                else []
                            ),
                            "scene_consequence": (
                                "Choosing the alternative changes the major action sequence and decisive scene."
                                if self.classification == "distinct"
                                else "The major action sequence and decisive scene remain substantially the same."
                            ),
                            "rationale": "Controlled F3 semantic assessment.",
                        }
                        for pair in pairs
                    ]
                }
            ),
            input_tokens=1,
            output_tokens=1,
        )


def test_diversity_request_is_content_keyed_and_candidate_id_invariant():
    profiles = _profiles()
    request, expected_pairs = build_causal_diversity_request(profiles)
    remapped = {
        "candidate_99": profiles["candidate_2"],
        "candidate_4": profiles["candidate_3"],
        "candidate_8": profiles["candidate_1"],
    }
    remapped_request, remapped_pairs = build_causal_diversity_request(remapped)

    assert request.user == remapped_request.user
    assert expected_pairs == remapped_pairs
    assert "candidate_1" not in request.user
    assert "candidate_2" not in request.user
    assert "candidate_3" not in request.user


def test_diversity_request_is_invariant_to_mapping_order():
    profiles = _profiles()
    reversed_mapping = dict(reversed(list(profiles.items())))
    first, first_pairs = build_causal_diversity_request(profiles)
    second, second_pairs = build_causal_diversity_request(reversed_mapping)
    assert first.user == second.user
    assert first_pairs == second_pairs


def test_all_distinct_pairs_qualify_without_numeric_score():
    client = _AssessmentClient("distinct")
    analysis = assess_causal_diversity(client, _profiles())

    assert analysis.status == "qualified"
    assert len(analysis.pairwise_assessments) == 3
    assert {item.classification for item in analysis.pairwise_assessments} == {"distinct"}
    assert "score" not in client.requests[0].system.lower()
    assert "numeric" in client.requests[0].system.lower()


def test_near_duplicate_pair_blocks_comparative_adjudication():
    analysis = assess_causal_diversity(_AssessmentClient("near_duplicate"), _profiles())
    assert analysis.status == "not_adjudicable_near_duplicate"


def test_uncertain_pair_blocks_comparative_adjudication():
    analysis = assess_causal_diversity(_AssessmentClient("uncertain"), _profiles())
    assert analysis.status == "not_adjudicable_uncertain"


def test_pairwise_schema_rejects_fake_similarity_score():
    with pytest.raises(ValueError):
        PairwiseAssessment.model_validate(
            {
                "left_evidence_key": "aaaaaaaa111111111111",
                "right_evidence_key": "bbbbbbbb222222222222",
                "classification": "near_duplicate",
                "shared_causal_mechanics": ["same sequence"],
                "material_differences": [],
                "scene_consequence": "same scenes",
                "rationale": "same mechanics",
                "similarity_score": 0.98,
            }
        )


def test_incomplete_pair_coverage_fails_closed():
    profiles = _profiles()
    _, expected_pairs = build_causal_diversity_request(profiles)
    left, right = expected_pairs[0]
    response = json.dumps(
        {
            "assessments": [
                {
                    "left_evidence_key": left,
                    "right_evidence_key": right,
                    "classification": "distinct",
                    "shared_causal_mechanics": [],
                    "material_differences": ["different climax"],
                    "scene_consequence": "different scenes",
                    "rationale": "controlled",
                }
            ]
        }
    )
    with pytest.raises(ValueError, match="cover exactly every expected pair"):
        parse_causal_diversity(response, expected_pairs)


def test_duplicate_pair_assessment_fails_closed():
    profiles = {
        key: value for key, value in list(_profiles().items())[:2]
    }
    _, expected_pairs = build_causal_diversity_request(profiles)
    left, right = expected_pairs[0]
    item = {
        "left_evidence_key": left,
        "right_evidence_key": right,
        "classification": "distinct",
        "shared_causal_mechanics": [],
        "material_differences": ["different climax"],
        "scene_consequence": "different scenes",
        "rationale": "controlled",
    }
    with pytest.raises(ValueError, match="duplicate pair"):
        parse_causal_diversity(
            json.dumps({"assessments": [item, item]}),
            expected_pairs,
        )


def test_single_survivor_is_not_a_comparative_diversity_judgment():
    only = {"candidate_1": _profiles()["candidate_1"]}
    analysis = assess_causal_diversity(_AssessmentClient(), only)
    assert analysis.status == "not_applicable_single_survivor"
    assert analysis.pairwise_assessments == []


def test_generation_guidance_only_touches_candidate_generation_request():
    calls: list[LLMRequest] = []

    class _Delegate:
        def complete(self, request: LLMRequest) -> LLMResponse:
            calls.append(request)
            return LLMResponse(text="ok", input_tokens=1, output_tokens=1)

    client = CausalGuidanceClient(_Delegate())
    generation = LLMRequest(
        system="You are an expert, opinionated narrative compiler.",
        user="Premise: constrained museum heist",
    )
    judge = LLMRequest(system="You are Auteur's comparative narrative architect.", user="evidence")

    client.complete(generation)
    client.complete(judge)

    assert "CAUSAL DISTINCTNESS GUIDANCE" in calls[0].user
    assert "climax resolution mechanic" in calls[0].user
    assert calls[1].user == "evidence"


def test_non_adjudicable_surface_preserves_authority_and_candidate_access(tmp_path: Path):
    profiles = _profiles()
    analysis = CausalAnalysis(
        status="not_adjudicable_near_duplicate",
        profiles=profiles,
        pairwise_assessments=[],
    )
    candidates = [
        SimpleNamespace(candidate_id=candidate_id, identity=SimpleNamespace(title=f"Title {index}"))
        for index, candidate_id in enumerate(profiles, 1)
    ]
    lines = non_adjudicable_surface_lines(analysis, candidates, tmp_path)
    text = "\n".join(lines)

    assert "NO RECOMMENDATION YET" in text
    assert "Nothing has been accepted yet." in text
    assert "Title 1" in text
    assert "comparison.md" in text
    assert "RECOMMENDED —" not in text


def test_non_adjudicable_artifacts_do_not_invent_recommended_candidate(tmp_path: Path):
    output_dir = tmp_path / "story_discovery"
    output_dir.mkdir()
    for name in ("discovery_set.yaml", "discovery_report.yaml"):
        (output_dir / name).write_text(
            "requested_candidates: 3\nvalid_candidates: 3\n",
            encoding="utf-8",
        )

    analysis = assess_causal_diversity(_AssessmentClient("near_duplicate"), _profiles())
    persist_causal_analysis(
        output_dir,
        analysis=analysis,
        artifact_names=("discovery_set.yaml", "discovery_report.yaml"),
    )

    for name in ("discovery_set.yaml", "discovery_report.yaml"):
        payload = yaml.safe_load((output_dir / name).read_text(encoding="utf-8"))
        assert payload["causal_analysis"]["status"] == "not_adjudicable_near_duplicate"
        assert "recommended_candidate_id" not in payload


def test_same_causal_profile_under_different_trace_ids_maps_back_after_assessment():
    profiles = _profiles()
    remapped = {
        "zeta": profiles["candidate_3"],
        "alpha": profiles["candidate_1"],
        "middle": profiles["candidate_2"],
    }
    analysis = assess_causal_diversity(_AssessmentClient("distinct"), remapped)
    observed_ids = {
        candidate_id
        for item in analysis.pairwise_assessments
        for candidate_id in (item.left_candidate_id, item.right_candidate_id)
    }
    assert observed_ids == {"alpha", "middle", "zeta"}
