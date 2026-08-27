# Repeated Map/Focus V2 — Human Validation Contract (Books 2/3/4 Archive of Lies)

Status: contract designed and persisted. The probe-enabling surface previously
described as a prerequisite (see
[docs/design/repeated-map-focus-v2-probe-enabling-surface-boundary.md](../design/repeated-map-focus-v2-probe-enabling-surface-boundary.md))
has been implemented, qualified, published, and integrated into `main`. That
prerequisite is now historical; the study is no longer blocked on surface
availability. No participant evidence has been collected.

This contract defines the human-validation protocol for the qualified Repeated
Map/Focus V2 capability. It is grounded in the Books 2/3/4 *Archive of Lies*
synthetic probe and the [Repeated Series Map/Focus Capability
Contract](../acceptance/series-repeated-map-focus-capability-contract-v1.md).
It closes the human-evidence boundary from the V2 workstream: it converts the
still-open usability questions into an observable, preregistered protocol.

The Human Validation Contract was designed and persisted before the probe
surface existed, but the actual human study was correctly gated until that
surface had been implemented and qualified. That gate is now satisfied; the
contract itself is unchanged as a preregistered protocol awaiting participants.

## Scope clarification

This contract remains valid for testing Map/Focus comprehension, why-now
comprehension, current vs superseded understanding, dormant-fact reactivation,
bounded Focus decisions, recommendation vs canon, workflow choice vs narrative
authority, and authority inversions. It does not answer the newer comparative
architecture-value question introduced in
[Product Design Research — Architecture value and Global Map](../research/product-design-research.md):

Does a richer explicit narrative architecture materially improve long-horizon
reasoning relative to prompt/context-only and current Map/Focus?

That question belongs to the separate Architecture Value Experiment. This human
validation contract is therefore retained as a later or complementary study,
not deleted or rewritten into the new Architecture Value Experiment. Its
preregistered participant-count and authority-inversion rules remain in force
unless a direct factual contradiction requires correction.

## Study question

Can a long-form writer understand and use repeated opening-Book Map/Focus
across Books 2, 3, and 4 of *Archive of Lies* without believing that Auteur has
planned the whole Series, silently changed canon, or made a presented
recommendation authoritative?

## Participant-facing rule

The participant requires **no CLI expertise** and **no internal knowledge**. The
facilitator operates any required tooling. The participant never sees:

- internal IDs (artifact IDs, revisions, fact IDs);
- YAML or other storage details;
- proposal or source artifact names; and
- any internal workflow, storage, or persistence internals.

Everything observed by the participant is a human-readable Map/Focus
presentation with plain-language "why this matters now" explanations and a
single bounded Focus decision.

## Books 2/3/4 probe coverage

The protocol exercises the following behaviors across the three later Books:

1. **Activation** — an accepted Book-1 consequence (forged founding record)
   activates as an active constraint at the Book 2 opening.
2. **Resolution/supersession** — a resolved falsifier question is not presented
   as an active item at the Book 3 opening, and a superseded council admission
   is not presented as current state.
3. **Dormant-fact reactivation** — the old monastery testimony is reactivated
   at the Book 4 opening because Book 4 planning intent triggers its relevance.
4. **Grouped continuity** — accepted consequences that instantiate one
   Series-level pressure are grouped into a compact history-of-the-archive view
   rather than presented as unrelated peers.
5. **Why-now comprehension** — every surfaced item or group carries a specific
   plain-language "why this matters now" that a writer can read and interpret.
6. **One bounded Focus decision** — Focus presents exactly one current-Book
   question with a small bounded option set, one recommendation, a rationale,
   and a principal tradeoff.
7. **Recommendation vs narrative fact** — the protocol checks whether a writer
   understands that a Focus recommendation (including the rejected "burn the
   archive" option for Book 4) is non-authoritative and distinct from accepted
   narrative fact.
8. **Workflow choice vs Book Direction/canon** — the protocol checks whether a
   writer understands that choosing a Focus option records workflow history and
   does not accept Book Direction or modify Canonical State.

## Facilitator rules and evidence discipline

- Keep **participant words/actions separate from facilitator interpretation**.
  Record verbatim or near-verbatim participant statements and observed actions
  in one column/field; put the facilitator's interpretation in a separate,
  explicitly-labeled field. Never merge the two.
- **Authority inversions are explicitly recorded.** Any moment the participant
  treats a recommendation as authoritative, canon, or already-decided —
  including treating the rejected "burn the archive" as a valid current option —
  is recorded as an authority inversion with the surrounding participant words.
- **Procedural clarification is allowed.** The facilitator may clarify how to
  read the screen or how to operate the interface. This is not interpreted as
  product comprehension evidence.
- **Product-meaning correction counts as evidence.** Any point where the
  facilitator corrects the participant's understanding of what a Map/Focus
  item *means* is recorded as product-meaning evidence, not filtered out or
  silently replaced.

## Participant-count clarification

- **With one participant, report directional qualitative evidence only.** Do
  not issue an overall study pass/fail from a single session.
- **Aggregate preregistered pass/fail criteria apply only when at least three
  qualifying participants complete the protocol.**
- **A severe individual result — especially persistent authority
  inversion — may still be consequential evidence even at low N.** A single
  persistent authority inversion is a blocking signal for the human-evidence
  boundary regardless of count, and must be escalated as evidence rather than
  averaged away.

## Qualified basis and surface requirement

The protocol runs against the real qualified surface described in the
probe-enabling boundary, not against a simulator or prototype that is not the
shipped product. The surface must provide:

- accepted historical facts grouped/listed in an understandable form;
- stable friendly selection labels (no internal IDs);
- friendly-label to exact `AcceptedFactRef` translation internally; and
- a supported way to enter the current planning-intent statement and present
  accepted-fact relevance triggers.

The human study was gated on both probe-enabling surface repairs being
qualified because it depends on those exact behaviors. That gate is now
satisfied: the surface has been implemented, qualified, and integrated into
`main`. The protocol remains to be run against that qualified surface; no
participant evidence has been collected.

## Non-goals

This contract does not add or design: finite/uncertain Series extent; Series
contraction/expansion; generalized recommendation-content generation; free-form
Book-N Direction; universal lifecycle/dependency/relevance/recommendation
machinery; new Domain Model V1 work; intra-Book checkpoints; numerical
relevance; or cross-Series federation.
