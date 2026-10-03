# Beginner Ergonomics Entry-Flow Comparison Protocol

**Date:** 2026-10-03  
**Implementation candidates:** PR #304 / #307 / #309  
**Purpose:** compare architecture-first compression, write-first Quick Draft, and a low-ceremony general-purpose baseline without reducing author control  
**Evidence class:** product ergonomics / real-author observation

## Conditions

Use the same participant and the same or equivalently unfamiliar premise where practical.

### A — Corrected pre-compression Auteur

Use the pre-compression Beginner experience with the candidate-prose visibility repair applied.

Expected uncomplicated path:

```text
premise
-> architecture interpretation
-> direction select
-> direction accept
-> identity accept
-> 3 Structure decisions + navigation/review
-> Structure accept
-> outline propose/accept
-> chapter plan propose/accept
-> scene plan propose/accept
-> draft handoff
-> draft
-> Chapter review / prose
```

Mechanical baseline: approximately 22 visible interactions.

### B — Compressed Auteur

Use PR #304.

Expected uncomplicated path:

```text
premise
-> Explore this story
-> That feels right
-> Use this direction
-> Yes, keep going
-> Use recommended story shape
-> Plan Chapter 1
-> Draft Chapter 1
-> prose visible
```

Mechanical target: approximately 8 visible interactions.

### C — Quick Draft

Use the write-first path from PR #309.

Expected uncomplicated path:

```text
premise
+ first-scene intent
-> Start writing now
-> prose visible
```

The participant may then edit freely, use **What did we discover?**, explicitly
select any ideas to carry forward, and choose **Shape this story**.

Before prose, Quick Draft performs zero explicit Story setup / Story shape
acceptance actions.

### D — Markdown + capable general-purpose LLM

Use a plain document plus a capable general-purpose conversational model.

Do not manually recreate Auteur's state machine or feed it hidden Auteur artifacts.

Give the participant the same creative objective: start from the premise and
reach a Chapter 1 draft they would genuinely consider continuing.

## Participant instruction

Tell the participant only:

> You have a rough story idea. Use this tool the way you naturally would to
> understand the story and get to a Chapter 1 draft. Think aloud when something
> confuses you, interests you, or makes you want to change direction.

Do not teach Auteur's vocabulary in advance.

Do not tell the participant which condition is expected to be better.

## Observer rules

Record behavior separately from interpretation.

For every meaningful interaction classify:

- **CREATE** — author creates or discovers story material;
- **CHOOSE** — author makes a meaningful creative decision;
- **INSIGHT** — the tool materially improves understanding;
- **NAVIGATE** — movement between useful surfaces;
- **APPROVE** — author ratifies generated work;
- **ADMIN** — state management with no immediate creative payoff;
- **GENERATE** — author requests derived material.

Do not infer emotion from silence alone.

Quote participant statements exactly when practical.

## Core measurements

Record:

```text
condition:
participant:
premise:
start_time:
time_to_first_useful_insight:
time_to_first_visible_prose:
total_visible_interactions:
CREATE:
CHOOSE:
INSIGHT:
NAVIGATE:
APPROVE:
ADMIN:
GENERATE:
max_APPROVE_or_ADMIN_run_between_payoffs:
customization_opened:
step_by_step_planning_opened:
backtracks:
external_tool_escape:
author_wants_to_continue:
```

### First useful insight

Count only when the participant indicates that the tool surfaced something they
had not already consciously formulated.

Examples:

- "Oh, that's interesting."
- "I didn't think of it that way."
- "Yes, that's what the story is actually about."

Do not count merely presenting information.

### External-tool escape

Record when the participant wants to leave the current product to use:

- a blank editor;
- another chat window;
- notes;
- a different writing tool;

because the current interaction is blocking or slowing their creative intent.

## Required qualitative prompts

Ask only after the uninterrupted task:

1. Where did you hesitate?
2. What was the first thing the tool did that felt genuinely useful?
3. Did anything feel like paperwork or approval ceremony?
4. Was there a point where you wanted to skip ahead and write?
5. Did you feel you were making the story, or approving a story the tool made?
6. When you disagreed with the tool, could you find how to change it?
7. Would you continue this story in this tool right now? Why or why not?

## A vs B decision questions

The compressed candidate is supported when evidence shows that it:

- materially reduces APPROVE/ADMIN interactions;
- reaches prose faster without eliminating meaningful CHOOSE moments;
- preserves the participant's sense of authorship;
- keeps customization discoverable when wanted;
- does not create confusion about what **Use this direction**, **Use recommended story shape**, or **Plan Chapter 1** will do.

Do not treat fewer clicks alone as a win.

## B vs C decision questions

Compare **shape-first** and **write-first** Auteur directly.

Observe whether C:
- reaches useful prose before the participant wants more planning;
- preserves authorship despite inferred provisional scaffolding;
- keeps ambiguous POV/setting comfortably open;
- lets the participant understand **What did we discover?** without feeling that
  heuristic observations are decisions;
- makes **Carry this idea into story shaping** feel explicit rather than
  bureaucratic;
- re-enters story shaping without forcing the writer to repeat the scene's useful
  discoveries.

Also observe whether B produces earlier useful insight that justifies its extra
pre-prose interaction.

## Auteur vs D decision questions

Auteur earns its additional machinery when the participant can point to benefits
such as:

- stronger long-range continuity;
- more specific story insight;
- clearer consequences of choices;
- safer change-of-mind behavior;
- better preservation of prior commitments;
- useful connections the general-purpose LLM missed;
- greater confidence that future chapters will remain coherent.

If the participant prefers D, record the concrete reason rather than reducing it
to a numeric winner.

## Change-my-mind stress

After a Chapter 1 candidate exists in condition B, introduce one material change:

- change intended tone;
- change protagonist desire;
- turn the presumed antagonist into an ally or relative;
- promote an unplanned side character;
- move a revelation substantially earlier.

Observe:

- whether the participant can state the new intent naturally;
- whether the UI leads with story consequences rather than internal lifecycle terms;
- number of visible interactions required before creative momentum resumes;
- whether the participant wants to abandon existing state and restart elsewhere.

## Messy Writer / Creative Discovery stress

Run this stress against both the compressed Auteur condition and Quick Draft / its post-draft handoff where applicable.

### Setup

Use a minimal premise with two modeled characters:

```text
Detective Miller investigates Suspect Vance.
```

The accepted/planned Chapter 1 should not contain Sister Beatrice or the
abandoned seaside convent.

### Author action

During drafting, introduce both:

- an unmodeled character: **Sister Beatrice**;
- an unmodeled setting: **an abandoned seaside convent**;

and materially move the scene away from the planned location/path.

Then attempt to save, keep, reconcile, revise, or proceed.

### Observe

Record:

- whether the prose is preserved;
- whether validation is automatically re-run or incorrectly reused;
- whether review evidence is bound to the exact candidate bytes;
- whether the system classifies the difference as additive discovery, plan
  divergence, or hard contradiction;
- whether the Browser exposes **Keep draft & update story**;
- whether **Keep as intentional divergence** is reachable;
- whether revision remains available;
- whether the UI describes the story change before technical diagnostics;
- whether accepted prose can leave realized/Bible/model state silently behind;
- whether the author is forced to erase a useful discovery merely to proceed.

### Mechanical pass condition

The flow mechanically passes when:

```text
unexpected idea
-> prose preserved
-> current validation state is truthful
-> author receives a meaningful choice
-> no silent upstream mutation
-> no forced loss of the new idea
```

A new character or location that does not contradict accepted canon must not be
presented as malformed data merely because it was absent from planning.

A hard contradiction may require explicit resolution, but the UI must present
the conflicting story facts and available author decisions rather than a raw
schema/validator failure.

### Human evidence question

Ask after the stress:

> When you introduced Sister Beatrice and changed the setting, did Auteur feel
> like it was helping you incorporate a discovery, or telling you that your idea
> was invalid?

The answer is subjective evidence and must not be inferred from mechanical
success alone.

## Stop rules

Stop a session when:

- Chapter 1 prose is visible and the participant has reacted to it;
- the participant voluntarily abandons the tool;
- an actual product error prevents continuation.

Do not coach through confusion unless the participant explicitly asks for help.
Record the confusion first.

## Claim boundaries

A headless/static contract may establish:

- action availability;
- interaction count on the designed default route;
- presence of customization escape hatches;
- visibility of prose.

Only real participant observation may establish:

- lower cognitive load;
- lower experienced bureaucracy;
- increased creative momentum;
- higher confidence;
- stronger ownership;
- preference;
- desire to continue.

## Result dispositions

After at least one serious real-author pass, record one of:

### COMPRESSION_SUPPORTED

The reduced interaction model removes material friction without meaningful loss
of author control.

### WRITE_FIRST_PATH_SUPPORTED

Quick Draft creates useful early momentum, keeps provisional inference
reversible, and returns to story shaping without unacceptable intent distortion.

### BOUNDED_ERGONOMIC_REPAIR

The selected flow is directionally correct but one specific surface or bundled
action causes confusion and warrants a small repair.

### CUSTOMIZATION_DISCOVERABILITY_GAP

The default path works, but authors cannot easily find deeper control when they
need it.

### CREATIVE_DISCOVERY_RECONCILIATION_GAP

The writer can create useful unexpected material, but Auteur either treats it as
an error, silently loses model coherence, or fails to offer a clear update-story / intentional-divergence / revise choice.

### WRITE_FIRST_PRESSURE_CONFIRMED

Repeated evidence shows authors need to write/explore before the remaining
required story commitments can be made. This is the evidence threshold at which
a Creative Scratch / Riff experiment becomes warranted.

### PRODUCT_THESIS_REVIEW_SIGNAL

Repeated evidence indicates that neither the compressed story-design-first flow nor the write-first Quick Draft flow creates differential value over Markdown + a capable general-purpose LLM. This is a signal for a separate higher-level review, not an automatic
thesis change.
