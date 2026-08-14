# Implementation Design — Referent-Level Thematic Contribution (F3): narrow referent-local declaration

> Phase: implementation design only (no construction). Mechanism **F3 — narrow
> referent-local thematic-contribution declaration**, selected by the human 2026-08-14.
> Discovery @ `7f4f6db` on `discovery/thematic-contribution`. Base SHA: c968a747
> (origin/main, PR #75 merged). The evidence earned explicit representation of the
> thematic contribution performed by a durable structural referent; it did NOT earn a
> general contribution ontology, a replacement for StoryThread, or broader footprint.

## 0. Product requirement (binding)

The first slice must reproduce the **human-demonstrated Case-4 behavior**:

```
explicit authored contribution
→ durable referent
→ contribution becomes non-operative with the referent
→ downstream reasoning exposes the resulting thematic loss
→ without interpreting contribution prose
```

Merely adding a field and rendering it unchanged does not qualify (the M2 echo trap).
The exact composition that earned R2 is:

```
non-operative referent
+ explicit authored contribution
↓
contribution absent from operative story
```

## 0.1 Schema hygiene correction (binding — recorded per human instruction)

Verified against shipped source: **`relationship_arc` is a `ThreadType`
(`blueprint.py:239`), NOT a referent kind.** `StructuralReferent.kind` is validated to the
single value `"subplot"` (`blueprint.py:706-719`). The Case-4 test's "relationship_arc
referent" conflated the referent's canonical kind with its carrier/thread function.
**`StructuralReferent.kind` is NOT broadened as a side effect of this campaign**; the
design treats `kind: "subplot"` as authoritative.

## 1. Contribution representation (binding, smallest)

On `StructuralReferent` (`blueprint.py`, `extra="forbid"` unchanged):

```python
class StructuralReferent(BaseModel):
    referent_id: str
    kind: str = "subplot"  # validated, unchanged
    participants: list[str]
    carrier_refs: list[str]
    provenance: ReferentProvenance
    thematic_contributions: list[str] = Field(default_factory=list)  # NEW
```

- `thematic_contributions: list[str]` — **opaque author-authored text**, e.g. "supplies
  the relational counterweight that keeps the bittersweet ending emotionally credible."
  Auteur reasons deterministically about **presence/absence only**; it NEVER parses,
  interprets, or infers from the text (no theme/target/significance/nature/action
  extraction).
- Empty list = no declared contribution → **no invented loss** (control).
- Multiple contributions per referent ARE representable (list) — matching the control
  "two referents provide related contributions → excluding one does not erase the other"
  and "one referent contributing differently to multiple targets, if claimed."
- **No explicit target reference** in this slice: referent-local contribution is
  sufficient; the demonstrated value is the presence/absence of the authored
  contribution, not linking it to a specific theme node. (Design answer: target
  reference is NOT necessary for the validated slice; adding it would be F2/F4 territory.)
- **No new `nature` vocabulary, no `sustains`/`pressures` collapse, no F1 significance
  entanglement.** The nuance "pressures the ending AND supplies material that makes it
  credible" is preserved because the contribution is opaque authored text independent of
  `bears_on`/`nature`.

## 2. Operative-state mechanism (binding — investigate, do NOT revive M2 standalone)

M2 standalone participation remains **falsified**. The design must determine the smallest
explicit operative/non-operative mechanism required solely to support the validated
contribution reasoning. Three options compared:

### Option A — Derive operative state from an explicit accepted/enacted decision at reasoning time
The contribution is operative iff the referent is not the target of an accepted `cut`
decision (via `chosen`+`combination_direction`+provenance). Derivation at reasoning time;
no persisted participation field.
- **Pros:** no new canonical state; provenance is the authority.
- **Cons:** the M2 falsification showed this derivation is underdetermined under
  shared/multi-carrier (which referent gets which value). For the single-referent Case-4
  slice it is deterministic, but it reintroduces the exact ambiguity M2 flagged.

### Option B — Minimal persisted operative state coupled to the contribution slice
A single explicit author-controlled fact on the referent: e.g. `operative: bool = True`
(True = contribution active; False = contribution absent from operative story).
- Explicit author action sets it (no automatic application from `chosen`);
- default True = backward compatible (existing referents stay operative);
- **this is NOT M2-as-participation** — it is a contribution-scoped operative flag,
  deliberately NOT a general participation field, NOT connected to thread/budget/scope
  reasoning (those were the falsified M2 consumers). It exists solely to gate
  contribution presence.
- **Pros:** deterministic, idempotent, provenance-recordable, single-purpose.
- **Cons:** is it semantically distinct from M2's participation? Yes — M2 claimed
  participation should change general structural reasoning (falsified); this flag claims
  only to gate the contribution's presence (validated). The distinction is the *scope of
  what it affects*.

### Option C — Another explicit author-controlled mechanism avoiding dual truth
e.g. contribution carries its own operative marker at authoring time. Same as B with a
different home; no dual-source advantage.

**Design decision: Option B** — a minimal `operative: bool = True` on
`StructuralReferent`, contribution-scoped and explicit. Rationale: it is the smallest
deterministic mechanism; it avoids the shared/multi-carrier derivation ambiguity of
Option A; it does not claim to affect anything beyond contribution presence, so it does
not revive M2's falsified scope. `chosen` alone never enacts it — an explicit author
action (extension of `decision promote` or a new `decision set-contribution`) sets it.

## 3. Consumer: the contribution-loss finding (binding)

A new deterministic finding, NOT a change to `theme.thesis_unrepresented`:

```
structural_referent.contribution_non_operative   (INFO, layer=REPRESENTATION)
```

Emitted for each `StructuralReferent` where `operative is False` AND
`thematic_contributions` is non-empty:

> "Durable structural referent '<id>' is not operative; its authored thematic
> contribution(s) are absent from the operative story. [N] contribution(s) declared."

Evidence: `referent_id`, `operative: false`, `contribution_count`.

**Why this qualifies (not the M2 echo):** it composes TWO independently authored facts —
`operative=false` AND a declared contribution — into a NEW consequence (contribution
absent from the operative story), which the Case-4 test demonstrated changes the author's
next structural action. It is not merely restating either field.

**The design explicitly does NOT require** existing thread-level theme aggregators
(`theme.thesis_unrepresented`, motif checks) to change or parse contributions. A narrow
provenance-aware contribution-loss surface is sufficient; forcing the old aggregators
would require semantic parsing that is not needed.

## 4. Binding invariants (from the brief)

- no prose/name/fuzzy/semantic/LLM inference (contribution text is opaque; only
  presence/absence is reasoned over);
- `chosen` alone does not enact anything (operative changes require explicit author
  action);
- no automatic decision→canon application;
- no dual-source-of-truth overlay;
- no footprint semantics;
- no thread deletion (a thread remains present when a referent contribution becomes
  non-operative);
- no F1 significance promotion;
- no `sustains`/`pressures` collapse;
- no broadening of `StructuralReferent.kind`;
- backward compatible (new fields default empty/True; existing referents valid).

## 5. Required controls (binding for qualification)

1. operative referent → authored contribution remains operative (no loss finding);
2. non-operative referent → authored contribution absent (loss finding emitted);
3. no declared contribution → no invented loss;
4. two referents provide related contributions → excluding one does not erase the other;
5. referent may simultaneously `pressure` a target (via existing bears_on/nature) and
   provide a valuable thematic contribution (via new field) — both preserved;
6. declared thread remains present when referent contribution becomes non-operative;
7. F1 significance stays decision-local;
8. `chosen` alone does not enact anything (no automatic operative change);
9. existing Blueprints and referents remain backward compatible;
10. restoration remains representationally possible (setting operative back True works);
11. no prose/name/fuzzy/semantic/LLM inference.

## 6. Stop conditions (escalate if hit)

Stop for human selection if coherent F3 requires: a general contribution ontology; broad
new thematic-target semantics; first-class structural footprint; automatic
accepted-decision application; redesign of `StoryThread` thematic reasoning; or
substantial lifecycle/revision semantics.

**Assessment:** this design satisfies F3 with an opaque contribution list + a
contribution-scoped operative flag + one deterministic contribution-loss finding,
without footprint, without thread restructuring, without parsing prose, and without
reviving M2's general participation scope. **No stop condition is hit.**

## 7. Verification plan (for construction, deferred)

- TDD: controls 1–11 first (RED), then schema + explicit set-contribution/enact action +
  the one contribution-loss finding + goldens.
- Full verification stack on the merge path: pytest (categories), ruff, `scripts/check.py`.
- Independent review; autonomous merge per the envelope when scope matches, CI passes,
  review clean, exact head merged.

## 8. Stop point

This is **design only**. Construction is deferred pending the human's go-ahead. The
end-to-end Case-4 reproduction (§0, §3) is the design's central claim and the first thing
construction must validate.
