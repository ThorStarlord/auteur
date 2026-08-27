# Global Map Architecture Value Experiment V2 — Preregistered Protocol (CORRECTED)

**Status:** `CORRECTED PREREGISTRATION` — **FROZEN for execution** once merged. This V2 corrects two pre-run validity defects in V1 before any model runs. **V1 remains:** `FROZEN, NOT EXECUTED, SUPERSEDED FOR EXECUTION BY V2 DUE TO PRE-RUN PROTOCOL LEAKAGE / HORIZON DEFECT` (`docs/research/global-map-architecture-value-v1/` — do not modify). No experimental outputs exist; no results discarded.

**Source revision (unchanged):** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge, `origin/main`).
**Experiment version:** `global-map-architecture-value-v2` (successor to `global-map-architecture-value-v1`).
**Artifacts:** `docs/research/global-map-architecture-value-v2/` (`README.md`, `decision-probes.md`, `condition-specification.md`, `evaluation-rubric.md`) plus reused-by-reference `../global-map-architecture-value-v1/source-manifest.md`, `candidate-architecture-ledger.md`, `run-manifest-template.md`. This file is the V2 summary entry point.

---

## Why V2 (two defects, pre-execution)

1. **Generator/evaluator leakage:** V1's `decision-probes.md` generator-visible packets paraphrased hidden evaluator expectations (e.g., labeled `monastery-testimony` “dormant”, `broken-lantern` “irrelevant”, `public-admission→retraction` as supersession chain, `burn-archive “incompatible”` + reason, “rationale must cite X”, “must not treat as current”). That lets a generator satisfy must-not-miss/forbidden by repeating instructions rather than via the treatment (A raw vs B derived Map vs C explicit ledger). V2 de-leaks generator packets.
2. **P05 inconsistent horizon:** V1 P05 was described as paired with P02 / Book3 opening but contained Book3 realizations (`archive-protected`, `repaired-lantern`) while allowing either Book3 or Book4 intent — not one reproducible horizon. V2 pairs P05 with P03 at a consistent **Book4 opening** (through Book3, Book4 intent, same question/options as P03), legitimately containing both lanterns, founding-record history, admission/retraction history, and current `archive-protected` while testing compact grouping/irrelevance at a valid decision boundary.

V2 is the smallest possible fix; all else in V1 is preserved.

---

## 1. Research question (unchanged)

> What explicit narrative architecture does Auteur need to make materially better long-horizon creative decisions than a prompt/context-only system and current Repeated Map/Focus, without unacceptable maintenance cost, false precision, stale structure, or authority confusion?

V2 tests **internal representational value** (“does richer architecture improve reasoning?”). If weak/negative, production Global Map UI may not be warranted.

Hypotheses (intent unchanged):
- `H0`: No material improvement over strong prompt/context and shipped Map/Focus.
- `H1`: Source-backed explicit relationships enable C to notice consequential constraints/opportunities that A/B miss, improving decision quality and explanation traceability without severe false-constraint/authority harm.

## 2. Conditions (concept unchanged; packets corrected)

- **A — Prompt/context-only baseline:** Plain, source-faithful facts for the probe horizon (e.g., fact lists + current state key=values) **without** treatment labels (`dormant`/`irrelevant`/`resolved`/`superseded`/`active`), without “must cite”, without omission instructions, without explicit causal/grouping interpretations, without compatibility answers. Strong baseline — A has enough to infer relationships.
- **B — Current Auteur:** Shipped `repeated-map-focus-v2-r1` (`src/auteur/series/repeated_map_focus.py` `select_repeated_continuity`) on same snapshot → `RepeatedBookPlanningContext`; neutral adapter `B-context-to-prompt v1` into same generation prompt. No modification; B supports corrected P05 at Book4 (same horizon as P03).
- **C — Architecture-rich (golden):** Same 33-item ledger (`../global-map-architecture-value-v1/candidate-architecture-ledger.md`) → Global Map → Decision Map per probe (including corrected P05 Book4 Decision Map). Ledger not enriched.

All derive from same frozen sources `3cc4975...`; every C statement traces to frozen rows; extra-facts advantage → invalidation.

## 3. Fixture selection (unchanged, honest limitation)

- **Archive of Lies** via `tests/fixtures/repeated_map_focus_v2/` (R1–R3 ledger: pressure, founding-record forged, falsifier resolved, admission→retraction, treaty-protected archive, dormant testimony, plus irrelevant/burn/militia negatives). Sufficient for V2's 5 useful mechanism configurations.
- No second tracked long-form fixture with comparable depth; V2 remains **directional single-fixture** (not generality claim).

## 4. Probes — V2 (5, frozen; 4 independent situations; P05 paired with P03)

| id | book opening | mechanisms | question | options |
|---|---|---|---|---|
| P01 Activation | 2 | consequence activation, irrelevance filtering, grouping | How make exposed fraud matter to lived memory? | witness vs cover-up |
| P02 Resolution/Supersession | 3 | resolved omission, superseded currentness | How respond to retraction while preserving witness? | publish-witness vs hearing |
| P03 Reactivation | 4 | dormant→reactivated, causal treaty | How bring testimony back without destroying chain? | publish-verified vs protected-hearing |
| P04 Incompatibility | 4 | state-compatibility, authority | Same, with burn-archive (no compatibility label) | burn (unlabeled) vs publish |
| P05 Grouping — **paired with P03** | 4 | pressure grouping, recency filtering | **Same as P03** (isolation probe, not independent decision) | same as P03 |

5 probes total but **4 independent creative-decision situations** (P03/P04/P05 share Book4 horizon; P03/P05 are one decision family for breadth; do not claim “two independent Book-4 decisions”). Same question across A/B/C per probe; 3 reps per condition per probe = **45 outputs** (15 if deterministic). Generator-visible specs are de-leaked in `global-map-architecture-value-v2/decision-probes.md`; hidden must-not-miss/forbidden in `evaluation-rubric.md` (evaluator-only).

## 5. Controls (unchanged)

Same model/version, system role, question, output contract (bounded recommendation + why + tradeoff + excluded, generic), max tokens, sampling `temperature 0.2` `top_p 1.0`, tools `none`, fresh context, no carry-over; deviation → logged, material → invalidation.

## 6. Blind evaluation (CORRECTED, unambiguous)

- Opaque IDs (`X17`/`Q04`) not `A`/`B`/`C`; sealed `hidden_condition_id` revealed only after judgments frozen.
- **Generator must NOT receive:** rubric, must-not-miss, forbidden, expected winner.
- **Blinded evaluator DOES receive:** opaque outputs, global rubric, per-probe must-not-miss, forbidden.
- **Blinded evaluator must NOT receive:** A/B/C identity, hidden mapping, expected winner.
- Prefer evaluator model distinct from generator; human adjudication path.

Matches V2 `condition-specification.md` and V2 `evaluation-rubric.md`.

## 7. Evaluation (no single aggregate, unchanged)

Global criteria per output (11): source fidelity, current-state compatibility, long-horizon awareness, causal coherence, direction preservation, relevance, decision quality, explanation traceability, authority correctness, overconstraint/false precision, architecture distraction; plus tokens/latency/cost. Per-probe hidden must-not-miss & forbidden (V2 P05 hidden moved to Book4, see `evaluation-rubric.md`). Judgment evidence-based, not taste-matched (either A/B defensible except P04 burn must be rejected via hidden criterion, not generator label). Material value: C uses source-backed relationship to produce better decision/explanation or prevent error that A/B miss; neutral = no improvement; negative = false constraints/distraction/authority confusion.

Per-concept trace after unblinding: available / surfaced / used / changed / improved / prevented / cost / redundant → `PROMISING`/`UNCLEAR`/`NEGATIVE`. Value/cost matrix preserved. V2 does **not** create production schema.

Invalidation×9 and severe negatives (separately recorded, not averaged) preregistered and unchanged.

## 8. Freeze rule (V2)

On merge, this V2 protocol is frozen for execution. Flaw requiring change → create V3; no silent rewrite after outputs. V1 remains immutable. Minor typos recorded separately.

## 9. Scope (what is NOT in V2)

No production implementation: no `src/`/`tests/`/CLI/Map-Focus runtime/architecture/ontology/schemas/persistence/UI/`.github/workflows`/build changes; no ADR; no new semantic layer; no relevance engine; no model calls, no outputs, no winner declared.

## 10. Interpretation after execution

If C shows consistent architecture-positive signals (notices setups, detects trajectory break, preserves payoff, reactivates, explains) without severe negatives → warrants V3 extraction + later Global Map UX study. If neutral/negative → defer production architecture. Severe negative not averaged away. Breadth claims must count decision families (P03/P05 = one), not probes.

---

## Next step

After review and merge: **execute V2 without redesigning** (`global-map-architecture-value-v2/` + reused V1 source-manifest/ledger/run-manifest).

## V1 → V2 delta (compact)

| defect | V1 generator packet | V2 correction |
|---|---|---|
| leakage | contained must-not-miss paraphrases, “must cite”, dormant/irrelevant/superseded labels, P04 `incompatible` + reason | only plain facts + generic contract; treatment carries distinctions |
| P05 horizon | ambiguous (Book3 question + Book3 realizations + either intent) paired (stated) with P02 | unambiguous Book4 opening paired with P03 (through Book3, Book4 intent, same Q as P03) |

All other V1 intent reused by reference.

## Quality check (V2)

All 15 V1 quality questions remain answered in `global-map-architecture-value-v2/README.md` context, with P05 horizon and leakage answers updated per this correction.
