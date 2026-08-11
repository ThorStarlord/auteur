# Solution Discovery — Cross-Goal Significance: Synthesis

> Cycle `discovery/cross-goal-significance` (base f9124ffa, merged main incl. PR #67).
> Zero production change. Evidence: `evidence-package.md` + per-control
> `decision.yaml`/`evaluate.txt`. Problem per the human's selection (solution-free);
> mechanism families compared per the brief; exclusions treated as "not assumed", never
> "forbidden" — the cycle was required to be capable of falsifying the current
> reluctance, and F6/S2 were tested on evidence, not dismissed by fiat.

## Discovery question

> **What is the smallest mechanism that helps the author assess or reveal which loss
> matters more in a concrete cross-goal tradeoff, after structural consequences are
> already legible?**

## What the evidence establishes

1. **Causal diagnosis (mechanical):** the shipped product at f9124ffa is
   significance-agnostic. Four controls over identical facts, differing only in authored
   significance prose (priority / no priority / opposite context priorities), produce
   **byte-identical reports** (7 observations, 11 per-alternative findings, 8 composed
   nature_consequences each). The composed tradeoff is legible; the author's significance
   cannot be received (no field) or surfaced (nothing renders it), and prose is rightly
   never parsed. Control 4 (refusal to rank) confirms the product never manufactures a
   preference — a status quo candidate mechanisms must preserve.
2. **The break is significance, not structure:** not missing story representation (all
   goals/relationships represented), not missing composition (fixed by PR #67), not
   (primarily) missing author knowledge — in controls 1/3 the author HAS stated the
   significance; the product cannot receive it. Only control 2's author may be genuinely
   unsettled.
3. **Falsifications (synthetic):**
   - Numeric weights / preference engine (F6): falsified by control 4 (forces ranking
     where the author intentionally refuses) and control 3 (canonical weights cannot be
     context-dependent; decision-local weights reduce to qualitative F1 without evidence
     for numerics).
   - Canonical/global goal priority: falsified by control 3 (significance is
     decision-scoped).
   - Any mechanism REQUIRING a ranking: falsified by control 4 (the product must not
     manufacture a preference because two goals conflict).
   - S2-style additional structural dimension: excluded on evidence for THIS gap (it
     would add another axis to trade off, not help weigh the existing tradeoff); remains
     valid for its own observed breaks (stress Cases 1/3).
4. **Smallest surviving candidates:**
   - **F1** — decision-scoped, nullable, non-ranking authored significance echo: the
     author's own significance declaration becomes representable and is surfaced next to
     the composed tradeoff, never used to rank. Passes control 4 via an explicit
     "unranked / tension intentional" state; passes control 3 by being decision-scoped.
   - **F3** — elicitation with a first-class refusal answer: for control 2's genuinely
     unsettled author; larger (interaction), must not coerce ranking.
   - **F4** — provisional Auteur tradeoff reaction: the heavier alternative, re-entered
     under the parked-hypothesis-B condition (an UNRESOLVED tradeoff, unlike the resolved
     Case E that closed the proposal direction); dismissible without ranking.

## Recommendation

**F1 is the smallest mechanism consistent with the evidence**: it requires only an
authored, decision-scoped significance declaration surfaced non-rankingly — no scoring,
no interaction machinery, no ontology. It directly addresses the causal diagnosis
(product cannot receive or surface significance) and preserves the author-value boundary
(the product echoes the author's own significance; it never decides which loss matters
more). F3 and F4 remain live candidates for the unsettled-author case (control 2), gated
on whether a first slice of F1 proves insufficient. F6 and S2 are falsified/excluded on
this cycle's evidence — recorded as falsified, not forbidden.

## Stop point

Per the brief: causal diagnosis, mechanism-family comparison, falsified
mechanisms/assumptions, smallest surviving candidates, and a recommendation are
recorded. **Human mechanism selection is required before Implementation Design.** No
schema, no code was changed; the shipped surface (merged main incl. PR #67) remains the
product boundary.
