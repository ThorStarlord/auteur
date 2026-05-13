# ADR 003: Temporary Placement of bible_audit.py in auteur.structure

## Status

Accepted (deferred move)

## Context

`auteur/structure/bible_audit.py` implements the **Bible Audit** — a diagnostic pass that reads the `StoryBible` event log and detects carrier-state inconsistencies (e.g., **Location Teleportation**) across chapter events. This is a Layer 6 operation over Bible events, not a blueprint-coherence operation.

However, `bible_audit.py` currently lives at `src/auteur/structure/bible_audit.py` — inside the `auteur.structure` package, which is otherwise the home of the whole-story blueprint diagnostic engine.

### Why it ended up here

`bible_audit.py` imports shared infrastructure from `auteur.structure.diagnostics`:

- `DiagnosticLayer` — the enum of structure layers (1–9)
- `DiagnosticSeverity` — error / warning
- `RepairOptions` — the preserve_intent / challenge_intent option container

These types were introduced as part of the structure engine and live in `auteur/structure/diagnostics.py`. Moving `bible_audit.py` to a more correct location (e.g., `auteur.audit` or `auteur.bible_audit`) requires first deciding whether `DiagnosticLayer`, `DiagnosticSeverity`, and `RepairOptions` stay in `auteur.structure` or are promoted to a shared location (e.g., `auteur.diagnostics`).

That extraction is a separate architectural decision not yet made.

### Current boundary signal

`BibleAuditDiagnostic` is intentionally excluded from `auteur.structure.__init__` exports, signalling that `bible_audit.py` is not a true member of the `auteur.structure` public API. This is a half-boundary: the file is physically inside the package but logically outside it.

## Decision

`bible_audit.py` stays in `auteur.structure` as a **temporary resident** until the shared diagnostic infrastructure (`DiagnosticLayer`, `DiagnosticSeverity`, `RepairOptions`) is extracted to a location reachable from both `auteur.structure` and the future `auteur.audit` (or equivalent) module.

The module docstring of `bible_audit.py` is updated to document this status and reference this ADR.

`BibleAuditDiagnostic` remains excluded from `auteur.structure.__init__` exports.

### Precondition for moving

Before `bible_audit.py` can move:

1. `DiagnosticLayer`, `DiagnosticSeverity`, and `RepairOptions` must be extracted from `auteur/structure/diagnostics.py` to a shared module (e.g., `auteur/diagnostics.py`).
2. Both `auteur.structure` and the new audit home must import from the shared module.
3. Existing tests must pass after the extraction.

This extraction is a follow-on ADR and implementation slice.

### Alternative considered

**Move `bible_audit.py` now** by duplicating `DiagnosticLayer`/`DiagnosticSeverity`/`RepairOptions` or adding a temporary re-export. Rejected because duplication creates a maintenance burden, and re-exports obscure the true module boundary rather than resolving it.

## Consequences

- The boundary ambiguity is documented, not hidden.
- A future agent reading this ADR knows exactly what must happen before the move can proceed.
- No code changes are required beyond the docstring update.
- `auteur.structure` continues to do double duty (blueprint diagnostics + Bible audit host) until the precondition is met.
