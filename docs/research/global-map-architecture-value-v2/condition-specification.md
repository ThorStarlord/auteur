# Global Map Architecture Value V2 — Condition Specification (A/B/C) — Corrected

This is V2's condition specification. It reuses V1's research question, hypotheses, and treatment concept unchanged, except for the two defects corrected here: generator/evaluator leakage and P05 horizon. For the canonical V1 statement, see `../global-map-architecture-value-v1/condition-specification.md` (frozen, do not modify). V2 source-manifest, candidate-ledger, and run-manifest are **reused by reference** (see README).

## Research question (unchanged, preregistered)

> What explicit narrative architecture does Auteur need to make materially better long-horizon creative decisions than a prompt/context-only system and current Repeated Map/Focus, without unacceptable maintenance cost, false precision, stale structure, or authority confusion?

V1/V2 test **internal representational value**, not production UI or human usability.

## Conditions (concept unchanged; packets corrected for leakage)

### A — Prompt / Context-Only Baseline (strong, not crippled)

**What generator receives — V2 correction applies:**
- Horizon-appropriate accepted narrative facts as plain, source-faithful sentences (same facts that underlie B/C current state, e.g., `archive.founding_record = forged`, `archive.protection = treaty protected`), **without** precomputed treatment labels (`dormant`/`irrelevant`/`resolved`/`superseded`/`active`), without “must cite X”, without “this is irrelevant/omit”, without explicit causal/grouping interpretations, without compatibility answers.
- Current planning intent sentence (non-authoritative).
- Exact creative question + bounded option list **as defined in V2 `decision-probes.md`** (for P04, options contain no `incompatible` label or reason).
- Generic output contract + generic non-authoritative reminder (per `decision-probes.md`).

**Example prompt frame (frozen, de-leaked — identical structure across probes):**
```
You are a story consultant for Series Archive of Lies (ongoing, pressure: ...).
Accepted history through Book N: [plain fact sentences].
Current state: [key = value sentences].
Planning intent: [intent sentence].
Question: [exact question].
Options: [option_id: label — summary — tradeoff].
Task: Provide bounded recommendation analysis per output contract. Recommendation is not canon.
```

No ledger, no dispositions, no why-now derivations, no grouping.

### B — Current Auteur (shipped, unchanged)

Identical to V1: frozen revision `3cc4975...` behavior `repeated_map_focus.py` `select_repeated_continuity` (`_DERIVATION_VERSION=repeated-map-focus-v2-r1`) → `RepeatedBookPlanningContext` (active/reactivated entries, groups, why-now) + `CurrentStateEvidence`. Neutral adapter `B-context-to-prompt v1` pipes B's derived Map (compact entries/groups/history with source ids) into same generation prompt as A/C. No C ledger smuggling. If B cannot produce context for corrected V2 P05 (Book4 horizon), stop rather than modify B — audit in `evaluation-rubric.md` confirms B supports P05 at Book4 via same P03 horizon.

### C — Architecture-Rich (golden ledger, unchanged)

Same 33-item ledger `../global-map-architecture-value-v1/candidate-architecture-ledger.md` → Global Map (whole-story) → Decision Map (per-probe relevance-selected, includes P05 Book4 Decision Map derived from same ledger). Ledger not enriched after V1; defect was packet leakage, not richness.

## Information-parity rule (unchanged, critical)

All three conditions derive from same frozen sources `3cc4975...` (`../global-map-architecture-value-v1/source-manifest.md`). C may expose explicit derived relationships A must infer — that is the treatment. Every C statement traces to frozen source rows; unsupported fact → excluded or `INTERPRETIVE`. Advantage from **organization** valid; advantage from **extra facts** invalid → invalidation.

## Isolate representation from extraction (unchanged)

Ledger is hand-built golden; V2 does not test auto-extraction. Same isolation.

## Control variables (unchanged)

Same model/version, system role, question, output contract, `max_output_tokens` (e.g., 1200), sampling `temperature:0.2` `top_p:1.0`, tools `none`, fresh context, no carry-over, input/output hashes, latency/cost; deviation → logged, material → invalidation.

## Repetition / variance (unchanged, with clarified independence)

- **3 independent generations per condition per probe** = 3×3×5 = **45 outputs** (1× if deterministic).
- V2 has 5 probes but **4 independent creative-decision situations** (P05 paired with P03 at Book4; P04 is adversarial variant of same P03/P05 Book4 horizon). Do not interpret P03/P04/P05 as three independent replications nor P02/P05 as before; breadth claims count decision families, not probes. Previous V1 P02/P05 family is superseded.

## Blind evaluation — CORRECTED (now unambiguous and consistent with evaluation-rubric.md)

Contradiction in V1 `condition-specification.md` (“rubric hidden from evaluator”) vs `evaluation-rubric.md` (evaluator receives rubric) is **fixed in V2**:

- Outputs exported under randomized opaque labels (e.g., `X17`, `Q04`, `M22`) — never `A`/`B`/`C`.
- Condition mapping (`opaque_id → {A,B,C}`) kept in separate sealed file (`run-manifest` column `hidden_condition_id`) **not shared with evaluator; revealed only after evaluator judgments are frozen**.
- **Generator must NOT receive:** evaluation rubric, probe-specific must-not-miss signals, probe-specific forbidden assumptions, expected winner.
- **Blinded evaluator DOES receive:** opaque outputs, global evaluation rubric, probe-specific must-not-miss signals, probe-specific forbidden assumptions.
- **Blinded evaluator must NOT receive:** A/B/C condition identity, hidden condition mapping, expected experimental winner.
- If LLM evaluator used, prefer distinct model from generator; preserve human adjudication path.

This matches `../global-map-architecture-value-v1/evaluation-rubric.md` § Blind evaluation procedure and corrects V1 leakage where generator packets paraphrased hidden signals.

## Probe packet reproducibility (V2 packets)

Each condition packet defined by:
- `source_revision = 3cc4975...`
- Probe ID → horizon (V2 P05 = Book4 via P03, not Book3)
- Condition context block (A plain facts vs B derived Map vs C Decision Map from golden ledger)
- **Shared V2 generator-visible block** (`decision-probes.md` V2: horizon facts + intent + question + options + generic contract) — now de-leaked
- Frozen generation policy

No execution in this task.
