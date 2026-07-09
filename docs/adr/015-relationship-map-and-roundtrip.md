# ADR 015: Relationship Map And Markdown Round-Trip

## Status

Accepted.

## Context

Auteur needs to support author edits made outside the drafting pipeline without
silently corrupting narrative state. Relationship state is also too important to
leave as unstructured prose or incidental Bible text.

## Decision

Relationship state is a canonical project-level state layer stored in
`relations.yaml`. It is separate from blueprint intent and Bible event facts.

Markdown round-trip import/export is a controlled artifact workflow:

- export copies the selected draft for external editing;
- import writes `imported_draft.md`, `diff_report.json`, `drift_report.json`,
  and `canon_update_proposals.yaml`;
- import never mutates `draft_vN.md`, `final.md`, `bible.json`, or
  `relations.yaml`;
- canonical relationship updates go through explicit relation change
  application.

V1 uses explicit `relation_changes.yaml` files for relationship drift. Prose
inference, `.docx`, Google Docs, and Scrivener support are deferred.
