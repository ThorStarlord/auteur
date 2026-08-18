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
class CandidateSpec:
    key: str
    title: str
    core_answer: str
    primary: str
    want: str
    resistance: str
    conflict: str
    stakes: str
    change: str
    genre: str = "mystery"
    medium: str = "novella"
    mode: str = "dramatic"
    why: str = "Synthetic provider self-advocacy; excluded from comparative evidence."
    confidence: float = 0.8


@dataclass(frozen=True)
class NaturalisticCase:
    case_id: str
    premise_class: str
    premise: str
    candidates: tuple[CandidateSpec, CandidateSpec, CandidateSpec]
    preferred_key: str
    rationale: str


def _spec(
    key: str,
    title: str,
    core: str,
    primary: str,
    conflict: str,
    *,
    want: str | None = None,
    resistance: str | None = None,
    stakes: str | None = None,
    change: str | None = None,
    genre: str = "mystery",
) -> CandidateSpec:
    return CandidateSpec(
        key=key,
        title=title,
        core_answer=core,
        primary=primary,
        want=want or f"The protagonist must pursue the {key} objective before the window closes.",
        resistance=resistance or f"The {key} opposition makes every direct route costly.",
        conflict=conflict,
        stakes=stakes or f"Failure permanently destroys what the {key} objective was meant to protect.",
        change=change or f"The protagonist abandons the old certainty and adopts the {key} truth as a new way of acting.",
        genre=genre,
    )


NATURALISTIC_CASES = (
    NaturalisticCase(
        "U1",
        "underdetermined",
        "A lighthouse keeper receives letters from ships that sank decades ago.",
        (
            _spec("grief", "The Last Mailboat", "A keeper follows impossible letters to finish the dead sailors' unresolved promises.", "melancholy curiosity becoming release", "Each delivered promise makes the keeper complicit in a history the town buried."),
            _spec("conspiracy", "Signal Below", "The letters expose a living smuggling network using old wrecks as cover.", "suspicion becoming hunted certainty", "The keeper must expose present criminals while the entire port profits from the old lie."),
            _spec("identity", "Names in the Fog", "The letters reveal the keeper is connected to a wreck whose official passenger list was falsified.", "uncanny recognition becoming self-redefinition", "The keeper's search for a sender becomes a fight over who has the right to define the keeper's past."),
        ),
        "identity",
        "The identity engine makes the supernatural correspondence causal to the protagonist's own stakes while preserving the premise's mystery.",
    ),
    NaturalisticCase(
        "U2",
        "underdetermined",
        "Every Tuesday, a child finds a different key under the same tree.",
        (
            _spec("wonder", "The Tuesday Doors", "Each key opens one temporary place the child must understand before sunset.", "wonder becoming bittersweet responsibility", "The child wants to keep the magical places, but every opened door must close forever."),
            _spec("family", "Keys to Before", "The keys open sealed rooms from the child's family's forgotten past.", "curiosity becoming difficult belonging", "The child must uncover family truths while the adults keep rewriting what happened."),
            _spec("choice", "The Unused Key", "Each key corresponds to a future choice, and using one erases the others.", "playful curiosity becoming moral weight", "The child wants certainty about the future but every answer permanently narrows who they can become."),
        ),
        "choice",
        "The choice engine turns the repeating key mechanic into escalating irreversible decisions rather than episodic novelty.",
    ),
    NaturalisticCase(
        "U3",
        "underdetermined",
        "A retired astronaut starts hearing mission-control chatter in her empty apartment.",
        (
            _spec("memory", "Dead Channel", "The chatter recreates the failed mission she has spent years misremembering.", "dread becoming painful clarity", "She must reconstruct the mission while her own protective memory edits the evidence."),
            _spec("rescue", "One More Orbit", "The chatter comes from an astronaut trapped in a time-displaced version of her old mission.", "urgency becoming impossible hope", "She must mount a rescue with obsolete knowledge while authorities treat the signal as trauma."),
            _spec("coverup", "Ground Loop", "The chatter is a covert transmission proving mission control sacrificed her crew for a classified objective.", "paranoia becoming righteous anger", "She must expose the people who own the official history before they silence the only surviving evidence."),
        ),
        "memory",
        "The memory engine binds the impossible chatter directly to the retired astronaut's unresolved transformation and premise-specific emotional core.",
    ),
    NaturalisticCase(
        "C1",
        "constraint-heavy",
        "A murder mystery in one elevator: six strangers, no supernatural explanation, and the killer must never leave the elevator.",
        (
            _spec("timing", "Between Floors", "The detective proves the murder happened during a staged emergency stop while every suspect remained inside.", "claustrophobic suspicion becoming mechanical clarity", "The detective must reconstruct seconds of hidden action while the suspects can alter the tiny crime scene."),
            _spec("identity", "Sixth Passenger", "The victim's false identity makes motive, not access, the central puzzle inside the sealed elevator.", "social suspicion becoming revelation", "The detective must determine who the victim really was while every suspect has a reason to preserve the false identity."),
            _spec("collusion", "All Doors Closed", "Several passengers helped conceal one killer's act for different reasons, though only one committed the murder.", "mistrust becoming moral disgust", "The detective must separate murder from collective concealment without inventing an outside accomplice."),
        ),
        "timing",
        "The timing engine uses the elevator constraint as the causal puzzle rather than treating the sealed location as decoration.",
    ),
    NaturalisticCase(
        "C2",
        "constraint-heavy",
        "A romance told only through grocery lists; the couple never meets on page, and the ending must be hopeful rather than tragic.",
        (
            _spec("care", "Things We Leave in the Cart", "Two neighbors alter shared grocery lists until practical substitutions become declarations of care.", "amusement becoming tenderness", "Each person wants to be known without breaking the list-only ritual that made honesty possible.", genre="romance"),
            _spec("misread", "Substitutions", "A chain of mistaken grocery substitutions makes each person infer a life the other is not actually living.", "comic uncertainty becoming vulnerable recognition", "They must correct increasingly intimate assumptions without ever speaking directly on page.", genre="romance"),
            _spec("recovery", "For Next Week", "Lists exchanged during illness become a record of one person's recovery and the other's growing commitment.", "concern becoming hopeful intimacy", "The pair must let practical caregiving become mutual choice without turning the ending into loss.", genre="romance"),
        ),
        "care",
        "The care engine makes the formal list constraint itself carry the romantic progression and preserves the required hopeful ending.",
    ),
    NaturalisticCase(
        "C3",
        "constraint-heavy",
        "A heist where nothing can be stolen, nobody may lie, and the crew must still defeat a corrupt museum director.",
        (
            _spec("provenance", "Nothing Missing", "The crew publicly re-proves the provenance of every object until the director's ownership claims collapse.", "cleverness becoming public vindication", "The crew must use only true statements and leave every object physically untouched while dismantling the director's authority."),
            _spec("access", "Open House", "The crew uses lawful access rules to force hidden records into public view without taking them.", "procedural tension becoming exposure", "They must turn the museum's own transparent procedures against a director who controls interpretation but cannot suppress every record."),
            _spec("performance", "The Honest Con", "A staged exhibition composed entirely of true statements causes donors and investigators to infer the director's fraud themselves.", "playful tension becoming collective recognition", "The crew must orchestrate truthful context so the audience reaches the damaging conclusion without a single false claim."),
        ),
        "provenance",
        "The provenance engine most directly solves the apparent contradiction: a heist-shaped victory with no theft and no lies.",
    ),
    NaturalisticCase(
        "G1",
        "strong-genre-promise",
        "A cozy mystery baker investigates who poisoned the town's annual pie contest without killing anyone.",
        (
            _spec("community", "A Slice of Suspicion", "The baker traces harmless poisonings to a feud threatening the town's shared traditions.", "comfort disrupted by curiosity, restored through repair", "The baker must expose sabotage without destroying the relationships that make the town worth protecting."),
            _spec("competition", "Blue Ribbon Alibi", "The baker reconstructs rivalries, recipes, and timing to identify a contestant manipulating the judging.", "playful rivalry becoming satisfying deduction", "The baker must solve a fair-play puzzle while every suspect has a plausible competitive motive."),
            _spec("inheritance", "Recipe for Trouble", "The poisoning points to an old recipe dispute that conceals a contested family inheritance.", "nostalgia becoming reconciled truth", "The baker must untangle family history before the contest turns a private grievance into permanent community division."),
        ),
        "community",
        "The community engine best preserves the cozy promise by making detection restore a damaged social fabric rather than merely solve sabotage.",
    ),
    NaturalisticCase(
        "G2",
        "strong-genre-promise",
        "A thriller about a commuter who realizes the same stranger boards every train she takes, even after she changes cities.",
        (
            _spec("pursuit", "Next Stop", "The commuter tests routes and cities to prove the stranger is tracking her toward a hidden objective.", "unease escalating into hunted urgency", "She must discover what the pursuer wants while every attempt to flee reveals more of her pattern."),
            _spec("network", "Platform Pattern", "The stranger is one visible node in a surveillance network built from transit systems and ordinary routines.", "paranoia escalating into systemic dread", "She must break a network that predicts her movements better than she understands them herself."),
            _spec("self", "Last Train Home", "The stranger is following clues the commuter herself unknowingly left during a dissociative period.", "fear escalating into destabilizing self-recognition", "She must determine whether she is being hunted or retracing actions she cannot remember before someone else exploits the gap."),
        ),
        "network",
        "The network engine turns the impossible recurrence across cities into escalating systemic pressure while preserving thriller momentum.",
    ),
    NaturalisticCase(
        "G3",
        "strong-genre-promise",
        "A horror story in which a family inherits a house that becomes one room smaller every night.",
        (
            _spec("consumption", "The Missing Room", "The house consumes rooms in the order the family uses them to avoid confronting old harm.", "unease becoming inescapable dread", "The family must face what each disappearing room represented before the house leaves no space for them at all."),
            _spec("boundary", "Measured Walls", "The shrinking floor plan reveals the house is sealing something into progressively less space with the family.", "spatial unease becoming trapped terror", "They must discover what the house is containing before the final rooms force them into contact with it."),
            _spec("inheritance", "Square Footage", "Each lost room corresponds to an erased person in the family's inheritance history.", "uncanny curiosity becoming ancestral horror", "The heirs must restore the people their family removed from the record before the house erases the heirs in turn."),
        ),
        "consumption",
        "The consumption engine makes the shrinking-house mechanism an escalating expression of the family's avoidance and gives each lost room causal emotional force.",
    ),
    NaturalisticCase(
        "A1",
        "author-boundary",
        "The protagonist must never discover that her brother caused the disaster; the reader should know by the midpoint, and the ending must still resolve her external goal.",
        (
            _spec("dramatic-irony", "What She Saves", "The reader watches the protagonist save a project her brother ruined while she permanently misattributes the original cause.", "dread becoming bittersweet accomplishment", "She must solve the external crisis using incomplete beliefs while the reader understands the brother's hidden responsibility."),
            _spec("brother-agency", "His Quiet Repair", "The brother secretly helps her repair the disaster he caused without confessing, creating a second causal line the reader can track.", "tension becoming morally complicated relief", "He must aid her success without revealing the truth she is required never to learn."),
            _spec("institution", "The Official Cause", "An institution knowingly gives her a false but actionable explanation so she can solve the external problem while the reader sees the protected brother behind it.", "frustration becoming uneasy resolution", "She must beat the institutional obstacle without uncovering the protected family truth."),
        ),
        "dramatic-irony",
        "The dramatic-irony engine satisfies the hard knowledge boundary while still allowing a complete external arc and meaningful reader superiority.",
    ),
    NaturalisticCase(
        "A2",
        "author-boundary",
        "No redemption arc for the tyrant: the story may explain him, but must never excuse him or make forgiveness the hero's victory.",
        (
            _spec("accountability", "The Cost of Understanding", "The hero learns exactly how the tyrant became cruel and uses that knowledge to dismantle his power without forgiving him.", "anger becoming lucid resolve", "Understanding creates strategic leverage but never converts accountability into absolution."),
            _spec("inheritance", "After the Throne", "The conflict centers on institutions built around the tyrant, so defeating him requires refusing the systems that would reproduce him.", "oppression becoming wary agency", "The hero must end the tyrant's rule and reject the tempting structures that explain how such rule persists."),
            _spec("witness", "No Pardon", "The hero's victory is preserving testimony the tyrant cannot rewrite, even when political peace pressures survivors to forgive.", "grief becoming defiant memory", "The hero must secure truth and justice while refusing reconciliation as the price of closure."),
        ),
        "accountability",
        "The accountability engine uses explanation as strategic knowledge while making the no-redemption/no-forgiveness boundary structurally explicit.",
    ),
    NaturalisticCase(
        "A3",
        "author-boundary",
        "A time-travel story where history cannot be changed; the protagonist can only change what the trip means to the people who remember it.",
        (
            _spec("witness", "Fixed Point", "The traveler returns to an unchangeable tragedy to recover testimony that changes how survivors understand it.", "helplessness becoming meaningful witness", "The traveler cannot prevent events and must instead decide what truth to carry back and whom it can help."),
            _spec("relationship", "The Same Goodbye", "Repeated visits cannot alter a loved one's death but can alter the traveler's final conversations and the memories shared afterward.", "grief becoming chosen tenderness", "The traveler must stop treating time as a rescue mechanism and use fixed encounters to transform present relationships."),
            _spec("legacy", "Annotations", "The traveler leaves no changes in history but creates a present-day archive explaining why forgotten choices mattered.", "curiosity becoming custodial purpose", "The trip cannot alter events, only the interpretive legacy available to people who remember them."),
        ),
        "witness",
        "The witness engine most directly turns immutable history from a limitation into the causal source of the protagonist's transformation.",
    ),
)


class _SyntheticProvider:
    def __init__(self, specs: tuple[CandidateSpec, ...], preferred_key: str, rationale: str):
        self._generation = list(specs)
        self._preferred_key = preferred_key
        self._rationale = rationale
        self.judge_requests = []
        self._generation_index = 0

    def complete(self, request):
        if "comparative narrative architect" in request.system:
            self.judge_requests.append(request)
            payload = json.loads(request.user.split("SURVIVING CANDIDATE EVIDENCE\n", 1)[1])
            by_title = {item["story_identity"]["title"]: item["candidate_id"] for item in payload}
            preferred = next(spec for spec in self._generation if spec.key == self._preferred_key)
            winner = by_title[preferred.title]
            rejected = {
                item["candidate_id"]: f"Synthetic contrast: {item['story_identity']['title']} optimizes a different tradeoff."
                for item in payload
                if item["candidate_id"] != winner
            }
            return LLMResponse(
                text=json.dumps(
                    {
                        "recommended_candidate_id": winner,
                        "recommendation_rationale": self._rationale,
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

        spec = self._generation[self._generation_index]
        self._generation_index += 1
        basis = "genre_aligned"
        if "best_basis: 'emotionally_powerful'" in request.system:
            basis = "emotionally_powerful"
        elif "best_basis: 'structurally_coherent'" in request.system:
            basis = "structurally_coherent"
        data = {
            "title": spec.title,
            "core_answer": spec.core_answer,
            "target_experience": {
                "primary": spec.primary,
                "progression": f"{spec.primary} -> pressure -> transformed understanding",
                "avoid": ["emotional flatness"],
            },
            "story_type": {
                "medium": spec.medium,
                "mode": spec.mode,
                "genre": spec.genre,
                "subgenres": [],
                "target_audience": "adult",
                "length_class": None,
            },
            "central_engine": {
                "want": spec.want,
                "resistance": spec.resistance,
                "conflict": spec.conflict,
                "stakes": spec.stakes,
                "change": spec.change,
            },
            "not_this": ["a generic version that ignores the premise mechanism"],
            "open_questions": ["Which concrete scene best demonstrates the engine?"],
            "confidence": spec.confidence,
            "alternatives": ["Synthetic alternative metadata excluded from judge evidence."],
            "recommendation_mode": "open_ended",
            "best_basis": basis,
            "why_this_is_best": spec.why,
            "rejected_directions": ["Synthetic rejected direction excluded from judge evidence."],
            "author_overrides": [],
        }
        return LLMResponse(
            text="```yaml\n" + yaml.safe_dump(data, sort_keys=False) + "```",
            input_tokens=1,
            output_tokens=1,
        )


def _args(tmp_path: Path, case: NaturalisticCase, *, output_name: str = "story_discovery"):
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


@pytest.mark.parametrize("case", NATURALISTIC_CASES, ids=lambda c: c.case_id)
def test_phase_d_naturalistic_cases_use_real_story_discovery_path(case, tmp_path, monkeypatch, capsys):
    provider = _SyntheticProvider(case.candidates, case.preferred_key, case.rationale)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: provider)

    exit_code = dispatch_story_discovery_recommend(_args(tmp_path, case))
    output = capsys.readouterr().out

    assert exit_code == 0
    assert len(provider.judge_requests) == 1
    for spec in case.candidates:
        assert spec.title in output
    preferred = next(spec for spec in case.candidates if spec.key == case.preferred_key)
    assert f"RECOMMENDED — {preferred.title}" in output
    assert "Nothing has been accepted yet." in output
    assert not (tmp_path / "story_identity.yaml").exists()
    discovery_set = yaml.safe_load(
        (tmp_path / "story_discovery" / "discovery_set.yaml").read_text(encoding="utf-8")
    )
    assert discovery_set["recommended_candidate_id"] in {"candidate_1", "candidate_2", "candidate_3"}


def _dumpable_candidate(candidate_id: str, spec: CandidateSpec, *, fit: int = 80, advocacy: str = "baseline"):
    class Dumpable(SimpleNamespace):
        def model_dump(self, mode="json"):
            return dict(self.__dict__)

    identity = SimpleNamespace(
        title=spec.title,
        core_answer=spec.core_answer,
        target_experience=Dumpable(primary=spec.primary, progression="a -> b -> c", avoid=[]),
        story_type=Dumpable(genre=spec.genre, medium=spec.medium, mode=spec.mode),
        central_engine=Dumpable(
            want=spec.want,
            resistance=spec.resistance,
            conflict=spec.conflict,
            stakes=spec.stakes,
            change=spec.change,
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
    case = NATURALISTIC_CASES[0]
    baseline = [
        _dumpable_candidate(f"candidate_{i}", spec, advocacy="BASELINE SELF ADVOCACY")
        for i, spec in enumerate(case.candidates, 1)
    ]
    mutated = [
        _dumpable_candidate(f"candidate_{i}", spec, advocacy="MUTATED SELF ADVOCACY SHOULD NOT LEAK")
        for i, spec in enumerate(case.candidates, 1)
    ]

    first = _build_judge_request(case.premise, baseline, genre=None, medium=None, mode=None)
    second = _build_judge_request(case.premise, mutated, genre=None, medium=None, mode=None)

    assert first.user == second.user
    assert "SELF ADVOCACY" not in first.user


@pytest.mark.parametrize("order", [(0, 1, 2), (2, 0, 1), (1, 2, 0)])
def test_phase_d_candidate_order_preserves_content_defined_winner(order, tmp_path, monkeypatch, capsys):
    original = NATURALISTIC_CASES[1]
    reordered = replace(original, candidates=tuple(original.candidates[i] for i in order))
    provider = _SyntheticProvider(reordered.candidates, reordered.preferred_key, reordered.rationale)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: provider)

    assert dispatch_story_discovery_recommend(_args(tmp_path, reordered, output_name=f"order_{''.join(map(str, order))}")) == 0
    output = capsys.readouterr().out
    preferred = next(spec for spec in reordered.candidates if spec.key == reordered.preferred_key)
    assert f"RECOMMENDED — {preferred.title}" in output
    assert not (tmp_path / "story_identity.yaml").exists()


def test_phase_d_candidate_id_remap_preserves_content_mapping():
    case = NATURALISTIC_CASES[2]
    ids = ["candidate_3", "candidate_1", "candidate_2"]
    outputs = [_dumpable_candidate(candidate_id, spec) for candidate_id, spec in zip(ids, case.candidates)]
    request = _build_judge_request(case.premise, outputs, genre=None, medium=None, mode=None)
    evidence = json.loads(request.user.split("SURVIVING CANDIDATE EVIDENCE\n", 1)[1])
    title_to_id = {item["story_identity"]["title"]: item["candidate_id"] for item in evidence}
    preferred = next(spec for spec in case.candidates if spec.key == case.preferred_key)
    assert title_to_id[preferred.title] == ids[list(case.candidates).index(preferred)]


def test_phase_d_high_contract_fit_is_evidence_not_a_deterministic_winner():
    case = NATURALISTIC_CASES[3]
    high = _dumpable_candidate("candidate_1", case.candidates[0], fit=100)
    lower = _dumpable_candidate("candidate_2", case.candidates[1], fit=60)
    request = _build_judge_request(case.premise, [high, lower], genre="mystery", medium=None, mode=None)
    assert '"contract_fit": 100' in request.user
    assert '"contract_fit": 60' in request.user
    assert "A higher contract-fit number does not automatically win." in request.system


def test_phase_d_exact_duplicate_is_rejected_but_semantic_near_duplicate_is_known_limitation():
    base = NATURALISTIC_CASES[4].candidates[0]
    exact_a = _dumpable_candidate("candidate_1", base)
    exact_b = _dumpable_candidate("candidate_2", base)
    with pytest.raises(ValueError, match="exact duplicates"):
        _require_distinct_engines([exact_a, exact_b])

    near = replace(
        base,
        want=base.want.replace("pursue", "seek"),
        resistance=base.resistance.replace("makes", "renders"),
        conflict=base.conflict + " in essentially the same causal pattern",
        stakes=base.stakes.replace("permanently destroys", "irreversibly ruins"),
        change=base.change.replace("adopts", "embraces"),
    )
    _require_distinct_engines([exact_a, _dumpable_candidate("candidate_2", near)])


def test_phase_d_explicit_constraints_remain_visible_to_comparative_judge():
    case = NATURALISTIC_CASES[6]
    outputs = [
        _dumpable_candidate(f"candidate_{i}", spec)
        for i, spec in enumerate(case.candidates[:2], 1)
    ]
    request = _build_judge_request(
        case.premise,
        outputs,
        genre="mystery",
        medium="novella",
        mode="dramatic",
    )
    assert '"genre": "mystery"' in request.user
    assert '"medium": "novella"' in request.user
    assert '"mode": "dramatic"' in request.user
    assert case.premise in request.user


def test_phase_d_judge_schema_requires_complete_rejection_coverage(tmp_path, monkeypatch, capsys):
    case = NATURALISTIC_CASES[7]
    provider = _SyntheticProvider(case.candidates, case.preferred_key, case.rationale)
    original_complete = provider.complete

    def malformed(request):
        if "comparative narrative architect" in request.system:
            return LLMResponse(
                text=json.dumps(
                    {
                        "recommended_candidate_id": "candidate_1",
                        "recommendation_rationale": "Incomplete synthetic judgment.",
                        "rejected_candidate_reasons": {"candidate_2": "Only one rejection."},
                    }
                ),
                input_tokens=1,
                output_tokens=1,
            )
        return original_complete(request)

    provider.complete = malformed
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: provider)
    assert dispatch_story_discovery_recommend(_args(tmp_path, case)) == 1
    err = capsys.readouterr().err
    assert "rejection reasons must cover exactly every non-selected survivor" in err
    assert not (tmp_path / "story_identity.yaml").exists()


def test_phase_d_authority_gate_recommendation_never_promotes_canonical_identity(tmp_path, monkeypatch):
    case = NATURALISTIC_CASES[-1]
    provider = _SyntheticProvider(case.candidates, case.preferred_key, case.rationale)
    monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **k: provider)
    assert dispatch_story_discovery_recommend(_args(tmp_path, case)) == 0
    assert (tmp_path / "story_discovery" / "comparison.md").exists()
    assert not (tmp_path / "story_identity.yaml").exists()
