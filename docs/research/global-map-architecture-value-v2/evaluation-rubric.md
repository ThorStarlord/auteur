# Global Map Architecture Value V2 — Evaluation Rubric (Corrected)

This is V2's rubric. For global criteria, material value, concept trace, value/cost, invalidation, and severe signals, it reuses V1's rubric unchanged (see `../global-map-architecture-value-v1/evaluation-rubric.md`). **Corrections in V2:** P05 probe-specific hidden expectations are moved to a consistent Book4 horizon paired with P03, and the blind-evaluation procedure is reaffirmed as generator-hidden / evaluator-visible.

V2 reuse:
- **Reused by reference (byte-identical intent):** global criteria (11), material value definitions, concept-level trace, value/cost matrix, invalidation×9, severe negatives.
- **V2 changes:** P05 hidden expectations horizon + pairing note; explicit statement that P03/P05 share Book4 horizon (not P02/P05).

---

## Probe-specific hidden expectations — V2 (DO NOT include in generator packet)

### P01 hidden — unchanged from V1
- Must-not-miss: `founding-record: forged` newly active constraining Book2; Series pressure `contested-history` governs Book2; `monastery-testimony` and `broken-lantern` not current constraints and explain omission; distinguish pressure from evidence.
- Forbidden: treat `burn-archive` as accepted; treat testimony as active; invent extra Book2 state.

### P02 hidden — unchanged from V1
- Must-not-miss: `commitment-falsifier` resolved via `named-falsifier`; `public-admission` superseded by `retracted admission` (current is retracted); rationale uses current retraction + resolved outcome together.
- Forbidden: treat `public-admission` as current; keep falsifier open; miss currentness.

### P03 hidden — unchanged from V1
- Must-not-miss: reactivate `monastery-testimony` because Book4 intent references it; state `archive.protection = treaty protected` current constraint; explain retraction → treaty causal link.
- Forbidden: present testimony as always active; treat treaty as history only; omit trigger why-now.

### P04 hidden — unchanged from V1 (evaluator-only, not leaked to generator)
- Must-not-miss: detect `burn-archive` incompatible with `archive.protection = treaty protected`; reject burn / mark unavailable, cite incompatibility reason; note burn was never accepted (unaccepted proposal).
- Forbidden: recommend burn as valid/compatible; treat burn as accepted fact; conflate recommendation with canon.
- **V2 packet ensures generator does NOT receive:** any `incompatible` label, `incompatible_with_state_refs`, reason *“Burning contradicts treaty”*, or instruction *“must reject burn”* — those are evaluator-only.

### P05 hidden — CORRECTED in V2 (Book4 paired with P03)

**Horizon:** Book4 opening (accepted history through Book3, Book4 planning intent), same as P03. Paired projection/mechanism isolation probe, not independent decision.

- **Must-not-miss (Book4 grouping/irrelevance):**
  - Groups accepted consequences that instantiate pressure `contested-history` (e.g., `founding-record forged` (history) + `public-admission`/`admission-retracted` lineage + `archive-protected treaty protected` (current)) as one compact pressure cluster with current `treaty protected` (and `admission-retracted` history explaining treaty) as present evidence — rather than listing as unrelated peers.
  - Excludes both `broken-lantern: broken` (older irrelevant) and `repaired-lantern: repaired` (recent irrelevant) and unaccepted proposals (`ally-militia`, and for P05 the burn content is not an option to include) from active Decision Map.
  - Keeps Map compact (not unbounded dump, not recency window) and gives specific why-now for grouped cluster and for reactivated `monastery-testimony` if surfaced.
- **Forbidden:**
  - List every accepted transition as unrelated peers.
  - Promote irrelevant lanterns due to recency.
  - Include unaccepted proposals.
- **Breadth interpretation:** P03 and P05 share the same Book4 question/options; they test decision quality (P03) vs projection compactness/irrelevance (P05) at the same horizon. Do **not** count P03/P05 as two independent Book4 decision replications; interpret as one decision family (paired). Total experiment remains 5 probes → 45 outputs but 4 independent situations (P01, P02, P03/P05 family, P04 adversarial variant).

**No other hidden expectations changed.** P01–P04 hidden signals remain verbatim V1 evaluator expectations, now correctly isolated from generator packets in V2.

---

## Blind evaluation (reaffirmed, unchanged from corrected V1 procedure)

1. Export outputs under randomized opaque IDs (`X17`, `Q04`, …).
2. **Blinded evaluator DOES receive:** opaque outputs + global rubric + per-probe must-not-miss/forbidden (evaluator needs these to judge). Does **NOT** receive condition labels, hidden mapping, or expected winner.
3. **Generator does NOT receive** any of the above hidden material.
4. Evaluator records per-probe judgments per criterion plus must-not-miss coverage and forbidden violations.
5. Keep condition mapping sealed; unblind only after judgments frozen.
6. If LLM evaluator used, prefer distinct model from generator; preserve human adjudication path.

## Reuse statement

All other rubric sections (global criteria, material value positive/neutral/negative, concept-level trace → PROMISING/UNCLEAR/NEGATIVE, value/cost matrix, invalidation, severe negatives, freeze rule) are **identical to V1** `../global-map-architecture-value-v1/evaluation-rubric.md` and are incorporated by reference without modification.
