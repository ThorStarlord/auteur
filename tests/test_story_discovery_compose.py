from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from auteur.blueprint import Genre, StoryMedium, StoryMode, TargetAudience, TargetExperience
from auteur.cli import main, parse_args
from auteur.identity import HighLevelCentralEngine, StoryIdentity, StoryType
from auteur.llm import LLMRequest, LLMResponse
from auteur.narrative_ontology.architecture_preferences import (
    CausalDistributionPreference,
    ComplexityPreference,
    EngineHierarchyPreference,
    NarrativeArchitecturePreferences,
)
from auteur.story_discovery_causality import (
    CausalAnalysis,
    CausalProfileRecord,
    PairwiseAssessmentRecord,
)
from auteur.story_discovery_compose import (
    _validate_preserved_commitments,
    build_composition_request,
    dispatch_story_discovery_compose,
    parse_borrow_spec,
)
from auteur.story_discovery_craft import (
    CraftAnalysis,
    CraftImpactRecord,
    ExternalActionShift,
    ReaderExperienceShift,
)


def _identity(title: str, conflict: str, *, advocacy: str = "SELF ADVOCACY") -> StoryIdentity:
    return StoryIdentity(
        title=title,
        core_answer=f"{title}: controlled Story Discovery composition fixture.",
        target_experience=TargetExperience(
            primary="painful dramatic irony",
            secondary=["dread", "hope"],
            progression="suspicion -> dread -> bittersweet agency",
        ),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.OTHER,
            genre=Genre.OTHER,
            target_audience=TargetAudience.ADULT,
        ),
        central_engine=HighLevelCentralEngine(
            want="Resolve the external disaster aftermath.",
            resistance="Incomplete knowledge and hidden interventions obstruct recovery.",
            conflict=conflict,
            stakes="Failure leaves the community exposed to a second catastrophe.",
            change="The protagonist earns practical closure without learning the forbidden truth.",
        ),
        architecture_preferences=NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.MAXIMALIST,
            causal_distribution=CausalDistributionPreference.MIXED,
            engine_hierarchy=EngineHierarchyPreference.PRIMARY_WITH_LAYERS,
        ),
        hard_constraints=[
            "the brother caused the disaster",
            "the protagonist never learns this",
        ],
        why_this_is_best=advocacy,
        alternatives=[advocacy],
        rejected_directions=[advocacy],
        confidence=0.99,
    )


def _profile(key: str, strategy: str, actions: list[str], climax: str) -> CausalProfileRecord:
    return CausalProfileRecord(
        evidence_key=key,
        primary_strategy=strategy,
        causal_owner="protagonist-led" if "repair" in strategy else "secondary hidden pressure",
        external_action_pattern=actions,
        pressure_system=f"pressure from {strategy}",
        reversal_mechanics=[f"a consequence of {strategy} changes the plan"],
        climax_mechanic=climax,
        scene_families=[f"{action} scene" for action in actions[:3]],
        evidence_gaps=[],
    )


def _impact(candidate_id: str, composability: str = "compatible_as_secondary") -> CraftImpactRecord:
    return CraftImpactRecord(
        primary_candidate_id="candidate_1",
        compared_candidate_id=candidate_id,
        primary_evidence_key="aaaaaaaa111111111111",
        compared_evidence_key=(
            "bbbbbbbb222222222222" if candidate_id == "candidate_2" else "cccccccc333333333333"
        ),
        craft_layers_changed=["causal_ownership", "external_action", "scene_families"],
        causal_ownership_shift="More causal weight moves toward the borrowed mechanism.",
        external_action_shift=ExternalActionShift(
            add_or_emphasize=["conceal", "intervene", "sacrifice"],
            de_emphasize=["direct repair"],
        ),
        scene_family_shift=["hidden intervention", "near-discovery"],
        pressure_texture_shift="More dramatic-ironic hidden action.",
        reader_experience_shift=ReaderExperienceShift(
            primary_promise_effect="preserved_but_reweighted",
            secondary_palette_effect=["more pity"],
            trajectory_effect="Dread increases while the primary promise remains legible.",
        ),
        thematic_effect="Atonement without confession gains weight.",
        gain="More hidden causal pressure.",
        give_up="Some causal weight leaves the protagonist.",
        composability=composability,
        composition_note=(
            "Keep the primary engine decisive."
            if composability == "compatible_as_secondary"
            else None
        ),
        primary_risk="Borrowed action can displace the primary engine.",
        evidence_gaps=[],
    )


def _write_run(tmp_path: Path, *, composability: str = "compatible_as_secondary", causal_status: str = "qualified"):
    discovery = tmp_path / "story_discovery"
    discovery.mkdir()
    primary = _identity(
        "What She Saves",
        "She must rebuild while acting on an incomplete but workable explanation.",
    )
    secondary = _identity(
        "His Quiet Repair",
        "Her brother's hidden interventions solve one problem while creating another.",
    )
    tertiary = _identity(
        "The Official Cause",
        "She must improve an incomplete institutional explanation without learning the intimate truth.",
    )
    primary.to_yaml(discovery / "candidate_1.yaml")
    secondary.to_yaml(discovery / "candidate_2.yaml")
    tertiary.to_yaml(discovery / "candidate_3.yaml")

    profiles = {
        "candidate_1": _profile(
            "aaaaaaaa111111111111",
            "repair visible consequences under incomplete knowledge",
            ["repair", "organize", "protect", "choose"],
            "the protagonist's own decisions resolve the external crisis",
        ),
        "candidate_2": _profile(
            "bbbbbbbb222222222222",
            "secret atonement through hidden intervention",
            ["conceal", "intervene", "compensate", "sacrifice"],
            "the brother sacrifices without confessing while her own arc still resolves",
        ),
        "candidate_3": _profile(
            "cccccccc333333333333",
            "navigate and correct an incomplete institutional model",
            ["diagnose", "negotiate", "mobilize", "correct"],
            "a better practical model resolves the public crisis without revealing the brother",
        ),
    }
    assessments = [
        PairwiseAssessmentRecord(
            left_evidence_key="aaaaaaaa111111111111",
            right_evidence_key="bbbbbbbb222222222222",
            left_candidate_id="candidate_1",
            right_candidate_id="candidate_2",
            classification="distinct",
            shared_causal_mechanics=["same disaster aftermath"],
            material_differences=["different causal ownership and actions"],
            scene_consequence="Different major scene families.",
            rationale="Controlled fixture.",
        )
    ]
    causal = CausalAnalysis(
        status=causal_status,
        profiles=profiles,
        pairwise_assessments=assessments,
    )
    craft = CraftAnalysis(
        status="complete",
        primary_candidate_id="candidate_1",
        impacts={
            "candidate_2": _impact("candidate_2", composability),
            "candidate_3": _impact("candidate_3", "compatible_as_secondary"),
        },
    )
    report = {
        "recommended_candidate_id": "candidate_1",
        "declared_author_intent": {
            "premise": "The protagonist never learns that her brother caused the disaster.",
            "target_experience": {
                "primary_emotional_promise": "painful dramatic irony",
            },
            "architecture_preferences": {
                "complexity": "maximalist",
                "causal_distribution": "mixed",
                "engine_hierarchy": "primary_with_layers",
            },
            "hard_constraints": list(primary.hard_constraints),
        },
        "causal_analysis": causal.model_dump(mode="json"),
        "craft_analysis": craft.model_dump(mode="json"),
    }
    (discovery / "discovery_report.yaml").write_text(
        yaml.safe_dump(report, sort_keys=False),
        encoding="utf-8",
    )
    (discovery / "discovery_set.yaml").write_text(
        yaml.safe_dump({"recommended_candidate_id": "candidate_1"}),
        encoding="utf-8",
    )
    return discovery, primary, secondary, causal, craft


def _args(discovery: Path, *, borrow=None, output=None):
    return type(
        "Args",
        (),
        {
            "discovery_dir": discovery,
            "primary": "candidate_1",
            "borrow": borrow or ["candidate_2:secret atonement interventions"],
            "output": output,
            "provider": "anthropic",
            "model": None,
        },
    )()


class ComposeClient:
    def __init__(self, composed: StoryIdentity, hierarchy="primary_preserved"):
        self.composed = composed
        self.hierarchy = hierarchy
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if "bounded narrative composition architect" in request.system:
            return LLMResponse(
                text=json.dumps(self.composed.model_dump(mode="json")),
                input_tokens=1,
                output_tokens=1,
            )
        if "bounded narrative-causality profiler" in request.system:
            return LLMResponse(
                text=json.dumps(
                    {
                        "primary_strategy": "repair visible consequences while hidden interventions complicate the route",
                        "causal_owner": "protagonist-led with subordinate brother intervention",
                        "external_action_pattern": ["repair", "organize", "protect", "adapt"],
                        "pressure_system": "incomplete knowledge plus hidden interventions",
                        "reversal_mechanics": ["a hidden intervention changes the protagonist's recovery plan"],
                        "climax_mechanic": "the protagonist's own repair decision resolves the external crisis",
                        "scene_families": ["recovery operation", "hidden intervention consequence", "protagonist decision"],
                        "evidence_gaps": [],
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )
        if "bounded narrative hierarchy assessor" in request.system:
            return LLMResponse(
                text=json.dumps(
                    {
                        "classification": self.hierarchy,
                        "rationale": "The protagonist's recovery strategy and climax remain decisive.",
                        "primary_mechanics_preserved": ["protagonist-led repair", "protagonist-owned climax"],
                        "borrowed_mechanics_subordinate": ["brother hidden intervention"],
                        "risks": ["too many successful interventions could displace the protagonist"],
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )
        raise AssertionError(f"unexpected request: {request.system[:80]}")


def _composed_from(primary: StoryIdentity) -> StoryIdentity:
    composed = primary.model_copy(deep=True)
    composed.title = "What She Saves — Layered"
    composed.core_answer = (
        "The protagonist still owns the recovery engine while her brother's hidden interventions "
        "add subordinate dramatic pressure without revealing the forbidden truth."
    )
    composed.central_engine = HighLevelCentralEngine(
        want=primary.central_engine.want,
        resistance=(
            "Incomplete knowledge and the brother's hidden interventions complicate recovery "
            "without taking ownership of its decisive turns."
        ),
        conflict=(
            "She must rebuild from incomplete evidence while unseen interventions alter obstacles "
            "she still has to solve herself."
        ),
        stakes=primary.central_engine.stakes,
        change=primary.central_engine.change,
    )
    return composed


def test_compose_cli_parses_repeated_borrows_without_touching_base_parser():
    args = parse_args(
        [
            "story-discovery",
            "compose",
            "story_discovery",
            "--primary",
            "candidate_1",
            "--borrow",
            "candidate_2:secret intervention",
            "--borrow",
            "candidate_3:institutional false model",
        ]
    )
    assert args.command == "story-discovery"
    assert args.story_discovery_command == "compose"
    assert args.discovery_dir == Path("story_discovery")
    assert args.primary == "candidate_1"
    assert args.borrow == [
        "candidate_2:secret intervention",
        "candidate_3:institutional false model",
    ]


def test_borrow_spec_splits_only_first_colon():
    borrow = parse_borrow_spec("candidate_2:secret intervention: moral cost")
    assert borrow.candidate_id == "candidate_2"
    assert borrow.mechanism == "secret intervention: moral cost"


def test_missing_self_duplicate_and_incompatible_borrows_fail_before_provider(tmp_path, monkeypatch):
    discovery, *_ = _write_run(tmp_path)

    def explode(*args, **kwargs):
        raise AssertionError("provider must not be constructed for deterministic eligibility failure")

    monkeypatch.setattr("auteur.llm.factory.build_client", explode)

    assert dispatch_story_discovery_compose(
        _args(discovery, borrow=["candidate_99:missing mechanism"])
    ) == 1
    assert dispatch_story_discovery_compose(
        _args(discovery, borrow=["candidate_1:self mechanism"])
    ) == 1
    assert dispatch_story_discovery_compose(
        _args(
            discovery,
            borrow=["candidate_2:first", "candidate_2:second"],
        )
    ) == 1

    incompatible_dir = tmp_path / "incompatible"
    incompatible_dir.mkdir()
    nested, *_ = _write_run(incompatible_dir, composability="requires_reframing")
    assert dispatch_story_discovery_compose(
        _args(nested, borrow=["candidate_2:secret intervention"])
    ) == 1


def test_nonqualified_causal_set_fails_before_provider(tmp_path, monkeypatch):
    discovery, *_ = _write_run(tmp_path, causal_status="not_adjudicable_uncertain")
    monkeypatch.setattr(
        "auteur.llm.factory.build_client",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("provider must not be used")),
    )
    assert dispatch_story_discovery_compose(_args(discovery)) == 1


def test_composition_request_excludes_primary_and_alternative_self_advocacy(tmp_path):
    discovery, primary, secondary, causal, craft = _write_run(tmp_path)
    request = build_composition_request(
        "candidate_1",
        primary,
        [(parse_borrow_spec("candidate_2:secret interventions"), secondary, craft.impacts["candidate_2"])],
        causal,
        declared_author_intent={"premise": "controlled premise"},
    )
    assert "SELF ADVOCACY" not in request.user
    assert "0.99" not in request.user
    assert '"requested_mechanism": "secret interventions"' in request.user
    assert '"hard_constraints"' in request.user
    assert '"architecture_preferences"' in request.user
    assert "primary_with_layers" in request.user


def test_preserved_commitment_mismatch_fails_closed():
    primary = _identity("Primary", "primary conflict")
    composed = _composed_from(primary)
    composed.target_experience.primary = "a different governing promise"
    with pytest.raises(ValueError, match="target_experience.primary"):
        _validate_preserved_commitments(primary, composed)


def test_hierarchy_displacement_writes_no_composed_candidate(tmp_path, monkeypatch):
    discovery, primary, *_ = _write_run(tmp_path)
    client = ComposeClient(_composed_from(primary), hierarchy="primary_displaced")
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: client)

    assert dispatch_story_discovery_compose(_args(discovery)) == 1
    assert not (discovery / "composed_candidate.yaml").exists()
    assert not (discovery / "composition_report.yaml").exists()
    assert not (tmp_path / "story_identity.yaml").exists()


def test_successful_composition_writes_candidate_and_report_without_changing_source_recommendation(
    tmp_path, monkeypatch, capsys
):
    discovery, primary, *_ = _write_run(tmp_path)
    original_report = yaml.safe_load(
        (discovery / "discovery_report.yaml").read_text(encoding="utf-8")
    )
    original_set = (discovery / "discovery_set.yaml").read_text(encoding="utf-8")
    original_primary = (discovery / "candidate_1.yaml").read_text(encoding="utf-8")
    client = ComposeClient(_composed_from(primary))
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: client)

    assert dispatch_story_discovery_compose(_args(discovery)) == 0
    stdout = capsys.readouterr().out
    composed_path = discovery / "composed_candidate.yaml"
    report_path = discovery / "composition_report.yaml"

    assert composed_path.exists()
    assert report_path.exists()
    composed = StoryIdentity.from_yaml(composed_path)
    assert composed.title == "What She Saves — Layered"
    assert composed.story_type == primary.story_type
    assert composed.target_experience.primary == primary.target_experience.primary
    assert composed.architecture_preferences == primary.architecture_preferences
    assert composed.hard_constraints == primary.hard_constraints

    report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "candidate_only"
    assert report["primary_candidate_id"] == "candidate_1"
    assert report["borrowed"][0]["candidate_id"] == "candidate_2"
    assert report["hierarchy_assessment"]["classification"] == "primary_preserved"
    assert report["composed_causal_profile"]["causal_owner"].startswith("protagonist-led")

    assert yaml.safe_load((discovery / "discovery_report.yaml").read_text(encoding="utf-8")) == original_report
    assert (discovery / "discovery_set.yaml").read_text(encoding="utf-8") == original_set
    assert (discovery / "candidate_1.yaml").read_text(encoding="utf-8") == original_primary
    assert not (tmp_path / "story_identity.yaml").exists()
    assert "Nothing has been accepted yet." in stdout
    assert "story-discovery accept" in stdout


def test_explicit_accept_can_promote_composed_candidate_after_success(tmp_path, monkeypatch):
    discovery, primary, *_ = _write_run(tmp_path)
    client = ComposeClient(_composed_from(primary))
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: client)
    assert dispatch_story_discovery_compose(_args(discovery)) == 0

    canonical = tmp_path / "story_identity.yaml"
    assert main(
        [
            "story-discovery",
            "accept",
            str(discovery / "composed_candidate.yaml"),
            "--output",
            str(canonical),
            "--keep-candidates",
        ]
    ) == 0
    promoted = StoryIdentity.from_yaml(canonical)
    assert promoted.title == "What She Saves — Layered"
    assert promoted.architecture_preferences == primary.architecture_preferences
    assert promoted.hard_constraints == primary.hard_constraints
