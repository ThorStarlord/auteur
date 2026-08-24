# Series Vertical Slice V1 Focus Authority Clarification

Status: the Variant B Focus wording clarification is source-qualified and
artifact-qualified as a presentation-only change. Synthetic comprehension
regression passed. Real human validation remains outstanding. This is not a
release-ready claim and does not qualify finite-Series or repeated-Book
architecture.

## Scope

The change addresses one narrow ambiguity found by the synthetic wording
experiment: a beginner could interpret choosing a Book 2 Focus option as
accepting Book 2 Direction or making Book 2 canon.

The exact beginner-facing addition is:

```text
This is a planning choice, not Book 2 canon.
Choosing an option records what you want to explore next. You can change or
develop it before accepting a Book 2 direction.
```

The existing action labels remain unchanged. No domain model, service,
persistence, authority, or canonical-state behavior was changed. In
particular, choosing the recommended option, choosing another option from the
exact proposal, or deferring still records workflow history only.

## Candidate identity

The product candidate qualified here is:

```text
candidate SHA: d3bb1eb37d065b34c132771cf19a0856e60d0cea
repository:    H:/GithubRepositories/auteur
worktree:      H:/GithubRepositories/auteur/.worktrees/series-vertical-slice-v1-qualification-wording
git common dir: H:/GithubRepositories/auteur/.git
checkout:      detached at the candidate SHA
Python:        C:/Python314/python.exe
import:        H:/GithubRepositories/auteur/.worktrees/series-vertical-slice-v1-qualification-wording/src/auteur/__init__.py
```

The candidate worktree was clean for source and test bytes when the structured
qualification run started. The generated JSON is the non-packaged evidence
artifact at:

```text
docs/qualification-evidence/d3bb1eb37d065b34c132771cf19a0856e60d0cea.json
```

The documentation commit recording this result is separate from the
qualified product candidate. `docs/` is not packaged by the project.

## TDD evidence

The focused CLI assertion was first run against the pre-change candidate and
failed because Focus did not contain:

```text
This is a planning choice, not Book 2 canon.
```

The minimal formatter and test change was then implemented. The focused
vertical-slice/provenance matrix passed:

```text
137 passed in 32.28s
```

The changed formatter and CLI test passed Ruff and `git diff --check`.

## Synthetic comprehension regression

This is synthetic comprehension evidence only. It is not participant
evidence, usability validation, or real-user approval.

Ten fresh independent synthetic contexts received only:

1. the short Archive of Lies writer scenario;
2. the beginner-facing acceptance, Map, and updated Focus output; and
3. the existing Q5/Q6 comprehension questions.

They did not receive ADRs, Domain Model V1, source code, expected answers,
authority terminology, or implementation documentation. A separate fresh
evaluator compared the answers against the pre-registered criteria.

| Criterion | Result |
|---|---:|
| Q5: recommendation and tradeoff understood | 10/10 |
| Q6: Book 2 choice remains non-canonical and requires later acceptance | 10/10 |

The evaluator classified the regression as PASS. All ten contexts understood
that selecting an option records what to explore next; none treated the
selection as Book 2 canon or as accepted Book 2 Direction. This confirms that
the implemented wording preserves the prior Variant B result. It does not
establish that real beginners will respond the same way.

The source experiment and its limitations remain recorded in
[the synthetic wording experiment](../product-validation/series-vertical-slice-v1-synthetic-wording-experiment.md).

## Source qualification

Workspace preflight verified the isolated linked worktree, exact HEAD, and
repository topology before qualification. The exact-candidate source command
was:

```powershell
$env:PYTHONPATH = 'H:\GithubRepositories\auteur\.worktrees\series-vertical-slice-v1-qualification-wording;H:\GithubRepositories\auteur\.worktrees\series-vertical-slice-v1-qualification-wording\src'
& 'C:\Python314\python.exe' scripts/release_evidence.py --skip-wheel
```

The structured suite reported:

| Category | Count |
|---|---:|
| collected | 4,421 |
| passed | 4,393 |
| skipped | 1 |
| xfailed | 27 |
| xpassed | 0 |
| failed | 0 |
| errors | 0 |

The evidence reconciled successfully and reported `QUALIFICATION EVIDENCE
GREEN`.

The focused seven-file matrix was also run in parallel:

```text
156 passed in 24.52s
```

The files were:

```text
tests/test_series_vertical_slice_cli.py
tests/test_series_vertical_slice_e2e.py
tests/test_series_vertical_slice_models.py
tests/test_series_vertical_slice_service.py
tests/test_provenance_pilot.py
tests/test_story_state_commands.py
tests/test_story_state_manager.py
```

## Artifact qualification

The exact candidate was built and tested from an isolated installed
environment using:

```powershell
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
& 'C:\Python314\python.exe' scripts/verify_wheel.py
```

The result was:

```text
wheel: auteur-0.37.1-py3-none-any.whl
SHA-256: 530bdcb20d59ac6c3fd19641fd2423d4faf54d444ac5b0c2056237c390d6f738
installed qualification checks: 11 passed
```

The installed matrix passed import/version, package contents, inspection,
recommendation, restart durability, pre-acceptance immutability, explicit
acceptance, restart persistence, version/hash persistence, and genre
validation/diagnosis.

## Classification and boundary

| Finding | Classification |
|---|---|
| The required Focus clarification is present in the exact candidate. | No consequential issue |
| Existing authority and state semantics remain unchanged under the full suite. | No consequential issue |
| The ten-context Q5/Q6 regression passed. | Synthetic comprehension evidence |
| Real beginner comprehension and naturalness remain unknown. | Product-design uncertainty requiring human validation |
| Finite extent, repeated multi-Book progression, and contraction/expansion remain unimplemented. | Missing V1 capability outside this change |
| No source, service, persistence, or authority defect was found in this change. | No implementation defect observed |
| No contradiction requiring reopening ADR 069 or Domain Model V1 was found. | No product-design contradiction observed |

The earlier Variant B wording decision is therefore implemented and
qualified as a narrow presentation clarification. It does not justify
reopening the bounded-action model, adding free-form Book 2 authoring, or
generalizing the Series architecture.

## Remaining human uncertainty

Only a real participant can establish whether a creative beginner:

- notices and trusts the distinction without facilitator explanation;
- understands what later acceptance means in their own words;
- experiences the wording as reassuring rather than defensive or confusing;
- still perceives a useful creative next decision; and
- can use the broader Map/Focus journey without CLI or synthetic-context
  artifacts masking other problems.

The prepared [human validation package](../product-validation/series-vertical-slice-v1-user-validation.md)
remains the next legitimate product-validation step.
