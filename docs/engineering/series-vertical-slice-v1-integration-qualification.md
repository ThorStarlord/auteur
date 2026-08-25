# Series Vertical Slice V1 — Remote-Main Integration Qualification

**Date:** 2026-08-25
**Qualified by:** Antigravity integration agent

---

## Candidate identification

| Field | Value |
|---|---|
| Integration candidate SHA | `4ef666697f24933706682ad62491265bcd99f644` |
| Candidate type | Merge commit |
| Parent 1 (remote main) | `ffa22bf9eef66e9f99f2d44e9ec166cc9040e7ad` |
| Parent 2 (Series V1 tip) | `ee3ed741871ede0d06e74e361bdc8339c32ca419` |
| Integration branch | `publish/series-vertical-slice-v1-integration` |
| Worktree path | `H:/GithubRepositories/auteur-publish-series-v1-integration` |

## Historical qualification reference

This qualification is **distinct from and does not replace** the historical standalone qualification:

```
Historical candidate:   e523676 (fix: scope acceptance timestamps to vertical slice artifacts)
Historical evidence:    ee3ed74 (docs: record series vertical slice qualification)
Historical claim:       Series Vertical Slice V1 passes in isolation from base `5d3dcbf`
```

The new claim is narrowly:

> **Series Vertical Slice V1 is integration-qualified against current remote Story Discovery main (`ffa22bf`).**

---

## Merge analysis

### Conflicts

**Zero textual conflicts.** Git's automatic three-way merge completed without conflict on all files.

### Files changed in merge (net diff against `origin/main @ ffa22bf`)

| File | Change |
|---|---|
| `docs/engineering/series-vertical-slice-qualification-v1.md` | New (qualification record) |
| `docs/superpowers/plans/2026-08-23-series-vertical-slice-v1.md` | New (implementation plan) |
| `src/auteur/provenance/store.py` | Modified (+7 lines) |
| `src/auteur/series/cli.py` | New |
| `src/auteur/series/vertical_slice_formatters.py` | New |
| `src/auteur/series/vertical_slice_models.py` | New |
| `src/auteur/series/vertical_slice_service.py` | New |
| `src/auteur/series/vertical_slice_store.py` | New |
| `tests/fixtures/archive_of_lies_vertical_slice/` | New (5 fixture files) |
| `tests/test_provenance_pilot.py` | Modified |
| `tests/test_series_cli.py` | Modified |
| `tests/test_series_vertical_slice_cli.py` | New |
| `tests/test_series_vertical_slice_e2e.py` | New |
| `tests/test_series_vertical_slice_models.py` | New |
| `tests/test_series_vertical_slice_service.py` | New |

**19 files changed, 6431 insertions(+), 1 deletion(-)**

No Story Discovery source files were modified. No remote work was deleted or reverted.

### Semantic interaction assessment

The Series Vertical Slice operates in `src/auteur/series/` — a module namespace with no overlap with the Story Discovery modules (`story_discovery_*.py`). The one shared touchpoint is `src/auteur/provenance/store.py`, which received a 7-line additive change in Campaign 1. No shared state or CLI routes conflict.

---

## Test results

### Environment

- Python: 3.14.3
- pytest: 9.0.3
- Package: auteur 0.37.1 (editable install from integration worktree)

### Focused: Series Vertical Slice suite

```
tests/test_series_vertical_slice_models.py
tests/test_series_vertical_slice_service.py
tests/test_series_vertical_slice_cli.py
tests/test_series_vertical_slice_e2e.py
tests/test_series_cli.py
tests/test_provenance_pilot.py
```

**Result: 142 passed, 0 failed, 0 skipped (36.30s)**

### Focused: Story Discovery regression suite

```
tests/test_story_discovery.py
tests/test_story_discovery_compose.py
tests/test_workflow_story_discovery_front_door.py
```

**Result: 34 passed, 0 failed (9.42s)**

### Full source suite (`pytest -n auto`, all tests)

**Result: 4562 passed, 3 failed, 1 skipped, 27 xfailed (302.59s)**

### Failure baseline classification

All 3 failures were **confirmed as known baseline failures** by running the identical tests against
`origin/main @ ffa22bf` in a clean worktree:

| Test | Integration result | Baseline result | Classification |
|---|---|---|---|
| `test_story_discovery_recommendation_basis.py::test_qualified_comparative_non_adjudicable_is_a_valid_project_state` | FAIL | FAIL | **KNOWN BASELINE FAILURE** |
| `test_story_discovery_review.py::test_recommendation_review_reconstructs_writer_facing_evidence` | FAIL | FAIL | **KNOWN BASELINE FAILURE** |
| `test_story_discovery_review.py::test_composed_review_explains_borrows_and_preserved_primary` | FAIL | FAIL | **KNOWN BASELINE FAILURE** |

No regressions introduced by the Series Vertical Slice integration.

### Collection errors (4)

The 4 import errors (`test_adherence_posture_severity.py`, `test_author_golden_path.py`,
`test_genre_overrides.py`, `test_genre_setup_contract.py`) occur due to `from tests.X import Y`
cross-test imports that require `tests/` on `sys.path`. These are resolved by the root
`pythonpath=.` configuration and all 4 affected tests pass in the full run. Zero errors in the
`pytest -n auto` full run (which uses `pythonpath=.`).

### Ruff linter

```
ruff check src tests → All checks passed!
```

---

## Qualification claim

> Series Vertical Slice V1 (Campaign 1, commits `bef94c5`..`ee3ed74`) is integration-qualified
> against remote Story Discovery main at `ffa22bf`.
>
> The integration candidate is merge commit `4ef6666`.
>
> No regressions were introduced relative to the remote main baseline.
> All Series Vertical Slice focused tests pass.
> All Story Discovery regression tests pass.
> The full source suite passes at baseline parity.

---

## Qualification evidence ancestry

```
origin/main @ ffa22bf
        |
        +── [22 Campaign-1 commits] ──> ee3ed74 (historical qualified tip)
        |                                    |
        |           e523676 ◄── in ancestry  |
        |                                    |
        └────────────── MERGE ──────────────-+
                           |
                    4ef6666 ← THIS CANDIDATE
                           |
              [qualification record] ← this document
```
