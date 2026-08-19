from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from auteur.llm import LLMRequest, LLMResponse
from auteur.story_discovery_causality import CausalProfileRecord
from auteur.story_discovery_craft import (
    CraftImpact,
    build_craft_impact_request,
    derive_craft_impacts,
    parse_craft_impact,
    persist_craft_analysis,
)


class Dumpable(SimpleNamespace):
    def model_dump(self, mode="json"):
        return deepcopy(self.__dict__)


def _candidate(
    candidate_id: str,
    *,
    title: str,
    core_answer: str,
    conflict: str,
    primary: str = "painful dramatic irony",
    secondary: list[str] | None = None,
    advocacy: str = "self advocacy",
):
    identity = SimpleNamespace(
        title=title,
        core_answer=core_answer,
        central_engine=Dumpable(
            want="Resolve the external disaster aftermath.",
            resistance="Incomplete knowledge and competing interventions obstruct recovery.",
            conflict=conflict,
            stakes="Failure leaves the community exposed to a second catastrophe.",
            change="The protagonist earns practical closure without learning the forbidden truth.",
        ),
        story_type=Dumpable(genre="other", medium="novel", mode="other", target_audience="adult"),
        target_experience=Dumpable(
            primary=primary,
            primary_emotional_promise=primary,
            secondary_palette=list(secondary or []),
            emotional_trajectory=None,
        ),
        not_this=[],
        open_questions=[],
        author_overrides=[],
        hard_constraints=["the protagonist never learns her brother caused the disaster"],
        why_this_is_best=advocacy,
        alternatives=[advocacy],
        confidence=0.99,
        rejected_directions=[advocacy],
    )
    candidate = SimpleNamespace(
        lens=advocacy,
        recommendation_summary=advocacy,
        tradeoffs=[advocacy],
        risks=[advocacy],
        best_for=[advocacy],
    )
    return SimpleNamespace(candidate_id=candidate_id, identity=identity, candidate=candidate)


def _profile(key: str, strategy: str, actions: list[str], pressure: str, climax: str):
    return CausalProfileRecord(
        evidence_key=key,
        primary_strategy=strategy,
        causal_owner="protagonist-led" if "repair" in strategy else "brother-led hidden intervention",
        external_action_pattern=actions,
        pressure_system=pressure,
        reversal_mechanics=[f"a reversal emerges from {strategy}"],
        climax_mechanic=climax,
        scene_families=[f"{action} scene" for action in actions[:3]],
        evidence_gaps=[],
    )


def _impact_payload(**overrides):
    payload = {
        "craft_layers_changed": ["causal_ownership", "external_action", "scene_families", "reader_experience", "theme"],
        "causal_ownership_shift": "More consequential turns originate with the brother's hidden interventions.",
        "external_action_shift": {
            "add_or_emphasize": ["conceal", "intervene", "compensate", "sacrifice"],
            "de_emphasize": ["direct protagonist-led repair decisions"],
        },
        "scene_family_shift": ["parallel hidden intervention", "near-discovery", "unintended consequence"],
        "pressure_texture_shift": "More dramatic-ironic hidden-action suspense and less purely protagonist-centered recovery.",
        "reader_experience_shift": {
            "primary_promise_effect": "preserved_but_reweighted",
            "secondary_palette_effect": ["more pity", "more moral discomfort", "more dread"],
            "trajectory_effect": "Reader knowledge becomes more painful as secret interventions accumulate.",
        },
        "thematic_effect": "Moves emphasis toward whether atonement matters without confession.",
        "gain": "Stronger hidden causal pressure and moral complexity.",
        "give_up": "Some causal ownership moves away from the declared protagonist.",
        "composability": "compatible_as_secondary",
        "composition_note": "Works beneath protagonist-led recovery if the brother does not solve decisive turns.",
        "primary_risk": "If the brother resolves too many obstacles, he becomes the effective protagonist.",
        "evidence_gaps": [],
    }
    payload.update(overrides)
    return payload


class CraftClient:
    def __init__(self, payload=None):
        self.payload = payload if payload is not None else _impact_payload()
        self.requests: list[LLMRequest] = []

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        text = self.payload if isinstance(self.payload, str) else json.dumps(self.payload)
        return LLMResponse(text=text, input_tokens=1, output_tokens=1)


def _fixtures():
    primary = _candidate(
        "candidate_1",
        title="What She Saves",
        core_answer="She repairs the disaster while permanently misattributing its original cause.",
        conflict="She must rebuild while acting on an incomplete but workable explanation.",
        secondary=["dread", "hope"],
    )
    alternative = _candidate(
        "candidate_2",
        title="His Quiet Repair",
        core_answer="Her brother secretly helps repair the disaster he caused without confessing.",
        conflict="His hidden interventions solve one problem while creating another.",
        secondary=["dread", "pity"],
    )
    profiles = {
        "candidate_1": _profile(
            "aaaaaaaa111111111111",
            "repair visible consequences under incomplete knowledge",
            ["repair", "organize", "protect", "choose"],
            "incomplete knowledge and visible recovery pressure",
            "the protagonist's own recovery decisions resolve the external crisis",
        ),
        "candidate_2": _profile(
            "bbbbbbbb222222222222",
            "secret atonement through hidden repair interventions",
            ["conceal", "intervene", "compensate", "sacrifice"],
            "near-discovery and unintended consequences of hidden intervention",
            "the brother sacrifices without confessing while the protagonist still completes her goal",
        ),
    }
    return primary, alternative, profiles


def test_craft_impact_schema_is_strict_and_categorical():
    impact = CraftImpact.model_validate(_impact_payload())
    assert impact.composability == "compatible_as_secondary"
    assert impact.reader_experience_shift.primary_promise_effect == "preserved_but_reweighted"

    with pytest.raises(ValueError):
        CraftImpact.model_validate({**_impact_payload(), "pedagogy_score": 9.8})


def test_malformed_craft_output_fails_closed():
    with pytest.raises(ValueError, match="did not contain"):
        parse_craft_impact("not json")
    with pytest.raises(ValueError, match="failed schema validation"):
        parse_craft_impact(json.dumps({"gain": "only one field"}))


def test_title_and_self_advocacy_do_not_change_bounded_craft_request():
    primary, alternative, profiles = _fixtures()
    renamed = _candidate(
        "candidate_99",
        title="A Completely Different Marketing Title",
        core_answer=alternative.identity.core_answer,
        conflict=alternative.identity.central_engine.conflict,
        secondary=["dread", "pity"],
        advocacy="MUTATED SELF ADVOCACY MUST NOT LEAK",
    )
    first = build_craft_impact_request(
        primary,
        alternative,
        profiles["candidate_1"],
        profiles["candidate_2"],
        "Brother disaster premise",
    )
    second = build_craft_impact_request(
        primary,
        renamed,
        profiles["candidate_1"],
        profiles["candidate_2"],
        "Brother disaster premise",
    )
    assert first.user == second.user
    assert "His Quiet Repair" not in first.user
    assert "MUTATED SELF ADVOCACY" not in second.user
    assert "candidate_99" not in second.user


def test_declared_architecture_preferences_are_labeled_as_prior_intent_not_emotion():
    primary, alternative, profiles = _fixtures()
    declared = {
        "target_experience": {
            "primary_emotional_promise": "painful dramatic irony",
            "secondary_palette": ["dread", "hope"],
        },
        "architecture_preferences": {
            "complexity": "maximalist",
            "causal_distribution": "mixed",
            "engine_hierarchy": "primary_with_layers",
        },
    }
    request = build_craft_impact_request(
        primary,
        alternative,
        profiles["candidate_1"],
        profiles["candidate_2"],
        "Brother disaster premise",
        declared_author_intent=declared,
    )
    assert '"architecture_preferences"' in request.user
    assert '"maximalist"' in request.user
    assert "Architecture preferences are authorial architecture constraints, not emotions." in request.system


def test_missing_architecture_preferences_are_not_invented_in_evidence():
    primary, alternative, profiles = _fixtures()
    request = build_craft_impact_request(
        primary,
        alternative,
        profiles["candidate_1"],
        profiles["candidate_2"],
        "Brother disaster premise",
        declared_author_intent={
            "target_experience": {"primary_emotional_promise": "painful dramatic irony"}
        },
    )
    evidence = json.loads(request.user.split("BOUNDED CRAFT EVIDENCE\n", 1)[1])
    assert "architecture_preferences" not in evidence["declared_author_intent"]


def test_missing_secondary_palette_does_not_require_invented_emotions():
    payload = _impact_payload(
        reader_experience_shift={
            "primary_promise_effect": "preserved",
            "secondary_palette_effect": [],
            "trajectory_effect": None,
        },
        evidence_gaps=["No declared secondary emotional palette or trajectory."],
    )
    impact = CraftImpact.model_validate(payload)
    assert impact.reader_experience_shift.secondary_palette_effect == []
    assert impact.reader_experience_shift.trajectory_effect is None
    assert impact.evidence_gaps


def test_derive_craft_impacts_records_pair_traceability_without_mutating_candidates():
    primary, alternative, profiles = _fixtures()
    client = CraftClient()
    before_primary = deepcopy(primary.identity.__dict__)
    before_alternative = deepcopy(alternative.identity.__dict__)

    analysis = derive_craft_impacts(
        client,
        "candidate_1",
        [primary, alternative],
        profiles,
        "Brother disaster premise",
        declared_author_intent={
            "architecture_preferences": {
                "complexity": "maximalist",
                "causal_distribution": "mixed",
                "engine_hierarchy": "primary_with_layers",
            }
        },
    )

    assert analysis.status == "complete"
    record = analysis.impacts["candidate_2"]
    assert record.primary_candidate_id == "candidate_1"
    assert record.compared_candidate_id == "candidate_2"
    assert record.primary_evidence_key == profiles["candidate_1"].evidence_key
    assert record.compared_evidence_key == profiles["candidate_2"].evidence_key
    assert primary.identity.__dict__ == before_primary
    assert alternative.identity.__dict__ == before_alternative
    assert len(client.requests) == 1


def test_craft_analysis_requires_profile_for_every_survivor():
    primary, alternative, profiles = _fixtures()
    with pytest.raises(ValueError, match="one causal profile"):
        derive_craft_impacts(
            CraftClient(),
            "candidate_1",
            [primary, alternative],
            {"candidate_1": profiles["candidate_1"]},
            "Brother disaster premise",
        )


def test_persist_craft_analysis_is_noncanonical(tmp_path: Path):
    primary, alternative, profiles = _fixtures()
    analysis = derive_craft_impacts(
        CraftClient(),
        "candidate_1",
        [primary, alternative],
        profiles,
        "Brother disaster premise",
    )
    output_dir = tmp_path / "story_discovery"
    output_dir.mkdir()
    report = output_dir / "discovery_report.yaml"
    report.write_text("recommended_candidate_id: candidate_1\n", encoding="utf-8")
    candidate_file = output_dir / "candidate_1.yaml"
    candidate_file.write_text("title: What She Saves\n", encoding="utf-8")

    persist_craft_analysis(output_dir, analysis)

    payload = yaml.safe_load(report.read_text(encoding="utf-8"))
    assert payload["craft_analysis"]["primary_candidate_id"] == "candidate_1"
    assert payload["craft_analysis"]["impacts"]["candidate_2"]["composability"] == "compatible_as_secondary"
    assert candidate_file.read_text(encoding="utf-8") == "title: What She Saves\n"
