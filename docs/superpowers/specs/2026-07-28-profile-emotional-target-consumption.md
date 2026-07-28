# Profile Emotional-Target Consumption Specification

## Status

Proposed / awaiting approval. Specification-only; no implementation is included.

## Problem

Accepted profile emotional targets are now persistently represented in
`StoryBlueprint.contract.profile_emotional_targets`, but no downstream system
receives them. The next safe boundary is a single canonical planning context,
without interpreting undefined weights or changing authored emotional intent.

## Proven current behavior

`PlanningCall.for_chapter()` is the centralized construction point for the
Cartographer chapter-planning input. It projects Blueprint fields into a
scope-aware `PlanningCall`. `render_cartographer_prompt()` is the centralized
renderer and emits stable labeled sections, including the existing authored
`EMOTIONAL TARGET` section. The Cartographer output is parsed separately and
its outline schema is unchanged by this proposal.

Current flow:

```text
StoryBlueprint
  -> PlanningCall.for_chapter()
  -> PlanningCall
  -> render_cartographer_prompt()
  -> Cartographer prompt
  -> unchanged outline output schema
```

Other observed consumers include Blueprint serialization/inspection, Bard
prompt rendering, critic prompts, structure analysis, and export. None is a
safer first consumer: some are downstream prose/critique paths, while the
Cartographer adapter is earlier, centralized, deterministic, and already
exposes authored emotional context.

## Consumer inventory

| Consumer | Current emotional input | Deterministic | First slice |
|---|---|---:|---:|
| Blueprint serialization/inspection | Full Blueprint | Yes | Already complete |
| `EmotionalBlueprint` | Authored target experience | Yes | Deferred |
| `PlanningCall.for_chapter()` | Per-act authored emotional target | Yes | Selected |
| `render_cartographer_prompt()` | `PlanningCall.emotional_target` | Yes | Selected |
| Cartographer output/parser | Fixed outline schema | No/LLM | Unchanged |
| Bard prompt | Outline and authored Blueprint context | No/LLM | Deferred |
| Critic prompts | Draft, outline, contract, Bible | No/LLM | Deferred |
| Structure analyzer | Blueprint structure and authored target | Yes | Diagnostics deferred |
| Scene/beat/revision paths | Existing artifacts | Mixed | Deferred |

## Authority boundary

Authored design remains:

```text
StoryIdentity.target_experience
  -> StoryBlueprint.identity.target_experience
  -> PlanningCall.emotional_target
  -> existing Cartographer emotional section
```

Accepted profile obligations become:

```text
StoryBlueprint.contract.profile_emotional_targets
  -> PlanningCall.profile_emotional_targets
  -> separately labeled Cartographer section
```

The two authorities remain independently labeled. There is no merge,
precedence, replacement, reconciliation, or cross-source deduplication. The
same emotion may occur in both sections.

## Meaning of consumption

This slice is context propagation plus bounded prompt consumption. It is not
enforcement or fulfillment evaluation. The Cartographer receives a labeled
planning consideration; no output field, score, or guarantee is added.

## Non-goals

Do not modify `AuthorAudienceContract`, `StoryIdentity.target_experience`,
`EmotionalBlueprint`, Cartographer output models/parsers, other planners,
diagnostics, adherence posture, planner schemas, CLI behavior, prompts outside
the Cartographer renderer, package metadata, or release files. Do not infer
emotional compatibility, assign emotions to acts, inject targets into Bard or
critic prompts, interpret weights, or claim fulfillment.

## Options considered

- Blueprint summary exposure: useful visibility but not operational planning
  context; already covered by serialization.
- EmotionalBlueprint metadata: would blur authored progression with profile
  obligations and imply a transformation that is not deterministic.
- Direct scene/beat/revision consumption: no single canonical adapter and
  broader behavioral risk.
- Fulfillment diagnostics: generated prose is nondeterministic, weights are
  undefined, and intentional divergence cannot be distinguished.
- No consumer: safest but leaves a stable, testable planning boundary unused.
- Cartographer context propagation: one adapter, one renderer, stable labels,
  directly testable prompt output, and no output-schema change. Selected.

## Selected first consumer

The first consumer is the Cartographer chapter-planning context:

- adapter: `PlanningCall.for_chapter()`;
- renderer: `render_cartographer_prompt()`;
- input: `StoryBlueprint.contract.profile_emotional_targets`;
- context field: `PlanningCall.profile_emotional_targets`;
- output change: one additive labeled prompt section only.

This boundary is preferred because it is centralized, deterministic, already
source-aware, and earlier than prose generation. No other planner is modified.

## PlanningCall contract

Add an optional-compatible field using the repository’s empty mapping
convention:

```python
profile_emotional_targets: dict[str, float] = Field(default_factory=dict)
```

The field is not a required constructor argument. Empty mapping and absent
profile targets have identical rendering behavior. Existing callers and
serialized PlanningCalls remain valid; no `null` or placeholder is rendered.

## Adapter behavior

`PlanningCall.for_chapter()` performs an exact mapping copy:

```text
call.profile_emotional_targets = dict(
    blueprint.contract.profile_emotional_targets
)
```

The adapter does not mutate the Blueprint or contract, normalize labels,
sort by weight, threshold, rank, deduplicate against `emotional_target`,
interpret values, depend on posture, or rewrite provenance. Repeated
construction is deterministic and idempotent.

## Prompt section contract

`render_cartographer_prompt()` emits the section after the existing authored
`EMOTIONAL TARGET` section and before `TENSION TARGET`:

```text
## ACCEPTED PROFILE EMOTIONAL TARGETS
dread: 0.9
fascination: 0.7
Numeric weights are preserved profile values; do not interpret them as
intensity, priority, probability, confidence, importance, proportion, or
fulfillment.
```

The heading is stable and explicitly profile-derived. The mapping is rendered
once. Empty mappings omit the heading, body, disclaimer, and surrounding blank
section. The authored section is not changed or combined with this section.

## Weight handling

Raw numeric values are passed through exactly. Presentation uses ordinary
string conversion and does not round, normalize, rank, threshold, clamp,
perform arithmetic, select a subset, or convert values to qualitative labels.

The minimal disclaimer is included because a prompt consumer might otherwise
invent semantics. It is a semantic guard, not a planning instruction and does
not tell the Cartographer to emphasize higher values.

## Deterministic ordering

Emotion labels are rendered alphabetically for stable presentation independent
of mapping construction order. This is presentation ordering only and must
not be described as semantic ranking. No ordering is applied to the Blueprint
mapping itself.

## Source and provenance labeling

The prompt exposes only the minimal source label and exact mapping. It does not
leak full `ProfileDerivation` internals, recommendation IDs, or timestamps.
Underlying provenance remains inspectable on the Blueprint. The section label
`ACCEPTED PROFILE EMOTIONAL TARGETS` distinguishes profile-derived,
author-accepted obligations from authored `EMOTIONAL TARGET` context.

## Behavioral limits

The Cartographer may consider the section as informational planning context. It
must not guarantee, maximize, satisfy, rank, or measure the emotions; replace
authored intent; resolve conflicts; or treat numeric values as importance or
intensity. The outline output cannot claim profile fulfillment in this slice.

## Empty and no-profile behavior

- No profile or absent mapping: no effective field values and no new prompt
  section; existing prompt behavior remains unchanged.
- Empty mapping: identical to no profile; no heading, blank section, or
  placeholder.
- Populated mapping: one deterministic section containing every key/value.
- Same authored/profile emotion: appears in both sections without annotation,
  deduplication, or precedence.
- Unknown labels: render exactly as accepted by the source model; no vocabulary
  transformation.

## Cartographer output-schema compatibility

No new outline key, fulfillment score, alignment field, checklist, parser rule,
schema version, or required response field is introduced. Only the input
context changes. Existing output models and parsing remain untouched.

## EmotionalBlueprint relationship

`EmotionalBlueprint` remains untouched. It continues to derive per-act tones
from authored target experience only. Profile context does not alter
progression, trajectory, ending tone, authored promise, palette, or per-act
tones.

## Diagnostics

No `D-EMO`, prompt-compliance, fulfillment, or compatibility diagnostic is
added. D-RES-001/002/003 and CLI exits remain unchanged. Transport does not
prove fulfillment; generated prose is nondeterministic, weight semantics are
undefined, intentional divergence is not objectively classifiable, and no
deterministic repair contract exists.

## Adherence-posture interaction

Posture does not affect whether context is transported, section wording,
ordering, weights, or planner behavior. No severity behavior is added.

## Backward compatibility

Legacy PlanningCall construction remains valid because the new field has an
empty default. Legacy Blueprints already load the additive profile mapping as
empty. No-profile prompts remain unchanged. Existing prompt snapshots change
only for populated profile targets. The Cartographer output parser and API
consumers remain compatible; no migration is required.

## Counterfactual acceptance tests

1. No profile: PlanningCall has no effective targets; prompt has no new heading.
2. Empty mapping: same prompt as no profile; no blank section.
3. One target: exact label and weight render; authored section unchanged.
4. Multiple targets: all values render alphabetically; no normalization/ranking.
5. Same emotion: both authored and profile sections contain it; no deduplication.
6. Weight fidelity: no intensity, priority, probability, confidence, or
   fulfillment language beyond the fixed disclaimer.
7. Repeated construction: identical PlanningCall and prompt.
8. Output schema: existing Cartographer output model remains unchanged.
9. EmotionalBlueprint: unchanged.
10. D-RES diagnostics: unchanged.
11. Posture invariance: identical field and prompt under every posture.
12. No mutation: Blueprint and contract unchanged after adapter/rendering.
13. Unknown label: exact source label preserved.
14. Source heading: stable and clearly profile-derived.
15. Only Cartographer: other planner renderers remain unchanged.

## Implementation surface

| File/component | Change | Risk | Required |
|---|---|---:|---:|
| `src/auteur/cartographer_models.py` | Add defaulted mapping and copy it in `for_chapter()` | Low | Yes |
| `src/auteur/cartographer.py` | Add conditional labeled section renderer | Low | Yes |
| Cartographer integration tests | Test adapter, prompt, ordering, omission, and invariants | Low | Yes |
| PlanningCall serialization tests | Regression guard for additive default | Low | Optional |
| Verification report | Record focused qualification | Low | Delivery |

Remain untouched: Blueprint and contract schemas; StoryIdentity; EmotionalBlueprint; structure analyzer; D-RES diagnostics; profile severity; Cartographer output schema/parser; Bard, critic, scene, beat, revision, and other planner renderers; package/release metadata.

## Delivery sequence

1. Approve this specification.
2. Add failing PlanningCall and renderer tests.
3. Add the defaulted context field and exact adapter copy.
4. Add the conditional labeled renderer section.
5. Run focused prompt/context and regression tests.
6. Qualify the resulting candidate SHA.

## Risks

Prompt changes can affect generated output even without changing the output
schema; deterministic prompt tests must constrain the surface. A disclaimer
could be mistaken for a semantic instruction, so it must remain fixed and
non-prescriptive. Alphabetic display ordering must not be interpreted as
ranking. Updating only the canonical Cartographer path avoids inconsistent
multi-planner behavior.

## Open decisions

- Whether future product evidence gives weights a defined meaning.
- Whether a later planner should consume the same labeled context.
- What deterministic evidence and repair contract would justify emotional
  diagnostics.

## Recommendation

Approve a single context-only consumer: add an empty-default
`PlanningCall.profile_emotional_targets`, populate it from the Blueprint in
`PlanningCall.for_chapter()`, and render one separately labeled section in
`render_cartographer_prompt()`. Preserve exact raw values, omit the section
when empty, keep authored emotional context independent, leave the Cartographer
output schema unchanged, and modify no other planner. This is the smallest
operational slice that transports accepted profile obligations without
inventing semantics or claiming fulfillment.
