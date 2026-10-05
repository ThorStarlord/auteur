# Release Qualification and Evidence Policy

## Principle

Blame processes, not people.

A completion claim is not evidence. Validation cost should scale with the
claim being made, the changed boundary, and the lifecycle stage.

The default question during development is not "what is the maximum evidence
we can collect?" It is "what is the cheapest evidence that can falsify the
claim being made now?"

Development validation and release qualification are separate activities.

## Local-first validation policy

Local validation is the default source of development evidence. GitHub Actions
is optional remote execution, not a dependency for ordinary development.
Automatic hosted-runner execution must not be required to continue work, open
or review ordinary pull requests, or preserve development momentum.

When GitHub Actions is unavailable because of quota, billing limits, outage, or
a deliberate cost-control decision:

- continue development with local L1 and justified L2 validation;
- record the exact candidate SHA, commands, environment, and results in the PR
  or work log;
- do not weaken the required evidence or promote the claim merely because a
  hosted runner is unavailable;
- run an explicitly triggered L3 checkpoint locally when the available local
  environment can satisfy that checkpoint;
- treat release qualification as incomplete when required platform-specific or
  independent evidence cannot be reproduced locally.

Hosted Actions may be manually dispatched when remote, independent, or
platform-specific evidence is decision-relevant and worth the cost. Exhausted
hosted-runner credits may block a higher qualification claim, but they must not
block ordinary implementation work.

## Development validation levels

### L1 — Focused validation

L1 is the default implementation feedback loop and the ordinary development
gate. It is normally run locally on the exact working or pull-request head.

Typical L1 evidence includes:

- new or changed unit tests;
- regression tests for the exact defect or invariant being modified;
- nearby deterministic contract tests;
- repository validators, Ruff, syntax, or import checks when cheap.

The coding agent may select and run L1 autonomously. L1 should remain small
enough to run repeatedly while implementing a work package.

When a shared compatibility facade or orchestration boundary changes, focused
validation should fan out to the regression suites for the behavioral
responsibilities reachable through that boundary. Test selection should follow
behavioral ownership, not only directly changed test filenames. Keep that
fan-out bounded to responsibilities actually reachable through the changed
boundary.

Passing L1 supports claims such as `implemented` and `focused tests pass`.
It does not support `source-qualified`, `artifact-qualified`, or
`release-ready`.

### L2 — Targeted integration validation

L2 verifies a named boundary or multi-component acceptance criterion. It is
evidence-triggered, not automatic.

Before running L2, record the changed boundary or risk in one sentence. Valid
reasons include persistence/serialization changes, CLI-to-service changes,
authority handoffs, provider/adapter changes, changed contracts with multiple
consumers, or a defect that occurred specifically at an integration boundary.

Select the smallest useful integration slice. If no concrete boundary or risk
can be named, defer L2 by default.

### L3 — Full regression validation

L3 is the complete repository regression suite for a stabilization target. It
is a checkpoint tool, not an inner development-loop tool.

Valid triggers include:

- an explicit milestone or stabilization checkpoint;
- recovery from a known repository-wide regression;
- a cross-cutting change whose blast radius cannot be bounded cheaply;
- freezing a release candidate;
- an explicit maintainer request for repository-wide confidence.

Routine commits and ordinary pull requests are not L3 triggers by themselves.
When L3 fails, return to focused L1/L2 debugging and rerun L3 only when a
checkpoint rerun is justified.

## Release qualification is separate from L3

Release qualification applies to an explicitly selected frozen candidate SHA.
It may include:

- L3 source regression evidence;
- the supported Python/platform compatibility matrix;
- repository validators;
- installed-wheel qualification;
- exact-SHA evidence;
- version and release-note consistency;
- publication invariant checks;
- explicitly required manual acceptance.

The canonical durable evidence producer is `scripts/release_evidence.py`. It
runs the Python 3.12 source suite and installed-wheel qualification for the
exact checked-out candidate. The release workflow adds the remaining supported
compatibility environments without duplicating that Python 3.12/wheel work.

A normal push to `main` is a development integration event. It does not
implicitly freeze a release candidate and must not automatically trigger
release qualification.

## Release states

### Implemented
- Product changes committed
- Appropriate L1 focused tests pass
- Scope reviewed

### Regression Checkpoint Passed
- An explicit L3 trigger is recorded
- Full regression suite passed at the recorded SHA/environment
- Result is checkpoint evidence, not release qualification

### Candidate Frozen
- Working tree clean
- Full candidate SHA recorded
- No source, test, version, packaged-resource, or build changes after freeze

### Source Qualified
- Required release source environments completed
- Test accounting reconciles
- Expected skips and xfails recorded separately
- No unexpected xpasses
- Any baseline failures classified explicitly

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

A known baseline failure may be non-blocking only when its exact identity is
recorded and the applicable policy permits it.

## Long-running commands

Long test runs must expose progress through terminal output, a growing log, a
heartbeat, or JUnit XML.

A timeout means the run is incomplete, not failed and not passed.

Do not pipe all progress through a filter that only emits the final summary.

## Publication boundary

Source release, artifact attachment, and package-registry publication are
separate authorization decisions.

## Pull-request merge validation

A merge requires sufficient evidence for the behavioral risk introduced by the
change. Evidence is risk-tiered; it is not maximized automatically.

### Code-bearing changes

Ordinary implementation changes use L1 focused validation on the exact
pull-request head. Local exact-head evidence is first-class merge evidence when
the command, environment, SHA, and result are recorded. The optional remote
Validation workflow may reproduce the same focused gate when independent hosted
evidence is useful, but a GitHub Actions run is not required merely because a
pull request exists.

L2 is added only when a named changed boundary or integration risk justifies
it. The PR or work log should state that reason and name the selected tests.

L3 is not an ordinary PR requirement. A CI/governance or architecture change
may itself justify extra review, but that does not automatically require the
entire product regression suite. Use the explicit stabilization workflow when
an L3 trigger exists.

A missing required L1/L2 run is not a passing run. Absence of a GitHub Actions
run is not missing evidence when the required L1/L2 evidence was produced
locally and recorded against the exact head. A timed-out or interrupted run is
incomplete evidence.

### Documentation/evidence-only changes

A documentation-only or evidence-only change may merge without product tests
when:

- executable behavior is demonstrably unchanged;
- relevant repository/document validation passes; and
- the absence of product tests is recorded rather than represented as a pass.

Where qualification uses an evidence-only publication commit after a qualified
candidate, the source/test distinction must be explicit and mechanically
verifiable.

## `main` lifecycle semantics

`main` represents the latest stable development state. It is not required to
be continuously artifact-qualified or release-ready.

A push to `main` receives bounded development validation. Release qualification
occurs only after an exact candidate has been explicitly selected for that
purpose.

This does not permit knowingly merging red focused evidence. Known L1/L2
regressions must be fixed or explicitly classified before integration.

## Explicit stabilization

The repository-wide L3 checkpoint is explicit rather than automatic. It may be
run locally or through the manual (`workflow_dispatch`) `Stabilization`
workflow. Either path must record the exact SHA and the milestone, recovery,
cross-cutting-risk, or release-candidate trigger that justified the cost.

## Explicit release qualification

The `Release Qualification` workflow is optional hosted execution. When used,
it is manual (`workflow_dispatch`), requires an exact `candidate_sha`, checks
out that SHA explicitly, and fails if the tested checkout does not match the
requested candidate.

The same qualification may be assembled locally only when the required exact-SHA
source, installed-artifact, and supported-platform evidence is actually run and
recorded. If the available machine cannot reproduce a required platform matrix,
the correct result is **qualification incomplete**, not a weaker release gate.
Moving hosted execution out of ordinary development changes *where and when*
the cost is paid, not the strength of the release boundary.

## Post-merge validation

Automatic post-merge GitHub Actions is not required. Optional remote validation
is useful additional evidence when deliberately dispatched, but it does not
retroactively satisfy a required pre-merge L1/L2 gate.

Likewise, a passing local or remote development gate does not imply that an L3
checkpoint or release qualification has occurred.

## Enforcement

Repository settings may enforce some or all of these rules mechanically.
Where GitHub does not enforce them, they remain project policy and must be
enforced by recorded local evidence and, when deliberately used, the
stabilization and publication workflows.
