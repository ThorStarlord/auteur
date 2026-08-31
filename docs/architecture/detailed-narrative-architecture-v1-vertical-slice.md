# Detailed Narrative Architecture V1 — Vertical Slice Proof

Status: deterministic vertical-slice core implemented on the feature branch;
focused P0 acceptance tests pass. Full repository qualification retains three
known baseline Story Discovery failures.

## Slice

Use `tests/fixtures/repeated_map_focus_v2/` to prove:

```text
accepted Series Direction
→ accepted Book 1–3 Direction and realization history
→ current-state projection
→ typed causal-support and persistent pressure-group index over accepted history
→ Global Map
→ Book 4 planning intent
→ Focus / Decision Map
→ non-authoritative recommendation
→ revise one earlier accepted fact
→ impact propagation, rebuild, changed Focus
```

No open-world relationship extraction is required. Grouping and causal inputs
may be declared, narrowly deterministically derived from the fixture, or
supplied as explicit candidates; their origin remains visible.

## Exact implementation boundary

After approval, inspect and touch only these seams as needed:

- `series/vertical_slice_models.py`: source refs, transition lineage, Map and
  Focus output types;
- `series/vertical_slice_store.py`: accepted history and disposable snapshots;
- `series/repeated_map_focus.py`: accepted-history selection, currentness,
  grouping, reactivation;
- `series/vertical_slice_service.py`: orchestration, freshness, rebuild;
- `provenance/` or `impact/`: only where existing revision/impact seams cannot
  represent the slice; and
- focused tests.

Do not alter semantic layer names, add a graph database, or change expression
or prose behavior.

## Minimum new entities

- `StateEvidence`: current value, transition, superseded IDs, accepted ref;
- `CausalSupportRelation | PressureGroupRelation`: typed relation payload,
  origin, evidence, owner/source revisions, rule version, disposition;
- `GlobalMapSnapshot`: source revisions, state evidence, commitments, groups,
  relationships, freshness;
- semantic impact reporting alongside existing provenance `health` and
  `freshness`; do not extend `ArtifactMetadata.health`;
- `InterpretationRecord`, only if the slice includes a rejected interpretation.

No universal lifecycle or entity-per-ledger-row model is justified.

## Migration, surface, and tests

Existing canonical artifacts must remain loadable without rewriting. New
metadata uses ArtifactStore revision conventions; derived snapshots are
disposable. Prefer service/test seams. If CLI is needed, keep it read-side:

```text
auteur series map --book 4
auteur series focus --book 4 --intent <file>
auteur series impact <artifact>
```

Author actions record workflow history only. Deterministic tests must prove
accepted-only horizons, ordered current-state lineage, exact-ref freshness,
Book 4 reactivation, false-recency filtering, pressure grouping,
burn-archive incompatibility, equivalent rebuild, Book 2 revision impact, and
no mutation before explicit acceptance.

Exercise D1–D8 and D10–D12 from the companion death tests. D9 may remain a
model-level correction contract if no interpretive producer is included.

Also exercise D13: explicit pressure grouping must survive Global Map -> Focus
projection without becoming canonical, while a historical/superseded member
remains relation-relevant without becoming current.

D4 and D5 remain valid architecture death tests, but do not force generalized
commitment lifecycle implementation into this P0 slice. D9 remains a contract
test unless an interpretive correction producer is included.

The implementation must preserve two independent orders: STATE_ORDER and
transition order define narrative position; ArtifactStore revisions update one
stable realization identity in place. Revising Book 2 must not append a new
Book 2 event after Book 3, and must not silently rewrite accepted downstream
artifacts. Downstream freshness and semantic impact are recomputed for
reconciliation.

## Explicit non-goals

No model calls, automatic extraction, Global Map UI, 100+ entry performance
infrastructure, automatic semantic rewriting, universal commitment lifecycle,
thematic/psychological inference, or chapter/prose expansion.

## Proof standard

An engineer must be able to implement the slice without deciding where truth
lives, when revisions become stale, or whether a recommendation is
authoritative. Those choices must already be visible in the architecture and
tests.
