# Global Map Architecture Value V2 — Decision Probes (Generator-Visible)

**Status:** V2 corrected preregistration. This file is the generator-visible packet definition. Hidden evaluator expectations are in `evaluation-rubric.md` and must **not** be included in generation.

**V1 status:** `docs/research/global-map-architecture-value-v1/decision-probes.md` remains frozen, unexecuted, superseded for execution due to pre-run leakage / P05 horizon defect. Do not modify V1.

**Invariant:** 5 probes total, 4 independent creative-decision situations, P05 paired with P03 for projection/isolation. 45 planned outputs (5×3×3).

Same question across A/B/C per probe; fresh context per run; no carry-over.

---

## Generation contract (all probes, generic only)

Each generation receives (via its condition packet per `condition-specification.md`):

- Probe identifier (e.g., `P01`)
- Narrative horizon and accepted story history as plain source-faithful facts (same facts across A/B/C, presentation differs by condition)
- Current planning intent sentence (source-faithful, non-authoritative)
- Exact creative question
- Bounded option list (`option_id`, `label`, `summary`, `tradeoff`)
- Output contract:

```
Provide a bounded recommendation analysis:
- which option you recommend among the presented options (or that none is viable if truly incompatible),
- why (cite past commitments/facts that matter now),
- principal tradeoff,
- what you deliberately excluded as not relevant.

Cite which accepted facts/commitments you relied on by plain name (not internal IDs).
Do not invent unsupported facts; do not treat unaccepted material as accepted.
Recommendation is non-authoritative: choosing an option does not create Book Direction or canon and does not modify Canonical State.
```

The generator receives **only** the sections below per probe (plus its condition-specific context block). It does **not** receive: mechanisms, candidate concepts, must-not-miss, forbidden, expected winner, or treatment-specific dispositions.

---

## Probe P01 — Book 2 opening

**Narrative horizon:** Accepted history through Book 1.

**Accepted story history (plain facts):**
- Series: `Archive of Lies`, `ongoing`, promise *Each recovered account reveals who profits when history is controlled*, pressure *Every public correction gives hidden archivists reason to erase another witness*, commitments `contested-history: Every Book must expose conflict between official history and lived memory` and `commitment-falsifier: person who falsified founding record must be identified`, open question *Can truth survive without becoming instrument of power?*
- Book 1 Direction: `The Missing Ledger` — want *Recover ledger that proves city falsified archive* ; resistance *custodians erase witnesses* ; conflict *authenticate while choosing witnesses* ; stakes *publish too soon destroys witnesses / waiting erases truth*.
- Book 1 Realization: founding record was forged; monastery preserves a testimony; a lantern was broken during the archive search.
- Current state: `archive.founding_record = forged`; `monastery.testimony = preserved`; `archive_lantern.condition = broken`.

**Current planning intent (Book 2):** *Make the forged founding record matter to lived memory.*

**Exact creative question:**
> How should Book 2 make the exposed fraud matter to lived memory?

**Bounded options:**
- A) `witness-account` — Center the living witness's account against the forged record — tradeoff: centers lived memory but exposes witness early
- B) `cover-up-trace` — Trace the institutional cover-up that produced the forged record — tradeoff: keeps institutional history central but delays lived-memory witness

**Accepted sources for this horizon:** `series_direction.yaml`, `book_1_direction.yaml`, `book_1_realization.yaml` (and derived Canonical State above).

---

## Probe P02 — Book 3 opening

**Narrative horizon:** Accepted history through Book 2.

**Accepted story history (plain facts, adds to P01):**
- Book 2 Direction: `The Council's Retraction` — want *Identify falsifier and force council to answer*; etc.
- Book 2 Realization: evidence identifies the person who falsified the record; the council publicly admitted the archive record was falsified; later the council retracted its admission.

**Fact list for this horizon:** founding record forged; monastery testimony preserved; lantern broken; falsifier named; council admitted fraud; council retracted admission.

**Current state:** `council.archive_position = retracted admission`; `archive.falsifier = named`; `archive.founding_record = forged`.

**Current planning intent (Book 3):** *Respond to the council's accepted retraction.*

**Exact creative question:**
> How should Book 3 respond to the council's retraction while preserving the witness's authority?

**Bounded options:**
- A) `publish-witness-account` — Give the witness an independent public record that the council cannot retract — tradeoff: protects authority but exposes witness to retaliation
- B) `force-council-hearing` — Use the named falsifier to compel council to answer in public — tradeoff: keeps accountability central but council controls forum/timing

---

## Probe P03 — Book 4 opening

**Narrative horizon:** Accepted history through Book 3.

**Accepted story history (plain facts, adds to P02):**
- Book 3 Direction: `The Protected Archive` — want *Protect archive after council retracts admission*.
- Book 3 Realization: a treaty protects the archive as the only evidentiary chain; the archive lantern was repaired.

**Fact list:** all P02 facts plus: archive protected by treaty; lantern repaired.

**Current state:** `archive.protection = treaty protected`; `council.archive_position = retracted admission` (now history supporting treaty); `monastery.testimony = preserved`; `archive.founding_record = forged`.

**Current planning intent (Book 4):** *Return to the monastery testimony without breaking the protected archive.*

**Exact creative question:**
> How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?

**Bounded options:**
- A) `publish-verified-testimony` — Authenticate and publish the testimony while the protected archive keeps the original evidence secure — tradeoff: preserves chain but delays release until verification complete
- B) `stage-protected-hearing` — Present the testimony beside selected archive evidence under the treaty's protections — tradeoff: immediate public pressure but reveals which records carry strongest evidence

---

## Probe P04 — Book 4 opening, adversarial option

**Narrative horizon:** Identical to P03 (accepted history through Book 3, same current state `archive.protection = treaty protected`, same monastery testimony fact, same Book 4 planning intent).

**Accepted story history / Current state:** Same as P03.

**Current planning intent (Book 4):** *Return to the monastery testimony without breaking the protected archive.* (same as P03)

**Exact creative question:**
> How should Book 4 bring the monastery testimony back into public memory without losing the archive's evidentiary chain?

**Bounded options:**
- A) `burn-archive` — Destroy the archive so the monastery testimony becomes the only surviving public account — tradeoff: makes testimony unavoidable but archive no longer exists as evidence
- B) `publish-verified-testimony` — Authenticate and publish the testimony while preserving the protected archive — tradeoff: preserves evidentiary chain but delays release until verification complete

---

## Probe P05 — Book 4 opening, paired probe

**Narrative horizon:** Identical to P03/P04 (accepted history through Book 3, Book 4 opening, Book 4 planning intent).

**Accepted story history (plain facts, same as P03):** founding record forged; monastery testimony preserved; lantern broken (older); falsifier named; council admitted fraud then retracted; archive protected by treaty; lantern repaired (recent).

**Current state:** `archive.protection = treaty protected`; `council.archive_position = retracted admission` (history explaining treaty); `archive.founding_record = forged` (grouped history); `monastery.testimony = preserved`.

**Current planning intent (Book 4):** *Return to the monastery testimony without breaking the protected archive.* (same as P03)

**Exact creative question:**
> How should Book 4 bring the monastery testimony back into public memory without destroying the archive's evidentiary chain?

**Bounded options (same as P03):**
- A) `publish-verified-testimony` — Authenticate and publish while protected archive keeps original secure — tradeoff: preserves chain but delays release
- B) `stage-protected-hearing` — Present testimony beside selected archive evidence under treaty — tradeoff: immediate pressure but reveals strongest records

---

## Frozen packet summary (V2)

| probe | book opening | planning intent | available history | question | options | note |
|---|---|---|---|---|---|---|
| P01 | 2 | DIR-INT2 (Book2) | Series+Book1 | fraud→lived memory | 2 (witness vs cover-up) | independent decision |
| P02 | 3 | DIR-INT3 (Book3) | +Book2 | retraction + witness | 2 (publish vs hearing) | independent decision |
| P03 | 4 | DIR-INT4 (Book4) | +Book3 | testimony without destroying chain | 2 (publish vs protected hearing) | independent decision |
| P04 | 4 | DIR-INT4 (Book4) | +Book3 | same, burn variant | 2 (burn vs publish) | adversarial variant of P03 decision family (state-compatibility) |
| P05 | 4 | DIR-INT4 (Book4) | +Book3 | same as P03 | 2 (same as P03) | paired with P03 — projection/isolation, not independent decision |

V2: 5 probes × 3 conditions × 3 generations = **45 outputs**; 4 independent creative-decision situations (P03/P04/P05 share Book4 horizon; P03/P05 are one decision family for breadth, P04 tests same horizon with adversarial option). Hidden evaluation only in `evaluation-rubric.md`.
