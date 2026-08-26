# Repeated Series Map/Focus Implementation Boundary

Status: plan-only repository analysis. No implementation has started.

This analysis maps the [Repeated Series Map/Focus Capability
Contract](../acceptance/series-repeated-map-focus-capability-contract-v1.md)
onto the qualified Series Vertical Slice implementation. It deliberately
separates reusable infrastructure from semantics that must be added. It does
not reopen Domain Model V1 or propose a universal lifecycle abstraction.

## Baseline identity

The analysis is grounded in the qualified product candidate:

```text
candidate: d3bb1eb37d065b34c132771cf19a0856e60d0cea
```

The current main checkout includes documentation commits after that candidate,
but the source and test bytes used for the qualification remain the baseline.
The previous qualification report records the exact source and artifact gates.

## Boundary conclusion

The smallest implementation boundary is a new repeated-planning capability
inside the existing sparse vertical-slice family, with three strict limits:

1. retain existing accepted Series Direction, Book Direction, realization, and
   Canonical State artifacts as authority owners;
2. add a deterministic, local continuity derivation that produces a compact
   current-Book projection; and
3. generalize the bounded Focus proposal only across the current Book planning
   seam, not into a universal recommendation or lifecycle framework.

The current implementation has enough persistence, provenance, acceptance, and
rebuild machinery to support this boundary. It does not have the semantic
projection or per-Book decision behavior. Extending the existing hard-coded
Book 2 rules in place would conceal those missing semantics and would make the
wrong fields look universal.

## Terminology boundary for implementation

The repository’s `ArtifactStore` `Lifecycle` is an authority/persistence
concept. It identifies facts such as whether an artifact is accepted and
whether its metadata is current. It must not be overloaded to mean that a
continuity item is active, resolved, dormant, reactivated, or superseded.

The repeated Map capability needs a local derivation result—whether represented
as an internal rule result, a projection-local value, or another narrow shape—
that can distinguish those relevance dispositions for one planning checkpoint.
That result is not a shared lifecycle entity and does not change the authority
state of the source artifact.

This distinction is required by the contract:

```text
accepted/proposed/unaccepted -> source authority and persistence
active/resolved/dormant/...  -> derived relevance for this Map computation
```

## Capability-to-repository map

| Contract behavior | Existing repository seam | Exact mismatch | Boundary disposition |
|---|---|---|---|
| Use accepted sources with exact revisions | `ArtifactStore`, `ArtifactRef`, source validators in `vertical_slice_store.py` | Existing source validation is strong but the context selects only the current Series, immediately previous Book, and hard-coded transitions. | Reuse provenance and freshness mechanisms; replace only the selection policy. |
| Preserve explicit planning entry | `PlanningEntry`, `enter_book_planning`, `derive_book_context` | The existing entry gates context derivation but does not make the accepted history through Book N-1 available as a generalized input set. | Reuse the workflow gate; generalize the read-side source collection. |
| Carry active Series commitments | `BookDirection.series_commitment_ids`, `DirectionCommitment` | Only commitments explicitly named by the immediately preceding Book Direction are selected; there is no distinction between active and resolved commitments. | Keep explicit commitment references as one valid relevance signal; add local disposition rules rather than universal commitment lifecycle. |
| Carry current state and state provenance | `AcceptedRealizationBundle`, `StateTransition`, `CanonicalState`, rebuild path | `CanonicalState` contains current key/value pairs and applied bundle IDs, but Map derivation does not link current values to their transition lineage or use the full accepted history. | Reuse deterministic state rebuild and accepted bundle chain; add a derived current-state evidence view for Map/Focus. |
| Reactivate dormant accepted facts | accepted realization history and Book Direction source refs | No current model expresses a relevance trigger from a later Book Direction or decision; old facts are either hard-coded in or absent. | Add a local reactivation rule based on current accepted context; do not add a universal dormant lifecycle. |
| Hide resolved and superseded material while preserving useful history | revisioned artifacts and ordered realization bundles | Current context has no status/currentness/lineage or grouping fields; it cannot tell current state from superseded state for presentation. | Add projection-local currentness/history handling; keep accepted history immutable and authoritative. |
| Group consequences by Series pressure | `SeriesDirection.pressure`, `DirectionCommitment`, `CarryForwardItem` | `CarryForwardItem` is a flat item with only two kinds; Map prints every item. | Add a narrow grouping/projection seam. Do not infer a universal cross-domain impact taxonomy. |
| Exclude recent irrelevant information and unaccepted proposals | accepted artifact loaders and explicit source refs | Accepted-only filtering exists, but relevance is not evaluated beyond the fixture’s hard-coded transition table. | Keep accepted-only boundary; add deterministic relevance tests and rules. |
| Produce one current-Book Focus proposal | `NextDecisionProposal`, `DecisionOption`, `record_decision_action` | Proposal generation is hard-coded to Book 2, the two Archive of Lies context IDs, and one question/options/rationale. | Reuse proposal/action shape and authority barrier; replace the generator with a current-Book bounded proposal seam. |
| Reject stale or state-incompatible recommendations | `accepted_input_refs` comparison in `record_decision_action` | Existing freshness compares proposal refs with regenerated `generated_from`; there is no explicit option-vs-current-state compatibility check. | Reuse compare-at-action-boundary behavior; add recommendation compatibility as a separate derived validation, not as authority mutation. |
| Present current Book language | `format_series_journey_map` and `format_series_journey_focus` | Focus hard-codes “Book 2 canon” and “Book 2 direction” even though the formatter reads `decision.book_number`. | Generalize presentation wording to the current Book as part of this capability; do not change V1 action semantics. |
| Rebuild derived results | `save_book_planning_context`, deletion, `rebuild_canonical_state` | Derived context is rebuildable, but the derivation version and source set describe only the Book 2 fixture. | Preserve delete/rebuild semantics and version the local repeated derivation. |

## What can be reused safely

### Authority and provenance

The following are compatible with the new contract:

- proposal versus accepted artifact separation;
- accepted source revision and content-hash validation;
- declared dependency metadata in `ArtifactStore`;
- atomic acceptance and rollback around realization bundles;
- ordered accepted realization history;
- deterministic `CanonicalState` reconstruction; and
- stale-input rejection when a decision action reaches the acceptance boundary.

These mechanisms answer whether a source is authoritative and fresh. They do
not answer whether the source is relevant to the current Map. That latter
decision is the missing projection behavior.

### Existing projection and presentation shapes

`BookPlanningContext` already provides a useful outer concept: a derived
planning result with a Book number, source references, items, and derivation
version. `CarryForwardItem` already requires a summary, why-now explanation,
and source references. `NextDecisionProposal` already carries the Book number,
question, options, recommendation, rationale, tradeoff, and accepted input
references.

These shapes are good seams, but their current fields are not sufficient for
the new behavior. Reusing them unchanged would force grouping, reactivation,
and compatibility semantics into free-form strings and would make the
contract unverifiable.

### Progressive disclosure

The existing formatter boundary is also useful:

- default Map/Focus output omits internal IDs and revisions;
- `--detail` exposes source references and proposal identifiers; and
- source references are kept adjacent to the item they support.

The repeated capability should preserve that disclosure model. Group support
does not justify showing the whole causal history by default.

## What is not a safe reuse

### The legacy full-Series model

`SeriesIdentity` and `BookPlan` represent a fuller, contiguous Series plan. The
accepted sparse Series boundary explicitly keeps that path separate. The
repeated Map capability must not relax `SeriesIdentity` validators, create
empty future Book plans, or reinterpret the full-Series compiler/Bible as the
sparse continuity projection.

### The existing hard-coded context table

`_BOOK_CONTEXT_STATE_TRANSITIONS` is an Archive of Lies / Book 2 fixture rule,
and `_BOOK_2_DECISION_CONTEXT_ITEMS` is an exact two-item gate. These are
qualification fixtures, not reusable relevance abstractions. Generalizing them
by adding Book 3 and Book 4 entries would demonstrate only a larger hard-coded
fixture and would not satisfy the accepted ledger scenarios.

### The existing `Lifecycle` enum

Using artifact lifecycle values to represent resolved, dormant, or superseded
continuity would conflate source authority with derived relevance. That would
make a presentation decision mutate or reinterpret authority metadata. The
existing lifecycle mechanism should remain the source freshness/authority
barrier only.

### Generic recommendation or Author Decision infrastructure

The current bounded decision action is intentionally a workflow record, not
Book Direction authority. A repeated Focus proposal should retain that
boundary. The accepted contract does not justify a universal recommendation
engine, a universal Author Decision aggregate, or free-form Book Direction
creation.

## Smallest likely implementation seam

The contract does not prescribe a final class layout, but the repository
analysis identifies four independently testable seams:

### 1. Accepted-history input seam

Add a read-side operation that gathers accepted Series Direction, accepted Book
Directions, accepted realization bundles, and current Canonical State through
the current planning horizon. It must validate each source revision using the
existing store mechanisms.

This is a read/projection input seam. It must not create a second authority
store or change acceptance behavior.

### 2. Local continuity selection seam

Add a deterministic selector scoped to the repeated Series Map capability. It
must produce the contract’s observable dispositions:

- active;
- resolved or superseded historical support;
- dormant until a current trigger; and
- reactivated when a current accepted source makes the fact relevant.

It must also produce pressure groups and why-now explanations. The selector
should be versioned and source-backed, but it need not be a reusable lifecycle
framework or a numerical ranking engine.

### 3. Current-Book Focus seam

Replace the Book-2-only proposal construction with a bounded current-Book
proposal boundary. The first concrete proposal strategy may remain fixture- or
Series-specific while the source/context and freshness contract becomes
reusable.

The proposal path must:

- consume the derived continuity result;
- retain exact accepted input references;
- produce current-Book question, options, rationale, and tradeoffs;
- validate recommendation compatibility against current accepted state; and
- preserve non-authoritative choose/choose-other/defer behavior.

This is the minimum needed to prove repeated Focus. It is not permission to
accept arbitrary author-authored Book Direction from a Focus action.

### 4. Presentation seam

Generalize Map/Focus labels and summaries to the current Book and to grouped
context while preserving default/detail disclosure. The wording change must
not alter authority semantics.

## Acceptance-test boundary

Implementation should add capability-level tests against the contract rather
than only extending model validation.

The minimum test groups are:

1. R1 Book 2 activation and exclusion of irrelevant/unaccepted material;
2. R2 Book 3 resolution and supersession behavior;
3. R3 Book 4 dormant-fact reactivation and grouped Map;
4. recommendation rejection or recomputation when accepted state contradicts
   the proposed recommendation;
5. exact accepted source references and why-now explanations;
6. deletion/rebuild semantic equivalence; and
7. stale proposal rejection after accepted source or state change.

Each test must distinguish:

```text
accepted authority mutation
derived Map/Focus projection
workflow action recording
```

No test should treat a Focus choice as accepted Book Direction or Canonical
State.

## Repository risk assessment

| Risk | Evidence | Classification | Boundary response |
|---|---|---|---|
| Sparse Direction and full Series planning are conflated | `SeriesIdentity`/`BookPlan` requires complete contiguous plans; sparse Direction is separate by ADR 067. | Contract mismatch | Keep repeated capability in sparse vertical-slice family. |
| Context relevance is fixture-specific | Hard-coded `_BOOK_CONTEXT_STATE_TRANSITIONS` and Book 2 item IDs. | Missing capability | Add local deterministic selector; do not append fixture cases. |
| History can be shown as current | Flat `CarryForwardItem` has no currentness or grouping. | Product-design pressure exposed as implementation gap | Add projection-local disposition/current-state handling. |
| Recommendation can be stale | Existing input-ref comparison is a useful freshness seam. | Reusable seam with missing compatibility check | Extend derived validation at proposal/action boundary. |
| Focus language is Book-2-specific | Formatter explicitly says Book 2 canon/direction. | Presentation implementation gap for generalization | Use current Book number in future repeated surface. |
| Universal abstraction grows prematurely | Domain Model V1 and ADR 067 defer universal Direction/lifecycle machinery. | Architecture risk | Keep local rules and typed projection semantics until a second independent concrete family exists. |

## Explicit non-goals for implementation planning

Do not, as part of this contract boundary:

- relax or replace the existing full-Series `SeriesIdentity`/`BookPlan` path;
- add finite or uncertain Series extent;
- add a universal lifecycle field to Direction, Commitment, State, or every
  artifact;
- infer dependencies from arbitrary narrative text;
- build a general event graph or relevance-ranking service;
- make every accepted historical transition visible in Map;
- make Book 3/4 decisions by copying the Book 2 question and options; or
- make a Focus action authoritative.

## Plan-only recommendation

The next implementation plan should begin with one concrete question:

> Can the accepted R1-R3 ledger be represented by a local, deterministic
> accepted-history selector and a current-Book bounded proposal seam while
> preserving existing V1 authority, provenance, and full-Series boundaries?

If the answer requires changing `ArtifactStore` lifecycle semantics, relaxing
the full-Series model, or making continuity relevance authoritative, stop and
reopen the boundary rather than extending the implementation by assumption.

No code is authorized by this document. The capability contract and this
analysis are the pre-implementation boundary for a future, separately
approved implementation plan.
