from __future__ import annotations

import json
from pathlib import Path

import yaml

from auteur.blueprint import Genre, StoryMedium, StoryMode, TargetAudience, TargetExperience
from auteur.cli import main
from auteur.identity import HighLevelCentralEngine, StoryIdentity, StoryType
from auteur.llm import LLMRequest, LLMResponse
from auteur.narrative_ontology.architecture_preferences import (
    CausalDistributionPreference,
    ComplexityPreference,
    EngineHierarchyPreference,
    NarrativeArchitecturePreferences,
)
from auteur.story_discovery_brief import DiscoveryBrief
from auteur.story_discovery_causality import (
    CausalAnalysis,
    CausalProfileRecord,
    PairwiseAssessmentRecord,
)
from auteur.story_discovery_compose import CompositionReport, HierarchyAssessment
from auteur.story_discovery_craft import (
    CraftAnalysis,
    CraftImpactRecord,
    ExternalActionShift,
    ReaderExperienceShift,
)
from auteur.story_discovery_state import StoryDiscoveryStateKind, classify_story_discovery_project
from auteur.workflow.engine import WorkflowEngine
from auteur.workflow.models import AuthorityLevel, WorkflowStage


def _answers(monkeypatch, values: list[str]) -> None:
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))


def _capture_minimum_brief(root: Path, monkeypatch) -> DiscoveryBrief:
    _answers(
        monkeypatch,
        [
            "A woman rebuilds a city after a disaster without learning her brother caused it.",
            "science fiction",
            "adult",
            "painful dramatic irony with fragile hope",
        ],
    )
    assert main(["story-discovery", "start", "--project", str(root)]) == 0
    assert not (root / "story_identity.yaml").exists()
    return DiscoveryBrief.from_yaml(root / "story_discovery" / "brief.yaml")


def _refine_brief(root: Path, monkeypatch) -> DiscoveryBrief:
    _answers(
        monkeypatch,
        [
            "tenderness, hope",
            "nihilism",
            "yes",
            "rising pressure",
            "unease",
            "dread",
            "bittersweet agency",
            "richly interconnected",
            "several interacting causes",
            "one main engine with substantial supporting layers",
            "not sure",
            "not sure",
            "the protagonist never learns the brother caused the disaster",
            "",
        ],
    )
    assert main(["story-discovery", "start", "--project", str(root), "--refine"]) == 0
    return DiscoveryBrief.from_yaml(root / "story_discovery" / "brief.yaml")


def _identity(title: str, conflict: str) -> StoryIdentity:
    return StoryIdentity(
        title=title,
        core_answer=f"{title}: controlled Phase G dogfood candidate.",
        target_experience=TargetExperience(
            primary="painful dramatic irony with fragile hope",
            secondary=["tenderness", "hope"],
            progression="unease -> dread -> bittersweet agency",
        ),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.OTHER,
            genre=Genre.SCI_FI,
            target_audience=TargetAudience.ADULT,
        ),
        central_engine=HighLevelCentralEngine(
            want="Rebuild the city and protect the surviving community.",
            resistance="Incomplete knowledge and hidden interventions complicate recovery.",
            conflict=conflict,
            stakes="Failure exposes the city to another collapse.",
            change="She earns practical agency without learning the forbidden truth.",
        ),
        architecture_preferences=NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.MAXIMALIST,
            causal_distribution=CausalDistributionPreference.MIXED,
            engine_hierarchy=EngineHierarchyPreference.PRIMARY_WITH_LAYERS,
        ),
        hard_constraints=["the protagonist never learns the brother caused the disaster"],
    )


def _profile(key: str, strategy: str, *, owner: str = "protagonist-led") -> CausalProfileRecord:
    return CausalProfileRecord(
        evidence_key=key,
        primary_strategy=strategy,
        causal_owner=owner,
        external_action_pattern=["repair", "organize", "protect", "choose"],
        pressure_system=f"pressure from {strategy}",
        reversal_mechanics=[f"a consequence of {strategy} changes the plan"],
        climax_mechanic="the protagonist's own decision resolves the public crisis",
        scene_families=["recovery operation", "hidden consequence", "public decision"],
        evidence_gaps=[],
    )


def _impact(composability: str = "compatible_as_secondary") -> CraftImpactRecord:
    return CraftImpactRecord(
        primary_candidate_id="candidate_1",
        compared_candidate_id="candidate_2",
        primary_evidence_key="aaaaaaaa111111111111",
        compared_evidence_key="bbbbbbbb222222222222",
        craft_layers_changed=["causal_ownership", "external_action", "scene_families"],
        causal_ownership_shift="The brother gains subordinate causal weight.",
        external_action_shift=ExternalActionShift(
            add_or_emphasize=["conceal", "intervene", "sacrifice"],
            de_emphasize=["direct explanation"],
        ),
        scene_family_shift=["hidden intervention", "near-discovery"],
        pressure_texture_shift="Dramatic irony becomes more intimate.",
        reader_experience_shift=ReaderExperienceShift(
            primary_promise_effect="preserved_but_reweighted",
            secondary_palette_effect=["more tenderness"],
            trajectory_effect="Dread deepens before bittersweet agency returns.",
        ),
        thematic_effect="Atonement without confession gains weight.",
        gain="More intimate hidden pressure.",
        give_up="Some causal simplicity.",
        composability=composability,
        composition_note=(
            "Keep the hidden repair layer subordinate to her public recovery engine."
            if composability == "compatible_as_secondary"
            else None
        ),
        primary_risk="Too many successful interventions could displace the primary engine.",
        evidence_gaps=[],
    )


def _persist_run(root: Path, brief: DiscoveryBrief, *, causal_status: str = "qualified") -> StoryIdentity:
    discovery = root / "story_discovery"
    primary = _identity(
        "What She Saves",
        "She must rebuild from incomplete evidence while owning the decisive recovery choices.",
    )
    secondary = _identity(
        "His Quiet Repair",
        "Her brother's hidden interventions alter obstacles without resolving them for her.",
    )
    primary.to_yaml(discovery / "candidate_1.yaml")
    secondary.to_yaml(discovery / "candidate_2.yaml")

    pairwise = PairwiseAssessmentRecord(
        left_evidence_key="aaaaaaaa111111111111",
        right_evidence_key="bbbbbbbb222222222222",
        left_candidate_id="candidate_1",
        right_candidate_id="candidate_2",
        classification="near_duplicate" if causal_status == "not_adjudicable_near_duplicate" else "distinct",
        shared_causal_mechanics=["same disaster aftermath"],
        material_differences=(
            []
            if causal_status == "not_adjudicable_near_duplicate"
            else ["different causal ownership and recurring action patterns"]
        ),
        scene_consequence=(
            "The major scene families remain too similar to justify a winner."
            if causal_status == "not_adjudicable_near_duplicate"
            else "The alternatives produce materially different recurring scenes."
        ),
        rationale="Controlled Phase G dogfood evidence.",
    )
    causal = CausalAnalysis(
        status=causal_status,
        profiles={
            "candidate_1": _profile("aaaaaaaa111111111111", "visible recovery"),
            "candidate_2": _profile(
                "bbbbbbbb222222222222",
                "secret atonement",
                owner="secondary hidden pressure",
            ),
        },
        pairwise_assessments=[pairwise],
    )
    payload = {
        "recommended_candidate_id": "candidate_1",
        "recommendation_rationale": "The visible recovery engine best preserves the declared reader promise.",
        "intent_mode": "intent_aware",
        "declared_author_intent": brief.declared_intent(),
        "causal_analysis": causal.model_dump(mode="json"),
    }
    if causal_status == "qualified":
        craft = CraftAnalysis(
            status="complete",
            primary_candidate_id="candidate_1",
            impacts={"candidate_2": _impact()},
        )
        payload["craft_analysis"] = craft.model_dump(mode="json")

    for name in ("discovery_set.yaml", "discovery_report.yaml"):
        (discovery / name).write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    return primary


def _composed_from(primary: StoryIdentity) -> StoryIdentity:
    composed = primary.model_copy(deep=True)
    composed.title = "What She Saves - Layered"
    composed.core_answer = (
        "She still governs the public recovery while her brother's hidden repairs add subordinate "
        "dramatic irony without revealing the forbidden truth."
    )
    composed.central_engine = HighLevelCentralEngine(
        want=primary.central_engine.want,
        resistance="Incomplete knowledge and hidden repairs complicate recovery without solving it for her.",
        conflict="She must keep rebuilding while unseen interventions change obstacles she still owns.",
        stakes=primary.central_engine.stakes,
        change=primary.central_engine.change,
    )
    return composed


class _ComposeClient:
    def __init__(self, composed: StoryIdentity):
        self.composed = composed
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if "bounded narrative composition architect" in request.system:
            text = json.dumps(self.composed.model_dump(mode="json"))
        elif "bounded narrative-causality profiler" in request.system:
            text = json.dumps(
                {
                    "primary_strategy": "visible recovery complicated by hidden repairs",
                    "causal_owner": "protagonist-led with subordinate hidden pressure",
                    "external_action_pattern": ["repair", "organize", "protect", "adapt"],
                    "pressure_system": "incomplete knowledge plus hidden interventions",
                    "reversal_mechanics": ["a hidden repair changes the recovery plan"],
                    "climax_mechanic": "her own public decision resolves the crisis",
                    "scene_families": ["recovery operation", "hidden repair consequence", "public choice"],
                    "evidence_gaps": [],
                }
            )
        elif "bounded narrative hierarchy assessor" in request.system:
            text = json.dumps(
                {
                    "classification": "primary_preserved",
                    "rationale": "Her recovery strategy and climax remain decisive.",
                    "primary_mechanics_preserved": ["protagonist-led recovery", "protagonist-owned climax"],
                    "borrowed_mechanics_subordinate": ["brother hidden repair"],
                    "risks": ["too many successful repairs could displace her causal ownership"],
                }
            )
        else:
            raise AssertionError(f"unexpected provider request: {request.system[:80]}")
        return LLMResponse(text=text, input_tokens=1, output_tokens=1)


def _persist_current_composition(root: Path, primary: StoryIdentity) -> None:
    discovery = root / "story_discovery"
    composed = _composed_from(primary)
    composed.to_yaml(discovery / "composed_candidate.yaml")
    report = CompositionReport(
        primary_candidate_id="candidate_1",
        borrowed=[
            {
                "candidate_id": "candidate_2",
                "mechanism": "secret atonement through hidden repairs",
            }
        ],
        primary_evidence_key="aaaaaaaa111111111111",
        borrowed_evidence_keys={"candidate_2": "bbbbbbbb222222222222"},
        hierarchy_assessment=HierarchyAssessment(
            classification="primary_preserved",
            rationale="Her recovery strategy and climax remain decisive.",
            primary_mechanics_preserved=["protagonist-led recovery"],
            borrowed_mechanics_subordinate=["hidden repair"],
            risks=[],
        ),
        composed_causal_profile=_profile(
            "cccccccc333333333333",
            "visible recovery complicated by hidden repairs",
        ),
        output_candidate="story_discovery/composed_candidate.yaml",
    )
    (discovery / "composition_report.yaml").write_text(
        yaml.safe_dump(report.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )


def test_phase_g_scenario_a_guided_review_compose_accept_advances_to_structure(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    root = tmp_path / "scenario-a"
    root.mkdir()

    brief = _capture_minimum_brief(root, monkeypatch)
    brief = _refine_brief(root, monkeypatch)
    assert brief.story_type is not None and brief.story_type.genre == Genre.SCI_FI
    assert brief.architecture_preferences is not None
    assert brief.architecture_preferences.complexity == ComplexityPreference.MAXIMALIST
    assert brief.architecture_preferences.causal_distribution == CausalDistributionPreference.MIXED
    assert brief.architecture_preferences.engine_hierarchy == EngineHierarchyPreference.PRIMARY_WITH_LAYERS
    assert not (root / "story_identity.yaml").exists()

    discovery_action = WorkflowEngine(root).analyze().actions[0]
    assert discovery_action.label == "Discover story directions against your intent"
    assert discovery_action.authority == AuthorityLevel.CANDIDATE_GENERATION

    primary = _persist_run(root, brief)
    review_action = WorkflowEngine(root).analyze().actions[0]
    assert review_action.label == "Review recommended story direction"
    assert review_action.authority == AuthorityLevel.READ_ONLY
    assert main(["story-discovery", "review", "--project", str(root)]) == 0
    review_text = capsys.readouterr().out
    assert "Recommended story direction" in review_text
    assert "What this story actually has the characters doing" in review_text
    assert "Nothing canonical has changed." in review_text
    assert not (root / "story_identity.yaml").exists()

    client = _ComposeClient(_composed_from(primary))
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *args, **kwargs: client)
    _answers(monkeypatch, ["yes", "1", "secret atonement through hidden repairs"])
    assert main(["story-discovery", "compose", "--project", str(root)]) == 0
    assert (root / "story_discovery" / "composed_candidate.yaml").exists()
    assert (root / "story_discovery" / "composition_report.yaml").exists()
    assert not (root / "story_identity.yaml").exists()

    state = classify_story_discovery_project(root)
    assert state.kind == StoryDiscoveryStateKind.COMPOSED_CANDIDATE_AVAILABLE
    assert main(["story-discovery", "review", "--project", str(root)]) == 0
    composed_review = capsys.readouterr().out
    assert "Composed story direction" in composed_review
    assert "secret atonement through hidden repairs" in composed_review
    assert "Accept the composed candidate explicitly" in composed_review
    assert not (root / "story_identity.yaml").exists()

    composed_path = root / "story_discovery" / "composed_candidate.yaml"
    identity_path = root / "story_identity.yaml"
    assert main(
        [
            "story-discovery",
            "accept",
            str(composed_path),
            "--output",
            str(identity_path),
            "--keep-candidates",
        ]
    ) == 0
    assert identity_path.exists()
    accepted = StoryIdentity.from_yaml(identity_path)
    assert accepted.title == "What She Saves - Layered"
    assert WorkflowEngine(root).analyze().current_stage == WorkflowStage.STRUCTURE


def test_phase_g_scenario_b_non_adjudicable_review_has_no_fake_accept_or_compose(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    root = tmp_path / "scenario-b"
    root.mkdir()
    brief = _capture_minimum_brief(root, monkeypatch)
    _persist_run(root, brief, causal_status="not_adjudicable_near_duplicate")

    state = classify_story_discovery_project(root)
    assert state.kind == StoryDiscoveryStateKind.NON_ADJUDICABLE
    action = WorkflowEngine(root).analyze().actions[0]
    assert action.label == "Review why Auteur cannot recommend a direction yet"
    assert action.authority == AuthorityLevel.READ_ONLY

    assert main(["story-discovery", "review", "--project", str(root)]) == 0
    rendered = capsys.readouterr().out
    assert "Auteur does not have a defensible recommendation yet." in rendered
    assert "story-discovery accept" not in rendered

    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider must not be constructed")),
    )
    assert main(["story-discovery", "compose", "--project", str(root)]) == 1
    assert not (root / "story_identity.yaml").exists()
    assert not (root / "story_discovery" / "composed_candidate.yaml").exists()


def test_phase_g_scenario_c_writer_edit_stales_recommendation_and_composition(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    root = tmp_path / "scenario-c"
    root.mkdir()
    brief = _capture_minimum_brief(root, monkeypatch)
    primary = _persist_run(root, brief)
    _persist_current_composition(root, primary)
    assert classify_story_discovery_project(root).kind == StoryDiscoveryStateKind.COMPOSED_CANDIDATE_AVAILABLE

    _answers(monkeypatch, ["4", "reconstructive relief", "done"])
    assert main(["story-discovery", "start", "--project", str(root), "--edit"]) == 0

    edited = DiscoveryBrief.from_yaml(root / "story_discovery" / "brief.yaml")
    assert edited.declared_intent() != brief.declared_intent()
    state = classify_story_discovery_project(root)
    assert state.kind == StoryDiscoveryStateKind.READY_TO_DISCOVER
    assert state.has_recommendation is False
    assert state.has_composed_candidate is False

    action = WorkflowEngine(root).analyze().actions[0]
    assert action.label == "Discover story directions against your intent"
    assert action.authority == AuthorityLevel.CANDIDATE_GENERATION

    assert main(["story-discovery", "review", "--project", str(root)]) == 1
    error_text = capsys.readouterr().err
    assert "needs a fresh Story Discovery run" in error_text

    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider must not be constructed")),
    )
    assert main(["story-discovery", "compose", "--project", str(root)]) == 1
    assert not (root / "story_identity.yaml").exists()
