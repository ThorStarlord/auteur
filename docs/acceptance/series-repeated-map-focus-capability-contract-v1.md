# Repeated Series Map/Focus Capability Contract

Status: accepted behavioral basis for implementation planning; implementation
has not started.

This is a narrowly scoped follow-on contract to Series Vertical Slice UX V1.
It turns the accepted synthetic Books 1-4 probe into observable behavior. It
does not define Domain Model V2, finite-Series extent, a universal lifecycle
system, or a general-purpose relevance engine.

Evidence basis: [Synthetic Repeated Map/Focus Probe](../product-validation/series-vertical-slice-v1-synthetic-repeated-map-focus-probe.md).

## Capability statement

A writer entering planning for Book `N > 1` can see a compact, derived view of
the accepted Series history that matters to the current Book, understand why
each surfaced item matters now, and receive one bounded, state-compatible next
creative decision.

Auteur preserves the distinction between:

```text
accepted authority       -> Series Direction, Book Direction, realized state
derived continuity view  -> Map for the current Book
derived decision proposal -> Focus for the current Book
author action             -> workflow history, not automatic canon
```

The Map and Focus outputs are rebuildable projections. They do not silently
create Book Direction, modify Canonical State, or turn a selected option into
canon.

## Terminology boundary

`ArtifactStore` already uses `Lifecycle` for persistence and authority facts
such as proposed and accepted artifacts. This contract does not reuse that
term for continuity relevance.

The continuity derivation may locally distinguish the following dispositions:

- active: accepted material still governs or constrains the current Book;
- resolved: an accepted question or commitment has been fulfilled and is no
  longer an active next-decision driver;
- dormant: an accepted historical fact has no present relevance trigger;
- reactivated: a dormant fact becomes relevant because current accepted
  Direction, state, or the proposed decision points to it;
- superseded: an older accepted state has been replaced by a later accepted
  state; and
- irrelevant: accepted material that supports neither active continuity nor
  the current decision.

These are derived relevance dispositions for one Map computation. They are not
a universal artifact lifecycle, not new authority states, and not a claim that
every narrative entity needs a lifecycle field.

## Inputs and authority boundary

For Book `N`, the derived planning context may use:

- the current accepted Series Direction and its revision;
- accepted Book Directions through Book `N - 1`;
- accepted realization bundles and their state transitions through Book
  `N - 1`;
- the rebuildable Canonical State derived from those accepted bundles; and
- the explicitly entered planning point and current Book Direction context
  available to the workflow.

It must not use as authoritative context:

- proposed or unaccepted Book Directions;
- proposed or unaccepted realization candidates;
- abandoned workflow alternatives;
- future Book authority; or
- recency alone.

Every surfaced item or group must be supported by exact accepted source
references. A derived context or proposal must be invalidated or recomputed
when those accepted inputs change.

## Map contract

At a planning checkpoint for Book `N`, Map must:

1. preserve active Series commitments that still govern the current Book;
2. surface current accepted state changes that constrain or enable the next
   decision;
3. reactivate an older accepted fact only when current accepted Direction,
   current accepted state, or the proposed next decision supplies a present
   relevance trigger;
4. omit resolved, superseded, dormant, irrelevant, proposed, and unaccepted
   material from the active item list unless a compact historical summary is
   needed to explain the present condition;
5. group several accepted consequences that instantiate one Series-level
   pressure rather than presenting them as unrelated peer items;
6. show the current state rather than presenting a superseded state as if it
   were current;
7. give every surfaced item or group a specific plain-language “why this
   matters now” explanation; and
8. provide the accepted source references behind each surfaced item or group,
   with deeper source detail progressively disclosed.

Map compactness is a behavioral requirement, not a fixed item-count promise.
The implementation must avoid both an unbounded history dump and a recency
window that drops durable active continuity.

## Focus contract

At the same planning checkpoint, Focus must present exactly one bounded next
creative decision for the current Book. It must include:

- a current-Book question;
- a small bounded set of presented options;
- one recommendation;
- a specific rationale based on the active pressure, current accepted state,
  and present relevance trigger;
- a specific principal tradeoff; and
- exact accepted input references supporting the proposal.

The recommended option must be compatible with current accepted state. If the
proposal or recommendation becomes stale or contradicts accepted state, the
workflow must reject the action, mark the proposal unusable, or recompute the
proposal before author action is accepted. It must not silently exercise a
contradictory recommendation.

Focus remains non-authoritative. Choosing the recommendation, choosing another
presented option, or deferring records workflow history only. None creates or
accepts the current Book Direction or modifies Canonical State.

The presentation must use the current Book number. It must not carry the
Book-2-specific wording into later Books.

## Acceptance scenarios

The following scenarios use the accepted adversarial ledger from the synthetic
probe. The source names are logical scenario references; they do not imply
that the current V1 implementation can already persist this ledger.

### Scenario R1 — Book 2 activates a new consequence

Given:

- `series-direction@1` establishes the pressure that official history must
  answer to lived memory;
- `book-1-direction@1` carries that pressure and the unresolved falsifier
  question;
- `book-1-realization@1 / founding-record` is accepted and confirms that the
  founding record is forged;
- `book-1-realization@1 / monastery-testimony` is accepted but dormant;
- `book-1-realization@1 / broken-lantern` is accepted but irrelevant; and
- `book-2-burn-archive` is proposed but unaccepted;

when the author enters Book 2 planning,

then Map surfaces:

- the active Series pressure;
- the forged founding record; and
- the still-open falsifier question or its decision-driving expression;

and Map omits the broken lantern, the unaccepted burn-archive proposal, and
future Book material.

Map may summarize the pressure and founding fraud as one continuity group, but
the concrete state change must remain understandable. Each surfaced item or
group explains that the accepted Book 1 change makes official history an active
constraint on Book 2 and cites accepted sources.

Focus presents one question equivalent in meaning to:

> How should Book 2 make the exposed fraud matter to lived memory?

The recommendation must cite the accepted Series pressure and forged-record
state, and its tradeoff must distinguish the available creative emphasis. A
Focus choice remains non-canonical.

### Scenario R2 — Book 3 resolves one question and supersedes one state

Given the accepted R1 history plus:

- `book-2-direction@1` continues the pressure and investigates the falsifier;
- `book-2-realization@1 / named-falsifier` identifies the falsifier and
  resolves the falsifier question;
- `book-2-realization@1 / public-admission` records a public admission;
- `book-3-direction@1` continues the pressure; and
- `book-3-realization@1 / admission-retracted` is accepted;

when the author enters Book 3 planning,

then Map:

- keeps the Series pressure active;
- surfaces the current council retraction;
- does not present the resolved falsifier question as an active next-decision
  item;
- does not present the public admission as current state; and
- may show the resolved question and superseded admission only as compact
  history when they explain the current retraction.

The current retraction must have a why-now explanation tied to accepted Book 3
context and accepted source references. The Map must omit irrelevant recent
information and unaccepted alternatives.

Focus presents one current-Book question equivalent in meaning to:

> How should Book 3 respond to the council’s retraction while preserving the
> witness’s authority?

Its rationale must use the current retraction and the accepted resolution of
the falsifier question. A recommendation based only on the latest event is
insufficient; listing all history is also insufficient.

### Scenario R3 — Book 4 reactivates dormant history

Given the accepted R2 history plus:

- `book-3-realization@1 / archive-protected` records that a treaty protects
  the archive because it contains the only evidentiary chain;
- `book-3-realization@1 / repaired-lantern` is recent but irrelevant;
- `book-3-ally-militia` is proposed but unaccepted; and
- `book-4-direction@1` points back to the monastery testimony;

when the author enters Book 4 planning,

then Map:

- keeps the Series pressure active;
- surfaces the treaty-protected archive as current accepted state;
- reactivates the old monastery testimony because current Book 4 Direction
  supplies the relevance trigger;
- explains why the old fact matters now; and
- omits the resolved falsifier question, superseded admission, irrelevant
  lantern, and unaccepted proposals from the active list.

Map may summarize the founding fraud, admission, retraction, and treaty
protection as one history-of-the-archive group. It must not flatten the current
treaty constraint into the same undifferentiated historical list.

Focus presents one question equivalent in meaning to:

> How should Book 4 bring the monastery testimony back into public memory
> without destroying the archive’s evidentiary chain?

If “burn the archive” appears as an apparent recommendation, it must be
rejected, marked incompatible and unavailable as a valid choice, or replaced by
a fresh proposal because it contradicts accepted archive-protected state.

### Scenario R4 — Derived projection and proposal freshness

Given any of R1-R3,

when the derived Map or Focus proposal is deleted and rebuilt from accepted
sources,

then the rebuilt result is semantically equivalent, including source
references, relevance explanations, grouping decisions, and recommendation
basis.

When an accepted source revision or current state changes after Focus is
proposed,

then the old proposal cannot be exercised as if its inputs were current. The
author must receive a stale/recompute boundary without any mutation to
historical acceptance or Canonical State.

### Scenario R5 — Authority preservation

Given any presented Map or Focus result,

when the author chooses the recommendation, chooses another presented option,
or defers,

then only non-authoritative workflow history changes. No Book Direction is
created or accepted and no Canonical State value changes.

## Deferred by this contract

This contract does not introduce or settle:

- finite, uncertain, expanding, or contracting Series extent;
- a universal `Lifecycle` abstraction for narrative entities;
- a universal Direction or inheritance system;
- an event graph or inferred dependency engine;
- numerical relevance ranking or machine-learned attention;
- free-form author-authored Book Direction from Focus;
- an author-facing history browser; or
- a universal recommendation engine.

The next implementation boundary must earn any shared structure by the
accepted scenarios above. It must not make the fields of one Series fixture
universal merely because they are convenient for that fixture.

## Evidence and human boundary

This contract is grounded in the synthetic repeated-Map/Focus probe. It is not
participant evidence. Human validation is still required for:

- acceptable Map density and grouping;
- whether resolved history should be hidden, collapsed, or shown as a
  milestone;
- whether reactivation feels useful rather than surprising;
- whether pressure grouping matches a writer’s mental model;
- whether state-compatibility warnings feel protective or obstructive; and
- whether one bounded Focus decision remains useful after several Books.
