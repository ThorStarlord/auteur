# ADR 021: Post-Draft Review and Chapter Continuation Boundary

**Status:** Accepted  
**Date:** 2026-09-20

## Decision

The Beginner post-draft surface is a derived orchestration layer over the
existing chapter lifecycle. `draft_vN.md` is a candidate Expression,
`validation_vN.json` is review evidence, and `final.md` remains the accepted
chapter authority.

The Beginner layer may project review state, create noncanonical revision
handoffs, and derive Chapter N -> N+1 planning context. It does not directly
write `final.md`, update `bible.json`, rewrite prose, or silently repair
Structure.

Explicit chapter acceptance delegates to the existing chapter acceptance owner.
A durable Beginner receipt makes retry safe: if the owning workflow completed
before a process interruption, the Beginner layer reconciles the matching
accepted artifact instead of replaying authority.

The current Beginner Workspace contracts remain authoritative for the
premise-to-foundation journey. Post-draft continuation is additive and must not
replace the existing `ContinuationState`, `ChapterPlan`, `ScenePlan`, or
`DraftHandoff` contracts used by the accepted-foundation-to-first-draft flow.

## Beginner creative-divergence reconciliation

The Beginner post-draft surface must not reduce every mismatch between prose
and planning to "revise until valid." Writing may legitimately discover story
material that the planning model did not know yet.

When review detects additive discovery, plan divergence, or a hard canon
contradiction, the primary human-facing workflow is **Reconcile New Elements**.

The normal choice set is:

1. **Keep draft & update story** — preserve the prose candidate and create
   noncanonical reconciliation proposals for the lowest appropriate owning
   layer or realized state.
2. **Keep as intentional divergence** — preserve/accept the Expression through
   an explicit divergence acknowledgement without silently rewriting its
   upstream plan.
3. **Revise to match plan** — preserve current authority and route to the
   existing noncanonical revision/retry path.

The Beginner layer may orchestrate these choices, but it still does not own
Identity, Structure, Realization, Bible, or Chapter acceptance. Proposals are
evidence/request objects until the target owner explicitly accepts them.

Additive discoveries should not be promoted to higher layers unnecessarily.
For example, an unplanned side character or location introduced in Chapter 1
does not by itself reopen Story Identity.

Validation findings must be bound to the exact candidate content they reviewed.
If prose bytes change after validation, the old review becomes stale and the
Beginner surface must not present it as current.

## Invariants

- Projection performs no provider calls and no canonical mutation.
- A newer draft is reviewed against validation evidence bound to that exact candidate content; version-number matching alone is insufficient.
- Upstream fingerprint mismatch is surfaced as stale.
- Missing or malformed review evidence remains explicit.
- Revision and reconciliation handoffs are `canonical: false` until their owning authority explicitly accepts a change.
- Acceptance uses the existing chapter owner and records a durable replay receipt.
- Accepted prior chapter state may inform later planning but does not rewrite prior Structure.
- Structure-versus-Expression divergence is reported and classified rather than repaired silently.
- Unexpected prose is treated as discovery evidence before it is treated as a validation error.
- Deliberate divergence remains an explicit author choice and must be visible in the Beginner surface.
- Chapter-owned scene projections retain their chapter index.
