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

## Three layers

Auteur has three distinct layers. Identify which layer a task belongs to
before working — each has its own definition of "complete."

1. **Narrative Engine** (Layers 1-5 + 9): Story identity, genre/medium/scope
   contracts, structural forces, threads, theme. Owned by `auteur identity`,
   `auteur blueprint`, `auteur structure`, `auteur state`. Fully contained in
   the blueprint — no chapter artifacts required.
2. **Chapter Outline Layer** (Layers 6-7): Cartographer outlines, Bible state,
   scene carriers, character state changes. Owned by `auteur cartographer`,
   `auteur plan`.
3. **Prose Drafting Layer** (Layer 8): Chapter prose, TDD critics, iteration
   loops. Owned by `auteur draft`, `auteur accept`, `auteur retry`.

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
