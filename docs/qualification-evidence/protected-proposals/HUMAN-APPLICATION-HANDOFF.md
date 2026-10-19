# Handoff: applying the protected validator repair and qualifying the final candidate

For: the authorised human maintainer. Status: nothing in this handoff has been applied. The builder has not merged, has not changed protected files on any merged branch, has not altered any credential, and has not changed `FACTORY_AUTONOMY`.

## 0. Preconditions and what each gate covers

Three separate gates are involved. They are not the same thing.

1. **Offline validator (`harness/ci.py`).** This is the standalone, manually started validator. It does not invoke Claude and does not require a Claude CLI login. Its configuration (`harness/harness.config.json`) runs the static checks, unit tests, the offline `story-discovery` journey (start, refine, review, compose, accept), holdout scenarios and the six mutations. It excludes the LLM-dependent `run` command. Its only external requirement is a Python environment with the declared dependencies, including Playwright.
2. **Factory agent and operator workflows.** These are Claude-powered. They need the configured agent credentials for the operator context. A logged-out Claude CLI (`claude auth status` reporting `loggedIn: false`) blocks these workflows. It does not block step 6 below. If a site-specific manual process needs Claude authentication, the maintainer should name that exact requirement rather than attributing it to the offline validator.
3. **Factory autonomy (`FACTORY_AUTONOMY`).** `factory/config.sh` sets `FACTORY_AUTONOMY="${FACTORY_AUTONOMY:-0}"`, so an unset value means `0`. `factory/orchestrator.sh` refuses dispatch below 1, validation dispatch needs 2 or more, and merge dispatch needs 3 or more. Confirm the effective value in the exact launcher environment before any factory workflow. Do not raise it as part of this handoff.

Before applying protected changes, the maintainer should also confirm that the protected-file guard is in the state reviewed in #465. Part 3 extends protection to `harness/*`, so the builder cannot apply these changes autonomously.

## 1. Independent fix, ordinary review: PR #462

`test(narrative): keep the diagnostics test's story bible out of the system temp directory`. Two test files, no product code, no protected paths.

Merge order is conditional. Merge #462 through the normal review process when the authorised integration process allows it. It must not require bypassing a validator gate that is broken. If the existing gate blocks #462 because of the protected-runner defect that this handoff repairs, do not waive the gate and do not require a prior green merge that cannot happen. The maintainer may stage #462 together with the protected repairs under an authorised transition.

## 2. Protected validator repair: PRs #463, #464, #465, in this order

Apply each patch on a fresh branch from `main`, through the human-maintained protected route. Each patch is a `git apply` input and is unchanged from the reviewed proposal.

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

Owner decision recorded on #457: keep the constraints already declared in `pyproject.toml`.

1. pytest 8.4.2 (within `>=8,<9`). The existing lock entry of 9.1.1 violates the declared `<9`.
2. openai 1.109.1 (within `>=1.40,<2`). The existing lock entry of 2.45.0 violates the declared `<2`. Only the mocked openai test module was verified against 1.109.1.
3. The regenerated dev tree (`pytest-xdist`, `ruff`), which the original lock lacked.

Verification after applying: `uv lock --check` must exit 0.

## 4. CI browser installation: PR #458 (protected, when approved)

`ci-playwright-browser-install.patch` adds Chromium install steps to `validation.yml`, `stabilization.yml` and `release-qualification.yml`. Linux uses `--with-deps` on `runner.os == 'Linux'`. Windows and macOS use the plain install.

Qualification limit: the Windows command was run locally. The Linux and macOS commands were not run. The first CI run on each runner is the verification.

## 5. Build the exact combined candidate

After steps 1–4 are applied through the protected route:

1. Create a candidate branch from the resulting `main`. Merge the Studio stack in its existing dependency order (#440, #441–#447, #448, #449, #451, #450, #456, #457, #458 as applicable) and the baseline PRs (#452–#455).
2. Record the candidate's commit and tree SHAs before running anything.
3. Confirm the candidate tree equals the intended tree, not a dry-run tree.

The previous candidate `a99609cf` (tree `c782b0c4`) is not this candidate. It does not contain the protected repair, and it has no full passing validator result.

## 6. One full offline validator qualification

Run exactly once at the recorded candidate SHA. The environment needs the project's declared dependencies, including Playwright. No Claude login is needed for this step. Capture the full output and the exit code. Do not run it again unless the candidate SHA changes.

```bash
PYTHONPATH="<checkout>/src" PYTHONIOENCODING=utf-8 python harness/ci.py > validator-<sha>.log 2>&1; echo "EXIT=$?" >> validator-<sha>.log
```

Pass criteria. All must hold:

- Final line `GATE_OK mode=full` and `EXIT=0`.
- `STATIC_OK`, `UNIT_PASSED`, `E2E_PASSED steps=14`, `HOLDOUT_PASSED scenarios=3`.
- `MUTATIONS_TOTAL=6`, `MUTATIONS_CAUGHT=6`, `MUTATIONS_INCONCLUSIVE=0`, `MUTATIONS_NOT_INJECTED=0`, `MUTATIONS_CLEANUP_FAILURES=0`, then `MUTATIONS_OK`.

Anything else is not a pass. A timeout, a cleanup failure, or an inconclusive mutant fails the gate. Record the failure with its log. Do not rerun to make it pass.

### Historical result (preserved, not a pass for the new candidate)

`fdcf39cb` (branch `codex/studio-combined-candidate`) has an authentic full-run log in this repository: `docs/qualification-evidence/2026-10-16-combined-fdcf39cb-validator-full.log`, with `MUTATIONS_TOTAL=6`, `MUTATIONS_CAUGHT=6`, `GATE_OK mode=full`, and `EXIT=0`. That result stands as history for `fdcf39cb`.

It does not qualify the new combined final candidate. The new candidate has not been built or run, and no exact-final-SHA PASS exists yet.

## 7. Evidence

Publish the log with a parsed receipt: candidate commit, tree, interpreter and package versions, command, exit code, gate markers, and the SHA-256 of the raw log. Keep failed attempts. Redact the local user-home prefix in every form (single, doubled, forward slash), and check the redacted copy with a scan before publication.

## Qualification limits to state explicitly

- Engineering qualification (the offline validator) is separate from connected-Codex execution, factory auto-merge, and human usability. Those are separate pending qualifications and are not established by this handoff.
- POSIX process-group termination has not been exercised; only Windows was.
- `taskkill /T` cannot reach a descendant re-parented before the kill.
- The Linux and macOS CI commands are unverified until the first real CI run.
- The username appears in earlier commits and three earlier receipts. Rewriting shared history is an owner decision, not part of this handoff.
- Human usability is NOT TESTED.

## Stop conditions

Stop and report, without retrying, if: a patch no longer applies; a test that passed before fails; `uv lock --check` fails; or the full validator fails for any reason. These are findings to be fixed through review, not conditions to be worked around. Do not waive the gate to unblock #462 or any later step.
