# Profile Emotional-Target Consumption Verification

Date: 2026-07-28  
Candidate SHA: `3dfb76b8ddf4a5482035a0b03db5285bdfa24058`  
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

The candidate serial run exposed one failure in `tests/test_release_integrity.py::TestVersionMetadata::test_package_version_matches_publishing`, reporting `publish.AUTEUR_VERSION='0.35.0'` versus installed metadata `0.37.1`. The same test passes in isolation on both candidate and baseline, and the baseline complete serial suite passed. The failure is therefore an order-dependent environment/import-metadata limitation, not a traced regression in the candidate boundary. No product code was changed to mask it.

## Focused result

The affected Cartographer, planning, profile propagation, and diagnostic visibility tests passed: 105 passed, 0 failed, 0 errors.

## Complete qualification

| Run | Collected | Passed | Skipped | Xfailed | Xpassed | Failed | Errors | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Candidate serial (`-n 0`) | 3,815 | 3,786 | 28 | 0 | 0 | 1 | 0 | 1 |
| Candidate parallel (`-n auto`) | 3,815 | 3,787 | 28 | 0 | 0 | 0 | 0 | 0 |
| Baseline serial (`-n 0`) | 3,808 | 3,780 | 28 | 0 | 0 | 0 | 0 | 0 |

Arithmetic reconciles for every run: passed + skipped + xfailed + xpassed + failed + errors = collected.

The candidate serial and parallel full outputs and JUnit evidence are preserved in the local qualification artifacts `pytest-cartographer-profile-emotions-serial.log`, `pytest-cartographer-profile-emotions-serial.xml`, `pytest-cartographer-profile-emotions-parallel.log`, and `pytest-cartographer-profile-emotions-parallel.xml`. Baseline serial evidence is preserved in the corresponding `pytest-cartographer-profile-emotions-baseline-serial.*` files.

## Implementation boundary verified

`StoryBlueprint.contract.profile_emotional_targets` is copied by `PlanningCall.for_chapter()` into the additive `PlanningCall.profile_emotional_targets` field. Only `render_cartographer_prompt()` renders it, under the exact heading `## ACCEPTED PROFILE EMOTIONAL TARGETS`, alphabetically by label, with values preserved and an explicit undefined-semantics disclaimer. The section is omitted when empty.

Authored `emotional_target` remains separate and unchanged; duplicate labels are not deduplicated or given precedence. The `CartographerOutline` output fields remain unchanged. No EmotionalBlueprint, diagnostics, posture, CLI, or other planner behavior was modified.

## Verdict

- Collection issue understood: **PASS**
- Candidate regression introduced: **UNKNOWN** — candidate-only occurrence, but not traced to the candidate diff
- Serial suite completed: **FAIL** — one baseline-untraced environment/order-dependent release-integrity failure remains
- Parallel suite completed: **PASS**
- Results reconciled: **PASS**
- Ready for review: **NO** — serial qualification is not clean

The approved specification remains intentionally uncommitted pending final review.
