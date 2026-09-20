# ADR 021: Post-Draft Review and Chapter Continuation Boundary

**Status:** Accepted  
**Date:** 2026-09-20

## Decision

The Beginner post-draft surface is a derived orchestration layer over the
existing chapter lifecycle. `draft_vN.md` is a candidate Expression,
`validation_vN.json` is review evidence, and `final.md` remains the accepted
chapter authority. The Beginner layer may create review and revision-handoff
projections, but it does not write `final.md`, update `bible.json`, rewrite
prose, or infer canonical Realization state.

Acceptance crosses the boundary through the existing acceptance owner and a
durable Beginner receipt. A retry reconciles an already matching `final.md`
instead of invoking acceptance again. Accepted chapter outcomes and next
chapter context are projections and retain source references.

## Invariants

- Projection performs no provider calls and no canonical mutation.
- A newer draft invalidates a review of an older draft by selecting only the
  latest matching validation artifact.
- An upstream fingerprint mismatch is reported as stale, never silently
  discarded.
- Missing or malformed review evidence remains explicit and does not become a
  guessed approval.
- Revision handoffs are non-canonical and route to either retry or editing.
- Next-chapter plans consume accepted prior outcomes and report disagreement
  with prior Structure without rewriting it.
