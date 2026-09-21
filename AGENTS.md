# Agent Instructions For Auteur

Auteur is becoming a whole-story structure engine first and a chapter drafting
engine second. Agent work should preserve that distinction.

For unsupervised/factory runs, `MISSION.md` (scope, out-of-scope-forever, hard
invariants) and `FACTORY_RULES.md` (unsupervised behavior rules) are the
governing documents and sit on the protected list.

## Core rules

1. **Infer within the delegation envelope; escalate material ambiguity.** Once a
   human has authorized a goal, accepted design/specification, and constraints,
   proceed autonomously on low-level implementation choices that preserve that
   envelope. Do not ask for approval on routine naming, helper placement, local
   refactoring, test organization, or behaviorally equivalent algorithms.
2. **Simplest solution first.** Always implement the simplest thing that could
   work. Do not add abstractions or flexibility that were not explicitly
   requested or required by the authorized behavior.
3. **Don't touch unrelated code.** If a file or function is not directly part
   of the current task, do not modify it, even if you think it could be
   improved.
4. **Flag material uncertainty explicitly.** Investigate routine technical
   uncertainty yourself. Stop only when the unresolved uncertainty would change
   product intent, architecture, authority, security, compatibility, external
   effects, or authorized scope.

## Process

- For conceptual design, use a grilling workflow: ask one question at a time,
  give a recommended answer, and wait for approval before locking owner-reserved
  decisions.
- After the work package/design is approved, execute continuously without
  human-in-loop pauses for low-level implementation choices unless a stop
  condition below is reached.
- Blame process, not people. If work drifts, add a clearer checkpoint,
  document the decision earlier, or improve the verification path.
- Capture approved conceptual decisions in `docs/` before implementing schema,
  analyzer, CLI, or pipeline behavior.
- Prefer updating an existing authoritative document over creating a new durable
  document. Create a new durable document only when it has a distinct long-lived
  role that cannot be represented clearly in an existing mission, PRD, status,
  roadmap, ADR, design, guide, or evidence surface. Do not create session-only
  meta-documents merely to restate information already preserved elsewhere.
- Keep user-authorial choices explicit. Do not silently fill or rewrite the
  story spine.
- Treat workspace identity as a preflight condition, not something the
  executor should discover or repair after work begins.

### Delegation envelope

The initial human prompt, accepted design/specification, repository hard
invariants, and explicit constraints define the delegation envelope.

Inside that envelope, the coding agent owns decisions such as:

- internal function and variable naming;
- helper extraction and local refactoring needed to implement the goal cleanly;
- behaviorally equivalent implementation algorithms;
- test fixture and focused regression-test organization;
- L1 focused-test selection;
- whether a named changed boundary justifies targeted L2 validation;
- local error-handling mechanics consistent with existing public semantics;
- internal data flow and commit decomposition;
- minor documentation updates that describe the implemented behavior;
- removal of dead ends introduced by the current work package.

These decisions do not require repeated human approval.

### Consuming strategic-analysis artifacts

A strategic analysis describes the decision space; it does not automatically
authorize every construction path, transition, candidate responsibility, or
future capability it identifies.

When the governing analysis disposition is `INVESTIGATE`, `DEFER`, `STOP`,
`NO_CHANGE`, or another evidence/authority-limited state, a later broad
instruction such as "implement all tasks" applies only to responsibilities that
are both executable and already authorized within the delegation envelope.
Candidate paths, future transitions, evidence-gated features, and owner-reserved
choices remain unselected until the required evidence or explicit authority
selects them.

If strategic analysis separates independent lanes, preserve that separation.
For example, already-authorized behavior-preserving maintenance may continue
while a product-direction lane waits for human or external evidence. Do not
manufacture the missing evidence merely to keep implementation moving.

For incremental maintainability programs, repository size or file length alone
is not sufficient admission evidence for another refactor. Continue
decomposition only when another concrete existing responsibility can be
extracted behavior-preservingly, behind stable public/authority semantics, with
focused regression evidence. When no such responsibility is presently
warranted, stopping the decomposition is a valid outcome.

In shorthand:

```text
strategic path != implementation authority
broad execution request != selection of every candidate
maintenance authorization != product-direction authorization
large file != automatic refactor responsibility
```

### Owner-reserved decisions and stop conditions

Stop and escalate only when continuing requires a material decision about:

- product intent or user-visible semantics not implied by the authorized goal;
- canonical narrative meaning or Layer 1 author commitments;
- semantic architecture or ownership boundaries;
- public compatibility contracts;
- destructive or irreversible data migration;
- security, credentials, privacy, or new external data transmission;
- deployment, publication, or release authorization;
- permanent product-scope constraints;
- material scope expansion beyond the authorized work package;
- changing a hard invariant in `MISSION.md`;
- contradictory requirements that cannot be resolved from current sources of truth.

Also stop when repeated focused attempts indicate the approved design is wrong
rather than merely incomplete, or when cheap validation cannot establish
reasonable confidence in the changed behavior.

Routine uncertainty about naming, helper placement, fixture structure, or
other equivalent implementation mechanics is not a stop condition.

### Code Review & Verification

When reviewing code changes or investigating test failures:

1. **Distinguish issue types before acting:**
   - **Code defect:** Tests fail, tests contradict source inspection, behavior violates invariants
   - **Incomplete requirements:** Feature partially implemented, edge cases unhandled
   - **Environment issue:** Tests pass, source is correct, manual behavior differs (stale package, PATH, Python version mismatch)
   - **Design preference:** Works as intended, but stakeholder wants different tradeoff

2. **Verify claims with evidence:**
   - Don't cite line numbers without inspecting them
   - Don't claim missing components without checking current git HEAD
   - Distinguish between "tests pass" (exercises live code) and "implementation exists in git" (requires committed files)
   - Investigate ordinary uncertainty before escalating it

3. **Investigate environment issues before rewriting:**
   - Multiple Python installations can coexist; verify `which python` and `python -m module`
   - Editable installs (`pip install -e .`) can become stale; verify import paths
   - Shell executables resolve from PATH; use `which` or equivalent to check resolution order
   - When manual test fails but automated tests pass: investigate execution environment, not code

4. **Regression tests protect invariants, not environments:**
   - Can't prevent environment issues (stale packages, PATH misconfiguration)
   - Can enforce repository behavior (e.g., "session storage must use neutral paths")
   - Add regression test when you discover an invariant was silently violated by code changes

### Workspace and repository identity

Treat these as distinct, because they can diverge silently:

- agent/session workspace root;
- Git repository;
- Git branch;
- linked Git worktree;
- standalone clone.

Before work whose correctness depends on repository identity or isolation:

1. Verify the workspace root with `git rev-parse --show-toplevel`.
2. Verify the Git common directory with `git rev-parse --git-common-dir`.
3. Verify the exact HEAD with `git rev-parse HEAD`.
4. Determine whether the checkout is a standalone repository or a linked
   worktree before changing branches, creating worktrees, or moving work.
   Path location does not determine isolation; `.git` topology does.

A branch switch does not change repositories. A shell `cd` does not
necessarily change the coding-agent session workspace. A linked worktree
shares the originating repository's Git object/ref universe; a standalone
clone has its own.

If the task requires a different repository or an isolated Git universe,
configure that repository as the agent workspace before creating the
execution session. Do not start in one repository and repair the workspace
mid-session.

When terminology such as "workspace", "repo", "branch", or "worktree" is
ambiguous, inspect first; escalate only if the ambiguity is material after
inspection.

See `docs/agents/workspace-isolation.md` for the detailed procedure and
`scripts/verify-agent-workspace.ps1` for a machine-checkable preflight.

### Concurrent-main reconciliation

When more than one agent or workspace can modify the repository, treat
integration currentness as a separate check from branch correctness:

1. Before opening or merging a PR, re-read current `main` and the open PR set.
2. Check whether another package already implemented, renamed, or overlaps the
   responsibility you are carrying.
3. A green exact head on an obsolete base is valid evidence for that head, but
   it is not sufficient evidence that the work is integration-ready.
4. If `main` advanced and the branch is no longer cleanly integrable, reconcile
   the smallest bounded change onto contemporary `main` and validate that new
   exact head. Do not force stale history across independently merged work.
5. If concurrent work already satisfies the responsibility, consume it rather
   than duplicate it. Preserve public/authority semantics and close or supersede
   the redundant branch explicitly.
6. Session completion requires no hidden session-owned branch or PR. Remaining
   repository responsibilities may stay open when they are explicitly tracked;
   a complete session is not a claim that the repository is complete.

## Validation budget

Follow `docs/engineering/release-qualification.md`.

- **L1 focused validation is the default.** Run it freely during implementation.
- **L2 targeted integration requires a named changed boundary or risk.** Select
  the smallest useful integration slice and record the reason.
- **L3 full regression requires an explicit milestone, stabilization, recovery,
  cross-cutting-risk, or release-candidate trigger.** Do not use the full suite
  as an inner debugging loop.
- **Release qualification requires an explicitly selected frozen candidate.**
  Do not run exact-SHA release qualification for ordinary development commits.

More testing is not automatically safer when it does not change a decision.
Do not spend expensive validation merely because it exists.

## Qualification and release evidence

For candidate qualification and releases, follow
`docs/engineering/release-qualification.md`.

Mandatory rules:

1. Never call work "fully repaired," "qualified," "merge-ready," or
   "release-ready" before the corresponding evidence gate is complete.
2. Record the exact candidate SHA before qualification.
3. Any source, test, version, packaging, or packaged-resource change
   invalidates downstream release evidence and requires qualification from the
   new SHA.
4. Report pytest categories separately: collected, passed, skipped,
   xfailed, xpassed, failed, and errors when making full-suite/qualification claims.
5. A timed-out or terminated command is incomplete evidence.
6. Compare required-check failures against the baseline before calling them
   pre-existing.
7. Build and installed-test artifacts from the exact frozen release SHA.
8. Publication requires explicit authorization separate from qualification.
9. Preserve author authority: any Layer 1 mutation requires explicit author
   action, atomic persistence, and auditable provenance.

### Baseline failure policy

Checks like `scripts/check.py` (third-party validator tooling, not Auteur
product code) may fail identically on baseline and candidate. Classify as:

- **REGRESSION**: fails on candidate, passes on baseline → BLOCK
- **KNOWN BASELINE FAILURE**: fails identically on both → proceed if
  candidate does not touch the affected boundary
- **SHIFTED FAILURE**: different failure shape or count → INVESTIGATE

Never report a known baseline failure as passing. Never block a release on
a baseline-identical failure unless its shape changed.

## Completion language

Use evidence-bounded language:

- "implemented" means the code exists
- "focused tests pass" means only the named L1 tests passed
- "targeted integration passes" means only the named L2 boundary tests passed
- "regression checkpoint passes" means an explicitly triggered L3 suite passed
  at the recorded SHA/environment
- "source-qualified" means the complete release source gate passed
- "artifact-qualified" means the exact built artifact passed installed testing
- "release-ready" means publication prerequisites are complete
- "published" means remote state has been verified

Do not use these terms interchangeably or promote a lower-level claim because
higher-level validation would be inconvenient.

## Semantic architecture

`docs/narrative-architecture.md` is the sole authority for semantic layer
names, count, ownership, and boundaries.

The canonical model defines five semantic layers (0: Ontology, 1: Identity,
2: Structure, 3: Realization, 4: Expression) and five scope containers
(Universe, Series, Book, Chapter, Scene). Scopes are not layers.

Root agent files may summarize but must not define competing layer models.
When a summary conflicts with the canonical document, the canonical document
wins.

Do not conflate gaps across layers. A narrative engine gap (e.g., missing
subgenre validation) is not fixed by improving the drafting pipeline.

## Structure Engine

- Treat global constraints as first-class: target experience, genre/subgenre
  hierarchy, mode, medium, scope, and scale.
- Keep the whole-story engine explicit: main thread plus subordinate threads,
  each with want, resistance, conflict, stakes, change, and thematic function.
- Separate parseable schema from narrative diagnostics:
  - Pydantic models answer whether a blueprint is shaped correctly.
  - `auteur.structure` analyzers answer whether it is complete or coherent.
- Prefer proposal and report artifacts over direct blueprint mutation.
- Structure generation/diagnosis operates in the whole-story Narrative Engine
  scope only. Do not generate or diagnose chapter outlines or prose structure
  unless the task explicitly crosses the scope boundary.

## Implementation

- Use TDD for schema, analyzer, CLI, and pipeline behavior changes.
- For docs-only changes, verify the touched files and run tests when the docs
  describe behavior that tests can cover.
- Do not add LLM calls to deterministic structure analysis.
- Keep early analyzer rules narrow and explainable. Avoid broad quality claims
  like "this is a good story."

## Agent skills

### Issue tracker

Issues live in GitHub Issues for `ThorStarlord/auteur`. See
`docs/agents/issue-tracker.md`.

### Triage labels

Use the default five-label triage vocabulary. See
`docs/agents/triage-labels.md`.

### Domain docs

Single-context repo: read root `CONTEXT.md` and `docs/adr/` when they exist.
See `docs/agents/domain.md`.
