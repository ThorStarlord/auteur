# Revised protected mutation-runner repair (supersedes the first proposal in #461)

Status: prepared for the human-maintained protected route. Nothing protected was edited in the repository, and no guard was bypassed. Each part is a patch that a human applies after review.

## What the revised proposal contains

| Part | Patch | Covers | Protected? |
|---|---|---|---|
| 1 | `mutation-runner-revised-p1-runner-config.patch` (291 lines) | `harness/mutations/run.py`, `harness/harness.config.json` (two explicit reserve keys; outer bound stays 5,400) | yes (`harness/mutations/*`); config is validator configuration |
| 2 | `mutation-runner-revised-p2-runner-tests.patch` (293 lines) | `tests/test_mutation_runner_failure_paths.py` (17 focused regressions) | no (test), but it needs Part 1 |
| 3 | `mutation-runner-revised-p3-entrypoint-guard.patch` (216 lines) | `harness/ci.py` (outer rung runs through a tree-killing helper), `factory/guard.py` (validator directory protected), `tests/test_outer_rung_termination.py`, `tests/test_factory_guard_validator_paths.py` | `harness/ci.py` and `factory/guard.py` are protected by the human route |

Each patch is under the 500-line cap and applies with `git apply --check` to the candidate tree `a99609cf`. The test `tests/test_temp_hygiene_narrative_engine.py` (a separate PR, #462) is independent of these three.

## Owner decisions, item by item

1. **File descriptor leak.** `run_inner_gate` now takes the descriptor from `tempfile.mkstemp()` and closes it with `os.close(fd)` before use. Test `test_inner_output_descriptor_is_closed_on_return` removes the output file immediately after the call; a still-open descriptor would block that on Windows.
2. **Cleanup verified, not assumed.** Each mutant's temporary tree is removed by `remove_tree()`, which clears read-only entries and retries, and reports failure. A tree still present after every attempt is printed as `CLEANUP_FAILED` and fails the verdict. Tests check that the scratch directory is empty after normal completion (`test_scratch_is_removed_after_normal_completion`), after an inner timeout (`test_scratch_is_removed_after_an_inner_timeout`), and after a read-only leftover (`test_read_only_leftover_is_removed_and_the_verdict_passes`). `test_removal_failure_fails_the_verdict_and_is_reported` covers a removal that keeps failing. Targeted run: `MUTATIONS_CLEANUP_FAILURES=0`, and the dedicated temporary directory was empty afterwards (`mutation-targeted-r2`, `mutation-targeted-r3`).
3. **Bounded overall runtime; no raise without measurement.** The outer budget stays at `mutations_timeout_s = 5400`. Each mutant gets the smaller of its own bound (1,920 s: static + unit + e2e + 120 s margin) and the time remaining, minus a reserve (`mutation_overhead_s`, 120 s) for copying, cleanup and scheduling. A mutant with no time left is `INCONCLUSIVE` and is not run. The time is measured again after the copy so the copy is charged. The verdict fails whenever the budget is exhausted; it never reports a partial pass.
   - Measured so far: a static-caught mutant took 19 s; a unit-caught mutant took 695 s (`mutation-targeted-r3`). Six mutants with a pessimistic four unit-caught and two static-caught is about 2,900 s, below 5,400 s. That estimate rests on one unit measurement, so it is not yet a stable figure.
4. **Timeouts, termination failures and infrastructure errors are never caught.** Classification now:
   - `CAUGHT` only if the inner gate completed, printed a `GATE_FAILED` label that is one of the known rungs (`static`, `unit`, `e2e`, `holdout`), and no rung printed `TIMEOUT after`.
   - `INCONCLUSIVE` for: a deadline with the tree terminated and confirmed; a deadline whose termination was not confirmed (`TERMINATION NOT CONFIRMED`); a rung timeout inside the gate; an unrecognised label; a non-zero exit with no verdict; an exhausted budget.
   - Tests: `test_inner_timeout_is_inconclusive_not_a_caught_mutation`, `test_crash_without_a_gate_verdict_is_inconclusive`, `test_unrecognised_gate_label_is_inconclusive_not_caught`, `test_unconfirmed_termination_is_inconclusive_and_says_so`, `test_hanging_inner_gate_is_bounded_inconclusive_and_its_tree_is_killed`.
   - Windows `taskkill /T /F` is checked: a non-zero return code is a failure unless the root has already exited.
5. **Outer validator termination.** `harness/ci.py`'s `run()` used `subprocess.run(..., capture_output=True, timeout=...)`. Measured with the real helper before the change: a 3-second deadline returned after **12.2 seconds**, because a descendant holding the captured pipe blocked the call, and that descendant kept running and wrote its sentinel (`test_outer_run_returns_at_its_deadline...` and `test_outer_run_reclaims_descendants...`, both RED). Part 3 replaces it with file output and tree termination on timeout, and reports whether termination was confirmed. After the change both tests pass (`outer-termination-patched.log`), and the real static rung still returns its code and its output through the new helper.
6. **Protected-path enforcement.** `factory/guard.py` protected only `harness/mutations/*`. Part 3 adds `harness/*`, which covers the validator entrypoint, its configuration, E2E and process helpers, and fixtures. `fnmatch` with `*` crossing `/` matches the whole directory. The regression `test_factory_guard_validator_paths.py` is RED before the change (five entrypoint and harness paths unprotected) and GREEN after, and it confirms that `src/auteur/...` is still not protected.
7. **Six defects preserved.** `defects.json` is not edited. `test_the_six_defects_and_their_anchors_are_intact` checks that there are exactly six defects and that every anchor is still in its file.

## Verification

- RED, previous runner (the first proposal, rebuilt from its patch): 9 of the 17 new mutation-runner tests fail, for the reasons above. Two of them fail on missing new API (a `timeout` keyword and a module-level `time` import), not on behaviour, and are labelled so in the log (`mutation-red-previous-runner.log`).
- GREEN, revised runner: 17 of 17 pass (`mutation-focused-r2.log`, earlier revision); all three focused files together: 29 of 29 pass (`focused-final-proposal.log`).
- RED, outer termination and guard on unpatched `origin/main`: 2 + 5 failures (`red-outer-and-guard-original.log`). GREEN after the patch: 2 and 10 (`outer-termination-patched.log`, `focused-final-proposal.log`).
- Targeted verification on the candidate tree `a99609cf` with the final runner and patched `ci.py`:
  - `override-silently-accepted` by static: 19 s, CAUGHT, `MUTATIONS_OK` (`mutation-targeted-r2.log`, which used the earlier `ci.py`).
  - `persistence-write-dropped` by unit: 695 s, CAUGHT, `MUTATIONS_OK`, cleanup 0 (`mutation-targeted-r3.log`, with the final `ci.py`).
  - The dedicated temporary directory had one file left after the run. It was written by an unrelated test (`test_narrative_engine_integration.py`), not by the runner. That defect is fixed in #462 (RED `tmp82i_f_2m.json`, GREEN empty).

## Remaining risks (not yet closed)

1. The full six-defect run has not been performed. It needs one authorised full validator run after review.
2. The POSIX process-group kill was not exercised; only Windows was.
3. `taskkill /T` cannot reach a descendant that was re-parented before the kill. Confirmed only for the tree still attached to the root.
4. Each rung's temporary output file in `harness/ci.py` is removed in a `finally` with the error ignored. If a descendant still holds the file on Windows, it would remain silently. This is a small, real gap.
5. The Linux and macOS commands in the CI proposal (#458) were not executed.
6. The candidate `a99609cf` does not contain #462's test fix or Parts 1–3. Any protected change, and the test fix, makes a new source tree that must be qualified on its own.

## Exact human-maintained actions

1. Review and apply Part 1 (`harness/mutations/run.py` and config). Its PR is stacked on #461.
2. Review and apply Part 2 (the runner regression tests). Its PR is stacked on Part 1.
3. Review and apply Part 3 (`harness/ci.py`, `factory/guard.py`, and the two guard/termination tests). Its PR is stacked on Part 2.
4. Review and merge #462 (the test-temp fix), which is independent.
5. Decide whether the 5,400-second outer bound should stay, based on one further measured unit-caught run. The current evidence supports keeping it.
6. Authorise exactly one full validator run at the final head, after 1–5 are applied. This is the only run that can establish `GATE_OK`. Do not run it before then.
7. Separately, decide the public history question: the username appears in earlier commits and three earlier receipts (`2026-10-15` blocked E2E; `2026-10-16` manual E2E and adversarial). Rewriting shared history is an owner decision, not a builder action.

## Authority boundary

The builder has not merged, rewritten history, changed authentication or changed `FACTORY_AUTONOMY`. Protected changes stop at the human-maintained route.

## Correction: rung output-file cleanup (owner review of #465)

`harness/ci.py`'s `run()` previously removed its temporary output file inside `finally` and swallowed the `OSError`. It now:

- retries the removal briefly through `_discard_rung_output()`, then returns the last error to the caller;
- keeps the rung's own exit code and diagnosis unchanged, and appends a `CLEANUP_FAILED` line naming the file and the error;
- turns a successful rung into a failure (exit 1) when its output file cannot be removed, because a gate that cannot clean up after itself does not pass.

Regression evidence: `test_successful_rung_leaves_no_temporary_output_file` (passes both before and after, as a guard); `test_failed_rung_keeps_its_own_diagnosis_and_reports_the_cleanup_failure` and `test_successful_rung_with_a_cleanup_failure_is_not_reported_as_success` (RED against the previous helper, GREEN after). Logs are in `protected-proposals/` of #465.
