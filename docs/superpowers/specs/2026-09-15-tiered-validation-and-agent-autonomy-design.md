# Tiered Validation and Bounded Agent Autonomy Design

**Date:** 2026-09-15  
**Status:** Proposed, human-authorized design awaiting implementation  
**Repository:** `ThorStarlord/auteur`

## Purpose

Auteur is an actively developed product with a large regression suite and a strong release-qualification discipline. The current process correctly values evidence, but development feedback and release qualification are still too tightly coupled. Ordinary implementation work can trigger thousands of tests, cross-platform execution, packaging checks, and release evidence even when the changed behavior is local. That raises iteration cost and makes testing itself a product-development bottleneck.

This design separates four concerns:

1. fast implementation feedback;
2. targeted boundary validation;
3. full regression validation at explicit stabilization checkpoints;
4. release qualification of an exact frozen candidate.

It also replaces approval-per-detail agent behavior with bounded implementation autonomy. Once a human authorizes a goal and constraints, the coding agent owns low-level implementation decisions inside that delegation envelope and escalates only material ambiguity.

The objective is not to test less carelessly. The objective is to spend evidence cost where it changes a decision.

## Goals

- Keep the normal coding loop fast enough for sustained agentic development.
- Preserve or improve confidence in changed behavior.
- Require an explicit reason before running broader integration validation.
- Remove the full regression suite from the ordinary implementation loop.
- Keep exact-SHA release qualification separate from development validation.
- Preserve author authority, canonical narrative invariants, compatibility, and publication boundaries.
- Give coding agents authority over low-level implementation after initial task authorization.
- Make escalation triggers explicit so agents do not ask for approval on routine engineering choices.
- Make completion claims evidence-bounded rather than test-maximalist.

## Non-goals

- Weakening tests to make failures disappear.
- Deleting regression coverage simply because it is expensive.
- Allowing implementation agents to redefine product intent, semantic architecture, author authority, security boundaries, or release policy without human authorization.
- Making `main` continuously release-qualified.
- Treating manual author acceptance as interchangeable with automated regression evidence.
- Treating every integration test as expensive or every unit test as cheap; cost, scope, and risk all matter.

## Core principle

Validation cost should scale with behavioral risk, changed boundaries, and lifecycle stage.

The default question is not "what is the maximum evidence we can collect?" It is "what is the cheapest evidence that can falsify the claim being made at this stage?"

## Validation model

### L1 — Focused validation

**Purpose:** immediate implementation feedback.

L1 is the default validation level during coding and may run frequently.

Typical evidence:

- new or changed unit tests;
- regression tests for the exact defect or invariant being modified;
- nearby contract tests whose scope is small and deterministic;
- syntax/import checks;
- narrowly scoped lint/static validation where cheap.

L1 should usually complete in seconds. The coding agent may select and run L1 autonomously.

Passing L1 supports only claims such as:

- implemented;
- focused tests pass;
- named invariant regression is covered.

Passing L1 does not support source-qualified, artifact-qualified, release-ready, or published claims.

### L2 — Targeted integration validation

**Purpose:** verify a changed boundary or multi-component acceptance criterion.

L2 is evidence-triggered, not automatic. Before running it, the coding agent must be able to state the boundary or risk being tested.

Valid triggers include:

- a change crosses a CLI-to-service boundary;
- persistence or serialization behavior changes;
- authority handoff behavior changes;
- two previously independent subsystems are newly connected;
- a reported defect occurred specifically at an integration boundary;
- an acceptance criterion requires multiple components to cooperate;
- a provider/adapter boundary changes;
- a changed data contract has more than one consumer.

An L2 justification should be expressible in one sentence, for example:

> Run `tests/test_structure_revision_cli.py::test_apply_preserves_authority` because this change modifies the CLI-to-revision-application boundary.

If no concrete boundary or risk can be named, defer L2 by default.

L2 should select the smallest useful integration slice. A full subsystem suite is not automatically justified merely because integration tests exist.

### L3 — Full regression validation

**Purpose:** detect unexpected cross-system regressions after a meaningful body of work.

L3 means the complete repository regression suite for the chosen supported environment, not a new category of test. It may include unit, contract, integration, regression, and end-to-end tests.

L3 is not part of the normal implementation loop.

Allowed triggers:

- an explicit milestone/stabilization checkpoint closes;
- a cross-cutting refactor changes a repository-wide contract;
- a suspected global regression cannot be localized cheaply;
- a release candidate is being frozen;
- a maintainer explicitly requests a repository-wide confidence check.

Ordinary implementation commits, routine pull requests, local helpers, copy changes, and narrowly bounded fixes are not L3 triggers by themselves.

A milestone may contain many L1 cycles and some justified L2 runs before one L3 checkpoint.

## Release qualification is not L3

Release qualification is a separate lifecycle activity performed against an exact frozen candidate.

A release candidate may require:

- L3 full regression validation;
- supported Python/platform matrix;
- repository validators;
- artifact build;
- fresh installed-wheel smoke or public workflow validation;
- exact-SHA evidence;
- version/release-note consistency;
- publication invariant checks;
- any explicitly required manual product acceptance.

Candidate invalidation rules remain strict: source, test, version, packaging, packaged-resource, or build-configuration changes create a new candidate and invalidate downstream evidence.

Normal pushes to `main` are development events, not implicit release candidates.

## Development and release lifecycle

```text
AUTHORIZED WORK PACKAGE
        |
        v
implementation <-> L1 focused validation
        |
        +---- changed boundary/risk? ---- yes ----> L2 targeted integration
        |                                  |
        +----------------------------------+
        |
        v
continue building
        |
        v
MILESTONE / STABILIZATION TRIGGER
        |
        v
L3 full regression validation
        |
        v
continue development OR freeze candidate
        |
        v
RELEASE CANDIDATE
        |
        v
exact-SHA release qualification
        |
        v
publication authorization
```

## CI behavior

### Pull requests

Ordinary code-bearing pull requests should default to a cheap development gate:

- L1 focused tests derived from changed behavior/tests;
- repository validators whose runtime is reasonably cheap;
- lint/static checks where cheap;
- a lightweight packaging/import smoke only when the package boundary is affected or when the smoke is sufficiently inexpensive to remain part of the default gate.

A pull request should not run the complete Windows suite or the full supported Python matrix solely because it contains ordinary implementation code.

L2 may be selected when the changed boundary justifies it. The CI or agent should record the reason.

L3 on a pull request requires an explicit L3 trigger, not merely a broad filename class.

### Main

`main` represents the latest stable development state, not a continuously release-qualified artifact.

A push to `main` may run a bounded post-merge confidence check, but exact-SHA release qualification should not run automatically for every development merge.

### Stabilization / release

Full regression and qualification run through explicit stabilization or release workflows. `workflow_dispatch`, a release-candidate branch/tag convention, or an equivalent explicit trigger is appropriate.

The workflow must make the lifecycle state visible: development validation and release qualification must not be visually or semantically conflated.

## Test-budget rule

The repository should encode the following defaults:

```text
Normal implementation iteration:
  L1 only.

L2:
  requires a named boundary/risk justification.

L3:
  prohibited unless an L3 trigger exists.

Release qualification:
  prohibited unless a candidate is explicitly being frozen/qualified.
```

"Prohibited" is intentional. Agents tend to over-test because more testing sounds safer. The repository should require evidence that additional validation cost is decision-relevant.

## Regression-discovery policy

Deferring L3 does not mean deferring known red evidence.

If L1 or justified L2 detects a regression, the agent must fix or explicitly classify it before continuing. The agent must not knowingly accumulate failing focused evidence until the next milestone.

If an L3 checkpoint fails:

1. compare against the most recent known-good L3 baseline;
2. localize the failure to the smallest likely change window;
3. return to focused L1/L2 debugging;
4. rerun L3 only after focused evidence is green and a checkpoint rerun is justified.

This prevents the full suite from becoming the inner debugging loop.

## Manual author testing

Human use of Auteur is first-class product evidence but serves a different purpose from automated tests.

Manual author testing is best described as exploratory testing, dogfooding, or product acceptance testing. It answers questions such as:

- Is the guided workflow understandable?
- Does Tutor guidance help the author make a better decision?
- Does the application feel coherent?
- Is the authority boundary understandable?
- Would the author continue using the product for a real long-form project?

Manual author testing should occur at coherent product milestones, not after every implementation package. Human attention is also a limited validation resource.

Manual acceptance never substitutes for deterministic checks of machine-enforceable invariants.

## Delegated implementation authority

### Principle

Replace "ask, don't assume" as a blanket implementation rule with:

> Infer within the delegation envelope; escalate material ambiguity.

The initial human prompt, accepted design/specification, repository invariants, and explicit constraints form the delegation envelope.

Inside that envelope, the coding agent may proceed without approval for low-level implementation choices.

### Agent-delegated decisions

Unless explicitly constrained, the coding agent owns decisions such as:

- internal function and variable naming;
- helper extraction;
- local refactoring needed to implement the authorized goal cleanly;
- implementation algorithm choice among behaviorally equivalent options;
- test fixture organization;
- focused regression-test selection;
- whether a justified targeted L2 test is needed;
- local error-handling mechanics consistent with existing public semantics;
- internal data flow;
- commit decomposition;
- minor documentation updates that describe the implemented behavior;
- removal of implementation dead ends introduced by the current work package.

The agent does not need approval for each of these decisions.

### Owner-reserved decisions

The agent must stop and escalate when continuing requires a decision that materially changes any of the following:

- product intent or user-visible semantics not implied by the authorized goal;
- canonical narrative meaning or Layer 1 author commitments;
- semantic architecture or ownership boundaries;
- public compatibility contract;
- destructive or irreversible data migration;
- security, credentials, privacy, or new external data transmission;
- external deployment or publication;
- release/publication authorization;
- permanent product-scope constraints;
- material scope expansion beyond the authorized work package;
- an explicit hard invariant in `MISSION.md`;
- contradictory requirements that cannot be resolved from existing sources of truth.

### Stop conditions

The coding agent proceeds autonomously until one of these conditions occurs:

1. requirements materially conflict;
2. a product/architecture decision not implied by the prompt is required;
3. a protected invariant would need to change;
4. a destructive or external action outside the authorization envelope is required;
5. scope expands materially beyond the authorized goal;
6. cheap validation cannot establish reasonable confidence in the changed behavior;
7. repeated focused attempts fail in a way that suggests the original design is wrong rather than merely incomplete.

Routine uncertainty about naming, helper placement, test organization, or equivalent implementation mechanics is not an escalation condition.

## Author authority remains strict

Broader coding-agent authority must not weaken Auteur's author-authority model.

The distinction is explicit:

- **coding authority:** implementation mechanics within an authorized engineering goal;
- **author authority:** canonical narrative commitments and acceptance actions belonging to the human author.

An agent may autonomously implement the mechanism that presents, validates, stores, or applies an author decision. It may not silently make the canonical creative decision on the author's behalf when the product contract requires explicit author action.

## Governance safety

The factory must not gain authority to weaken its own validation or governance rules during an unsupervised run.

Changes to governance, CI policy, protected invariants, or qualification policy remain human-authorized changes. Factory protections that prevent self-modification remain conceptually valid.

This design changes the content of the human-approved policy; it does not remove the separation between governed implementation and governance modification.

## Current regression recovery

The present `main` regression after commit `eb62e6fa23869a0da0e13c47425be0a4dbbc6479` should be the first application of the new model.

Known-good comparison baseline: `1d8b0b459b808e149aeab91c88a877f4f7807beb`.

Recovery sequence:

1. reproduce each currently known failure with the smallest focused test selection;
2. inspect the `HandlerResult` contract before choosing whether to extend its API or change callers;
3. restore expected CLI stderr/error-channel semantics where the public contract requires them;
4. restore repository-specific `.gitignore` safety entries and remove accidental Markdown fences;
5. add or preserve focused regression coverage for each corrected contract;
6. run only the targeted integration slices justified by the changed CLI/workflow boundaries;
7. once focused evidence is green, run one L3 stabilization checkpoint to establish a new known-good repository baseline;
8. do not run exact-SHA release qualification unless the repository is explicitly entering a release-candidate state.

The L3 checkpoint is a recovery/stabilization trigger, not evidence that every ordinary future change must run the full suite.

## Completion language

Completion claims remain evidence-bounded:

- **implemented** — code exists for the authorized behavior;
- **focused tests pass** — named L1 tests passed;
- **targeted integration passes** — named L2 boundary tests passed;
- **regression checkpoint passes** — an explicitly triggered L3 suite passed at the recorded SHA/environment;
- **source-qualified** — the release source gate defined by release policy passed;
- **artifact-qualified** — the exact built artifact passed installed qualification;
- **release-ready** — all publication prerequisites except publication authorization/action are complete;
- **published** — remote publication state was verified.

Do not promote a lower-level claim into a higher-level claim merely because more tests would be inconvenient.

## Expected repository changes during implementation

The implementation plan should minimally reconcile these surfaces:

- `AGENTS.md` — replace blanket approval-per-ambiguity language with bounded implementation autonomy while preserving escalation for material decisions;
- `CLAUDE.md` — align contributor process language and test-budget guidance;
- `docs/engineering/release-qualification.md` — separate L1/L2/L3 development validation from exact-SHA release qualification;
- `.github/workflows/validation.yml` — make ordinary PR validation cheap, remove unconditional Windows full-suite execution, and move L3/release qualification behind explicit triggers;
- release/stabilization workflow configuration — add or adapt an explicit path for L3 and exact-SHA qualification;
- relevant tests/validators for CI-policy selection where the repository has machine-checkable workflow-policy tests;
- current regression files introduced by #228, including the `HandlerResult`/CLI error paths and `.gitignore` safety regression.

`FACTORY_RULES.md` should be changed only if the existing protected-file and self-modification model cannot express the new human-approved delegation envelope without contradiction. If a change is necessary, it remains an explicitly human-authorized governance edit; the unsupervised factory does not modify its own rules.

## Acceptance criteria

The design is implemented when all of the following are true:

1. Ordinary implementation work has a cheap default L1 path.
2. L2 execution requires a named integration boundary or risk.
3. L3 is not automatically run for routine implementation changes.
4. Windows full-suite and the full Python matrix are not unconditional ordinary-PR costs.
5. Exact-SHA release qualification does not run on every ordinary `main` push.
6. A maintainer can explicitly trigger an L3 stabilization checkpoint.
7. A maintainer can explicitly trigger exact-SHA release qualification for a frozen candidate.
8. Coding agents may make low-level implementation decisions without repeated approval after the initial authorized prompt/spec.
9. Owner-reserved decisions and stop conditions remain explicit.
10. Author authority over canonical narrative commitments remains unchanged.
11. Governance/self-modification protections remain intact.
12. The #228 regression is repaired using focused evidence first, justified L2 where appropriate, and one L3 recovery checkpoint after the focused fixes are green.
13. Documentation no longer implies that ordinary development commits are continuously release-qualified.

## Design decision summary

Auteur should optimize the development loop for cheap falsification and optimize the release boundary for strong qualification.

The normal path is **L1 by default, L2 with a reason, L3 at checkpoints, qualification for frozen candidates**.

The normal authority model is **one human authorization for the work package, autonomous low-level implementation within that envelope, escalation only for material decisions**.
