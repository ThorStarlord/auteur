# Bounded Episode 1 Direction Implementation Boundary

Status: ratified implementation boundary. This document was approved before
implementation, as a plan-only repository analysis describing intended
responsibilities and an approved architectural boundary. Implementation and
qualification status are tracked separately from this boundary document.

This analysis maps the
[Bounded Episode 1 Direction Capability Contract](../acceptance/series-episode-one-direction-capability-contract-v1.md)
onto the Series Vertical Slice implementation family. It deliberately separates
reusable authority and provenance infrastructure from the Episode-specific
semantics that must be added. It does not reopen the Series Vertical Slice
boundary, does not add a generalized entry-unit abstraction, and does not
propose Episode realization or canonical-state work.

## Baseline

The analysis is grounded in the Series Vertical Slice family
(`src/auteur/series/vertical_slice_models.py`,
`src/auteur/series/vertical_slice_service.py`,
`src/auteur/series/vertical_slice_store.py`,
`src/auteur/series/vertical_slice_formatters.py`,
`src/auteur/series/cli.py`) and the shared provenance store
(`src/auteur/provenance/`). The most recent bounded extension of this family,
Repeated Map/Focus V2, added a dedicated pure module
(`src/auteur/series/repeated_map_focus.py`) rather than growing the store and
service, kept the prior behavior frozen, and reran the regression matrix. This
capability follows the same shape.

## Architectural placement

- An Episode 1 Direction is a Series-scope, Identity-layer entry-unit Direction
  artifact for an episodic Series. It is not a sixth canonical scope. The
  five-scope, five-layer model in [Narrative Architecture](../narrative-architecture.md)
  is not changed by this capability.
- The explicit episodic entry-form choice is a separate authority-bearing
  artifact. It must not be a field on `SeriesDirection`, because adding a field
  there would change the accepted Series Direction's serialized content and
  content hash and would force re-acceptance of existing accepted Series
  Directions and fixtures. Absence of the entry-form artifact is defined as
  Book-oriented behavior.
- The Episode artifacts are first-class concrete models, in the same style as
  the `SeriesDirection` and `BookDirection` triads: standalone models with
  `extra="forbid"`, no shared generic Direction base class, their own artifact
  identity, artifact type, storage path, and CLI verbs. Renaming or aliasing
  the Book Direction models to represent an Episode is out of scope and would
  violate the capability contract.

## Compatibility requirement

`SeriesDirection`, the legacy Series type model, and every existing accepted
artifact and sidecar must remain unchanged. This capability is additive:
new models, one new pure module, thin persistence and orchestration hooks on
the existing store and service, new CLI verbs, and additive documentation. The
existing Book Direction proposal, acceptance, reload, and inspection paths keep
their established semantics; the only modification to an existing service path
is a leading guard that rejects Book Direction work when the Series is
explicitly episodic, which is a no-op for an undeclared or Book-oriented
Series.

## Capability-to-repository map

The following table pairs each contract behavior with the existing seam it
should build on and the Episode-specific responsibility that must be added. The
"added responsibility" column describes intended work; none of it exists yet.

| Contract behavior | Existing seam to build on | Added responsibility |
|---|---|---|
| Explicit episodic entry-form decision, persisted separately from `SeriesDirection` | Atomic accepted-artifact write with staging and rollback; `ArtifactStore` acceptance with a declared dependency and an opt-in UTC timestamp | A new accepted entry-form artifact with a stable identity, a declared dependency on the accepted Series Direction, and no write to `SeriesDirection` |
| Entry-form eligibility (accepted Series Direction exists; no Book Direction work yet) | The accepted-Series-Direction read used by the Book Direction path; the proposal and accepted-artifact path lookups | A precondition check for an accepted Series Direction and a check that no Book Direction proposal and no accepted Book Direction exist |
| Entry-form lock and no conversion | Idempotent, author-scoped workflow-entry pattern | Idempotent re-declaration that preserves the original author, timestamp, and provenance and does not depend on the supplied author string; no conversion path is added |
| Propose Episode 1 Direction, non-authoritative | The Book Direction proposal builder, which stamps a source reference to the current accepted Series Direction and writes only a proposal file | An Episode 1 Direction proposal builder that mirrors this, gated on the Series being explicitly episodic |
| Reference at least one current Series commitment, structural validation only | The existing Series-commitment validator used by the Book Direction path at both propose and accept | Reuse that validator unchanged for the "present, at least one, belongs to the current accepted Series Direction" checks; add a duplicate-reference rejection at model validation |
| Explicit acceptance is the only authority transition; atomic; UTC timestamp; declared dependency | The Book Direction acceptance path: re-validate the proposal against the current accepted Series Direction, reject a stale source reference, stage, accept through the provenance store with an opt-in timestamp, roll back on any exception | An Episode 1 Direction acceptance path that mirrors this exactly, with its own artifact identity and type |
| Idempotent re-acceptance with an explicit no-change result | The provenance store always increments the accepted revision | An explicit pre-acceptance guard: if an accepted Episode 1 Direction already exists for the same proposal with equal content, return it as an explicit no-change result without calling the provenance acceptance path |
| Two-way Book/Episode exclusivity | The Book Direction propose and accept service methods | A leading guard on both that rejects the operation when the Series is explicitly episodic; a no-op for an undeclared or Book-oriented Series |
| Inspect Series Direction, Episode 1 Direction, and referenced commitments distinctly; never "Book 1" | The progressive-disclosure formatter pattern used by the Series journey map, with a default view and a detail view | A dedicated read-only inspection view and formatter that labels Series-level and Episode-level content separately, lists the referenced commitments, and never emits the token "Book"; a clear absence report when no Episode 1 Direction is accepted |
| Keep new derivation and view logic out of the oversized store and service | The dedicated-pure-module precedent | A new pure module holding the inspection result shape and pure helpers, with the store and service holding only thin persistence and orchestration hooks |

## What can be reused safely

- Proposal versus accepted-artifact separation and the "explicit acceptance is
  the only authority transition" barrier.
- Accepted source revision and content-hash validation, and the stale-source
  rejection performed when an acceptance reaches the authority boundary.
- Declared dependency metadata in the provenance store, used instead of any
  inferred dependency.
- Atomic staged write with rollback around accepted artifacts.
- Opt-in UTC acceptance timestamps for new vertical-slice artifacts, which keep
  legacy artifact hashes deterministic.
- The Series-commitment structural validator, reused unchanged.
- The progressive-disclosure formatter model: default output omits identifiers
  and revisions; a detail view exposes them.
- The idempotent, author-scoped workflow-entry pattern, adapted to drop the
  different-author rejection per the capability contract.

## What is not a safe reuse

- Adding an "episodic" value to `SeriesDirection` or the legacy Series type
  model. This would change an accepted Series Direction's content hash and
  break the compatibility guarantee.
- Reusing or renaming the Book Direction models to stand in for Episode 1. The
  contract requires a genuinely distinct first-class model, artifact identity,
  artifact type, storage path, and CLI verb.
- Growing the existing store and service modules with the new derivation and
  view logic. They already exceed the project's module-size guidance; new pure
  logic belongs in a dedicated module.
- The Book-2-specific context and next-decision machinery. It is fixture-bound
  and unrelated to a Direction-only Episode slice.
- The medium-contract enums that mention episodes elsewhere in the codebase.
  They are Layer-1 medium-contract values and are not connected to the Series
  vertical slice; this capability must not wire itself to them.
- Introducing a typed exception hierarchy. The vertical-slice family raises the
  plain built-in value error for domain violations and has no dedicated
  exceptions module; this capability follows that local convention and does not
  perform an unrelated exception-hierarchy cleanup.

## Proposal and acceptance authority distinction

Proposal generation must write only a proposal artifact and must never create
authority. Acceptance must be a separate, explicit author action that:

- re-validates the proposal's structure and its Series-commitment references
  against the current accepted Series Direction;
- rejects the acceptance if the proposal's recorded Series Direction source
  reference no longer matches the current accepted Series Direction revision;
- otherwise stages the accepted Episode 1 Direction, records it through the
  provenance store with a declared dependency on the accepted Series Direction
  and a UTC timestamp, and commits atomically;
- rolls back completely on any failure, leaving no partial artifact and no
  changed authority;
- never writes, re-versions, or re-accepts the Series Direction.

## Stale-reference behavior

A referenced Series commitment is invalid, at both proposal time and acceptance
time, if it is unknown to the current accepted Series Direction, has been
removed, or belongs to a superseded Series Direction revision. A proposal whose
recorded Series Direction source reference does not equal the current accepted
Series Direction revision must be rejected at acceptance; the author must
create a fresh proposal.

## Idempotency requirements

- Re-declaring the entry form a Series already holds must not create a new
  authoritative revision, must preserve the original declaring author and
  timestamp, and must not depend on the supplied author string.
- Re-accepting an already-accepted Episode 1 Direction proposal, unchanged,
  must not create a new authoritative revision and must produce an explicit
  no-change result that a caller and the CLI can present differently from a
  first acceptance. Only a new proposal plus a new explicit acceptance produces
  a new authoritative revision.

## Boundary against generalized work

This document does not authorize, and a conforming implementation must not add:

- any Episode beyond Episode 1;
- Episode realization, canonical-state progression, outcomes, or next-episode
  planning;
- a generalized entry-unit or Direction abstraction spanning Book and Episode;
- Direction inheritance, universal revision propagation, or dependency
  inference;
- a generalized Author Decision system;
- changes to the legacy full-Series or StoryBible workflows;
- any browser, TUI, or editor surface;
- an author-facing "begin Episode 1 planning" step.

## Acceptance-test boundary

Implementation should add capability-level tests against the capability
contract's acceptance invariants, in addition to model-level and
service-level unit tests. The minimum capability-test groups are:

1. propose is non-authoritative; explicit acceptance is the only authority
   transition; reload equality after acceptance;
2. structural reference validation at propose and accept: at least one
   reference, membership in the current accepted Series Direction, duplicate
   rejection, unknown/stale rejection;
3. acceptance is all-or-nothing under an injected failure;
4. accepting Episode 1 Direction leaves the Series Direction content, revision,
   and hash unchanged;
5. re-acceptance idempotency with an explicit no-change result;
6. entry-form eligibility and lock: rejected without an accepted Series
   Direction, rejected after Book Direction work, idempotent re-declaration;
7. two-way Book/Episode exclusivity, including the invariant that no supported
   path yields both an accepted Book 1 Direction and an accepted Episode 1
   Direction for one Series;
8. inspection distinguishes Series-level and Episode-level content, lists
   referenced commitments, never emits "Book", and reports a clean absence;
9. an existing Book-oriented project loads with no migration and its accepted
   artifacts remain byte-stable.

Each capability test must keep three things distinct: an authority mutation, a
derived or view projection, and a workflow record.

## Plan-only recommendation

The next implementation plan should begin with one concrete question:

> Can the bounded Episode 1 Direction capability be built by mirroring the
> Book Direction propose and accept paths, adding a separate entry-form
> authority artifact and a dedicated inspection module, while leaving
> `SeriesDirection`, every existing accepted artifact hash, and the legacy
> full-Series path unchanged?

If the answer requires changing `SeriesDirection`, changing an existing
accepted artifact's hash, adding a canonical Episode scope, or making Episode
Direction share a generic base with Book Direction, stop and reopen the
boundary rather than extending by assumption.
