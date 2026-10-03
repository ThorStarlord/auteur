# Beginner Adversarial Agent Simulation Findings v1

**Date:** 2026-10-03
**Tracking:** #316
**Evidence class:** synthetic agent/repository evidence
**Human participants:** 0
**Baseline:** PR #314 / #309 candidate stack

## Status

Initial repository-grounded adversarial synthesis. The companion probe and
regression test are the machine-checkable evidence surface. Exact-head CI must
be green before the mechanical results below are treated as qualified for this
branch.

## Existing evidence reused

This simulation does not restart from zero. Auteur already has:

- repeated premise-to-StoryIdentity synthetic persona/stress runs;
- mutation-challenge evaluator rehearsals;
- a premise-to-Chapter-2 scripted simulation that previously discovered a real
  workflow projection defect and verified its repair;
- owner-authorized synthetic acceptance for the earlier Beginner coherence
  package;
- current Quick Draft ambiguity, discovery, handoff, stale-review, and
  post-draft reconciliation tests;
- current designed entry-flow counts of roughly 22 / 8 / 2 interactions to
  visible prose.

The relevant remaining question is therefore not "have we tested the user
journey at all?" It is "which claims still require real humans after the
synthetic evidence is exhausted?"

## Finding 1 — The 22-interaction baseline is no longer a live product candidate

**Disposition:** RETIRED BY MECHANICAL EVIDENCE for default-path construction.

The current product has mechanically compressed the old approximately
22-interaction route to an approximately 8-interaction Shape First route, while
Quick Draft can reach working prose after two author inputs and zero Story
setup/Structure acceptance actions.

This does not prove that eight interactions are optimal. It does establish that
the old ceremony level is not necessary to preserve the current authority model.

**Implication:** do not spend human-attention budget deciding whether to restore
the old approval density.

## Finding 2 — Shape First and Write First remain meaningfully distinct tempos

**Disposition:** SYNTHETIC SUPPORT / HUMAN FOREGROUNDING STILL OPEN.

Write First uniquely provides:

    premise + first-scene intent
    -> working prose

before Story setup/Structure acceptance.

Shape First uniquely provides interpretation and explicit direction/shape work
before prose.

The two paths therefore solve different task orderings. Synthetic evidence does
not support deleting either path merely to choose one universal flow.

**Human-only remainder:** which tempo should be visually foregrounded for
different real authors, if either should be the default.

That is a calibration question, not evidence that the two-tempo architecture is
wrong.

## Finding 3 — Quick Draft authority risk is substantially bounded mechanically

**Disposition:** RETIRED AS A STRUCTURAL AUTHORITY BLOCKER.

The current implementation marks Quick Draft scaffolding
inferred_provisional, creates no accepted root Story Identity/Blueprint/Bible
or final Chapter artifact, and requires explicit selection before discoveries
are carried into shaping.

The deliberately vague case leaves POV and location blank instead of inventing
accepted values.

**Important residual risk:** provisional StoryIdentity scaffolding still
contains generic inferred defaults used to construct the drafting context.
#310 must inspect whether those defaults leak into real-provider prose despite
their noncanonical status.

That is a provider-behavior question, not an authority-owner defect established
by current synthetic evidence.

## Finding 4 — The messy-writer path is mechanically much stronger than the
original risk suggested

**Disposition:** RETIRED AS A DATA-LOSS / STALE-TRUTH BLOCKER.

The current path can preserve edited prose, detect Sister Beatrice and the
abandoned seaside convent, invalidate review freshness when draft bytes change,
hide stale findings as current evidence, and carry only explicitly selected
discoveries into shaping.

For normal post-draft reconciliation, keeping a draft can accept Expression
through the existing owner while emitting noncanonical proposals to lower
semantic owners rather than silently rewriting Story Identity/Structure.

**Human-only remainder:** whether the explicit reconciliation moment feels like
helpful reflection or administrative maintenance.

## Finding 5 — "What did we discover?" remains the strongest first-session UX risk

**Disposition:** SHARPENED BUT NOT RETIRED.

Mechanically, the discovery boundary is correct:

    heuristic observation
    != author commitment

But correctness does not answer whether surfacing discovery after ordinary
drafting creates too much ceremony.

The next synthetic/persona test should therefore try to proceed naturally
without telling the persona that the discovery action exists and record whether
the recovery path is inferable from the visible interface.

A human test is warranted only if the answer could change whether discovery
review is foregrounded, ambient, or deferred.

## Finding 6 — The remaining unique value question moves toward longitudinal
coherence

**Disposition:** STRONG SYNTHETIC SUPPORT FOR F2 AS THE NEXT PRODUCT TEST.

A general-purpose LLM is already very strong at:

    idea
    -> conversation
    -> first draft

Auteur's distinctive machinery is intended to matter when the story accumulates
accepted history, discoveries, changes of intent, and later planning.

The current context projection can mechanically expose accepted prior Chapters
and realized state to later work. That is necessary but not sufficient evidence
for useful long-form coherence.

It does **not** establish:

- relevance selection across a six-Chapter book;
- whether old Structure incorrectly dominates accepted prose;
- whether pending updates create excessive blocking;
- whether continuity help is perceptible to the author;
- whether the system outperforms a plain LLM baseline on accumulated state.

These are precisely the questions F2 + X3 is designed to test.

## Finding 7 — A full generic #305 study should not automatically block F2/X3

**Disposition:** REVISE EVIDENCE STRATEGY.

Use:

    existing synthetic evidence
    +
    #316 adversarial synthetic evidence
    +
    #310 provider evidence
    -> provisional #313 reconciliation

Then ask which remaining human-only questions can still change the next
repository responsibility.

If the remaining questions are limited to:

- preference between two already-supported tempos;
- felt ownership;
- emotional reaction;
- wording/polish;
- desire-to-continue calibration;

and no plausible answer would change the decision to test longitudinal value,
then a broad #305 study should become a narrower calibration rather than a hard
construction gate.

Do **not** mark #305 complete from synthetic evidence. Change its role only
through explicit reconciliation.

## Current provisional answers

### Is the old flow too ceremonious?

Strong synthetic/mechanical evidence says yes for a default Beginner path.

### Is compressed Shape First directionally supported?

Yes, mechanically and architecturally. Human evidence may tune wording/defaults.

### Should Quick Draft replace Shape First?

No synthetic evidence supports that. The two-tempo model remains better
grounded.

### Does Quick Draft structurally seize authorship?

Current authority mechanics strongly argue no. Felt ownership remains human.

### Is discovery reconciliation still risky?

Yes, primarily as an interaction-cost/attention question rather than a
data-integrity question.

### Where is Auteur most likely to justify its machinery over Markdown + LLM?

Longitudinal coherence, change propagation, and accumulated story-state
management, not first-prose generation alone.

## Human-only questions that may still matter

1. Does post-draft discovery review feel like useful reflection or maintenance?
2. Does a real beginner understand the current ordinary-language primary actions
   without facilitator rescue?
3. Does either tempo materially damage felt authorship?
4. Does real-provider prose feel useful enough to react to?
5. After continuity actually matters over multiple Chapters, can the author
   perceive value without learning internal machinery?

Questions 1–3 may be calibrated with a narrow human session if #313 determines
they could change the next bounded responsibility. Question 4 belongs first to
#310. Question 5 belongs naturally to F2 + X3 and should not be overclaimed from
Chapter-1 testing.

## Provisional recommendation to #313

Unless #310 exposes a provider-level contradiction, proceed toward a
**provisional F2 + X3 qualification** after this synthetic package is qualified.

Do not treat missing broad human preference data as a reason to invent another
first-session feature.

Reserve human-attention budget for the smallest remaining subjective question
whose answer could actually change the next implementation responsibility.

## Claim ceiling

These findings are simulation hypotheses plus repository/mechanical evidence.
They are not human usability research and do not establish real-user preference,
emotion, fatigue, prose taste, or market value.
