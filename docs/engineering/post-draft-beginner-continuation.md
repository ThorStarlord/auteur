# Post-Draft Beginner Continuation — Targeted Integration Record

**Reconstruction base:** `main @ d7966dc3250970d0c5f435af162263cea93eeb78`  
**Reason for reconstruction:** historical PR #245 was 268 commits behind current
`main` and could not be merged safely. The bounded capability was rebuilt
additively on the contemporary Beginner Workspace contracts.

## Implemented boundary

- artifact-derived post-draft review projection;
- matching validation evidence and bounded plan-alignment projection;
- stale-upstream detection from draft metadata;
- noncanonical retry/editing handoff;
- explicit acceptance delegation to the existing chapter owner;
- durable acceptance receipt with crash/replay reconciliation;
- accepted chapter outcome and next-chapter context projections;
- contextual Chapter N -> N+1 planning;
- explicit Structure-vs-accepted-state divergence reporting;
- chapter-owned scene-plan projection;
- local JSON endpoints and browser actions.

## Authority boundary

The Beginner layer does not directly create `final.md` or mutate
`bible.json`. Acceptance is delegated to the existing chapter acceptance
handler. Derived planning, review, revision handoff, and browser state do not
become canon merely because they are deterministic or persisted.

## Validation intent

This package is an ordinary development integration. Its required evidence is:

1. exact-head L1 for the new/changed focused tests and repository verification;
2. named L2 coverage for review -> revision handoff -> explicit acceptance ->
   replay reconciliation -> accepted outcome/context -> Chapter N+1 planning;
3. no L3 or release-qualification claim unless separately triggered.

A missing or incomplete L3 run must be recorded as incomplete/deferred evidence,
not as a failure and not as a pass.
