# Premise-to-StoryIdentity Stress Simulation v1.3 Registry

Status: `INTERNAL SIMULATION EVIDENCE`

This registry indexes a controlled adversarial rehearsal of the Book-level
premise-to-`StoryIdentity` protocol. Every record is synthetic agent evidence.
It is not human participant research, creative-beginner validation, usability
validation, or product validation.

## Purpose

V1.2 produced six positive rehearsals. V1.3 holds the premise constant and
tests whether an evaluator can detect three deliberately defective participant-
facing packets while a valid control preserves the existing flow. The defects
are test mutations, not proposed product behavior.

The v1.2 registry and [historical findings archive](premise-to-story-identity-stress-simulation-findings.md)
remain unchanged. The [v1.2 learning synthesis](premise-to-story-identity-stress-simulation-learning-synthesis.md)
records why this adversarial round was selected.

## Fixed configuration

| Field | Value |
|---|---|
| Protocol | `v1.3` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Scope | Book-level `StoryIdentity` only |
| Frozen premise basis | v1.2 run `stress-v12-primary-secondary-07` |
| Human participants | `0` |
| Run count | `4` |
| Transcript policy | Complete participant-facing packet, persona transcript, and separate evaluator transcript per run |

The protocol definition is in the [v1.3 section of the stress simulation
protocol](premise-to-story-identity-stress-simulation.md#protocol-v13--controlled-mutation-challenges).
Run records are stored in
[the v1.3 run directory](premise-to-story-identity-stress-simulation-v1-3-runs/).

## Run index

| Run ID | Packet condition | Normal classification | Mutation detection | Run record |
|---|---|---|---|---|
| `stress-v13-control-08` | Valid, unmodified v1.2 packet | `SIMULATION_PASS` | `CONTROL` | [control 08](premise-to-story-identity-stress-simulation-v1-3-runs/stress-v13-control-08.md) |
| `stress-v13-mutation-thread-09` | Secondary recordings goal demoted to background context | `SIMULATION_PASS` | `DETECTED` | [thread mutation 09](premise-to-story-identity-stress-simulation-v1-3-runs/stress-v13-mutation-thread-09.md) |
| `stress-v13-mutation-constraint-10` | Resident-authority constraint reduced to an abstract principle | `SIMULATION_PASS` | `DETECTED` | [constraint mutation 10](premise-to-story-identity-stress-simulation-v1-3-runs/stress-v13-mutation-constraint-10.md) |
| `stress-v13-mutation-authority-11` | Identity shown before primary-thread ratification with unclear status | `SIMULATION_FAILURE` | `DETECTED` | [authority mutation 11](premise-to-story-identity-stress-simulation-v1-3-runs/stress-v13-mutation-authority-11.md) |

`Normal classification` applies the ordinary v1.2 rubric to the observed
interaction. `Mutation detection` is a separate evaluator result. A detected
mutation does not turn a defective packet into a valid protocol run.

## Aggregate v1.3 result

- Valid controls: one `SIMULATION_PASS`.
- Mutation runs: two `SIMULATION_PASS`, one `SIMULATION_FAILURE`.
- Mutation detection: three of three `DETECTED`.
- Human participants: `0`.
- Role separation: preserved in the records; evaluator criteria were not shown
  to the persona.

The thread and constraint mutations were surfaced by the persona and repaired
through explicit author action. The authority mutation was detected by the
evaluator, but the persona initially treated a prematurely shown Identity as
settled direction. That is an interaction failure even though the evaluator
recognized it. The protocol therefore did not satisfy the full freeze gate.

## Decision gate

Decision: `NOT READY TO FREEZE FOR HUMAN RESEARCH`.

The control passed and all three mutations were detected, but the authority
mutation demonstrated that a packet can still blur the ratification boundary
when Identity appears before primary-thread authorization. No runtime artifact
was written, but the simulated interaction did not preserve the intended
authority boundary. A v1.4 protocol should add a hard participant-facing gate:
no Identity content may appear until the primary-thread decision is recorded,
and every Identity display must carry explicit `PROPOSED / NOT CANON` status.

This is a protocol-readiness decision only. It does not authorize runtime
implementation, product-surface selection, or claims about creative beginners.

## Limitations

- All records are synthetic agent rehearsals with zero human participants.
- The same coding agent produced the persona and evaluator in separate passes.
- The premise and most packet content are inherited from v1.2, so this is not a
  broad premise-generalization test.
- The mutations are hand-designed and do not estimate the frequency of real
  product failures.
- Detection by an evaluator does not prove a human author would notice the
  same defect.

## Append-only continuation

Do not rewrite v1.2 or these v1.3 records. If the packet, guide, prompt,
persona, evaluator, or mutation method changes materially, create a v1.4
protocol and new run records. Keep all synthetic evidence separate from
`premise-to-story-identity-findings.md`, which remains reserved for human
participant evidence.

## Append-only continuation: authority repeat run 12

The four-run v1.3 baseline above remains unchanged. Run 12 repeats the
existing authority mutation with an alternate participant-facing status label;
it does not introduce a new mutation family or change the v1.3 protocol.

| Run ID | Packet condition | Normal classification | Mutation detection | Run record |
|---|---|---|---|---|
| `stress-v13-mutation-authority-repeat-12` | Identity shown before primary-thread ratification with `WORKING DIRECTION` status | `SIMULATION_FAILURE` | `DETECTED` | [authority repeat 12](premise-to-story-identity-stress-simulation-v1-3-runs/stress-v13-mutation-authority-repeat-12.md) |

### Continuation result

Including run 12, the v1.3 evidence contains five records:

- `SIMULATION_PASS`: three;
- `SIMULATION_FAILURE`: two;
- `SIMULATION_INCONCLUSIVE`: zero;
- mutation detection: four of four mutation runs `DETECTED`;
- human participants: `0`.

The authority-boundary failure reproduced with a different provisional-sounding
label. The persona again treated the Identity direction as effectively chosen
before primary-thread ratification, while the evaluator identified the defect
from the transcript. This strengthens the existing v1.4 recommendation: put a
hard primary-thread gate before any Identity content and label every pre-
ratification Identity view `PROPOSED / NOT CANON`.

The overall decision remains `NOT READY TO FREEZE FOR HUMAN RESEARCH`. Run 12
is synthetic repeatability evidence, not human participant evidence or product
validation.
