# Architecture Value Experiment V2 — Agent-Native Replication — Result

**Status:** EMPIRICAL — genuine isolated model invocations (Agent-tool sub-agents), provenance class A/B (see `execution-provenance-audit.md`; not class C/synthetic)
**Source revision:** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge)
**Protocol revision:** `a11e58d219a8ffd311690960d69398471b141884` (PR #145 merge, V2 leakage fix)
**Run ID:** `20260828-agent-native-sonnet-opus-v2`

This is an **independent replication** of the frozen V2 protocol. It does not use, target, or compare itself against the synthetic rehearsal `20260827-muse-spark-v2` (illustrative only, provenance class C) or any other prior run during blind execution. Per the task's explicit instruction, cross-run comparison is left to the human as a separate decision after this run's own result is frozen — this document does not perform that comparison.

## Run provenance

- Generator: Agent tool, `subagent_type: general-purpose`, `model: sonnet` (claude-sonnet-5), frozen across all 45 generation invocations.
- Evaluator: Agent tool, `subagent_type: general-purpose`, `model: opus` (claude-opus-5), frozen across all 45 evaluation invocations, distinct from generator.
- Isolation: fresh sub-agent per invocation; each read exactly one frozen packet file (verified `tool_uses: 1` on all 90 invocations); no `to:`/resume used anywhere.
- 45 planned / 45 completed generations; 45/45 blinded evaluations. No missing or duplicate slots (mechanically verified, see `post-unblind/full-evaluations-with-conditions.jsonl`).
- Randomization: schedule seed derived from `sha256(run_id) mod 2^32 = 1693323480`, Fisher–Yates shuffle, opaque IDs (`B64`, `F83`, …) not encoding probe/condition/repetition. Schedule hash: see `schedule_hash.txt`.
- Blind packet hash: see `blind-packet/blind_packet_hash.txt`. Judgment hash (frozen before unblinding): see `blind-evaluation/judgment_hash.txt`.
- Condition B: verbatim output of shipped `select_repeated_continuity` / `format_repeated_series_map(detail=True)` (`derivation_version=repeated-map-focus-v2-r1`) run against `tests/fixtures/repeated_map_focus_v2/` for Book 2/3/4 — no modification.
- Condition C: hand-built Decision Map per horizon, every statement traced to an id in the existing 33-item golden ledger (`../../global-map-architecture-value-v1/candidate-architecture-ledger.md`), not enriched.
- **Deviation (disclosed):** the Agent-tool backend does not expose temperature/top_p/seed/max_output_tokens to the orchestrator. This control-variable deviation is uniform across A/B/C (not a between-condition confound) but is a real loss of exact reproducibility control. See `post-unblind/invalidation-audit.json`.

## Validity audit

| check | result |
|---|---|
| C did not receive extra narrative facts | PASS |
| questions/options stayed identical within each probe across A/B/C | PASS |
| generator model/version did not change mid-run | PASS (sonnet frozen) |
| evaluator remained blind until judgments frozen | PASS (leakage audit: 0 hits pre- and post-freeze; sealed map read only after judgment hash computed) |
| raw outputs were not manually edited | PASS, with one disclosed syntax-only repair (truncated JSON closed on one evaluator response, content unchanged) |
| B was not modified for the experiment | PASS (shipped code, unmodified) |
| C ledger did not gain unsupported facts | PASS |
| sampling/tooling settings did not materially drift | DEVIATION — not controllable via this backend; disclosed, uniform across conditions |
| source fixture did not change mid-run | PASS |

**Empirical validity: VALID WITH ONE DISCLOSED DEVIATION** (sampling-parameter control). The A vs B vs C comparison itself is not confounded by this deviation, since it applies identically to all three conditions.

## Mechanical reconciliation (from `post-unblind/full-evaluations-with-conditions.jsonl`)

Overall judgment counts (PASS/MIXED/FAIL), 15 per condition, 45 total, 3 per condition×probe cell (all invariants mechanically verified — see `scripts/freeze_and_unblind.py` output):

| Condition | PASS | MIXED | FAIL | Total |
|---|---:|---:|---:|---:|
| A (plain facts) | 6 | 4 | 5 | 15 |
| B (shipped Repeated Map/Focus) | 9 | 6 | 0 | 15 |
| C (golden Decision Map) | 14 | 1 | 0 | 15 |

Severe negatives: **2**, both in Condition A, both at probe P01 (opaque IDs `N58`, `S62`; repetitions 3 and 2). Both were independently flagged by the blinded evaluator for the same forbidden move: treating the dormant `monastery-testimony` fact as a currently active, load-bearing resource for the Book 2 recommendation, while under-weighting the actually-active `founding-record forged` constraint. No severe negatives in B or C.

### Per-probe breakdown

| Probe | A (P/M/F) | B (P/M/F) | C (P/M/F) | Note |
|---|---|---|---|---|
| P01 (Book 2, independent) | 0/0/3 | 3/0/0 | 3/0/0 | A fails uniformly (dormant-testimony forbidden move, 2/3 severe) |
| P02 (Book 3, independent) | 1/2/0 | 3/0/0 | 3/0/0 | A tends to gesture at retraction/resolution without stating it explicitly |
| P03 (Book 4, independent) | 0/1/2 | 0/3/0 | 2/1/0 | Weakest probe for all conditions; recurring miss is the explicit retraction→treaty causal trace and the Book 4 trigger for testimony reactivation |
| P04 (Book 4, adversarial burn-archive variant) | 3/0/0 | 3/0/0 | 3/0/0 | All three conditions correctly rejected `burn-archive` in all 3 reps this run — no severe negative recorded here |
| P05 (Book 4, paired grouping/isolation probe with P03) | 2/1/0 | 0/3/0 | 3/0/0 | C is the only condition to consistently form the required single `contested-history` grouping cluster; B's shipped Map structurally separates the group's items without an explicit single-cluster statement the rubric credits, so B scores MIXED throughout |

## Findings (post-unblind, as required by frozen V2 interpretation rules)

- **P01:** Architecture-positive for both B and C relative to A. A's generator, given only plain facts, consistently over-weighted the dormant, narratively appealing `monastery-testimony` fact instead of the genuinely newly-active `founding-record forged` fact — exactly the failure mode the treatment (dormant/active disposition, explicit in B and C) is designed to prevent. This is the strongest, cleanest signal in this run.
- **P02:** B and C both PASS uniformly; A is MIXED/PASS but never explicitly states the resolved/superseded state transitions the probe requires, even though it avoids all forbidden moves. Neutral-to-positive architecture signal; A is defensible but weaker on explanation traceability.
- **P03 (paired with P05, one decision family):** The hardest probe for every condition. Even C reaches only 2 PASS / 1 MIXED (never a clean 3/3), and B never exceeds MIXED. The recurring miss across all conditions is failing to state the causal chain *retraction → treaty* explicitly, and (for A/B in the FAIL/MIXED cases) not naming the Book 4 planning-intent trigger that reactivates the dormant testimony. This is a genuine "hard for everyone" probe rather than a clean architecture-positive result.
- **P04 (state-compatibility, adversarial):** No architecture differentiation this run — all three conditions correctly rejected `burn-archive` in all 9 outputs (3 conditions × 3 reps), citing the plain fact `archive.protection = treaty protected` as sufficient grounds even without an explicit incompatibility derivation. This is a genuine finding: a strong plain-facts baseline (A) can catch this particular incompatibility without explicit architecture, at least for this fixture and this generator model. Contrast with the burn-archive/severe-negative pattern reported in the (quarantined, not used as a target) synthetic rehearsal — this replication's own empirical result stands on its own regardless of that pattern.
- **P05 (paired isolation probe):** Clear architecture-positive signal for C specifically on the mechanism this probe targets (compact grouping of the `contested-history` pressure cluster, irrelevance filtering of both lantern states). C forms the required single cluster in all 3 reps; B's shipped Map, while structurally correct (it does group `contested-history` as a `ContinuityGroup`), does not consistently earn a clean PASS from the blinded evaluator, most often for lacking an explicit why-now trace tying the grouped cluster together in prose — a presentation/explanation gap rather than a computation gap.

### A vs B vs C (this run's own preregistered comparisons)

- **A vs B:** B PASS 9/MIXED 6/FAIL 0 vs A PASS 6/MIXED 4/FAIL 5. B strictly dominates A in this run, driven almost entirely by P01 (A fails uniformly there, including both severe negatives) and, to a lesser extent, P02/P03 explanation-traceability gaps in A.
- **A vs C:** C PASS 14/MIXED 1/FAIL 0 vs A PASS 6/MIXED 4/FAIL 5. C strictly dominates A across every probe except P04 (tied) and is the largest gap observed in this run.
- **B vs C (most consequential comparison):** C PASS 14/MIXED 1/FAIL 0 vs B PASS 9/MIXED 6/FAIL 0. Neither had a FAIL or a severe negative. C's advantage over B is concentrated in P03 (2 PASS vs 0 PASS) and P05 (3 PASS vs 0 PASS) — both Book-4-horizon probes where the explicit golden-ledger relationships (REL-05 causal chain, REL-06 reactivation trigger, REL-09 grouping) appear to help the generator state an explicit why-now/causal trace that B's derived Map supports computationally but does not always surface in prose strongly enough for the blinded evaluator to credit as PASS on `explanation_traceability`/`causal_coherence`. P01, P02, and P04 show no B vs C gap (both clean).

## Limitations (frozen, preserved)

- Single fixture (*Archive of Lies*).
- Four independent decision situations (P03/P05 are one decision family; P04 is an adversarial variant of the same Book-4 horizon), not five.
- Golden hand-built C architecture — this run does not test extraction quality.
- Model/runtime-specific: generator = claude-sonnet-5, evaluator = claude-opus-5, both via the Claude Code Agent-tool sub-agent backend. Results are scoped to this model/runtime pairing and this fixture; they are not a universal claim about "architecture" in the abstract.
- Sampling-parameter control deviation (disclosed above) means the 3 repetitions per cell are not temperature-pinned in the way the frozen protocol specifies.
- No human-usability claim, no production Global Map implementation claim, no extraction-quality claim.

## Human boundary

This replication supplies evidence. It does not authorize V3, extraction research, Global Map implementation, or ontology/schema changes. Cross-run comparison against `20260827-deepseek-v2-empirical` (asserted in the task's quarantine section) or against the synthetic rehearsal `20260827-muse-spark-v2` remains a separate human research decision — and the orchestrator notes, for the human's benefit and not as part of the blinded analysis above, that no `20260827-deepseek-v2-empirical` run artifact exists anywhere in this repository's git history, branches, or tags as of this replication (verified by `git log --all` / `git branch -a` search); only the synthetic rehearsal exists as a prior run. See the accompanying final report message for this discrepancy.
