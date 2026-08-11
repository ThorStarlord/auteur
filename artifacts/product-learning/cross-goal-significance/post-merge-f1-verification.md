# Post-Merge Verification - F1 decision-scoped goal significance on shipped main (PR #68)

> Recorded 2026-08-11 after PR #68 merged (merge commit a21bb43 on origin/main; exact
> PR head e881e52, F1 echo-only goal significance). Product-learning follow-up per the
> post-merge directive: re-run the F1 controls against shipped main and confirm the
> narrow claim (DECISION_CONTEXT_IMPROVED, recorded @ 2dcf073) is delivered by the
> shipped surface. Runs used the repo .venv with the merged main source (HEAD
> 4b834c7), source-qualified at the PR head before merge (4140 passed / 1 skipped /
> 27 xfailed; ruff + check.py green).

## The gap (from the S1 residual, evidence @ bef260c / discovery @ 84dbb38)

After PR #67 the product composes the one_of tradeoff deterministically but is
significance-agnostic: four controls differing only in authored significance prose
produced byte-identical reports. The product could neither receive nor surface the
author's decision-local significance. F1 adds one optional, decision-scoped
goal_significance declaration (closed shape {ordered: [ref, ref]} | {unranked: true}),
surfaced as a provenance-labeled observation - echo only, never used to rank, score,
reorder, or filter.

## Controls on merged main

All runs: case-goal-significance fixtures (Salt of the Earth frozen story; Marta's
pregnancy sustains ending tone + pressures POV contract; Signe's marriage mirrors).

| Control | observations | significance observation | invariant |
|---|---|---|---|
| ordered-ab.yaml (ending tone > POV) | 8 | authored goal significance (this decision): blueprint.contract.mandatory_ending_tone > blueprint.identity.pov_type | byte-identical-without-obs == absent OK |
| ordered-ba.yaml (POV > ending tone) | 8 | ... blueprint.identity.pov_type > blueprint.contract.mandatory_ending_tone | byte-identical OK |
| unranked.yaml (intentional non-precedence) | 8 | ... unranked - no goal has authored precedence; non-ranking is intentional | byte-identical OK |
| absent.yaml (status quo) | 7 | none | - OK |

- Deterministic consequence content is byte-identical with and without the field in
  every control - F1 adds only the provenance-labeled observation.
- Schema fail-closed verified at the PR head (26 F1 tests): both-shapes, unranked: false,
  1 or 3+ refs, duplicates, non-explicit-root refs, unrelated/stale refs, numeric weights,
  unknown fields all rejected; prose is never parsed.
- Existing goldens (case-d, case-e, case-one-of) unchanged.

## Post-merge test evidence

    tests\test_author_decisions_goal_significance.py + anchors + consequences + bindings + core:
    126 passed in 30.21s  (merged main, repo .venv)

## Claim check

The shipped surface delivers the recorded narrow claim: authored decision-local
significance is received and surfaced legibly beside the composed consequences with
provenance; nothing ranks, scores, or applies the ordering. DECISION_CONTEXT_IMPROVED
holds; DECISION_RESOLVED_BY_PRODUCT remains false by construction (echo-only).
The "I don't know" unsettled-author case stays outside F1 (deferred to F3).
