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

## Invariants

- Projection performs no provider calls and no canonical mutation.
- A newer draft is reviewed against its matching validation artifact.
- Upstream fingerprint mismatch is surfaced as stale.
- Missing or malformed review evidence remains explicit.
- Revision handoffs are `canonical: false` and route to existing retry/editing work.
- Acceptance uses the existing chapter owner and records a durable replay receipt.
- Accepted prior chapter state may inform later planning but does not rewrite prior Structure.
- Structure-versus-accepted-state divergence is reported rather than repaired silently.
- Chapter-owned scene projections retain their chapter index.
