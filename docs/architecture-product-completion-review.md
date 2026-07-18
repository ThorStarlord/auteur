# Auteur Architecture and Product Completion Review

Date: 2026-07-15

The durable principles for extending this platform are recorded in
[Architecture Constitution](architecture-constitution.md).

## Conclusion

Auteur's four foundational architectures are coherent and operational:

- Narrative Architecture defines semantic ownership.
- Provenance Architecture defines revision authority and freshness.
- Transformation Architecture defines safe movement and acceptance boundaries.
- Reasoning Architecture defines evidence-backed diagnosis and recommendation.

The Critic Contract, Registry, Runtime, synthesis, author-facing review,
reconciliation, publication, independent candidate decisions, recomposition,
and Chapter acceptance now exercise those foundations together.

## Canonical reference evidence

`The Lantern at Low Water` is the living executable reference for the bounded
single-Chapter product loop:

```text
Identity
→ Blueprint
→ Chapter Structure
→ Scene Realizations
→ Scene Expressions
→ Chapter Expression
→ external edit
→ reasoning review
→ proposals
→ application plan
→ publication
→ independent decisions
→ accepted-source recomposition
→ Chapter acceptance
→ partially_reconciled completion
```

The dogfood deliberately accepted one Scene edit, rejected another, and
deferred a Chapter transition. It therefore proves that publication, candidate
decisions, Chapter acceptance, and reconciliation completion remain distinct.

It also proves the reference artifacts are protected: the runner copies the
project to a temporary workspace, and the committed reference receives no
derived reconciliation or reasoning artifacts.

## What is complete at this boundary

The single-Chapter path is product-complete enough for continued dogfooding.
The architecture is not missing another foundational layer. Remaining gaps are
breadth, usability, and richer authoring scenarios:

- multi-Chapter Book Manuscript assembly;
- long-form author sessions;
- broader Structure and Realization revision workflows;
- stronger prioritization and additional critics;
- markerless mapping and Scene merge/split;
- grouped dependent candidate decisions;
- broader Universe and Series workflows.

These are intentionally deferred capabilities, not violations of the authority
constitution.

The full Book reconciliation workflow is now implemented:

1. **Phase A (Inspection & Routing):** Book external-edit inspection and
   ownership routing keep Book-owned edits as noncanonical proposals.
2. **Phase B (Planning & Publication):** Book proposal planning plus atomic
   candidate publication produce durable, unaccepted Book candidates with a
   noncanonical preview and publication manifest. Publication is not acceptance:
   a stale plan publishes nothing, a duplicate publication is rejected, failure
   is atomic, and no accepted Book, Chapter, or upstream artifact is mutated.
3. **Phase C1 (Recomposition):** Pointer-based recomposition from current
   accepted Chapter and Book-owned sources produces a derived, noncanonical
   Book — no pointer movement, no acceptance.
4. **Phase C2 (Comparison):** Read-only, deterministic comparison of
   recomposed Book against external manuscript with per-finding ownership
   classification (chapter-owned, book-owned, structural, marker).
5. **Phase C3 (Acceptance):** Acceptance creates an immutable accepted Book
   revision (authority=accepted, canonical=true) plus an immutable acceptance
   record (authority=decision), then moves the accepted Book pointer atomically
   (compare-and-swap, last). Duplicate acceptance is idempotent.
6. **Phase C4 (Completion):** Administrative/provenance closure that creates a
   single immutable completion record (authority=derived, lifecycle=completed,
   canonical=false) after a 20-point eligibility gate. No pointer, revision, or
   narrative authority is touched. Duplicate completion is idempotent.

Full Book-level reasoning/editing and publishing formats remain deferred.

## Next evidence-driven slice

The next candidate is Book-level workflow:

```text
multiple accepted Chapters
→ Book Manuscript → Book external edit
→ Book inspection → Book proposals → Book plan
→ Book publication → Book candidate decisions → Book recomposition
→ Book comparison → Book acceptance → completion
```

The full Book reconciliation workflow is now implemented and committed with
300+ passing tests. The remaining gap is Book-level reasoning/editing (an
LLM-backed cross-cutting workflow outside the deterministic reconciliation
pipeline) and production publishing formats.

## Decision rule

Future work should follow:

```text
run canonical reference → observe friction → choose one bounded gap
→ implement → verify on the reference
```
