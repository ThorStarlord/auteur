# Cartographer Profile Emotional-Target Evaluation

## Status

Draft / product evaluation. No live model evaluation was executed.

## Question

When otherwise identical planning inputs differ only by accepted profile emotional targets, does Cartographer produce useful, attributable outline differences while preserving authored emotional authority and avoiding invented weight semantics?

## Proven technical boundary

The implemented transport is:

`StoryBlueprint.contract.profile_emotional_targets` → `PlanningCall.for_chapter()` → `PlanningCall.profile_emotional_targets` → `render_cartographer_prompt()` → separate Cartographer planning-context section.

The field is additive with an empty mapping default. Values are copied exactly, labels render alphabetically, the section heading is `## ACCEPTED PROFILE EMOTIONAL TARGETS`, the undefined-semantics disclaimer is fixed, and the section is omitted when empty. Authored `emotional_target` remains separate. The Cartographer output schema, EmotionalBlueprint, diagnostics, posture, and other planners are unchanged.

Transport success is proven by the merged implementation and tests. Behavioral influence, useful influence, and fulfillment are not proven by this evaluation.

## Evaluation methodology

The proposed evaluation would use 8–12 paired Blueprint scenarios, with control and treatment differing only in `profile_emotional_targets`. Each pair would capture the exact rendered prompts and Cartographer outlines, then receive ordinal ratings for attributable influence, authored-intent preservation, planning usefulness, coherence, genre/profile alignment, weight restraint, parroting, and authority separation.

Required case families include reinforcing targets, duplicate authored/profile emotions, distinct compatible targets, authored/profile tension, unusual labels, counterintuitive and reversed weights, no authored target where valid, strong authored targets with weakly related profile targets, and genre variation.

## Models and settings

The production path uses `build_client()` with Anthropic or OpenAI clients wrapped by `RetryingClient` (three retries). `compile_outline()` sends temperature `0.1` and max tokens `4000`. `LLMRequest` exposes no seed or top-p field, and the repository has no evaluation replay/cache harness for Cartographer outputs. Provider API keys and a fixed model/version were not available for a safe bounded run.

Therefore no provider, model, temperature-controlled output sample, cost, runtime, prompt pair, or outline result is claimed here. The evaluation stopped at the repository-defined stop condition rather than fabricating evidence from mocked outputs. Existing fake-client tests prove pipeline mechanics, not behavioral usefulness.

## Case inventory

| Case | Genre | Authored target | Profile targets | Repetitions | Main finding |
| --- | --- | --- | --- | ---: | --- |
| Planned R1 | varied | compatible | dread, fascination | 0 | Not evaluated |
| Planned R2 | varied | same emotion | dread | 0 | Not evaluated |
| Planned R3 | varied | grief | tenderness, awe | 0 | Not evaluated |
| Planned R4 | varied | austere restraint | hope, tenderness | 0 | Not evaluated |
| Planned R5 | varied | authored target | uncommon accepted label | 0 | Not evaluated |
| Planned R6 | varied | authored target | dread 0.2, tenderness 0.9 | 0 | Not evaluated |
| Planned R7 | varied | authored target | reversed values | 0 | Not evaluated |
| Planned R8 | varied | absent where valid | profile targets only | 0 | Not evaluated |

## Counterfactual controls

The required control is the same Blueprint with an empty mapping. The treatment changes only the accepted profile mapping. The exact prompt renderer can capture these paired prompts deterministically, but outline comparison requires a live provider or a deliberately fixed replay artifact; neither was available.

## Human review rubric

The planned ordinal scale is -2 clearly worse, -1 somewhat worse, 0 no meaningful difference, +1 somewhat better, and +2 clearly better. Reviewers would also record meaningful difference, attribution, harmful interference, suspected weight interpretation, and confidence. No ratings are reported because no paired outlines exist. Independent human review and blinded review were not performed.

## Results summary

| Measure | Result |
| --- | --- |
| Meaningful influence rate | Not estimable |
| Useful influence rate | Not estimable |
| Prompt-parroting rate | Not estimable |
| Weight interpretation | Not observed; no live outputs |
| Structural harm | Not observed; no live outputs |
| Authored-intent preservation | Transport-level separation only; behavioral result unknown |
| No-profile regression | PASS at prompt/transport level; behavioral output equivalence not tested |

## Pair-by-pair findings

None. Producing findings without paired model outputs would confuse prompt transport with behavioral influence.

## Weight-interpretation findings

None. The implementation preserves raw values and explicitly rejects semantics, but only repeated output comparisons could establish whether a model invents priority, intensity, allocation, or ranking semantics.

## Authored-intent preservation

The prompt preserves authored and profile authorities in separate sections. Whether a model respects that separation under tension is untested.

## Prompt-parroting findings

Not evaluated. Prompt text alone cannot establish whether an outline changes event sequencing, reveal timing, scene function, escalation, or payoff preparation.

## Structural usefulness

Not evaluated. An outline-level usefulness judgment requires paired outputs and a human rubric.

## Failure modes

No behavioral failure modes can be counted. The untested risks remain F1 no meaningful influence, F2 parroting, F3 authored-intent displacement, F4 weight interpretation, F5 generic genre inflation, F6 structural damage, F7 inconsistent effect, F8 excessive influence, F9 hallucinated semantics, and F10 beneficial bounded influence.

## Limitations

- No safe provider credentials or fixed provider/model were available.
- No deterministic seed, replay, or response cache is exposed by the Cartographer path.
- No live outline outputs or costs can be retained.
- One reviewer was not available; independent/blinded review was not performed.
- Fulfillment remains out of scope and is not inferred.

## GenreProfileCommitment inventory

| Commitment field | Represented in Blueprint | Provenance | Consumer | Validation | Status |
| --- | :---: | --- | --- | --- | --- |
| `primary_pack_id` | Yes | accepted genre profile | genre/profile tooling | Pydantic and profile validation | represented only |
| `primary_pack_version` | Yes | accepted genre profile | genre/profile tooling | Pydantic and profile validation | represented only |
| `pack_content_hash` | Yes | accepted genre profile | genre/profile tooling | Pydantic and profile validation | represented only |
| `primary_profile_id` | Yes | accepted genre profile | genre/profile tooling | Pydantic and profile validation | represented only |
| `secondary_genres` | Yes | accepted genre profile | genre/profile tooling | Pydantic and profile validation | represented only |
| `accepted_target_emotions` | Yes | accepted profile derivation, author acceptance | PlanningCall → Cartographer prompt | Pydantic and profile validation | transported; behavioral use unevaluated |
| `accepted_narrative_engine` | Yes | accepted genre profile | Blueprint/structure consumers | Pydantic and profile validation | represented only / deferred |
| `accepted_framing` | Yes | accepted genre profile | Blueprint/genre tooling | Pydantic and profile validation | represented only / deferred |
| `accepted_resolution_contract` | Yes | accepted genre profile | diagnostics and genre tooling | Pydantic and profile validation | represented / partially consumed |
| `adherence_posture` | Yes | author acceptance | diagnostics and posture policy | Pydantic and posture validation | behaviorally consumed by diagnostics |
| `source_recommendation_id` | Yes | recommendation provenance | persistence/inspection | Pydantic | provenance only |
| `author_overrides` | Yes | author action | profile/genre tooling | Pydantic | represented / deferred |
| `accepted_at` | Yes | acceptance event | persistence/inspection | Pydantic | provenance only |

The current weakest evaluated boundary is not transport; it is behavioral usefulness and traceability of Cartographer planning influence. A later evaluation should address that with a safe fixed provider or replayable model fixture.

## Options considered

| Decision option | Supporting evidence | Contrary evidence | Recommendation |
| --- | --- | --- | --- |
| Keep current consumer unchanged | Boundary is deterministic, bounded, and fully tested | Behavioral usefulness unmeasured | Recommended now |
| Refine prompt wording | Could help only if live evaluation finds inconsistency | No output evidence | Defer |
| Add planner-output traceability | Would make influence reviewable | No evidence yet that a field is needed | Consider after evaluation |
| Propagate to beat/scene planning | Could increase granularity | No outline-level usefulness evidence | Defer |
| Connect to EmotionalBlueprint | Would blur authored progression and accepted obligations | No deterministic reconciliation model | Strongly defer |
| Add diagnostics | Could assess later observable artifacts | Fulfillment is not deterministic here | Defer |
| Remove consumer | No demonstrated harm | Transport boundary is safe and tested | Do not remove without behavioral evidence |

## Recommendation

Keep the current Cartographer consumer unchanged. Do not implement another slice yet. First obtain a safe, fixed-provider or replayable evaluation environment and run the paired counterfactual study. The next evidence boundary should be output traceability only if repeated human-reviewed cases show useful, attributable influence that is not parroting, weight interpretation, or authored-intent displacement.

## Decision gate

**DEFER JUDGMENT.** No implementation change is justified by the current evidence. The technical transport is complete; behavioral usefulness remains unproven.

## Explicit answers

1. Does Cartographer respond to profile emotional targets? Transport is yes; behavioral response is unknown.
2. Are differences attributable to the new context? Not evaluated.
3. Are they useful at outline level? Not evaluated.
4. Does authored emotional intent remain authoritative? Prompt authority separation is preserved; model behavior is untested.
5. Does Cartographer interpret weights? No such behavior was observed; live evaluation is required.
6. Does it merely repeat emotional labels? Unknown.
7. Does the output schema need traceability? No evidence yet; defer.
8. Should prompt wording change? No.
9. Should context propagate to another planner? No, not yet.
10. Should EmotionalBlueprint change? No.
11. Are diagnostics justified? No.
12. What is the next weakest boundary? Behavioral usefulness and output traceability.
13. Is another implementation slice warranted? No; evaluation infrastructure or safe provider access is needed first.

No production behavior, prompts, schemas, diagnostics, tests, planners, package metadata, or release files were modified by this evaluation.
