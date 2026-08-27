# Global Map Architecture Value V2 — README (Leakage Correction)

**Version:** `global-map-architecture-value-v2` — **CORRECTED PREREGISTRATION, NOT YET EXECUTED**
**Replaces for execution:** V1 is frozen, unexecuted, superseded due to pre-run leakage / P05 horizon defect (see `../global-map-architecture-value-v1/` — do not modify V1).

**Source revision (unchanged):** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge)
**Ledger (unchanged):** 33-item golden ledger `../global-map-architecture-value-v1/candidate-architecture-ledger.md`
**Source manifest / run-manifest (reused by reference):** `../global-map-architecture-value-v1/source-manifest.md` and `run-manifest-template.md` — not duplicated.

---

## What V2 fixes (only two defects)

1. **Generator/evaluator leakage:** V1 generator packets paraphrased hidden must-not-miss/forbidden and revealed compatibility. V2 generator packets contain only narrative task information (horizon facts + intent + question + options + generic contract). Treatment differences (A raw, B derived Map, C explicit ledger) now carry the distinctions.
2. **P05 horizon:** V1 P05 was ambiguous (Book3 question + Book3 realizations + either intent). V2 P05 is unambiguously **Book4 opening, paired with P03** (through Book3, Book4 intent, same question/options as P03), enabling valid irrelevance/grouping test with both lanterns and archive-protected history at a consistent boundary.

All else preserved: research question, H0/H1, A/B/C concept, strong A, shipped B (`repeated-map-focus-v2-r1`), golden C, parity, isolation, controls (`temperature 0.2`, `top_p 1.0`, no tools, fresh context, 3 reps → 45 outputs), blinding (evaluator sees rubric + hidden signals, not mapping/winner), evaluation model, invalidation, severe signals, no production claims.

---

## Artifacts in this V2 directory

| file | purpose | generator sees? | evaluator sees? |
|---|---|---|---|
| `decision-probes.md` | **V2 de-leaked** 5 probes (4 independent situations; P05 paired with P03) | **yes** (de-leaked) | yes |
| `condition-specification.md` | **V2 corrected** A/B/C + leakage separation + P05 pairing note | yes (as packets) | blind mapping hidden |
| `evaluation-rubric.md` | **V2 corrected** P05 hidden at Book4 + reaffirmed blind procedure | **no** (hidden) | **yes** |
| `README.md` | This file | — | — |

**Reused by explicit reference (not duplicated):** `../global-map-architecture-value-v1/source-manifest.md`, `candidate-architecture-ledger.md`, `run-manifest-template.md`.

Top-level `../global-map-architecture-value-experiment-v2.md` is the V2 summary entry point.

---

## How to run V2 (without redesigning)

1. Checkout `3cc4975...`, read reused source-manifest + ledger.
2. For each V2 probe P01–P05 (note P05 = Book4 paired with P03), build 3 condition packets per V2 `condition-specification.md` (A plain facts vs B derived Map vs C Decision Map).
3. Generate 3 independent outputs per condition per probe under opaque IDs (45 outputs).
4. Blind-evaluate with V2 `evaluation-rubric.md` (P05 hidden is Book4 grouping now).
5. Unblind per concept trace; apply value/cost.

No execution in this task.

---

## V1 vs V2 (compact)

| aspect | V1 (frozen) | V2 (corrected) |
|---|---|---|
| P04 options | labeled `incompatible` + reason given to generator | no compatibility labeling; evaluator-only |
| P01–P03 generator text | contained “must cite”, “must not treat as current”, dormant/irrelevant labels | only plain facts + generic contract |
| P05 horizon | ambiguous Book3 (mixed) paired (stated) with P02 | unambiguous Book4 paired with P03 |
| independent situations | stated as 5 probes total but claimed “genuinely independent” | 5 probes, 4 independent situations (P03/P05 family) for breadth |
| blind separation | contradictory (rubric hidden from evaluator) | unambiguous: generator hidden, evaluator sees rubric + signals, mapping sealed |

---

## Leakage & horizon audits (V2 self-check)

- **Leakage audit:** Each V2 probe packet contains no must-not-miss paraphrase, no forbidden warning, no “incompatible” label, no supersession/resolved/irrelevant terminology that is the treatment; a generator cannot satisfy hidden criteria by repeating packet instructions.
- **Condition-A audit:** A receives all horizon-appropriate accepted facts and underlying current-state values for each probe (same facts as C, just not organized); no relevant fact selectively removed; no future fact leaks across horizon.
- **Condition-B audit:** Shipped `select_repeated_continuity` supports corrected P05 at Book4 (same horizon as P03); no B modification.
- **Condition-C audit:** Same 33-item ledger supports V2 P05 Book4 Decision Map (archive-protected + both lanterns + grouped history + reactivated testimony).

---

## Next

After review and merge: execute V2 (`NEXT: Auteur — Global Map — Architecture Value Experiment V2 — Execution`). Do not modify V1; do not execute in this run.
