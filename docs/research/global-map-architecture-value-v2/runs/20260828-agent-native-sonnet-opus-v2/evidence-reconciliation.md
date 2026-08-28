# Architecture Value Experiment V2 — Agent-Native Replication — Evidence Reconciliation

**Applies to:** `20260828-agent-native-sonnet-opus-v2`
**Purpose:** correct overclaims, provenance classifications, and interpretation language in `result.md` / `execution-provenance-audit.md` / `post-unblind/invalidation-audit.json` so PR #147's claims match exactly what the existing evidence proves. This is an append-only reconciliation pass. **No raw generation output, blind packet, or blind evaluation judgment was altered, reevaluated, or regenerated for this reconciliation.** All PASS/MIXED/FAIL counts and severe-negative flags are unchanged and remain mechanically reproducible from the existing `blind-evaluation/*.json` and `post-unblind/full-evaluations-with-conditions.jsonl` files.

Preferred overall classification after this reconciliation:

> **AGENT-NATIVE EMPIRICAL EXECUTION WITH DISCLOSED FROZEN-V2 EXECUTION DEVIATIONS — DIRECTIONALLY INTERPRETABLE FOR WITHIN-RUN A/B/C COMPARISON — NOT A STRICT FROZEN-CONTROL-CONFORMANT V2 REPLICATION.**

This is genuine empirical evidence (real, isolated, distinct-model sub-agent invocations captured verbatim — not synthesis/templating). It is not a strict frozen-V2-control-conformant execution, for the specific, itemized reasons below.

---

## A. Execution base vs. source revision vs. protocol revision

Three distinct commits were previously used loosely/interchangeably in places. The correct distinctions, each independently verified in this reconciliation pass:

| term | value | meaning |
|---|---|---|
| **Execution base** | `1053154f3d23893e2ce6a4e48fa5cb16b2d459ed` | the `main` commit this replication branched from and diffs against (verified: `git merge-base origin/main HEAD` = this SHA) |
| **Frozen narrative/source revision** | `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` | the frozen fixture/source snapshot all three conditions derive from (PR #143 merge; unchanged since) |
| **Frozen V2 protocol revision** | `a11e58d219a8ffd311690960d69398471b141884` | the commit at which the corrected V2 protocol (leakage fix) was frozen for execution (PR #145 merge) |

No historical hash has been rewritten. `result.md` and `execution-provenance-audit.md` are corrected below to use these three terms consistently rather than conflating "execution base" with "source revision."

## B. Sub-agent context isolation — narrowed claim

**Original overclaim:** "exact control over the input supplied to the worker," implying the worker's entire context was the single packet file.

**What is actually proven, and how:**
- The canary test (two sub-agents, distinct secret nonces, run in parallel before any experimental packet existed) proved: neither canary agent's response contained the other's nonce, and each of the 90 subsequent experimental invocations used a fresh `Agent` call with no `to:`/resume parameter. This proves **no inheritance of the orchestrator's prior conversational reasoning and no inheritance of another worker's experimental conversation.**
- The experimental *task input* — the packet file content — is proven exact and hashable: it was written to disk before any worker ran, and each worker was instructed to read exactly that one path.
- **What is NOT proven:** whether a fresh `general-purpose` sub-agent additionally receives ordinary runtime/startup context beyond the experimental task input — e.g. its own system prompt, tool definitions, the repository's `CLAUDE.md` / agent instructions, or workspace/repository metadata. This was not independently inspected or ruled out in this execution. If such runtime context was present, it was present **uniformly** for every one of the 90 invocations (same `subagent_type`, same repository, same session) — not a between-condition confound — but it means the packet file was not necessarily the worker's *entire* context.

**Corrected claim (replaces the overclaim throughout):**
> The sub-agent did not inherit the orchestrator's prior conversational reasoning or another worker's experimental conversation. The experimental narrative packet supplied to each worker was controlled and hash-verifiable. Whether ordinary runtime/startup context (system prompt, CLAUDE.md, tool definitions, repository metadata) was additionally present in each worker's context was not independently verified; if present, it was uniform across all 90 invocations. This is recorded as a **provenance limitation**, not as proof of exclusive single-file context.

## C. Condition-correlated generator packet filenames — real leakage risk, disclosed

**Finding:** the 15 generator packet files are named `{probe_id}-{condition}.txt` (e.g. `packets/P01-A.txt`, `packets/P04-C.txt`), and every generator delegation prompt in this run instructed the sub-agent to read that exact path — e.g. *"Use the Read tool exactly once, on exactly this path... `.../packets/P01-A.txt`."* **The condition letter (A/B/C) was therefore literally present, in plain text, in the string given to each generator sub-agent**, even though the sub-agent was never told what that letter meant and was not asked to reason about it.

**Two distinct questions, answered separately, per the reconciliation instructions:**

1. **Did frozen V2 itself require the generator to be blind to A/B/C?** No. Re-reading `evaluation-rubric.md` and `condition-specification.md`: the frozen A/B/C blinding requirement is stated for the **evaluator** ("Blinded evaluator must NOT receive: A/B/C condition identity, hidden mapping, expected winner"). The generator-side requirement in frozen V2 is narrower: the generator must not receive the rubric, must-not-miss/forbidden signals, or the expected winner — it says nothing about the generator not seeing which condition it is producing. This makes sense: the generator is, by construction, executing under one specific condition; only the evaluator's blindness to that fact is load-bearing for the experiment's validity.
2. **Did this replication's own execution-contract instructions ask for generator-side A/B/C blinding anyway?** Yes — the task's own §8 ("GENERATOR WORKERS") stated generator workers should NOT receive the A/B/C condition name, as an additional precaution beyond the frozen minimum. That precaution was **not fully honored**: the file path — not any prose in the packet body — carried the condition letter.

**Classification:** **AGENT-NATIVE EXECUTION-CONTRACT DEVIATION / LEAKAGE RISK**, not a frozen-V2 invalidation (frozen V2 does not require this). Practical materiality is low — the packet body itself contains no condition label, no rubric, no must-not-miss/forbidden text, and the generator was never instructed to infer or use the letter — but the byte string was present and a sufficiently motivated model could in principle have noticed and used it. This is disclosed rather than asserted away.

**Not done in this reconciliation:** the existing packet files were **not renamed**, per the instruction to avoid touching frozen/existing artifacts casually. For any future run, opaque generator packet filenames (matching the opaque `opaque_run_id` scheme already used for evaluator packets and raw outputs) would remove this risk entirely — recorded here as a note for future work only.

## D. Model identity — narrowed to what was actually observed

**Original overclaim:** "generator model: sonnet (claude-sonnet-5)... frozen"; "evaluator model: opus (claude-opus-5)... frozen"; "model/version did not change mid-run."

**What the execution record actually shows:** the orchestrator supplied the request-side parameter `model: "sonnet"` on all 45 generation calls and `model: "opus"` on all 45 evaluation calls (mechanically verifiable — every `Agent` invocation in the session transcript used one of exactly these two literal strings). The `Agent` tool's result payload does not additionally return a response-side resolved model/version identifier (no field analogous to a provider's `model` field on a `messages.create` response was observed in any of the 90 results).

**Corrected claims:**
- Generator requested runtime model alias: `sonnet`
- Evaluator requested runtime model alias: `opus`
- Provider/runtime-resolved exact model version: **UNAVAILABLE / NOT INDEPENDENTLY OBSERVABLE FROM THIS EXECUTION RECORD**
- "claude-sonnet-5" / "claude-opus-5" as used in `result.md`/`execution-provenance-audit.md`/the PR body are **documentation-derived context** (this session's own system-prompt-level knowledge of what the `sonnet`/`opus` aliases currently resolve to), not execution-observed provenance. They are retained in prose as a documentation note only, clearly separated from the execution-provenance claim below.
- "Model/version did not change mid-run" is narrowed to: **"The requested runtime model alias remained fixed across all relevant invocations (`sonnet` for all 45 generations, `opus` for all 45 evaluations); exact resolved provider model-version stability was not independently observable through this backend."**

## E. Frozen control deviations — itemized, not collapsed

Frozen V2 control variables: `temperature 0.2, top_p 1.0, tools none, max_output_tokens ~1200, fresh context, same model/version` (`condition-specification.md`). The single "one deviation" framing in the original `post-unblind/invalidation-audit.json` is replaced with five itemized entries:

| id | deviation | classification |
|---|---|---|
| **E1** | No temperature/top_p/seed/max_output_tokens exposed to the orchestrator by the Agent-tool backend; could not be set or verified for any of the 90 invocations. | Loss of reproducibility/control. Uniform across A/B/C — not a between-condition confound. Frozen-V2 protocol deviation (frozen control not met). |
| **E2** | Frozen V2 specifies `tools: none`. `general-purpose` sub-agents have full tool access by definition; the "none" restriction was enforced only by instruction ("use exactly one Read call, no other tool"), verified post hoc via `tool_uses: 1` on all 90 results, not guaranteed in advance by a sandbox. | Instruction-enforced, not sandbox-enforced, tool restriction. Agent-native execution-contract limitation. Uniform across A/B/C. |
| **E3** | Exact resolved provider model-version is not observable through this backend (see §D). | Provenance/observability limitation, not a between-condition confound (same alias, same lack of confirmation, for both generator and evaluator roles respectively across all their own invocations). |
| **E4** | Sub-agent startup context beyond the packet file was not independently verified (see §B). | Provenance limitation. Uniform across all 90 invocations if present at all. |
| **E5** | Generator packet filenames were condition-correlated (see §C). | Agent-native execution-contract deviation / leakage risk, **not uniform** — unlike E1–E4, the exposed token itself differed by condition (`-A`/`-B`/`-C`). Not a frozen-V2 invalidation (frozen V2 requires only evaluator-side blinding, which was maintained). Low practical materiality (no condition label or hidden signal in the packet *body*, and no observed evidence the filename token changed generator behavior), but disclosed rather than assumed away or described as uniform. |

**E1–E4 were uniform across the relevant treatments or roles and provide no identified between-condition confound: each applied identically to A, B, and C (or, for E3, identically to the generator's own 45 calls and identically to the evaluator's own 45 calls), so none of E1–E4 by itself explains why one condition scored differently from another.**

**E5 is different and must not be folded into that uniformity claim.** E5 was condition-specific because the generator packet path itself encoded the condition letter (`P01-A.txt` vs `P01-B.txt` vs `P01-C.txt`) — the cue differed by condition, unlike E1–E4. Frozen V2 did not require generator-side condition blinding (only evaluator-side, which was maintained), and there is no observed evidence in the raw outputs that the filename token changed generator behavior — no generation packet body contains a condition label, and the recommendations/rationales show no pattern consistent with the generator having "known" or acted on which letter it was. So E5 does not, on its own, invalidate the frozen-V2 evaluator-blinded comparison. But it remains a **potential condition-identity cue** and must not be described as uniform, non-differential by construction, or demonstrably immaterial — those are two different claims (no identified confound engine vs. a condition-specific cue with no observed effect), and this document keeps them separate rather than collapsing E5 into the "uniform, so harmless" framing that correctly describes E1–E4.

Taken together: none of E1–E5 is treated here as invalidating the A vs B vs C comparison outright, because the observed pattern (A weakest, with a specific, mechanistically explainable failure mode at P01; B and C both stronger; C strongest, concentrated at the Book-4 probes) is a plausible, mechanistically grounded signal rather than an artifact obviously attributable to any of E1–E5 — but for E5 specifically, "not invalidating" rests on the absence of observed evidence of an effect, not on uniformity, since E5 was not uniform. A reader should weigh E1–E5 (and E5 in particular, differently from E1–E4) when deciding how much confidence to place in the magnitude, not just the direction, of the observed gaps.

## F. Blinding chronology — session-supported, not Git-anchored

**Original overclaim (implicit in "blind-freeze commit" framing borrowed from the muse-spark-v2 precedent):** that the repository's Git history independently anchors freeze-before-unblind chronology.

**Actual state:** PR #147 contains **one** experimental commit (`11feb7a`), which includes the blind packets, the blind evaluations, the sealed condition map, and the post-unblind joined/reconciled files together, committed only after the entire pipeline (packet construction → generation → blind evaluation → freeze/hash → unblind → mechanical reconciliation) had already run to completion inside one orchestration session. There is **no separate, earlier Git commit** that contains the frozen blind judgments while excluding the sealed condition map.

This means: **the hash values in `judgment_hash.txt` and `blind_packet_hash.txt` prove content identity/integrity of the frozen artifacts as they now stand, but they do not by themselves prove temporal ordering** (i.e., that the hash was computed *before* the sealed map was read). That ordering claim currently rests on:
- the deterministic structure of `scripts/freeze_and_unblind.py`, which computes and writes `judgment_hash.txt` (step 1) before it opens `sealed-condition-map.json` (step 2) — this is verifiable by reading the script's control flow, and
- the session transcript itself, in which the freeze step's printed hash and the leakage-scan-clean result were produced and observed before the unblind step's output appeared.

**Corrected chronology classification:** **SESSION-SUPPORTED / SELF-AUDITED CHRONOLOGY ONLY.** It is not independently Git-anchored. No retroactive "blind-freeze" commit has been fabricated to manufacture the appearance of Git-anchored chronology — doing so now would misrepresent history rather than correct it, which the reconciliation task explicitly prohibits. A reader who requires independently auditable (not merely script-and-transcript-supported) chronology should treat this as an open item for any future run: e.g., committing the blind-evaluation artifacts in a dedicated commit *before* a second commit reveals the sealed map, so Git history itself carries the ordering proof.

## G. E61 raw evaluator response — recovered, preserved additively

The blinded evaluator's raw response for opaque candidate `E61` (probe P02) was truncated mid-string by the sub-agent (missing a closing quote and closing braces on the `one_line_rationale` field). The orchestrator's session transcript retains the exact text of that truncated tool response. That exact text has now been recovered and preserved verbatim, additively, alongside (not replacing) the existing normalized `blind-evaluation/E61.json`:

- **New artifact:** `blind-evaluation/E61.raw.txt` — the literal, unmodified sub-agent response text as it was returned, including the truncation (no closing `"` or `}`).
- **Existing artifact, unchanged by this reconciliation:** `blind-evaluation/E61.json` — a normalized, machine-parseable version produced at original commit time (`11feb7a`), before this reconciliation pass existed.

**Correction to an initial overclaim in this reconciliation doc:** on first drafting this section, the reconciliation checked whether `E61.json` is byte-identical to the raw text plus a syntax closure, and it is **not**. Direct comparison shows all structured fields (`criteria`, `must_not_miss_covered`, `must_not_miss_missed`, `forbidden_violations`, `severe_negative`, `overall: MIXED`) are identical between the raw response and `E61.json`, but the free-text `one_line_rationale` field in `E61.json` is a **shortened paraphrase** of the raw response's rationale sentence (em dashes and one parenthetical quoted-example clause were dropped), not merely the same text with the JSON syntax closed. This is a genuine, previously mis-described normalization step, not a syntax-only fix.

**Disposition:** per this task's explicit instruction not to rewrite existing evaluator judgments, `E61.json` is left as-is (its overall verdict, all 11 criterion values, and both must-not-miss lists are unaffected by the rationale-text difference, so the mechanical PASS/MIXED/FAIL reconciliation and the severe-negative count are unaffected). The discrepancy is disclosed here instead of silently corrected. A reader who needs the evaluator's exact original wording should read `E61.raw.txt`, not `E61.json`'s `one_line_rationale` field.

Original raw response recovered: **YES**. Normalized artifact relationship: **`E61.json` = `E61.raw.txt` with JSON syntax closed AND its `one_line_rationale` field paraphrased/shortened; all other fields unchanged**. Judgment content that drives the mechanical reconciliation (all 11 criteria, `must_not_miss_covered`/`missed`, `forbidden_violations`, `severe_negative`, `overall: MIXED`) is **unchanged**; only the free-text rationale summary differs from the verbatim original, which is now disclosed and separately preserved.

## H. Interpretation language — bounded synthesis (replaces "strictly dominates" framing)

The mechanically reconciled counts are unchanged and are restated here for reference:

| Condition | PASS | MIXED | FAIL |
|---|---:|---:|---:|
| A (plain facts) | 6 | 4 | 5 |
| B (shipped Repeated Map/Focus) | 9 | 6 | 0 |
| C (golden Decision Map) | 14 | 1 | 0 |

Severe negatives: 2, both Condition A, both probe P01 (`N58`, `S62`) — mechanically confirmed unchanged (see `post-unblind/severe-negatives.json`).

Frozen V2 explicitly rejects a single weighted aggregate score as the basis for a verdict. "B strictly dominates A" / "C strictly dominates A" language in the original `result.md` and PR body overstated what an ordinal PASS/MIXED/FAIL count across a small, mechanism-specific probe set can support. Replacing with:

- Both structured conditions (B and C) outperform plain-context A on some tested mechanisms in this run, most clearly the P01 activation/relevance mechanism (A fails uniformly at P01, including both severe negatives; B and C both pass uniformly).
- C shows an additional observed advantage over B in this run, concentrated in the paired P03/P05 Book-4 decision family — **P03 and P05 are one decision family, not two independent replications**, per frozen V2's own breadth-interpretation rule.
- The C-over-B signal in this run is primarily causal/explanation/grouping related (explicit retraction→treaty causal trace, explicit compact `contested-history` clustering) rather than a difference in which option was recommended.
- P01, P02, and P04 do not provide an independent C-over-B signal in this run (P01/P02: both B and C pass cleanly; P04: all three conditions, including A, pass cleanly).
- P04 (the adversarial burn-archive probe) did not discriminate among conditions in this run — no severe negative and no FAIL anywhere in P04's 9 outputs.
- No universal architecture conclusion follows from this single fixture, this single model/runtime configuration (§D), or this one decision family.

**Headline (bounded):** this agent-native run provides directional empirical evidence that structured relevance/context improves some long-horizon decisions over plain facts, and that richer explicit causal/grouping representation may add value beyond the shipped Map/Focus representation in the single P03/P05 Book-4 decision family tested here. It does not prove richer architecture is better in general, and it does not validate Global Map as a production feature.

## I. Concept dispositions

No PROMISING/UNCLEAR/NEGATIVE concept-level disposition labels were assigned in the original `result.md` for this run (the run recorded probe-level PASS/MIXED/FAIL outcomes and per-probe narrative findings, not a concept-by-concept trace table). No correction is needed here beyond noting, for anyone extending this run to a concept-level trace later: **"no observed incremental value at a given probe" is not, on its own, sufficient grounds for a NEGATIVE disposition** — NEGATIVE requires evidence of a false constraint, stale reasoning, unsupported certainty, distraction, a worse recommendation, authority confusion, or rigidity-induced missed possibility, none of which were observed for C or B in this run (their weakest results were MIXED, not FAIL, and carried no severe-negative flags).

## J. Prior deepseek run discrepancy

No corresponding committed repository artifact for `20260827-deepseek-v2-empirical` was found in this repository's Git history, branches, or tags (confirmed again in this reconciliation pass: `git log --all --oneline | grep -i deepseek` and `git branch -a | grep -i deepseek` both return nothing). PR #147 therefore stands on its own evidence; no cross-run empirical conclusion is made here or in `result.md`. The prior conversational report of this absence is not itself repository evidence — the absence is independently reconfirmed by the git commands above, run again during this reconciliation pass.

---

## Mechanical verification (this reconciliation pass)

- [x] All original 45 generation outputs exist and are byte-identical to `11feb7a` (verified: no diff against that commit for `raw-outputs/`).
- [x] All original 45 blinded judgments exist and are byte-identical to `11feb7a` (verified: no diff for `blind-evaluation/*.json`).
- [x] PASS/MIXED/FAIL counts reconcile: A 6/4/5, B 9/6/0, C 14/1/0 (recomputed mechanically from `post-unblind/full-evaluations-with-conditions.jsonl`, unchanged).
- [x] Severe-negative count (2, both A/P01) mechanically re-derived, unchanged.
- [x] No condition mapping present in any evaluator-visible blind packet (re-scanned; one false-positive grep hit on the substring "condition as" inside candidate H22's own prose, not an actual leak, manually inspected and excluded).
- [x] Frozen V2 protocol documents byte-unchanged since execution base (verified via `git diff --stat` against `1053154`).
- [x] `src/` and `tests/` unchanged since execution base (verified via `git diff --stat` against `1053154`).
- [x] New `E61.raw.txt` is additive; existing `E61.json` is unchanged by this reconciliation pass; its structured judgment fields (criteria/must-not-miss/forbidden/severe-negative/overall) match the recovered raw response, though its `one_line_rationale` is a paraphrase rather than verbatim (disclosed in §G, not silently fixed).
