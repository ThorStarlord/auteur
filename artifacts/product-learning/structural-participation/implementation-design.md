# Implementation Design — Structural Participation (M2): per-referent canonical participation semantics

> Phase: implementation design only (no construction). Mechanism **M2 — explicit
> per-referent canonical participation**, selected by the human 2026-08-14. Discovery @
> `d061909` on `discovery/structural-participation`. Base SHA: c968a747 (origin/main, PR
> #75 merged). The evidence earned representation of a durable structural referent's
> **current participation in the story**; it did NOT earn footprint, thread restructuring,
> or a first-class subplot model.

## 0. Product intent (binding)

The product can now identify the durable thing a decision concerns (PR #75) but cannot
express whether that thing **currently participates** in the story. M2 adds the smallest
participation semantic and — critically — proves it is **end-to-end useful**, not merely
another field: an explicit author enactment changes canonical participation, and at least
one genuine downstream consumer observes it.

## 0.1 The central semantic distinction (binding)

Three separate concepts, never conflated:

1. **Identity** — the durable structural referent; survives inclusion, exclusion, and later revision.
2. **Decision operation/history** — e.g. the author chose `cut` or `keep`.
3. **Current canonical participation** — whether the referent currently participates.

Canonical participation is NOT encoded as historical `cut/kept` semantics. `cut`/`keep`
describe how a decision changed something; participation describes current state,
independent of why it got there. This matters for later revision (a referent can be
re-introduced without claiming it was "never cut").

## 1. The end-to-end contract (binding — the design's central proof)

M2 must close the demonstrated behavioral loop, not merely add schema:

```
accepted chosen outcome
→ durable referent (PR #75)
→ explicit author-controlled enactment
→ canonical participation changes
→ at least ONE genuine downstream consumer observes current participation
```

The discovery proved the trap: `structural_referents` + `carrier_refs` are read by NO
downstream consumer today (only the author_decisions CLI). A participation field that
nothing consumes would "add the missing representation while failing the demonstrated
product problem." Therefore the design REQUIRES a consumer integration.

**The smallest genuine consumer integration: `analyze_structure` gains one new
deterministic diagnostic over `structural_referents` participation** (see §3). This is the
same genuine downstream consumer used throughout the campaign (`auteur structure
diagnose` → `analyze_structure`), so the loop is behaviorally observable.

## 2. Field (binding)

On `StructuralReferent` (`blueprint.py`):

```python
class StructuralReferent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    referent_id: str
    kind: str  # validated "subplot"
    participants: list[str]
    carrier_refs: list[str]
    provenance: ReferentProvenance
    participation: bool | None = None   # NEW
```

- `participation: bool | None = None` — **None = not declared** (backward compatible:
  existing referents, and referents without an explicit statement, are treated as
  "participating by default" by the consumer). `True` = currently participating;
  `False` = currently not participating.
- Vocabulary deliberately NOT `cut/kept` or `active/inactive` — it is current
  participation, and the default (`None`) means "no declaration, status quo" so old
  Blueprints load unchanged.

## 3. Consumer integration (binding — the smallest genuine downstream consumer)

`analyze_structure` gains one new diagnostic over referent participation:

- **Rule:** `structural_referent.not_participating` — emitted for each
  `StructuralReferent` with `participation is False`.
- **Severity:** INFO (a status observation, not an error — a non-participating referent is
  a legitimate state).
- **Layer:** `REPRESENTATION` (existing enum value).
- **Message:** `Durable structural referent '<referent_id>' is currently not participating in the story.`
- **Evidence:** `referent_id`, `participation: false`.
- **No footprint semantics invented:** the diagnostic observes participation of the
  referent itself; it does NOT claim which thread/budget/carrier realizes the referent, does
  NOT delete threads, does NOT decrement `subplot_budget`. (Whether footprint is also needed
  is deferred; if a real case later shows the diagnostic is unhelpful without knowing the
  realizing structures, that is a NEW footprint question — not silently added here.)

This is the smallest end-to-end consumer: `cut signe_marriage` (accepted) → promote →
author enactment sets `participation: false` → `structure diagnose` emits the
not-participating observation. Behavior now reflects current participation.

## 4. Enactment (binding) — explicit author-controlled operation

New author-decisions subcommand:

```
decision enact <decision_id> --referent <referent_id> [--participating yes|no]
```

Semantics:
- **Explicit author action only.** No automatic application merely because `chosen`
  exists; `chosen` alone never changes participation.
- For the supported first slice, when invoked with `--participating` it sets the
  referent's participation explicitly. (Deterministic `cut→no / keep→yes` mapping from
  `chosen`+`combination_direction` is a design decision recorded for the slice; the
  explicit `--participating` flag is the smallest safe first form.)
- **Idempotent:** enacting the same value twice is a no-op.
- **Fail closed:** unknown `referent_id` rejected; referent must exist (resolved via
  `_resolve_entity_ref` on the Blueprint, no name/prose matching); `--participating`
  required (no inference of the intended value from prose).
- **Provenance:** the participation change is recorded (participating value + decision_id
  + timestamp) so later restoration remains possible without deleting/recreating the
  referent.
- **Unresolved / no `chosen`:** nothing changes (enactment is explicit; it does not read
  the decision's `chosen` automatically in this slice).

## 5. Design correctness question the human posed

> "Knowing signe_marriage does not participate doesn't help structure diagnose unless we
> also know which story structures realize it."

The design's answer: the `not_participating` diagnostic IS meaningful without footprint,
because it observes the referent's own participation — the thing the experiment showed
was inexpressible. It does not claim to alter thread-level reasoning. **However**, if
construction-time validation shows the diagnostic is unhelpful in practice without
footprint, this design's escalation clause triggers (see §8): stop and report that M2
alone is insufficient — do NOT silently add footprint semantics.

## 6. Binding invariants (from the brief)

- no automatic application merely because `chosen` exists;
- no name/prose/fuzzy/semantic/LLM inference;
- no deletion of the referent on `cut`;
- no automatic thread deletion;
- no assumption that carrier refs are one-to-one;
- no F1 significance promotion;
- no general subplot ontology;
- no footprint expansion unless separately earned;
- backward compatibility for existing Blueprints/referents (participation defaults None);
- fail closed when the accepted operation cannot be enacted safely.

## 7. Required controls (binding for qualification)

1. cut → referent remains addressable while current participation changes (identity
   preserved; `not_participating` observed).
2. keep → participation True, no redundant manufactured state.
3. unresolved decision → no participation change.
4. missing `chosen` → no application.
5. repeated/idempotent enactment → no double-apply, byte-identical second run.
6. shared carrier → cutting one referent does NOT delete or touch the shared carrier
   thread.
7. multiple carriers → no one-to-one assumption (carriers untouched).
8. no carrier → fail closed or participation-only (no inference).
9. F1 significance stays decision-local (not promoted to participation or canon).
10. old Blueprint with no participation declaration → loads unchanged; consumer treats
    None as participating (no new diagnostic).
11. future restoration remains representationally possible (referent + provenance
    retained; setting participation back True works).

## 8. Escalation gates (stop before construction if hit)

Escalate to the human if coherent M2 requires: richer footprint semantics; destructive
thread restructuring; dual application/canonical truth; automatic application on
acceptance; or a substantially richer subplot lifecycle model. In particular, if the
consumer integration proves that participation cannot be meaningfully observed without
footprint, **stop and report M2 alone is insufficient** rather than silently adding
footprint.

**Assessment:** this design satisfies M2 with a minimal `participation: bool | None`
field, one deterministic consumer diagnostic (no footprint), and an explicit
author-controlled `decision enact`. **No escalation gate is hit** — but the end-to-end
consumer proof is the acceptance bar, and a construction-time failure of that proof is an
explicit stop-and-escalate condition.

## 9. Verification plan (for construction, deferred)

- TDD: controls 1–11 first (RED), then schema + `decision enact` + the one consumer
  diagnostic + goldens (new `not_participating` diagnostic only when participation False).
- Full verification stack on the merge path: pytest (categories), ruff, `scripts/check.py`.
- Independent review; autonomous merge per the envelope when scope matches, CI passes,
  review clean, exact head merged.

## 10. Stop point

This is **design only**. Construction is deferred pending the human's go-ahead. The
end-to-end consumer proof (§3) is the design's central claim and the first thing
construction must validate.
