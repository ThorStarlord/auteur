from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from auteur.llm import LLMResponse
from auteur.story_discovery_recommend import (
    _build_judge_request,
    _require_distinct_engines,
    dispatch_story_discovery_recommend,
)


@dataclass(frozen=True)
class EngineSeed:
    key: str
    title: str
    conflict: str
    change: str
    genre: str = "other"


@dataclass(frozen=True)
class SyntheticCase:
    case_id: str
    premise_class: str
    premise: str
    seeds: tuple[EngineSeed, EngineSeed, EngineSeed]
    preferred_key: str


CASES = (
    SyntheticCase(
        "U1",
        "underdetermined",
        "A lighthouse keeper receives letters from ships that sank decades ago.",
        (
            EngineSeed("grief", "The Last Mailboat", "Delivering the dead sailors' promises exposes the town's buried history.", "The keeper gives up protective isolation and becomes a witness for the dead."),
            EngineSeed("conspiracy", "Signal Below", "The letters expose a living smuggling network using old wrecks as cover.", "The keeper stops trusting official history and chooses public exposure."),
            EngineSeed("identity", "Names in the Fog", "A falsified passenger list ties the keeper personally to one of the wrecks.", "The keeper replaces an inherited identity with a deliberately chosen one."),
        ),
        "identity",
    ),
    SyntheticCase(
        "U2",
        "underdetermined",
        "Every Tuesday, a child finds a different key under the same tree.",
        (
            EngineSeed("wonder", "The Tuesday Doors", "Every key opens a temporary place that disappears at sunset.", "The child learns that wonder can matter without being possessed."),
            EngineSeed("family", "Keys to Before", "The keys open sealed rooms from the family's forgotten past.", "The child replaces inherited family stories with earned belonging."),
            EngineSeed("choice", "The Unused Key", "Each key reveals one future but using it permanently erases another.", "The child gives up certainty and accepts responsibility for irreversible choice."),
        ),
        "choice",
    ),
    SyntheticCase(
        "U3",
        "underdetermined",
        "A retired astronaut hears mission-control chatter in her empty apartment.",
        (
            EngineSeed("memory", "Dead Channel", "The chatter reconstructs a failed mission she has spent years misremembering.", "She gives up protective memory and accepts an accurate account of her choices.", "sci_fi"),
            EngineSeed("rescue", "One More Orbit", "The chatter belongs to a time-displaced survivor of her old mission.", "She stops treating retirement as surrender and chooses one last rescue attempt.", "sci_fi"),
            EngineSeed("coverup", "Ground Loop", "The signal proves mission control sacrificed her crew for a classified objective.", "She abandons loyalty to the institution and becomes its public accuser.", "sci_fi"),
        ),
        "memory",
    ),
    SyntheticCase(
        "C1",
        "constraint-heavy",
        "A murder mystery in one elevator: six strangers, no supernatural explanation, and the killer never leaves the elevator.",
        (
            EngineSeed("timing", "Between Floors", "The murder occurred during a staged emergency stop while everyone remained inside.", "The detective replaces intuition with a precise reconstruction of hidden seconds.", "mystery"),
            EngineSeed("identity", "Sixth Passenger", "The victim's false identity makes motive the central sealed-room puzzle.", "The detective learns that access matters less than the social identity everyone protected.", "mystery"),
            EngineSeed("collusion", "All Doors Closed", "Several passengers conceal one killer's act for different reasons.", "The detective distinguishes collective concealment from individual guilt.", "mystery"),
        ),
        "timing",
    ),
    SyntheticCase(
        "C2",
        "constraint-heavy",
        "A romance told only through grocery lists; the couple never meets on page, and the ending must be hopeful.",
        (
            EngineSeed("care", "Things We Leave in the Cart", "Shared grocery lists turn practical substitutions into declarations of care.", "Both writers risk making their private care legible and choose a shared future.", "romance"),
            EngineSeed("misread", "Substitutions", "Mistaken substitutions make each person infer a life the other is not living.", "They replace projection with vulnerable, accurate attention.", "romance"),
            EngineSeed("recovery", "For Next Week", "Lists exchanged during illness become a record of recovery and commitment.", "Caregiving becomes mutual choice rather than one-sided obligation.", "romance"),
        ),
        "care",
    ),
    SyntheticCase(
        "C3",
        "constraint-heavy",
        "A heist where nothing can be stolen, nobody may lie, and the crew must still defeat a corrupt museum director.",
        (
            EngineSeed("provenance", "Nothing Missing", "The crew re-proves every object's provenance until the director's ownership claims collapse.", "The crew replaces possession with public proof as its definition of victory."),
            EngineSeed("access", "Open House", "Lawful access rules force hidden records into public view without taking them.", "The crew learns to weaponize procedure instead of secrecy."),
            EngineSeed("performance", "The Honest Con", "A staged exhibition of true statements causes the audience to infer the fraud.", "The crew gives up deception and learns to control context instead."),
        ),
        "provenance",
    ),
    SyntheticCase(
        "G1",
        "strong-genre-promise",
        "A cozy-mystery baker investigates who poisoned the town pie contest without killing anyone.",
        (
            EngineSeed("community", "A Slice of Suspicion", "The sabotage exposes a feud threatening the town's shared traditions.", "The baker learns to solve harm while repairing the community that produced it.", "cozy_mystery"),
            EngineSeed("competition", "Blue Ribbon Alibi", "Recipes and judging times reveal a contestant manipulating the competition.", "The baker replaces friendly assumptions with fair-minded scrutiny.", "cozy_mystery"),
            EngineSeed("inheritance", "Recipe for Trouble", "An old recipe dispute conceals a contested family inheritance.", "The baker turns nostalgia into an honest account of what the town owes its families.", "cozy_mystery"),
        ),
        "community",
    ),
    SyntheticCase(
        "G2",
        "strong-genre-promise",
        "A commuter realizes the same stranger boards every train she takes, even after she changes cities.",
        (
            EngineSeed("pursuit", "Next Stop", "The commuter tests routes to prove the stranger is tracking her toward a hidden objective.", "She stops running randomly and becomes an active counter-pursuer.", "thriller"),
            EngineSeed("network", "Platform Pattern", "The stranger is one node in a surveillance network built from transit routines.", "She gives up the fantasy of anonymity and learns to disrupt the system predicting her.", "thriller"),
            EngineSeed("memory", "Last Train Home", "The stranger follows clues the commuter unknowingly left during a memory gap.", "She replaces fear of the stranger with a harder investigation of her missing self.", "thriller"),
        ),
        "network",
    ),
    SyntheticCase(
        "G3",
        "strong-genre-promise",
        "A family inherits a house that becomes one room smaller every night.",
        (
            EngineSeed("avoidance", "The Missing Room", "Rooms disappear in the order the family uses them to avoid old harm.", "The family stops spatializing denial and confronts the injury holding them together.", "horror"),
            EngineSeed("containment", "Measured Walls", "The shrinking plan reveals the house is sealing something into less space with them.", "The family gives up escape and chooses what must be contained or released.", "horror"),
            EngineSeed("inheritance", "Square Footage", "Each lost room corresponds to a person erased from the inheritance record.", "The heirs restore the excluded dead to the family's account of itself.", "horror"),
        ),
        "avoidance",
    ),
    SyntheticCase(
        "A1",
        "author-boundary",
        "The protagonist must never learn that her brother caused the disaster; the reader knows by the midpoint, and her external goal still resolves.",
        (
            EngineSeed("irony", "What She Saves", "She repairs the disaster while permanently misattributing its original cause.", "She gains competence and closure without receiving the forbidden knowledge."),
            EngineSeed("brother", "His Quiet Repair", "Her brother secretly helps repair the disaster he caused without confessing.", "He accepts responsibility through action while she completes her external arc without learning why."),
            EngineSeed("institution", "The Official Cause", "An institution gives her a false but actionable explanation while protecting her brother.", "She defeats the external obstacle but retains a deliberately incomplete private history."),
        ),
        "irony",
    ),
    SyntheticCase(
        "A2",
        "author-boundary",
        "No redemption arc for the tyrant: explain him, but never excuse him or make forgiveness the hero's victory.",
        (
            EngineSeed("accountability", "The Cost of Understanding", "The hero learns how the tyrant became cruel and uses that knowledge to dismantle his power.", "Understanding becomes strategic clarity rather than forgiveness."),
            EngineSeed("institution", "After the Throne", "Defeating the tyrant requires refusing the institutions that would reproduce him.", "The hero rejects both the tyrant and the structures that made his rule repeatable."),
            EngineSeed("witness", "No Pardon", "The hero preserves testimony when political peace pressures survivors to forgive.", "The hero chooses durable truth and justice over reconciliatory closure."),
        ),
        "accountability",
    ),
    SyntheticCase(
        "A3",
        "author-boundary",
        "History cannot be changed; a time traveler can only change what the trip means to people who remember it.",
        (
            EngineSeed("witness", "Fixed Point", "The traveler revisits an unchangeable tragedy to recover testimony for present survivors.", "She gives up rescue fantasies and becomes a deliberate witness.", "sci_fi"),
            EngineSeed("relationship", "The Same Goodbye", "Repeated visits cannot prevent a death but can change the conversations remembered afterward.", "She stops using time as rescue and uses fixed encounters to transform present relationships.", "sci_fi"),
            EngineSeed("legacy", "Annotations", "The traveler creates a present-day archive explaining why unchanged past choices mattered.", "She replaces intervention with custodianship as her measure of agency.", "sci_fi"),
        ),
        "witness",
    ),
)


class _SyntheticProvider:
    def __init__(self, seeds: tuple[EngineSeed, ...], preferred_key: str):
        self.seeds = seeds
        self.preferred_key = preferred_key
        self.generation_index = 0
        self.judge_requests = []

    def _seed_for_profiler_request(self, request) -> EngineSeed:
        evidence = json.loads(request.user.split("BOUNDED STORY EVIDENCE\n", 1)[1])
        conflict = evidence["candidate_commitments"]["central_engine"]["conflict"]
        return next(seed for seed in self.seeds if seed.conflict == conflict)

    def complete(self, request):
        if "bounded narrative-causality profiler" in request.system:
            seed = self._seed_for_profiler_request(request)
            return LLMResponse(
                text=json.dumps(
                    {
                        "primary_strategy": f"pursue the {seed.key} strategy through premise-specific action",
                        "causal_owner": "protagonist-led",
                        "external_action_pattern": [
                            f"investigate {seed.key}",
                            f"pressure {seed.key}",
                            f"resolve {seed.key}",
                        ],
                        "pressure_system": f"resistance generated by the {seed.key} engine",
                        "reversal_mechanics": [
                            f"new {seed.key} evidence changes the protagonist's plan"
                        ],
                        "climax_mechanic": (
                            f"the protagonist resolves the {seed.key} conflict through its defining action"
                        ),
                        "scene_families": [
                            f"{seed.key} setup",
                            f"{seed.key} escalation",
                            f"{seed.key} climax",
                        ],
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
                                "shared_causal_mechanics": ["same premise-level objective"],
                                "material_differences": [
                                    "controlled seed keys imply different action and climax mechanics"
                                ],
                                "scene_consequence": (
                                    "The controlled synthetic profiles imply materially different major scenes."
                                ),
                                "rationale": (
                                    "Synthetic F3 harness preserves content-defined distinctions, not position or ID."
                                ),
                            }
                            for pair in pairs
                        ]
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )

        if "comparative narrative architect" in request.system:
            self.judge_requests.append(request)
            evidence = json.loads(request.user.split("SURVIVING CANDIDATE EVIDENCE\n", 1)[1])
            by_title = {
                item["story_identity"]["title"]: item["candidate_id"]
                for item in evidence
            }
            preferred = next(seed for seed in self.seeds if seed.key == self.preferred_key)
            winner = by_title[preferred.title]
            rejected = {
                item["candidate_id"]: (
                    f"Synthetic contrast: {item['story_identity']['title']} "
                    "optimizes a different tradeoff."
                )
                for item in evidence
                if item["candidate_id"] != winner
            }
            return LLMResponse(
                text=json.dumps(
                    {
                        "recommended_candidate_id": winner,
                        "recommendation_rationale": (
                            "Synthetic blind expectation prefers the content-defined engine, "
                            "not its position or candidate ID."
                        ),
                        "rejected_candidate_reasons": rejected,
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )

        if "assistant summarizing a story identity" in request.system:
            return LLMResponse(
                text=json.dumps(
                    {
                        "summary": "Controlled synthetic summary.",
                        "tradeoffs": ["Tradeoff one", "Tradeoff two"],
                        "risks": ["Risk one", "Risk two"],
                        "best_for": ["Scenario one", "Scenario two"],
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )

        seed = self.seeds[self.generation_index]
        self.generation_index += 1
        basis = "genre_aligned"
        if "best_basis: 'emotionally_powerful'" in request.system:
            basis = "emotionally_powerful"
        elif "best_basis: 'structurally_coherent'" in request.system:
            basis = "structurally_coherent"
        data = {
            "title": seed.title,
            "core_answer": (
                f"{seed.title}: the protagonist pursues a premise-specific goal, "
                "meets escalating resistance, and reaches a changed relationship to it."
            ),
            "target_experience": {
                "primary": f"mounting pressure around the {seed.key} interpretation",
                "progression": "curiosity -> pressure -> transformed understanding",
                "avoid": ["emotional flatness"],
            },
            "story_type": {
                "medium": "novel",
                "mode": "other",
                "genre": seed.genre,
                "subgenres": [],
                "target_audience": "adult",
                "length_class": None,
            },
            "central_engine": {
                "want": f"The protagonist must resolve the {seed.key} objective before it closes.",
                "resistance": f"Opposition rooted in the {seed.key} engine blocks the direct solution.",
                "conflict": seed.conflict,
                "stakes": f"Failure makes the {seed.key} loss permanent and public.",
                "change": seed.change,
            },
            "not_this": ["a generic version that ignores the premise mechanism"],
            "open_questions": ["Which scene proves this engine most clearly?"],
            "confidence": 0.8,
            "alternatives": ["Synthetic self-advocacy metadata."],
            "recommendation_mode": "open_ended",
            "best_basis": basis,
            "why_this_is_best": "Synthetic provider self-advocacy metadata.",
            "rejected_directions": ["Synthetic provider rejected-direction metadata."],
            "author_overrides": [],
        }
        return LLMResponse(
            text="```yaml\n" + yaml.safe_dump(data, sort_keys=False) + "```",
            input_tokens=1,
            output_tokens=1,
        )


def _args(tmp_path: Path, case: SyntheticCase, output_name: str = "story_discovery"):
    return SimpleNamespace(
        candidates=3,
        brain_dump=case.premise,
        provider="anthropic",
        model=None,
        genre=None,
        medium=None,
        mode=None,
        lens=None,
        strict_candidate_count=False,
        debug=False,
        project=None,
        output=tmp_path / output_name,
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_phase_d_naturalistic_cases_use_real_story_discovery_path(
    case, tmp_path, monkeypatch, capsys
):
    provider = _SyntheticProvider(case.seeds, case.preferred_key)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *args, **kwargs: provider)

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, case))
    output = capsys.readouterr().out

    assert exit_code == 0
    assert len(provider.judge_requests) == 1
    for seed in case.seeds:
        assert seed.title in output
    preferred = next(seed for seed in case.seeds if seed.key == case.preferred_key)
    assert f"RECOMMENDED — {preferred.title}" in output
    assert "Nothing has been accepted yet." in output
    assert not (tmp_path / "story_identity.yaml").exists()
    discovery_set = yaml.safe_load(
        (tmp_path / "story_discovery" / "discovery_set.yaml").read_text(encoding="utf-8")
    )
    assert discovery_set["recommended_candidate_id"] in {
        "candidate_1",
        "candidate_2",
        "candidate_3",
    }
    assert discovery_set["causal_analysis"]["status"] == "qualified"


def _dumpable_candidate(
    candidate_id: str,
    seed: EngineSeed,
    *,
    fit: int = 80,
    advocacy: str = "baseline",
):
    class Dumpable(SimpleNamespace):
        def model_dump(self, mode="json"):
            return dict(self.__dict__)

    identity = SimpleNamespace(
        title=seed.title,
        core_answer=f"Controlled core answer for {seed.title}.",
        target_experience=Dumpable(primary="controlled feeling", progression="a -> b -> c", avoid=[]),
        story_type=Dumpable(genre=seed.genre, medium="novel", mode="other"),
        central_engine=Dumpable(
            want=f"want {seed.key}",
            resistance=f"resistance {seed.key}",
            conflict=seed.conflict,
            stakes=f"stakes {seed.key}",
            change=seed.change,
        ),
        not_this=[],
        open_questions=[],
        author_overrides=[],
        genre_contract_snapshot=None,
        why_this_is_best=advocacy,
        alternatives=[advocacy],
        confidence=0.99,
        rejected_directions=[advocacy],
    )
    candidate = SimpleNamespace(
        validation_status="valid",
        warning_count=0,
        contract_fit=fit,
        contract_fit_status="strong" if fit >= 80 else "mixed",
        contract_fit_problems=[],
        contract_fit_notes=[],
        lens=advocacy,
        best_basis=SimpleNamespace(value=advocacy),
        recommendation_summary=advocacy,
        tradeoffs=[advocacy],
        risks=[advocacy],
        best_for=[advocacy],
    )
    return SimpleNamespace(candidate_id=candidate_id, identity=identity, candidate=candidate)


def test_phase_d_self_advocacy_mutation_does_not_change_bounded_judge_evidence():
    case = CASES[0]
    baseline = [
        _dumpable_candidate(f"candidate_{index}", seed, advocacy="BASELINE SELF ADVOCACY")
        for index, seed in enumerate(case.seeds, 1)
    ]
    mutated = [
        _dumpable_candidate(
            f"candidate_{index}",
            seed,
            advocacy="MUTATED SELF ADVOCACY SHOULD NOT LEAK",
        )
        for index, seed in enumerate(case.seeds, 1)
    ]

    first = _build_judge_request(case.premise, baseline, genre=None, medium=None, mode=None)
    second = _build_judge_request(case.premise, mutated, genre=None, medium=None, mode=None)

    assert first.user == second.user
    assert "SELF ADVOCACY" not in first.user


@pytest.mark.parametrize("order", [(0, 1, 2), (2, 0, 1), (1, 2, 0)])
def test_phase_d_candidate_order_preserves_content_defined_winner(
    order, tmp_path, monkeypatch, capsys
):
    original = CASES[1]
    reordered = replace(original, seeds=tuple(original.seeds[index] for index in order))
    provider = _SyntheticProvider(reordered.seeds, reordered.preferred_key)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *args, **kwargs: provider)

    output_name = "order_" + "".join(str(index) for index in order)
    assert dispatch_story_discovery_recommend(_args(tmp_path, reordered, output_name)) == 0
    output = capsys.readouterr().out
    preferred = next(seed for seed in reordered.seeds if seed.key == reordered.preferred_key)
    assert f"RECOMMENDED — {preferred.title}" in output
    assert not (tmp_path / "story_identity.yaml").exists()


def test_phase_d_candidate_id_remap_preserves_content_mapping():
    case = CASES[2]
    ids = ["candidate_3", "candidate_1", "candidate_2"]
    outputs = [
        _dumpable_candidate(candidate_id, seed)
        for candidate_id, seed in zip(ids, case.seeds, strict=True)
    ]
    request = _build_judge_request(case.premise, outputs, genre=None, medium=None, mode=None)
    evidence = json.loads(request.user.split("SURVIVING CANDIDATE EVIDENCE\n", 1)[1])
    title_to_id = {
        item["story_identity"]["title"]: item["candidate_id"]
        for item in evidence
    }
    preferred = next(seed for seed in case.seeds if seed.key == case.preferred_key)
    preferred_index = list(case.seeds).index(preferred)
    assert title_to_id[preferred.title] == ids[preferred_index]


def test_phase_d_high_contract_fit_is_evidence_not_a_deterministic_winner():
    case = CASES[3]
    high = _dumpable_candidate("candidate_1", case.seeds[0], fit=100)
    lower = _dumpable_candidate("candidate_2", case.seeds[1], fit=60)
    request = _build_judge_request(
        case.premise,
        [high, lower],
        genre="mystery",
        medium=None,
        mode=None,
    )
    assert '"contract_fit": 100' in request.user
    assert '"contract_fit": 60' in request.user
    assert "A higher contract-fit number does not automatically win." in request.system


def test_phase_d_exact_duplicate_and_semantic_near_duplicate_boundary():
    seed = CASES[4].seeds[0]
    exact_a = _dumpable_candidate("candidate_1", seed)
    exact_b = _dumpable_candidate("candidate_2", seed)
    with pytest.raises(ValueError, match="exact duplicates"):
        _require_distinct_engines([exact_a, exact_b])

    near = replace(
        seed,
        conflict=seed.conflict + " in essentially the same causal pattern",
        change=seed.change + " while preserving the same underlying transformation",
    )
    _require_distinct_engines([exact_a, _dumpable_candidate("candidate_2", near)])


def test_phase_d_explicit_constraints_remain_visible_to_comparative_judge():
    case = CASES[6]
    outputs = [
        _dumpable_candidate(f"candidate_{index}", seed)
        for index, seed in enumerate(case.seeds[:2], 1)
    ]
    request = _build_judge_request(
        case.premise,
        outputs,
        genre="mystery",
        medium="novel",
        mode="other",
    )
    assert '"genre": "mystery"' in request.user
    assert '"medium": "novel"' in request.user
    assert '"mode": "other"' in request.user
    assert case.premise in request.user


def test_phase_d_judge_schema_requires_complete_rejection_coverage(
    tmp_path, monkeypatch, capsys
):
    case = CASES[7]
    provider = _SyntheticProvider(case.seeds, case.preferred_key)
    normal_complete = provider.complete

    def malformed(request):
        if "comparative narrative architect" in request.system:
            return LLMResponse(
                text=json.dumps(
                    {
                        "recommended_candidate_id": "candidate_1",
                        "recommendation_rationale": "Incomplete synthetic judgment.",
                        "rejected_candidate_reasons": {
                            "candidate_2": "Only one rejection."
                        },
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )
        return normal_complete(request)

    provider.complete = malformed
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *args, **kwargs: provider)

    assert dispatch_story_discovery_recommend(_args(tmp_path, case)) == 1
    error = capsys.readouterr().err
    assert "rejection reasons must cover exactly every non-selected survivor" in error
    assert not (tmp_path / "story_identity.yaml").exists()


def test_phase_d_authority_gate_recommendation_never_promotes_canonical_identity(
    tmp_path, monkeypatch
):
    case = CASES[-1]
    provider = _SyntheticProvider(case.seeds, case.preferred_key)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *args, **kwargs: provider)

    assert dispatch_story_discovery_recommend(_args(tmp_path, case)) == 0
    assert (tmp_path / "story_discovery" / "comparison.md").exists()
    assert not (tmp_path / "story_identity.yaml").exists()
