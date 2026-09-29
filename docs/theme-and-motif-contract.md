# Theme and Motif Contract

**Status:** canonical semantic ownership contract  
**Scope:** theme, thematic progression, motif, and symbolic recurrence  
**Authority:** clarifies current ownership; does not create a separate Theme layer.

## Purpose

Theme and motif appear in several Auteur subsystems. The same word must not be
treated as the same kind of authority everywhere.

```text
Identity      -> thematic commitment / governing question
Structure     -> planned thematic progression and functions
Realization   -> events that concretely test or alter thematic conditions
Expression    -> language/images/behavior that render resonance
Derived views -> diagnosis of alignment, recurrence, omission, or tension
```

## Theme

### Identity — thematic commitment

Identity owns the authorial commitment: the story's central thematic question,
thesis, or equivalent governing meaning when explicitly accepted.

This is a commitment about what the story is exploring. It is not proof that a
particular scene has successfully expressed it.

### Structure — thematic progression

Structure owns the plan for how thematic pressure is distributed:

- thread `thematic_function`;
- act/chapter thematic movement;
- planned opposition or counterposition;
- setup/payoff related to the theme;
- ending relation to the thesis.

Deterministic diagnostics may check whether a declared thesis is represented by
planned threads. They must not judge the thesis as artistically correct.

### Realization — thematic evidence

Concrete events can support, challenge, complicate, or fail to realize a planned
thematic function.

Realization records the event/state facts. A thematic interpretation of those
facts is derived unless the owning accepted artifact explicitly records it.

### Expression — thematic rendering

Prose may create resonance through image, dialogue, juxtaposition, irony,
rhythm, symbolism, and repeated language. Expression may intensify or soften
the rendering without silently changing upstream canonical event facts.

## Motif

A motif is a recurring element whose repetition carries emotional, thematic,
character, or structural significance.

Current representations include:

- Blueprint-level thematic motifs;
- character `MotifProfile` behaviors/signatures;
- recurring symbols or story elements used by planning/reasoning systems.

These are not automatically one shared canonical registry.

### Ownership rule

```text
motif declared in accepted Identity/Structure
-> canonical planned motif

motif attached to accepted character design
-> canonical only to the authority level of that character artifact

motif observed in prose by analysis
-> derived observation

motif inferred across history by reasoning
-> derived projection
```

Repeated wording in prose is not enough to create a new canonical motif.

## Character thematic alignment

Character models may record `ThematicAlignment`: how a character embodies or
challenges a theme.

This is character-design/planning evidence. It does not transfer ownership of
the theme itself away from Identity/Structure.

## Series thematic arcs

Series artifacts may plan thematic progression across books. This is
Series-scope Structure/Identity authority and can constrain Book planning without
becoming a new semantic layer.

## Theme versus emotion

Theme answers a meaning/question claim. Emotional trajectory answers an
experience/state claim.

Examples:

```text
theme:
  "What does truth cost when institutions own memory?"

reader promise:
  mounting dread followed by fragile vindication

character state:
  relieved

motif:
  damaged archival seals
```

All four can coexist and have different owners.

See [Emotional Trajectory Contract](emotional-trajectory-contract.md).

## Theme versus motif

A motif can reinforce a theme, contradict it, or simply create character/aesthetic
continuity. A motif is not automatically thematic.

Likewise, the presence of a thematic keyword in prose is not deterministic
evidence that the theme was realized well.

## Diagnostics

Deterministic diagnostics may check explicit declared relationships, such as:

- a theme thesis has no planned thread thematic function;
- a declared motif is absent where an accepted plan explicitly requires it;
- a Series thematic progression omits a required stage.

Diagnostics should cite the declared source relationship. They must not infer
creative quality from keyword frequency.

## Non-goals

This contract does not introduce:

- a Theme semantic layer;
- automatic motif extraction as canon;
- keyword-count thematic scoring;
- an automatic verdict on what a story "really means";
- forced one-to-one mapping between motifs and themes;
- mandatory motifs for every project.

Historical structure/critic/research material remains evidence. This document is
the canonical ownership rule when those materials use overlapping terminology.
