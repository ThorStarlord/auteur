from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import yaml

from auteur.cli_handlers import RecommendOpenEndedData
from auteur.llm import LLMResponse
from auteur.story_discovery_recommend import (
    _augment_artifacts,
    _recommendation_surface_lines,
    dispatch_story_discovery_recommend,
)


class _Identity:
    def __init__(self, suffix: str):
        self.title = f"Story {suffix}"
        self.core_answer = f"core answer {suffix}"
        self.target_experience = SimpleNamespace(primary=f"reader experience {suffix}")
        self.central_engine = SimpleNamespace(
            want=f"want {suffix}",
            resistance=f"resistance {suffix}",
            conflict=f"conflict {suffix}",
            stakes=f"stakes {suffix}",
            change=f"change {suffix}",
        )
        self.genre_contract_snapshot = None
        self.story_type = SimpleNamespace(model_dump=lambda mode="json": {})
        self.not_this = []
        self.open_questions = []
        self.author_overrides = []


class _DumpableIdentity(_Identity):
    def __init__(self, suffix: str):
        super().__init__(suffix)
        self.target_experience = SimpleNamespace(
            primary=f"reader experience {suffix}",
            model_dump=lambda mode="json": {"primary": f"reader experience {suffix}"},
        )
        self.central_engine = SimpleNamespace(
            want=f"want {suffix}",
            resistance=f"resistance {suffix}",
            conflict=f"conflict {suffix}",
            stakes=f"stakes {suffix}",
            change=f"change {suffix}",
            model_dump=lambda mode="json": {
                "want": f"want {suffix}",
                "resistance": f"resistance {suffix}",
                "conflict": f"conflict {suffix}",
                "stakes": f"stakes {suffix}",
                "change": f"change {suffix}",
            },
        )


def _candidate(candidate_id: str, suffix: str, *, fit: int = 80):
    return SimpleNamespace(
        candidate_id=candidate_id,
        identity=_DumpableIdentity(suffix),
        candidate=SimpleNamespace(
            validation_status="valid",
            warning_count=0,
            contract_fit=fit,
            contract_fit_status="strong" if fit >= 80 else "mixed",
            contract_fit_problems=[],
            contract_fit_notes=[],
        ),
        yaml_content="",
    )


def _args(tmp_path: Path, *, candidates: int = 3):
    return SimpleNamespace(
        candidates=candidates,
        brain_dump="A controlled Phase B premise.",
        provider="anthropic",
        model=None,
        genre=None,
        medium=None,
        mode=None,
        lens=None,
        strict_candidate_count=False,
        debug=False,
        project=None,
        output=tmp_path / "story_discovery",
    )


def _serializer(data, output_dir: Path, premise: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for co in data.candidates:
        path = output_dir / f"{co.candidate_id}.yaml"
        path.write_text("candidate: true\n", encoding="utf-8")
        written.append(path)
    discovery_set = output_dir / "discovery_set.yaml"
    discovery_set.write_text("mode: open_ended\n", encoding="utf-8")
    report = output_dir / "discovery_report.yaml"
    report.write_text("chosen_candidate: null\n", encoding="utf-8")
    comparison = output_dir / "comparison.md"
    comparison.write_text("# Story Discovery\n", encoding="utf-8")
    written.extend([discovery_set, report, comparison])
    return written


def _profile_response(request):
    evidence = json.loads(request.user.split("BOUNDED STORY EVIDENCE\n", 1)[1])
    conflict = evidence["candidate_commitments"]["central_engine"]["conflict"]
    suffix = conflict.replace("conflict ", "")
    return {
        "primary_strategy": f"resolve through {suffix}",
        "causal_owner": "protagonist-led",
        "external_action_pattern": [f"act {suffix}", f"pressure {suffix}", f"resolve {suffix}"],
        "pressure_system": f"resistance {suffix}",
        "reversal_mechanics": [f"{suffix} reverses the plan"],
        "climax_mechanic": f"resolve through the {suffix} mechanism",
        "scene_families": [f"{suffix} setup", f"{suffix} pressure", f"{suffix} climax"],
        "evidence_gaps": [],
    }


def _diversity_response(request):
    pairs = json.loads(request.user.split("CAUSAL PROFILE PAIRS\n", 1)[1])
    return {
        "assessments": [
            {
                "left_evidence_key": pair["left_evidence_key"],
                "right_evidence_key": pair["right_evidence_key"],
                "classification": "distinct",
                "shared_causal_mechanics": ["same controlled premise"],
                "material_differences": ["different controlled conflict mechanics"],
                "scene_consequence": "The controlled candidates imply different major scenes.",
                "rationale": "Phase B compatibility fixture through F3.",
            }
            for pair in pairs
        ]
    }


def test_phase_b_multi_survivor_surface_is_author_facing_and_ordered(tmp_path):
    first = _candidate("candidate_1", "one", fit=100)
    second = _candidate("candidate_2", "two", fit=60)
    third = _candidate("candidate_3", "three", fit=80)

    lines = _recommendation_surface_lines(
        winner="candidate_2",
        rationale="Story two makes the premise mechanism causal.",
        rejected={
            "candidate_1": "More compliant but generic.",
            "candidate_3": "More thematic but less immediate.",
        },
        candidate_outputs=[first, second, third],
        output_dir=tmp_path / "story_discovery",
        requested_candidates=3,
    )
    text = "\n".join(lines)

    assert "RECOMMENDED — Story two (`candidate_2`)" in text
    assert "core answer two" in text
    assert "Story two makes the premise mechanism causal." in text
    assert "Story one (`candidate_1`) — More compliant but generic." in text
    assert "Story three (`candidate_3`) — More thematic but less immediate." in text
    assert text.index("Story one (`candidate_1`)") < text.index("Story three (`candidate_3`)")
    assert "Nothing has been accepted yet." in text
    assert "auteur story-discovery accept" in text
    assert "candidate_2.yaml --output story_identity.yaml" in text
    assert "candidate_1.yaml --output story_identity.yaml" in text
    assert "candidate_3.yaml --output story_identity.yaml" in text


def test_phase_b_primary_surface_does_not_expose_contract_fit(tmp_path):
    high_fit = _candidate("candidate_1", "high-fit", fit=100)
    lower_fit = _candidate("candidate_2", "premise-specific", fit=60)

    text = "\n".join(
        _recommendation_surface_lines(
            winner="candidate_2",
            rationale="The lower-fit candidate uses the premise more causally.",
            rejected={"candidate_1": "Higher compliance does not make it the stronger story."},
            candidate_outputs=[high_fit, lower_fit],
            output_dir=tmp_path / "story_discovery",
            requested_candidates=2,
        )
    )

    assert "RECOMMENDED — Story premise-specific (`candidate_2`)" in text
    assert "contract_fit" not in text
    assert "100" not in text
    assert "60" not in text


def test_phase_b_single_survivor_is_viability_not_comparative_recommendation(tmp_path):
    survivor = _candidate("candidate_1", "only", fit=70)
    rationale = (
        "candidate_1 is the only candidate that survived StoryIdentity validation "
        "from a 3-candidate search. This is a viability result, not a comparative "
        "artistic-quality judgment."
    )

    text = "\n".join(
        _recommendation_surface_lines(
            winner="candidate_1",
            rationale=rationale,
            rejected={},
            candidate_outputs=[survivor],
            output_dir=tmp_path / "story_discovery",
            requested_candidates=3,
        )
    )

    assert "ONLY VIABLE INTERPRETATION — Story only (`candidate_1`)" in text
    assert "viability result" in text
    assert "RECOMMENDED —" not in text
    assert "candidate_1.yaml --output story_identity.yaml" in text


def test_phase_b_comparison_document_mirrors_author_surface(tmp_path):
    output_dir = tmp_path / "story_discovery"
    output_dir.mkdir()
    (output_dir / "discovery_set.yaml").write_text("mode: open_ended\n", encoding="utf-8")
    (output_dir / "discovery_report.yaml").write_text("chosen_candidate: null\n", encoding="utf-8")
    (output_dir / "comparison.md").write_text("# Story Discovery\n", encoding="utf-8")

    first = _candidate("candidate_1", "one")
    second = _candidate("candidate_2", "two")
    surface_lines = _recommendation_surface_lines(
        winner="candidate_2",
        rationale="Story two wins comparatively.",
        rejected={"candidate_1": "Story one gives up premise specificity."},
        candidate_outputs=[first, second],
        output_dir=output_dir,
        requested_candidates=2,
    )

    _augment_artifacts(
        output_dir,
        winner="candidate_2",
        rationale="Story two wins comparatively.",
        rejected={"candidate_1": "Story one gives up premise specificity."},
        surface_lines=surface_lines,
    )

    comparison = (output_dir / "comparison.md").read_text(encoding="utf-8")
    report = yaml.safe_load((output_dir / "discovery_report.yaml").read_text(encoding="utf-8"))
    assert "RECOMMENDED — Story two (`candidate_2`)" in comparison
    assert "Story one (`candidate_1`) — Story one gives up premise specificity." in comparison
    assert "Nothing has been accepted yet." in comparison
    assert "candidate_2.yaml --output story_identity.yaml" in comparison
    assert report["recommended_candidate_id"] == "candidate_2"


def test_phase_b_dispatch_prints_surface_without_promoting_canon(tmp_path, monkeypatch, capsys):
    first = _candidate("candidate_1", "one", fit=100)
    second = _candidate("candidate_2", "two", fit=60)
    data = RecommendOpenEndedData(
        candidates=[first, second],
        rec_set=SimpleNamespace(recommended_candidate_id=None),
        comparison_lines=[],
    )
    result = SimpleNamespace(is_success=True, data=data, error="", exit_code=0)
    judge_json = (
        '{"recommended_candidate_id":"candidate_2",'
        '"recommendation_rationale":"Story two uses the premise causally.",'
        '"rejected_candidate_reasons":{"candidate_1":"Story one genericizes it."}}'
    )

    class _Client:
        def complete(self, request):
            if "bounded narrative-causality profiler" in request.system:
                return LLMResponse(text=json.dumps(_profile_response(request)), input_tokens=1, output_tokens=1)
            if "causal-diversity assessor" in request.system:
                return LLMResponse(text=json.dumps(_diversity_response(request)), input_tokens=1, output_tokens=1)
            return LLMResponse(text=judge_json, input_tokens=1, output_tokens=1)

    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: _Client())
    monkeypatch.setattr("auteur.cli_handlers.handle_identity_recommend", lambda **k: result)
    monkeypatch.setattr("auteur.cli_serializers.serialize_story_discovery", _serializer)

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, candidates=2))
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "RECOMMENDED — Story two (`candidate_2`)" in captured.out
    assert "Story one (`candidate_1`) — Story one genericizes it." in captured.out
    assert "Nothing has been accepted yet." in captured.out
    assert "contract_fit" not in captured.out
    assert not (tmp_path / "story_identity.yaml").exists()


def test_phase_b_zero_survivor_failure_has_recovery_guidance(tmp_path, monkeypatch, capsys):
    result = SimpleNamespace(
        is_success=False,
        data=None,
        error="0 valid candidates survived validation checks.",
        exit_code=1,
    )

    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *a, **k: SimpleNamespace(complete=lambda request: None),
    )
    monkeypatch.setattr("auteur.cli_handlers.handle_identity_recommend", lambda **k: result)

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, candidates=3))
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "no Story Discovery candidate survived validation" in captured.err
    assert "Try revising the premise or constraints" in captured.err
    assert "Use --debug" in captured.err
    assert not (tmp_path / "story_discovery").exists()
    assert not (tmp_path / "story_identity.yaml").exists()
