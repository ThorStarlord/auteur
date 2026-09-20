# Book Acceptance Stabilization Record

**Issue:** #247  
**Classification:** execution-window / evidence observability, not a reproduced Book authority regression.

## Evidence

The latest repository-wide Stabilization run before this issue was created was
GitHub Actions run `35446934735` on
`019e7c39abe577c9a03c60d2c1d8d5be0eb000d2`.

- event: `workflow_dispatch`;
- environment: Ubuntu / Python 3.12;
- full `python -m pytest -q --tb=short`: completed successfully;
- verification stack: completed successfully;
- full-suite test step ran from approximately 13:51:36Z to 14:06:32Z on
  2026-09-19;
- Book acceptance tests were included in the full suite.

Subsequent local continuation work reported full pytest as incomplete around the
long-running Book region. Those incomplete executions are not failures under the
release-qualification policy and do not override the successful L3 evidence.

No current evidence identified a Book acceptance semantic regression that
warrants weakening the 20-point acceptance gate, changing pointer authority, or
altering Book reconciliation semantics.

## Smallest Book regression command

The repository now carries a bounded sentinel:

```bash
python -m pytest -q tests/test_book_acceptance_smoke.py --tb=short
```

It crosses the real supported path:

```text
accepted chapters
→ composed + accepted Book
→ external Book inspection
→ Book-owned proposal/publication
→ derived recomposition
→ exact comparison
→ explicit Book acceptance
→ accepted Book pointer revision
```

The smoke does not replace `tests/test_book_acceptance.py`, the full suite, or
release qualification. It exists to distinguish a Book authority regression
from repository-wide execution cost.

## Stabilization observability

The manual L3 workflow now records:

- the 25 slowest tests through pytest `--durations=25`;
- a JUnit XML artifact for every run, including incomplete/failed runs when the
  file exists.

This makes a future timeout attributable to concrete test regions instead of
being described as a generic “Book path” failure.

## Disposition rule

If the focused Book sentinel is green on the exact candidate head and no Book
failure is reproduced, #247 is reconciled as an incomplete local execution
problem. A future actual Book acceptance failure should be tracked from its
specific failing test and authority invariant rather than reopening a generic
runtime diagnosis.
