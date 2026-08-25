# Repeated Map/Focus V2 — Probe-Enabling Surface Qualification (Boundary 2)

Date: 2026-08-25

## Qualification boundary

This report qualifies the exact candidate
`092bd48f5728e7b1f2d6dfac16e40f7bf3850665` in the linked worktree
`H:/GithubRepositories/auteur/.worktrees/probe-surface`, on branch
`feat/repeated-map-focus-v2-probe-surface` based off `main` `1d92803`.

This is a **new** qualification distinct from the historical Repeated Map/Focus
V2 application-capability qualification (`2e066108db51ff4b42b41316d5ea5e8d627eef71`,
see [series-repeated-map-focus-qualification-v2.md](series-repeated-map-focus-qualification-v2.md)).
Because production CLI/service seams changed (two supported reachability/
discoverability repairs were added), the probe-enabled production surface is
qualified from this new exact SHA rather than re-qualifying or rewriting the
historical V2 evidence.

Boundary: [repeated-map-focus-v2-probe-enabling-surface-boundary.md](../design/repeated-map-focus-v2-probe-enabling-surface-boundary.md)
and the [Human Validation Contract](../product-validation/series-repeated-map-focus-v2-human-validation-contract.md).

## What is qualified

The **probe-enabled production surface** for Repeated Map/Focus V2:

1. **Accepted-fact discovery** (`series journey accepted-facts --book N [--detail]`):
   read-only listing of accepted historical facts in deterministic order with a
   user-facing selection token (`B{book}-{position}~{fingerprint}`), a
   plain-language summary, and the accepted source Book; internal artifact id,
   revision, and fact id are hidden by default and opt-in under `--detail`.
   Unaccepted/proposed facts never appear.
2. **Friendly selection → exact `AcceptedFactRef` resolution**
   (`selection_token_for`, `list_accepted_facts`,
   `resolve_accepted_fact_selection_token`): the token is a derived,
   non-authoritative presentation locator bound to the exact revisioned
   `AcceptedFactRef`; 0 matches and >1 matches fail closed (stale/invalid and
   ambiguous); the accepted-history snapshot is the only lookup source; no fuzzy
   matching, no aliases, no registry.
3. **Book-N planning-intent entry** (`plan-next-book --book N --intent ... [--relevance <token> ...]`):
   reuses `enter_repeated_book_planning` semantics; workflow state only,
   non-authoritative, not accepted Book-N Direction, does not change Canonical
   State. Frozen invariant: `--relevance` without `--intent` fails with no
   persistence; no args preserves the legacy `enter_book_planning` path.
4. **Book 2/3/4 journey-level reachability**: Books 3 and 4 exercise the
   repeated Map/Focus CLI route end-to-end (discovery → intent entry → Map →
   Focus), including the Book-4 dorman-fact reactivation of the accepted
   monastery testimony through the supported surface with unchanged V2
   provenance semantics.

The qualified V2 application capability is not redesigned. This surface only
removes the two demonstrated reachability/discoverability gaps so the Human
Validation Contract can exercise the real product surface fairly.

## Book-2 Map routing note

`journey map --book 2` intentionally remains the pre-existing V1 route. Boundary
2 does not re-route it (that would be a third surface behavior change not in
scope). Book 2 therefore proves the two new CLI affordances through
`main(...)`, while the R1 repeated-activation semantics are asserted through the
already-qualified `derive_repeated_book_context(2)` service seam; a regression
test proves the legacy Book-2 Map renders unchanged V1 context. See the
implementation plan section 5a for the bounded surface asymmetry note and its
possible later human-probe presentation implication.

## Focused and relevant regression qualification

The new Boundary-2 tests, the existing Repeated Map/Focus suite, and the
relevant V1 regressions all pass:

```text
tests/test_series_repeated_map_focus.py        69 passed  (54 V2 + 15 Boundary-2)
tests/test_series_vertical_slice_service.py
tests/test_series_vertical_slice_models.py
tests/test_series_vertical_slice_cli.py
tests/test_series_vertical_slice_e2e.py         114 passed
tests/test_provenance_pilot.py
tests/test_story_state_commands.py
tests/test_story_state_manager.py                44 passed
```

`scripts/check.py --skip-pytest` (validators, repo checks, `validate-repo.py`,
`verify_vendored_contract.py`, `ruff check src tests`) passes; the only warnings
are the known non-critical pre-existing workflow registration warnings unrelated
to the series surface.

## Complete source qualification

`scripts/release_evidence.py` produced
`docs/qualification-evidence/092bd48f5728e7b1f2d6dfac16e40f7bf3850665.json`
from the exact candidate:

| Collected | Passed | Skipped | Xfailed | Xpassed | Failed | Errors | Reconciles |
|---:|---:|---:|---:|---:|---:|---:|---|
| 4,492 | 4,464 | 1 | 27 | 0 | 0 | 0 | yes |

Zero failure nodes. This is source-qualified for the bounded probe-enabled
surface behavior described here.

## Installed artifact qualification

`scripts/verify_wheel.py` built and installed a wheel from the same candidate:

- filename: `auteur-0.37.1-py3-none-any.whl`; version `0.37.1`;
- wheel file count: `394`; SHA-256:
  `e819d1eb430d3e28a4fae392e3af270edc71e66ffd1a1582d43cdb8a136125a6`;
- all 11 installed checks passed: import/version from site-packages, pack list,
  pack inspect, recommendation, recommendation durability, zero pre-acceptance
  mutation, explicit acceptance mutation, restart persistence, pack version/hash,
  genre validation, genre diagnosis.

This is artifact-qualified for the same bounded surface. It is not release-ready:
publication, release finalization, and authorization remain separate decisions.

## Exact claims

> Repeated Map/Focus V2 probe-enabled production surface is implemented,
> source-qualified, and artifact-qualified for accepted-fact discovery and
> Book-N planning-intent entry through the supported CLI.

No claim of human usability validation is made. No participant evidence was
collected.

## Explicit non-claims and boundary

The qualified V2 application capability semantics (`select_repeated_continuity`,
`validate_repeated_proposal`, `derive_repeated_book_context`) are unchanged.
This qualification does not claim: a general history browser; full-text/semantic/
fuzzy search; relevance ranking; a universal fact registry or second identity
scheme; new Domain Model entities for the CLI; finite/uncertain Series extent;
recommendation-content generation; free-form Book-N Direction; intra-Book
Map/Focus; browser/TUI/editor redesign; universal lifecycle/dependency/
recommendation machinery; or re-routing Book-2 Map to the repeated surface.

## Remaining evidence boundary

A real participant is still required to determine whether a creative beginner
can understand and use the bounded journey through this qualified surface. The
Human Validation Contract cannot start until the probe kit is rendered from this
qualified surface. Human evidence is also required for whether the Book-2 V1
presentation split and the repeated Book-3/4 presentation remain coherent
together (see the implementation plan's bounded surface asymmetry note).
