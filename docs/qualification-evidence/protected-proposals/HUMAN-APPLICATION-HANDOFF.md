# Handoff: applying the protected validator repair and qualifying the final candidate

For: the authorised human maintainer. Status: nothing in this handoff has been applied. The builder has not merged, has not changed protected files on any branch that is merged, has not altered authentication, and has not changed `FACTORY_AUTONOMY`.

## 0. Preconditions (check first)

- `FACTORY_AUTONOMY` is still `0`. This handoff does not change it.
- Claude is authenticated for the validator operator. At the last check it was logged out (`loggedIn: false`).
- The protected-file guard has been reviewed. Part 3 extends protection to `harness/*`, so the builder cannot apply these changes autonomously.
- Each step below is reviewed through the normal protected route. Do not merge a stack in one step.

## 1. Independent fix, ordinary review: PR #462

`test(narrative): keep the diagnostics test's story bible out of the system temp directory`. Two test files, no product code, no protected paths. Review and merge through the normal process.

## 2. Protected validator repair: PRs #463, #464, #465, in this order

Apply each patch on a fresh branch from `main`, through the human-maintained protected route. Each patch is a `git apply` input.

```bash
git switch -c protected/mutation-runner-revised origin/main
git apply --check <p1>   # then: git apply <p1>
git apply --check <p2>   # then: git apply <p2>
git apply --check <p3>   # then: git apply <p3>
```

Patch files (in `docs/qualification-evidence/protected-proposals/` of each PR):

| Step | Patch | Changes | Protected |
|---|---|---|---|
| a | `mutation-runner-revised-p1-runner-config.patch` (#463) | `harness/mutations/run.py`, `harness/harness.config.json` | yes |
| b | `mutation-runner-revised-p2-runner-tests.patch` (#464) | `tests/test_mutation_runner_failure_paths.py` (17 tests) | no |
| c | `mutation-runner-revised-p3-entrypoint-guard.patch` (#465) | `harness/ci.py`, `factory/guard.py`, `tests/test_outer_rung_termination.py` (5 tests, including the cleanup corrections), `tests/test_factory_guard_validator_paths.py` | yes (`harness/ci.py`, `factory/guard.py`) |

Focused check after applying all three (must pass before anything is merged):

```bash
python -m pytest -q tests/test_mutation_runner_failure_paths.py tests/test_outer_rung_termination.py tests/test_factory_guard_validator_paths.py
```

Expected: 32 passed (17 + 5 + 10).

## 3. Dependency and lock change: PR #457 (protected)

`playwright-dev-dependency.patch` adds `playwright>=1.64,<2` to the `dev` extra in `pyproject.toml`. `uv-lock-playwright.patch` is the regenerated lock. Apply both, or run `uv lock` after applying the first if the lock patch conflicts.

Decisions the maintainer must make before applying:

1. Accept pytest 8.4.2 (the lock currently pins 9.1.1, which violates the declared `<9`), or change the declared constraint.
2. Accept openai 1.109.1 (the lock currently pins 2.45.0, which violates the declared `<2`). Only the mocked openai test module was verified against 1.109.1.
3. Accept the regenerated dev tree (`pytest-xdist`, `ruff`), which the original lock lacked.

Verification after applying: `uv lock --check` must exit 0.

## 4. CI browser installation: PR #458 (protected, when approved)

`ci-playwright-browser-install.patch` adds Chromium install steps to `validation.yml`, `stabilization.yml` and `release-qualification.yml`. Linux uses `--with-deps` on `runner.os == 'Linux'`. Windows and macOS use the plain install.

Qualification limit: the Windows command was run locally. The Linux and macOS commands were not run, and the first CI run on each runner is the verification.

## 5. Build the exact combined candidate

After steps 1–4 are merged through the protected route:

1. Create a candidate branch from the resulting `main`, merging the Studio stack in its existing dependency order (#440, #441–#447, #448, #449, #451, #450, #456, #457, #458 as applicable) and the baseline PRs (#452–#455).
2. Record the candidate's commit and tree SHAs before running anything.
3. Confirm the candidate tree equals the intended tree, not a dry-run tree.

## 6. One full validator qualification

Run exactly once at the recorded candidate SHA, with a validation environment that has the project's declared dependencies (including Playwright) installed. Capture the full output and the exit code. Do not run it again unless the candidate SHA changes.

```bash
PYTHONPATH="<checkout>/src" PYTHONIOENCODING=utf-8 python harness/ci.py > validator-<sha>.log 2>&1; echo "EXIT=$?" >> validator-<sha>.log
```

Pass criteria. All must hold:

- Final line `GATE_OK mode=full` and `EXIT=0`.
- `STATIC_OK`, `UNIT_PASSED`, `E2E_PASSED steps=14`, `HOLDOUT_PASSED scenarios=3`.
- `MUTATIONS_TOTAL=6`, `MUTATIONS_CAUGHT=6`, `MUTATIONS_INCONCLUSIVE=0`, `MUTATIONS_NOT_INJECTED=0`, `MUTATIONS_CLEANUP_FAILURES=0`, then `MUTATIONS_OK`.

Anything else is not a pass. A timeout, a cleanup failure, or an inconclusive mutant fails the gate. Record the failure with its log; do not rerun to make it pass.

## 7. Evidence

Publish the log with a parsed receipt: candidate commit, tree, interpreter and package versions, command, exit code, gate markers, and the SHA-256 of the raw log. Keep failed attempts. Redact the local user-home prefix in every form (single, doubled, forward slash), and check the redacted copy with a scan before publication.

## Qualification limits to state explicitly

- POSIX process-group termination has not been exercised; only Windows was.
- `taskkill /T` cannot reach a descendant re-parented before the kill.
- The Linux and macOS CI commands are unverified until the first real CI run.
- The username appears in earlier commits and three earlier receipts. Rewriting shared history is an owner decision, not part of this handoff.
- Human usability is NOT TESTED.

## Stop conditions

Stop and report, without retrying, if: a patch no longer applies; a test that passed before fails; `uv lock --check` fails; or the full validator fails for any reason. These are findings to be fixed through review, not conditions to be worked around.
