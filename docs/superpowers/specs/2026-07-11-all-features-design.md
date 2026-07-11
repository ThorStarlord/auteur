# All Discussed Features Design

## Scope

Implement accepted genre, Story Discovery, Series, Universe, Genre Guide,
round-trip, editing, and durable-artifact behavior, plus session history,
warning acknowledgment, health readiness, standalone Universe/Book builders,
and dependency-graph visualization.

## Decisions

- Existing StoryIdentity, SeriesIdentity, and UniverseIdentity remain canonical.
- Session diagnostics are replace-on-success and persisted atomically.
- `/health` is a read-only readiness endpoint.
- Builders are deterministic model-to-artifact transforms with no LLM calls.
- Graph visualization is Mermaid text beside the existing YAML graph.
- Legacy sessions remain explicitly rejected rather than auto-migrated.

## Verification

Every behavior has a failing pytest first, then a minimal implementation,
focused verification, and full-suite verification.
