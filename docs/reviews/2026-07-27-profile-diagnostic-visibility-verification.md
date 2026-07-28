# Profile Diagnostic Visibility Verification

Date: 2026-07-27

Qualification reference SHA (current HEAD): `de0ec3de397e8bc81f837c5bfdb3603e504c6b98`.

## Previous public behavior

`analyze_structure()` already produced D-RES-001, D-RES-002, and D-RES-003, but
`genre diagnose` called `run_genre_diagnostics(identity)` without loading a
blueprint. Consequently the canonical profile diagnostics were not reachable
through that public workflow. The previous D-RES-003 map also treated
`transformative_resolution` as compatible only with hopeful and bittersweet
endings, producing a false positive for tragic mode.

## Implemented composition

The workflow is now:

```text
genre diagnose -> canonical structural analysis -> pack-specific diagnostics
```

The CLI locates the project blueprint and passes it to
`run_genre_diagnostics()`. The canonical analyzer remains the only source of
D-RES-001/002/003. Diagnostics are ordered by analysis order and then pack
order; duplicate rule IDs are suppressed, keeping the first diagnostic.
Human and JSON output serialize the same diagnostic objects, including rule,
severity, message, and evidence.

## D-RES-003 compatibility policy

The policy uses a narrow deterministic blocklist-compatible map. Contextual
patterns (`transformative_resolution` and `relational_fulfillment`) accept all
current ending tones, avoiding unsupported semantic inference. Restricted
patterns retain only their documented compatible tones. Therefore tragic,
hopeful, and bittersweet `transformative_resolution` endings do not emit
D-RES-003, while a contradictory `dark_transgression_resolution` plus
bittersweet ending does.

## Scope preserved

No rejected_outcomes schema field, adherence-posture modulation, emotional or
narrative-engine propagation, framing propagation, package-version change, or
release publication was added.

## Evidence

Focused command:

```text
pytest -q tests/test_profile_diagnostic_visibility.py \
  tests/test_profile_propagation.py tests/test_genre_diagnostics.py \
  tests/test_cli_genre_packs.py
```

Result: collected 56, passed 56, skipped 0, xfailed 0, xpassed 0, failed 0,
errors 0.

Disposable scenarios A-G were run. A clean profile and no-profile project had
no profile diagnostics; B exposed D-RES-001; C exposed D-RES-002; D exposed
D-RES-003 for a real contradiction; tragic transformative resolution did not
produce D-RES-003; and the required-outcome override suppressed its diagnostic.

Human/JSON parity and duplicate suppression are covered by the focused public
CLI tests. Existing erotic-fiction pack diagnostics remain covered and pass.

The full serial suite was attempted but is not reconciled: the default
invocation failed collection in three modules because `tests` was not an
importable package (`ModuleNotFoundError: No module named 'tests'`). A
`python -m pytest` attempt exceeded the 120-second command window without a
completed summary. The parallel suite was also attempted with four workers
and exceeded the 180-second command window without a completed summary.
These are incomplete evidence, not passing results.

## Deferred work

Dedicated `rejected_outcomes` schema work and adherence-posture severity
modulation remain deferred as requested.

## Qualification recovery addendum

Candidate qualification was repeated from branch `main`, HEAD
`de0ec3de397e8bc81f837c5bfdb3603e504c6b98`, using the existing working tree.

Environment: Python `C:\Python314\python.exe`, Python 3.14.3, pytest 9.0.3,
pytest-cov 7.1.0, pytest-xdist 3.8.0, importing
`H:\GithubRepositories\auteur\src\auteur\__init__.py`. Active pytest plugins
were xdist and pytest-cov. The suite was run with
`PYTHONPATH=H:\GithubRepositories\auteur\src` to pin the repository import.

Both requested candidate collection commands passed with 3774 tests:

```text
python -m pytest tests --collect-only -q -n 0
python -m pytest tests --collect-only -q -n auto
```

The detached baseline worktree at `H:\GithubRepositories\auteur-qualification-baseline`
(`de0ec3d`) passed both collection commands with 3756 tests. The 18-test
delta is the visibility regression suite. The earlier collection failure was
an invocation/import-path issue: an unrelated temporary editable clone won
import resolution when the explicit `tests` path and source pin were absent.

The first candidate full run also found three compatibility regressions from
unconditionally invoking canonical analysis on lightweight `DummyBlueprint`
objects. A minimal guard restored the existing pack-specific path; the
affected tests pass, and no product diagnostic behavior was changed.

Final candidate serial and parallel runs both completed at 100% with exit
code 0. Logs: `qualification-candidate-serial-final.log` and
`qualification-candidate-parallel-categories.log`.

```text
collected 3774
passed    3746
skipped     1
xfailed    27
xpassed     0
failed      0
errors      0
sum       3774
```

The serial and parallel arithmetic reconciles. Pytest emitted only a
non-fatal Windows temporary-directory cleanup warning after each run.

Collection issue understood: PASS

Candidate regression introduced: NO — compatibility regression corrected

Serial suite completed: PASS

Parallel suite completed: PASS

Results reconciled: PASS

Ready for review: YES

## Historical initial verdict (superseded by the recovery addendum)

Diagnostic reachability fixed: PASS

D-RES-003 false positive fixed: PASS

Pack-specific diagnostics preserved: PASS

Human/JSON parity preserved: PASS

No duplicate diagnostics: PASS

No-profile behavior preserved: PASS

Full serial suite reconciled: NO — incomplete/environment-blocked

Full parallel suite reconciled: NO — incomplete/timeout

Ready for review: NO — full-suite qualification remains incomplete
