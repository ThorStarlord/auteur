# Rejected-Outcome Representation Verification

## Repository

Baseline SHA: `49bf508a5b5ad5fdc05da7fba20850a7665db79c`
Branch: `feat/rejected-outcome-representation`
Implementation SHA: `86a268f`
Working tree before hygiene: implementation committed; approved specification and generated qualification logs/XML were uncommitted. Final working tree is clean after committing the specification and report.

Environment: `C:\Python314\python.exe`, Python 3.14.3, pytest 9.0.3, xdist installed. With `PYTHONPATH=H:\GithubRepositories\auteur\src`, `auteur` imports from the checkout. Without it, `auteur` resolved to a temporary audit clone and collection failed before tests; this is a stale installation/import-path issue.

## Representation

New field: `AuthorAudienceContract.rejected_outcomes`
Field type: `list[str]`
Default: `default_factory=list`
Forbidden-trope meaning: author-authored forbidden narrative mechanisms or conventions.
Rejected-outcome meaning: terminal states rejected by an accepted profile resolution contract.
Dual-write: none for new profile compilations.
Compilation destination: `author_audience_contract.rejected_outcomes`.

## Provenance and diagnostics

New destination path: `rejected_outcomes: <value>` in `ProfileDerivation.obligations_applied`.
Legacy fallback: only explicit legacy `forbidden_tropes: <value>` provenance is evaluated.
Fallback mutation: none; the Blueprint remains in its legacy shape.
Fallback deduplication: D-RES-002 tracks reported outcome values and emits once.
Override identity: existing stable profile obligation identity is preserved.
D-RES-002 source: dedicated field for new artifacts; explicit provenance fallback for legacy artifacts.
D-RES-002 ID preserved: yes.
Affected path: evidence reports `rejected_outcomes`.
Posture severity: unchanged and still centralized in `profile_severity.py`.
Human/JSON parity: covered by existing profile visibility tests.
D-RES-001 changes: none.
D-RES-003 changes: none.

## Compatibility

Legacy without provenance loads unchanged and does not trigger D-RES-002 from `forbidden_tropes` alone. Legacy with proven provenance loads unchanged and can trigger the diagnostic. No speculative migration occurs. New empty and populated fields serialize through existing Pydantic/YAML/JSON paths. No-profile compilation remains free of profile derivation and profile diagnostics. Compilation remains permissive; CLI behavior and schema version are unchanged.

## Counterfactuals

Focused tests cover pure authored tropes, pure profile outcomes, no dual-write, same-field distinction, legacy fallback, no-provenance legacy data, deduplication, round trip, idempotence, no-profile behavior, and existing D-RES-001/002/003 reachability.

## Tests

Baseline collected: 3,792 (recorded at baseline SHA).
Candidate collected: 3,796.
Delta: +4 tests.
Added nodes: 4 focused representation tests.
Removed nodes: 0.
Marker changes: none; the existing 27 xfails and 1 ordinary skip remain.

Focused: 99 passed.

Serial: 3,796 total = 3,768 passed + 27 xfailed + 1 skipped + 0 xpassed + 0 failed + 0 errors. Tests reached 100%. Process exit was nonzero only because pytest cleanup raised Windows `PermissionError` for its temporary `pytest-current` link after completion.

Parallel: 3,796 total = 3,768 passed + 27 xfailed + 1 skipped + 0 xpassed + 0 failed + 0 errors. Tests reached 100%. The same post-run Windows cleanup error occurred.

Initial full unfiltered output is preserved during this recovery pass for diagnosis. Disposable raw logs/XML were removed after inspection. With unique explicit `--basetemp` roots, candidate and baseline serial/parallel commands all exited 0 and finalized JUnit successfully.

### Test-node execution

Candidate serial: 3,796 collected; 3,768 passed; 1 skipped; 27 xfailed; 0 xpassed; 0 failed; 0 errors. Exit code 0.
Candidate parallel: 3,796 collected; 3,768 passed; 1 skipped; 27 xfailed; 0 xpassed; 0 failed; 0 errors. Exit code 0.
Baseline serial: 3,792 collected; 3,764 passed; 1 skipped; 27 xfailed; 0 xpassed; 0 failed; 0 errors. Exit code 0.
Baseline parallel: 3,792 collected; 3,764 passed; 1 skipped; 27 xfailed; 0 xpassed; 0 failed; 0 errors. Exit code 0.

The earlier no-`--basetemp` runs reached 100% and finalized JUnit, then exited 1 from pytest’s Windows temp cleanup: `PermissionError: [WinError 5]` unlinking `C:\Users\Admin\AppData\Local\Temp\pytest-of-Admin\pytest-current`. The exception occurred in pytest’s `_pytest.pathlib.cleanup_numbered_dir` atexit callback, after the normal result summary; it was not repository fixture or product cleanup code. Candidate and baseline both pass with unique explicit temporary roots. Classification: **CLEAN PASS; prior cleanup failure was transient environment/tooling state**.

## Deferred work

- automatic migration tooling;
- generalized typed constraints;
- forbidden-trope diagnostic;
- CLI redesign;
- emotional-target, narrative-engine, and framing propagation;
- acknowledgment workflows;
- compilation blocking.

## Verdict

Specification implemented: PASS
Additive schema change: PASS
Legacy loading preserved: PASS
No speculative migration: PASS
New compilation avoids forbidden_tropes: PASS
No dual-write: PASS
Provenance fallback narrow: PASS
Fallback does not mutate: PASS
D-RES-002 ID preserved: PASS
D-RES-002 scope correct: PASS
Posture severity unchanged: PASS
Overrides remain targeted: PASS
Human/JSON parity preserved: PASS
D-RES-001/003 unchanged: PASS
Serial suite reconciled: PASS; pytest exit code 0 with isolated temp root.
Parallel suite reconciled: PASS; pytest exit code 0 with isolated temp root.
Ready for review: YES
