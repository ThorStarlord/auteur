# Global Map Architecture Value Experiment V1 — Preregistered Protocol (FROZEN)

**Status:** `FROZEN` — research question, hypotheses, A/B/C definitions, frozen sources, 5 decision probes, Condition C ledger, hidden evaluator expectations, rubric, repetition policy, and interpretation rules are locked for V1. Material change requires V2.

**Source revision:** `3cc497583dcb9b3bcee5ba273ee8bcbf27cbba41` (PR #143 merge, `origin/main`).
**Experiment version:** `global-map-architecture-value-v1`
**Artifacts:** `docs/research/global-map-architecture-value-v1/` (`README.md`, `source-manifest.md`, `candidate-architecture-ledger.md`, `decision-probes.md`, `condition-specification.md`, `evaluation-rubric.md`, `run-manifest-template.md`); this file is the summary entry point.

---

## 1. Research question

> What explicit narrative architecture does Auteur need to make **materially better** long-horizon creative decisions than a prompt/context-only system and current Repeated Map/Focus, without unacceptable maintenance cost, false precision, stale structure, or authority confusion?

Primary focus for V1 is **internal representational value** (“does richer architecture actually improve reasoning?”), not production UI quality or human usability. If answer is weak/negative, a production Global Map UI may not be warranted.

Hypotheses:
- `H0` (null): Richer explicit architecture provides no material improvement over strong prompt/context and shipped Map/Focus.
- `H1`: Source-backed explicit relationships (settlement→payoff, supersession/currentness, dormant→reactivated, causal dependencies, pressure grouping) enable C to notice consequential constraints/opportunities that A/B miss, improving decision quality and explanation traceability without introducing severe false-constraint or authority harm.

## 2. Conditions (frozen, single-fixture directional test)

- **A — Prompt/Context-only baseline:** Capable model receives frozen narrative sources (Series Direction, relevant Book Directions/Realizations, Canonical State as plain key=values) + planning intent + exact question/options. No explicit ledger, dispositions, or grouping. Strong prompt, not crippled.
- **B — Current Auteur:** Shipped `repeated-map-focus-v2-r1` (`src/auteur/series/repeated_map_focus.py` `select_repeated_continuity`) on same snapshot. Outputs `RepeatedBookPlanningContext` (active/reactivated entries, groups, why-now, `generated_from`). Neutral adapter `B-context-to-prompt v1` pipes B's Map into same decision prompt as A/C — no C architecture smuggled.
- **C — Architecture-rich (golden ledger):** Hand-built, source-faithful research ledger (33 items) → Global Map (whole-story projection: What is story / Where going / trajectories / established / unresolved / relationships) → relevance-selected Decision Map per probe → same question. Not production schema, not auto-extracted; isolates value-of-representation from extraction quality.

All derive from **same frozen sources** (`source-manifest.md`). C may expose derived relationships A must infer, but every statement traces to frozen source rows; unsupported fact → excluded or `INTERPRETIVE`.

## 3. Fixture selection (honest limitation)

- **Archive of Lies** via `tests/fixtures/repeated_map_focus_v2/` supplies qualified R1–R3 ledger (Series pressure, founding-record forged, falsifier resolved, admission→retraction supersession, treaty-protected archive, dormant monastery testimony, plus irrelevant/burn/militia negatives). Sufficient for 5 useful mechanism configurations across 4 independent creative-decision situations (P05 is paired with P02 to isolate grouping/irrelevance; see `decision-probes.md`).
- **No second tracked long-form fixture** with comparable depth exists in `tests/fixtures/`; V1 is therefore **directional single-fixture**, not generality claim. Limitation is explicitly recorded rather than inventing fake breadth.

## 4. Probes (5, frozen — 4 independent decisions + 1 paired mechanism probe)

| id | book | mechanisms | question | options |
|---|---|---|---|---|
| P01 Activation | 2 | consequence activation, irrelevance filtering, grouping | How make exposed fraud matter to lived memory? | witness vs cover-up |
| P02 Resolution/Supersession | 3 | resolved omission, superseded currentness | How respond to retraction while preserving witness? | publish-witness vs hearing |
| P03 Reactivation | 4a | dormant→reactivated, causal treaty | How bring testimony back without destroying chain? | publish-verified vs protected-hearing |
| P04 Incompatibility | 4b | state-compatibility, authority | Same, with burn-archive incompatible option | burn (incompatible) vs publish |
| P05 Grouping — paired with P02 | 3 | pressure grouping, recency filtering | Same as P02 (grouping focus) — paired isolation probe | same as P02 |

5 probes total, 4 independent creative-decision situations; P05 intentionally reuses P02's question/options to isolate pressure-grouping and irrelevance-filtering behavior and must not be interpreted as a second independent decision replication (P02/P05 = one decision family for breadth claims).

Generator-visible specs in `decision-probes.md`; hidden must-not-miss/forbidden in `evaluation-rubric.md` (not sent to generator). Same question across A/B/C per probe; fresh context each; 3 reps per condition per probe = **45 outputs** (or 15 if deterministic).

## 5. Controls

- Same model/version, system role, question, output contract (bounded recommendation + why past matters + tradeoff + excluded), max tokens, sampling `temperature 0.2`, tools `none`, fresh context, no carry-over. Values recorded in run manifest; seed if supported else `NO_SEED_SUPPORT`. Deviation → logged, material → invalidation.

## 6. Blind evaluation

Opaque IDs (`X17`/`Q04`) not `A`/`B`/`C`; sealed `hidden_condition_id`; evaluator sees only outputs + rubric global criteria + per-probe hidden signals; expected winner never revealed; prefer evaluator model distinct from generator; human adjudication path for close cases.

## 7. Evaluation (no single aggregate)

Global criteria per output: source fidelity, current-state compatibility, long-horizon awareness, causal coherence, direction preservation, relevance, decision quality, explanation traceability, authority correctness, overconstraint/false precision, architecture distraction; plus tokens/latency/cost. Per-probe hidden must-not-miss & forbidden (see `evaluation-rubric.md`). Judgment is evidence-based, not taste-matched (either A/B defensible except P04 burn must be rejected). Material value defined as C using source-backed relationship to produce better decision/explanation or prevent error that A/B miss; neutral = no improvement; negative = false constraints/stale/distraction/authority confusion.

Per-concept trace after unblinding: available / surfaced / used / changed recommendation / improved explanation / prevented error / introduced cost / redundant → `PROMISING`/`UNCLEAR`/`NEGATIVE`. Value/cost matrix: high/low → strong candidate; high/high → automate/simplify; low/low → probably unnecessary; low/high → remove. V1 does **not** create production schema; it only moves concepts toward further experimentation.

Invalidation (9) and severe negatives (separately recorded, not averaged) are preregistered in `evaluation-rubric.md`.

## 8. Freeze rule

On merge, this protocol is frozen for V1. Flaw requiring change → create V2; no silent rewrite after outputs. Minor typos recorded separately.

## 9. Scope (what is NOT in V1)

No production implementation: no `src/`/`tests/`/CLI/Map-Focus runtime/architecture/ontology/schemas/persistence/UI/`.github/workflows`/build changes; no ADR; no new semantic layer; no relevance engine/graph ranking; no model calls, no outputs, no winner declared.

## 10. Interpretation after execution

If C shows consistent architecture-positive signals (notices setups, detects trajectory break, preserves payoff, reactivates, explains) without severe negatives → warrants V2 extraction + later Global Map UX study. If neutral/negative → defer production architecture. Severe negative not averaged away.

---

## Next step

After review and merge: **execute the frozen experiment without redesigning V1** (`condition-specification.md` + `run-manifest-template.md`).

## Quality check

The 15 questions from the task are answered in `README.md` (§ Quality check). All are resolved within research-design scope.
