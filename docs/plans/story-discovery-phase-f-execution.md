# Phase F — Detailed Story Discovery Execution Plan

## Status

**Planning artifact for the remaining Phase F implementation.**

Current production baseline on `main`:

- Phase E founder adjudication: complete.
- F1 architecture-preference vocabulary + Story Identity commitment: complete via PR #97.
- F2 structured Discovery Brief + intent adequacy: complete via PR #99.
- Current `main` baseline when this plan was created: `8e55bcbe52eae1d3b2a578f92c4224732316f544`.
- Umbrella issue: #94.

The next production uncertainty is **causal distinctness**, followed by **craft-teaching recommendation explanation**. After those are qualified, run a compact founder dogfood gate. Composition remains optional.

This document turns the Phase F roadmap into an implementation-ready execution contract. It is intentionally more specific than `docs/plans/story-discovery-intent-aware-architecture.md` while preserving that roadmap's product thesis and hard invariants.

---

# 1. Product thesis to preserve

> Story Discovery should recommend against declared author intent, search across causally distinct narrative architectures, and explain how each architectural choice changes the story the author will actually write.

The implementation must preserve two distinct product modes:

```text
RAW PREMISE
→ exploratory Story Discovery
→ “What could this premise become?”

STRUCTURED DISCOVERY BRIEF
→ intent-aware Story Discovery
→ “Which direction best serves the story I say I want to write?”
```

F3 and F4 improve the quality and legibility of the alternatives. They do **not** create a new authority path and do not change the fact that canonical identity changes only through explicit author acceptance.

---

# 2. Hard invariants

These are release gates, not preferences.

1. **Advisory authority only.** Story Discovery never writes canonical `story_identity.yaml` before explicit `story-discovery accept`.
2. **Prior author intent remains distinct from candidate output.** Candidate-generated genre, audience, emotional framing, preferences, rationales, or self-evaluation never become evidence that the author wanted those things.
3. **No fake deterministic creativity metric.** Do not introduce a scalar “causal diversity score,” “creativity score,” or semantic-distance number and treat it as truth.
4. **Exact duplicate protection remains deterministic.** The existing normalized central-engine force-tuple duplicate guard stays intact.
5. **Semantic near-duplicate handling is explicitly semantic.** It must be represented as bounded derived evidence with uncertainty, not disguised as a deterministic check.
6. **Contract fit remains compliance evidence.** It never becomes an artistic-quality ranking or automatic winner rule.
7. **Generation provenance and self-advocacy remain excluded.** Lens, best-basis, confidence, generated summaries, tradeoffs, risks, “why this is best,” and rejected directions must not leak into bounded causal-diversity or winner evidence.
8. **F1 UNKNOWN semantics remain intact.** Omitted architecture preferences remain omitted.
9. **F2 intent adequacy remains intact.** Intent-aware recommendation must not proceed without the declared minimum author intent.
10. **One/zero survivor semantics remain intact.** A single survivor is a viability result, not comparative artistic judgment; zero survivors remain a recovery condition.
11. **Order and candidate-ID invariance remain hard gates.** Reordering candidate generation or remapping IDs must not change content-defined causal assessments.
12. **No parallel emotion ontology.** F4 must use the existing `TargetExperience` hierarchy.
13. **No semantic Layer 1.5.** Derived analysis lives in recommendation/search evidence and artifacts unless separately promoted through a future ontology decision.
14. **No automatic composition in the first Phase F completion gate.** F5 remains optional.

---

# 3. Existing seams to build on

F3/F4 should extend the qualified Story Discovery path rather than replace it.

Current relevant production seams:

- `src/auteur/story_discovery_recommend.py`
  - exact normalized central-engine duplicate guard;
  - bounded candidate evidence;
  - comparative judge request/parser;
  - single-survivor semantics;
  - author-facing recommendation surface;
  - advisory artifact augmentation.
- `src/auteur/story_discovery_intent.py`
  - structured Discovery Brief orchestration;
  - prior-author-intent evidence separation;
  - declared-intent contradiction checks;
  - F1 architecture preference and hard-constraint preservation;
  - intent-aware comparative judge path.
- `tests/test_story_discovery_synthetic_confidence_gate.py`
  - synthetic real-path harness;
  - self-advocacy isolation;
  - order/ID invariance;
  - exact-vs-semantic-duplicate boundary;
  - authority and malformed-judge failure tests.
- `tests/test_story_discovery_intent_brief.py`
  - F2 brief, adequacy, prior-intent, and acceptance behavior.

The preferred architecture is additive: create dedicated bounded-analysis modules and let the existing adapters orchestrate them.

---

# 4. Remaining release sequence

Recommended implementation sequence:

```text
F3a — Derived causal-profile contract
        ↓
F3b — Semantic causal-diversity gate + judge integration
        ↓
F4a — Derived craft-impact explanation contract
        ↓
F4b — Author-facing craft-teaching recommendation surface
        ↓
F-DOGFOOD — compact synthetic + founder adjudication
        ↓
F5 DECISION — compose only if still valuable
```

F3 and F4 are each split into two reviewable PRs because they introduce two different classes of risk:

- **evidence-model risk** — are we deriving the right concepts without contaminating canonical state?
- **behavior/surface risk** — do those concepts change recommendation behavior and author-facing output correctly?

If a sub-slice proves trivial it may be combined with its sibling, but the review boundaries below should still be respected internally.

---

# 5. F3a — Derived causal-profile contract

## 5.1 Goal

Give Auteur a bounded vocabulary for answering:

> **What causal strategy would make the author write materially different major scenes?**

This is derived recommendation evidence, not a new Story Identity contract.

## 5.2 New model

Add a dedicated module, tentatively:

`src/auteur/story_discovery_causality.py`

Introduce a strict Pydantic model approximately like:

```yaml
causal_profile:
  primary_strategy: expose institutional contradictions
  causal_owner: protagonist-led with institutional counterforce
  external_action_pattern:
    - schedule
    - trigger
    - constrain
    - force_choice
  pressure_system: incompatible institutional obligations close off safe options
  reversal_mechanics:
    - an apparent procedural victory creates a stronger obligation
    - the antagonist weaponizes the same rule the crew planned to use
  climax_mechanic: antagonist must publicly violate one of his own institutional rules
  scene_families:
    - procedural setup
    - timed institutional triggers
    - public rule conflicts
```

Required semantic dimensions:

1. **primary causal strategy** — the dominant method by which the protagonist pursues the central objective;
2. **causal ownership** — which character/system most strongly generates consequential turns;
3. **external action pattern** — recurring protagonist/ensemble verbs;
4. **pressure system** — what repeatedly makes those actions harder and escalates them;
5. **reversal mechanics** — how plans convert into new obstacles or changed tactical conditions;
6. **climax mechanic** — what kind of causal action actually resolves the central conflict;
7. **scene families** — representative kinds of major scenes implied by the engine.

Do not create controlled enums for every possible strategy or scene type in F3. The ontology evidence does not yet justify a universal taxonomy of narrative mechanisms. Use bounded structured prose/list fields first.

## 5.3 Evidence source

The causal profile must be derived only from bounded candidate commitments and prior author intent where applicable.

Allowed inputs:

- premise;
- declared Discovery Brief intent when supplied;
- candidate `core_answer`;
- candidate `central_engine`;
- candidate `story_type`;
- candidate `target_experience` only where it constrains causal interpretation;
- explicit hard constraints / author overrides;
- bounded genre-contract evidence;
- relevant character commitments if the current candidate evidence already exposes them in a bounded way.

Excluded inputs:

- discovery lens;
- `best_basis`;
- confidence;
- recommendation summary;
- generated tradeoffs / risks / best-for;
- `why_this_is_best`;
- rejected directions;
- generation provenance;
- candidate-authored claims that it is “unique,” “more causal,” “more exciting,” etc.

## 5.4 Extraction boundary

Create a dedicated causal-profiler request rather than asking the generation request to grade itself.

The profiler should:

- receive one candidate at a time;
- receive no candidate ID as a quality signal;
- return strict JSON matching `CausalProfile`;
- describe what the candidate's commitments imply, not advocate for the candidate;
- use low-temperature bounded inference;
- fail closed on malformed output.

The same provider may execute the profiler in production, but the prompt/evidence boundary must remain separate from candidate generation. Tests must demonstrate that mutating self-advocacy/provenance does not change profiler input.

## 5.5 Stable evidence key

For invariance testing and pairwise mapping, derive a stable opaque evidence key from content, not position or candidate ID.

Example:

```text
causal_evidence_key = first N characters of a SHA-256 over bounded candidate evidence
```

The exact representation is an implementation detail. Requirements:

- deterministic for the same bounded evidence;
- changes when causal evidence changes materially;
- does not depend on candidate order;
- does not expose artistic ranking.

Candidate IDs remain useful for artifact traceability, but the semantic assessor must not depend on them.

## 5.6 Artifact behavior

F3a should be able to serialize derived profiles to diagnostic/recommendation artifacts without putting them inside candidate Identity YAML.

Preferred shape in `discovery_report.yaml`:

```yaml
causal_analysis:
  schema_version: 1
  profiles:
    candidate_1:
      evidence_key: ...
      primary_strategy: ...
      causal_owner: ...
      external_action_pattern: [...]
      pressure_system: ...
      reversal_mechanics: [...]
      climax_mechanic: ...
      scene_families: [...]
```

At F3a this can remain diagnostic-only. It must not yet alter winner selection.

## 5.7 F3a tests

Add focused tests for:

- strict model parse/serialization;
- malformed profiler JSON fails closed;
- self-advocacy/provenance mutation does not change profiler input;
- candidate ID remap does not change the bounded profile request;
- order does not change per-candidate profile content mapping;
- changed causal actions change the evidence key;
- title-only/aesthetic-only mutation does not falsely count as a new causal profile if bounded causal evidence is otherwise unchanged;
- profiles do not appear in canonical `StoryIdentity` serialization;
- `story-discovery accept` remains unaffected;
- old raw and F2 structured-brief flows remain behaviorally unchanged in F3a.

## 5.8 F3a done condition

F3a is done when Auteur can derive and persist stable, bounded causal profiles for controlled candidates **without changing recommendation outcomes or canonical state**.

---

# 6. F3b — Semantic causal-diversity gate + comparative evidence

## 6.1 Goal

Prevent Auteur from presenting rhetorically different but causally equivalent candidates as a meaningful comparative choice.

Core criterion:

> **If choosing Candidate B instead of Candidate A would not materially change the major scenes the author writes, the alternatives are not sufficiently distinct for comparative recommendation.**

## 6.2 Pairwise assessment model

Add a strict model approximately like:

```yaml
pairwise_assessment:
  left_evidence_key: abc123
  right_evidence_key: def456
  classification: distinct | near_duplicate | uncertain
  shared_causal_mechanics:
    - both rely on obtaining records and proving provenance
  material_differences:
    - candidate B uses public performance to trigger self-incrimination
  scene_consequence: >
    Choosing B would create substantially different staged-performance and
    provocation scenes; choosing A would not.
  rationale: >
    Distinct because the protagonists repeatedly perform different external
    strategies and the climax resolves through a different causal mechanism.
```

Do **not** add a 0–100 similarity number.

The three-state classification matters:

- `distinct` — material causal difference is supported;
- `near_duplicate` — differences are mostly framing/interpretation while major acts/reversals/climax remain substantially the same;
- `uncertain` — evidence is insufficient to make a defensible causal-distinctness claim.

`uncertain` must not be silently treated as `distinct`.

## 6.3 Set-level qualification

For `N >= 2` surviving candidates:

1. derive profiles;
2. build every unordered pair;
3. sort pair evidence by stable content-derived keys, not candidate ID/order;
4. run the bounded diversity assessor;
5. require complete pair coverage and valid schema;
6. compute a set-level status.

Suggested statuses:

```text
qualified
not_adjudicable_near_duplicate
not_adjudicable_uncertain
malformed_analysis
not_applicable_single_survivor
```

No scalar aggregate diversity score.

## 6.4 V1 behavior policy

Do **not** automatically discard one member of a near-duplicate pair in F3b.

Automatically choosing which duplicate survives would itself require an additional ranking rule and could reintroduce order bias or hidden artistic scoring.

V1 behavior:

| Candidate state | F3 behavior |
| --- | --- |
| 0 survivors | existing zero-survivor recovery behavior |
| 1 survivor | existing viability-only result; semantic diversity not applicable |
| 2+ and all pairs `distinct` | comparative recommendation may proceed |
| 2+ with any `near_duplicate` | persist candidates + causal diagnostics, but do not claim a comparative winner |
| 2+ with any `uncertain` | persist candidates + diagnostics, but do not claim causal diversity |
| malformed causal analysis | fail closed; no recommendation |

Preferred author-facing concept for failed set qualification:

> **No recommendation yet — these interpretations are not causally distinct enough to justify a meaningful choice.**

The search artifacts remain useful. `recommended_candidate_id` must remain absent/empty for a non-adjudicable set.

This is intentionally analogous to F2 intent adequacy: when the optimization problem is under-specified or the alternatives do not create a real choice, Auteur should refuse to pretend it knows “best.”

## 6.5 Generation guidance

F3 should also reduce the probability of false choices before the gate.

Update Story Discovery generation guidance so each candidate must seek a materially different causal strategy, not merely a different theme, metaphor, or emotional framing.

The prompt should explicitly ask the generation model to think in terms of:

- different protagonist/ensemble verbs;
- different causal owner;
- different recurring pressure;
- different reversal mechanism;
- different climax resolution mechanic;
- different major scene families.

Do **not** expose other candidates' self-advocacy to generation as authoritative evidence.

V1 does not require an automatic regeneration loop. The semantic gate is the safety mechanism if generation still collapses into near-duplicates.

A future F3.1 could use failed causal-diversity feedback for bounded regeneration, but only after the basic gate proves reliable.

## 6.6 Winner-judge integration

Only invoke the comparative winner judge when the causal set is `qualified`.

Add derived causal profile evidence to each candidate under a clearly labeled block such as:

```json
"derived_causal_profile": { ... }
```

This block must remain separate from `story_identity` and from candidate self-evaluation.

Update the judge instruction so:

- causal profiles are derived evidence about what scenes/actions the candidate implies;
- causal distinctness is a prerequisite, not an artistic score;
- the judge still chooses against declared author intent when F2 brief exists;
- high contract fit still does not auto-win;
- architecture preferences may influence the winner but do not erase primary-engine hierarchy;
- the judge must not reward a candidate simply because its profile looks longer or more complex.

## 6.7 F3 artifact changes

`discovery_report.yaml` / `discovery_set.yaml` should expose enough diagnostic state to explain whether recommendation was qualified.

Suggested fields:

```yaml
causal_analysis:
  schema_version: 1
  status: qualified
  profiles: {...}
  pairwise_assessments:
    - left_candidate_id: candidate_1
      right_candidate_id: candidate_2
      classification: distinct
      material_differences: [...]
      scene_consequence: ...
```

`comparison.md` should add a bounded **Causal Distinctness** section containing:

- candidate primary strategies;
- action patterns;
- pressure systems;
- climax mechanics;
- pairwise distinctness result.

Do not yet implement the full F4 `What you gain / What you give up` craft lesson here.

## 6.8 F3 adversarial test matrix

Reuse Phase D/E cases and add purpose-built mutations.

### Required positive cases

1. **Museum heist — evidence vs systems vs social engineering**
   - evidence: retrieve → authenticate → connect → disclose;
   - systems: schedule → trigger → constrain → force choice;
   - social engineering: stage → misdirect truthfully → provoke → expose.
   - Expected: all pairs `distinct`.

2. **Shrinking house — relational vs containment vs restitution**
   - expected different major scene families and climax mechanics despite shared premise/theme.

3. **Elevator mystery — timing vs identity vs concealment**
   - expected distinct even though all remain within one physical location and genre contract.

### Required negative cases

4. **Rhetorical paraphrase**
   - same access → records → authenticate → expose chain under different titles/themes.
   - Expected: `near_duplicate`.

5. **Aesthetic-only mutation**
   - gothic vs procedural vocabulary while external acts, pressure, reversal, and climax remain the same.
   - Expected: `near_duplicate`.

6. **Theme-only mutation**
   - “truth vs power” vs “memory vs institution” with same causal sequence.
   - Expected: `near_duplicate` or `uncertain`, never automatically `distinct` solely due thematic language.

7. **Insufficient evidence**
   - vague candidate engine with no inferable reversal/climax mechanics.
   - Expected: `uncertain`, no comparative winner.

### Mutation tests

- mutate title only → classification unchanged;
- mutate self-advocacy only → classification unchanged;
- mutate target-experience adjectives only → classification unchanged unless the mutation changes an explicit pressure/causal commitment;
- mutate protagonist action sequence materially → may become `distinct`;
- mutate climax mechanism materially → may become `distinct`;
- mutate contract-fit score → diversity classification unchanged.

### Invariance tests

- candidate order permutations;
- candidate ID remaps;
- pair order permutations;
- same bounded evidence with different generation provenance;
- same causal profile presented under different titles.

### Authority / failure tests

- near-duplicate set produces no canonical state;
- `uncertain` set produces no fake winner;
- malformed profiler output fails closed;
- malformed diversity assessment fails closed;
- incomplete pair coverage fails closed;
- one survivor retains viability wording;
- zero survivor retains recovery wording;
- exact normalized duplicate still triggers the deterministic guard before semantic diversity is treated as qualified.

## 6.9 F3 bounded claim after merge

Allowed claim:

> Auteur can derive bounded causal profiles for Story Discovery candidates and, in controlled regression cases, refuse comparative recommendation when alternatives do not imply materially different causal strategies and major scenes.

Do **not** claim:

- universal semantic duplicate detection;
- live-provider creative diversity quality;
- human consensus about whether two stories are “really different”;
- numeric creativity measurement.

---

# 7. F4a — Derived craft-impact explanation contract

## 7.1 Goal

Given a causally qualified candidate set and a recommended primary engine, derive a grounded explanation of **what choosing each alternative changes in the actual craft of the story**.

F4 should consume F3 evidence instead of creating a second unrelated causal-analysis system.

## 7.2 Craft propagation model

Use the Phase E propagation chain:

```text
CRAFT LAYER CHANGED
        ↓
CAUSAL OWNERSHIP / EXTERNAL ACTION PATTERN
        ↓
PRESSURE SYSTEM / SCENE FAMILIES
        ↓
STORY TEXTURE / AESTHETIC EMPHASIS
        ↓
READER EXPERIENCE
        ↓
THEMATIC CONSEQUENCE
```

Important distinctions:

- causal engine ≠ external acts;
- external acts ≠ story texture;
- story texture ≠ aesthetic framing;
- aesthetic framing ≠ reader emotion;
- reader emotion ≠ theme;
- changes upstream can propagate downstream, but target experience is also prior author intent that constrains which causal architecture is desirable.

## 7.3 New derived comparison model

Tentative model:

```yaml
craft_impact:
  compared_candidate: candidate_2
  craft_layer_changed:
    - causal_ownership
    - pressure_system
  causal_ownership_shift: >
    More consequential turns originate with the brother's hidden interventions.
  external_action_shift:
    add_or_emphasize:
      - conceal
      - intervene
      - compensate
      - sacrifice
    de_emphasize:
      - direct protagonist-led repair decisions
  scene_family_shift:
    add_or_emphasize:
      - parallel hidden interventions
      - near-discovery scenes
      - unintended consequences of secret repair
  pressure_texture_shift: >
    More dramatic-ironic hidden-action suspense and less purely protagonist-centered recovery.
  reader_experience_shift:
    primary_promise_effect: preserved_but_reweighted
    secondary_palette_effect:
      - more pity
      - more moral discomfort
      - more dread
    trajectory_effect: >
      Reader knowledge becomes increasingly painful as secret interventions accumulate.
  thematic_effect: >
    Moves emphasis from healing without full truth toward whether atonement matters without confession.
  gain: >
    Stronger hidden causal pressure and moral complexity.
  give_up: >
    Some causal ownership by the declared protagonist.
  composability: compatible_as_secondary
  composition_note: >
    Can sit beneath the protagonist-led recovery engine if the brother does not solve decisive turns.
  primary_risk: >
    If the brother's interventions resolve too many obstacles, he becomes the effective protagonist.
```

Do not expose a fake precision score for “composability.” Use categorical states such as:

```text
compatible_as_secondary
requires_reframing
mutually_exclusive_with_primary
uncertain
```

The exact names can be refined in implementation.

## 7.4 Grounding rules

Craft-impact derivation may use:

- structured Discovery Brief;
- F1 architecture preferences;
- existing rich `TargetExperience` fields;
- winner + alternative StoryIdentity bounded evidence;
- F3 causal profiles;
- explicit hard constraints;
- bounded genre-contract evidence.

It must not use candidate self-advocacy as evidence.

Every statement should be traceable to one of these sources. The explainer should prefer `unknown / not enough evidence` over inventing an unsupported scene or emotion shift.

## 7.5 Architecture-preference behavior

F4 is where the F1 preference vocabulary becomes visible to the author.

### `complexity=maximalist`

The explainer should actively consider whether compatible mechanisms from alternatives can enrich the selected primary engine.

This does **not** mean all alternatives should be combined.

### `causal_distribution=mixed`

The explainer should consider several compatible causes/pressure systems contributing to major outcomes rather than assuming one isolated cause is ideal.

### `engine_hierarchy=primary_with_layers`

The explainer should preserve one clearly governing engine while treating compatible alternatives as subordinate causal/relational/institutional layers.

The combination:

```text
maximalist
+ mixed
+ primary_with_layers
```

means:

> Prefer a dense interacting architecture, but keep causal hierarchy legible enough that the primary reader promise and protagonist story remain identifiable.

F4 must not collapse this into “more complexity is always better.”

## 7.6 Emotional hierarchy behavior

Use the existing `TargetExperience` model.

Distinguish:

- **target audience** — who the story is for;
- **primary emotional promise** — governing reader experience;
- **secondary emotional palette** — supporting/contrasting feelings;
- **emotional trajectory** — macro emotional progression;
- avoided experiences / genre emotion roles / POV contracts when explicitly present.

F4 should explain whether an alternative:

- preserves the primary promise;
- reweights the secondary palette;
- alters the trajectory;
- threatens to replace the governing promise;
- leaves emotional impact unknown because the brief/candidate lacks enough evidence.

Do not equate “many emotions” with confusion. The relevant question is whether emotional hierarchy and trajectory remain legible.

## 7.7 F4a tests

- same F3 causal profile + different title does not change craft-impact structure;
- explicit external-action difference produces different scene-family explanation;
- primary emotional promise is not overwritten by secondary emotions;
- missing secondary palette does not create invented emotions;
- maximalist/mixed/primary-with-layers preferences are represented as architecture guidance, not target emotion;
- no architecture preference supplied → no invented maximalism/minimalism advice;
- hard constraints remain visible;
- self-advocacy mutations do not change explainer evidence;
- strict output schema / malformed output fail closed;
- craft analysis remains derived and non-canonical.

## 7.8 F4a done condition

Auteur can derive a grounded, typed craft-impact comparison for a controlled winner/alternative pair without yet changing the CLI rendering.

---

# 8. F4b — Author-facing craft-teaching recommendation surface

## 8.1 Goal

Make the Story Discovery recommendation teach the author **what the architectural choice changes**, not merely state a winner and generic tradeoff.

## 8.2 Recommended surface hierarchy

For the winner:

```text
RECOMMENDED — <title>
<core answer>

WHY THIS FITS YOUR BRIEF
<bounded rationale>

PRIMARY ENGINE
<primary strategy / causal owner / central conflict>

READER PROMISE
Primary emotional promise: ...
Supporting palette: ...         # only if declared/present
Trajectory: ...                 # only if declared/present

WHY THIS ENGINE IS PRIMARY
<relationship to genre/audience/target experience/preferences>
```

For each alternative:

```text
ALTERNATIVE — <title>

WHAT CHANGES
<craft layers changed>

CAUSAL EFFECT
<causal ownership / strategy shift>

WHAT YOU WILL WRITE MORE OF
<external verbs + scene families>

PRESSURE / STORY TEXTURE
<recurring scene pressure and experiential texture>

READER-EXPERIENCE SHIFT
<primary promise / secondary palette / trajectory effect>

THEMATIC EFFECT
<meaning produced by the changed causal pattern>

WHAT YOU GAIN
<specific strength>

WHAT YOU GIVE UP
<narrative weight that moves away; not necessarily deletion>

COMPOSABILITY
<categorical state + explanation>

PRIMARY RISK
<what would cause the alternative/subordinate layer to displace the intended primary engine>
```

## 8.3 “Give up” wording rule

Avoid implying that every tradeoff is literal deletion.

Prefer language such as:

> **Narrative weight moves from X toward Y.**

The implementation should explain changes in causal weight, page-space pressure, scene energy, suspense, or emotional emphasis where supported.

## 8.4 Sparse-data behavior

F4 must degrade gracefully.

If a brief has only a primary emotional promise:

- show the primary promise;
- omit secondary-palette/trajectory claims rather than inventing them.

If no architecture preferences were declared:

- explain the primary engine and alternatives;
- do not recommend maximalist composition as if it were author intent.

If causal impact is `uncertain`:

- say that the downstream craft effect is uncertain;
- do not fabricate scene families.

## 8.5 Artifacts

`comparison.md` becomes the durable detailed teaching artifact.

CLI output should remain useful but more compact than the full file.

Preferred split:

### CLI

- recommendation;
- concise why;
- primary engine;
- one compact craft-shift line per alternative;
- exact accept/review commands;
- explicit “Nothing has been accepted yet.”

### `comparison.md`

- full F3 causal analysis;
- full F4 craft-impact blocks;
- target-experience hierarchy;
- composition compatibility notes;
- recommendation rationale.

### YAML report

Store typed derived analysis for machine/research regression without making it canonical Identity.

## 8.6 F4b regression matrix

Required cases:

1. **Case 5 / brother disaster**
   - recommendation must teach protagonist-led recovery vs brother-led atonement vs institutional causation;
   - reader-experience impact must distinguish primary painful dramatic irony from supporting pity/dread/moral discomfort;
   - risk must identify brother becoming effective protagonist.

2. **Case 6 / fixed history**
   - witness engine vs relationship engine vs institutional/public-memory engine;
   - explain how the causal choice shifts scene texture and emotion without claiming only one emotion may exist.

3. **Case 4 / shrinking house**
   - demonstrate maximalist + mixed + primary-with-layers behavior;
   - relational, containment, and restitution mechanisms may be composable but one remains primary.

4. **No architecture preferences**
   - no composition preference inferred.

5. **Primary experience only**
   - no invented secondary palette.

6. **Raw exploratory Story Discovery**
   - surface remains explicitly exploratory and does not imply undeclared intent.

7. **Single survivor**
   - remains viability wording; no fake alternative tradeoff lesson.

8. **Zero survivor / non-adjudicable F3 set**
   - no recommendation block rendered.

9. **Authority**
   - exact accept commands remain correct;
   - canonical Identity absent until explicit acceptance.

## 8.7 F4 bounded claim after merge

Allowed claim:

> In controlled regression cases, Auteur can explain how a selected causal engine and its alternatives would change causal ownership, external action, scene pressure, reader experience, and thematic emphasis while preserving explicit author authority.

Do not claim broad writing pedagogy effectiveness or population-level usability before founder/human dogfood.

---

# 9. Compact Phase F dogfood gate

## 9.1 Purpose

After F1–F4 are merged, test the exact failure modes that motivated Phase F.

This is not a broad usability study and does not need a large benchmark.

The founder's job is to judge whether the resulting recommendation is now **legible, causally meaningful, and creatively useful**.

## 9.2 Required cases

Use five high-information cases rather than reopening a large synthetic benchmark.

### D1 — intent adequacy

Retired astronaut / mission-control chatter.

Test:

- raw premise remains exploratory;
- intent-aware path refuses an under-specified brief;
- sufficiently specified brief makes recommendation rationale legible.

### D2 — causal false choice

Museum heist with nothing stolen / nobody lies.

Test:

- evidence, systems, and social-engineering engines produce different action chains, pressures, reversals, and climax mechanics;
- rhetorical paraphrases are rejected as non-adjudicable.

### D3 — maximalist mixed causation

Shrinking inherited house.

Test:

- primary engine remains legible;
- compatible subordinate layers can be explained without flattening hierarchy;
- maximalism is treated as architecture preference, not target emotion.

### D4 — craft teaching

Protagonist never learns brother caused disaster.

Test:

- `What you gain / What you give up` now identifies the actual craft layer touched;
- causal ownership, scenes, texture, emotional hierarchy, and theme propagation are understandable.

### D5 — emotional hierarchy

Fixed history / time traveler as witness.

Test:

- one governing emotional promise can coexist with a secondary palette and trajectory;
- multiple causal systems do not imply multiple ungoverned emotional promises;
- audience, target experience, architecture preference, and causal engine remain conceptually separate.

## 9.3 Founder questions

For each adjudicable case, ask:

1. **Is the alternative a genuinely different story engine?**
2. **Can you name the major scenes/actions that would change if you chose it?**
3. **Can you tell which causal layer is primary?**
4. **Can you tell what reader-experience element changes and what remains governing?**
5. **Does `What you gain / What you give up` teach a real craft consequence?**
6. **If composition is suggested, is the hierarchy legible rather than “everything at once”?**
7. **Does Auteur still feel advisory rather than prescriptive?**

Natural-language answers remain acceptable; do not reduce founder judgment to a fake numerical score.

## 9.4 Dogfood pass criteria

Phase F first-wave qualification requires:

- no authority invariant violation;
- no repeated false-choice pattern in the targeted causal-distinctness cases;
- the founder can explain why the recommendation serves the declared brief;
- the founder can identify materially different scene/action consequences among alternatives;
- architecture preferences are understood as architecture preferences;
- target emotional hierarchy is legible and not confused with causal topology;
- craft tradeoffs are educational enough to support a conscious author decision.

A **respectful disagreement with the winner remains acceptable** if the recommendation is defensible and the tradeoff is clear.

A repeated failure class routes back to the owning slice:

```text
intent inadequacy / prior-intent confusion → F2
false causal choice                  → F3
opaque gain/give-up or emotion shift → F4
authority problem                    → authority regression
composition soup                     → do not implement F5 yet
```

## 9.5 Dogfood artifact

Create a research-only findings document and PR, analogous to Phase E but much smaller.

Suggested path:

`docs/research/story-discovery-phase-f-dogfood-findings.md`

No production changes in the dogfood PR unless a failure is already separately understood and intentionally scoped.

---

# 10. F5 — Optional composition decision

## 10.1 Decision gate

Do not implement F5 merely because alternatives are technically composable.

Implement only if the dogfood shows that authors repeatedly want:

> **Keep the recommended primary engine, but borrow these compatible subordinate mechanisms.**

If F4 explanation alone is sufficient for the author to make that decision manually, F5 can remain deferred.

## 10.2 If implemented

Composition must produce a **new candidate**, never canonical state.

Possible workflow:

```text
recommended candidate
+ selected subordinate mechanisms
+ declared brief
+ hard constraints
        ↓
composition request
        ↓
new composed StoryIdentity candidate
        ↓
validate against intent + contracts
        ↓
re-profile causally
        ↓
explain what remained primary / what was borrowed
        ↓
author accept / revise / reject
```

Hard requirements:

- primary engine explicitly identified;
- borrowed mechanisms explicitly traceable to alternatives;
- hard constraints preserved;
- F1 architecture preferences preserved;
- F3 causal profile regenerated for the composed candidate;
- F4 explanation states whether hierarchy stayed intact;
- composition provenance remains advisory metadata, not evidence that the author accepted anything;
- only `story-discovery accept` promotes canonical Identity.

Potential future typed request:

```yaml
composition_request:
  primary_candidate_id: candidate_1
  borrow:
    - from_candidate_id: candidate_2
      mechanism: secret atonement interventions
    - from_candidate_id: candidate_3
      mechanism: incomplete institutional causal model
```

Do not freeze this API before the dogfood gate.

---

# 11. PR / issue execution map

## Planning PR

This document only.

## F3a production PR

Tentative title:

`Add derived Story Discovery causal profiles`

Primary files:

- new `src/auteur/story_discovery_causality.py`;
- focused new causal-profile tests;
- minimal artifact plumbing if needed.

Behavior change: diagnostic analysis only; recommendation outcome unchanged.

## F3b production PR

Tentative title:

`Require causal distinctness before Story Discovery recommendation`

Primary files:

- `src/auteur/story_discovery_causality.py`;
- `src/auteur/story_discovery_recommend.py`;
- `src/auteur/story_discovery_intent.py`;
- generation prompt seam in `cli_handlers.py` or the smallest existing search-prompt location;
- synthetic confidence tests + new F3 adversarial tests.

Behavior change: causally non-adjudicable candidate sets no longer receive a winner.

## F4a production PR

Tentative title:

`Add derived Story Discovery craft-impact analysis`

Primary files:

- new `src/auteur/story_discovery_craft.py` or equivalent;
- strict craft-impact models/parser;
- focused tests.

Behavior change: derived analysis only; minimal/no CLI change.

## F4b production PR

Tentative title:

`Teach Story Discovery recommendation tradeoffs`

Primary files:

- recommendation surface renderer;
- intent-aware comparison rendering;
- artifact augmentation;
- Phase B surface tests + new F4 tests.

Behavior change: author-facing recommendation becomes craft-teaching.

## Dogfood PR

Research-only findings.

## F5

Create issue/PR only after explicit go decision.

---

# 12. Validation matrix for every production PR

Every production PR must pass:

1. exact-head GitHub Actions Validation;
2. wheel/package smoke;
3. Python 3.11;
4. Python 3.12;
5. Python 3.13;
6. repository validators/checks;
7. Ruff;
8. targeted unit/regression tests for the slice;
9. authority-boundary tests;
10. accepted-identity regression tests where Identity is touched;
11. order/ID invariance tests where comparative evidence is touched.

Draft PR until the exact final head is green.

Merge using the frozen expected head SHA.

---

# 13. Risk register

## Risk A — semantic assessor merely agrees with generated labels

Mitigation:

- derive profile from bounded StoryIdentity evidence;
- exclude generation self-advocacy;
- use mutation tests where titles/lenses change but causal acts do not;
- test action/climax changes independently.

## Risk B — false precision

Mitigation:

- categorical distinct / near-duplicate / uncertain;
- no scalar creativity or diversity score;
- explicit uncertainty state.

## Risk C — order bias when choosing what to drop

Mitigation:

- F3 v1 does not auto-drop near-duplicates;
- stable content-derived evidence keys;
- full permutation tests.

## Risk D — too many provider calls

F3/F4 add derived analysis requests.

Mitigation:

- keep schemas compact;
- prefer one bounded set-level diversity request after per-candidate profiles rather than arbitrary repeated critique loops;
- avoid regeneration loops in v1;
- measure request count in tests;
- optimize only after correctness is established.

## Risk E — maximalism becomes “always add everything”

Mitigation:

- architecture preferences remain optional;
- primary-with-layers hierarchy explicitly modeled;
- F4 composition categories include incompatibility / reframing / uncertainty;
- F5 remains gated.

## Risk F — emotional complexity treated as confusion

Mitigation:

- use existing TargetExperience hierarchy;
- distinguish governing promise, secondary palette, and trajectory;
- only flag incoherence when the architecture actually undermines the declared promise, not because several emotions exist.

## Risk G — F4 fabricates creative-writing lessons

Mitigation:

- require grounding in F3 profile + Identity + brief;
- explicit unknown/uncertain path;
- mutation tests;
- founder dogfood specifically asks whether the teaching corresponds to actual scene/action consequences.

## Risk H — raw exploratory mode becomes accidentally intent-aware

Mitigation:

- keep F2 mode boundary explicit;
- raw path may gain causal-diversity protection, but it must not claim optimization against undeclared author intent;
- regression test wording and evidence blocks.

---

# 14. Stop / rollback conditions

Stop the current slice and revise before merge if any of these occur:

- derived causal analysis depends on candidate IDs/order;
- self-advocacy/provenance leaks into profiler/diversity evidence;
- semantic assessor needs a scalar score to make the design work;
- near-duplicate handling silently chooses a survivor by position;
- F3 changes one/zero survivor meaning;
- F4 creates new canonical fields merely for explanatory convenience;
- F4 invents secondary emotions/architecture preferences when absent;
- composition logic appears before F3/F4 are qualified;
- canonical Identity changes before explicit acceptance;
- CI regression requires weakening an existing authority or evidence-isolation test.

If a slice cannot satisfy these conditions cleanly, prefer a smaller bounded implementation over relaxing the invariants.

---

# 15. Phase F first-wave done condition

F1–F4 plus compact dogfood are sufficient for the first Phase F completion gate.

Required final state:

```text
Author supplies raw premise or structured intent
        ↓
Auteur generates viable StoryIdentity candidates
        ↓
F3 derives causal profiles from bounded evidence
        ↓
F3 verifies alternatives imply materially different causal strategies/scenes
        ↓
if not distinct: no fake winner
        ↓
if distinct: comparative judge chooses against available author intent
        ↓
F4 explains what the choice changes in craft and reader experience
        ↓
Author sees gains, weight shifts, composition compatibility, and risks
        ↓
Nothing canonical yet
        ↓
Author explicitly accepts / revises / chooses another candidate
```

The first-wave Phase F claim may be:

> **Auteur can use declared author intent to compare causally distinct Story Discovery architectures, refuse false-choice recommendation when alternatives collapse into the same causal strategy, and explain how a selected engine changes external action, scene pressure, reader experience, and thematic emphasis without taking canonical authority away from the author.**

This remains a controlled product-mechanics and founder-dogfood claim. Live-provider semantic quality and independent writer-population validation remain separate future confidence layers.

---

# 16. Immediate next action

After this plan is merged:

1. create the bounded F3 implementation issue from sections 5–6;
2. start **F3a — derived causal-profile contract** from current `main`;
3. keep it behavior-neutral except diagnostic causal analysis;
4. validate exact-head CI;
5. merge F3a before adding the F3b semantic gate.

This ordering ensures the most important remaining semantic concept—**what makes two narrative engines causally different**—is inspectable and testable before it is allowed to suppress or enable a recommendation.
