# Beginner Workspace human-friction correction implementation plan

## Verification strategy

Use vertical TDD slices. Each behavior gets one focused failing test, the
smallest implementation that makes it pass, then a focused regression run.
Use L1 tests by default and one named L2 boundary run after the browser/API
journey is complete. Do not run release qualification or merge the branch.

## Sequence

1. Reconcile and record the previous candidate's human-gate result.
2. Add option-impact and human-readable evidence contract tests, then extend
   the Mystery adapter and projection with derived deterministic data.
3. Add authority regression tests proving valid non-recommended options are
   nonblocking while genuine contradictions still block; make the smallest
   application classification change.
4. Add projection/API action-availability tests, then expose the existing
   review, acknowledgement, acceptance, and revision commands through the
   browser client.
5. Add a server-surface integration test that completes Discover, Identity,
   and Structure through HTTP commands and verifies canonical references.
6. Add or preserve revision-flow coverage for at-risk preview, cancellation,
   and accepted downstream staleness.
7. Run changed-path lint and named L1/L2 tests; record the exact new SHA.
8. Update the qualification record with automated evidence and keep human
   usability explicitly pending for a new walkthrough.

## Test behaviors

- Each Discover story-experience option has distinct audience, framing,
  tropes, structure, and trade-off metadata.
- Choosing an option changes the Decision Card impact before Continue.
- Beginner evidence is readable, deduplicated, role-distinct, and retains
  exact technical provenance.
- A valid alternative to the recommendation does not block acceptance merely
  because it diverges from advice.
- Genuine contradiction still blocks milestone acceptance.
- HTTP/browser commands can open review and accept each milestone in order.
- Revision actions remain isolated, show at-risk impact, and preserve canon on
  cancellation.

## Exit state

The package is implemented and automated evidence passes, but the new browser
candidate remains human-usability pending. No release or merge claim is made.
