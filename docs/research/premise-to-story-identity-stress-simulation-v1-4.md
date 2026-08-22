# Premise-to-StoryIdentity Stress Simulation v1.4 Registry

Status: `INTERNAL SIMULATION EVIDENCE`

This registry records a synthetic adversarial rehearsal of the v1.4
pre-Identity authority gate. It is not human participant research,
creative-beginner validation, usability validation, or product validation.

## Purpose

V1.3 showed the same authority failure twice: Identity appeared before
primary-thread ratification, and provisional wording did not prevent the
persona from treating it as effectively chosen. V1.4 tests two protections
separately and together:

1. ordering: no Identity content before primary-thread authorization;
2. status: every pre-canon Identity proposal is explicitly marked
   `PROPOSED / NOT CANON`.

The [v1.4 protocol section](premise-to-story-identity-stress-simulation.md#protocol-v14---pre-identity-authority-gate)
defines the gate. V1.3 and earlier evidence remain preserved in their existing
registry, archive, and standalone records.

## Fixed configuration

| Field | Value |
|---|---|
| Protocol | `v1.4` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Scope | Book-level `StoryIdentity` only |
| Frozen premise basis | v1.2 run `stress-v12-primary-secondary-07` |
| Human participants | `0` |
| Run count | `4` |
| Transcript policy | Complete participant-facing packet, persona transcript, evaluator-only disclosure, and separate evaluator transcript per run |

## Run index

| Run ID | Packet condition | Normal classification | Mutation detection | Run record |
|---|---|---|---|---|
| `stress-v14-control-13` | Correct pre-Identity gate and explicit proposal status | `SIMULATION_PASS` | `CONTROL` | [control 13](premise-to-story-identity-stress-simulation-v1-4-runs/stress-v14-control-13.md) |
| `stress-v14-mutation-order-14` | Identity shown before primary-thread ratification; status explicit | `SIMULATION_PASS` | `DETECTED` | [order mutation 14](premise-to-story-identity-stress-simulation-v1-4-runs/stress-v14-mutation-order-14.md) |
| `stress-v14-mutation-status-15` | Identity shown after ratification; proposal status ambiguous | `SIMULATION_PASS` | `DETECTED` | [status mutation 15](premise-to-story-identity-stress-simulation-v1-4-runs/stress-v14-mutation-status-15.md) |
| `stress-v14-mutation-combined-16` | Identity shown early and proposal status ambiguous | `SIMULATION_FAILURE` | `DETECTED` | [combined mutation 16](premise-to-story-identity-stress-simulation-v1-4-runs/stress-v14-mutation-combined-16.md) |

`Normal classification` applies the ordinary v1.4 rubric to the observed
interaction. `Mutation detection` is a separate evaluator result. A detected
mutation does not erase an author-facing failure.

## Aggregate result

- `SIMULATION_PASS`: three;
- `SIMULATION_FAILURE`: one;
- `SIMULATION_INCONCLUSIVE`: zero;
- mutation detection: three of three `DETECTED`;
- human participants: `0`;
- role separation: preserved in all records.

The isolated ordering and status mutations were noticed by the persona and
kept from becoming accepted canon. The combined mutation reproduced the v1.3
authority failure: the persona treated the Identity direction as chosen before
explicit authorization. The evaluator detected the defect, but evaluator
detection did not make the author-facing flow safe.

## Decision gate

Decision: `NOT READY TO FREEZE FOR HUMAN RESEARCH`.

The v1.4 control passed and all mutations were detected, but the combined
mutation still produced premature author acceptance. The protocol should not
be frozen until a further version demonstrates that the combined defect is
blocked or safely rejected by the participant-facing flow.

This is a protocol-readiness decision only. It does not authorize runtime,
schema, CLI, semantic architecture, product-surface, or human-research claims.

## Candidate Auteur implications

These are product-design hypotheses, not approved requirements:

- an interaction state may need to prevent Identity rendering until the
  primary-thread decision is recorded;
- every proposed Identity view may need machine-checkable and plain-language
  `PROPOSED / NOT CANON` status;
- author authorization may need provenance that records the decision before
  proposal display;
- the product may need a safe-stop state when the authorization sequence is
  incomplete.

The simulations do not authorize implementing these hypotheses or choosing a
browser, TUI, editor, or CLI surface.

## Limitations

- All records are synthetic agent rehearsals with zero human participants.
- One coding agent produced the persona and evaluator in separate passes.
- The same frozen premise was used for all four runs, so premise
  generalization was not tested.
- Mutations were hand-designed and do not estimate real product failure rates.
- Persona detection of the isolated mutations does not establish human
  comprehension.

## Append-only rule

Do not rewrite v1.2, v1.3, or this v1.4 evidence. If the packet, prompt, guide,
persona, evaluator, or mutation method changes materially, preserve the
affected record and create v1.5. Keep all records separate from
`premise-to-story-identity-findings.md`, which remains reserved for human
participant evidence.

## Append-only continuation: combined repeat run 17

The four-run v1.4 baseline remains unchanged. Run 17 repeats the combined
ordering-and-status mutation with the alternate label `DRAFT STORY SHAPE`; it
does not change the v1.4 protocol.

| Run ID | Packet condition | Normal classification | Mutation detection | Run record |
|---|---|---|---|---|
| `stress-v14-mutation-combined-repeat-17` | Identity shown before ratification with ambiguous `DRAFT STORY SHAPE` status | `SIMULATION_FAILURE` | `DETECTED` | [combined repeat 17](premise-to-story-identity-stress-simulation-v1-4-runs/stress-v14-mutation-combined-repeat-17.md) |

### Continuation result

Including run 17, the v1.4 evidence contains five records:

- `SIMULATION_PASS`: three;
- `SIMULATION_FAILURE`: two;
- `SIMULATION_INCONCLUSIVE`: zero;
- mutation detection: four of four `DETECTED`;
- human participants: `0`.

The combined authority failure reproduced with a different label. The persona
again treated Identity-shaped content as selected before primary-thread
ratification, while the evaluator detected both defects. This strengthens the
v1.5 recommendation: the participant-facing flow must prevent Identity content
from being shown before authorization, rather than relying on wording alone.

The decision remains `NOT READY TO FREEZE FOR HUMAN RESEARCH`. Run 17 is
synthetic repeatability evidence, not human participant evidence or product
validation.
