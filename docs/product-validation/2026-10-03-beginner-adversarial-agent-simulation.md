# Beginner Adversarial Agent Simulation Protocol v1

**Date:** 2026-10-03
**Tracking:** #316
**Evidence class:** synthetic agent/repository evidence
**Human participants:** 0
**Baseline:** PR #314 stacked over #309

## Purpose

Exhaust repository-answerable and agent-answerable uncertainty before spending
human-attention budget in #305.

This protocol does not replace human evidence for claims that are inherently
subjective. It asks a narrower question:

> Which open product questions can already be resolved, weakened, or sharpened
> through adversarial simulation and machine-checkable evidence?

## Evidence hierarchy

Use four evidence classes without conflation:

1. **MECHANICAL** — deterministic repository behavior, state, action availability,
   preservation, freshness, authority, or continuity projection.
2. **SYNTHETIC BEHAVIORAL** — an agent persona can or cannot complete a task from
   the visible surface without privileged internal instructions.
3. **PROVIDER** — observed real-provider latency/output behavior.
4. **HUMAN** — actual human comprehension, felt ownership, preference, joy,
   frustration, fatigue, prose taste, or desire to continue.

A stronger class is not required when a weaker class already resolves the
decision. A weaker class must not impersonate a stronger one.

## Adversarial evaluator

The evaluator begins from the null hypothesis:

> Auteur adds bureaucracy without enough compensating value.

It should actively try to find:

- repeated or redundant approvals;
- state-management ceremony presented as creative work;
- duplicated author input;
- internal terminology exposed before the author has a problem requiring it;
- unclear next actions;
- hidden escape hatches;
- places where plain Markdown + a capable LLM is materially simpler;
- places where Auteur's continuity machinery solves no demonstrated problem;
- places where Auteur prevents or repairs state/continuity errors that a plain
  conversational baseline would require the writer to manage manually.

The evaluator must distinguish observed evidence from interpretation.

## Persona suite

### P1 — Discovery writer

Goal: obtain prose before committing to story architecture.

Task:

    rough premise
    + first-scene intent
    -> prose
    -> substantial edit
    -> unplanned character
    -> unplanned place
    -> continue toward shaping

Do not instruct the persona which reconciliation action to use.

Questions:

- Can prose exist before Story setup/Structure acceptance?
- Are inferred structures visibly provisional?
- Does editing preserve the working scene?
- Are discoveries observations rather than automatic commitments?
- Can one discovery be carried forward without carrying all discoveries?

### P2 — Planner

Goal: understand direction before prose.

Task:

    ambiguous premise
    -> interpret
    -> choose direction
    -> choose/review story shape
    -> plan Chapter 1
    -> prose

Questions:

- Are extra interactions attached to meaningful interpretation/choice rather
  than lifecycle ceremony?
- Does the compressed path preserve customization?
- Does the existence of Quick Draft make Shape First redundant, or do the
  paths serve different authoring tempos?

The simulation may support the two-tempo architecture. It cannot establish
which path a real population prefers.

### P3 — Uncertain beginner

Constraint: the persona does not know Auteur's internal architecture or terms
such as canon, provenance, reconciliation, realization, or semantic owner.

Task:

    rough premise
    -> first useful understanding
    -> first meaningful decision
    -> prose

Evaluator checks:

- whether primary actions are understandable in ordinary story language;
- whether internal terms are required to proceed;
- whether advanced terminology appears only after a perceptible problem;
- whether the persona must guess about authority/state.

Static source terminology counts are only flags for inspection, not proof of
human visibility or comprehension.

### P4 — Chaotic writer

Reference setup:

    Detective Miller investigates Suspect Vance.

During prose introduce:

    Sister Beatrice
    +
    an abandoned seaside convent

Then edit after review evidence exists.

Do not tell the persona to reconcile.

Questions:

- Is prose preserved?
- Does changed prose invalidate stale review truthfully?
- Are old findings hidden as current?
- Is a meaningful keep/update/diverge/revise choice available?
- Does keeping prose avoid silent upstream mutation?

### P5 — Change-my-mind writer

After accepted/planned Chapter 1 work, change a meaningful premise-dependent
decision, for example:

    the presumed antagonist is the protagonist's older sister
    and eventually becomes an ally

Measure mechanically where possible:

- accepted work preserved;
- changed intent can be stated in story language;
- historical accepted prose remains distinguishable from future intent;
- later context can still see accepted prior Chapters/state;
- number of mandatory administrative steps before productive work can resume.

Any statement that the sequence feels low-friction remains a human claim.

### P6 — Minimalist baseline user

Use Markdown + a capable general-purpose LLM.

This condition requires a provider and therefore belongs to #310 / a compatible
provider-capable environment.

Do not reproduce Auteur's internal state machine manually for the baseline.

## Blind longitudinal comparison

When provider execution is available, use one controlled six-Chapter story for
both Auteur and the general-purpose baseline.

Inject at predetermined points:

1. a new important character;
2. a changed relationship;
3. a revelation moved earlier;
4. an obsolete old plan;
5. a newly accepted event;
6. an intentionally ambiguous fact.

Evaluate externally observable outcomes:

- Chapter N retention of Chapter N-2 accepted facts;
- changed-intent propagation;
- whether obsolete planning overrides accepted prose;
- whether unaccepted suggestions become facts;
- contradictions with accepted story state;
- amount of manual reminding/restating required from the simulated author.

Do not ask the evaluator which interface it likes.

## Machine-checkable probe

Run:

    python scripts/beginner_adversarial_simulation_probe.py --json

The probe currently establishes:

- old/compressed/Quick Draft designed interaction counts;
- zero Quick Draft acceptance actions before prose;
- provisional Quick Draft authority;
- intentionally vague POV/location remaining open;
- Sister Beatrice + convent discovery detection;
- explicit selection before discovery carry-forward;
- noncanonical handoff;
- stale-review detection after prose edits;
- suppression of stale findings as current evidence;
- current prior-Chapter/realized-state context visibility.

The probe deliberately records a claim ceiling.

## Decision use

After the synthetic run, classify unresolved #305 questions into:

### RETIRED BY SYNTHETIC/MECHANICAL EVIDENCE

Further human study would not change the next implementation responsibility.

### SHARPENED BUT NOT RETIRED

Synthetic evidence narrows the question but a human answer could still change
foregrounding, wording, or interaction behavior.

### HUMAN-ONLY AND DECISION-CHANGING

A real participant is still needed before selecting the next responsibility.

### HUMAN-ONLY BUT NOT CURRENTLY DECISION-CHANGING

Record as post-construction calibration rather than blocking the frontier.

## Stop rule

Do not run a broad human study merely because some human-only claims remain.

Ask instead:

> Could a plausible human answer to this remaining question change whether the
> repository should proceed to F2 + X3, or change the bounded implementation
> responsibility selected before it?

If no, the question is not a blocking gate.

## Claim ceiling

This protocol cannot establish:

- real-user preference;
- felt ownership;
- joy;
- frustration;
- cognitive fatigue;
- prose taste;
- actual willingness to continue;
- market value;
- real-provider prose quality;
- six-Chapter longitudinal coherence before that experiment runs.

Synthetic evidence should be used to reduce uncertainty, not relabel it.


---

## Current architecture reconciliation

This protocol was authored against an earlier head of PR #314. Current #314
adds product-contract refinements but no runtime changes to the surfaces this
probe exercises.

The current evidence-routing rule is therefore:

```text
this simulation
-> qualify agent/mechanical claims

#310
-> qualify provider behavior

#305
-> human calibration only when its remaining subjective answer can still change
   the next repository responsibility

#313
-> decide contradiction / reaffirmation and activate F2 + X3 when warranted
```

Do not rerun the same broad persona suite merely because #314 documentation
advanced.
