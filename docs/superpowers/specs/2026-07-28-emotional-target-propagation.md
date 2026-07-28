# Emotional-Target Propagation Specification

## Status

Proposed / awaiting approval. Specification-only; no implementation is included.

## Problem

`GenreProfileCommitment.accepted_target_emotions` is a weighted mapping accepted through the Genre Profile process, but it currently disappears during Blueprint compilation. Authored emotional intent is already preserved. This slice makes the profile commitment visible without merging it into authored intent or claiming fulfillment.

## Proven current behavior

`accepted_target_emotions: dict[str, float]` defaults to an empty mapping. The repository does not define whether weights mean priority, intensity, confidence, probability, proportion, or recommendation strength; this specification preserves them opaquely.

`StoryIdentity.target_experience` is author-owned and includes the primary emotional promise, secondary palette, avoided experiences, progression, trajectory, genre-emotion stack, and POV experience contracts. Compilation copies it to `StoryBlueprint.identity.target_experience`. `EmotionalBlueprint` derives per-act display tones from that authored value. Accepted profile emotions currently reach neither Blueprint nor `ProfileDerivation`.

## Emotional concept inventory

| Concept | Model | Authority | Consumer | Status |
|---|---|---|---|---|
| Primary promise | `TargetExperience.primary_emotional_promise` | Author | Emotional Blueprint / structure | Propagated |
| Secondary palette | `TargetExperience.secondary_palette` | Author | Target model | Propagated |
| Avoidance | `TargetExperience.avoided_experiences` | Author | Identity/structure checks | Propagated |
| Progression/trajectory | `TargetExperience.progression`, `emotional_trajectory` | Author | Emotional Blueprint / target model | Propagated |
| Per-act tones | `EmotionalBlueprint.per_act_tones` | Derived | Blueprint consumers | Authored-intent derivative |
| Ending tone | `AuthorAudienceContract.mandatory_ending_tone` | Contract | Resolution diagnostics | Distinct |
| Accepted target emotions | `GenreProfileCommitment.accepted_target_emotions` | Profile-derived, author-accepted | None | Stranded |

Tone, mood, trajectory, ending tone, and profile target emotions are distinct. No weight semantics are inferred.

## Authority boundary

Authored emotional design flows from `StoryIdentity.target_experience` to `StoryBlueprint.identity.target_experience` and then to `EmotionalBlueprint`. Accepted profile obligations flow from `GenreProfileCommitment.accepted_target_emotions` to `StoryBlueprint.contract.profile_emotional_targets` and `ProfileDerivation`.

The former is explicitly author-owned. The latter is profile-derived and author-accepted. Neither source overwrites, mutates, merges with, or suppresses the other.

## Domain distinctions

- Emotion is a felt state such as dread, hope, grief, awe, relief, tenderness, or triumph.
- Audience experience is a broader intended effect that may include cognition, tension, identification, uncertainty, or moral discomfort.
- Tone is expressive attitude or atmosphere; mood is sustained affective atmosphere.
- Emotional arc/trajectory is ordered change over time; ending tone is the quality of resolution.
- Profile emotional targets are weighted profile expectations whose weight meaning is currently undefined.

## Non-goals

No emotional arc/intensity model, sentiment analysis, synonym matching, planner or scene consumption, reconciliation, diagnostics, posture behavior, migration, new Genre Packs, compilation blocking, CLI changes, package changes, or release work. Existing rejected-outcome and forbidden-trope behavior remains untouched.

## Options considered

Reusing `target_experience` was rejected because it would erase authority and require undefined merge and weight semantics. A top-level `StoryBlueprint.profile_emotional_targets` was rejected because it promotes a source-specific commitment to the root and encourages root schema growth. A new profile-obligations submodel or structured target objects were deferred as unnecessary abstractions without a proven consumer.

## Selected destination

Add to `AuthorAudienceContract`, beside existing audience-facing contract obligations:

```python
profile_emotional_targets: dict[str, float] = Field(default_factory=dict)
```

`profile_emotional_targets` belongs to `AuthorAudienceContract` because it represents audience-facing obligations accepted through the Genre Profile process. The `profile_` prefix and `ProfileDerivation` provenance preserve source authority without promoting source-specific commitments to the `StoryBlueprint` root.

## Field name and schema contract

- Name/type: `profile_emotional_targets: dict[str, float]`.
- Default: repository-safe `default_factory=dict`.
- Keys and values: preserve the source contract exactly; no new vocabulary, enum, case folding, whitespace normalization, synonym map, rounding, normalization, ranking, or interpretation.
- Duplicate keys: ordinary mapping parsing applies.
- Malformed/non-finite values: source validation remains authoritative; the destination adds no incompatible rule.
- Ordering: repository mapping serialization convention; no semantic ordering.
- Empty mapping: deterministic empty mapping and no emotional provenance.
- Serialization/equality/schema: normal Pydantic YAML/JSON serialization, equality, and additive generated schema behavior.
- Legacy loading: absent field loads as an empty mapping.

## Ownership and authority

`target_experience` remains author-owned. `profile_emotional_targets` remains profile-derived and author-accepted. A copied profile value does not become authored intent, and authored intent does not become profile evidence.

## Coexistence policy

```text
identity.target_experience
and
author_audience_contract.profile_emotional_targets
coexist without reconciliation
```

The same emotion may occur in both. There is no cross-source deduplication, precedence, weight transfer, filling of authored fields, or conflict resolution. Apparent duplication records two independent facts: direct author design and accepted profile recommendation.

## Compilation behavior

```text
contract.profile_emotional_targets = {}
if identity.genre_profile exists and accepted_target_emotions is non-empty:
    contract.profile_emotional_targets = exact mapping copy(accepted_target_emotions)
    record one provenance obligation per emotion and weight
compile with identity.target_experience unchanged
```

No profile or an empty mapping produces no emotional provenance. Profile targets must not populate primary promise, secondary palette, avoidance, progression, trajectory, ending tone, per-act tones, required outcomes, rejected outcomes, or forbidden tropes. Repeated compilation is deterministic and idempotent; it does not mutate `StoryIdentity`, duplicate provenance, or drift weights.

## Provenance

Reuse `ProfileDerivation`; do not redesign it. Prefer one entry per emotion/weight for inspectability and future targeted identity. Each entry identifies source field `genre_profile.accepted_target_emotions`, the emotion key, opaque weight, destination `contract.profile_emotional_targets.<emotion>`, and applied state. Existing source profile, recommendation ID, and accepted commitment remain inspectable.

## Override behavior

Implementation must inspect existing override infrastructure for stable per-emotion identity. If it supports safe targeting, only the targeted profile obligation may be skipped and unrelated targets remain copied. If it does not, override support is deferred: all accepted targets are copied and no global text suppression or new override system is introduced.

## Serialization and inspection

```yaml
contract:
  profile_emotional_targets:
    dread: 0.9
    fascination: 0.7
identity:
  target_experience:
    primary_emotional_promise: dread
```

Normal complete Blueprint serialization and inspection should expose the field automatically. Authored intent remains separate. Existing files are not rewritten or migrated, and no unintended `null` is introduced.

## Downstream consumption

Required: compilation, `ProfileDerivation`, YAML/JSON serialization, and ordinary complete-Blueprint inspection. Deferred: `EmotionalBlueprint`, outline/beat/scene planning, revision recommendations, diagnostics, posture severity, and prompt injection. Representation is valuable because the accepted commitment currently disappears; it is not evidence of operational fulfillment.

## Diagnostics

No `D-EMO` diagnostic and no changes to D-RES-001/002/003, posture severity, CLI exits, or compilation blocking. Fulfillment is not objectively measurable while weights lack semantics and no downstream consumer defines success. Future diagnostics require defined weight semantics, deterministic consumption, compatibility rules, repair guidance, approved posture policy, and stable obligation identity.

## Adherence-posture interaction

Posture does not affect storage, propagation, provenance, or severity in this slice. Future emotional diagnostics require a separately approved policy rather than inheriting resolution severity by analogy.

## Backward compatibility

Legacy Blueprints without the field load with an empty mapping. Existing authored target experience and EmotionalBlueprint behavior remain unchanged. Existing accepted profiles may populate the field only when newly compiled; existing serialized Blueprints are not rewritten. No-profile projects retain current behavior and have no emotional provenance. Unknown labels and weights follow source validation. The additive field requires no migration framework or schema-version bump under current conventions.

## Counterfactual acceptance tests

1. No profile: empty field, unchanged authored target, no emotional provenance.
2. One target `{"dread": 0.9}`: exact mapping, weight, and destination provenance.
3. Multiple targets: all values preserved, deterministic serialization, round trip.
4. Authored plus profile intent: authored promise, palette, avoidance, progression, and trajectory unchanged.
5. Same emotion in both: both inspectable; no cross-source deduplication.
6. Empty accepted mapping: empty field and no false provenance.
7. Repeated compilation: no duplicate provenance or weight drift.
8. Legacy Blueprint: loads with empty field; no inferred migration.
9. YAML/JSON round trip: exact weighted mapping and authority separation.
10. EmotionalBlueprint and ending tone: unchanged.
11. D-RES-001/002/003: unchanged.
12. Profile emotions do not enter required/rejected outcomes or forbidden tropes.
13. All postures: storage identical.
14. Weight fidelity: no rounding, normalization, ranking, or interpretation.
15. Overrides follow the supported/deferred policy without broad suppression.

## Implementation surface

| Component | Intended change | Risk | Required |
|---|---|---:|---:|
| `src/auteur/blueprint.py` | Add contract field | Low | Yes |
| `src/auteur/identity.py` | Copy mapping and record provenance | Medium | Yes |
| `ProfileDerivation` | Reuse existing model; no redesign | Low | Maybe |
| Propagation/round-trip tests | Add authority, fidelity, provenance, and compatibility cases | Low | Yes |
| EmotionalBlueprint tests | Regression guard only | Low | Yes |

Remain untouched: Genre Profile source model unless validation exposes a gap; EmotionalBlueprint implementation; structure analyzer; profile severity policy; D-RES diagnostics; CLI exit logic; rejected-outcome/forbidden-trope code; package version; release metadata.

## Delivery sequence

1. Approve this specification.
2. Inspect override identity and serializer behavior.
3. Add failing tests.
4. Implement field, compiler copy, and provenance.
5. Run focused compatibility/regression tests.
6. Qualify the new candidate SHA fully.

## Risks

The contract location could be mistaken for authored data; the `profile_` prefix and provenance must remain explicit. Undefined weights could invite accidental interpretation. Per-emotion provenance may not match current override identity; defer rather than suppress by ambiguous text. Additive serialization may require inspected snapshot updates.

## Open decisions

- Whether existing override infrastructure safely targets one accepted emotion.
- Whether serializers emit empty mappings or omit them; follow existing convention.
- Future meaning of weights; out of scope until product evidence defines it.

## Recommendation

Approve a representation-only slice adding `AuthorAudienceContract.profile_emotional_targets: dict[str, float]` with per-emotion provenance. Preserve authored design unchanged, copy weights opaquely, use normal serialization, and defer overrides if stable per-emotion identity is unavailable. The specification is ready for implementation approval; implementation has not begun.
