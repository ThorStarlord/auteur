# Agent Instructions For Auteur

Auteur is becoming a whole-story structure engine first and a chapter drafting
engine second. Agent work should preserve that distinction.

## Core rules

1. **Ask, don't assume.** If something is unclear, ask before writing a single
   line. Never make silent assumptions about intent, architecture, or
   requirements.
2. **Simplest solution first.** Always implement the simplest thing that could
   work. Do not add abstractions or flexibility that were not explicitly
   requested.
3. **Don't touch unrelated code.** If a file or function is not directly part
   of the current task, do not modify it, even if you think it could be
   improved.
4. **Flag uncertainty explicitly.** If you are not confident about an approach
   or technical detail, say so before proceeding. Confidence without certainty
   causes more damage than admitting a gap.

## Process

- For conceptual design, use a grilling workflow: ask one question at a time,
  give a recommended answer, and wait for approval before locking decisions.
- Blame process, not people. If work drifts, add a clearer checkpoint,
  document the decision earlier, or improve the verification path.
- Capture approved conceptual decisions in `docs/` before implementing schema,
  analyzer, CLI, or pipeline behavior.
- Keep user-authorial choices explicit. Do not silently fill or rewrite the
  story spine.
- Treat workspace identity as a preflight condition, not something the
  executor should discover or repair after work begins.

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
   - If uncertain, ask or investigate further rather than escalating

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
ambiguous, inspect first and ask rather than choosing an interpretation.

See `docs/agents/workspace-isolation.md` for the detailed procedure and
`scripts/verify-agent-workspace.ps1` for a machine-checkable preflight.

## Qualification and release evidence

For candidate qualification and releases, follow
`docs/engineering/release-qualification.md`.

Mandatory rules:

1. Never call work "fully repaired," "qualified," "merge-ready," or
   "release-ready" before the corresponding evidence gate is complete.
2. Record the exact candidate SHA before qualification.
3. Any source, test, version, packaging, or packaged-resource change
   invalidates downstream evidence and requires qualification from the new
   SHA.
4. Report pytest categories separately: collected, passed, skipped,
   xfailed, xpassed, failed, and errors.
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
- "focused tests pass" means only the named tests passed
- "source-qualified" means the complete source gate passed
- "artifact-qualified" means the exact built artifact passed installed testing
- "release-ready" means publication prerequisites are complete
- "published" means remote state has been verified

Do not use these terms interchangeably.

## Semantic architecture

`docs/narrative-architecture.md` is the sole authority for semantic layer
names, count, ownership, and boundaries.

The canonical model defines five semantic layers (0: Ontology, 1: Identity,
2: Structure, 3: Realization, 4: Expression) and five scope containers
(Universe, Series, Book, Chapter, Scene). Scopes are not layers.

Root agent files may summarize but must not define competing layer models.
When a summary conflicts with the canonical document, the canonical
document wins.

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
