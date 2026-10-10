# Adversarial Architecture Review — Does the Structure Earn Its Cost?

**Frozen target:** \`bd2ba539d2f300941681fa7c7b80ab4765354b79\`
**Scope:** working state, source authority, projection fidelity, coupling, change complexity, recovery, bounded graph.
**Method:** source and contract inspection; **no running Python/HTTP app, performance benchmark, or host-agent qualification**.
**Disposition:** **TARGETED SIMPLIFICATION / VERIFY PERSISTENCE AND SOURCE FIDELITY**, not wholesale rewrite.

## 1. Responsibility / ownership mapping

| Concern | Actual owner / route | Judgment |
| --- | --- | --- |
| Noncanonical notes and links | [CanvasStore](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_store.py) | A real no-premise requirement; separate *working* storage can be justified |
| Accepted narrative meaning | Existing Direction/Structure/Realization/Expression/relations owners | Preserved by the new graph/working API source examined |
| Story Lenses / relations | [studio_projection.py](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_projection.py) | Read-only projection; source-currentness and chapter-change meaning need stronger verification |
| Change impact | [studio_impact.py](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_impact.py) + existing impact graph | Hypothetical dependency walk, not narrative-causal proof |
| Working prose generation | Existing [quick_draft.py](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/quick_draft.py#L650-L688) | Backend reuse justified; integration should retain exact request/source identity |
| Book re-entry | Existing book progress projection | Read-only and source-owned; UI surface may still be redundant |
| Presentation/layout | Canvas positions, zoom, filters in Browser | Layout should not become authority and need not be stored in the same mutation history as meaningful prose |

**Good boundary to preserve:** Studio does not introduce a new canonical relationship YAML, automatic acceptance flow, or graph database. A technical purity drive that removes the no-premise working store without a valid replacement would destroy a real product property.

## 2. Consequential architecture findings

### A-01 — Unbounded command ledger and deletion journal inside full-rewrite document

**Evidence:** \`WorkingCanvas.command_hashes: dict[str,str]\` and \`deleted: dict[str,DeletedItem]\` have no visible retention bound ([store fields](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_store.py#L73-L84)). Every accepted command appends a fingerprint then rewrites \`canvas.json\` by \`_atomic_write\` ([apply tail](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_store.py#L239-L245)). Browser save requests include full document snapshots, including layout-only changes ([queueSave](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/browser/studio.js#L17-L44)).

**Mechanism:** N ordinary commands create O(N) retained identity metadata; every subsequent save serializes the accumulated ledger, making cumulative serialized work scale at least quadratically with command count if saved indefinitely. Deleted-note payloads add potentially large retained data. This is a **source-supported longitudinal resource risk**, not a measured performance failure.

**Alternative:** bounded expiring command receipts plus a durable recovery window or separate compact replay identities; possibly coalesced layout writes. Do not break idempotence/retry guarantees to win a cosmetic line-count reduction.

**Probe:** 100, 1k, 10k edits with 0/50/200 active notes; measure file size, save latency, recovery and replay after trimming. Define durability/retention policies before a compaction repair.

### A-02 — Full-document replacement is powerful and hard to reason about

The store exposes granular create/update/delete/move/connect commands alongside \`replace-working-document\`. The Browser predominantly saves the entire in-memory graph via that replacement command ([store operations](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_store.py#L142-L244)).

**Risk:** exact revision conflicts prevent stale cross-tab overwrites, but reconciling deleted notes, links, positions and outstanding edits into whole snapshots expands the failure surface. There has already been a targeted repair for deleted-note recovery (PR #359) and save-ordering (PR #361); both are source changes, not verified runtime closures.

**Counterargument:** one atomic replacement is simple for a small canvas and avoids complicated partial mutations. Evaluate correctness under S2/S10 before proposing a larger command architecture.

**Decision:** keep the store during opt-in qualification, isolate the smallest model for meaningful edits vs layout, and avoid a speculative event-sourcing rewrite.

### A-03 — Working graph and derived graph lack identity roundtrip

Working nodes/edges and source-derived nodes/edges are separate Browser arrays, with separate source refs. The no-premise CanvasStore data model does not yet contain a bound canonical node/reference identity field to roundtrip a working item into an accepted source and later refresh it ([CanvasItem](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_store.py#L26-L39); [projection](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_projection.py)).

**Architecture/Product conflict:** the data is safely segregated, but the promised "one coherent author workspace" remains incomplete. Adding a second canonical graph store would be the wrong repair.

**Minimal direction:** source-bound link metadata on working items when an existing owning workflow returns a stable reference; explicit author acceptance remains in the owning flow. Verify source revision freshness on re-entry.

### A-04 — Chapter-change projection can be overinterpreted

\`load_relation_change_sets(project_root)\` scans all \`chapters/*/relation_changes.yaml\` files ([serializers](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/relations/serializers.py#L14-L19)); Studio indexes changes if relation IDs are known, but does not independently establish that every referenced chapter's expression is accepted ([projection](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_projection.py#L50-L76)).

**Risk:** users may read "Changed in Chapter N" as an authoritative history even if the change file represents working/unaccepted material. The Browser warns that current relation values are not historical snapshots; that does not resolve acceptance/currentness provenance.

**Counterargument:** chapter change files may already have stronger lifecycle semantics upstream. Inspect exact ownership/fixtures locally before changing projection behavior. If unaccepted change sets are possible, label them as recorded/provisional with source context, not as accepted history.

### A-05 — Hypothetical impact is not accepted story causality

The impact analyzer graph adds standard workflow edges in addition to recorded provenance ([impact/graph.py](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/impact/graph.py#L215-L248)). The Studio preview traverses dependencies and warns that they are not certain story consequences. This is **good epistemic caution** but the UI should preserve the difference between actual provenance and workflow default links.

**Action:** test semantic explanations on a real accepted story revision. Do not infer actual Chapter rewriting from a highlighted dependency path. Avoid building an automatic revision executor.

### A-06 — Canvas bounds are prototype constraints, not yet a need for graph infrastructure

Position bounds \`x=0..1400\`, \`y=0..1040\`, 200 notes and 500 working connections are explicit ([store](https://github.com/ThorStarlord/auteur/blob/bd2ba539d2f300941681fa7c7b80ab4765354b79/src/auteur/beginner/studio_store.py#L47-L85)). These contradict a literal "infinite" claim, but constraints may be sound safety guardrails for initial development.

**Action:** name it a bounded canvas in product/UI until scaling evidence supports extension. Measure realistic S6/S8 and rendering responsiveness first. No graph database or wholesale frontend framework change.

## 3. Alternative implementation choices

| Choice | Why plausible | Why not default now |
| --- | --- | --- |
| Retain current bounded CanvasStore and derived projections | Lowest migration risk, preserves no-premise and noncanonical author material | Needs correctness + lifecycle validation |
| Remove separate working store and reuse SessionEnvelope | Apparent fewer data models | SessionEnvelope requires premise and accepted-story boundaries; regression in core goal |
| Add a general graph database/event store | Could support large future stories | New authority and migration surface without proven current need |
| Focused domain operations with compact replay history | Can improve clarity and retention if stress tests fail | Refactor itself risks retries/recovery; must prove net benefit |

## 4. Verification plan specific to architecture

- Run exact-head \`python -m pytest -q tests -k beginner_studio\`; inspect stale snapshot, duplicate command, delete/restart/restore, invalid file paths and payloads.
- Execute real Browser -> server -> atomic file write -> reload and two-tab conflict.
- Simulate interruption **only in a controlled fixture project**, not a user's live Book.
- Verify no canonical Story Identity, relations, accepted Chapter bytes changed by canvas-only operations.
- Measure repeated save file size/latency and test replay behavior after any retention change.
- Test relation change file attached to a not-yet-kept Chapter; inspect resulting provenance semantics.
- Compare source refresh before/after a real accepted-story update.

**Current execution blocker:** no runnable local checkout in this workspace and DNS resolution of github.com fails in the container. Connected GitHub source inspection is available; do not invent test PASS counts or fake performance metrics.

## 5. Verdict

**TARGETED SIMPLIFICATION**, not architectural reversal. Existing semantic ownership and read-only projections are broadly defensible; the risky boundaries are working-document recovery/longitudinal growth and exact source/working identity.

**Blockers for default/release:** repeatable data durability, source truth/freshness and Browser-end-to-end qualification. **Deferred:** general graph database, cloud sync, event sourcing, infinite coordinate scheme and multi-Book automation until material needs are demonstrated.

**Claim ceiling:** architecture source analysis and test design, not operational reliability proof.
