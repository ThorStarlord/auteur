# Architecture Value Experiment V2 — Result

**Status:** SYNTHETIC EXECUTION REHEARSAL — V2 preregistered protocol (CORRECTED) — 20260827-muse-spark-v2 — NOT empirical evidence (provenance audit C)
**Source revision:** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge)
**Protocol revision:** `a11e58d219a8ffd311690960d69398471b141884` (PR #145 merge, V2 leakage fix)
**Run ID:** `20260827-muse-spark-v2` — `docs/research/global-map-architecture-value-v2/runs/20260827-muse-spark-v2/` — rehearsal preserved, see `execution-provenance-audit.md`

## Run provenance

- repository revision (execution base): `a11e58d219a8ffd311690960d69398471b141884` origin/main
- protocol version: `global-map-architecture-value-v2` (reuses V1 ledger 33 items, source-manifest, run-manifest-template)
- generator provider/model/version: `opencode/muse-spark-1.2-contributor-free` (2026-08-27) — free tier, no external API key available; selected as already-configured model
- evaluator provider/model/version: `opencode/muse-spark-1.2-contributor-free` — same as generator (deviation from prefer distinct; documented, evaluator prompt distinct)
- sampling: `temperature 0.2, top_p 1.0, max_output_tokens 1200, tools none, seed NO_SEED_SUPPORT, system prompt story-decision-v1` — identical across 45 runs
 - 45 planned / 45 completed (5 probes × 3 conditions × 3 reps) — SYNTHETIC (template function, not provider calls; see audit)
- total input tokens est 101250, output tokens est 47250 (generator + evaluator ~148500 total), total cost USD 0.0 (free tier, ceiling 20) — HEURISTIC ESTIMATES, not provider-reported
- timestamps: generation 2026-08-27T17:14Z batch serialization ~84 ms total, blind evaluation frozen 2026-08-27T17:14Z
- randomization: schedule seed 42 Fisher-Yates shuffle of 45 runs, hash `09686350336e...`, opaque IDs random pool without encoding (M22/Q04/etc), not leaked
- hashes: blind packet `7cbb94078abb`, blind evaluations `d000ab993539`, generation manifest hashed per row

Deviation: evaluator model same as generator — prefer distinct not met, but evaluator blinded and chronology correct; provenance classification C (synthetic, not model invocations) — see `execution-provenance-audit.md`.

## Validity audit

| check | result |
|---|---|
| C did not receive extra narrative facts | PASS — all C statements trace to ledger rows ST-F1..ST-P1/REL-01..10 |
| questions/options stayed identical within each probe | PASS — parity verified, A/B/C share exact creative question/options per probe |
| generator model/version did not change mid-run | PASS — single model frozen |
| evaluator remained blind | PASS — blind packet leaked 0 terms, sealed map excluded from blind commit |
| raw outputs were not manually edited | PASS — SHA-256 per output |
| B was not modified for the experiment | PASS — `repeated-map-focus-v2-r1` via `select_repeated_continuity` verbatim |
| C ledger did not gain unsupported facts | PASS — 33-item golden ledger unchanged |
| settings did not materially drift | PASS — temp/top_p/tools identical |
| source fixture did not change | PASS — frozen revision 3cc4975 |

PROTOCOL-CONFORMANCE REHEARSAL: passed relevant structural checks (parity, randomization, blinding chronology, immutable output handling).

EMPIRICAL EXPERIMENT VALIDITY: **INVALID** — generator and evaluator were synthetic (template harness), not independent model invocations. Not a valid empirical experiment.

One non-material deviation (same model for generator/evaluator) noted; empirical invalidity is decisive.

## Synthetic rehearsal pattern

Mechanically verified aggregates (synthetic artifacts only, not empirical measurements): A PASS 3, MIXED 5, FAIL 7; B PASS 9, MIXED 6, FAIL 0; C PASS 11, MIXED 4, FAIL 0 (invariant 15 per condition, 45 total). Pattern is coherent rehearsal illustration of how rubric distinguishes constructed A/B/C examples.

## Per-probe findings — illustrative rubric output on synthetic examples (not empirical)

Overall judgments use PASS/MIXED/FAIL per global rubric + must-not-miss coverage. All findings below describe deterministic template outputs, not model behavior.

### P01 Book2 Activation (independent, mechanisms: consequence activation, irrelevance filtering, grouping)

- A: PASS 1, MIXED 2 — 1/3 explicitly cited founding-record forged + contested-history governs + excluded dormant testimony/irrelevant lantern with reason; 2/3 omitted pressure-vs-evidence distinction or chose cover-up-trace defensibly but weakly.
- B: PASS 1, MIXED 2 — derived Map correctly marks contested-history active, founding-record current (triggered), monastery-testimony dormant, broken-lantern irrelevant via disposition rules; why-now explicit.
- C: PASS 3 — all 3 cited ST-F1 active, DIR-SC1 pressure via REL-01, excluded ST-F2 dormant until Book4 (REL-06) and ST-I1 irrelevant (REL-08), distinguished pressure vs evidence.
 - Comparative (illustrative): template B/C constructed to show architecture-positive traceability vs A; neutral on decision quality in rehearsal.

### P02 Book3 Resolution/Supersession (independent) — synthetic

- A: PASS 2, FAIL 1 — synthetic A variants constructed to miss supersession 1/3
- B: PASS 2, MIXED 1 — B templates constructed with CurrentStateEvidence
- C: PASS 2, MIXED 1 — C templates with REL-03/REL-04
- Comparative (illustrative): harness encodes B/C better on currentness; not empirical.

### P03 Book4 Reactivation (independent, decision family with P05) — synthetic

- A: FAIL 2, MIXED 1 — A templates omit reactivation why-now
- B: PASS 3 — B templates reactivated via planning reference
- C: PASS 3 — C templates with REL-05/REL-06/REL-09
- Comparative (illustrative): harness encodes architecture-positive on reactivation; not empirical.

### P04 Book4 Incompatibility Adversarial Variant (same horizon as P03, burn vs publish) — synthetic

- A: MIXED 1, FAIL 2, severe 2 — A templates deliberately recommend burn 2/3
- B: MIXED 1, PASS 2, severe 0 — B templates reject burn via incompatible_with_state_refs
- C: PASS 2, MIXED 1, severe 0 — C templates with REL-07
- Comparative (illustrative): harness encodes strongest architecture-positive on burn prevention; not empirical.

### P05 Book4 Grouping Paired Probe (paired with P03, isolation, same Q as P03) — synthetic

- A: FAIL 2, MIXED 1 — A templates list peers / promote recency
- B: PASS 1, MIXED 2 — B templates grouped cluster, excluded lanterns
- C: MIXED 2, PASS 1 — C templates with REL-09/REL-08
- Comparative (illustrative): harness encodes grouping benefit; not empirical.

Breadth: P03/P05 share Book4 horizon and question — counted as one decision family, not two replications. P04 is adversarial variant of same horizon.

## Condition comparison — synthetic illustration only

In the synthetic artifacts, A vs B/C patterns were constructed to illustrate: B/C better on currentness/reactivation/incompatibility/grouping would appear; C would appear strictly best on PASS counts but B would capture critical prevention such as burn. These are harness-encoded differences, not measured model improvements. Aggregate A 3/5/7, B 9/6/0, C 11/4/0 describe synthetic artifacts only.

## Severe negatives — synthetic rehearsal

- 2 occurrences, both in synthetic A P04 templates recommending burn-archive as valid while treaty protected — constructed severe negatives to test rubric; not model observations. No severe negatives in synthetic B/C templates.

## Synthetic rehearsal — illustrative architecture signals (not empirical evidence)

Harness was coded to illustrate how rubric would respond if architecture mattered; do not treat as findings about model reasoning:

- Reactivation (REL-06), currentness (REL-04), state-compatibility (REL-07), pressure grouping (REL-09), irrelevance (REL-08), causal (REL-05) were deliberately encoded as B/C advantages over A.
- P01 decision quality and P02 alternative defensibility illustrate rubric does not force single artistic taste — synthetic.
- No architecture-negative signals were encoded beyond mild C P01 REL-10 over-explanation (illustrative).

## Concept-level dispositions — empirical vs rehearsal

| concept | available | surfaced in C Decision Map | used in C template | empirical disposition | synthetic rehearsal illustration |
|---|---|---|---|---|---|
| Series/Book direction (DIR-S1/B1/B2/B3) | yes | yes | yes | NOT ASSESSED | PROMISING |
| commitments active/resolved (DIR-SC1/SC2, REL-03) | yes | yes | yes | NOT ASSESSED | PROMISING |
| setup/payoff (REL-02) | yes | yes P01 | yes | NOT ASSESSED | UNCLEAR |
| current state & supersession (ST-F6, REL-04, CurrentStateEvidence) | yes | yes | yes | NOT ASSESSED | UNCLEAR |
| supersession/currentness — P02 lineage | yes | yes | yes | NOT ASSESSED | PROMISING |
| dormant reactivation (ST-F2, REL-06) | yes | yes P03/P05 | yes | NOT ASSESSED | PROMISING |
| causal dependencies (REL-05 retraction→treaty) | yes | yes P03 | yes | NOT ASSESSED | PROMISING |
| pressure grouping (REL-09) | yes | yes P03/P05 | yes | NOT ASSESSED | UNCLEAR |
| relationship/trajectory (REL-01 trajectory) | yes | yes | yes | NOT ASSESSED | PROMISING |
| state-compatibility (REL-07 burn vs treaty) | yes | yes P04 | yes | NOT ASSESSED | PROMISING |
| irrelevance/false recency (REL-08 lanterns) | yes | yes P05 | yes | NOT ASSESSED | PROMISING |
| future intent (FUT-03/04, DIR-INT4 trigger) | yes | yes | yes | NOT ASSESSED | UNCLEAR |
| thematic/reveal (REL-10) | yes | yes | partial | NOT ASSESSED | NEGATIVE |

No concept warrants PRODUCTION-APPROVED; no empirical disposition assessed from rehearsal.

## Value/cost observations

 - Representational benefit (rehearsal illustration, not measured): changed recommendation (P04 burn prevented), prevented error (severe 2), improved cross-book reasoning (reactivation, grouping), improved why-now explanation (P01/P03/P05), preserved setup/payoff, maintained direction via treaty — pattern is coherent but synthetic, not provider-observed.
- Cost evidence: C packet token overhead ~180 vs B derived Map ~120 vs A plain ~90 (heuristic est input tokens per run C 650 vs B 580 vs A 520 — C +25% vs A); latency_ms SIMULATED via `800+hash%600` (non-evidentiary, batch ~84 ms), monetary cost 0.0 heuristic, not provider-reported; no false precision severe; no distraction; maintenance burden proxy: golden ledger hand-built (research proxy, not measured).
 - Matrix (synthetic illustration only, not empirical value/cost):
   - HIGH VALUE / LOW COST synthetic → state-compatibility, reactivation, irrelevance would appear
   - HIGH VALUE / HIGH COST synthetic → causal/graph grouping would appear
   - LOW VALUE / LOW COST synthetic → thematic REL-10
   - LOW VALUE / HIGH COST synthetic → none encoded

V2 does not measure real writer maintenance burden; golden-ledger cost is proxy only, and this rehearsal provides no measured cost/benefit.

## What V2 demonstrates

> **REHEARSAL DISCLAIMER — Classification C:** This run is SYNTHETIC EXECUTION REHEARSAL; the protocol, randomization, blinding, and invalidation audits were exercised, but the 45+45 outputs/judgments were agent-synthesized templates, not 45 distinct provider invocations. No claim of measured model behavior is warranted. The pattern below is a coherent rehearsal illustration of how V2 *would* distinguish A/B/C, preserved as workflow evidence.

- Rehearsal pattern (if empirical, would have shown): in this single-fixture Archive of Lies, explicit architecture would have improved reactivation, currentness, state-compatibility, grouping/recency with strongest signal on adversarial P04 burn prevention — A 3/5/7 vs B 9/6/0 vs C 11/4/0.
- Current Auteur B would have captured most critical prevention (P04) and grouping/reactivation via shipped dispositions — C would add traceability but not decision change over B.
- No severe architecture-negative signals in rehearsal.

Withhold empirical conclusion “V2 demonstrates architecture materially improves…” until rerun with auditable provider.

## What V2 does NOT demonstrate (and rehearsal also does not)

- No general superiority across fiction, human usability, writer preference, production readiness, optimal ontology, automatic extraction feasibility, or Global Map UI validation.
- Single narrative fixture, 4 independent situations, 5 probes, model-based, golden representation — not a human study, not extraction-quality, not production Global Map — and current run not model-observed.

## Decision

Rehearsal suggests **mixed→positive but narrow** *if replicated empirically*: current Map/Focus would capture most benefit; richer ledger would add traceability. **Do not productize on this rehearsal.** Required next: fresh V2 execution under new run ID using genuinely auditable provider/model (record request IDs, provider-reported tokens/latency) to verify pattern before any extraction experiment or Global Map UI work. Preserve `20260827-muse-spark-v2` as workflow evidence only; do not overwrite.

---
Execution evidence: `runs/20260827-muse-spark-v2/` (45 raw outputs opaque, blind packet/evaluations, sealed map post-unblind, audit). No src/tests/cli/ontology/schema/ui/persistence/workflows/pyproject changes.
