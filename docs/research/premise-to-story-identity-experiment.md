# Premise-to-StoryIdentity Research Experiment

Status: approved research protocol; findings have not yet been collected.

This document defines the first product-design research experiment for Auteur.
It tests the premise-to-Identity interaction before a guided product surface or
new runtime behavior is selected.

## System definition and product hypothesis

The system definition is held constant during this experiment:

- `docs/narrative-architecture.md` remains the authority for the five semantic
  layers and the scope axis.
- `StoryIdentity` is the canonical Layer 1 authority when explicitly accepted
  by the author.
- A recommendation, proposal, or research packet is not accepted canon.
- Auteur proposes and explains; the author accepts, rejects, revises, or
  ratifies.
- The experiment does not alter schemas, CLI behavior, persistence, or
  semantic-layer boundaries.

The product-design hypothesis under test is that a creative beginner can move
from a raw premise to an understandable proposed `StoryIdentity` when Auteur
uses plain-language explanations, one strongest recommendation, meaningful
rejected alternatives, and an explicit author decision boundary.

This distinction is important: the experiment tests how an author discovers and
understands the settled contract. It does not redefine the narrative engine.

## Experiment hypothesis

A creative beginner can move from a raw premise to an understandable proposed
`StoryIdentity`, then make an informed accept, reject, or revision decision,
without learning Auteur's internal machinery first.

The first valuable outcome is an accepted whole-story direction and a clear
next creative decision. Chapter planning, prose drafting, and complete
five-layer disclosure are outside this experiment.

## Target participant

Recruit a creative beginner with limited long-form narrative-planning
experience. The participant should bring an original premise, character
impulse, or desired reader experience that they can express in approximately
one to three sentences.

Technical ability is not a selection criterion. A technically experienced
participant may take part, but the session evaluates whether the
creative-beginner experience works for them rather than whether Auteur should
be positioned as a technical-author tool.

## Sample input

Use the participant's own raw premise or character impulse, captured verbatim.
Do not require a genre, plot outline, character dossier, or complete ending.

Use a standardized fallback premise only when a participant cannot provide an
input. Record when the fallback is used because it changes the evidence from a
personal-premise session to a controlled-input session.

## Experiment format

Run a moderated, surface-neutral concept test. Each session is one-on-one and
lasts approximately 45–60 minutes.

The facilitator prepares a proposal packet manually from the participant's
premise. The study does not invoke `auteur identity recommend`, build a
prototype, or choose between browser, TUI, editor, and CLI surfaces. This
isolates comprehension, author authority, and the usefulness of the proposed
interaction from recommendation-generation quality and implementation
convenience.

No research packet is written to `story_identity.yaml`. Any participant
decision in this study is research evidence, not canonical Layer 1 mutation.

## Interaction flow

Use the same sequence for every participant:

1. Capture the raw premise verbatim.
2. Present a plain-language reflection of what the facilitator understood.
3. Present one recommended story direction, its rationale, and meaningful
   rejected alternatives.
4. Present a compact proposed `StoryIdentity` with plain-language meanings
   beside canonical terms.
5. Ask the participant to explain the direction and its main commitments in
   their own words.
6. Ask the participant to explicitly accept, reject, or request a revision.
7. If they request a revision, apply one author-directed revision and show the
   changed commitments beside the original proposal.
8. Ask the participant to identify the next useful creative decision.

The proposal should expose only the commitments needed for the current
decision:

- target reader experience and genre/subgenre promise;
- scope and scale;
- emotional core and theme;
- the core engine, explained through protagonist want, resistance, conflict,
  stakes, change, and broad ending shape;
- why the direction fits the premise;
- meaningful rejected alternatives.

Detailed Structure, Realization, Expression, chapter planning, prose drafting,
and the full five-layer taxonomy remain deferred.

## Research questions

### Primary question

Can a creative beginner move from their raw premise to an understandable
proposed `StoryIdentity`, then make an informed accept, reject, or revision
decision without learning Auteur's internal machinery?

### Secondary questions

- Can the participant explain the recommended direction in ordinary language?
- Can they distinguish a proposal from accepted canon?
- Does one strong recommendation reduce uncertainty without causing premature
  agreement?
- Can they identify something to preserve or revise?
- Can they identify the next useful creative decision?
- Where do confusion, hesitation, facilitator intervention, or abandonment
  occur?

## Evidence plan

Record the following for every session:

- participant code, protocol version, and whether a fallback premise was used;
- the participant's premise, preserved verbatim in private research notes;
- the exact proposal packet shown;
- elapsed time at each flow step;
- completion, abandonment, hesitation, and requests for help;
- the participant's plain-language paraphrase;
- whether they distinguish proposed commitments from accepted canon;
- accept, reject, or revision decision and the participant's rationale;
- requested revisions and whether they preserve the premise's intent;
- the next creative decision identified by the participant;
- facilitator prompts or substantive interventions;
- researcher interpretation, kept separate from participant statements;
- an optional brief confidence rating, treated as secondary evidence.

Do not treat enthusiasm, satisfaction, recommendation acceptance, or successful
artifact creation as proof of product value. A successful session requires both
an informed author decision and comprehension of what was accepted, what
remains provisional, and what happens next.

## Participant-level success criteria

A participant succeeds when they:

- reach an explicit accept, reject, or revision decision;
- accurately explain the proposed direction's main commitments;
- distinguish a proposal from accepted canon;
- identify something to preserve or revise;
- identify the next useful creative decision;
- do so without substantive facilitator coaching.

A thoughtful rejection or revision counts as success when it is informed. The
experiment does not optimize for first-pass acceptance.

## Participant-level failure criteria

Classify a session as a failure when the participant:

- cannot explain the proposed direction after one neutral clarification;
- mistakes the proposal for accepted canon;
- cannot identify what they are being asked to accept or revise;
- loses the premise's intent without noticing;
- requires the facilitator to supply narrative reasoning or make the decision;
- abandons the flow because the concepts or authority boundary remain unclear.

When recording a failure, distinguish proposal mismatch from comprehension,
authority-boundary, facilitation, or task-friction failure.

## Stopping rules

- Run at least five sessions.
- Pause and revise the protocol after two consecutive critical failures of the
  same kind, especially authority-boundary confusion or inability to explain
  the direction.
- Stop at five sessions if at least four participants meet the success criteria
  and no critical failure appears in the final two sessions.
- Continue to a maximum of eight sessions when results are mixed or new failure
  modes continue to appear.
- If the criteria remain unmet after eight sessions, classify the experiment as
  failed or inconclusive. Do not proceed directly to product implementation.

Freeze the facilitator guide and proposal template before session one. If a
critical failure requires a material change, create a new protocol version and
do not pool pre-change and post-change results without labeling them.

## Unresolved decisions

This experiment intentionally leaves the following decisions open:

- participant recruitment source and operational consent process;
- the standardized fallback premise;
- the final guided surface: browser, TUI, editor integration, or another form;
- whether a later experiment should add structural diagnosis and repair;
- the exact author-facing wording and visual presentation of the proposal.

## Bounded-complexity gate

Before beginning a human or founder self-study with a complex Book-level
premise, complete the v1.2 stress-simulation gate in the separate
[stress simulation findings report](premise-to-story-identity-stress-simulation-findings.md).

The bounded-complexity flow adds a pre-Identity triage that:

- inventories important threads, explicit constraints, and unresolved
  questions;
- recommends one primary Book-level thread for author ratification;
- classifies other threads as supporting, deferred, unresolved, or explicitly
  excluded only by author decision;
- separates context required for the current Identity decision from optional
  worldbuilding;
- maps each important premise intention to its proposed representation; and
- translates abstract constraints into observable commitments and boundary
  examples.

Do not force a `StoryIdentity` when the author cannot identify a primary
Book-level thread. Pause for clarification and record the unresolved decision.
The proposal/canon boundary remains necessary but is not sufficient; the author
must also be able to inspect whether the proposal preserved the premise before
ratifying it.

The v1.2 stress suite must pass before the complex-premise self-study gate is
opened. The simulation remains synthetic evidence and does not count as human
participant evidence.

## Next decision gate

After sessions, add an anonymized aggregate findings document at
`docs/research/premise-to-story-identity-findings.md`. Use it to decide whether
to proceed to a surface-specific prototype, revise and repeat the concept test,
or stop or narrow the product hypothesis.

Do not create that findings document before participant sessions are complete.

An internal simulated walkthrough may be run before or alongside human
recruitment to rehearse the protocol. It is governed by the separate
[Simulation Protocol](premise-to-story-identity-simulation.md). Simulation
results are not participant evidence and must not be merged into the human
findings document.

## Related documentation

- [Narrative Architecture](../narrative-architecture.md)
- [Opinionated Narrative Engine](../opinionated-narrative-engine.md)
- [Product Design Research](product-design-research.md)
- [Simulation Protocol](premise-to-story-identity-simulation.md)
- [Stress Simulation Protocol](premise-to-story-identity-stress-simulation.md)
- [Stress Simulation Findings](premise-to-story-identity-stress-simulation-findings.md)
