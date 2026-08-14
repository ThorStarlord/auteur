# M2 Design Falsification Pass — Structural Participation

> Cycle: `discovery/structural-participation` (design @ af322b1, reopened per human
> correction 2026-08-14). Zero production code. Verdict of this pass, recorded
> solution-free.

## Issue 1 — Enactment must not re-author the accepted result

**Finding:** the derivation chain is *in principle* present but *not deterministically
closed* for the supported slice:

```
chosen [signe_marriage] → alternative_bindings[signe_marriage].references[].entity_ref
  → decision.structural_anchors[id=signe_marriage] → promoted referent signe_marriage
```

In the demonstrated case, `chosen` + `combination_direction` + provenance **can** derive
participation without the author restating `--participating no`. BUT the shared-carrier
and multi-carrier controls break this: a chosen alternative may concern several anchors
(multi-carrier), or one carrier may realize several referents (shared carrier). In those
cases, deriving "which referent gets which participation value" from the accepted decision
is **underdetermined** — the mapping requires exactly the footprint information the design
has refused to add.

**Verdict on issue 1:** a *single-referent-per-choice* slice could derive participation
deterministically and fail closed on ambiguity, but that slice silently assumes a
one-to-one chosen→referent mapping — precisely the assumption the controls forbid. The
"derive, don't re-author" correction is sound in spirit; it cannot be made sound in
general without footprint.

## Issue 2 — The diagnostic is an echo, not meaningful structural reasoning

**Finding (decisive):** `analyze_structure` produces every structural conclusion from:
- `thread_count` vs `subplot_budget` (counts, not membership),
- per-thread `supports_main_by` / `thematic_function` checks (by thread, not by referent),
- character obligations (by character),
- theme/scope/genre/medium/profile rules (none consume referents).

Grep confirms `analyze_structure` has **zero** `structural_referents` references. For
`participation=false` on `signe_marriage` to change any of these meaningfully, the
analyzer would need to know **which thread(s)/budget slot(s) realize `signe_marriage`** —
i.e. footprint. Without it:

- it cannot decrement `thread_count` (referents ≠ threads; shared carriers; cutting one
  referent must not delete a shared carrier),
- it cannot skip a thread's `supports_main_by` check (no referent→thread link),
- it cannot adjust character structural obligations (referents are not traversed).

A `structural_referent.not_participating` INFO diagnostic would therefore only repeat the
field's value — "add a field, add a diagnostic that echoes it" — which is exactly the
trap the campaign set out to avoid. The product problem was *"the evolving story cannot
meaningfully reflect the decision"*; an INFO echo does not change any structural
conclusion.

## Verdict

**M2 ALONE INSUFFICIENT — FOOTPRINT NOT DEFERRABLE.**

Participation is representable, but it cannot close the demonstrated downstream problem
without knowing which canonical structures realize the referent. The human's anticipated
failure condition is confirmed: `identity → participation → footprint` is not as
operationally separable as the M2 discovery hoped. `analyze_structure` cannot make any
structurally meaningful inference from `participation=false` without footprint.

**Stop for human product selection.** No production code was written; the design is
withdrawn pending selection. Do NOT silently add footprint semantics.
