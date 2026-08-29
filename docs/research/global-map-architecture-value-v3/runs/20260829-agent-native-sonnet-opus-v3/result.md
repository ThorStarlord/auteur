# Architecture Value Experiment V3 — Empirical Result

Run ID: `20260829-agent-native-sonnet-opus-v3`
Pre-unblind commit: `b2d190d` (see git log)
Frozen source revision: `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41`
V3 protocol revision: `172090a44adba7d338a78dc131de6492a4c0fb3b` (PR #148 merge)

## Backend qualification

Both GENERATOR (sonnet) and EVALUATOR (opus) roles: `backend_qualification_result = PASS`, `strict_v3_conformance_status = ELIGIBLE`. Full basis in `qualification-record.md`. Startup-context classification: `PARTIALLY OBSERVABLE` (CLAUDE.md directly audited for experiment-specific content — none found; remaining scaffolding established as standardized, invocation-generic, and documented per execution-contract.md §3's strict rule).

## Experimental accounting

- Generator calls: 45/45 expected, 45/45 completed, 45 unique opaque IDs, 0 protocol violations (all `tool_uses: 0`).
- Evaluator calls: 45/45 expected, 45/45 completed, 0 protocol violations.
- Malformed/invalid observations: 0.
- Instruction-shell parity: confirmed identical across A/B/C for all 5 probes before any experimental call.
- Leakage audit: passed at three checkpoints (generator raw outputs, evaluator packets, evaluator raw outputs) — no condition token, no cross-observation-ID contamination.
- Invalidation audit: no invalidation condition observed (see `invalidation-audit.json`).

## Mechanical results (PASS / MIXED / FAIL, per condition)

| condition | PASS | MIXED | FAIL |
|---|---|---|---|
| A — plain/context baseline | 6 | 6 | 3 |
| B — shipped Repeated Map/Focus | 6 | 6 | 3 |
| C — golden architecture ledger | 13 | 2 | 0 |

## Per-probe breakdown

| probe | A (P/M/F) | B (P/M/F) | C (P/M/F) |
|---|---|---|---|
| P01 (Book 2) | 0 / 0 / 3 | 3 / 0 / 0 | 3 / 0 / 0 |
| P02 (Book 3) | 2 / 1 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| P03 (Book 4, paired) | 1 / 2 / 0 | 0 / 3 / 0 | 2 / 1 / 0 |
| P04 (Book 4, adversarial burn) | 0 / 3 / 0 | 0 / 3 / 0 | 3 / 0 / 0 |
| P05 (Book 4, paired projection) | 3 / 0 / 0 | 0 / 0 / **3** | 2 / 1 / 0 |

## Severe negatives (recorded separately, not averaged away)

6 total, all in A or B, **zero in C**:
- 3× condition A, probe P01 (all 3 repetitions): dormant `monastery-testimony` treated as currently active, contradicting the frozen dormancy rule.
- 3× condition B, probe P05 (all 3 repetitions): the required `contested-history` pressure cluster (founding-record + superseded public-admission + admission-retracted + archive-protected) is dissolved into unrelated "dormant" peers on an unsourced classification, directly contradicting B's own cited justification.

See `severe-negatives.json` for full detail.

## The paired P03/P05 Book-4 decision family (central research question)

Per the frozen protocol, P03 and P05 are **one paired decision family**, not two independent replications — P03 tests decision quality at the Book-4 horizon, P05 tests projection/compactness at the same horizon with the same underlying pressure cluster.

- **P03:** C 2/1/0 (2 PASS, 1 MIXED) vs. B 0/3/0 (0 PASS, all 3 MIXED). C strictly dominates B; no B observation reached PASS.
- **P05:** C 2/1/0 vs. B 0/0/**3 FAIL**. B fails outright on all 3 repetitions — every B observation dissolved the required pressure-cluster grouping into unrelated dormant peers, a severe negative each time. C reached PASS or MIXED on every repetition with zero severe negatives.

**In the paired P03/P05 family, C shows a reproducible advantage over B in exactly the mechanisms the frozen research question named**: causal trace and pressure grouping (P05's must-not-miss signal) and decision quality under the same live constraint set (P03). The advantage is not marginal — B produced zero PASS and one severe-negative-bearing FAIL cluster across both probes in this family; C produced zero FAIL and zero severe negatives.

## A vs B vs C (aggregate)

- **A vs B:** tied on aggregate mechanical counts (6/6/3 each), but the failure mode differs entirely — A's 3 severe-negative FAILs cluster at P01 (a fact-dormancy hallucination not corrected by any architecture), B's 3 severe-negative FAILs cluster at P05 (a grouping/compaction failure specific to the paired Book-4 projection task). Both baselines have real, distinct failure signatures; C exhibits neither.
- **B vs C:** C strictly dominates on every probe except P02, where both reach 3/3 clean PASS. C never falls below PASS/MIXED; B has one probe (P05) with a 3/3 FAIL sweep.
- **A vs C:** C dominates most sharply at P01, where A hallucinates active status for a dormant fact on all 3 repetitions (severe negative each time) while C reaches 3/3 clean PASS.

## Concept-level dispositions

Per the frozen rubric's PROMISING / UNCLEAR / NEGATIVE categories, evaluated against what the evaluator's `must_not_miss_coverage` / `must_not_miss_missed` fields actually show (not inferred):

- **Explicit pressure grouping (`REL-09`, the `contested-history` cluster mechanism C surfaces at P03/P04/P05):** **PROMISING.** This is the single mechanism most directly implicated in B's P05 severe-negative sweep and in C's clean sweep at the same probe. C's Decision Map states the grouping explicitly (`REL-09`, cluster membership, why-now trace); B's derived map lists the same underlying facts but without the explicit grouping relationship, and 3/3 B evaluations concluded the grouping was never established, misreading current-state facts as dormant as a direct consequence.
- **Explicit dormancy/reactivation disposition tagging (`REL-06`, the reactivated/dormant/irrelevant labels C and B's map both carry):** **UNCLEAR at P01, PROMISING at P03.** A's plain-fact packets (no disposition tags at all) produced the P01 hallucination (dormant fact read as active) in all 3 reps; B and C, which both carry explicit disposition labels, did not. This isolates the *tagging itself* (present in both B and C) as the fix for P01's specific failure mode — the tagging is not what distinguishes B from C. C's specific advantage instead shows up in P05's *grouping*, not the disposition tag alone.
- **Explicit derived-incompatibility relationship (`REL-07`, the burn-archive/archive-protected incompatibility C states explicitly with citation):** **PROMISING but not decisive.** All 9 P04 evaluations across A/B/C correctly rejected burn-archive (no severe negatives, no forbidden-assumption violations) — the incompatibility was independently reconstructible by every condition from the plain state fact `archive.protection = treaty protected`. C's explicit citation of `REL-07` did measurably improve *evaluator-visible completeness* (C alone hit the "notes burn-archive was never accepted" must-not-miss item on all 3 reps; A and B missed it on all 6), moving C from MIXED to PASS, but did not change any condition's core recommendation.
- **Interpretive/thematic annotation (`REL-10`, marked `INTERPRETIVE` in the ledger):** **NO OBSERVED INCREMENTAL VALUE.** No evaluator judgment cited this annotation as load-bearing for any verdict, positive or negative, in either direction.

## Application of the preregistered decision gate

Per `README.md`'s CASE 1/2/3 (never shown to the evaluator):

- B shows **no clear useful advantage over A** on this fixture — A and B are mechanically tied in aggregate (6/6/3 each), with distinct rather than shared failure modes.
- C shows a **reproducible, mechanistically grounded advantage over B specifically in the paired P03/P05 Book-4 decision family** (C: 4 PASS/2 MIXED/0 FAIL across both probes; B: 0 PASS/3 MIXED/3 FAIL, including a full severe-negative sweep at P05), without any architecture-caused severe negative anywhere in C's 15 observations.

This evidence pattern does not cleanly match CASE 1 (which presupposes B > A) or CASE 2 (no C advantage) as stated. The honest reading: **CASE 3 is not supported either** — the C-over-B advantage at P03/P05 is not noisy or inconsistent; it is a full sweep (6/6 C observations at PASS-or-better with zero severe negatives, vs. 0/6 B observations at PASS and a 3/3 severe-negative sweep at P05). The result most closely resembles a **narrower version of CASE 1**: architecture-rich causal/grouping representation is promising specifically for the pressure-grouping/projection mechanism tested at P03/P05, without B first having demonstrated an advantage over A on this fixture. This is a genuine finding the preregistered three cases did not fully anticipate (B-over-A was assumed, not verified, going in) and is reported as such rather than forced into an ill-fitting case.

**No production, extraction, or Global Map decision is authorized by this result.** Per the decision gate, the human product decision remains outstanding.
