# Bounded Episode 1 Direction Qualification

Status: **qualification evidence complete**. Implementation, unit-test,
acceptance-test (including the post-documentation second acceptance pass
described below), and specialist-reviewer evidence for this bounded
capability are all gathered and passing. This is not a release-ready claim
and it is not a claim that this repository's downstream Feature Factory
orchestration gates have run: the final Validator rerun and CHECKPOINT 3 are
separate, downstream orchestration steps that this document does not assert
one way or the other. See "What this document does and does not assert"
below.

This report qualifies the bounded, Direction-only Episode 1 capability
described in
[Bounded Episode 1 Direction Capability Contract](../acceptance/series-episode-one-direction-capability-contract-v1.md)
and
[Bounded Episode 1 Direction Implementation Boundary](../design/series-episode-one-direction-implementation-boundary-v1.md),
built on top of the existing
[Series Vertical Slice V1](series-vertical-slice-qualification-v1.md).

## Candidate identity

Worktree: `experiment/ai-factory-tier3-compat`, HEAD `7e8cda9204d418041403c231bc1dcde1e8d6ecb1`
plus uncommitted feature changes from the Backend Builder, Test Verifier, and
this documentation pass. No commit has been made against this candidate as of
this record; all feature changes remain uncommitted in the worktree by design
of this build.

## Evidence gathered so far

### Backend unit tests (Backend Builder)

The Backend Builder implemented the production code under `src/auteur/series/`
(`vertical_slice_models.py`, `vertical_slice_service.py`,
`vertical_slice_store.py`, `vertical_slice_formatters.py`, `cli.py`, and a new
dedicated helper module) together with unit tests for every new and
meaningfully modified function, per this repository's Backend Builder
contract. The Backend Builder reported all of its unit tests passing before
handoff.

### Acceptance tests (Test Verifier, first pass)

The Test Verifier authored one acceptance test per acceptance criterion
(AC1 through AC19) plus edge-case coverage, and extended the existing
end-to-end Series journey test with an episodic journey. The Acceptance
command for this feature is:

```text
PYTHONPATH=src python -m pytest -q --tb=short tests/test_series_episode_one_direction.py tests/test_series_vertical_slice_e2e.py
```

This command was run and reported **34 passed, 0 failed**. The result was
independently re-executed once more outside the Test Verifier's own run, and
the rerun reproduced the same result: **34 passed, 0 failed**. All AC1–AC19
are mapped to a named test and all mapped tests pass.

### Security review

The Security Reviewer's final report recorded no Critical, Important, or
Minor findings. Verdict: no security issues found.

### Performance review

The Performance Reviewer's final report recorded no Critical or Important
findings. One Minor was recorded:

- `src/auteur/series/vertical_slice_models.py:120-133` — duplicate-commitment
  detection uses a `.count()` call inside a comprehension, which is O(n²),
  where a sibling O(n) `seen`/`duplicates`-set pattern already exists
  elsewhere in the same file. The reviewer judged this explicitly
  non-blocking: the input list is small and human-authored (an author is
  selecting a handful of commitment references, not thousands), so the
  quadratic behavior has no observable effect in practice. This qualification
  record treats it as a recorded, non-blocking observation, not a defect
  requiring correction before this feature can ship. No code change was made
  as a result of it.

### Validator review (pre-documentation)

The Validator's pre-documentation final report recorded no Critical or
Important findings, and two Minor observations:

1. `src/auteur/series/vertical_slice_service.py:364` — a bare
   `assert episode_meta is not None` guarding a genuine invariant. Under
   `python -O`, Python strips `assert` statements, which would turn this from
   a guaranteed-invariant check into an unguarded exception path (a
   `NoneType` attribute error further down) if the invariant were ever
   violated. The Validator recorded this as a Minor because the invariant is
   in practice guaranteed by the loader contract it follows, but flagged the
   `assert`-under-`-O` fragility for future attention. This qualification
   record carries the observation forward; no code change was made under this
   documentation pass, since Doc Writer is scoped to `docs/**` and
   `CHANGELOG.md` only and cannot touch `src/auteur/**`.
2. New public service methods (`declare_series_episodic`,
   `propose_episode_direction`, `accept_episode_direction`,
   `inspect_episode_direction`, and their store-level counterparts) lack
   docstrings. The Validator confirmed this matches the pre-existing sibling
   Book Direction convention in the same modules (`propose_book_direction`,
   `accept_book_direction`, and related store methods are also undocumented)
   — it is a systemic, pre-existing repository convention, not a regression
   introduced by this feature. Recorded here as a known, non-blocking,
   pre-existing pattern.

The Validator additionally confirmed, for this pre-documentation candidate:

- all of AC1 through AC19 have both implementation evidence and a passing
  acceptance test;
- no out-of-scope item (Episode 2+, Episode realization, canonical state,
  a generalized Episode scope, a `SeriesDirection` schema change, an
  HTTP/frontend surface, or a new runtime dependency) was implemented;
- the technical brief's file-change map was followed exactly.

### Acceptance tests (Test Verifier, second pass — post-documentation, final)

A second Test Verifier pass re-ran the exact same Acceptance command quoted
above against the documentation-complete candidate — that is, against the
repository state after this qualification record and the rest of the
documentation pass had already been written:

```text
PYTHONPATH=src python -m pytest -q --tb=short tests/test_series_episode_one_direction.py tests/test_series_vertical_slice_e2e.py
```

This run reported **34 passed in 28.62s**, exit code 0. The result was
independently re-executed once more, and the rerun reproduced the same
result: **34 passed, 0 failed**. This second pass additionally confirmed:

- all 19 `test_ac*` functions are still present by name, with no skip,
  xfail, or focus markers on any of them;
- AC19 continues to validate only the three ratified C-04 /
  narrative-architecture normative documents — it does not require, and was
  not made to require, the CHANGELOG entry, this qualification record,
  CHECKPOINT 3, or final-Validator evidence;
- the `auteur` package imported during both acceptance runs resolved to
  `H:\GithubRepositories\auteur-ai-factory-tier3-compat\src\auteur\__init__.py`,
  confirming the tests ran against this worktree's own source rather than
  some other installed copy;
- all 18 changed candidate files (11 from the Backend Builder, 4 from the
  first Test Verifier pass, and 3 from Doc Writer, including this qualification
  record itself) remained byte-identical throughout this second pass — zero
  mutation occurred as a side effect of re-verification.

Both acceptance runs in this second pass produced one benign,
Windows-specific `PermissionError` from pytest's `atexit` temp-directory
cleanup. In both cases this occurred *after* the "34 passed" summary line had
already been printed; it is an environment artifact of this platform's
temp-directory teardown, not a test failure, and it did not affect the exit
code or the reported pass count.

This second pass is the final acceptance-test evidence this record relies on:
because it ran against the documentation-complete state, there is no
remaining acceptance-test evidence that would still be "stale" relative to
the documentation in this repository.

## What this bounded capability adds

For a Series the author has explicitly declared episodic:

- an author can propose and then explicitly accept an Episode 1 Direction
  that references one or more commitments from the currently accepted Series
  Direction;
- proposing an Episode 1 Direction creates no authority; only explicit
  acceptance does;
- re-declaring an already-episodic Series and re-accepting an
  already-accepted Episode 1 Direction proposal are both visibly idempotent,
  distinct from a first declaration or first acceptance;
- Book Direction work and Episode Direction work are mutually exclusive per
  Series, enforced in both directions;
- a read-only inspection view distinguishes Series-level authority from
  Episode-level authority and never presents Episode 1 as "Book 1";
- duplicate Series-commitment references in a proposed Episode 1 Direction
  are rejected outright, never silently deduplicated.

Existing Book-oriented Series and projects are unaffected: absence of the new
entry-form declaration means Book-oriented behavior, unchanged.

## What remains explicitly out of scope

Per the approved user story and the ratified capability contract: Episode 2
and beyond, Episode realization, Episode canonical state, a generalized
Episode scope or Book/Episode scope unification, any `SeriesDirection` schema
change, and any HTTP or frontend surface. None of these were implemented, and
this record does not claim otherwise.

## What this document does and does not assert

This record distinguishes two separate things, and asserts one of them while
explicitly declining to assert the other:

1. **Qualification evidence** — implementation, unit tests, the full
   acceptance-test suite (including the second, post-documentation pass
   described above, which ran against the documentation-complete candidate
   and closes AC19 against the final documentation state), and all three
   specialist reviewer reports (security, performance, and the
   pre-documentation Validator review). This record asserts that this
   evidence is complete and passing, and that assertion does not depend on
   the outcome of any orchestration step that has not yet occurred.
2. **Feature Factory completion** — this repository's own downstream
   orchestration gates, specifically a final Validator rerun and CHECKPOINT 3.
   These are separate, downstream orchestration steps that this document does
   not assert have occurred, have not occurred, or will produce any
   particular outcome. Readers who need to know whether this candidate has
   been merged, released, or has passed CHECKPOINT 3 should consult those
   gates directly rather than inferring an answer from this record.

## Non-claims

This record does not claim: a release or publish event; a merge into any
other branch; a version bump (none occurred and none is required by the
technical brief); that the minor Performance or Validator observations above
have been fixed (they have not — they were judged non-blocking by their
respective reviewers and are recorded here, not resolved here); or that the
Feature Factory's final Validator rerun and CHECKPOINT 3 have occurred. Those
two are downstream orchestration gates not asserted by this qualification
record, in either direction.
