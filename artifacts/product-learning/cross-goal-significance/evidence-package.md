# Solution Discovery — Cross-Goal Significance: Evidence Package

> Cycle: `discovery/cross-goal-significance` (worktree `H:/GithubRepositories/auteur-cross-goal-significance`,
> base f9124ffa = merged main, PR #67 included). Zero production change; no schema; no
> code. Grounded in the post-S1 residual limitation (human judgment DECISION_CLARIFIED,
> recorded @ bef260c). All product runs via the repo `.venv` on the frozen Salt of the
> Earth story; control artifacts authored for this cycle (`decision.yaml` per control;
> verbatim output in `evaluate.txt`).

## Problem (solution-free, per the human's selection)

> **When a choice creates a genuine tradeoff between multiple accepted story goals,
> Auteur can now deterministically expose what each choice preserves and removes, but
> the author may remain unable to decide because the relative significance of those
> competing goals in this decision is not represented or otherwise surfaced.**

## Primary discovery question

> **What is the smallest mechanism that helps the author assess or reveal which loss
> matters more in a concrete cross-goal tradeoff, after structural consequences are
> already legible?**

---

## 1. Causal diagnosis (shipped product, f9124ffa)

Five control artifacts over the SAME represented facts (marta_pregnancy: sustains
`contract.mandatory_ending_tone` + pressures `identity.pov_type`; signe_marriage: the
mirror), differing ONLY in the authored question/criterion prose, which expresses goal
significance. All exit 0 through accept → evaluate.

| Control | Authored significance | Direction | Report (verbatim) |
|---|---|---|---|
| 1 — obvious priority | "the ending-tone goal takes precedence over the POV-contract goal" | cut | 7 obs / 11 per-alt / **8 nature_consequence** |
| 2 — conflicting, no priority | "(No priority is stated between ...)" | cut | 7 obs / 11 per-alt / **8 nature_consequence** |
| 3a — context: ending matters | "ending tone matters more than the POV contract" | cut | 7 obs / 11 per-alt / **8 nature_consequence** |
| 3b — context: POV matters | "POV goal outweighs the ending-tone goal" | cut | 7 obs / 11 per-alt / **8 nature_consequence** |
| 4 — refusal to rank | "the unresolved tension ... is intentional and must be preserved" | none | 7 obs / 11 per-alt / **0 nature_consequence** |

**Diagnosis:** controls 1/2/3a/3b produce **byte-identical reports** — the composed
tradeoff (cut marta removes its sustaining relationship to the ending tone AND its
pressuring relationship to the POV contract; cut signe mirrors) renders identically
regardless of whether the author declares a priority, no priority, or opposite
context-dependent priorities. **The product is significance-agnostic: it cannot receive
the author's significance declaration (no field exists; prose is rightly not parsed),
and it surfaces nothing about significance.** Control 4 confirms the product never
manufactures a preference (no composition without direction; no ranking anywhere) — the
correct status quo that candidate mechanisms must not break.

## 2. Distinction preserved (per the human's brief)

The residual limitation is classified as primarily **missing relative goal
significance** — in controls 1/3 the author HAS supplied the significance (in prose the
product must not read), so it is NOT "missing author knowledge"; in control 2 the
author's valuation may genuinely be unsettled. It is NOT "missing story representation"
(all goals and relationships are represented) and NOT "missing structural composition"
(fixed by PR #67). Whether the product should (a) receive and surface the author's own
significance non-rankingly, or (b) offer an interaction that helps the author discover
it, is exactly what the mechanism comparison must test.

---

## 3. Mechanism families compared (paper + controls; synthetic falsification only)

### F1 — Explicit qualitative goal priority/significance (authored, decision-scoped)
A per-decision authored declaration of relative goal significance (e.g. ordered goals or
a significance statement), consumed NON-rankingly: surfaced as an authored fact next to
the composed tradeoff, never used to rank or score.
- Control 1 (obvious priority): the author's own declaration becomes representable and
  visible — the report could echo "authored goal significance in this decision: ending
  tone > POV contract" alongside the tradeoff. Author applies their own priority to the
  composed losses.
- Control 3 (context-dependent): passes ONLY if decision-scoped. A canonical/global
  priority is **falsified** by 3a-vs-3b (opposite significance in different decisions).
- Control 4 (refusal): passes ONLY with an explicit "unranked / tension intentional"
  state — a REQUIRED priority falsifies F1 here.
- Control 2 (no priority): absent significance = status quo (no surfacing); does not
  force the author to decide.

### F2 — Decision-local tradeoff criterion/comparison
Structuring the existing free-text criterion into a comparison the tradeoff is judged
by. Overlaps F1 (a structured significance statement IS a decision-local criterion); the
distinguishing question is whether it must be orderable (→ F1) or merely stated (→
surfacing without ordering). Controls do not yet discriminate F2 from F1; treated as an
F1 variant unless evidence separates them.

### F3 — Elicitation/questioning (ask the author to resolve the conflict)
The product asks the author to resolve the competing goals, without proposing.
- Control 2 (no priority): the intended beneficiary — the author's valuation is
  unsettled; a question surfaces it.
- Control 4 (refusal): must allow "neither — the tension is the point" as a first-class
  answer; an elicitation that coerces a ranking is **falsified** here.
- Control 1 (obvious priority): unnecessary (the author already knows); an interaction
  that asks anyway adds friction — weak.
- Requires interaction machinery (larger than F1).

### F4 — Reacting to a provisional Auteur tradeoff/choice (parked hypothesis B)
The product makes a provisional tradeoff choice and the author reacts.
- Control 2: the exact "genuinely undecided" condition hypothesis B was parked for; the
  author's reaction ("no — the ending matters more to me") could surface the valuation.
- Control 4: the provisional choice must be dismissible without ranking; if rejection
  forces a ranking, **falsified**.
- Gated by the closed opinionated-proposals cycle: proposals showed no value on a
  RESOLVED case (Case E); this is an UNRESOLVED tradeoff — the condition that hypothesis
  was parked for, so it re-enters as a candidate mechanism, not a revival of the closed
  direction.
- Heaviest interaction option.

### F5 — Another non-ranking way of surfacing significance
E.g., presenting the two-sided tradeoff symmetrically with the significance question
made visible but unanswered; or naming the conflict ("this decision trades ending tone
against POV contract") as an explicit observation. Minimal; the tradeoff naming already
partly exists via composition. Weakest value claim; cheap.

### F6 — Preference/scoring machinery (numeric weights) — CONTROL/FALSIFICATION family
Included only to falsify or benchmark, per the brief.
- Control 4: a scoring mechanism requires a ranking/weight → **falsified** (manufactures
  preference where the author refuses).
- Control 3: canonical global weights cannot vary by decision → **falsified** by
  3a-vs-3b; decision-local weights collapse into F1-with-numbers, and there is no
  evidence numeric representation is needed.
- Control 1: expressible but heavyweight (machinery where a qualitative declaration
  suffices).

## 4. Falsified mechanisms/assumptions

1. **Numeric weights / preference engine (F6):** falsified by control 4 (forces ranking
   where the author intentionally refuses) and control 3 (canonical weights cannot be
   context-dependent; decision-local weights reduce to F1 without evidence for
   numerics). Retained only as a control family for future cycles.
2. **Canonical/global goal priority (any family):** falsified by control 3 — significance
   is decision-scoped (3a vs 3b demand opposite priorities for the same two goals).
3. **Any mechanism REQUIRING a ranking:** falsified by control 4 — the product must not
   manufacture a preference because two goals conflict.
4. **S2-style second structural dimension (stakes/role/causality):** excluded on
   evidence — the gap is significance of EXISTING goals, not an additional
   distinguishing axis; adding an axis would give the author more to trade off, not help
   weigh the existing tradeoff. (S2 remains a valid candidate for its OWN observed
   breaks — stress Cases 1/3 — not for this one.)
5. **"The author lacks knowledge" as the primary break:** falsified for controls 1/3
   (the author HAS stated the significance; the product cannot receive it). Holds only
   for control 2's unsettled case.

## 5. Smallest surviving candidates

- **F1 (decision-scoped, nullable, non-ranking authored significance echo):** the
  smallest mechanism — a per-decision authored significance declaration surfaced
  non-rankingly beside the composed tradeoff; explicit "unranked / tension intentional"
  state for control 4; decision-scoped for control 3. It receives the author's own
  significance without ever deciding.
- **F3 (elicitation with a first-class refusal answer):** the candidate for control 2's
  genuinely unsettled author; an interaction, larger than F1.
- **F4 (provisional tradeoff reaction):** the heavier alternative, re-entered under the
  parked-hypothesis-B condition (a genuinely unresolved tradeoff), dismissible without
  ranking.

## 6. Evidence boundary

All falsifications above are synthetic (product runs + paper mechanism analysis). Any
claim that a surviving mechanism **materially helps an author resolve or clarify** the
tradeoff requires human judgment — per the brief, no such claim is made here. Production
code untouched.
