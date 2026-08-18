from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from auteur.llm import LLMResponse
from auteur.story_discovery_recommend import (
    _build_judge_request,
    _parse_judgment,
    _refresh_project_contract,
    _require_distinct_engines,
    dispatch_story_discovery_recommend,
)


class _Dumpable:
    def __init__(self, data: dict):
        self._data = data

    def model_dump(self, mode: str = "json") -> dict:
        return dict(self._data)


class _Engine(_Dumpable):
    def __init__(self, suffix: str):
        data = {
            "want": f"want {suffix}",
            "resistance": f"resistance {suffix}",
            "conflict": f"conflict {suffix}",
            "stakes": f"stakes {suffix}",
            "change": f"change {suffix}",
        }
        super().__init__(data)
        for key, value in data.items():
            setattr(self, key, value)


class _Contract(_Dumpable):
    pass


class _Identity:
    def __init__(self, suffix: str, *, contract=None):
        self.title = f"Candidate {suffix}"
        self.core_answer = f"core answer {suffix}"
        self.target_experience = _Dumpable(
            {"primary": f"feeling {suffix}", "progression": f"progression {suffix}"}
        )
        self.story_type = _Dumpable(
            {"genre": "mystery", "medium": "novella", "mode": "dramatic"}
        )
        self.central_engine = _Engine(suffix)
        self.not_this = []
        self.open_questions = []
        self.alternatives = []
        self.confidence = 0.8
        self.why_this_is_best = f"advocacy {suffix}"
        self.rejected_directions = []
        self.genre_contract_snapshot = contract

    def model_dump(self, mode: str = "json") -> dict:
        contract = self.genre_contract_snapshot
        return {
            "title": self.title,
            "core_answer": self.core_answer,
            "central_engine": self.central_engine.model_dump(mode=mode),
            "genre_contract_snapshot": (
                contract.model_dump(mode=mode) if contract is not None else None
            ),
        }


def _candidate(candidate_id: str, suffix: str, *, fit: int = 80, contract=None):
    candidate = SimpleNamespace(
        candidate_id=candidate_id,
        lens="commercial_clarity",
        best_basis=SimpleNamespace(value="genre_aligned"),
        validation_status="valid",
        warning_count=0,
        contract_fit=fit,
        contract_fit_status="strong" if fit >= 80 else "mixed",
        contract_fit_problems=[],
        contract_fit_notes=[],
    )
    return SimpleNamespace(
        candidate_id=candidate_id,
        identity=_Identity(suffix, contract=contract),
        candidate=candidate,
        yaml_content="",
    )


def _args(tmp_path: Path, *, candidates: int = 3, genre: str | None = None):
    return SimpleNamespace(
        candidates=candidates,
        brain_dump="A controlled Phase A premise.",
        provider="anthropic",
        model=None,
        genre=genre,
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


def test_phase_a_false_numeric_winner_is_not_automatically_selected(tmp_path, monkeypatch):
    high_fit = _candidate("candidate_1", "high-fit", fit=100)
    lower_fit = _candidate("candidate_2", "premise-specific", fit=60)
    data = SimpleNamespace(
        candidates=[high_fit, lower_fit],
        rec_set=SimpleNamespace(recommended_candidate_id=None),
    )
    result = SimpleNamespace(is_success=True, data=data, error="", exit_code=0)

    judge_json = (
        '{"recommended_candidate_id":"candidate_2",'
        '"recommendation_rationale":"Candidate 2 makes the premise mechanism causal.",'
        '"rejected_candidate_reasons":{"candidate_1":'
        '"Candidate 1 is compliant but genericizes the premise."}}'
    )

    class _Client:
        def complete(self, request):
            # Contract fit remains visible as compliance evidence, but there is no
            # deterministic ranker that can override the comparative judgment.
            assert '"contract_fit": 100' in request.user
            assert '"contract_fit": 60' in request.user
            return LLMResponse(text=judge_json, input_tokens=1, output_tokens=1)

    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: _Client())
    monkeypatch.setattr("auteur.cli_handlers.handle_identity_recommend", lambda **k: result)
    monkeypatch.setattr("auteur.cli_serializers.serialize_story_discovery", _serializer)

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, candidates=2, genre="mystery"))
    assert exit_code == 0
    report = yaml.safe_load(
        (tmp_path / "story_discovery" / "discovery_report.yaml").read_text(encoding="utf-8")
    )
    assert report["recommended_candidate_id"] == "candidate_2"
    assert not (tmp_path / "story_identity.yaml").exists()


def test_phase_a_one_survivor_skips_comparative_judge(tmp_path, monkeypatch):
    survivor = _candidate("candidate_1", "only", fit=70)
    data = SimpleNamespace(
        candidates=[survivor],
        rec_set=SimpleNamespace(recommended_candidate_id=None),
    )
    result = SimpleNamespace(is_success=True, data=data, error="", exit_code=0)

    class _Client:
        def complete(self, request):
            raise AssertionError("single-survivor path must not call the creative judge")

    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: _Client())
    monkeypatch.setattr("auteur.cli_handlers.handle_identity_recommend", lambda **k: result)
    monkeypatch.setattr("auteur.cli_serializers.serialize_story_discovery", _serializer)

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, candidates=3))
    assert exit_code == 0
    report = yaml.safe_load(
        (tmp_path / "story_discovery" / "discovery_report.yaml").read_text(encoding="utf-8")
    )
    assert report["recommended_candidate_id"] == "candidate_1"
    assert "viability result" in report["recommendation_rationale"]


def test_phase_a_no_survivor_fails_without_recommendation_or_canon(tmp_path, monkeypatch):
    result = SimpleNamespace(
        is_success=False,
        data=None,
        error="0 valid candidates survived validation checks.",
        exit_code=1,
    )

    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *a, **k: SimpleNamespace(complete=lambda request: pytest.fail("judge must not run")),
    )
    monkeypatch.setattr("auteur.cli_handlers.handle_identity_recommend", lambda **k: result)

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, candidates=3))
    assert exit_code == 1
    assert not (tmp_path / "story_discovery").exists()
    assert not (tmp_path / "story_identity.yaml").exists()


def test_phase_a_duplicate_search_set_fails_before_judging():
    first = _candidate("candidate_1", "same")
    duplicate = _candidate("candidate_2", "same")
    with pytest.raises(ValueError, match="exact duplicates"):
        _require_distinct_engines([first, duplicate])


def test_phase_a_project_local_contract_remains_authoritative(tmp_path, monkeypatch):
    contract = _Contract(
        {
            "genre_id": "other",
            "display_name": "Cozy Political Fantasy",
            "core_truth": "Civic restoration through clever public repair.",
        }
    )
    co = _candidate("candidate_1", "custom-contract", fit=20)
    args = SimpleNamespace(project=tmp_path, genre="other")

    monkeypatch.setattr(
        "auteur.genres.registry.load_project_genre_contract",
        lambda project, genre: contract,
    )
    monkeypatch.setattr(
        "auteur.cli_handlers.analyze_contract_fit",
        lambda identity: (77, "mixed", ["bounded issue"], ["custom authority"]),
    )

    _refresh_project_contract([co], args)

    assert co.identity.genre_contract_snapshot is contract
    assert co.candidate.contract_fit == 77
    assert co.candidate.contract_fit_status == "mixed"
    assert "Cozy Political Fantasy" in co.yaml_content


def test_phase_a_judge_request_excludes_generated_summary_fields():
    first = _candidate("candidate_1", "one", fit=90)
    second = _candidate("candidate_2", "two", fit=70)
    for co in (first, second):
        co.candidate.recommendation_summary = "SELF ADVOCACY SUMMARY"
        co.candidate.tradeoffs = ["SELF ADVOCACY TRADEOFF"]
        co.candidate.risks = ["SELF ADVOCACY RISK"]
        co.candidate.best_for = ["SELF ADVOCACY BEST FOR"]

    request = _build_judge_request(
        "A premise.",
        [first, second],
        genre="mystery",
        medium=None,
        mode=None,
    )
    assert "SELF ADVOCACY SUMMARY" not in request.user
    assert "SELF ADVOCACY TRADEOFF" not in request.user
    assert "SELF ADVOCACY RISK" not in request.user
    assert "SELF ADVOCACY BEST FOR" not in request.user

    winner, rationale, rejected = _parse_judgment(
        '{"recommended_candidate_id":"candidate_2",'
        '"recommendation_rationale":"Premise-specific causal use.",'
        '"rejected_candidate_reasons":{"candidate_1":"More generic."}}',
        ["candidate_1", "candidate_2"],
    )
    assert winner == "candidate_2"
    assert rationale
    assert set(rejected) == {"candidate_1"}
