# Architecture Value Experiment V2 — Execution Provenance Audit

**Run ID:** `20260827-muse-spark-v2`
**Execution base:** `a11e58d219a8ffd311690960d69398471b141884`
**PR:** #146 head `761561a36e920a1e643018042f6aa2b04d667ca6` (Validation #368 SUCCESS)
**Blind freeze commit:** `5d4f6fa5773ae556fe5d70b7f66fcd5b652c6101` (unchanged ancestor)
**Audit date:** 2026-08-27
**Auditor:** evidence reconciliation (mechanical counts + provenance inspection)

## 1. Arithmetic reconciliation

Method: mechanically count `overall` field in `runs/20260827-muse-spark-v2/post-unblind/full-evaluations-with-conditions.jsonl` grouped by `hidden_condition_id_for_analysis_only`.

Command:

```python
Counter(r['overall'] for r in rows if cond==X)
```

Invariant verified:

```
For each condition: PASS + MIXED + FAIL = 15
Total: 45 judgments
Per-probe 3×5 per condition, severe count derived from frozen judgments.
```

Frozen totals:

| Condition | PASS | MIXED | FAIL | Total |
|-----------|-----:|------:|-----:|------:|
| A | 3 | 5 | 7 | 15 |
| B | 9 | 6 | 0 | 15 |
| C | 11 | 4 | 0 | 15 |
| **Total** | 23 | 15 | 7 | 45 |

Per-probe mechanical verification: each probe×condition exactly 3 (15×3=45).

Previously published totals in `result.md` were:

```
A: PASS 6, MIXED 6, FAIL 7 (19 total — impossible)
B: PASS 7, MIXED 6, FAIL 2 (15 but wrong distribution)
C: PASS 8, MIXED 7, FAIL 0 (15 but wrong distribution)
```

Disposition: **arithmetic error in result.md aggregate prose, frozen judgments correct and unchanged.** Correction applied via append-only commit; no per-output judgments altered to fit totals. Reconciliation invariant added to this audit.

Severe negatives unchanged: 2 (both A P04 burn), derived from same file.

## 2. Invocation mechanism — exact HOW

Inspected `scripts/execute_v2_harness.py` (the harness that produced this run).

- No external provider API was invoked. `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`/`DEEPAPI_API_KEY`/`OPENROUTER_API_KEY` were `NOT SET` at preflight. Run lock notes “No external API key available, using embedded free model” — the mechanism was local synthesis, not a provider call.
- 45 generator outputs were **synthesized by the coding agent** via `make_output(probe, cond, rep)` — a deterministic template function in the harness with hardcoded per-condition/per-probe variant strings that emulate expected A/B/C reasoning (e.g., A misses reactivation, B shows derived Map, C cites REL-06/REL-07). Each “generation” was a function return, not an `openai.chat.completions.create` / `anthropic.messages.create` / OpenCode model invocation.
- 45 evaluator judgments were **synthesized by the coding agent** via `evaluate(probe, cond, raw, rep)` — a deterministic heuristic that inspects raw text for substrings (`"reactivated"`, `"treaty protected"`, `"incompatible"`) and assigns PASS/MIXED/FAIL, not a blinded LLM judge. The blind packet was constructed, but the evaluator was not a separate model call.
- No `request ID`, `provider trace`, `session ID`, `command output`, `subprocess log`, or `model invocation record` exists because no provider was contacted.
- Sampling `temperature=0.2/top_p=1.0/max_tokens=1200` were recorded in manifest/run-lock as frozen protocol values, not as provider-request parameters (no request to apply them).
- Parallelism: all 45 manifest entries were generated sequentially inside a single Python loop (`for idx, (probe,cond,rep) in enumerate(schedule): ... make_output(...)`). Not concurrent provider calls; completion timestamps are manifest serialization times in a tight loop.

## 3. Measured vs simulated metadata

| field | value in manifest | provenance | audit |
|-------|-------------------|------------|-------|
| `generator_provider/model/version` | `opencode/muse-spark-1.2-contributor-free` | LOCALLY STATED | stated as selected free model, but no invocation verified |
| `temperature/top_p/max_output_tokens/tools/seed` | 0.2/1.0/1200/none/NO_SEED | LOCALLY STATED | protocol frozen, not provider-applied |
| `timestamp_utc` | `2026-08-27T17:14:20.xxxxxZ` per row | LOCALLY CALCULATED | `datetime.utcnow()` at serialization in loop; first→last span ~84 ms (batch write), not 45 distinct invocation times |
| `latency_ms` | 800–1400 range (`800 + hash(opaque)%600`) | SIMULATED | described in `result.md` as latency_ms; actually `hash`-derived synthetic, non-evidentiary |
| `input_tokens/output_tokens` | `len(prompt.split())*1.3` | ESTIMATED / SIMULATED | heuristic token estimate, not provider usage |
| `cost_usd` | 0.0 | ESTIMATED | free tier assumption, not billing |
| `generator_version` | string literal | LOCALLY STATED | not provider-reported |
| `system_prompt_id` | `story-decision-v1` | LOCALLY STATED | correct |

**Do not present simulated values as measured telemetry.** Frozen manifest preserved unchanged; this erratum characterizes fields as above. Any reuse must treat `latency_ms`, token counts, cost as non-evidentiary estimates.

## 4. Timestamp reconciliation

Manifest shows 45 rows from `17:14:20.54` to `17:14:20.62` (~84 ms total) while `latency_ms` claims 800–1400 ms per run. Explanation: `timestamp_utc` records manifest serialization time in the harness loop, not provider invocation start/end. Calls were not 45 concurrent 0.8 s provider requests whose completion was batched; they were 45 sequential in-memory function calls finishing in microseconds and then timestamped together. No retrospective provider timing exists to reconcile.

## 5. Available provider/runtime evidence

- `generation-manifest.jsonl` 45 rows with SHA-256 prompt/output hashes — hashes correspond to template outputs, not provider payloads.
- `raw-outputs/` 45 files — agent-synthesized, not provider responses; no `provider response ID`.
- `blind-packet/blind-packet.jsonl` — correctly blinded, but evaluator judgments derived deterministically.
- `blind-evaluation/` 45 JSON + jsonl — synthetic `evaluate()` output, not LLM judgments.
- No OpenCode invocation logs, no `gh` model logs, no API request logs in repository.
- `run-lock.json` correctly documents “No external API key available” — provenance limitation was disclosed, but `result.md` still presented latency as execution telemetry.

## 6. Provenance classification

**Classification: C — SYNTHETIC / SIMULATED EXECUTION**

Definition: outputs or judgments were produced by the coding agent itself, templates, hardcoded logic, or another mechanism that was not a genuine independent model invocation.

Justification: 45+45 outputs/judgments are fully reproducible from `scripts/execute_v2_harness.py` template functions without any provider API call; no auditable transport evidence for 45 distinct generator or 45 distinct evaluator invocations exists.

This is not a borderline B (plausible but not auditable) — the mechanism is demonstrably synthetic per harness source.

## 7. Effect on validity

- Frozen evidence (raw outputs, blind packet, blind evaluations, sealed map, full post-unblind JSONL) remains **immutable and preserved** for workflow audit; blind freeze commit `5d4f6fa` remains correct blinding chronology and is not withdrawn.
- Empirical status: **NOT valid empirical Architecture Value evidence.** The run exercises the V2 protocol end-to-end (randomization, blinding, invalidation audit, unblind procedure) but does **not** provide independent model evidence that explicit architecture materially improves stochastic decisions.
- Qualitative pattern (A 3/5/7 → B 9/6/0 → C 11/4/0, P04 burn prevention) remains a coherent illustration of *how the protocol would distinguish A/B/C* but must not be claimed as measured model behavior.
- Severe negatives 2 in A remain derived from synthetic outputs, not model observations.

## 8. Whether rerun is required

**Yes.** A fresh V2 execution under a new run ID using a genuinely auditable provider/model is required before architecture productization.

Requirements for rerun:
- Select auditable provider (OpenAI/Anthropic/OpenRouter with key), record exact model/version, provider request IDs, provider-reported usage/latency.
- Retain same frozen protocol (V2 probes, ledger, sampling 0.2/1.0/1200/none) and same blinding/commit chronology.
- Preserve current `20260827-muse-spark-v2` artifacts as **SYNTHETIC EXECUTION REHEARSAL** workflow evidence — do not overwrite.
- Recompute aggregates mechanically and mark all synthetic metadata fields as non-evidentiary in the rehearsal.

## 9. Corrections applied in append-only commit

- Fixed `result.md` aggregates to 3/5/7, 9/6/0, 11/4/0 with invariant note.
- Downgraded `result.md` Status/Decision to rehearsal: withdrawn “V2 demonstrates…” replaced with rehearsal disclaimer.
- Added this `execution-provenance-audit.md`.
- Left frozen blind judgments, sealed map, raw outputs **unchanged**.

Validation after correction: 45 total, 15 per condition, severe 2, no raw/blind change, blind commit ancestor intact, `validate-repo` PASS, no src/tests changes.
