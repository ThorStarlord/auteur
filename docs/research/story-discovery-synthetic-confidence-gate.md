# Phase D — Story Discovery Synthetic Product-Confidence Gate

## Status

Planned deterministic research gate. This extends the existing StoryIdentity simulation protocol and stress-simulation findings; it does not replace or reinterpret those results.

## Why this phase exists

The existing simulation work exercised facilitator-created StoryIdentity packets and identified useful handoff and anti-anchoring behavior, but it deliberately did not establish the quality of Story Discovery's recommendation-generation path.

Phase D closes a narrower gap that can be tested without live provider credentials: controlled synthetic creativity is fed through Auteur's actual merged Story Discovery mechanics — candidate parsing and validation, open-ended search packaging, bounded comparative-evidence construction, recommendation rendering, artifact serialization, workflow state, and authority boundaries.

The synthetic provider is the test double. Auteur is the system under test.

## Claim this phase may earn

If the gate passes, the strongest allowed claim is:

> Story Discovery has passed systematic synthetic product stress testing across naturalistic, adversarial, mutation, permutation, and authority-boundary scenarios. Under controlled provider outputs, the merged product mechanics preserve meaningful candidate distinctions, bounded comparative evidence, honest survivor semantics, stable authority boundaries, and non-canonical recommendation behavior.

## Claims this phase must not make

This phase does **not** establish:

- the quality or diversity of live Anthropic or OpenAI generations;
- that a live model will choose the same winner as the synthetic judge;
- usability or preference across a population of real writers;
- real-world recommendation acceptance rates;
- semantic near-duplicate detection beyond the product's current exact-force duplicate rule.

Live-provider semantic validation and independent human-writer validation remain deferred confidence layers.

## Research boundary

**Synthetic creativity, real product mechanics.**

Synthetic / controlled:

- candidate YAML returned by the provider double;
- summary responses;
- comparative-judge responses;
- deliberately adversarial candidate sets;
- one-variable mutations;
- candidate order and ID permutations.

Real Auteur mechanics:

- `dispatch_story_discovery_recommend()`;
- `handle_identity_recommend()` open-ended generation flow;
- `StoryIdentity` parsing and validation;
- deterministic contract-fit computation;
- exact central-engine duplicate rejection;
- bounded judge evidence construction;
- comparative judgment schema validation;
- `serialize_story_discovery()` artifact writing;
- recommendation/comparison rendering;
- no canonical `story_identity.yaml` before explicit acceptance.

The harness must not bypass generation by directly constructing final recommendation artifacts.

## Hypotheses

### H1 — Naturalistic search packaging

Across a compact benchmark of underdetermined, constraint-heavy, genre-promise, and author-boundary premises, three valid synthetic candidates can traverse the actual open-ended Story Discovery path and remain visibly distinct at the recommendation surface.

### H2 — Evidence isolation

Generation provenance and candidate self-advocacy do not enter the comparative judge's bounded evidence, while story commitments, explicit author constraints, validation status, and contract evidence remain available.

### H3 — Irrelevant-metadata invariance

Changing excluded self-advocacy/provenance fields must not change the judge request's story evidence.

### H4 — Order/ID robustness of the product contract

Permuting candidate order or candidate IDs must preserve candidate-content mapping, rejection coverage, and canonical non-mutation. The synthetic judge may map a content-defined preferred story to its current candidate ID, but no positional or lexical ID preference is allowed in the harness.

### H5 — Contract-fit non-dominance

A higher deterministic contract-fit value must remain compliance evidence rather than an automatic winner. The product must permit a lower-fit candidate to be selected when the synthetic comparative judgment prefers its causal/premise-specific architecture.

### H6 — Honest survivor semantics

One survivor is rendered as a viability result rather than an artistic winner; zero survivors produce recovery guidance rather than a recommendation.

### H7 — Authority invariance

No recommendation run, mutation, or permutation may create canonical `story_identity.yaml`. Explicit acceptance remains a separate author action.

## Benchmark design

### Naturalistic benchmark — 12 cases

Four premise classes, three cases each:

1. **Underdetermined** — sparse premises with several plausible narrative engines.
2. **Constraint-heavy** — premises where multiple candidates must remain distinct despite tight requirements.
3. **Strong genre promise** — premises where genre compliance matters but must not become a hidden quality rank.
4. **Author-boundary** — premises with unusual explicit requirements that should remain visible in the decision context.

The benchmark is intentionally deterministic. It tests the product contract under plausible controlled outputs, not provider creativity.

### Adversarial micro-cases

The automated suite must cover at least these failure hypotheses:

- exact duplicate central-engine forces;
- semantic-near-duplicate candidates that are not exact duplicates;
- high-contract-fit loser;
- premise-drift loser;
- attractive losing alternative;
- single survivor;
- zero survivors;
- malformed comparative-judge coverage;
- self-advocacy/provenance mutation;
- candidate order permutation;
- candidate-ID remapping;
- explicit author-constraint visibility;
- recommendation artifact without canonical promotion.

## Evaluation roles

The automated harness is not a human-subject simulation. It separates concerns instead:

- **Synthetic provider**: returns controlled candidate, summary, and comparative responses.
- **Product under test**: Auteur's merged Story Discovery path.
- **Blind fixture expectation**: identifies the content-defined preferred synthetic story without relying on candidate position or ID.
- **Adversarial assertions**: try to falsify invariants and expose leakage, positional dependence, or authority erosion.
- **Research audit**: aggregates pass/fail evidence and classifies any failure by subsystem.

A later founder review may inspect a small high-information sample, but founder taste is not encoded as an automated truth label.

## Hard gates

Phase D fails if any of the following occurs:

1. recommendation creates or implies canonical `story_identity.yaml` without explicit acceptance;
2. a one-survivor result is presented as comparative artistic superiority;
3. zero survivors result in a fabricated winner;
4. excluded generation self-advocacy appears in bounded judge evidence;
5. candidate ordering or ID remapping breaks content-to-recommendation mapping in the controlled harness;
6. contract fit becomes a deterministic winner rule;
7. explicit author constraints disappear from the comparative request.

## Research-health gates

The deterministic suite should demonstrate:

- 12/12 naturalistic cases complete through the actual Story Discovery recommendation path;
- all benchmark runs preserve non-canonical state;
- all order/ID permutation controls preserve content-defined winner mapping;
- all self-advocacy/provenance mutations leave bounded evidence unchanged;
- exact duplicates are rejected before comparative judgment;
- semantic near-duplicates are documented as a known current limitation rather than falsely rejected;
- high-contract-fit candidates can lose;
- single- and zero-survivor behavior remains honest and recoverable.

These are product-confidence thresholds, not population-level statistical claims.

## Failure classification

Any failing case should be classified as one of:

- **SEARCH CONTRACT FAILURE** — candidate packaging/distinction invariant failed;
- **EVIDENCE FAILURE** — inappropriate information entered or disappeared from judge evidence;
- **JUDGMENT CONTRACT FAILURE** — winner/rejection schema or mapping failed;
- **SURFACE FAILURE** — recommendation presentation misstates the underlying state;
- **AUTHORITY FAILURE** — recommendation crosses or obscures the canonical boundary;
- **KNOWN LIMITATION CONFIRMED** — expected limitation, especially semantic near-duplicate detection, is reproduced honestly.

## Decision after Phase D

If the gate is green, close the local synthetic confidence gap and move to the next product question without claiming live-provider or real-writer validation.

If failures cluster around search distinction, improve search. If they cluster around bounded evidence or comparative mapping, improve judgment plumbing. If mechanics are sound but the remaining uncertainty is creative quality, leave the architecture unchanged and treat live-provider/founder dogfood as the next optional confidence layer.
