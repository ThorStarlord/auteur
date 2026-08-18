# Premise-to-StoryIdentity Simulation Protocol

This protocol defines an internal `simulated creative-beginner walkthrough`
for rehearsing the premise-to-`StoryIdentity` research flow.

It is not a substitute for human participant research. Agent runs may expose
protocol ambiguity, missing proposal information, role drift, or authority-
boundary failures, but they cannot establish human comprehension, motivation,
emotional response, or product value.

## Relationship to the human experiment

The human experiment remains defined in
[Premise-to-StoryIdentity Research Experiment](premise-to-story-identity-experiment.md).

Simulation results must:

- be labeled as simulation results;
- never count toward the human study's 5–8 participant stopping rule;
- never be written into the human findings document as participant evidence;
- never be described as validation with creative beginners;
- remain separate from any later anonymized human synthesis.

The simulation does not change Auteur's system definition, semantic layers,
`StoryIdentity` authority, or product-surface hypotheses.

## Simulation persona

Use one fixed persona card for the first rehearsal round:

```text
Role: creative beginner

Experience:
- Inexperienced with long-form narrative planning.
- Technically capable, but must not use technical knowledge to compensate for
  narrative uncertainty.
- Does not know Auteur's internal vocabulary.

Behavior:
- Brings a personal 1–3 sentence premise.
- Asks for plain-language explanations when confused.
- Can express preferences and reject proposals.
- May struggle to name want, resistance, stakes, or change directly.
- Distinguishes supplied facts from inference.
- May accept, reject, or request one revision based on premise fidelity.

Boundary:
- Do not reveal the simulation rubric or expected failure modes to the persona.
- Do not let the persona act as a technical expert, product designer, or
  narrative-engineering critic.
```

The fixed persona improves repeatability. Persona variants should be added
only after the first rehearsal round exposes a concrete need for them.

## Scenario set

Run one walkthrough for each fixed scenario type:

1. **Clear premise:** an ordinary 1–3 sentence premise with a recognizable
   central situation.
2. **Sparse premise:** a premise that intentionally leaves important narrative
   commitments unspecified.
3. **Explicit constraint:** a premise containing a non-negotiable author
   constraint that the proposal could accidentally violate.

The simulated persona starts from the raw premise. Do not provide a completed
`StoryIdentity` as an input. Keep the scenarios fixed so repeated rehearsals
remain comparable.

## Role separation

Separate the persona from the evaluator:

- The persona receives only the participant-facing premise, proposal packet,
  and neutral facilitator prompts.
- The persona prompt must not contain the success criteria or expected failure
  modes.
- Capture the full walkthrough transcript.
- A separate evaluation pass applies the simulation rubric.

If the same coding agent performs both roles, run them as separate passes and
do not expose the evaluator instructions during the persona pass.

## Walkthrough flow

Use the human protocol's sequence without changing its authority boundary:

1. Start with the raw premise.
2. Present the plain-language premise reflection.
3. Present one recommended direction, rationale, and rejected alternatives.
4. Present the compact proposed `StoryIdentity`.
5. Ask for a plain-language explanation of the direction and commitments.
6. Request an explicit accept, reject, or revision decision.
7. Allow one author-directed revision and show the before/after commitments.
8. Ask for the next useful creative decision.

The facilitator must use only neutral prompts. The evaluator must distinguish
persona confusion from a packet omission, protocol ambiguity, authority-boundary
failure, or role drift.

## Simulation criteria

Classify a walkthrough as `SIMULATION_PASS` when the persona can:

- follow the documented flow without undocumented facilitator help;
- explain the proposed direction in ordinary language;
- identify what is proposed versus accepted;
- make an accept, reject, or revision choice consistent with its stated
  premise;
- identify the next creative decision;
- expose any confusing vocabulary, missing packet information, or authority-
  boundary ambiguity for the evaluator to record.

Classify as `SIMULATION_FAILURE` when the walkthrough exposes:

- proposal/canon confusion;
- silent mutation or an implied loss of author authority;
- a proposal that violates an explicit premise constraint without surfacing it;
- a facilitator prompt that supplies substantive narrative reasoning;
- persona role drift into technical expertise or evaluator behavior;
- an interaction step that cannot be completed from the documented materials.

Classify as `SIMULATION_INCONCLUSIVE` when the transcript is incomplete, the
persona and evaluator roles were not separated, or the scenario cannot support
a clear interpretation.

These classifications assess protocol quality only. They do not map to the
human experiment's participant-level success or failure criteria.

## Stopping and versioning

- Run one walkthrough for each of the three fixed scenarios.
- Pause immediately for any authority-boundary failure, proposal/canon
  confusion, or role drift.
- Record the failure before changing the guide, packet, or prompts.
- If a material change is made, increment the protocol version and rerun the
  affected scenario once.
- Stop when all three baseline scenarios complete without critical simulation
  failures, or when a revised rerun shows that the same failure persists.

Simulation stopping does not authorize product implementation or surface
selection. It only determines whether the research protocol is internally
coherent enough to take to human participants.

## Simulation record

Keep agent transcripts and evaluation records separate from human participant
records. Each record should include:

```text
Record type: SIMULATION
Scenario: CLEAR / SPARSE / EXPLICIT_CONSTRAINT
Protocol version:
Persona version:
Evaluator version:

Result: SIMULATION_PASS / SIMULATION_FAILURE / SIMULATION_INCONCLUSIVE
Observed authority-boundary issue:
Observed proposal mismatch:
Observed vocabulary or packet issue:
Observed role drift:
Required protocol change:
```

## Findings

The versioned baseline report is maintained in the
[Simulation Findings](premise-to-story-identity-simulation-findings.md)
document. It is internal simulation evidence and is not human participant
research.

The separate v1.1 stress variant is documented in the
[Stress Simulation Protocol](premise-to-story-identity-stress-simulation.md)
and its [Stress Simulation Findings](premise-to-story-identity-stress-simulation-findings.md)
report. Those results are also internal simulation evidence only.
