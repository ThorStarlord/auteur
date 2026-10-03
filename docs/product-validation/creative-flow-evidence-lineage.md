# Creative Flow Evidence Lineage

**Date:** 2026-10-03  
**Status:** durable evidence-method lineage; not an active product roadmap  
**Supersedes active use of:** draft PR #300 / original #299 dogfood lane  
**Current governing surfaces:** #305, #310, #313, #316, #318

## Why this survives

The older Creative Flow lane introduced one measurement idea that remains useful
after the newer Unified Author Experience work absorbed its broader product
principle:

> Do not evaluate creative friction by raw click count alone. Distinguish actions
> that create story value from actions that merely administer system state.

The old lane's strategic slogan, **Freedom Before Commitment**, is already
subsumed by the current author mental model:

    freedom to explore
    !=
    authority to make exploration durable

and by the current experience direction:

    strong internal governance
    +
    minimal visible author administration

This file therefore preserves only the unique evidence method. It does not
restore #300 as the active roadmap, reselect Creative Scratch / Riff, or require
a broad human study before longitudinal qualification.

## Interaction classes

Classify meaningful author actions by the value they create.

### CREATIVE

The author creates, explores, or discovers story material.

Examples:

- writing or substantially editing prose;
- inventing a character, relationship, place, event, or twist;
- changing an intended story direction;
- discovering a motive or implication through drafting.

### INSIGHT

Auteur materially improves the author's understanding of the story.

Examples:

- surfacing a consequence the author had not noticed;
- clarifying why one direction changes the central pressure;
- exposing a continuity contradiction;
- making an implicit story engine legible.

### NAVIGATION

The author moves to a useful task or surface without itself creating story or
insight value.

Examples:

- opening a project;
- moving from review to drafting;
- expanding optional detail;
- returning to the next Chapter.

### ADMINISTRATIVE

The author manages system state without a distinct creative or insight payoff.

Examples:

- repeating an already-understood acceptance solely to advance workflow;
- classifying an idea before classification matters to the story;
- resolving lifecycle terminology rather than a story question;
- confirming bookkeeping that could safely be absorbed by the product.

Administrative actions are not automatically defects. Explicit authority can be
valuable. The test is whether the action protects a meaningful author decision
or merely exposes machinery.

## Primary friction signal

Prefer:

> **administrative interactions between CREATIVE or INSIGHT events**

over raw click count.

Useful supporting observations include:

- time to first useful INSIGHT;
- time to first meaningful prose;
- longest uninterrupted run of ADMINISTRATIVE / NAVIGATION actions;
- repeated restatement of author intent;
- attempts to skip a step;
- terminology requiring explanation;
- ideas with no obvious place to go;
- recovery steps after a change of mind;
- manual continuity reminders;
- manual synchronization work.

Subjective observations such as frustration, ownership, confidence, creative
momentum, or desire to continue remain human evidence.

## Current evidence mapping

The original Creative Flow lane asked whether strict internal authority could
coexist with permissive exploration. Current work has decomposed that question
into more precise evidence responsibilities.

| Original concern | Current owner |
| --- | --- |
| Too much pre-prose ceremony | #304 / #316 synthetic-mechanical evidence |
| Plain-language Beginner surface | #307 / #314 |
| Write before planning | #309 Quick Draft |
| Provisional inference does not become canon | #309 / #316 |
| Messy-writer discovery preservation | #309 / #316 |
| Stale review after prose edits | #309 / #316 |
| Real-provider prose / inference leakage | #310 |
| Human-perceived bureaucracy / ownership | #305 when decision-changing |
| High-order requirements reconciliation | #313 |
| Longitudinal continuity value | #318 F2 + X3 |
| Plain Markdown + capable LLM comparison | #318 with real provider |

## Current interpretation rule

When evaluating a flow, keep these evidence classes separate:

    mechanical reachability
    + authority preservation
    + provider behavior
    + human subjective response
    + longitudinal product value

A pass in one class does not prove the others.

However, human evidence should not be demanded simply because a human-only claim
exists. The current decision rule is:

> Run human calibration now only when a plausible human answer could change the
> next bounded repository responsibility.

Otherwise preserve the question for the frontier where it becomes meaningful.

## Example: Quick Draft discovery review

Current synthetic evidence found a concrete interaction:

    edit Quick Draft
    -> choose "Shape this story"
    -> discovery review appears
    -> select anything to carry forward
    -> choose "Shape this story" again

Mechanically, this protects author authority.

The evidence-method interpretation is:

- first Shape action: NAVIGATION / workflow transition;
- discovery selection: CREATIVE or INSIGHT when genuinely meaningful;
- second Shape action: potentially ADMINISTRATIVE if it only repeats intent.

Whether the sequence *feels* burdensome is human evidence. Whether the second
action exists is mechanical evidence.

This is the intended use of the classification system: identify precisely where
human calibration might matter without pretending subjective experience can be
read from code.

## Example: F2 + X3

For the six-Chapter controlled Book in #318, record not only narrative
continuity failures but also interaction value.

A good longitudinal session should not become:

    Chapter
    -> reconcile machinery
    -> state maintenance
    -> approval
    -> Chapter
    -> reconcile machinery
    -> state maintenance
    -> approval

Prefer:

    write / decide
    -> Auteur absorbs safe bookkeeping
    -> surface only meaningful consequence
    -> continue

The evidence method therefore remains relevant at X3 even though #300 itself is
no longer the active lane.

## Retirement rule for #300

PR #300 should not merge unchanged because its STATUS and roadmap assertions are
superseded by the later unified author-experience architecture and current
evidence topology.

Its unique durable contribution is retained here:

- Freedom Before Commitment lineage;
- CREATIVE / INSIGHT / NAVIGATION / ADMINISTRATIVE classification;
- administrative-between-value-events friction signal;
- claim boundary between mechanical and subjective evidence;
- comparison discipline against Markdown + capable LLM.

Everything else should follow the newer #305 / #310 / #313 / #316 / #318
responsibilities.
