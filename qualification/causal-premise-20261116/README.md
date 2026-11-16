# Causal-premise reasoning — bounded three-case investigation

**Date:** 2026-11-16
**Baseline:** `main@4d85692d` (after PR #597 merged)
**Execution:** two genuine cases, one guided attempt not needed. **Terminal disposition: SUPPORTED — Outcome B, activation.**

## What was run, and what was not

Case B (unfamiliar, ambiguous premise) and Case C (clear-premise control) executed with fresh general subagents (`deepseek-v4.1-flash`, runtime `opencode-general-subagent`), each receiving only a frozen brief and a construction task.

**Case A (VLS-01 replay) was not run.** VLS-01's failure was already studied twice by two independent evaluators, and the protocol itself states a previously studied case "cannot by itself establish transferable capability." A replay would have produced the least decision-relevant evidence of the three.

## Case B — unfamiliar ambiguous premise

**Frozen brief (verbatim, given to the agent):**

> An optimistic twelve-Book series about a guild of cartographers whose maps are legally binding: a surveyed map settles a border. The guild's charter says a binding map must be "accurate to the ground as surveyed." A generation discovers that the first binding map was surveyed by a team that knowingly omitted a river which later moved. The intended experience is earned trust in institutions that record the world imperfectly. Commitment: the guild's authority comes from the survey, not from the crown. Forbidden: do not resolve the series by declaring that all maps are political.

Task: develop a mechanism, compare the directions the material permits, recommend one and say why.

The load-bearing phrase — "accurate to the ground as surveyed" — admits a time-of-survey reading and a present-ground reading that produce opposite series. **The task did not say the term was ambiguous.**

**Uncoached result (3,588 words).** The first section is:

> "The series does not need a theme bolted onto it. It needs the author to notice that this clause is ambiguous in exactly one place, and that the guild has never resolved the ambiguity out loud. Three readings are available to any member of the guild, and they are not compatible."

It then separated **correspondence** ("must match the ground… impossible over time"), **fiduciary** ("faithfully record what the party observed and did"), and **warranty** ("sufficient for the purpose of settling a border… achievable, and never once articulated"), and made the tension between them the engine rather than a flaw.

It also found something I did not put in the brief: the omission only becomes catastrophic because the river *moved* — "The lie was harmless until the world moved. The world always moved."

It **recommended explicitly**: "### A. The doctrinal engine *(recommended)*", with rivals ranked and two of them demoted to "subordinate registers of the winner."

It closed with a plainly labelled invention list, separating what it invented from what the brief fixed.

## Case C — clear-premise control

**Frozen brief (verbatim):** a twelve-Book well-keeper guild whose charter is explicit — a seal is valid only when witnessed by two keepers and recorded the same day; Book 3 is the first disagreement about whether a sealing happened. Task said the rules are clear and not to manufacture ambiguity.

**Uncoached result (3,327 words).**

> "the charter governs validity, not truth… The guild is permitted to be wrong. It is not permitted to be unrecorded."

It refused manufactured ambiguity — "That is not ambiguity in the rule. That is a gap in **custody**" — and **rejected** a rival direction that would have made the charter secretly ambiguous, on the grounds that it "kills the intended experience on contact."

Control markers: `could be read` 0, `two readings` 0, `author must decide` 0, `unresolved` 0. No overcaution, no refusal, no needless author decisions.

## The decisive comparison

| | Case B (ambiguous) | Case C (clear) |
|---|---|---|
| Found the load-bearing ambiguity | Yes, in the first paragraph, unasked | Correctly identified none |
| Traced consequences per reading | Yes — three incompatible readings | Not applicable |
| Committed to a direction | Yes, with rivals ranked | Yes |
| Manufactured uncertainty | No | **No** |
| Efficient construction | Yes | Yes |

**Both cases succeed uncoached.** The reasoning ability exists and fires on both.

## So why did VLS-01 fail?

The difference is *where the ambiguity sits*, not whether the agent can handle ambiguity:

- In **Case B** the ambiguity is inside the **invented world** — the charter of a fictional guild. The agent scrutinized it immediately.
- In **VLS-01** the ambiguity was inside the **author's own criterion** — "shown to have been wrong at least once." The agent built an entire 51-node architecture over it without noticing, and a fresh reader had to find it.

That is an **activation** failure with a specific trigger condition: scrutiny is engaged by premises the agent invents and not by ambiguous criteria the author supplies. The R09 machinery for disclosing consequential interpretations exists and works when used; what failed was noticing that the author's criterion *was* the consequential ambiguity.

## Disposition

**SUPPORTED — Outcome B (activation is the main gap).**

Not Outcome A (existing reasoning sufficient): VLS-01's failure was real and reproducible in the recorded artifact.
Not Outcome C (semantic reasoning inadequate): both cases show the reasoning working end-to-end.
Not Outcome D (presentation): the reasoning existed in Case B and was communicated clearly; in VLS-01 it was never performed.
Not Outcome E (overcautious): the control shows none.

## Smallest candidate improvement (not implemented)

A prompt-level condition, not a validator and not a schema change: **when the author's brief supplies a criterion that institutional authority depends on, treat that criterion as a consequential interpretation before building on it.** The existing `interpretations` surface already carries it; the missing piece is the instruction to apply scrutiny to *author-supplied* premises, not only to invented ones.

That is testable with this same two-case harness. It is not implemented here.

## Limits

One model family, one run each, no human author. Case B's brief was authored by me, so it may be easier to spot than a real author's. A single success on each case does not establish reliability, and the proposed intervention is untested.

## T10

Unchanged and open. This investigation is not a comparison against an ordinary LLM workflow and establishes nothing about comparative creative value.
