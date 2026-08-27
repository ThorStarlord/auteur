# Global Map Architecture Value V1 — Evaluation Rubric

**Evaluation model: NOT “which sounds best” and NOT a single weighted aggregate.** Per-probe evidence-based judgments + global criteria. Blinded opaque labels only.

---

## Global criteria (apply per output)

| criterion | what to judge | material evidence cues |
|---|---|---|
| **SOURCE FIDELITY** | Faithful to accepted facts; no invented unsupported conditions | No mention of non-ledger events; `burn-archive` not invented as accepted |
| **CURRENT-STATE COMPATIBILITY** | Does not reason from superseded/contradicted state | Does not treat `public-admission` as current (P02/P05); does not treat `broken-lantern` as constraint |
| **LONG-HORIZON AWARENESS** | Notices consequential earlier commitments/setups/trajectories/consequences/future pressures | Cites `contested-history` pressure, `founding-record forged` (P01), `named-falsifier` resolution, `monastery-testimony` reactivation, `archive-protected` chain |
| **CAUSAL COHERENCE** | Respects prerequisite/consequence relationships | `retraction` → `treaty` (REL-05); burn destroys chain → cannot coexist with `treaty` (REL-07) |
| **DIRECTION / TRAJECTORY PRESERVATION** | Recognizes when locally attractive option damages established longer-range direction | Choosing burn or militia damages `contested-history` + Book3/4 change arcs; preservation via publish/hearing |
| **RELEVANCE** | Identifies what actually matters to current decision vs flooding with unrelated continuity | Omits `broken-lantern`/`repaired-lantern` and unaccepted `ally-militia`/`burn-archive` (unless probe tests burn) while keeping grouped history compact |
| **DECISION QUALITY** | Produces useful bounded recommendation / choice analysis | Clear recommendation among options with tradeoff, or explicit stale/incompatible rejection (P04) |
| **EXPLANATION TRACEABILITY** | Can explain WHY past element matters now | Uses `why-now` trace: e.g., “`monastery-testimony` preserved Book1 dormant → reactivated because Book4 intent references it” |
| **AUTHORITY CORRECTNESS** | Preserves recommendation vs accepted fact vs author decision | States recommendation is non-authoritative; does not claim choosing creates Book Direction/canon; does not treat proposed `burn-archive` as canon |
| **OVERCONSTRAINT / FALSE PRECISION** | Does architecture make provisional interpretation rigid law? | C does not treat `INTERPRETIVE` ledger entries (e.g., thematic REL-10) as hard constraints |
| **ARCHITECTURE DISTRACTION** | Does richer representation distort with irrelevant architecture? | C does not flood P02 with dormant testimony or detailed investigator change lines when not relevant |

Operational metadata (cost evidence, not quality): input/output tokens, latency, cost — from `run-manifest-template.md`.

---

## Probe-specific hidden expectations (DO NOT include in generator packet)

### P01 hidden

**Must-not-miss signals:**
- Notes `founding-record: forged` is newly active consequence constraining Book2 (ST-F1)
- Notes Series pressure `contested-history` still governs Book2 (REL-01)
- Notes `broken-lantern` and `monastery-testimony` are **not** current constraints (I1 dormant, I1 irrelevant) and explains omission
- Distinguishes pressure from concrete evidence (grouping)

**Forbidden assumptions:**
- Treat `book-2-burn-archive` (ST-P1) as accepted/current option
- Treat `monastery-testimony` as currently active (it is dormant until P03/P04 trigger)
- Invent extra Book2 state beyond `forged` record

### P02 hidden

**Must-not-miss:**
- Explicitly states `commitment-falsifier` is **resolved** (not active driver) due to `named-falsifier` (REL-03)
- Explicitly states `public-admission` is **superseded** by `retracted admission` and current is `retracted admission` (REL-04)
- Rationale uses **current** retraction + resolved falsifier outcome together

**Forbidden:**
- Treat `public-admission: admitted fraud` as current state
- Keep falsifier question as open driver
- Miss currentness (e.g., citing only `named-falsifier` and ignoring retraction)

### P03 hidden

**Must-not-miss:**
- Reactivates `monastery-testimony` **because** Book4 intent explicitly references it (REL-06)
- States `archive.protection = treaty protected` is current constraint requiring preservation (ST-F6)
- Explains causal link retraction → treaty (REL-05)

**Forbidden:**
- Present testimony as always active (ignore dormancy until trigger)
- Treat treaty as history only (it is current)
- Omit why testimony matters *now* (trigger)

### P04 hidden

**Must-not-miss:**
- Detects `burn-archive` is **incompatible** with current `archive.protection = treaty protected` (REL-07)
- Rejects burn (or marks unavailable) and recommends compatible alternative; cites `incompatible_with_state_refs` reason
- Notes `burn-archive` was never accepted (ST-P1 PROPOSED)

**Forbidden:**
- Recommend burn as valid/compatible
- Treat burn as accepted fact or as equal tradeoff without state check
- Conflate recommendation with canon (“burning would make it canon”)

### P05 hidden

**Must-not-miss:**
- Groups `founding-record` + `public-admission` (superseded) + `admission-retracted` + `archive-protected` as one `contested-history` pressure cluster, with current `retracted admission` / `treaty protected` as present evidence
- Excludes both `broken-lantern` and `repaired-lantern` (irrelevant) and unaccepted `ally-militia`
- Keeps Map compact (not unbounded dump, not recency window)

**Forbidden:**
- List every accepted transition as unrelated peers
- Promote irrelevant lantern due to recency
- Include unaccepted proposals

**Judgment rule:** Do not require one predetermined artistic taste among defensible options. Judge whether reasoning **noticed consequential constraints/opportunities**, not whether it matches a specific option. P04 is the only probe where burn must be rejected; otherwise either option A/B can be defensible if reasoning respects must-not-miss and avoids forbidden.

---

## Define “material architecture value” (preregistered)

- **Architecture-positive:** C uses a source-backed ledger relationship to produce consequentially better decision/explanation that A and/or B misses or handles materially worse. Examples: notices earlier setup others overlook; detects local choice breaks established trajectory; identifies prerequisite no longer exists; preserves future payoff others destroy; recognizes reactivated fact; explains relevance more clearly because relationship is explicit.
- **Architecture-neutral:** Richer representation produces no meaningful improvement.
- **Architecture-negative:** Explicit architecture causes false constraints, stale reasoning, unsupported certainty, irrelevant complexity, worse recommendation, authority confusion, or missed possibilities due to rigidity.

## Concept-level value trace (per candidate concept, per probe)

For each ledger category used by C, record after experiment:

| field | values |
|---|---|
| was_available? | yes/no (ledger contains it) |
| was_surfaces_in_Decision_Map? | yes/no |
| was_reasoning_used? | yes/no/partial |
| did_change_recommendation? | yes/no |
| did_improve_explanation? | yes/no |
| did_prevent_error? | yes/no (e.g., prevented burn) |
| did_introduce_cost/confusion? | yes/no (+ note) |
| was_redundant? | yes/no (duplicates another representation) |

Per-concept disposition after V1: **PROMISING** | **UNCLEAR** | **NEGATIVE** — not production-approved; promotion is later decision.

## Value / Cost interpretation (Track 8 principle, preserved)

- **HIGH VALUE / LOW COST → strongest candidate** for further productization
- **HIGH VALUE / HIGH COST → investigate automation or simpler representation**
- **LOW VALUE / LOW COST → probably unnecessary**
- **LOW VALUE / HIGH COST → remove or defer**

V1 evidence only moves concepts toward/away from further experimentation; does not create production schema.

## Invalidation conditions (weaken/invalidate comparison)

Comparison is invalid or weakened if:
- C received story facts unavailable to A (parity violation)
- Conditions used different creative questions
- Model/version changed mid-run without preregistered reason
- Evaluator learned condition identity before judgment (unblinding)
- Outputs manually edited before evaluation
- Production B was modified specifically for the test
- C ledger contains important unsupported narrative facts
- Run settings materially differed without reason
- Source fixture changed after some conditions ran

If any occurs later: record it; do **not** quietly repair and pretend original.

## Severe negative signals (separate record, not averaged away)

- Recommendation incompatible with accepted current state (e.g., burn when treaty exists)
- Derived interpretation treated as canonical fact
- Repeated false constraints
- Consistently narrowing creative possibility without source basis
- Provenance cannot explain important assertion source

A severe negative blocks “C wins on prose” averaging; must be escalated.

## Blind evaluation procedure

1. Export outputs under randomized opaque IDs (`X17`, `Q04`, …) per run manifest.
2. Evaluator receives only opaque outputs + rubric global criteria + per-probe must-not-miss/forbidden (without condition labels or expected winner).
3. Evaluator records per-probe judgments per criterion plus must-not-miss coverage and forbidden violations.
4. Keep condition mapping in separate sealed file; unblind only after judgments frozen.
5. If LLM evaluator used, prefer distinct model from generator; preserve human adjudication path for close/surprising.

## Freeze rule

Once this protocol merges: research question, A/B/C definitions, source revision `3cc4975...`, 5 probes, Condition C ledger (33 items), hidden expectations, rubric, repetition policy (3 per condition per probe), interpretation rules are **FROZEN** for V1. Flaw requiring change → create V2; do not silently rewrite V1. Minor typos recorded separately.
