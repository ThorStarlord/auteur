# Global Map Architecture Value V1 — Decision Probes (Generator-Visible)

**Do not confuse generator input with evaluator key.** This file is the **generator-visible** frozen probe packet definition. Hidden evaluator expectations (`must-not-miss`, `forbidden`, per-concept expectations) are in `evaluation-rubric.md` and must **not** be included in the generation prompt.

Same creative question is used across A/B/C for a given probe. Fresh context per run, no carry-over.

Probe honesty: 5 probes total. Archive of Lies provides 5 genuinely independent mechanisms; no padding, no invented events. Single-fixture limitation is recorded (see source-manifest).

---

## Generation contract (all probes)

Output contract (same for A/B/C):
- Provide a bounded recommendation analysis: which option you recommend among the presented options, why (cite past commitments/state that matter now), principal tradeoff, and what you deliberately excluded.
- Must cite which accepted facts/commitments you relied on (by plain name, not internal IDs).
- Must not invent unsupported facts; must not treat proposed/unaccepted material as accepted.
- Must state that recommendation is non-authoritative (does not create Book Direction/canon).

The generator receives **only** the sections below per probe. It does **not** receive hidden expectations, rubric, or condition labels.

---

## Probe P01 — Activation (Book 2 opening)

**Mechanisms exercised:** long-range consequence activation, relevance selection, irrelevance filtering, grouping.

**Frozen story state:** Through Book 1 accepted history.
- Series: `contested-history` active, `commitment-falsifier` unresolved, pressure official-history vs lived memory
- Book 1 Direction: `The Missing Ledger` carries `contested-history`, open question *Who falsified record?*
- Realizations accepted: `founding-record: forged`, `monastery-testimony: preserved` (dormant), `broken-lantern: broken` (irrelevant)
- Canonical State: `archive.founding_record=forged`
- Book 2 Direction **not yet accepted**; `book-2-burn-archive` **proposed not accepted** (must not be used)

**Current planning intent (Book 2):** *Make the forged founding record matter to lived memory.* (trigger ref `founding-record`)

**Available accepted sources (generator may reference):** `series_direction.yaml`, `book_1_direction.yaml`, `book_1_realization.yaml` (and derived Canonical State above)

**Exact creative question:**
> How should Book 2 make the exposed fraud matter to lived memory?
Options (bounded set, from `decision_seeds` analogue for Book2 — use probe-supplied options):
- A) Center the living witness's account against the forged record
- B) Trace the institutional cover-up that produced the forged record
(Recommendation must include rationale citing active Series pressure + forged-record state, and a specific tradeoff distinguishing testimony vs institutional emphasis.)

**Authority constraints:** No Book2 canon exists yet; `burn-archive` is unaccepted and must not be treated as current option; choosing an option records workflow history only.

**Candidate concepts exercised:** Series/Book direction, commitment (`contested-history`), setup `founding-record`, current state `forged`, unresolved `falsifier` question, relevance trigger, irrelevant filtering (`broken-lantern`, `monastery-testimony` dormant), pressure grouping.

---

## Probe P02 — Resolution & Supersession (Book 3 opening)

**Mechanisms exercised:** resolved commitment omission, superseded state currentness, current-state compatibility, why-now explanation.

**Frozen story state:** Through Book 2.
- Adds: `book_2_direction.yaml` (continues pressure), `book_2_realization.yaml` (`named-falsifier: named` resolves `commitment-falsifier`; `public-admission: admitted fraud` → `admission-retracted: retracted admission` supersession chain)
- Canonical State: `council.archive_position=retracted admission` (current), `archive.falsifier=named` (resolved), `archive.founding_record=forged` (history)
- Unaccepted: `book-2-burn-archive`, `book-3-ally-militia` excluded; `broken-lantern` remains irrelevant
- Book3 Direction not yet accepted at opening; planning intent is non-authoritative trigger only

**Current planning intent (Book 3):** *Respond to the council's accepted retraction.* (trigger ref `admission-retracted`)

**Available accepted sources:** adds `book_2_direction.yaml`, `book_2_realization.yaml` to P01 sources

**Exact creative question:**
> How should Book 3 respond to the council's retraction while preserving the witness's authority?
Options:
- A) `publish-witness-account` — give witness independent public record council cannot retract (tradeoff: protects authority but exposes witness to retaliation)
- B) `force-council-hearing` — use named falsifier to compel council to answer in public (tradeoff: keeps accountability central but council controls forum/timing)
Rationale must use current retraction + resolved falsifier outcome; recommendation must not treat `public-admission` as current.

**Authority constraints:** Resolved `commitment-falsifier` is history support only, not active driver; `public-admission` must not be presented as current state.

**Concepts:** commitment resolution, supersession/currentness, current state, causal consequence, future direction (preserve witness).

---

## Probe P03 — Dormant Reactivation & Causal Dependency (Book 4 opening, valid options)

**Mechanisms exercised:** dormant→reactivated, causal dependency, treaty as current constraint.

**Frozen story state:** Through Book 3.
- Adds: `book_3_direction.yaml` (protect archive after retraction), `book_3_realization.yaml` (`archive-protected: treaty protected`, `repaired-lantern: repaired` irrelevant)
- History: `founding-record forged`, `admission-retracted` (history), `archive-protected` current, `monastery-testimony preserved` dormant until now
- Canonical State: `archive.protection=treaty protected`
- Unaccepted: `ally-militia` excluded; Book4 Direction not yet accepted

**Current planning intent (Book 4):** *Return to the monastery testimony without breaking the protected archive.* (trigger refs `monastery-testimony` + `archive-protected`)

**Available accepted sources:** all above through Book3 + `book_4_planning_intent.yaml`

**Exact creative question:**
> How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?
Options:
- A) `publish-verified-testimony` — authenticate/publish testimony while protected archive keeps original secure (tradeoff: preserves chain, delays release)
- B) `stage-protected-hearing` — present testimony beside selected archive evidence under treaty protections (tradeoff: immediate pressure, reveals strongest records)
Rationale must cite reactivated testimony (Book4 intent trigger) + current treaty protection.

**Authority constraints:** Testimony was dormant (accepted but not relevant until Book4 trigger); archive protection is current constraint; recommendation non-authoritative.

**Concepts:** dormant reactivation, causal dependency (retraction→treaty), current state, relationship trajectory (testimony ↔ archive), future intent, grouping (founding fraud + retraction + treaty as history-of-archive).

---

## Probe P04 — State-Incompatible Option & Authority Correctness (Book 4 burn variant)

**Mechanisms exercised:** state-compatibility validation, forbidden assumption detection, recommendation vs canon.

**Frozen story state:** Identical to P03 (through Book 3, same Canonical State `archive.protection=treaty protected`, same reactivated testimony).

**Current planning intent:** Same as P03.

**Available accepted sources:** Same as P03.

**Exact creative question (adversarial variant):**
> How should Book 4 bring the monastery testimony back into public memory without losing the archive's evidentiary chain?
Options (includes incompatible option):
- A) `burn-archive` — destroy archive so monastery testimony becomes only surviving account (**incompatible**: destroys accepted `treaty protected` chain; reason: *Burning contradicts current archive.protection = treaty protected* — per `decision_seeds.yaml` `incompatible_with_state_refs`)
- B) `publish-verified-testimony` — authenticate/publish while preserving archive (same as P03 A)
Rationale must detect incompatibility and **not** recommend burn; must explain why burn is unavailable despite dramatic appeal.

**Authority constraints:** `burn-archive` was never accepted (`book-2-burn-archive`/`book_four_burn_archive` seed); even if recommended, `validate_repeated_decision_proposal` would reject; choosing B does not create Book4 Direction.

**Concepts:** state-compatibility, authority correctness (proposed vs accepted), overconstraint detection, explanation traceability.

---

## Probe P05 — Irrelevance Filtering & Pressure Grouping (Book 3 grouping check)

**Mechanisms exercised:** irrelevance filtering across recency, pressure grouping compactness, why-now concision.

**Frozen story state:** Same as P02/P03 boundary (through Book 2 + Book 3 realizations). Recent but irrelevant `repaired-lantern: repaired` and older irrelevant `broken-lantern: broken` both present; `founding-record`, `public-admission`, `admission-retracted`, `archive-protected` instantiate one pressure `contested-history`.

**Current planning intent:** Either Book3 intent (*Respond to retraction*) or Book4 intent (same as P03) — probe tests grouping independent of specific question: at this horizon, grouped history-of-the-archive should be compact, not an unbounded dump, and irrelevant lanterns must be excluded.

**Available accepted sources:** Same as P02/P03.

**Exact creative question (use P02 question to isolate grouping, not new decision):**
> How should Book 3 respond to the council's retraction while preserving the witness's authority? (same as P02)
Options same as P02. Evaluation focuses on whether reasoning groups `founding-record`→`public-admission`→`admission-retracted`→`archive-protected` as one pressure cluster with current `retracted admission` / `treaty protected` as evidence, rather than listing as unrelated peers, and whether it excludes `broken-lantern`/`repaired-lantern` and unaccepted `ally-militia`.

**Authority constraints:** Grouping is projection-local, not universal taxonomy; irrelevant facts remain accepted but not surfaced.

**Concepts:** relevance selection, pressure grouping, irrelevance filtering, explanation traceability.

---

## Frozen packet summary

| probe | book | planning intent | available history | question | options | primary mechanisms |
|---|---|---|---|---|---|---|
| P01 | 2 | DIR-INT2 | Series+Book1 | fraud→lived memory | 2 (witness vs cover-up) | activation, irrelevance, grouping |
| P02 | 3 | DIR-INT3 | +Book2 | retraction + witness | 2 (publish vs hearing) | resolution, supersession, currentness |
| P03 | 4a | DIR-INT4 | +Book3 | testimony without destroying chain | 2 (publish vs protected hearing) | reactivation, causal dependency |
| P04 | 4b | DIR-INT4 | +Book3 | testimony (burn variant) | 2 (burn incompatible vs publish) | state-compatibility, authority |
| P05 | 3 | DIR-INT3/4 | +Book3 | same as P02 (grouping focus) | 2 (same) | irrelevance filtering, grouping |

All probes use same sources across A/B/C. Hidden evaluation only in `evaluation-rubric.md`.
