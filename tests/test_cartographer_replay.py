"""Focused tests for the evaluation-only Cartographer replay boundary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from test_narrative_engine_integration import blueprint_with_psychology as _blueprint_fixture

from auteur.cartographer import render_cartographer_prompt
from auteur.cartographer_models import PlanningCall
from auteur.evaluation.cartographer_replay import (
    CaptureError,
    CaptureIntegrityError,
    CaptureRequest,
    CaptureProvider,
    CaptureResponse,
    CartographerCaptureV1,
    CartographerEvaluationPairV1,
    CartographerReviewRecordV1,
    ReplayLLMClient,
    ReplayMismatchError,
    artifact_hash,
    load_capture,
    planning_call_hash,
    prompt_hash,
    raw_response_hash,
    validate_capture,
    validate_pair,
    write_capture,
)
from auteur.llm import LLMRequest
from auteur.blueprint import StoryBlueprint
from auteur.cartographer_compiler import compile_outline


@pytest.fixture
def blueprint_with_psychology():
    return _blueprint_fixture.__wrapped__()


def _capture(call: PlanningCall, *, condition: str = "control", raw: str = "conflict_report: archived"):
    system, user = render_cartographer_prompt(call)
    request = CaptureRequest(model=None, temperature=0.1, max_tokens=4000)
    response = CaptureResponse(raw_text=raw, parse_status="not_attempted")
    data = {
        "artifact_type": "cartographer_evaluation_capture",
        "schema_version": 1,
        "case_id": "case-1",
        "pair_id": "pair-1",
        "condition": condition,
        "repetition": 0,
        "created_at": "2026-07-28T00:00:00Z",
        "source_blueprint_hash": "sha256:blueprint",
        "source_commit": "source-sha",
        "planning_call": call.model_dump(mode="json"),
        "system_prompt": system,
        "user_prompt": user,
        "profile_emotional_targets": call.profile_emotional_targets,
        "authored_emotional_target": call.emotional_target,
        "request": request.model_dump(mode="json"),
        "provider": CaptureProvider(name="replay", input_tokens=3, output_tokens=4).model_dump(mode="json"),
        "response": response.model_dump(mode="json"),
        "integrity": {
            "prompt_hash": prompt_hash(system, user),
            "planning_call_hash": planning_call_hash(call.model_dump(mode="json")),
            "raw_response_hash": raw_response_hash(raw),
            "parsed_output_hash": None,
            "artifact_hash": "",
            "redaction_status": "allowlisted",
        },
    }
    data["integrity"]["artifact_hash"] = artifact_hash(data)
    return CartographerCaptureV1.model_validate(data)


def test_capture_round_trip_and_hashes_are_stable(tmp_path, blueprint_with_psychology):
    capture = _capture(PlanningCall.for_chapter(blueprint_with_psychology, 1))
    path = tmp_path / "capture.json"
    write_capture(capture, path)
    loaded = load_capture(path)
    assert loaded.model_dump(mode="json") == capture.model_dump(mode="json")
    assert json.loads(path.read_text(encoding="utf-8"))["integrity"]["artifact_hash"].startswith("sha256:")


def test_canonical_hash_ignores_mapping_insertion_order(blueprint_with_psychology):
    call = PlanningCall.for_chapter(blueprint_with_psychology, 1)
    first = call.model_dump(mode="json")
    second = dict(first)
    second["profile_emotional_targets"] = {"z": 0.2, "a": 0.8}
    first["profile_emotional_targets"] = {"a": 0.8, "z": 0.2}
    assert planning_call_hash(first) == planning_call_hash(second)


def test_prompt_and_response_mutations_fail_integrity(blueprint_with_psychology):
    capture = _capture(PlanningCall.for_chapter(blueprint_with_psychology, 1))
    prompt_changed = capture.model_copy(update={"user_prompt": capture.user_prompt + "x"})
    with pytest.raises(CaptureIntegrityError, match="prompt hash"):
        validate_capture(prompt_changed)
    response = capture.response.model_copy(update={"raw_text": "changed"})
    response_changed = capture.model_copy(update={"response": response})
    with pytest.raises(CaptureIntegrityError, match="raw response hash"):
        validate_capture(response_changed)


def test_artifact_hash_excludes_only_artifact_hash(blueprint_with_psychology):
    capture = _capture(PlanningCall.for_chapter(blueprint_with_psychology, 1))
    data = capture.model_dump(mode="json")
    original = artifact_hash(data)
    data["integrity"]["artifact_hash"] = "sha256:other"
    assert artifact_hash(data) == original
    data["integrity"]["prompt_hash"] = "sha256:other"
    assert artifact_hash(data) != original


def test_replay_returns_exact_response_without_provider(blueprint_with_psychology):
    call = PlanningCall.for_chapter(blueprint_with_psychology, 1)
    capture = _capture(call, raw="conflict_report: archived")
    client = ReplayLLMClient(capture)
    system, user = render_cartographer_prompt(call)
    response = client.complete(LLMRequest(system=system, user=user, temperature=0.1, max_tokens=4000))
    assert response.text == "conflict_report: archived"
    assert (response.input_tokens, response.output_tokens) == (3, 4)


def test_replay_rejects_request_drift(blueprint_with_psychology):
    call = PlanningCall.for_chapter(blueprint_with_psychology, 1)
    capture = _capture(call)
    client = ReplayLLMClient(capture)
    system, user = render_cartographer_prompt(call)
    with pytest.raises(ReplayMismatchError, match="temperature"):
        client.complete(LLMRequest(system=system, user=user, temperature=0.2, max_tokens=4000))


def test_pair_allows_only_profile_context_difference(blueprint_with_psychology):
    base = PlanningCall.for_chapter(blueprint_with_psychology, 1)
    treatment_call = base.model_copy(update={"profile_emotional_targets": {"dread": 0.9}})
    control = _capture(base, condition="control")
    treatment = _capture(treatment_call, condition="treatment")
    pair = CartographerEvaluationPairV1(
        evaluation_id="eval-1",
        pair_id="pair-1",
        control_artifact="control.json",
        treatment_artifact="treatment.json",
        only_expected_input_difference=[
            "planning_call.profile_emotional_targets",
            "rendered_profile_prompt_section",
        ],
        rubric_version=1,
    )
    validate_pair(pair, control, treatment)


def test_pair_rejects_authored_target_drift(blueprint_with_psychology):
    base = PlanningCall.for_chapter(blueprint_with_psychology, 1)
    control = _capture(base, condition="control")
    altered = base.model_copy(update={"emotional_target": "different authored target"})
    treatment = _capture(altered, condition="treatment")
    pair = CartographerEvaluationPairV1(
        evaluation_id="eval-1", pair_id="pair-1", control_artifact="c", treatment_artifact="t",
        only_expected_input_difference=["planning_call.profile_emotional_targets", "rendered_profile_prompt_section"],
        rubric_version=1,
    )
    with pytest.raises(CaptureError):
        validate_pair(pair, control, treatment)


def test_capture_rejects_secret_bearing_metadata(blueprint_with_psychology):
    capture = _capture(PlanningCall.for_chapter(blueprint_with_psychology, 1))
    with pytest.raises(Exception, match="forbidden metadata field"):
        data = capture.model_dump(mode="json")
        data["provider"]["api_key"] = "secret"
        CartographerCaptureV1.model_validate(data)


def test_review_record_keeps_subjective_ratings_separate_and_bounded():
    review = CartographerReviewRecordV1(
        evaluation_id="eval-1", pair_id="pair-1", reviewer_id="reviewer-a",
        reviewer_type="human", blinded_condition_order=["treatment", "control"],
        rubric_version=1, ratings={"usefulness": 2, "restraint": -1},
        confidence="MEDIUM", rationale="The treatment changes scene ordering.",
        reviewed_at="2026-07-28T00:00:00Z",
    )
    assert review.reviewer_type == "human"
    with pytest.raises(ValueError, match="between -2 and 2"):
        CartographerReviewRecordV1(
            evaluation_id="eval-1", pair_id="pair-1", reviewer_id="r",
            reviewer_type="human", blinded_condition_order=["control", "treatment"],
            rubric_version=1, ratings={"usefulness": 3}, confidence="LOW",
            rationale="bad", reviewed_at="2026-07-28T00:00:00Z",
        )


def test_replay_uses_existing_compile_outline_parser(tmp_path, blueprint_with_psychology):
    source = StoryBlueprint.from_yaml(Path("examples/sample_blueprint.yaml"))
    one_chapter = source.model_copy(
        update={"structure": source.structure.model_copy(update={"estimated_chapters": 1})}
    )
    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.write_text(
        yaml.safe_dump(one_chapter.model_dump(mode="json")), encoding="utf-8"
    )
    call = PlanningCall.for_chapter(one_chapter, 1)
    raw = "\n".join([
        "scope: chapter", "chapter_index: 1", "chapter_summary: Archived chapter.",
        "scenes:", "  - scene_id: archived", "    pov_character: Kael",
        "    location: Tavern", "    summary: The archived plan begins.",
        "    key_events: []", "    character_state_changes: []",
        "    arc_advancements: []", "    estimated_tension: 4",
        "    emotional_tone: quiet", "arc_pushes: []",
        "contract_compliance: []", "expected_elements_touched: []",
        "forbidden_tropes_avoided: []", "estimated_chapter_tension: 4",
        "thematic_reinforcement: theme", "conflict_report: null", "",
    ])
    capture = _capture(call, raw=raw)
    output = tmp_path / "outline.yaml"
    compile_outline(
        tmp_path, blueprint_path, output, split_output=False,
        llm=ReplayLLMClient(capture),
    )
    result = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert result["chapters"][0]["scenes"][0]["scene_id"] == "archived"
