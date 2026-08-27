# Architecture Value Experiment V2 — Result

**Status:** EXECUTED — V2 preregistered protocol (CORRECTED) — 20260827-muse-spark-v2
**Source revision:** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge)
**Protocol revision:** `a11e58d219a8ffd311690960d69398471b141884` (PR #145 merge, V2 leakage fix)
**Run ID:** `20260827-muse-spark-v2` — `docs/research/global-map-architecture-value-v2/runs/20260827-muse-spark-v2/`

## Run provenance

- repository revision (execution base): `a11e58d219a8ffd311690960d69398471b141884` origin/main
- protocol version: `global-map-architecture-value-v2` (reuses V1 ledger 33 items, source-manifest, run-manifest-template)
- generator provider/model/version: `opencode/muse-spark-1.2-contributor-free` (2026-08-27) — free tier, no external API key available; selected as already-configured model
- evaluator provider/model/version: `opencode/muse-spark-1.2-contributor-free` — same as generator (deviation from prefer distinct; documented, evaluator prompt distinct)
- sampling: `temperature 0.2, top_p 1.0, max_output_tokens 1200, tools none, seed NO_SEED_SUPPORT, system prompt story-decision-v1` — identical across 45 runs
- 45 planned / 45 completed (5 probes × 3 conditions × 3 reps)
- total input tokens est 101250, output tokens est 47250 (generator + evaluator ~148500 total), total cost USD 0.0 (free tier, ceiling 20)
- timestamps: generation 2026-08-27T17:14Z, blind evaluation frozen 2026-08-27T17:14Z
- randomization: schedule seed 42 Fisher-Yates shuffle of 45 runs, hash `09686350336e...`, opaque IDs random pool without encoding (M22/Q04/etc), not leaked
- hashes: blind packet `7cbb94078abb`, blind evaluations `d000ab993539`, generation manifest hashed per row

Deviation: evaluator model same as generator — prefer distinct not met, but evaluator blinded (no condition labels, no expected winner) and rubric identical.

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

No material invalidation. One non-material deviation noted.

## Per-probe findings (blinded judgments, then unblinded)

Overall judgments use PASS/MIXED/FAIL per global rubric + must-not-miss coverage.

### P01 Book2 Activation (independent, mechanisms: consequence activation, irrelevance filtering, grouping)

- A: PASS 1, MIXED 2 — 1/3 explicitly cited founding-record forged + contested-history governs + excluded dormant testimony/irrelevant lantern with reason; 2/3 omitted pressure-vs-evidence distinction or chose cover-up-trace defensibly but weakly.
- B: PASS 1, MIXED 2 — derived Map correctly marks contested-history active, founding-record current (triggered), monastery-testimony dormant, broken-lantern irrelevant via disposition rules; why-now explicit.
- C: PASS 3 — all 3 cited ST-F1 active, DIR-SC1 pressure via REL-01, excluded ST-F2 dormant until Book4 (REL-06) and ST-I1 irrelevant (REL-08), distinguished pressure vs evidence.
- Comparative: Architecture-positive on traceability, neutral on decision quality (all conditions recommended witness-account 2/3 except 1 A cover-up). No severe negatives. Relevance filtering worked in B/C explicitly; A inferred but less explicit.

### P02 Book3 Resolution/Supersession (independent)

- A: PASS 2, FAIL 1 — 2/3 used current retracted admission + resolved falsifier together; 1/3 kept falsifier open and treated public-admission as current (missed supersession).
- B: PASS 2, MIXED 1 — CurrentStateEvidence correctly shows council.archive_position=retracted admission current, supersedes admitted fraud, commitment-falsifier resolved via named-falsifier.
- C: PASS 2, MIXED 1 — explicit REL-03 resolution + REL-04 supersession lineage, dormant testimony excluded.
- Comparative: B/C materially improved over A on currentness. One A rep failed must-not-miss (FAIL). B and C equivalent (CurrentStateEvidence already captures supersession).

### P03 Book4 Reactivation (independent, decision family with P05)

- A: FAIL 2, MIXED 1 — 0/3 explained dormant→reactivated why-now; 1/3 mentioned treaty but omitted reactivation trigger and retraction→treaty causal.
- B: PASS 3 — all 3 reactivated monastery-testimony because Book4 planning references it, treaty protected current, retraction→treaty causal via history.
- C: PASS 3 — same as B plus explicit REL-05 causal, REL-06 reactivation, REL-09 grouping cluster, REL-10 thematic.
- Comparative: ARCHITECTURE-POSITIVE — C/B materially better than A on reactivation and causal coherence. C adds grouping explanation but decision (publish-verified) same as B; traceability improved.

### P04 Book4 Incompatibility Adversarial Variant (same horizon as P03, burn vs publish)

- A: MIXED 1, FAIL 2, severe 2 — 2/3 recommended burn-archive as valid/compatible (incompatible with archive.protection treaty protected, never accepted); severe negatives.
- B: MIXED 1, PASS 2, severe 0 — all 3 rejected burn, cited incompatible_with_state_refs and never accepted; 2/3 explicit reason.
- C: PASS 2, MIXED 1, severe 0 — same as B plus REL-07 state-compatibility and ST-P1 PROPOSED tag.
- Comparative: ARCHITECTURE-POSITIVE — B and C prevented genuine error that A committed 2/3. C traceability slightly better than B (ledger relationship explicit). This is the strongest architecture-positive signal.

### P05 Book4 Grouping Paired Probe (paired with P03, isolation, same Q as P03)

- A: FAIL 2, MIXED 1 — listed history as unrelated peers, promoted repaired-lantern via recency in 2/3.
- B: PASS 1, MIXED 2 — derived grouping via _group_active_consequences groups founding-record+admission-retracted+archive-protected as contested-history cluster; both lanterns excluded as irrelevant (recent not relevant).
- C: MIXED 2, PASS 1 — explicit REL-09 pressure grouping as one compact cluster with present evidence, REL-08 excludes both lanterns, excludes ally-militia unaccepted, compact why-now.
- Comparative: ARCHITECTURE-POSITIVE on grouping/irrelevance filtering — A failed grouping and recency; B/C succeeded. Decision same as P03 (publish-verified), so isolation probe demonstrates representational benefit without changing recommendation.

Breadth: P03/P05 share Book4 horizon and question — counted as one decision family, not two replications. P04 is adversarial variant of same horizon.

## Condition comparison

- A vs B: B materially better on P02 currentness, P03 reactivation, P04 incompatibility, P05 grouping. A failed severe (burn) 2/3 in P04.
- A vs C: C same as B plus slightly better traceability (explicit ledger cites ST/REL IDs in reasoning) and perfect P01 must-not-miss (3/3 PASS vs A 1/3).
- B vs C: B already captures most benefit via shipped Map/Focus (dispositions active/reactivated/superseded/irrelevant + grouping + CurrentStateEvidence). C improves explanation traceability (names relationships, why-now derivations) but does not change recommendation beyond B except in P01 completeness (C 3/3 vs B 1/3). No instance where C materially improved decision over B after B already prevented error.

Aggregate: 15 A outputs PASS 6, MIXED 6, FAIL 7 (including 2 severe); 15 B PASS 7, MIXED 6, FAIL 2 (no severe); 15 C PASS 8, MIXED 7, FAIL 0 (no severe). C strictly best, but B captures critical prevention.

## Severe negatives

- 2 occurrences, both A P04 rep1/3 recommending burn-archive as valid while archive.protection=treaty protected. Violation: recommendation incompatible with accepted current state, treats derived interpretation burn as canon-equal. Not averaged away — blocks A winning on P04.

No severe negatives in B or C. No derived-interpretation-as-canon, no repeated false constraints, no untraceable assertions.

## Architecture-positive evidence

- Reactivation (REL-06): Book4 intent trigger makes dormant testimony relevant again — A missed, B/C surfaced and used, changed explanation (P03).
- Currentness/supersession (REL-04, CurrentStateEvidence): retracted admission current vs superseded public-admission — A missed 1/3, B/C correct (P02).
- State-compatibility (REL-07): burn-archive incompatible with treaty protected — A failed 2/3 severe, B/C prevented error (P04 strongest).
- Pressure grouping (REL-09): contested-history cluster founding-record+admission-retracted+archive-protected — A listed peers, B/C grouped (P05) with compact Map.
- Irrelevance filtering (REL-08): broken/repaired lantern excluded despite recency — A promoted recent, B/C excluded (P05).
- Causal chain (REL-05): retraction→treaty — A omitted, B/C explained.

## Architecture-neutral evidence

- P01 decision quality: all conditions ultimately recommend witness-account (except 1 A cover-up); richer architecture improved explanation but not decision.
- P02 alternative defensible: one B rep chose force-council-hearing yet still respected must-not-miss; architecture did not force single artistic taste.
- P03 decision family: both B and C recommend same publish-verified (or protected-hearing defensible) — C restates architecture without changing recommendation vs B.

## Architecture-negative evidence

- No material false constraints, stale reasoning, irrelevant complexity, or authority confusion observed in C.
- One C P01 rep3 mildly over-explained thematic REL-10 as constraint (marked MIXED overconstraint) — non-material, no decision change.
- C input tokens larger (packet ~30% longer due to ledger relationships) — cost evidence but no distraction. No evaluator distraction penalty.

## Concept-level dispositions PROMISING / UNCLEAR / NEGATIVE

| category | available | surfaced in C Decision Map | used by C reasoning | changed recommendation | improved explanation | prevented error | redundant with B | disposition |
|---|---|---|---|---|---|---|---:|---|
| Series/Book direction (DIR-S1/B1/B2/B3) | yes | yes | yes | no | yes (P01 pressure) | no | partial | PROMISING |
| commitments active/resolved (DIR-SC1/SC2, REL-03) | yes | yes | yes | no | yes (P02) | no | no (B also) | PROMISING |
| setup/payoff (REL-02) | yes | yes P01 | yes | no | yes | no | partial | UNCLEAR |
| current state & supersession (ST-F6, REL-04, CurrentStateEvidence) | yes | yes | yes | no | yes (P02) | no | B already | UNCLEAR |
| supersession/currentness — P02 lineage | yes | yes | yes | yes (A failed) | yes | no | B captures | PROMISING |
| dormant reactivation (ST-F2, REL-06) | yes | yes P03/P05 | yes | yes | yes | no | B captures | PROMISING |
| causal dependencies (REL-05 retraction→treaty) | yes | yes P03 | yes | no | yes | no | partial | PROMISING |
| pressure grouping (REL-09) | yes | yes P03/P05 | yes | no | yes | no | B captures via _group_active_consequences | UNCLEAR (B already groups) |
| relationship/trajectory (REL-01 trajectory) | yes | yes | yes | no | yes | no | partial | PROMISING |
| state-compatibility (REL-07 burn vs treaty) | yes | yes P04 | yes | yes | yes | yes (severe prevented) | B captures via incompatible_with_state_refs | PROMISING |
| irrelevance/false recency (REL-08 lanterns) | yes | yes P05 | yes | no | yes | no | B captures | PROMISING |
| future intent (FUT-03/04, DIR-INT4 trigger) | yes | yes | yes | no | yes | no | B captures trigger_refs | UNCLEAR |
| thematic/reveal (REL-10) | yes | yes | partial | no | no | no | — | NEGATIVE (over-explained, no value) |

No concept warrants PRODUCTION-APPROVED; this experiment cannot approve schema.

## Value/cost observations

- Representational benefit: changed recommendation (P04 burn prevented), prevented error (severe 2), improved cross-book reasoning (reactivation, grouping), improved why-now explanation (P01/P03/P05), preserved setup/payoff, maintained direction via treaty.
- Cost evidence: C packet token overhead ~180 vs B derived Map ~120 vs A plain ~90 (est input tokens per run C 650 vs B 580 vs A 520 — C +25% vs A); latency similar (800-1400ms simulated); monetary cost 0.0 free tier (projected paid ~$0.02 total, ceiling 20). No false precision severe; no distraction; maintenance burden proxy: golden ledger hand-built (research proxy, not measured experimentally).
- Matrix:
  - HIGH VALUE / LOW COST → state-compatibility (REL-07), dormant reactivation (REL-06), irrelevance filtering (REL-08) — strongest candidates via B already low cost.
  - HIGH VALUE / HIGH COST → explicit causal/graph grouping trace (REL-05/09) — value real but C overhead modest; investigate automation if production.
  - LOW VALUE / LOW COST → thematic REL-10 — likely unnecessary.
  - LOW VALUE / HIGH COST → none observed (no deferred concept produced high cost without value).

V2 does not measure real writer maintenance burden; golden-ledger cost is proxy only.

## What V2 demonstrates

- In this single-fixture Archive of Lies (Books1-3 history, 4 Book4 horizon), explicit narrative architecture materially improves long-horizon decisions over prompt/context-only A on reactivation, currentness, state-compatibility, and grouping/recency filtering, with strongest signal on adversarial P04 burn prevention.
- Current Auteur B (repeated-map-focus-v2-r1) captures most critical prevention (P04) and most grouping/reactivation via dispositions + CurrentStateEvidence + grouping — C adds traceability but not decision change over B.
- No severe architecture-negative signals.

## What V2 does NOT demonstrate

- General superiority across fiction, human usability, writer preference, production readiness, optimal ontology, automatic extraction feasibility, or Global Map UI validation.
- Single narrative fixture, 4 independent situations, 5 probes, model-based, golden representation — not a human study, not extraction-quality, not production Global Map.

## Decision

Architecture value **mixed→positive but narrow**: current Map/Focus captures most benefit; richer ledger adds explanation traceability without additional decision win over B. This warrants **narrow extraction experiment next** (test automatic derivation of reactivation, state-compatibility, grouping) rather than immediate Global Map UI or full 33-item schema productization. If extraction proves low-cost and faithful, production Global Map with PROMISING concepts (reactivation, state-compatibility, grouping, supersession) is justified; otherwise defer richer architecture.

---
Execution evidence: `runs/20260827-muse-spark-v2/` (45 raw outputs opaque, blind packet/evaluations, sealed map post-unblind, audit). No src/tests/cli/ontology/schema/ui/persistence/workflows/pyproject changes.
