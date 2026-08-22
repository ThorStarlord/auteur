# Premise-to-StoryIdentity Stress Simulation Learning Synthesis

Status: `INTERNAL SIMULATION EVIDENCE`

This document is a synthesis of six v1.2 synthetic agent rehearsals. It is
not human participant research, creative-beginner validation, usability
validation, or product validation. It records protocol learning and candidate
product hypotheses only.

## Purpose and boundary

The v1.2 runs tested whether a Book-level premise-to-`StoryIdentity` packet
could keep authorial intent visible while guiding one primary-thread decision.
They did not test a product implementation, a product surface, recommendation
quality at scale, or human comprehension. The synthesis therefore answers a
narrow question:

> Which interaction protections are worth adversarially testing before the
> research protocol is considered ready for bounded human research?

The semantic model remains governed by
[Narrative Architecture](../narrative-architecture.md): Identity contains
commitments, Structure contains plans, and Book is a scope rather than a
semantic layer. The product-definition distinction between settled system
definition and open product design follows
[Opinionated Narrative Engine](../opinionated-narrative-engine.md). The
research framing follows
[Auteur Product Design Research](product-design-research.md).

## Evidence set

The source record is the [v1.2 registry](premise-to-story-identity-stress-simulation-v1-2.md),
which links the six standalone transcripts and preserves the older
[full findings archive](premise-to-story-identity-stress-simulation-findings.md).
All six runs used `Protocol v1.2`, `creative-beginner-v1.0`,
`simulation-evaluator-v1.0`, record type `SIMULATION`, and zero human
participants.

| Run ID | Observed result | Narrow stress target | Evidence summary |
|---|---|---|---|
| `stress-v12-ensemble-01` | `SIMULATION_PASS` | Ensemble threads and a Book-level center | The preservation map kept each sibling goal visible while the persona ratified one primary direction. |
| `stress-v12-dense-setting-03` | `SIMULATION_PASS` | Required versus deferred setting context | Context triage kept institutions and history from becoming an encyclopedia before the Identity decision. |
| `stress-v12-constraints-04` | `SIMULATION_PASS` | Multiple explicit constraints | Abstract constraints were restated as observable commitments and boundary examples. |
| `stress-v12-overloaded-05` | `SIMULATION_PASS` | Competing goals, timelines, and constraints | Primary-thread triage reduced load and kept unresolved intentions visible before a proposal. |
| `stress-v12-triage-stop-06` | `SIMULATION_PASS` | No authorized primary thread | The flow stopped without forcing a `StoryIdentity` and named the decision needed to continue. |
| `stress-v12-primary-secondary-07` | `SIMULATION_PASS` | Primary thread, secondary goal, and resident authority | The persona ratified the route, retained the recordings as an active secondary goal, and strengthened the authority boundary in one bounded revision. |

Aggregate v1.2 result: six `SIMULATION_PASS`, zero
`SIMULATION_FAILURE`, zero `SIMULATION_INCONCLUSIVE`, and no mid-run protocol
changes. This is a description of the synthetic record, not a success rate for
people.

## System definition and product design remain separate

The following are settled boundaries that the simulations were expected to
respect:

- an accepted `StoryIdentity` is a Layer 1 author commitment;
- a recommendation, packet, transcript, or report is proposed or derived
  until explicitly ratified;
- Book-level Identity work must not be presented as Chapter, Scene, Realization,
  or Expression work;
- the author must retain authority over identity-level changes.

The following remain product-design hypotheses or research questions, not
changes to the semantic architecture:

- whether a guided packet is the right first experience for a creative beginner;
- which plain-language terms best explain primary thread, secondary goal,
  constraint, proposal, and canon;
- whether a preservation map reduces cognitive load for people rather than
  only for the synthetic persona;
- which surface can support this flow while keeping the canonical artifacts
  inspectable;
- whether a next-decision handoff produces meaningful continued work.

## Observations, interpretations, and candidate invariants

The evidence is separated into three levels so a rehearsal observation is not
silently promoted into architecture or a product requirement.

### Observations

- Every v1.2 packet showed a raw premise, an inventory, a recommended primary
  thread, a preservation map, a proposal/canon status, and a next decision.
- The six personas could state a primary direction or explicitly stop when no
  primary direction was authorized.
- Run 07 showed that an author can accept a primary thread while revising the
  treatment of a secondary goal and an authority boundary.
- Run 06 produced no `StoryIdentity`; the transcript still contained a clear
  unresolved choice and a continuation decision.
- The evaluator recorded no facilitator rescue, role drift, or unnoticed
  premise-intent loss in these six rehearsals.

### Interpretations

These observations suggest that the v1.2 protections are operationally useful
as protocol devices. They do not establish that human authors will notice the
same distinctions, understand the same vocabulary, or value the same
recommendations. The all-pass result is also compatible with a shared-agent
bias: the packet designer, persona, and evaluator may share assumptions about
what a good interaction should look like.

### Candidate interaction invariants

These are candidates for protocol and later product-design testing. They are
not new semantic layers, runtime rules, schemas, or approved implementation
requirements.

| Candidate invariant | v1.2 evidence | What would disconfirm it |
|---|---|---|
| Proposals and canon remain separate. | Every run labeled the direction `PROPOSED`; author acceptance or revision followed the paraphrase. | A participant treats a recommendation as already accepted, or a packet makes the distinction impossible to explain. |
| Every important premise intention receives an explicit disposition. | Runs 01, 05, and 07 used the preservation map to mark primary, supporting, deferred, unresolved, or constrained intentions. | An intention disappears, becomes background without authorization, or cannot be located in the proposed direction. |
| Primary-thread selection requires author ratification. | Runs 01, 05, 06, and 07 asked for an explicit primary-thread decision before Identity. | The flow generates or treats Identity as settled before the author chooses the center. |
| An unresolved primary choice can produce a safe triage stop. | Run 06 stopped without forcing Identity and named the decision needed to continue. | The packet pressures the author into a center, or a stop has no actionable continuation. |
| Constraints are translated into observable behavior. | Run 04 and run 07 converted agency and resident-authority language into actions characters may or may not take. | The persona can repeat a constraint but cannot say how a story would violate it. |
| Required context is separated from deferred context. | Run 03 and the other dense packets marked only decision-relevant context as required. | Optional lore is required before a decision, or deferral hides a premise commitment. |
| A completed or stopped flow ends with an explicit next decision. | All six transcripts ended with a creative decision or a safe-stop continuation decision. | The author leaves with a packet but cannot say what to decide next. |

## Candidate future Auteur capabilities

The following capabilities are possible product directions suggested by the
evidence. They are deliberately phrased as hypotheses for later design work:

1. A premise inventory that preserves the raw premise beside each proposed
   disposition.
2. A primary-thread gate that blocks or pauses an Identity proposal until the
   author accepts, revises, or declines the recommendation.
3. A preservation map that makes supporting, deferred, and unresolved
   intentions inspectable without pretending they are canon.
4. A constraint-to-behavior view that shows must, must-not, and authority
   examples in plain language.
5. A required/deferred context control that postpones worldbuilding which does
   not change the current decision.
6. A bounded revision view with before/after commitments and provenance.
7. A safe-stop state that explains why no proposal was generated and names the
   next decision required to continue.
8. A next-decision handoff that makes continued author work explicit.

These are not authorization to change Auteur. Any implementation would require
a later approved product-design decision and must preserve the canonical
architecture and explicit author authority.

## What v1.2 does not establish

The six rehearsals cannot establish:

- human creative-beginner comprehension or success rates;
- whether the recommendation is actually the strongest direction for a human
  author;
- whether the vocabulary transfers outside these prepared premises;
- whether people prefer a preservation map, safe stop, or bounded revision;
- whether the flow creates value, reduces abandonment, or supports continued
  writing;
- which browser, TUI, editor, CLI, or other surface should be built;
- whether the candidate invariants generalize beyond Book-level
  premise-to-Identity work.

The most important bias is single-agent coupling: one coding agent generated
the persona and evaluator in separate passes, while the packet was manually
prepared by the same research process. The persona was synthetic, the
evaluator saw the same domain vocabulary, and no independent human observer
was present. These limitations make the evidence suitable for protocol
rehearsal, not product validation.

## Interim decision and next experiment

V1.2 is coherent enough to justify an adversarial protocol experiment, but not
enough to freeze the procedure for human research. The all-pass result needs
negative controls that deliberately remove a preservation entry, weaken an
observable constraint, or blur the ratification boundary.

The next experiment is [v1.3 adversarial stress simulation](premise-to-story-identity-stress-simulation-v1-3.md).
It holds the premise constant and mutates the packet so evaluator sensitivity
can be tested directly. Its decision gate is protocol readiness only. Even a
successful v1.3 gate would not validate the product or authorize runtime work;
bounded human research would remain the next evidence step.

## Append-only rule

Later synthesis rounds must be appended under a new protocol-version heading.
Do not rewrite v1.2 observations to fit later outcomes, and do not combine
synthetic evidence with the human findings document.
