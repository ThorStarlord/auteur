from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
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
from auteur.story_discovery_brief import DiscoveryBrief, DiscoveryBriefStoryType
from auteur.story_discovery_intent import dispatch_story_discovery_recommend


@dataclass(frozen=True)
class Engine:
    title: str
    strategy: str
    actions: tuple[str, ...]
    pressure: str
    conflict: str
    climax: str


@dataclass(frozen=True)
class DogfoodCase:
    case_id: str
    premise: str
    genre: Genre
    primary_experience: str
    secondary: tuple[str, ...]
    trajectory: str
    constraints: tuple[str, ...]
    engines: tuple[Engine, ...]
    architecture: NarrativeArchitecturePreferences | None = None


CASES = {
    "D2": DogfoodCase(
        case_id="D2",
        premise="A heist where nothing can be stolen, nobody may lie, and the crew must defeat a corrupt museum director.",
        genre=Genre.OTHER,
        primary_experience="impossible-constraint ingenuity",
        secondary=("fascination", "operational pressure"),
        trajectory="constraint -> plan fascination -> pressure -> public reversal",
        constraints=("nothing is stolen", "nobody on the crew knowingly lies", "the museum remains essential"),
        engines=(
            Engine("Nothing Missing", "prove corruption through provenance evidence", ("retrieve", "authenticate", "connect", "disclose"), "evidentiary burden and controlled records", "The crew must turn authenticated provenance into public proof.", "public proof collapses the director's ownership claims"),
            Engine("Procedural Trap", "weaponize incompatible museum procedures", ("schedule", "trigger", "constrain", "force choice"), "conflicting institutional obligations", "The crew must make the director choose between incompatible rules.", "the director publicly violates one of his own procedures"),
            Engine("The Honest Con", "stage truthful social pressure that provokes self-exposure", ("stage", "frame", "provoke", "expose"), "audience inference and appearance management", "The crew must arrange true statements so the director incriminates himself.", "the director exposes himself through his public reaction"),
        ),
    ),
    "D3": DogfoodCase(
        case_id="D3",
        premise="A family inherits a house that becomes one room smaller every night.",
        genre=Genre.HORROR,
        primary_experience="claustrophobic dread",
        secondary=("curiosity", "grief", "familial tenderness"),
        trajectory="unease -> confinement -> family revelation -> disturbing catharsis",
        constraints=("the shrinking is genuinely supernatural", "inheritance matters", "the family remains central"),
        engines=(
            Engine("The Missing Room", "confront present family avoidance as rooms disappear", ("recognize", "confront", "reckon", "choose"), "lost private space forces avoided relationships into contact", "The family must confront the harm their disappearing rooms externalize.", "a family reckoning determines what space remains"),
            Engine("Measured Walls", "investigate and contain what the shrinking house is sealing", ("map", "test", "penetrate", "contain"), "physical compression closes investigative options", "The family must discover what the house is compressing toward them.", "the family chooses what must be contained or released"),
            Engine("Square Footage", "restore people erased from the inheritance history", ("research", "trace", "name", "restitute"), "each missing room removes another piece of inherited history", "The heirs must trace exclusion before the house erases their own place.", "restitution changes the inheritance before the final room vanishes"),
        ),
        architecture=NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.MAXIMALIST,
            causal_distribution=CausalDistributionPreference.MIXED,
            engine_hierarchy=EngineHierarchyPreference.PRIMARY_WITH_LAYERS,
        ),
    ),
    "D4": DogfoodCase(
        case_id="D4",
        premise="The protagonist never learns that her brother caused the disaster; the reader knows by midpoint, and her external goal still resolves.",
        genre=Genre.OTHER,
        primary_experience="painful dramatic irony",
        secondary=("dread", "hope", "pity"),
        trajectory="suspicion -> reader knowledge -> hope -> bittersweet unresolved catharsis",
        constraints=("the brother caused the disaster", "the protagonist never learns this", "her external goal resolves"),
        engines=(
            Engine("What She Saves", "repair visible consequences under permanently incomplete knowledge", ("repair", "organize", "protect", "choose"), "incomplete knowledge complicates practical recovery", "She must resolve the aftermath without the truth the reader possesses.", "her own recovery decisions resolve the external crisis"),
            Engine("His Quiet Repair", "secretly atone through hidden interventions", ("conceal", "intervene", "compensate", "sacrifice"), "near-discovery and unintended intervention consequences", "Her brother must mitigate what he caused without confessing.", "he sacrifices without confession while she completes her goal"),
            Engine("The Official Cause", "navigate and correct an incomplete institutional explanation", ("diagnose", "negotiate", "mobilize", "correct"), "institutional incentives preserve a useful false model", "She must improve the system without discovering her brother's culpability.", "a better practical model resolves the crisis while intimate truth remains hidden"),
        ),
        architecture=NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.MAXIMALIST,
            causal_distribution=CausalDistributionPreference.MIXED,
            engine_hierarchy=EngineHierarchyPreference.PRIMARY_WITH_LAYERS,
        ),
    ),
    "D5": DogfoodCase(
        case_id="D5",
        premise="History cannot be changed; a time traveler can only change what the trip means to people who remember it.",
        genre=Genre.SCI_FI,
        primary_experience="bittersweet meaningful agency",
        secondary=("wonder", "frustration", "grief", "moral urgency"),
        trajectory="wonder -> frustration -> recognition -> moral urgency -> bittersweet agency",
        constraints=("historical events cannot change", "agency must operate through memory, meaning, testimony, or present action"),
        engines=(
            Engine("Fixed Point", "recover lost testimony and turn witnessing into present obligation", ("revisit", "observe", "question", "carry testimony", "act"), "fixed history and resistance to recovered truth", "The traveler must decide what present action recovered testimony obligates.", "present choices change because fixed history is understood differently"),
            Engine("The Same Goodbye", "change relationship meaning through repeated fixed encounters", ("revisit", "converse", "remember", "disclose"), "attachment and inevitability intensify each encounter", "The traveler must accept that conversation can change meaning but not outcome.", "a present relationship changes because the same loss is remembered differently"),
            Engine("Annotations", "contest public memory with an archive only time travel can supply", ("witness", "curate", "authenticate", "publish", "defend"), "institutions contest credibility and public interpretation", "The traveler must decide who controls the meaning of fixed history.", "the archive changes present collective memory without changing the event"),
        ),
        architecture=NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.MAXIMALIST,
            causal_distribution=CausalDistributionPreference.MIXED,
            engine_hierarchy=EngineHierarchyPreference.PRIMARY_WITH_LAYERS,
        ),
    ),
}


def _brief(case: DogfoodCase) -> DiscoveryBrief:
    start, midpoint, ending = case.trajectory.split(" -> ", 2)
    return DiscoveryBrief(
        premise=case.premise,
        story_type=DiscoveryBriefStoryType(
            genre=case.genre,
            target_audience=TargetAudience.ADULT,
        ),
        target_experience=TargetExperience(
            primary_emotional_promise=case.primary_experience,
            secondary_palette=list(case.secondary),
            emotional_trajectory=EmotionalTrajectory(
                pattern=case.trajectory,
                start=start,
                midpoint=midpoint,
                ending=ending,
            ),
        ),
        architecture_preferences=case.architecture,
        hard_constraints=list(case.constraints),
    )


def _identity(case: DogfoodCase, engine: Engine) -> StoryIdentity:
    return StoryIdentity(
        title=engine.title,
        core_answer=f"{engine.title}: {engine.strategy}.",
        target_experience=TargetExperience(
            primary=case.primary_experience,
            secondary=list(case.secondary),
            progression=case.trajectory,
        ),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.OTHER,
            genre=case.genre,
            target_audience=TargetAudience.ADULT,
        ),
        central_engine=HighLevelCentralEngine(
            want=f"The protagonist must {engine.actions[0]} toward the premise objective.",
            resistance=engine.pressure,
            conflict=engine.conflict,
            stakes="Failure makes the story's central loss or threat irreversible.",
            change=f"The protagonist changes through the consequences of {engine.strategy}.",
        ),
    )


def _data(case: DogfoodCase) -> RecommendOpenEndedData:
    outputs = []
    for index, engine in enumerate(case.engines, 1):
        identity = _identity(case, engine)
        content = yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False)
        candidate_id = f"candidate_{index}"
        outputs.append(
            CandidateOutput(
                candidate_id=candidate_id,
                yaml_content=content,
                identity=identity,
                candidate=StoryIdentityCandidate(
                    candidate_id=candidate_id,
                    path="",
                    label=engine.title,
                    best_basis=BestBasis.GENRE_ALIGNED,
                    lens="controlled_dogfood",
                    lens_rationale="Phase F controlled dogfood fixture.",
                    recommendation_summary="excluded self-evaluation",
                    validation_status="valid",
                    warning_count=0,
                    contract_fit=80,
                    contract_fit_status="strong",
                    content_hash="sha256:" + hashlib.sha256(content.encode()).hexdigest(),
                ),
            )
        )
    return RecommendOpenEndedData(
        candidates=outputs,
        rec_set=StoryIdentityRecommendationSet(
            mode=RecommendationMode.OPEN_ENDED,
            source_input_path="",
            generated_at="2026-08-19T21:00:00+00:00",
            requested_candidates=len(outputs),
            valid_candidates=len(outputs),
            search_strategy="Narrative Search",
            design_lenses=["controlled_dogfood"],
            recommended_candidate_id=None,
            candidates=[item.candidate for item in outputs],
        ),
        comparison_lines=["# Story Discovery Comparison", ""],
    )


class DogfoodClient:
    def __init__(self, case: DogfoodCase):
        self.case = case
        self.requests: list[LLMRequest] = []

    def _engine_for_conflict(self, conflict: str) -> Engine:
        return next(engine for engine in self.case.engines if engine.conflict == conflict)

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if "bounded narrative-causality profiler" in request.system:
            evidence = json.loads(request.user.split("BOUNDED STORY EVIDENCE\n", 1)[1])
            engine = self._engine_for_conflict(
                evidence["candidate_commitments"]["central_engine"]["conflict"]
            )
            return LLMResponse(
                text=json.dumps(
                    {
                        "primary_strategy": engine.strategy,
                        "causal_owner": "protagonist-led primary engine",
                        "external_action_pattern": list(engine.actions),
                        "pressure_system": engine.pressure,
                        "reversal_mechanics": [f"a consequence of {engine.strategy} forces a new plan"],
                        "climax_mechanic": engine.climax,
                        "scene_families": [f"{verb} scene" for verb in engine.actions[:3]],
                        "evidence_gaps": [],
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )
        if "causal-diversity assessor" in request.system:
            pairs = json.loads(request.user.split("CAUSAL PROFILE PAIRS\n", 1)[1])
            return LLMResponse(
                text=json.dumps(
                    {
                        "assessments": [
                            {
                                "left_evidence_key": pair["left_evidence_key"],
                                "right_evidence_key": pair["right_evidence_key"],
                                "classification": "distinct",
                                "shared_causal_mechanics": ["same premise and declared reader promise"],
                                "material_differences": ["different actions, pressure, and climax mechanics"],
                                "scene_consequence": "The alternatives require materially different major scenes.",
                                "rationale": "Controlled Phase F dogfood classification.",
                            }
                            for pair in pairs
                        ]
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )
        if "comparative narrative architect" in request.system:
            evidence = json.loads(request.user.split("SURVIVING CANDIDATE EVIDENCE\n", 1)[1])
            winner = evidence[0]["candidate_id"]
            return LLMResponse(
                text=json.dumps(
                    {
                        "recommended_candidate_id": winner,
                        "recommendation_rationale": "The first controlled engine best preserves the declared primary story promise while retaining clear protagonist agency.",
                        "rejected_candidate_reasons": {
                            item["candidate_id"]: "This direction shifts causal ownership or scene pressure away from the selected primary engine."
                            for item in evidence[1:]
                        },
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )
        if "creative-writing architecture explainer" in request.system:
            evidence = json.loads(request.user.split("BOUNDED CRAFT EVIDENCE\n", 1)[1])
            alternative = evidence["alternative"]["causal_profile"]
            actions = alternative["external_action_pattern"]
            declared = evidence.get("declared_author_intent") or {}
            preferences = declared.get("architecture_preferences") or {}
            composability = (
                "compatible_as_secondary"
                if preferences.get("engine_hierarchy") == "primary_with_layers"
                else "requires_reframing"
            )
            return LLMResponse(
                text=json.dumps(
                    {
                        "craft_layers_changed": ["causal_strategy", "external_action", "pressure_system", "scene_families", "reader_experience", "theme"],
                        "causal_ownership_shift": "The alternative moves more causal weight toward its own defining mechanism.",
                        "external_action_shift": {
                            "add_or_emphasize": actions,
                            "de_emphasize": evidence["primary"]["causal_profile"]["external_action_pattern"][:2],
                        },
                        "scene_family_shift": alternative["scene_families"],
                        "pressure_texture_shift": f"More scenes are organized around {alternative['pressure_system']}.",
                        "reader_experience_shift": {
                            "primary_promise_effect": "preserved_but_reweighted",
                            "secondary_palette_effect": [],
                            "trajectory_effect": "The route to the same governing promise changes with the new scene pressure.",
                        },
                        "thematic_effect": "The alternative makes its causal mechanism carry more of the story's meaning.",
                        "gain": "A distinct source of causal pressure and scene variety.",
                        "give_up": "Some narrative weight moves away from the selected primary engine.",
                        "composability": composability,
                        "composition_note": "Use as a subordinate mechanism only if the primary engine still owns decisive turns." if composability == "compatible_as_secondary" else None,
                        "primary_risk": "If the alternative solves decisive turns, it displaces the selected primary engine.",
                        "evidence_gaps": [],
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )
        raise AssertionError(f"Unexpected dogfood request: {request.system[:80]}")


def _run_case(case: DogfoodCase, tmp_path: Path, monkeypatch):
    brief = _brief(case)
    brief_path = tmp_path / f"{case.case_id}.yaml"
    brief_path.write_text(yaml.safe_dump(brief.declared_intent(), sort_keys=False), encoding="utf-8")
    data = _data(case)
    client = DogfoodClient(case)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: client)
    monkeypatch.setattr(
        "auteur.cli_handlers.handle_identity_recommend",
        lambda **kwargs: HandlerResult.success(data=data),
    )
    args = SimpleNamespace(
        candidates=len(case.engines),
        brain_dump="__auteur_structured_discovery_brief__",
        brief=brief_path,
        provider="anthropic",
        model=None,
        genre=None,
        medium=None,
        mode=None,
        lens=None,
        strict_candidate_count=False,
        debug=False,
        project=None,
        output=tmp_path / case.case_id,
    )
    assert dispatch_story_discovery_recommend(args) == 0
    return brief, client, args.output


def test_d1_under_specified_intent_fails_before_provider(tmp_path, monkeypatch, capsys):
    path = tmp_path / "D1.yaml"
    path.write_text(
        "premise: A retired astronaut hears mission-control chatter in her empty apartment.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("provider should not be used")),
    )
    args = SimpleNamespace(
        candidates=3,
        brain_dump="__auteur_structured_discovery_brief__",
        brief=path,
        provider="anthropic",
        model=None,
        genre=None,
        medium=None,
        mode=None,
        lens=None,
        strict_candidate_count=False,
        debug=False,
        project=None,
        output=tmp_path / "D1",
    )
    assert dispatch_story_discovery_recommend(args) == 1
    assert "Insufficient author intent" in capsys.readouterr().err


def test_d2_causal_false_choice_is_replaced_by_materially_distinct_scene_engines(tmp_path, monkeypatch):
    _, _, output = _run_case(CASES["D2"], tmp_path, monkeypatch)
    report = yaml.safe_load((output / "discovery_report.yaml").read_text(encoding="utf-8"))
    analysis = report["causal_analysis"]
    assert analysis["status"] == "qualified"
    action_patterns = {
        tuple(profile["external_action_pattern"])
        for profile in analysis["profiles"].values()
    }
    climaxes = {profile["climax_mechanic"] for profile in analysis["profiles"].values()}
    assert len(action_patterns) == 3
    assert len(climaxes) == 3
    assert all(item["classification"] == "distinct" for item in analysis["pairwise_assessments"])


def test_d3_maximalist_mixed_causation_remains_architecture_intent_with_primary_hierarchy(tmp_path, monkeypatch):
    brief, client, output = _run_case(CASES["D3"], tmp_path, monkeypatch)
    assert brief.architecture_preferences is not None
    assert brief.architecture_preferences.complexity is ComplexityPreference.MAXIMALIST
    assert brief.architecture_preferences.causal_distribution is CausalDistributionPreference.MIXED
    assert brief.architecture_preferences.engine_hierarchy is EngineHierarchyPreference.PRIMARY_WITH_LAYERS
    craft_requests = [request for request in client.requests if "creative-writing architecture explainer" in request.system]
    assert craft_requests
    assert all('"architecture_preferences"' in request.user for request in craft_requests)
    report = yaml.safe_load((output / "discovery_report.yaml").read_text(encoding="utf-8"))
    impacts = report["craft_analysis"]["impacts"]
    assert impacts
    assert all(item["composability"] == "compatible_as_secondary" for item in impacts.values())
    assert report["recommended_candidate_id"] == "candidate_1"


def test_d4_tradeoff_surface_teaches_actual_craft_layers(tmp_path, monkeypatch):
    _, _, output = _run_case(CASES["D4"], tmp_path, monkeypatch)
    comparison = (output / "comparison.md").read_text(encoding="utf-8")
    for heading in (
        "WHAT CHANGES",
        "CAUSAL EFFECT",
        "WHAT YOU WILL WRITE MORE OF",
        "PRESSURE / STORY TEXTURE",
        "READER-EXPERIENCE SHIFT",
        "WHAT YOU GAIN",
        "WHAT YOU GIVE UP / REWEIGHT",
        "COMPOSABILITY",
        "PRIMARY RISK",
    ):
        assert heading in comparison
    assert "narrative-weight movement" in comparison
    assert not (tmp_path / "story_identity.yaml").exists()


def test_d5_emotional_hierarchy_is_visible_without_becoming_architecture_preference(tmp_path, monkeypatch, capsys):
    case = CASES["D5"]
    _, _, output = _run_case(case, tmp_path, monkeypatch)
    stdout = capsys.readouterr().out
    assert f"Governing reader promise: {case.primary_experience}" in stdout
    assert "Supporting emotional palette: wonder, frustration, grief, moral urgency" in stdout
    assert f"Emotional trajectory: {case.trajectory}" in stdout
    report = yaml.safe_load((output / "discovery_report.yaml").read_text(encoding="utf-8"))
    declared = report["declared_author_intent"]
    assert declared["target_experience"]["primary_emotional_promise"] == case.primary_experience
    assert declared["architecture_preferences"]["complexity"] == "maximalist"
    assert "maximalist" not in declared["target_experience"]["secondary_palette"]
