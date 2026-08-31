# Detailed Narrative Architecture V1 — Gap Matrix

| Capability | Needed architecture | Exists now? | Gap | Priority | Why |
|---|---|---|---|---|---|
| authoritative history | Revisioned accepted artifacts and decisions | Partial | Cross-book history is split across seams | P0 | Prevents silent loss |
| current state projection | Deterministic values with transition lineage | Partial | Current values lack uniform lineage | P0 | Separates now from happened |
| commitment lifecycle | Direction owner plus fulfillment assessment | Partial | Portfolio commitment states are different | P1 | Preserves author intent |
| dependency edges | Source affects target, refs, traversal | Partial | Series and ArtifactStore graphs are separate | P0 | Enables impact |
| story-instance relationships | Declared/deterministic/interpretive origins | Partial | Relations lack unified origin semantics | P1 | Controls trust |
| causal history | Historical transitions remain traversable | Partial | No cross-book causal index | P1 | Supports long horizon |
| pressure groups | Derived grouping by shared commitment | Partial | Narrow Map grouping only | P1 | Compact reasoning |
| incompatibility | State-based candidate filtering | Yes, narrow | Generalize only after proof | P1 | Prevents unsafe suggestions |
| revision impact | Direct/transitive reports | Yes, partial | Semantic suspect/contradictory boundary | P0 | Protects downstream work |
| Global Map | Rebuildable full internal projection | No | Only narrow Map exists | P0 | Central gap |
| Focus selection | Relevance over Map and intent | Yes, narrow | Generalized history/dependency inputs | P0 | Planning seam |
| provenance | Refs, revisions, hashes, derivation version | Yes, pilot | Series/relations alignment | P0 | Audit and rebuild |
| interpretive correction | Versioned candidate and author rejection | Partial | No unified correction record | P1 | Wrong inference safety |
| scalable context | Progressive disclosure and bounded traversal | Conceptual | No budgeted selector | P2 | 50/100+ entries |

## Existing-code crosswalk

| Component | Classification | Reason |
|---|---|---|
| `narrative_ontology` | REUSE AS-IS | Concept vocabulary boundary |
| `identity`, `book`, `series` | EXTEND carefully | Existing Direction/Series owners are correct |
| `narrative_blueprint`, `structure` | REUSE AS-IS | Structure diagnostics stay separate |
| `narrative_realization` | EXTEND | Add lineage only as proven |
| `bible.py`, canonical state | EXTEND selectively | Expose cross-book evidence |
| `series/repeated_map_focus.py` | EXTEND | Correct deterministic selection seam |
| `series/vertical_slice_*` | REUSE/EXTEND | Acceptance, refs, and Focus boundary exist |
| `relations` | EXTEND | Preserve explicit changes; align origin |
| `impact` | REUSE/EXTEND | Traversal/report machinery exists |
| `provenance` | REUSE AS-IS first | Revision, hash, freshness, atomic writes |
| `commitment` | REUSE AS-IS as workflow | Distinct from narrative commitments |
| `reconciliation` | EXTEND | Author review of downstream change |
| `roundtrip` | REUSE AS-IS | Controlled import/export boundary |
| LLM orchestration | DEFER | Deterministic proof needs no model |
