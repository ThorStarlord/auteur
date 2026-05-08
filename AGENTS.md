# Agent Instructions For Auteur

Auteur is becoming a whole-story structure engine first and a chapter drafting
engine second. Agent work should preserve that distinction.

## Process

- For conceptual design, use a grilling workflow: ask one question at a time,
  give a recommended answer, and wait for approval before locking decisions.
- Blame process, not people. If work drifts, add a clearer checkpoint,
  document the decision earlier, or improve the verification path.
- Capture approved conceptual decisions in `docs/` before implementing schema,
  analyzer, CLI, or pipeline behavior.
- Keep user-authorial choices explicit. Do not silently fill or rewrite the
  story spine.

## Structure Engine

- Treat global constraints as first-class: target experience, genre/subgenre
  hierarchy, mode, medium, scope, and scale.
- Keep the whole-story engine explicit: main thread plus subordinate threads,
  each with want, resistance, conflict, stakes, change, and thematic function.
- Separate parseable schema from narrative diagnostics:
  - Pydantic models answer whether a blueprint is shaped correctly.
  - `auteur.structure` analyzers answer whether it is complete or coherent.
- Prefer proposal and report artifacts over direct blueprint mutation.
- Keep structure generation/diagnosis separate from chapter drafting unless the
  task explicitly asks to integrate them.

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
