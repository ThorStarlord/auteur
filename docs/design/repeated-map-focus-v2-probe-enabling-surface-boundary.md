# Repeated Map/Focus V2 — Probe-Enabling Surface Boundary

Status: design-only boundary note. No implementation has started. Actual
implementation is separately authorized (Boundary 2).

This note defines the smallest set of surface repairs required to enable the
real human-validation study for Repeated Map/Focus V2. It deliberately defines
**exactly two blockers**, and nothing more. It is grounded in the qualified V2
candidate and the human-facing presentation/comprehension boundary selected as
the next consequential product boundary.

## Boundary position in the execution order

```text
Boundary 0 — safe integration of qualified V2
      ↓
Boundary 2 — implement + qualify the two probe-enabling surface repairs
      ↓
render the final probe kit from the real qualified surface
      ↓
Boundary 1 — run the human-validation protocol
      ↓
STOP at the human-evidence boundary
```

This note scopes Boundary 2 only. The two repairs below are exactly the
probe-enabling surface; nothing else is required to run the study.

## The two demonstrated surface blockers

The previous product analysis demonstrated exactly two blockers against the
human study on the real shipped surface. They are the only two repairs defined
here.

### Blocker A — Book-N planning-intent entry

The shipped CLI needs a supported way to enter:

1. the current planning-intent statement; and
2. which already accepted facts are present relevance triggers.

This reuses the existing `enter_repeated_book_planning` semantics — no new
concept. The entered material remains:

- workflow state;
- non-authoritative; and
- not accepted Book-N Direction.

The participant (or facilitator on the participant's behalf) must be able to
state a planning intention and name accepted facts as relevance triggers without
knowing any internal ID.

### Blocker B — accepted-fact discovery

The user and facilitator must **not** manually know or invent internal artifact
IDs, revisions, or fact IDs. Boundary 2 must provide only the smallest read-only
discovery surface:

- accepted historical facts grouped/listed in an understandable form;
- stable friendly selection labels; and
- friendly-label to exact `AcceptedFactRef` translation internally.

Exact provenance must be preserved internally. The friendly label is only a
presentation/selection handle; it never replaces or hides the authoritative
source reference.

This surface is read-only: it lets the author discover and select already
accepted facts, but it does not propose, edit, or accept anything.

## Explicitly excluded from the discovery surface

Boundary 2 **explicitly excludes**:

- a general history browser;
- a search engine;
- a ranking/relevance engine;
- new domain entities;
- a `PressureGroup` taxonomy; and
- any browser/TUI/editor redesign.

A selection list with stable friendly labels and internal reference translation
is not any of those. If a proposed repair starts to look like a search or
ranking engine, or a new taxonomy, it is out of boundary for this step.

## Non-goals (do not add or design)

Boundary 2 does not add or design:

- finite/uncertain Series extent;
- Series contraction/expansion;
- generalized recommendation-content generation;
- free-form Book-N Direction;
- universal lifecycle/dependency/relevance/recommendation machinery;
- new Domain Model V1 work;
- intra-Book checkpoints;
- numerical relevance; or
- cross-Series federation.

## Acceptance framing for the repairs

Each repair, when implemented and qualified, must make the shipped surface able
to run the Human Validation Contract end to end:

- a planner can enter planning intent + name accepted-fact relevance triggers
  without internal IDs (Blocker A); and
- can discover already accepted facts via friendly labels that translate
  internally to exact `AcceptedFactRef`s (Blocker B).

The probe kit is then rendered from this real qualified surface. Until both
repairs are qualified, Boundary 1 (the human study) must not start.
