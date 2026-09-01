from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from auteur.llm import LLMResponse
from auteur.story_discovery_causality import (
    CausalProfile,
    build_causal_profile_request,
    causal_evidence_key,
    derive_causal_profile,
    parse_causal_profile,
    persist_causal_analysis,
)


class Dumpable(SimpleNamespace):
    def model_dump(self, mode="json"):
        return deepcopy(self.__dict__)


def _candidate(
    candidate_id: str = "candidate_1",
    *,
    title: str = "Nothing Missing",
    conflict: str = "The crew authenticates records until the director's ownership claim collapses.",
    core_answer: str = "The crew defeats the director by replacing possession with public proof.",
    advocacy: str = "baseline self advocacy",
):
    identity = SimpleNamespace(
        title=title,
        core_answer=core_answer,
        central_engine=Dumpable(
            want="Expose the corrupt museum director without stealing anything.",
            resistance="The director controls access and the official provenance story.",
            conflict=conflict,
            stakes="If the proof fails, the director keeps control and the crew loses its only lawful opening.",
            change="The crew learns to make public proof, not possession, its definition of victory.",
        ),
        story_type=Dumpable(
            genre="other",
            medium="novel",
            mode="other",
            target_audience="adult",
        ),
        target_experience=Dumpable(primary="operational pressure"),
        not_this=["a theft disguised as a no-theft heist"],
        open_questions=["Which proof becomes decisive?"],
        author_overrides=[],
        hard_constraints=["nothing may be stolen", "nobody on the crew knowingly lies"],
        genre_contract_snapshot=None,
        why_this_is_best=advocacy,
        alternatives=[advocacy],
        confidence=0.99,
        rejected_directions=[advocacy],
    )
    candidate = SimpleNamespace(
        lens=advocacy,
        best_basis=advocacy,
        recommendation_summary=advocacy,
        tradeoffs=[advocacy],
        risks=[advocacy],
        best_for=[advocacy],
    )
    return SimpleNamespace(candidate_id=candidate_id, identity=identity, candidate=candidate)


def _profile_payload(**overrides):
    payload = {
        "primary_strategy": "authenticate and connect provenance evidence until ownership claims collapse",
        "causal_owner": "crew-led investigation against institutional gatekeeping",
        "external_action_pattern": ["retrieve", "authenticate", "connect", "disclose"],
        "pressure_system": "access and evidentiary standards close off easy exposure",
        "reversal_mechanics": [
            "a promising record creates a stronger authentication burden",
            "the director reframes apparently decisive proof as routine ambiguity",
        ],
        "climax_mechanic": "the crew publicly proves the director's claim cannot survive authenticated provenance",
        "scene_families": [
            "records retrieval",
            "authentication disputes",
            "public evidentiary confrontation",
        ],
        "evidence_gaps": [],
    }
    payload.update(overrides)
    return payload


class ProfileClient:
    def __init__(self, payload=None):
        self.payload = payload if payload is not None else _profile_payload()
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        text = self.payload if isinstance(self.payload, str) else json.dumps(self.payload)
        return LLMResponse(text=text, input_tokens=1, output_tokens=1)


def test_causal_profile_is_strict_and_round_trips():
    profile = CausalProfile.model_validate(_profile_payload())
    assert profile.external_action_pattern == ["retrieve", "authenticate", "connect", "disclose"]
    assert CausalProfile.model_validate(profile.model_dump(mode="json")) == profile

    with pytest.raises(ValueError):
        CausalProfile.model_validate({**_profile_payload(), "quality_score": 99})


def test_causal_profile_requires_complete_schema():
    payload = _profile_payload()
    del payload["climax_mechanic"]
    with pytest.raises(ValueError):
        CausalProfile.model_validate(payload)


def test_malformed_profiler_output_fails_closed():
    with pytest.raises(ValueError, match="did not contain a JSON object"):
        parse_causal_profile("not json")

    with pytest.raises(ValueError, match="failed schema validation"):
        parse_causal_profile(json.dumps({"primary_strategy": "only one field"}))


def test_profiler_prompt_bounds_reversal_specificity():
    request, _ = build_causal_profile_request(_candidate(), "Museum heist premise")

    assert "mechanically implied classes of reversal" in request.system
    assert "particular witness, object, room, discovery, timing beat" in request.system
    assert "prefix that reversal\n  item exactly `hypothetical:`" in request.system
    assert "`hypothetical reversal:`" in request.system
    assert "never phrase an unsupported illustrative event as an established reversal mechanic" in request.system


def test_hypothetical_reversal_requires_explicit_evidence_gap():
    payload = _profile_payload(
        reversal_mechanics=[
            "hypothetical: a second witness appears and contradicts the remembered command"
        ],
        evidence_gaps=[],
    )

    with pytest.raises(ValueError, match="hypothetical reversal mechanics require"):
        parse_causal_profile(json.dumps(payload))


def test_hypothetical_reversal_is_preserved_when_gap_is_explicit():
    payload = _profile_payload(
        reversal_mechanics=[
            "hypothetical: truthful confrontation changes the disappearance pattern"
        ],
        evidence_gaps=[
            "hypothetical reversal: bounded evidence does not establish how confrontation changes the supernatural rule"
        ],
    )

    profile = parse_causal_profile(json.dumps(payload))

    assert profile.reversal_mechanics == [
        "hypothetical: truthful confrontation changes the disappearance pattern"
    ]
    assert profile.evidence_gaps[0].startswith("hypothetical reversal:")


def test_self_advocacy_mutation_does_not_change_profiler_input_or_key():
    first = _candidate(advocacy="BASELINE")
    second = _candidate(advocacy="MUTATED SHOULD NEVER LEAK")

    first_request, first_key = build_causal_profile_request(first, "Museum heist premise")
    second_request, second_key = build_causal_profile_request(second, "Museum heist premise")

    assert first_request.user == second_request.user
    assert first_key == second_key
    assert "MUTATED SHOULD NEVER LEAK" not in first_request.user
    assert "BASELINE" not in first_request.user


def test_candidate_id_remap_does_not_change_profiler_input_or_key():
    first = _candidate("candidate_1")
    remapped = _candidate("candidate_99")

    first_request, first_key = build_causal_profile_request(first, "Museum heist premise")
    second_request, second_key = build_causal_profile_request(remapped, "Museum heist premise")

    assert first_request.user == second_request.user
    assert first_key == second_key
    assert "candidate_1" not in first_request.user
    assert "candidate_99" not in first_request.user


def test_title_only_mutation_does_not_create_new_causal_evidence_key():
    first = _candidate(title="Nothing Missing")
    renamed = _candidate(title="The Archive Job")

    _, first_key = build_causal_profile_request(first, "Museum heist premise")
    _, second_key = build_causal_profile_request(renamed, "Museum heist premise")

    assert first_key == second_key


def test_material_causal_commitment_changes_evidence_key():
    first = _candidate()
    changed = _candidate(
        conflict=(
            "The crew schedules incompatible museum obligations so the director must publicly "
            "violate one of his own procedures."
        )
    )

    first_request, first_key = build_causal_profile_request(first, "Museum heist premise")
    changed_request, changed_key = build_causal_profile_request(changed, "Museum heist premise")

    assert first_request.user != changed_request.user
    assert first_key != changed_key


def test_declared_author_intent_is_bounded_prior_evidence():
    candidate = _candidate()
    declared = {
        "story_type": {"genre": "heist", "target_audience": "adult"},
        "architecture_preferences": {
            "complexity": "maximalist",
            "causal_distribution": "mixed",
            "engine_hierarchy": "primary_with_layers",
        },
    }

    request, _ = build_causal_profile_request(
        candidate,
        "Museum heist premise",
        declared_author_intent=declared,
    )

    assert '"declared_author_intent"' in request.user
    assert '"causal_distribution": "mixed"' in request.user


def test_derive_profile_does_not_mutate_candidate():
    candidate = _candidate()
    before = deepcopy(candidate.identity.__dict__)
    client = ProfileClient()

    record = derive_causal_profile(client, candidate, "Museum heist premise")

    assert record.primary_strategy.startswith("authenticate")
    assert len(record.evidence_key) == 20
    assert candidate.identity.__dict__ == before
    assert len(client.requests) == 1


def test_persist_causal_analysis_is_diagnostic_only(tmp_path: Path):
    output_dir = tmp_path / "story_discovery"
    output_dir.mkdir()
    report_path = output_dir / "discovery_report.yaml"
    report_path.write_text("recommended_candidate_id: candidate_1\n", encoding="utf-8")
    candidate_path = output_dir / "candidate_1.yaml"
    original_candidate = "title: Nothing Missing\ncore_answer: test\n"
    candidate_path.write_text(original_candidate, encoding="utf-8")

    client = ProfileClient()
    record = derive_causal_profile(client, _candidate(), "Museum heist premise")
    persist_causal_analysis(output_dir, {"candidate_1": record})

    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    assert report["causal_analysis"]["schema_version"] == 1
    assert report["causal_analysis"]["status"] == "diagnostic_only"
    assert report["causal_analysis"]["profiles"]["candidate_1"]["evidence_key"] == record.evidence_key
    assert candidate_path.read_text(encoding="utf-8") == original_candidate


def test_evidence_key_is_deterministic_for_json_key_order():
    first = {"premise": "x", "candidate_commitments": {"b": 2, "a": 1}}
    second = {"candidate_commitments": {"a": 1, "b": 2}, "premise": "x"}
    assert causal_evidence_key(first) == causal_evidence_key(second)
