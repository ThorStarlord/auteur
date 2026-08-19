# Phase F — Intent-Aware Story Discovery Architecture

## Status

**Ready for implementation planning.** Phase E founder creative adjudication merged via PR #93 at merge commit `2b6db623e7c1fe8678def87922cbe040d14049b8`.

Umbrella issue: #94.

This document is the bounded implementation roadmap. Production work should be split into separate PRs for F1–F4; F5 remains optional until those slices are qualified.

## Product thesis

> Story Discovery should recommend against declared author intent, search across causally distinct narrative architectures, and explain how each architectural choice changes the story the author will actually write.

Phase F converts the qualified Phase E findings into production slices. It does not reopen the Phase E research question and it does not relax the author-acceptance authority boundary.

## Evidence basis

Phase E identified seven repeated requirements:

1. raw-premise exploration and intent-aware comparative recommendation are different modes;
2. candidate diversity must be causal, not merely rhetorical;
3. Auteur lacks first-class authorial narrative-architecture preference vocabulary;
4. the existing rich `TargetExperience` ontology should be collected and exposed rather than duplicated;
5. recommendation tradeoffs should teach craft-layer propagation;
6. alternatives may be composable under a legible primary engine;
7. explicit author acceptance remains the canonical boundary.

## Architecture placement

Do **not** create a new semantic layer.

Use Auteur's existing semantic architecture:

- **Layer 0 — Ontology:** defines narrative-architecture preference concepts and relationships.
- **Layer 1 — Identity:** records author commitments to those preferences and target experience.
- **Layer 2 — Structure:** realizes those commitments as threads, causal systems, beats, reversals, and plans.
- **Layer 3 — Realization:** concrete events embody those causal interactions.
- **Layer 4 — Expression:** renders the realized events in prose.

---

# F1 — Architecture-preference ontology + Identity contract

## Goal

Give Auteur a first-class, optional vocabulary for the author's preferred shape of narrative complexity.

## Initial ontology hypothesis

```yaml
architecture_preferences:
  complexity: maximalist
  causal_distribution: mixed
  engine_hierarchy: primary_with_layers
```

Candidate vocabularies:

```text
ComplexityPreference
- focused
- layered
- maximalist

CausalDistributionPreference
- concentrated
- layered
- mixed

EngineHierarchyPreference
- single_center
- primary_with_layers
- ensemble
```

The exact names are hypotheses, not frozen API. Prefer terms that are understandable to authors and map cleanly onto ontology concepts.

## Placement

The concepts belong to Ontology; an accepted story's selected values belong to Story Identity.

Do not place them in:

- `StoryType`;
- `TargetExperience`;
- premise prose;
- generation provenance.

## Compatibility requirements

- all fields optional;
- unspecified remains genuinely unspecified;
- old StoryIdentity YAML continues to parse unchanged;
- round-trip serialization preserves explicit preferences;
- blueprint seeding does not invent preferences when absent;
- existing authority / acceptance behavior remains unchanged.

## Tests

- parse old identities without new fields;
- parse and serialize each explicit enum value;
- preserve unknown/omitted state;
- accept a Story Discovery candidate and preserve preferences in canonical `story_identity.yaml`;
- verify no default silently converts an unspecified preference into focused, layered, or maximalist.

---

# F2 — Structured Discovery Brief + intent adequacy

## Goal

Separate exploratory premise search from recommendation against declared author intent.

## Product modes

```text
RAW PREMISE
→ exploratory Story Discovery
→ “What could this premise become?”

DECLARED DISCOVERY BRIEF
→ intent-aware Story Discovery
→ “Which direction best serves the story I say I want to write?”
```

## Discovery-brief hypothesis

```yaml
premise: A family inherits a house that loses one room every night.

story_type:
  genre: supernatural_horror
  target_audience: adult

target_experience:
  primary_emotional_promise: claustrophobic_dread
  secondary_palette:
    - curiosity
    - grief
    - familial_tenderness
  emotional_trajectory:
    start: unease
    midpoint: confinement
    ending: disturbing_catharsis

architecture_preferences:
  complexity: maximalist
  causal_distribution: mixed
  engine_hierarchy: primary_with_layers

hard_constraints:
  - the shrinking is genuinely supernatural
  - inheritance must matter
```

## Important distinction

Do not duplicate `TargetExperience`. Use the existing rich model:

- primary emotional promise;
- secondary emotional palette;
- emotional trajectory;
- avoided experiences;
- genre-emotion stack and POV contracts where relevant.

Candidate-generated target experience, genre, audience, or preferences must remain distinguishable from **prior author intent**.

## Behavior

- raw premise remains valid for exploration;
- intent-aware comparative language does not pretend to know an under-specified optimization target;
- explicit author constraints remain hard unless overridden;
- the judge receives declared intent distinctly from candidate-generated proposals;
- missing optional fields do not create fake commitments;
- accepted candidates preserve selected Identity commitments.

## Tests

- raw-premise flow remains backward-compatible and non-canonical;
- structured brief reaches search/judgment evidence;
- author-intent fields remain distinguishable from candidate outputs;
- missing optional fields stay unspecified;
- acceptance preserves selected commitments.

---

# F3 — Causal-distinctness search + comparative evidence

## Goal

Make Story Discovery alternatives differ in the story the author would actually write, not merely in framing.

## Derived causal profile

A candidate should be describable for search/reasoning purposes with evidence such as:

```yaml
causal_profile:
  primary_strategy: institutional_entrapment
  causal_owner: ensemble
  external_action_pattern:
    - schedule
    - trigger
    - constrain
    - force_choice
  pressure_system: conflicting institutional obligations
  climax_mechanic: antagonist forced to violate one of his own rules
```

This profile is initially **derived search/reasoning evidence**, not automatically a new canonical Identity contract.

## Diversity criterion

Two candidates are not sufficiently distinct merely because they have different titles, themes, metaphors, or stated advantages.

Prefer candidates that differ materially in:

- primary causal strategy;
- causal ownership;
- protagonist action pattern;
- pressure system;
- reversal mechanics;
- climax mechanics.

Practical diagnostic:

> If choosing Candidate B instead of Candidate A would not materially change the major scenes the author writes, the engines may not be distinct enough.

## Keep existing safeguards

Retain exact normalized central-engine tuple duplicate rejection as deterministic compliance evidence. Do not pretend deterministic tuple checks solve semantic near-duplicate detection.

## Tests

- rhetorical paraphrases fail the controlled semantic-diversity gate;
- genuinely different causal strategies survive even when theme/setting overlap;
- candidate order/ID permutation preserves content mapping;
- explicit constraints remain visible and binding;
- contract fit remains compliance evidence, not artistic-quality score;
- one/zero survivor semantics remain unchanged.

---

# F4 — Craft-teaching recommendation surface

## Goal

Make Auteur explain not only **which** direction it recommends but **what the decision changes in the craft of the story**.

## Recommended alternative block

For each recommendation / alternative, expose where relevant:

```text
WHAT CHANGES
Which craft layer moves?

CAUSAL EFFECT
Who or what gains causal ownership?

WHAT YOU WILL WRITE MORE OF
Which protagonist verbs and scene families increase?

PRESSURE / STORY TEXTURE
What recurring experience fills the book?

READER-EXPERIENCE SHIFT
How does the primary emotional promise, secondary palette,
or emotional trajectory change?

THEMATIC EFFECT
What different meaning does the causal pattern imply?

WHAT YOU GAIN
What becomes stronger?

WHAT YOU GIVE UP
Where does narrative weight move away from?

COMPOSABILITY
Can the mechanism be borrowed as a subordinate layer?

PRIMARY RISK
What would cause this alternative/layer to displace the intended primary engine?
```

## Craft propagation model

```text
craft layer changed
→ causal ownership / protagonist verbs
→ scene families + pressure
→ story texture / aesthetic framing
→ reader experience
→ thematic implication
```

## Emotional hierarchy

Use the existing target-experience vocabulary. Do not create parallel “primary emotion” fields.

The surface should distinguish:

- target audience = **who**;
- primary emotional promise = governing reader experience;
- secondary palette = supporting/contrasting feelings;
- emotional trajectory = macro change over time.

## Tests

- expose primary + relevant secondary/trajectory information when present;
- omitted optional emotional fields do not produce invented copy;
- alternatives identify concrete craft-layer shifts rather than generic “more intimate / more complex” prose;
- output remains advisory and non-canonical;
- exact accept/review commands remain correct.

---

# F5 — Optional composition workflow

## Goal

After F1–F4 are qualified, allow the author to keep a recommended primary engine while borrowing compatible subordinate mechanisms from alternatives.

Example:

```text
Auteur:
I recommend Between Floors.

Author:
Keep it, but borrow the false-identity layer from Sixth Passenger
and the concealment layer from All Doors Closed.

Auteur:
Produces a composed candidate with Between Floors still primary.

Author:
Accept / revise / reject.
```

Composition produces another **candidate**. It never auto-promotes canonical state or bypasses `story-discovery accept`.

Do not implement F5 until:

- architecture preferences are modeled;
- structured author intent reaches the judge;
- causal diversity is qualified;
- the recommendation surface can explain primary vs subordinate layers.

---

# Implementation sequence

```text
F1 ontology + Identity
        ↓
F2 Discovery Brief / intent adequacy
        ↓
F3 causal-distinct search/judgment
        ↓
F4 craft-teaching recommendation surface
        ↓
compact synthetic + founder dogfood
        ↓
F5 optional composition
```

Each slice should be a bounded PR with tests and explicit authority invariants.

## Hard invariants across Phase F

1. Story Discovery remains advisory and non-canonical until explicit author acceptance.
2. Existing accepted-identity workflow behavior remains unchanged.
3. Raw-premise exploratory Story Discovery remains available.
4. No candidate-generated preference or emotional field is silently relabeled as prior author intent.
5. Deterministic contract fit remains compliance evidence, not an artistic-quality ranking.
6. Search/judge self-advocacy and generation provenance remain excluded from bounded judge evidence.
7. No new semantic Layer 1.5 or parallel emotional ontology.
8. Optional fields preserve backward compatibility and UNKNOWN/unspecified semantics.
9. One/zero survivor semantics remain intact.
10. Order / candidate-ID invariance remains a hard gate where comparative behavior is involved.

## Validation strategy

For every production slice:

- unit tests for schema and serialization;
- golden-path CLI tests;
- authority-boundary tests;
- controlled synthetic-provider fixtures;
- adversarial cases derived from Phase D/E findings;
- order/ID invariance where comparative behavior is involved;
- exact-head CI before merge.

After F1–F4, run a compact founder dogfood pass against the Phase E failure modes:

- under-specified intent;
- rhetorical near-duplicate alternatives;
- maximalist / mixed-causation intent;
- rich emotional hierarchy;
- craft-layer explanation.

Live-provider semantic validation and independent human-writer validation remain optional future confidence layers unless separately prioritized.

## Out of scope for the first Phase F wave

- GUI/TUI redesign;
- broad onboarding redesign beyond the structured brief required by Story Discovery;
- live-provider quality claims;
- automatic canonical acceptance;
- automatic composition;
- large speculative taxonomies of every possible author preference;
- replacing the existing `TargetExperience` model.

## Done condition

Phase F is mechanically qualified when F1–F4 are merged with tests and compact founder dogfood shows that:

- declared intent is sufficient to understand why a winner is preferred;
- alternatives are causally distinct enough to imply different major scenes;
- architecture preferences meaningfully affect recommendation behavior;
- rich target-experience hierarchy is visible and used correctly;
- tradeoffs teach what changes in the craft of the story;
- author authority remains explicit and intact.

F5 composition is optional and not required for the initial Phase F done condition.