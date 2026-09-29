# Character and Relationship Architecture

**Status:** canonical semantic ownership map  
**Scope:** character and relationship concepts across Auteur  
**Authority:** clarifies existing owners; it does not create a new character or relationship canon.

## Purpose

Auteur has several character and relationship representations because they
answer different questions. They must not be merged merely because fields have
similar names.

```text
Identity      -> who/what is committed
Structure     -> what transformation/function is planned
Realization   -> what state is concretely true now
Expression    -> how character/relationship meaning is rendered
Derived views -> analysis, categorization, graphs, diagnostics
```

## Character ownership

### Identity

Story Identity may name characters and commit to stable book-level facts such
as role, intended arc type, or other explicit author commitments.

Identity answers:

> Who must this character be for this story to remain this story?

It does not own scene-by-scene state.

### Structure / Blueprint

Blueprint characters carry planning information such as:

- dramatic role;
- arc type and milestones;
- current/planned structural state;
- relationships used by structural planning;
- optional richer character identity/categorization data.

The rich character model under `src/auteur/character/` can represent:

- structural/narrative role;
- archetype and shadow;
- wound, fear, desire, contradictions;
- vulnerability family and defense mechanisms;
- validation dependencies and intimacy requirements;
- texture: voice, habits, gestures, rituals, tells, social aura;
- ideology/philosophy;
- essence traits;
- motifs;
- arc direction;
- relationship mesh;
- thematic alignment.

These are useful planning/analysis semantics. Their authority depends on the
owning accepted Blueprint/Identity artifact. Running
`auteur character categorize` is a **derived proposal/analysis operation**; it
does not by itself create new story canon.

### Realization

Realization owns concrete character state produced by events:

- where the character is;
- what the character knows;
- what they feel;
- decisions made;
- physical/inventory state when represented;
- event-caused relationship change.

A planned arc milestone is not proof that it happened. Realization evidence is.

### Expression

Expression renders character through prose, dialogue, behavior, interiority,
gesture, voice, and style. Wording does not silently rewrite Identity,
Structure, or Realization.

## Relationship ownership

Auteur intentionally has multiple relationship domains.

### 1. Ontology relationships

Ontology relation types describe available narrative concepts/vocabulary. They
do not assert that two story characters currently have a particular state.

### 2. Planned / identity relationship semantics

Blueprint/character models may describe relationship signatures and arcs:
relationship type, ideological alignment, authorship/dependency shape,
progression stages, trust evolution, turning points, and other planned
semantics.

These explain intended relationship design.

### 3. Canonical project relationship state

ADR 015 remains authoritative for current project-level relationship state:

```text
relations.yaml
```

`RelationState` tracks directional state between two characters, including:

- public role and private truth;
- trust;
- resentment;
- dependency;
- attraction;
- fear;
- obligation;
- last changed location/reference.

The six numeric relation metrics are bounded project-state measures used by this
specific domain. They do **not** imply that all character psychology or all
emotional state should become numeric.

Chapter-scoped `relation_changes.yaml` records explicit deltas. Applying a
change is the authority-bearing state update; diagnosing or graphing relations is
not.

Relevant commands:

```text
auteur relations validate
auteur relations diagnose
auteur relations graph
auteur relations apply
```

### 4. Series relationship continuity

Series artifacts may represent relationship state/progression across books.
Those records are Series-scope continuity authority; they are not a replacement
for a Book project's local `relations.yaml`.

### 5. Scene relationship deltas

A Scene Realization can establish that an event changed a relationship. The
local event is Realization evidence. Project relationship state changes still
flow through the owning explicit relation-state workflow where that workflow is
in use.

### 6. Derived story-instance relations

Global Map/Focus and relationship-extraction systems may derive relations among
accepted story facts for reasoning. Those relations are projections unless an
owning contract explicitly grants authority.

They must not overwrite `relations.yaml`, accepted character commitments, or
Series continuity.

## Why apparently duplicate fields are allowed

Two models can use similar terms while representing different semantic jobs.

For example:

```text
CharacterIdentity relationship arc
= planned character-design semantics

RelationState.trust
= current project relationship state

Scene outcome relationship delta
= concrete event-caused change

Series relationship record
= cross-book continuity
```

A future unification is warranted only if evidence shows that separate owners
create harmful ambiguity. Similar names alone are not sufficient reason.

## Character categorization commands

```text
auteur character categorize <blueprint>
auteur character diagnose <blueprint>
auteur character show <blueprint>
```

These inspect/propose derived character semantics from Blueprint data.
Categorization output must not be treated as accepted author intent unless an
existing authority-bearing workflow explicitly persists/accepts it.

## Cross-layer trajectory rule

A character or relationship trajectory is reconstructed from explicit sources:

```text
accepted identity/plan
+ ordered accepted realization/state evidence
-> derived trajectory / diagnosis
```

The trajectory is not permission to invent intermediate states, infer hidden
motives as facts, or retroactively rewrite accepted events.

## Emotion

Character emotional state belongs to Realization; the reader-facing emotional
promise belongs to Identity/Structure. See
[Emotional Trajectory Contract](emotional-trajectory-contract.md).

## Theme and motif

Characters may embody or challenge a theme and may carry motifs. This does not
move theme authority into the character subsystem. See
[Theme and Motif Contract](theme-and-motif-contract.md).

## Non-goals

This architecture does not introduce:

- a universal Character entity spanning every scope/layer;
- automatic promotion of categorization output;
- prose-derived canonical relationship changes;
- a single numeric psychology model;
- automatic reconciliation between Series and Book relationship stores;
- a new relationship ontology for Global Map/Focus.

Historical character, relationship, and trajectory design documents remain
evidence. This document is the current ownership map.
