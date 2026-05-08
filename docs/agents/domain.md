# Domain Docs

How engineering skills should consume this repo's domain documentation when
exploring the codebase.

## Layout

This is a single-context repo.

Read these files when they exist:

- `CONTEXT.md` at the repo root
- `docs/adr/` for architectural decisions that touch the area being changed

If these files do not exist, proceed silently. Do not suggest creating them
upfront; producer workflows should create them when project terms or decisions
need to be captured.

## Vocabulary

When output names a domain concept in an issue title, refactor proposal,
hypothesis, or test name, use the term as defined in `CONTEXT.md`.

If the needed concept is not in the glossary yet, treat that as a signal to
either reconsider the wording or note a documentation gap for a future
conceptual pass.

## ADR Conflicts

If output contradicts an existing ADR, surface the conflict explicitly rather
than silently overriding it.
