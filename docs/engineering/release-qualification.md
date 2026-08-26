# Release Qualification and Evidence Policy

## Principle

Blame processes, not people.

A completion claim is not evidence. A release state is reached only when
its required artifacts and checks exist.

## Release states

### Implemented
- Product changes committed
- Focused tests pass
- Scope reviewed

### Candidate Frozen
- Working tree clean
- Full candidate SHA recorded
- No source, test, version, or packaged-resource changes after freeze

### Source Qualified
- Required repository checks accounted for
- Targeted tests pass
- Serial suite reconciles
- Parallel suite reconciles
- Expected skips and xfails recorded separately
- No unexpected xpasses

### Artifact Qualified
- Artifact built from frozen candidate SHA
- Artifact hash recorded
- Fresh external environment created
- Installed import path resolves from site-packages
- Public workflow matrix passes

### Release Ready
- Version finalized
- Release notes finalized
- Exact release invariant satisfied
- Remote state inspected
- Publication authorization received

### Published
- Main pushed
- Annotated tag pushed
- GitHub Release created
- Remote invariant verified
- Registry and asset publication status explicitly recorded

## Candidate invalidation rule

Any change to source code, tests, version metadata, package resources, or
build configuration creates a new candidate SHA and invalidates downstream
qualification evidence.

Documentation-only commits may be distinguished from the qualified product
commit only when the documentation is not packaged and the distinction is
explicitly recorded.

## Exact release invariant

For a final release:

```
source-qualified commit
= artifact-built-from commit
= installed-qualified commit
= final release HEAD
= tag peeled commit
```

## Test accounting

Never report "all tests passed" when the suite includes skips or expected
failures.

Report:

- collected
- passed
- skipped
- xfailed
- xpassed
- failed
- errors

The arithmetic must reconcile.

## Baseline-failure policy

- Candidate passes, baseline passes: PASS
- Candidate fails, baseline passes: REGRESSION
- Candidate and baseline fail identically: KNOWN BASELINE FAILURE
- Failure identity differs: INVESTIGATE

A known baseline failure may be non-blocking only when its exact identity
is recorded and release policy permits it.

## Long-running commands

Long test runs must expose progress through terminal output, a growing log,
a heartbeat, or JUnit XML.

A timeout means the run is incomplete, not failed and not passed.

Do not pipe all progress through a filter that only emits the final summary.

## Publication boundary

Source release, artifact attachment, and package-registry publication are
separate authorization decisions.

## Pull-request merge qualification

A merge requires sufficient qualification evidence for the behavioral risk
introduced by the change.

### Code-bearing changes

Changes to source code, tests, version metadata, packaged resources, or build
configuration normally require successful CI on the exact pull-request head
before merge.

An explicitly recorded equivalent complete qualification may substitute for
remote CI when:

- it qualifies the exact candidate being merged;
- all required repository and artifact checks completed successfully; and
- no candidate-invalidating change occurred afterward.

If the complete local qualification is incomplete — including timeout,
interruption, or unavailable environment — successful exact-head CI is required.

A missing CI run is not a passing CI run.

### Documentation/evidence-only changes

A documentation-only or evidence-only change may merge without CI when:

- executable behavior is demonstrably unchanged;
- the qualified product candidate remains unchanged;
- relevant repository/document validation passes; and
- the absence of CI is explicitly recorded rather than represented as a pass.

Where qualification uses an evidence-only publication commit after a qualified
candidate, the source/test distinction must be explicit and mechanically
verifiable.

### Post-merge CI

Post-merge CI is useful additional evidence, but it does not retroactively
satisfy a pre-merge CI requirement.

If pre-merge CI was mandatory for the change, it must pass before merge.

### Enforcement

Repository settings may enforce some or all of these rules mechanically.
Where GitHub does not enforce them, they remain project policy and must be
enforced by the publication workflow.
