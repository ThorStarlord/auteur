from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from auteur.blueprint import (
    EmotionalTrajectory,
    Genre,
    StoryMedium,
    StoryMode,
    TargetAudience,
    TargetExperience,
)
from auteur.cli import main, parse_args
from auteur.cli_handlers import CandidateOutput, HandlerResult, RecommendOpenEndedData
from auteur.identity import (
    BestBasis,
    HighLevelCentralEngine,
    RecommendationMode,
    StoryIdentity,
    StoryIdentityCandidate,
    StoryIdentityRecommendationSet,
    StoryType,
)
from auteur.llm import LLMRequest, LLMResponse
from auteur.narrative_ontology.architecture_preferences import (
    CausalDistributionPreference,
    ComplexityPreference,
    EngineHierarchyPreference,
    NarrativeArchitecturePreferences,
)
from auteur.story_discovery_brief import (
    DiscoveryBrief,
    DiscoveryBriefStoryType,
    assess_intent_adequacy,
)
from auteur.story_discovery_intent import (
    _BriefAwareClient,
    _apply_brief_commitments,
    _build_intent_judge_request,
    _qualify_surface,
    dispatch_story_discovery_recommend,
)


def _target_experience() -> TargetExperience:
    return TargetExperience(
        primary_emotional_promise="claustrophobic suspicion",
        secondary_palette=["dread", "moral uncertainty"],
        avoided_experiences=["supernatural awe"],
        emotional_trajectory=EmotionalTrajectory(
            pattern="suspicion -> pressure -> reconstructive relief",
            start="suspicion",
            midpoint="pressure",
            ending="reconstructive relief",
        ),
    )


def _brief() -> DiscoveryBrief:
    return DiscoveryBrief(
        premise=(
            "A murder mystery in one elevator: six strangers, no supernatural "
            "explanation, and the killer never leaves the elevator."
        ),
        story_type=DiscoveryBriefStoryType(
            genre=Genre.MYSTERY,
            target_audience=TargetAudience.ADULT,
        ),
        target_experience=_target_experience(),
        architecture_preferences=NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.MAXIMALIST,
            causal_distribution=CausalDistributionPreference.MIXED,
            engine_hierarchy=EngineHierarchyPreference.PRIMARY_WITH_LAYERS,
        ),
        hard_constraints=[
            "The killer never leaves the elevator.",
            "The final solution is physically possible and retrospectively fair.",
        ],
    )


def _identity(suffix: str, *, audience: TargetAudience = TargetAudience.ADULT) -> StoryIdentity:
    return StoryIdentity(
        title=f"Between Floors {suffix}",
        core_answer=f"A timing-driven sealed-space murder interpretation {suffix}.",
        target_experience=TargetExperience(
            primary="claustrophobic suspicion",
            progression="suspicion -> pressure -> reconstructive relief",
            avoid=["supernatural awe"],
        ),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.PROCEDURAL,
            genre=Genre.MYSTERY,
            target_audience=audience,
        ),
        central_engine=HighLevelCentralEngine(
            want=f"The detective wants to reconstruct the impossible murder {suffix}.",
            resistance=f"Every passenger's assumptions obscure the hidden seconds {suffix}.",
            conflict=f"The detective must reconstruct conflicting timing evidence {suffix}.",
            stakes=f"A murderer escapes behind a physically impossible explanation {suffix}.",
            change=f"The detective learns to treat shared assumptions as evidence {suffix}.",
        ),
        architecture_preferences=NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.FOCUSED,
        ),
        hard_constraints=["candidate-generated constraint"],
        why_this_is_best=f"SELF ADVOCACY {suffix}",
        alternatives=[f"SELF ADVOCACY ALTERNATIVE {suffix}"],
        rejected_directions=[f"SELF ADVOCACY REJECTION {suffix}"],
        confidence=0.91,
    )


def _candidate(candidate_id: str, suffix: str) -> CandidateOutput:
    identity = _identity(suffix)
    yaml_content = yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False)
    content_hash = "sha256:" + hashlib.sha256(yaml_content.encode("utf-8")).hexdigest()
    candidate = StoryIdentityCandidate(
        candidate_id=candidate_id,
        path="",
        label=f"Candidate {suffix}",
        best_basis=BestBasis.GENRE_ALIGNED,
        lens="commercial_clarity",
        lens_rationale="Controlled F2 test lens.",
        recommendation_summary=f"summary {suffix}",
        validation_status="valid",
        warning_count=0,
        contract_fit=80,
        contract_fit_status="strong",
        content_hash=content_hash,
    )
    return CandidateOutput(
        candidate_id=candidate_id,
        yaml_content=yaml_content,
        identity=identity,
        candidate=candidate,
    )


def _data() -> RecommendOpenEndedData:
    outputs = [_candidate("candidate_1", "one"), _candidate("candidate_2", "two")]
    rec_set = StoryIdentityRecommendationSet(
        mode=RecommendationMode.OPEN_ENDED,
        source_input_path="",
        generated_at="2026-08-19T20:00:00+00:00",
        requested_candidates=2,
        valid_candidates=2,
        search_strategy="Narrative Search",
        design_lenses=["commercial_clarity", "thematic_coherence"],
        recommended_candidate_id=None,
        candidates=[co.candidate for co in outputs],
    )
    return RecommendOpenEndedData(
        candidates=outputs,
        rec_set=rec_set,
        comparison_lines=["# Story Discovery Comparison", ""],
    )


def _args(tmp_path: Path, *, brief: Path | None) -> SimpleNamespace:
    return SimpleNamespace(
        candidates=2,
        brain_dump="A raw exploratory premise.",
        brief=brief,
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


def test_discovery_brief_round_trip_preserves_rich_intent_and_omissions(tmp_path):
    brief = _brief()
    path = tmp_path / "brief.yaml"
    path.write_text(
        yaml.safe_dump(brief.declared_intent(), sort_keys=False),
        encoding="utf-8",
    )

    loaded = DiscoveryBrief.from_yaml(path)
    declared = loaded.declared_intent()

    assert loaded.story_type is not None
    assert loaded.story_type.genre is Genre.MYSTERY
    assert loaded.story_type.target_audience is TargetAudience.ADULT
    assert loaded.story_type.medium is None
    assert loaded.story_type.mode is None
    assert "medium" not in declared["story_type"]
    assert "mode" not in declared["story_type"]
    target = declared["target_experience"]
    assert target["primary_emotional_promise"] == "claustrophobic suspicion"
    assert target["secondary_palette"] == ["dread", "moral uncertainty"]
    assert target["emotional_trajectory"]["ending"] == "reconstructive relief"
    assert loaded.architecture_preferences is not None
    assert loaded.architecture_preferences.complexity is ComplexityPreference.MAXIMALIST
    assert loaded.hard_constraints == brief.hard_constraints


def test_intent_adequacy_requires_genre_audience_and_target_experience():
    inadequate = DiscoveryBrief(premise="A premise.")
    result = assess_intent_adequacy(inadequate)

    assert result.adequate is False
    assert result.missing == [
        "story_type.genre",
        "story_type.target_audience",
        "target_experience",
    ]
    assert assess_intent_adequacy(_brief()).adequate is True


def test_cli_adapter_accepts_brief_without_raw_premise_and_preserves_raw_mode():
    brief_args = parse_args(
        ["story-discovery", "run", "--brief", "brief.yaml", "--recommend"]
    )
    assert brief_args.recommend is True
    assert brief_args.brief == Path("brief.yaml")
    assert brief_args.brain_dump == "__auteur_structured_discovery_brief__"

    raw_args = parse_args(
        ["story-discovery", "run", "A raw premise.", "--recommend"]
    )
    assert raw_args.recommend is True
    assert raw_args.brief is None
    assert raw_args.brain_dump == "A raw premise."


def test_cli_rejects_brief_without_recommend(capsys):
    exit_code = main(["story-discovery", "run", "--brief", "brief.yaml"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "--brief currently requires --recommend" in captured.err


def test_under_specified_brief_fails_before_provider_use(tmp_path, monkeypatch, capsys):
    path = tmp_path / "brief.yaml"
    path.write_text("premise: A premise.\n", encoding="utf-8")

    def _explode(*args, **kwargs):
        raise AssertionError("provider must not be constructed for inadequate intent")

    monkeypatch.setattr("auteur.llm.factory.build_client", _explode)

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, brief=path))
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Insufficient author intent" in captured.err
    assert "story_type.genre" in captured.err
    assert "story_type.target_audience" in captured.err
    assert "target_experience" in captured.err
    assert not (tmp_path / "story_discovery").exists()


def test_brief_aware_client_labels_prior_intent_only_for_generation_requests():
    calls: list[LLMRequest] = []

    class _Delegate:
        def complete(self, request: LLMRequest) -> LLMResponse:
            calls.append(request)
            return LLMResponse(text="ok", input_tokens=1, output_tokens=1)

    client = _BriefAwareClient(_Delegate(), _brief())
    generation = LLMRequest(
        system="You are an expert, opinionated narrative compiler.",
        user="Premise: elevator murder",
    )
    judge = LLMRequest(system="You are a comparative judge.", user="candidate evidence")

    client.complete(generation)
    client.complete(judge)

    assert "DECLARED AUTHOR INTENT (PRIOR TO CANDIDATE GENERATION)" in calls[0].user
    assert "maximalist" in calls[0].user
    assert "killer never leaves the elevator" in calls[0].user.lower()
    assert calls[1].user == "candidate evidence"


def test_brief_commitments_preserve_unknowns_and_replace_candidate_preference_provenance():
    brief = _brief()
    output = _candidate("candidate_1", "one")
    original_medium = output.identity.story_type.medium
    original_mode = output.identity.story_type.mode

    _apply_brief_commitments([output], brief)

    identity = output.identity
    assert identity.story_type.medium is original_medium
    assert identity.story_type.mode is original_mode
    assert identity.story_type.target_audience is TargetAudience.ADULT
    assert identity.target_experience.primary == "claustrophobic suspicion"
    assert identity.target_experience.secondary_palette == ["dread", "moral uncertainty"]
    assert identity.target_experience.emotional_trajectory is not None
    assert identity.target_experience.emotional_trajectory.ending == "reconstructive relief"
    assert identity.architecture_preferences is not None
    assert identity.architecture_preferences.complexity is ComplexityPreference.MAXIMALIST
    assert identity.architecture_preferences.causal_distribution is CausalDistributionPreference.MIXED
    assert identity.hard_constraints == brief.hard_constraints
    assert "candidate-generated constraint" not in output.yaml_content
    expected_hash = "sha256:" + hashlib.sha256(output.yaml_content.encode("utf-8")).hexdigest()
    assert output.candidate.content_hash == expected_hash


def test_brief_commitment_mismatch_fails_closed_instead_of_rewriting_candidate():
    brief = _brief()
    output = _candidate("candidate_1", "one")
    output.identity.story_type.target_audience = TargetAudience.YOUNG_ADULT

    with pytest.raises(ValueError, match="contradicts declared author intent"):
        _apply_brief_commitments([output], brief)

    assert output.identity.story_type.target_audience is TargetAudience.YOUNG_ADULT


def test_intent_judge_separates_prior_intent_from_candidate_evidence_and_excludes_advocacy():
    brief = _brief()
    candidates = [_candidate("candidate_1", "one"), _candidate("candidate_2", "two")]
    _apply_brief_commitments(candidates, brief)

    request = _build_intent_judge_request(brief, candidates)

    assert request.user.index("DECLARED AUTHOR INTENT") < request.user.index(
        "SURVIVING CANDIDATE EVIDENCE"
    )
    assert '"complexity": "maximalist"' in request.user
    assert "The killer never leaves the elevator." in request.user
    assert '"hard_constraints"' in request.user
    assert "SELF ADVOCACY one" not in request.user
    assert "SELF ADVOCACY two" not in request.user
    assert "SELF ADVOCACY ALTERNATIVE" not in request.user
    assert "SELF ADVOCACY REJECTION" not in request.user
    assert "0.91" not in request.user


def test_recommendation_surface_distinguishes_exploratory_from_intent_aware():
    base = ["Story Discovery", "", "RECOMMENDED — Between Floors (`candidate_1`)"]

    exploratory = _qualify_surface(base, intent_aware=False)
    intent_aware = _qualify_surface(base, intent_aware=True)

    assert "Exploratory recommendation using Auteur's default criteria" in exploratory[1]
    assert any(line.startswith("EXPLORATORY RECOMMENDATION —") for line in exploratory)
    assert "Intent-aware recommendation against your declared Discovery Brief." in intent_aware[1]
    assert any(line.startswith("RECOMMENDED —") for line in intent_aware)


def test_intent_aware_dispatch_records_declared_intent_without_promoting_canon(
    tmp_path, monkeypatch, capsys
):
    brief = _brief()
    brief_path = tmp_path / "brief.yaml"
    brief_path.write_text(
        yaml.safe_dump(brief.declared_intent(), sort_keys=False),
        encoding="utf-8",
    )
    data = _data()

    class _JudgeClient:
        def complete(self, request: LLMRequest) -> LLMResponse:
            assert "DECLARED AUTHOR INTENT" in request.user
            return LLMResponse(
                text=(
                    '{"recommended_candidate_id":"candidate_1",'
                    '"recommendation_rationale":"Candidate one best serves the declared puzzle promise.",'
                    '"rejected_candidate_reasons":{"candidate_2":"Candidate two diffuses the puzzle center."}}'
                ),
                input_tokens=1,
                output_tokens=1,
            )

    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: _JudgeClient())
    monkeypatch.setattr(
        "auteur.cli_handlers.handle_identity_recommend",
        lambda **kwargs: HandlerResult.success(data=data),
    )

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, brief=brief_path))
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Intent-aware recommendation against your declared Discovery Brief." in captured.out
    assert "RECOMMENDED — Between Floors one (`candidate_1`)" in captured.out
    assert not (tmp_path / "story_identity.yaml").exists()

    report = yaml.safe_load(
        (tmp_path / "story_discovery" / "discovery_report.yaml").read_text(encoding="utf-8")
    )
    assert report["intent_mode"] == "intent_aware"
    assert report["intent_adequacy"]["adequate"] is True
    assert report["declared_author_intent"]["story_type"]["genre"] == "mystery"
    assert report["premise_summary"] == brief.premise
    assert report["recommended_candidate_id"] == "candidate_1"


def test_story_discovery_accept_preserves_hard_constraints_and_architecture_preferences(tmp_path):
    discovery_dir = tmp_path / "story_discovery"
    discovery_dir.mkdir()
    candidate_path = discovery_dir / "candidate_1.yaml"
    identity = _identity("accepted")
    identity.architecture_preferences = _brief().architecture_preferences
    identity.hard_constraints = list(_brief().hard_constraints)
    identity.to_yaml(candidate_path)
    (discovery_dir / "discovery_report.yaml").write_text(
        yaml.safe_dump({"chosen_candidate": None}),
        encoding="utf-8",
    )
    output = tmp_path / "story_identity.yaml"

    exit_code = main(
        [
            "story-discovery",
            "accept",
            str(candidate_path),
            "--output",
            str(output),
            "--keep-candidates",
        ]
    )

    assert exit_code == 0
    promoted = StoryIdentity.from_yaml(output)
    assert promoted.hard_constraints == _brief().hard_constraints
    assert promoted.architecture_preferences is not None
    assert promoted.architecture_preferences.complexity is ComplexityPreference.MAXIMALIST
    assert promoted.architecture_preferences.causal_distribution is CausalDistributionPreference.MIXED
