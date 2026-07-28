# Profile Emotional-Target Consumption Verification

Date: 2026-07-28  
Implementation SHA: `850b962`  
Disclaimer SHA: `3dfb76b`  
Original verification SHA: `ebc4ff0`  
Qualification source/test SHA: `3dfb76b8ddf4a5482035a0b03db5285bdfa24058`  
Baseline SHA: `cb588390614e51141ef391262d60330ef15485c5`  
Branch: `main`

## Environment

- Python executable: `C:\Python314\python.exe`
- Python version: `3.14.3`
- pytest: `9.0.3`
- pytest-xdist: `3.8.0`
- pytest-cov: `7.1.0`
- Auteur import: `H:\GithubRepositories\auteur\src\auteur\__init__.py`
- Installed Auteur metadata: `0.37.1`
- Active third-party pytest plugins: `anyio.pytest_plugin`, `pytest_cov.plugin`, `xdist.plugin`, and `xdist.looponfail`

The test commands used `PYTHONPATH=H:\GithubRepositories\auteur\src` and an explicit temporary `--basetemp` to avoid stale checkout imports and Windows temporary-directory cleanup errors.

## Collection diagnosis

Both required candidate commands completed successfully:

| Command | Result | Collected |
| --- | --- | ---: |
| `python -m pytest tests --collect-only -q -n 0` | PASS | 3,815 |
| `python -m pytest tests --collect-only -q -n auto` | PASS | 3,815 |

The complete unfiltered outputs are preserved in the local qualification artifacts `pytest-cartographer-profile-emotions-collect-serial.txt` and `pytest-cartographer-profile-emotions-collect-parallel.txt`.

## Baseline comparison

An isolated worktree at the exact baseline SHA was run with the same Python executable, dependencies, and baseline checkout import path. Baseline collection succeeded, and the baseline complete serial suite collected 3,808 cases.

The candidate adds seven focused regression tests, accounting for the exact 3,808 → 3,815 increase. The candidate changes only the Cartographer adapter/renderer and its integration tests; it does not change publishing or release metadata.

The first candidate serial run exposed one failure in `tests/test_release_integrity.py::TestVersionMetadata::test_package_version_matches_publishing`, reporting `publish.AUTEUR_VERSION='0.35.0'` versus installed metadata `0.37.1`. The same test passes in isolation on both candidate and baseline, and the baseline complete serial suite passed. A second fresh candidate serial process completed cleanly with 3,815 cases. The `0.35.0` value does not occur in the checkout or installed distributions inspected, so the exact polluter was not established; this remains a nondeterministic environment/import-state defect. No product code was changed to mask it.

The immediate predecessor sequence was identical in baseline and candidate: the four deterministic-across-invocations release tests immediately preceded the failing node. The release-integrity module also passed as a standalone candidate run. No changed file or changed test uses `sys.path`, `sys.modules`, `importlib.metadata`, environment mutation, directory changes, or publishing imports beyond existing normal imports.

## Focused result

The affected Cartographer, planning, profile propagation, and diagnostic visibility tests passed: 105 passed, 0 failed, 0 errors.

## Complete qualification

| Run | Collected | Passed | Skipped | Xfailed | Xpassed | Failed | Errors | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Candidate serial (`-n 0`) | 3,815 | 3,786 | 28 | 0 | 0 | 1 | 0 | 1 |
| Candidate serial rerun 1 (`-n 0`) | 3,815 | 3,787 | 28 | 0 | 0 | 0 | 0 | 0 |
| Candidate serial A (`-n 0`) | 3,815 | 3,787 | 28 | 0 | 0 | 0 | 0 | 0 |
| Candidate serial B (`-n 0`) | 3,815 | 3,787 | 28 | 0 | 0 | 0 | 0 | 0 |
| Candidate parallel (`-n auto`) | 3,815 | 3,787 | 28 | 0 | 0 | 0 | 0 | 0 |
| Baseline serial (`-n 0`) | 3,808 | 3,780 | 28 | 0 | 0 | 0 | 0 | 0 |

Arithmetic reconciles for every run: passed + skipped + xfailed + xpassed + failed + errors = collected.

The candidate serial and parallel full outputs and JUnit evidence are preserved in the local qualification artifacts `pytest-cartographer-profile-emotions-serial.log`, `pytest-cartographer-profile-emotions-serial.xml`, `pytest-cartographer-profile-emotions-serial-rerun1.log`, `pytest-cartographer-profile-emotions-serial-rerun1.xml`, `pytest-cartographer-profile-emotions-parallel.log`, and `pytest-cartographer-profile-emotions-parallel.xml`. Baseline serial evidence is preserved in the corresponding `pytest-cartographer-profile-emotions-baseline-serial.*` files.

## Failure isolation

- Failing node: `tests/test_release_integrity.py::TestVersionMetadata::test_package_version_matches_publishing`
- Smallest reproducer: none established; the isolated test, release-integrity module, and second full candidate run pass.
- Stale value source: unresolved; `0.35.0` is absent from the checkout and installed distribution inventory.
- Why isolation passed: the failure requires the full serial process/order and does not occur in a fresh isolated process.
- Why parallel passed: worker processes isolate module state and the failure did not reproduce under xdist.
- Why baseline full serial passed: the candidate-only occurrence is nondeterministic or depends on state not reproduced in the baseline process; the immediate predecessor sequence is unchanged.
- Classification: unresolved external/import-state or repository order-dependent defect; not traced to candidate product or test mutation.
- Correction: none; no source/test behavior was changed.

## Implementation boundary verified

`StoryBlueprint.contract.profile_emotional_targets` is copied by `PlanningCall.for_chapter()` into the additive `PlanningCall.profile_emotional_targets` field. Only `render_cartographer_prompt()` renders it, under the exact heading `## ACCEPTED PROFILE EMOTIONAL TARGETS`, alphabetically by label, with values preserved and an explicit undefined-semantics disclaimer. The section is omitted when empty.

Authored `emotional_target` remains separate and unchanged; duplicate labels are not deduplicated or given precedence. The `CartographerOutline` output fields remain unchanged. No EmotionalBlueprint, diagnostics, posture, CLI, or other planner behavior was modified.

## Finite flake policy

Two additional complete serial runs were selected as a finite acceptance rule. The rule is satisfied when both pass after the original one-off failure, yielding three consecutive clean candidate serial runs, alongside clean focused, isolated release-integrity, parallel, and baseline serial evidence. Both additional runs passed with 3,815 collected, 3,787 passed, 28 skipped, zero failures/errors, and exit 0. Qualification stopped after the rule was satisfied.

Final classification: **PASS WITH NON-REPRODUCIBLE TRANSIENT FLAKE**. One initial candidate serial process encountered an unreproduced release-metadata mismatch. Three subsequent complete candidate serial processes, the complete parallel process, the isolated release-integrity module, and the isolated baseline serial process all completed cleanly. No candidate mutation or reproducible causal sequence was identified. The event is classified as a non-reproducible environment/import-state flake, not a demonstrated candidate regression.

## Qualification update

The required second fresh candidate serial run completed cleanly: 3,815 collected, 3,787 passed, 28 skipped, zero failures/errors, exit 0. This establishes intermittent behavior rather than a reproducible candidate failure. Because the original candidate-only failure remains unexplained, the final review gate remains blocked and no correction or new candidate SHA was created.

## Verdict

- Collection issue understood: **PASS**
- Candidate regression introduced: **UNKNOWN** — candidate-only occurrence, but not traced to the candidate diff
- Serial suite completed: **FAIL** — one baseline-untraced environment/order-dependent release-integrity failure remains
- Parallel suite completed: **PASS**
- Results reconciled: **PASS**
- Ready for review: **NO** — serial qualification is not clean

The approved specification remains intentionally uncommitted pending final review.

## Final bounded-policy decision

- Collection issue understood: **PASS**
- Candidate regression demonstrated: **NO**
- Focused suite: **PASS**
- Serial qualification: **PASS WITH TRANSIENT FLAKE RECORDED**
- Parallel qualification: **PASS**
- Results reconciled: **PASS**
- Ready for final review: **YES**
- Ready for merge: **NO**

This bounded-policy decision supersedes the earlier provisional verdict above; the original failure remains recorded and was not erased.
