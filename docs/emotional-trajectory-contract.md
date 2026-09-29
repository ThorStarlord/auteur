# Emotional Trajectory Contract

**Status:** canonical semantic contract  
**Scope:** emotional meaning across Identity, Structure, Realization, and Expression  
**Authority:** supplements [Narrative Architecture](narrative-architecture.md); does not add an emotional state machine.

## Purpose

Auteur represents several different kinds of emotion. They must not be collapsed
into one field or one numeric curve.

```text
reader promise              Identity
macro emotional progression Identity / Structure
scene experiential target   Structure
character felt state        Realization
emotional rendering         Expression
```

The central rule is:

> **The emotion the reader should experience is not automatically the emotion a
> character feels.**

## 1. Identity — reader-facing emotional promise

`StoryIdentity.target_experience` owns the accepted experiential commitment.

Current concepts include:

- primary emotional promise;
- secondary emotional palette;
- avoided experiences;
- macro emotional trajectory;
- genre-emotion roles;
- optional POV-specific experience contracts.

These are authorial commitments. They describe what the work is trying to make
the audience experience, not a sequence of mandatory character moods.

Profile-derived emotional targets remain distinct from explicitly authored
target experience. Their numeric weights are transported as opaque accepted
profile data; the repository must not silently reinterpret a weight as
intensity, probability, confidence, duration, or percentage.

## 2. Structure — planned emotional progression

Structure translates the Identity promise into planned progression:

- act/chapter emotional functions;
- target scene effects;
- thematic/emotional turns;
- contrast and pacing;
- ending-tone alignment.

A structural target is a plan. It may say that a chapter should move the reader
from safety to unease, but it does not assert that every character becomes
"uneasy."

## 3. Realization — character/state evidence

Realization records what characters concretely feel at scene boundaries.

`EmotionalState` uses:

- semantic labels such as `guarded`, `relieved`, `ashamed`, or
  `determined`;
- categorical intensity `low | moderate | high`;
- optional rationale.

This is deliberately qualitative. Auteur does not infer a universal numeric
distance between emotions.

Scene outcomes may also record explicit emotional shifts. A shift must be
compatible with the resulting exit state when the workflow validates that
boundary.

## 4. Expression — rendering

Expression chooses how emotional meaning appears in prose: diction, imagery,
dialogue, silence, rhythm, interiority, gesture, and pacing.

Expression may make an accepted emotional state subtle, masked, ironic, or
ambiguous. It must not silently change the underlying accepted event/state.

## Allowed complexity

The model must support, rather than diagnose away, normal narrative complexity:

- **variation** — adjacent scenes may produce different local feelings while
  serving one macro trajectory;
- **masking** — a character can perform calm while internally afraid;
- **contradiction** — a character may hold mixed emotions;
- **regression** — an arc may temporarily move backward;
- **sudden transition** — a revelation may cause a discontinuous change;
- **intentional divergence** — reader experience may deliberately oppose a
  character's felt state;
- **irony** — the reader may know enough to feel dread while a character feels
  relief;
- **false resolution** — local safety may coexist with a structural promise of
  coming collapse.

None of these is automatically an error.

## Consistency rules

Deterministic validation may check explicit contradictions such as:

- required state fields missing at a validation boundary;
- an impossible state transition declared under an explicit invariant;
- a structural ending tone directly violating an accepted target-experience
  constraint;
- a profile-derived obligation being dropped where the owning contract requires
  transport.

Validation must not judge whether an emotional arc is artistically good, nor
force every scene to monotonically follow the macro trajectory.

## Character versus reader example

```text
Identity:
  reader promise = mounting dread

Structure:
  scene function = temporary relief before reversal

Realization:
  protagonist state = relieved, high intensity

Expression:
  warm dialogue + one ominous environmental detail

Result:
  character relief and reader dread can both be correct.
```

## Relationship to theme

Emotion and theme can reinforce one another but have separate ownership.
A thematic thesis is not an emotion, and an emotional target is not evidence
that the story has made a thematic claim.

See [Theme and Motif Contract](theme-and-motif-contract.md).

## Relationship to character models

Character psychology, vulnerabilities, defenses, intimacy conditions, motifs,
and arc definitions may explain why an emotional state is plausible. They do
not replace the concrete Realization state.

See
[Character and Relationship Architecture](character-and-relationship-architecture.md).

## Non-goals

This contract does not introduce:

- a universal emotion ontology;
- numeric emotional simulation;
- automatic sentiment extraction as canon;
- mandatory monotonic arcs;
- an LLM verdict on emotional quality;
- a parallel emotional-authority store.

Historical emotional-target propagation specs and verification reports remain
implementation evidence. This document is the current semantic ownership
contract.
