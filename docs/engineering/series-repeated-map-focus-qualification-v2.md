# Repeated Map/Focus V2 Qualification

Date: 2026-08-25

## Qualification boundary

This report qualifies the exact product candidate
`2e066108db51ff4b42b41316d5ea5e8d627eef71` in the linked worktree
`H:/GithubRepositories/auteur/.worktrees/repeated-map-focus-v2`.

The candidate is the implementation and test state before this documentation
handoff. Documentation and candidate-addressed evidence are not packaged by
Auteur, so this report does not change the bytes qualified below.

The successful workspace preflight verified:

- repository root: `H:/GithubRepositories/auteur/.worktrees/repeated-map-focus-v2`;
- linked-worktree git directory with common directory
  `H:/GithubRepositories/auteur/.git`;
- exact HEAD: `2e066108db51ff4b42b41316d5ea5e8d627eef71`;
- clean candidate source/test state before evidence generation.

Source/test runs imported the candidate from:

```text
H:/GithubRepositories/auteur/.worktrees/repeated-map-focus-v2/src
H:/GithubRepositories/auteur/.worktrees/repeated-map-focus-v2
```

## Focused and relevant regression qualification

The Task 12 serial and parallel matrices covered:

```text
tests/test_series_repeated_map_focus.py
tests/test_series_vertical_slice_models.py
tests/test_series_vertical_slice_service.py
tests/test_series_vertical_slice_cli.py
tests/test_series_vertical_slice_e2e.py
tests/test_provenance_pilot.py
tests/test_story_state_commands.py
tests/test_story_state_manager.py
```

Both runs reconciled identically:

| Run | Collected | Passed | Skipped | Xfailed | Xpassed | Failed | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Serial | 212 | 212 | 0 | 0 | 0 | 0 | 0 |
| Parallel (`-n 2`) | 212 | 212 | 0 | 0 | 0 | 0 | 0 |

The Task 11 R1–R5 fixture/test gate passed 168/168. The repeated Map/Focus
suite itself passed 54/54.

## Complete source qualification

`scripts/release_evidence.py --skip-wheel` produced
`docs/qualification-evidence/2e066108db51ff4b42b41316d5ea5e8d627eef71.json`
from the exact candidate. Its complete repository accounting is:

| Collected | Passed | Skipped | Xfailed | Xpassed | Failed | Errors | Reconciles |
|---:|---:|---:|---:|---:|---:|---:|---|
| 4,477 | 4,449 | 1 | 27 | 0 | 0 | 0 | yes |

The candidate was compared with baseline
`d3bb1eb37d065b34c132771cf19a0856e60d0cea`. Both candidate and baseline had
zero failure nodes: added failures 0, removed failures 0, unchanged failures
0.

This is source-qualified for the bounded candidate behavior described here.

## Installed artifact qualification

`scripts/verify_wheel.py` built and tested a wheel from the same candidate
worktree:

- filename: `auteur-0.37.1-py3-none-any.whl`;
- package version: `0.37.1`;
- wheel file count: `394`;
- SHA-256:
  `c5a0e8df92c523f58a750e23db6acd174ea7680892d010e8da5edb476e908950`;
- installed import resolved from the isolated environment's site-packages;
- all 11 installed checks passed: import/version, pack list, pack inspect,
  recommendation, recommendation durability, zero pre-acceptance mutation,
  explicit acceptance mutation, restart persistence, pack version/hash,
  genre validation, and genre diagnosis.

This is artifact-qualified for the same bounded candidate behavior. It is not
release-ready: publication, release finalization, and authorization remain
separate decisions.

## R1–R5 result summary

The corrected ledger demonstrates:

- opening Book 2 uses accepted history through Book 1 only;
- opening Book 3 uses accepted history through Book 2 only;
- opening Book 4 uses accepted history through Book 3 only;
- current Book planning intent can reactivate accepted older facts without
  becoming Book Direction authority;
- resolved and superseded history is not surfaced as active context by default;
- dormant and irrelevant accepted facts are distinguished;
- unaccepted proposals do not enter Map context;
- grouped context retains exact accepted provenance and specific why-now text;
- deleting a derived projection and rebuilding it produces equivalent context;
- Map, Focus, choose-other, and defer do not mutate accepted authority;
- incompatible recommendations and stale proposals cannot cross the action
  boundary.

## Explicit non-claims

This qualification does not claim finite-Series support, a complete Series
architecture, a universal lifecycle abstraction, a universal relevance or
recommendation engine, free-form Book-N Direction authoring, or a generalized
Series-extent model. The deterministic Book 3/4 decision seeds are bounded
qualification inputs, not a general recommendation-content solution.

This qualification is not human usability validation, participant evidence,
or evidence that a creative beginner understands the Map/Focus experience.

## Remaining evidence boundary

A real participant is still required to determine whether a creative beginner
can understand and use the bounded journey: sparse Series Direction, local Book
Direction, accepted realization, repeated Map/Focus context, why-now
explanations, bounded decision actions, and the distinction between workflow
choice and narrative authority. Human evidence is also required for the
quality of the recommendation content and for whether compact grouped history
remains cognitively useful as a Series grows.

Repeated Map/Focus V2 is implemented, source-qualified, and
artifact-qualified only for opening Book-N planning through the accepted R1–R5
behavior. It is not a claim of finite-Series support, complete Series
architecture, human usability validation, or release readiness.
