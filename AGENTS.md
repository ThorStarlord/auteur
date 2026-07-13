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

## Semantic architecture

See [docs/narrative-architecture.md](docs/narrative-architecture.md) for the
canonical five-layer model and scope axis.

Auteur has three distinct layers. Identify which layer a task belongs to
before working — each has its own definition of "complete."

1. **Identity and Structure**: Story identity, genre/medium/scope contracts,
   structural forces, threads, theme, and whole-story plans. Owned by
   `auteur identity`, `auteur blueprint`, `auteur structure`, `auteur state`.
   These can be fully represented in the blueprint without chapter artifacts.
2. **Realization**: Cartographer outputs, Bible state, scene events, and
   character state changes. Owned by `auteur cartographer`, `auteur plan`, and
   realization workflows.
3. **Expression**: Chapter prose, TDD critics, and iteration. Expression is
   the fourth semantic layer; critics and iteration are cross-cutting
   validation/orchestration workflows. Owned by `auteur draft`, `auteur accept`,
   `auteur retry`.

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
- Structure generation/diagnosis operates in the Narrative Engine layer only.
  Do not generate or diagnose chapter outlines or prose structure unless the
  task explicitly crosses layers.

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
