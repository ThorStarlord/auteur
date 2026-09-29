# Realization State Contract

**Status:** canonical semantic contract  
**Scope:** Layer 3 (Realization) across Scene/Chapter workflows  
**Authority:** supplements [Narrative Architecture](narrative-architecture.md); does not create a new layer or acceptance path.

## Purpose

Realization answers:

> **What concretely happened, and what state is true because it happened?**

It sits between Structure and Expression:

```text
Structure                     Realization                         Expression
planned dramatic function  -> concrete event + state change  -> rendered language
```

Structure may plan a revelation. Realization records the scene in which the
revelation actually occurs and the resulting state. Expression decides how that
event is written.

## Canonical ownership

Realization owns concrete narrative facts and state transitions, including:

- scene identity and ordering;
- participants and POV reference;
- story time and explicit temporal relationships;
- goal, opposition, turn, decision, and outcome;
- knowledge facts and changes;
- character emotional state at scene boundaries;
- setup/payoff realization;
- arc-beat realization degree;
- concrete character, relationship, location, inventory, and other state deltas
  when represented by their owning state systems.

It does **not** own the authorial promise (Identity), the plan for how the story
should unfold (Structure), or the wording of prose (Expression).

## Scene artifact

The current Scene Realization schema is `SceneOutline` under
`src/auteur/narrative_realization/schema/`.

A scene progresses:

```text
draft -> incomplete -> ready
```

- **draft** requires only scene/chapter identity;
- **incomplete** requires core dramatic structure;
- **ready** requires temporal placement, POV/participants, full dramatic action,
  and both entry and exit state.

A ready scene therefore establishes a bounded transition:

```text
entry_state
+ goal / opposition / turn / decision / outcome
= exit_state
```

The transition is the Realization claim. Prose may render it differently, but
must not silently change it.

## Knowledge contract

`KnowledgeFact` is the atomic knowledge representation. A fact records:

- `what` — author-written fact value;
- `how_known` — learned, perceived, inferred, or external source;
- `degree` — certain, probable, suspected, or questioned;
- `source` — chapter position, character, document, or inference.

### Exact continuity rule

The current schema supports deterministic exact-fact continuity only:

```text
Outcome.knowledge_added value
= exact exit_state.knowledge[].what value
```

Matching is literal and case-sensitive. Validators do not infer that two
paraphrases mean the same fact.

For every entry fact:

```text
entry fact
-> remains in exit knowledge

unless

that same exact fact is listed in outcome.knowledge_questioned
```

Questioning is not forgetting. It changes the trust status of a fact; it does
not authorize silently deleting unrelated knowledge.

If Auteur later needs stable fact IDs plus display prose, that requires an
explicit schema distinction. Fuzzy matching must not be added to deterministic
validation as a substitute.

## Emotional state at Realization

Scene emotional state is character/state evidence, not the story's reader-facing
emotional promise.

`EmotionalState` uses:

- an author-defined semantic `state`;
- categorical intensity: `low | moderate | high`;
- optional rationale.

This is deliberately not a numeric psychology simulation. The wider relationship
between reader experience, structural emotional progression, and character
emotional state is defined in
[Emotional Trajectory Contract](emotional-trajectory-contract.md).

## Temporal contract

`narrative_position` identifies scene order within a chapter. Explicit temporal
relations may declare:

- `follows_scene`;
- `parallel_with`.

Parallelism is a temporal relationship, not permission to duplicate narrative
position or merge knowledge automatically. State from parallel scenes must only
be combined through an explicit downstream reconciliation/continuation rule.

## Character and relationship state

Realization may record concrete character or relationship change, but it must
respect the owning domain:

- character commitments/planned arcs remain in Identity/Structure;
- project relationship state remains owned by `relations.yaml` and explicit
  relation changes;
- scene outcome/state records what happens locally;
- derived relationship graphs or story-instance relations are projections, not
  replacement canon.

See
[Character and Relationship Architecture](character-and-relationship-architecture.md).

## Setup, payoff, and arc beats

A scene can record `setups_created`, `payoffs_triggered`, and
`realizes_arc_beats`.

These fields record what the scene concretely realizes. They do not replace the
Structure-layer plan that declared the setup, payoff expectation, or arc beat.

## Expression boundary

Accepted Expression may choose dialogue wording, imagery, syntax, rhythm,
sensory detail, interiority, and local pacing. It must preserve the accepted
Realization facts unless an explicit divergence/revision workflow is used.

The canonical boundary is
[Expression Boundary](expression-boundary.md).

## Freshness and revision

When accepted Realization changes, dependent Expression and composition may
become stale. Reuse requires explicit fresh dependencies; absence of a detected
dependency is not proof of independence.

See
[Revision and Staleness Contract](revision-staleness-contract.md).

## Artifact locations

Common current surfaces include:

```text
chapters/<chapter>/scenes/<scene>/realization.yaml
chapters/<chapter>/scenes/scene_<CC>_<SS>.yaml
.auteur/scenes/*.yaml
```

Exact storage depends on the owning workflow/reference fixture. Semantic
authority comes from the accepted artifact/provenance workflow, not merely from
a filename.

## Non-goals

This contract does not introduce:

- semantic paraphrase inference for knowledge;
- an emotional state machine;
- automatic relationship mutation from prose;
- automatic causal inference;
- a sixth semantic layer;
- automatic acceptance of generated scenes;
- Episode-specific Realization semantics.

Historical Layer-3 plans/specs remain design evidence. Where examples in those
documents conflict with this contract, this contract and the current schema are
authoritative.
