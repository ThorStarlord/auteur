# ADR 019: Derived Global Map And Story-Instance Relation Authority

**Date:** 2026-08-31
**Status:** Accepted
**Context:** Detailed Narrative Architecture V1 requires a rebuildable whole-story Map and a clear authority boundary for relations used by Map and Focus.

## Decision

1. Global Map is a derived, rebuildable projection over accepted source
   revisions. Focus is a derived relevance projection over Global Map. Neither
   is a second canonical narrative store.
2. Story-instance relationship indexes are derived and rebuildable. Declared
   relations are authoritative only when declared in, and accepted through,
   their owning Direction, Structure, or Realization artifact. A derived index
   cannot promote its own row to canon.
3. Deterministic relations are derived from accepted facts under a named rule.
   Interpretive relations remain corrigible, non-authoritative reasoning
   evidence; confidence affects ranking, never authority.
4. The existing `relations.yaml` and `relation_changes.yaml` domain remains
   the canonical character-relationship-state mechanism defined by ADR 015.
   It is separate from causal-support and pressure-group story-instance
   reasoning.
5. Derived views may be discarded and rebuilt from authoritative sources.
   Persisted snapshots carry source revisions and derivation metadata, but
   never become a second source of narrative truth.

## Consequences

The implementation must preserve accepted history, source revisions, evidence,
and relation origin. Upstream revision impact may make downstream work stale
or semantically contradictory, but does not silently rewrite or roll back
accepted downstream artifacts. Narrative order is independent from revision
order: a revised realization retains its stable narrative position.

The detailed contract and first vertical-slice boundary remain in
[`Detailed Narrative Architecture V1`](../architecture/detailed-narrative-architecture-v1.md).
