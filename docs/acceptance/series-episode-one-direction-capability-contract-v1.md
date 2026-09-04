# Bounded Episode 1 Direction Capability Contract

Status: accepted design authority for implementation planning; implementation
has not started. No code, schema, CLI, or persistence behavior described here
exists yet. This document is not a claim that the capability is implemented,
qualified, released, or shipped.

This is a narrowly scoped follow-on capability to the Series Vertical Slice.
It adds the smallest coherent first-class Episode 1 Direction workflow for a
Series whose entry form is episodic. It does not define Book/Episode
unification, a generalized entry-unit abstraction, Episode realization or
canonical-state progression, a general-purpose Author Decision system, or any
Episode beyond Episode 1.

It reverses, for Episode 1 Direction only, the deferral recorded in
[Series Vertical Slice V1 Qualification](../engineering/series-vertical-slice-qualification-v1.md)
("episode support or Book/Episode unification") and in
[the Series Vertical Slice V1 plan](../superpowers/plans/2026-08-23-series-vertical-slice-v1.md).
Those documents remain accurate historical records of what that qualification
and that plan covered; this contract does not rewrite them.

## Capability statement

For a Series that the author has explicitly declared episodic, Auteur must let
the author propose a local Direction for Episode 1 that builds on the accepted
Series Direction and references the Series commitments the author selects,
explicitly accept it so that it becomes authoritative, and inspect it
distinctly from the Series Direction. Proposal generation must remain
non-authoritative; explicit acceptance is the only authority transition.

## Architectural placement

Episode 1 is defined as a first-class episodic entry unit. For this bounded
capability:

- Episode is not introduced as a sixth canonical scope. The canonical scope
  axis remains exactly Universe, Series, Book, Chapter, Scene, and the semantic
  layer model remains exactly Ontology, Identity, Structure, Realization,
  Expression, as defined by
  [Narrative Architecture](../narrative-architecture.md), which stays the sole
  authority for scope and layer names, count, ownership, and boundaries.
- An Episode 1 Direction is defined as a Series-scope, Identity-layer
  entry-unit Direction artifact for an episodic Series. It is the episodic
  counterpart of a Book 1 Direction, not a relabelled Book Direction.
- There must be no generalized Episode scope, no generalized Book/Episode
  scope unification, and no Episode-to-Chapter nesting machinery.

## Authority model

The accepted artifacts of this capability are, in order:

```text
accepted Series Direction        -> pre-existing Series-scope authority (unchanged)
accepted episodic entry-form     -> Series identity decision: this Series is episodic
accepted Episode 1 Direction     -> Episode-1 entry-unit Direction authority
```

Everything else the capability produces — proposals, inspection views — is a
working or derived artifact and must not be treated as authoritative.

Consistent with [Authority and mutation](../../CONTEXT.md) and with the
`AGENTS.md` rule that any authority-bearing decision requires explicit author
action, atomic persistence, and auditable provenance, each accepted artifact of
this capability must be created only by an explicit author action, persisted
atomically, carry provenance, and leave prior state unchanged on failure.

## Entry-form rules

- A Series is either Book-oriented or explicitly episodic. Absence of an
  explicit episodic declaration is defined as Book-oriented behavior. Existing
  Series and existing projects are Book-oriented under this rule and must not
  be reinterpreted, migrated, or forced to re-accept anything merely because
  this capability ships.
- The explicit episodic declaration is an authority-bearing Series identity
  decision. It must be persisted separately from `SeriesDirection` so that no
  existing accepted Series Direction, its content, or its content hash is
  rewritten.
- The declaration must record: the declaring author; a declaration/acceptance
  timestamp in UTC; a stable artifact identity; and provenance linking it to
  the accepted Series Direction that was current when it was declared.
- The declaration is permitted only after an accepted Series Direction exists.
- The declaration is permitted only before any entry-level Direction work has
  begun in either form — that is, only while the Series has no Book Direction
  proposal and no accepted Book Direction.
- Once entry-level Direction work has begun in either form, the entry form is
  locked for this bounded capability. Converting an episodic Series that has
  begun Episode 1 Direction work to Book-oriented, and converting a
  Book-oriented Series that has begun Book Direction work to episodic, both
  remain out of scope. General conversion between entry forms remains out of
  scope.
- Re-declaring the entry form that a Series already holds must be idempotent:
  it must not create a new authoritative revision, must not change the
  recorded declaring author or timestamp, and must not depend on which author
  string is supplied. This capability introduces no new role or permission
  model; Auteur remains a single local-author tool.

## Bounded workflow

The complete author-facing workflow for Episode 1 is:

```text
declare the Series episodic
  -> propose an Episode 1 Direction
  -> explicitly accept the Episode 1 Direction
  -> inspect
```

There must be no separate author-facing "begin Episode 1 planning" step. If the
implementation needs internal, non-author-facing workflow state, that state
must not surface as an additional author action.

## Dependency and reference semantics

- An Episode 1 Direction must reference at least one commitment from the
  current accepted Series Direction.
- The author chooses which commitments are referenced. Auteur must not
  evaluate, rank, or reject the selection on artistic or narrative grounds and
  must not automatically infer which commitments are relevant.
- Auteur validates only structure, at both proposal time and acceptance time:
  at least one reference is present; every referenced commitment belongs to the
  current accepted Series Direction; duplicate references are invalid; unknown
  or stale references — including a reference to a commitment from a superseded
  Series Direction revision — are invalid.
- References must be stored as references to the accepted Series Direction, not
  as embedded copies.
- If the accepted Series Direction changes after an Episode 1 Direction
  proposal is created but before it is accepted, acceptance of that proposal
  must be rejected; the author must produce a fresh proposal against the
  current accepted Series Direction.
- Accepting an Episode 1 Direction must not alter, re-version, or re-accept the
  Series Direction.

## Book/Episode exclusivity

- For an explicitly episodic Series, proposing a Book Direction is invalid and
  accepting a Book Direction is invalid.
- For an undeclared or Book-oriented Series, existing Book Direction behavior is
  unchanged and Episode Direction is unavailable.
- No normal supported path may result in both an accepted Book 1 Direction and
  an accepted Episode 1 Direction for the same Series under this bounded
  capability. This must be enforced by an active check, not left to the
  incidental absence of the other artifact.

## Persistence and provenance expectations

- The accepted episodic entry-form artifact and the accepted Episode 1
  Direction must each be written atomically, with rollback that leaves nothing
  partial on any failure.
- Each must be recorded through the existing provenance machinery with a stable
  artifact identity, an explicit declared dependency on the accepted Series
  Direction, and a recorded UTC acceptance timestamp.
- Reloading an accepted Episode 1 Direction in a later session must yield
  identical Direction content and identical referenced commitments.
- Re-accepting the exact same Episode 1 Direction proposal must be idempotent:
  it must not create a new authoritative revision and must yield an explicit
  "already accepted, no change" result that is distinguishable from a first
  acceptance. A new authoritative Episode 1 Direction revision requires a new
  proposal and an explicit acceptance of that new proposal.

## Inspection requirements

The author must be able to inspect, distinctly and unambiguously:

- the accepted Series Direction;
- the accepted Episode 1 Direction;
- the Series commitments referenced by Episode 1.

Series-level content and Episode-level content must be clearly separated and
clearly labelled. An Episode 1 Direction must never be surfaced merely as
"Book 1". Inspection must succeed and report the absence clearly when no
Episode 1 Direction has been accepted yet.

## Compatibility guarantees

- Existing Book-oriented projects must continue to load and operate with no
  migration step.
- Existing accepted Series Directions and Book Directions must remain valid and
  authoritative, with unchanged content and content hashes.
- Existing Book Direction proposal, acceptance, reload, and inspection behavior
  must retain its established meaning.
- No existing canonical authority may change merely because this capability is
  present, and no existing Series may be silently reinterpreted as episodic.
- Compatibility is behavioral. Existing textual command output may change only
  where a legitimate additive inspection capability requires it; established
  workflow semantics must not change.

## Acceptance invariants

A conforming implementation must satisfy each of the following. Each is stated
so that a capability-level test can verify it.

1. An Episode 1 Direction proposal is created without becoming authoritative;
   no accepted Episode 1 Direction exists until an explicit acceptance.
2. Explicit acceptance is the only action that makes an Episode 1 Direction
   authoritative; the accepted artifact records the accepting author and a UTC
   timestamp and reloads with identical content.
3. Acceptance is all-or-nothing; a failure during acceptance leaves no partial
   Episode 1 Direction and no changed authority.
4. A proposal with zero commitment references, with duplicate commitment
   references, or with an unknown or stale commitment reference is rejected at
   both proposal time and acceptance time.
5. The referenced-commitment set recorded on acceptance equals the
   author-supplied set exactly; Auteur adds nothing and makes no artistic
   judgement.
6. Acceptance of an Episode 1 Direction leaves the accepted Series Direction —
   its content, revision, and content hash — unchanged.
7. Re-accepting an already-accepted Episode 1 Direction proposal produces no
   new authoritative revision and an explicit no-change result distinct from a
   first acceptance.
8. Episode Direction is available only for an explicitly episodic Series; on an
   undeclared Series it is unavailable and all existing Book behavior is
   unchanged.
9. Declaring a Series episodic is rejected when no accepted Series Direction
   exists and when any Book Direction proposal or accepted Book Direction
   already exists.
10. Once entry-level Direction work has begun, no supported path converts the
    entry form, and no supported path yields both an accepted Book 1 Direction
    and an accepted Episode 1 Direction for the same Series.
11. Re-declaring the already-effective episodic entry form is an idempotent
    no-op that preserves the original declaration author, timestamp, and
    provenance regardless of the supplied author string.
12. Inspection presents the accepted Series Direction, the accepted Episode 1
    Direction, and the referenced Series commitments as distinct, clearly
    labelled content, never presenting Episode 1 as "Book 1", and succeeds with
    a clear absence report when no Episode 1 Direction has been accepted.
13. Existing Book-oriented projects load without migration; existing accepted
    Series and Book Directions remain byte-stable and authoritative.
14. Authoritative documentation defines this bounded capability and its
    exclusions accurately; the definition does not depend on a changelog entry
    or a post-implementation qualification claim.

## Out of scope

This contract does not introduce or settle:

- any Episode beyond Episode 1, including season or multi-episode roadmaps and
  arbitrary future-episode planning;
- Episode realization, Episode canonical-state progression, Episode outcomes,
  or next-episode planning;
- Book/Episode unification or a generalized entry-unit or Direction
  abstraction spanning Book and Episode;
- generalized Direction inheritance, universal Direction revision propagation,
  or automatic flow of Series Direction changes into an accepted Episode 1
  Direction;
- universal dependency inference or automatic relevance judgement;
- a generalized Author Decision system;
- changes to the legacy full-Series or StoryBible workflows;
- any browser, TUI, or editor presentation surface;
- adding an "episodic" value to `SeriesDirection` or to the legacy Series type
  model, or any change that would alter an existing accepted Series Direction's
  content hash;
- recreating or renumbering the historical ADRs or contract documents that
  earlier plans reference but that are absent from the checkout.

## Evidence and human boundary

This contract captures approved product and architecture decisions for a
pre-implementation checkpoint, consistent with the `AGENTS.md` requirement to
capture approved conceptual decisions in `docs/` before implementing schema,
CLI, or pipeline behavior. It is design authority, not evidence of behavior.
Human validation is still required for:

- whether the four author-facing steps read as the smallest coherent workflow;
- whether the entry-form lock timing matches how writers actually begin a
  Series;
- whether the inspection view makes the Series/Episode distinction obvious;
- whether rejecting duplicate commitment references (rather than silently
  de-duplicating them) matches author expectations.
