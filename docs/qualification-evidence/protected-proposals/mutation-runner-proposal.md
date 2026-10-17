# Protected mutation-runner repair: proposal for the human-maintained route

Status: prepared, not applied. `harness/mutations/*` is protected (`FACTORY_RULES.md`). `harness/harness.config.json` is part of the validator configuration and is included here so the change is reviewed as one unit. The builder did not edit any of these files in the repository, and it did not bypass the protected-file guard.

## Patch

`mutation-runner-failure-paths.patch` (339 lines), relative to `origin/main` (`bb9c102d`). It changes:

1. `harness/mutations/run.py`
2. `harness/harness.config.json`
3. `tests/test_mutation_runner_failure_paths.py` (new)

Verified with `git apply --check` against the candidate `a99609cf` (tree `c782b0c4`).

## Root cause (established from the published attempt logs)

- Both attempts of the full validator at `a99609cf` first raised `subprocess.TimeoutExpired` at the mutation runner's **per-mutant** deadline of 600 seconds (`harness/mutations/run.py`, `subprocess.run(..., timeout=600)`).
- The Windows temporary-directory cleanup errors (WinError 32, then WinError 145) occurred while that exception was unwinding. They were a consequence, not the cause.
- The per-mutant deadline was below the configured unit rung (`unit_timeout_s` = 900). A mutant caught by the unit rung must let the whole unit suite finish, which takes about 9 minutes on this host.
- `subprocess.run` ends only the direct child on timeout. The inner gate's pytest-xdist workers kept files open in the throwaway build.
- A second defect in the same runner: the inner gate prints `GATE_FAILED` after a rung times out, so a timeout inside the inner gate counted as a **caught** mutation.

## What the patch changes

- **Per-mutant deadline** is derived from the configured rungs: `static_timeout_s + unit_timeout_s + e2e_timeout_s + mutation_margin_s` (120 s), which is 1,920 s with the current configuration.
- **Outer budget** is checked before any mutant runs. If `mutations_timeout_s` cannot cover every mutant, the runner prints `MUTATIONS_BUDGET` and exits 1 without running anything. The configuration is raised from 5,400 to 11,520 (6 × 1,920).
- **Process tree**: the inner gate is started in its own process group (POSIX) or addressed with `taskkill /T /F` (Windows) on timeout, then awaited, before the temporary directory is removed.
- **Strict classification**. A mutant is `CAUGHT` only when the inner gate completed, reported a `GATE_FAILED` rung, and no rung timed out. Otherwise it is `INCONCLUSIVE`: an outer or inner timeout, a rung timeout inside the gate, or a non-zero exit with no verdict. An `INCONCLUSIVE` result fails the whole verdict. `MUTATIONS_OK` requires every mutant caught, zero inconclusive, and zero not injected.
- **Cleanup** uses `TemporaryDirectory(ignore_cleanup_errors=True)`, after the tree has been terminated. Cleanup errors no longer decide a verdict.
- The six defects, their anchors and the `NOT_INJECTED` contract are unchanged.

## Evidence

- Focused regression file (`tests/test_mutation_runner_failure_paths.py`, 9 tests): the 5 failure-path tests fail against the unpatched `origin/main` runner for the stated reasons (an inner timeout counted as caught; a crash without a verdict counted as caught; the hanging gate not bounded; no outer-budget check; no derived budget). The other 4 (genuine catch, escape, not-injected, read-only leftover) pass on both versions and guard behaviour that must not change. The read-only test does not reproduce the Windows failure; it only guards against a cleanup crash.
- Focused suite against the patched runner: 9 passed (see the qualification evidence for the exact command and output).
- Targeted verification on the candidate tree `a99609cf` with the real inner gate, restricted to two of the six defects (`override-silently-accepted`, caught by static; `persistence-write-dropped`, caught by unit): see `mutation-targeted-patched.log`.

## Not yet verified

- The full six-defect run with the patched runner. Deliberately not run until the targeted verification and focused tests are reviewed, to avoid another hour-long run on an unreviewed change.
- Linux and macOS behaviour of the process-group kill (POSIX path). Only Windows was exercised.
- `harness/ci.py`'s own `run()` has the same direct-child-only termination for the outer `mutations` rung. A follow-up change to `harness/ci.py` is needed for the outer rung to clean its tree too. This is not in this patch.

## Review points for the owner

1. Whether 1,920 s per mutant and 11,520 s outer are acceptable for the validator's runtime.
2. Whether `harness/ci.py`'s outer-rung termination should be changed in the same review.
3. Whether the six-mutant set should be rerun as a full validator run after review, as the single authorised exact-head run.

## Authority boundary

Nothing here is applied, merged or released by the builder. Protected-file changes require the human-maintained route.
