# Architecture Value Experiment V2 — Agent-Native Replication — Result

**Status:** AGENT-NATIVE EMPIRICAL EXECUTION WITH DISCLOSED FROZEN-V2 EXECUTION DEVIATIONS — genuine isolated model invocations (Agent-tool sub-agents), not synthesized/templated — directionally interpretable for within-run A/B/C comparison — not a strict frozen-control-conformant V2 replication. See `evidence-reconciliation.md` for the full itemized deviation list (including why deviation E5, condition-correlated generator filenames, is not uniform like E1–E4) and corrected claims; this document has been updated to match it.
**Execution base:** `1053154f3d23893e2ce6a4e48fa5cb16b2d459ed` (the `main` commit this replication branched from)
**Frozen narrative/source revision:** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge — all three conditions derive from this fixture snapshot)
**Frozen V2 protocol revision:** `a11e58d219a8ffd311690960d69398471b141884` (PR #145 merge, V2 leakage fix)
**Run ID:** `20260828-agent-native-sonnet-opus-v2`

This is an **independent replication** of the frozen V2 protocol. It does not use, target, or compare itself against the synthetic rehearsal `20260827-muse-spark-v2` (illustrative only, provenance class C) or any other prior run during blind execution. Per the task's explicit instruction, cross-run comparison is left to the human as a separate decision after this run's own result is frozen — this document does not perform that comparison.

## Run provenance

- Generator: Agent tool, `subagent_type: general-purpose`, requested runtime model alias `sonnet`, frozen (identical alias) across all 45 generation invocations. Exact resolved provider model-version is not independently observable through this backend (documentation context: this alias currently maps to claude-sonnet-5, but that is not an execution-observed fact — see `evidence-reconciliation.md` §D).
- Evaluator: Agent tool, `subagent_type: general-purpose`, requested runtime model alias `opus`, frozen across all 45 evaluation invocations, distinct alias from the generator's. Same exact-version-observability caveat applies (documentation context: currently maps to claude-opus-5).
- Isolation: fresh sub-agent per invocation, no `to:`/resume used anywhere; each was instructed to read exactly one frozen packet file and use no other tool, verified post hoc via `tool_uses: 1` on all 90 invocations. This proves no inheritance of the orchestrator's or another worker's conversation, and exact/hashable control of the experimental task input; it does **not** prove the packet file was the worker's entire runtime context (ordinary sub-agent startup context was not independently ruled out — see `evidence-reconciliation.md` §B) and the tool restriction itself was instruction-enforced, not sandboxed (§E2).
- **Condition-correlated generator packet filenames (disclosed):** generator packet files are named `{probe}-{condition}.txt` (e.g. `packets/P01-A.txt`), and each generator's delegation prompt named that exact path — so the condition letter was present, as a filename token, in the string given to every generator sub-agent, even though the packet body itself carries no condition label. Frozen V2 does not require generator-side A/B/C blinding (only evaluator-side); this replication's own execution-contract intent to keep generators condition-blind was not fully honored on this point. See `evidence-reconciliation.md` §C.
- 45 planned / 45 completed generations; 45/45 blinded evaluations. No missing or duplicate slots (mechanically verified, see `post-unblind/full-evaluations-with-conditions.jsonl`).
- Randomization: schedule seed derived from `sha256(run_id) mod 2^32 = 1693323480`, Fisher–Yates shuffle, opaque IDs (`B64`, `F83`, …) not encoding probe/condition/repetition — evaluator-facing blind-packet filenames use only these opaque IDs (no condition-correlation issue on the evaluator side). Schedule hash: see `schedule_hash.txt`.
- Blind packet hash: see `blind-packet/blind_packet_hash.txt`. Judgment hash: see `blind-evaluation/judgment_hash.txt` — this hash and the script's step ordering are **session-supported/self-audited** evidence of freeze-before-unblind chronology; there is no separate, independently Git-anchored pre-unblind commit (all artifacts landed in one commit, `11feb7a`). See `evidence-reconciliation.md` §F.
- Condition B: verbatim output of shipped `select_repeated_continuity` / `format_repeated_series_map(detail=True)` (`derivation_version=repeated-map-focus-v2-r1`) run against `tests/fixtures/repeated_map_focus_v2/` for Book 2/3/4 — no modification.
- Condition C: hand-built Decision Map per horizon, every statement traced to an id in the existing 33-item golden ledger (`../../global-map-architecture-value-v1/candidate-architecture-ledger.md`), not enriched.
- **Deviations (disclosed, itemized E1–E5 in `evidence-reconciliation.md` §E, superseding the earlier single-deviation framing):** no temperature/top_p/seed/max_output_tokens control; instruction- rather than sandbox-enforced tool restriction; unobservable exact model version; unverified sub-agent startup context; condition-correlated generator filenames. E1–E4 are uniform across A/B/C (no identified between-condition confound). **E5 is not uniform** — the exposed generator-filename token itself differed by condition (`-A`/`-B`/`-C`); frozen V2 did not require generator-side condition blinding and there is no observed evidence the token changed generator behavior, so it does not by itself invalidate the comparison, but it remains a potential condition-identity cue, not a demonstrably immaterial one. All five represent a real loss of exact reproducibility control and of some execution-contract precautions. See `post-unblind/invalidation-audit.json`.

## Validity audit

| check | result |
|---|---|
| C did not receive extra narrative facts | PASS |
| questions/options stayed identical within each probe across A/B/C | PASS |
| requested generator model alias did not change mid-run | PASS (`sonnet` alias frozen; exact resolved provider version not independently observable — see §D of `evidence-reconciliation.md`) |
| evaluator remained blind to condition identity until judgments frozen | PASS on the evaluator side (leakage audit: 0 condition-identity hits pre- and post-freeze in evaluator-visible blind packets and in the frozen judgments); chronology proof is session-supported/self-audited, not independently Git-anchored (§F) |
| generator remained blind to hidden rubric/must-not-miss/forbidden/expected-winner | PASS (frozen V2 requirement; packets contain none of this) |
| generator packet filenames did not carry condition-identity tokens | DEVIATION — filenames were condition-correlated (`P01-A.txt` etc.); an agent-native execution-contract deviation, not a frozen-V2 requirement violation (§C) |
| raw outputs were not manually edited | PASS for all 44 non-truncated evaluations; one disclosed exception (E61) where the normalized `E61.json` closed truncated JSON syntax **and** paraphrased the free-text rationale (structured fields unchanged); original raw text preserved separately in `E61.raw.txt` (§G) |
| B was not modified for the experiment | PASS (shipped code, unmodified) |
| C ledger did not gain unsupported facts | PASS |
| sampling/tooling/model-version-observability/startup-context settings did not materially drift or were verifiable | DEVIATION/LIMITATION (E1–E4 in §E) — not controllable or not independently verifiable via this backend; disclosed, uniform across conditions |
| source fixture did not change mid-run | PASS |

**Empirical validity: AGENT-NATIVE EMPIRICAL EXECUTION WITH DISCLOSED FROZEN-V2 EXECUTION DEVIATIONS — DIRECTIONALLY INTERPRETABLE FOR WITHIN-RUN A/B/C COMPARISON — NOT A STRICT FROZEN-CONTROL-CONFORMANT V2 REPLICATION.** E1–E4 (`evidence-reconciliation.md` §E) were uniform across the relevant treatments or roles and provide no identified between-condition confound. E5 (condition-correlated generator packet filenames) was condition-specific, not uniform — frozen V2 did not require generator-side condition blinding, and there is no observed evidence the filename token changed generator behavior, so E5 does not by itself invalidate the frozen-V2 evaluator-blinded comparison, but it remains a potential condition-identity cue and should be weighed as such, not dismissed as harmless-by-uniformity. The chronology/context/filename limitations should all be weighed by any reader assessing how much confidence to place in the magnitude (not just the direction) of the observed gaps.

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

Frozen V2 explicitly does not reduce this experiment to one weighted aggregate score; the ordinal PASS/MIXED/FAIL counts below describe *this run's* observed pattern per probe/condition and should not be read as a general dominance claim.

- **A vs B:** B PASS 9/MIXED 6/FAIL 0 vs A PASS 6/MIXED 4/FAIL 5. B outperforms A on this run's PASS/MIXED/FAIL ordinal count, concentrated almost entirely at P01 (A fails uniformly there, including both severe negatives) and, to a lesser extent, at P02/P03 explanation-traceability gaps in A.
- **A vs C:** C PASS 14/MIXED 1/FAIL 0 vs A PASS 6/MIXED 4/FAIL 5. C outperforms A on this run's ordinal count at every probe except P04 (tied) and shows the largest gap observed in this run.
- **B vs C (most consequential comparison):** C PASS 14/MIXED 1/FAIL 0 vs B PASS 9/MIXED 6/FAIL 0. Neither had a FAIL or a severe negative. C's observed advantage over B is concentrated in P03 (2 PASS vs 0 PASS) and P05 (3 PASS vs 0 PASS) — **P03 and P05 are one paired decision family, not two independent replications**, per frozen V2's own breadth-interpretation rule — both Book-4-horizon probes where the explicit golden-ledger relationships (REL-05 causal chain, REL-06 reactivation trigger, REL-09 grouping) appear to help the generator state an explicit why-now/causal trace that B's derived Map supports computationally but does not always surface in prose strongly enough for the blinded evaluator to credit as PASS on `explanation_traceability`/`causal_coherence`. P01, P02, and P04 show no independent B vs C gap in this run (both clean at P01/P02; all three conditions clean at P04).

**Bounded headline synthesis:** this agent-native run provides directional empirical evidence that structured relevance/context improves some long-horizon decisions over plain facts, and that richer explicit causal/grouping representation may add value beyond the shipped Map/Focus representation in the single P03/P05 Book-4 decision family tested here. It does not prove richer architecture is better in general, and it does not validate Global Map as a production feature.

## Limitations (frozen, preserved)

- Single fixture (*Archive of Lies*).
- Four independent decision situations (P03/P05 are one decision family; P04 is an adversarial variant of the same Book-4 horizon), not five.
- Golden hand-built C architecture — this run does not test extraction quality.
- Model/runtime-specific: generator requested alias `sonnet`, evaluator requested alias `opus`, both via the Claude Code Agent-tool sub-agent backend; exact resolved provider versions are not independently observable from this execution record (documentation context only: these aliases currently map to claude-sonnet-5/claude-opus-5). Results are scoped to this model/runtime pairing and this fixture; they are not a universal claim about "architecture" in the abstract.
- Sampling-parameter control deviation means the 3 repetitions per cell are not temperature-pinned in the way the frozen protocol specifies; see `evidence-reconciliation.md` §E for this and four further itemized execution deviations (tool-restriction enforcement, model-version observability, sub-agent startup context, condition-correlated generator filenames).
- Blinding chronology is session-supported/self-audited, not independently Git-anchored (`evidence-reconciliation.md` §F).
- No human-usability claim, no production Global Map implementation claim, no extraction-quality claim.

## Human boundary

This replication supplies evidence. It does not authorize V3, extraction research, Global Map implementation, or ontology/schema changes. Cross-run comparison against `20260827-deepseek-v2-empirical` (asserted in the task's quarantine section) or against the synthetic rehearsal `20260827-muse-spark-v2` remains a separate human research decision — and the orchestrator notes, for the human's benefit and not as part of the blinded analysis above, that no `20260827-deepseek-v2-empirical` run artifact exists anywhere in this repository's git history, branches, or tags as of this replication (verified by `git log --all` / `git branch -a` search); only the synthetic rehearsal exists as a prior run. See the accompanying final report message for this discrepancy.
