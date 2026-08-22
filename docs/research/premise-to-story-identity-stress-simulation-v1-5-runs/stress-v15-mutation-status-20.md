# Simulation Run `stress-v15-mutation-status-20`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v15-mutation-status-20` |
| Protocol | `v1.5` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Explicit primary authorization followed by an unavailable proposal status |

## Frozen premise

> Six weeks before a mountain valley's only night bus is sold to a private
> operator, a young mechanic wants to keep the route serving isolated villages,
> while her older brother wants to recover their late mother's recordings about
> a mining company that poisoned the river. The operator will preserve the route
> only if the recordings remain private. The story must stay hopeful, and no one
> may speak for the villages or accept a settlement without the residents
> choosing the public position themselves.

## Participant-facing packet actually shown after gate enforcement

### State: `PRE_IDENTITY`

**Premise inventory**

- Six weeks remain before the night-bus route may be sold.
- The mechanic wants to preserve service to isolated villages.
- The brother wants to recover the recordings about the poisoned river.
- The operator's privacy condition links the route and recording goals.
- Hope and resident choice are explicit story boundaries.

**Recommended primary direction**

Use the mechanic's effort to keep the route open as the primary Book-level
thread, while preserving recovery of the recordings as an important secondary
goal.

### Author decision: state `PRIMARY_AUTHORIZED`

Do you accept the route as primary, or revise that choice?

**Persona decision recorded:** I accept the route as primary and keep the
recordings as an important secondary goal.

### Safe stop: state `GATE_BLOCKED`

The proposal cannot be shown yet because its proposal status is not explicit.
No Identity fields are shown. The proposal will be available only after its
status is repaired and the gate is checked again.

**Next decision:** confirm that the corrected proposal is clearly marked
`PROPOSED / NOT CANON` before reviewing it.

## Persona transcript

**Facilitator:** Which part of the premise should lead the Book?

**Persona:** The bus route. The deadline is clear and it affects the villages.
The recordings should remain a real secondary goal, not just background.

**Facilitator:** Do you accept the route as the primary thread?

**Persona:** Yes. I accept it as primary, with the recordings still important.

**Facilitator:** The proposal cannot be shown because its proposal status is not
explicit. What do you understand from that?

**Persona:** I understand that there is no proposal for me to accept yet. I
would want to see a clear label saying it is proposed and not canon before I
judge it.

**Facilitator:** What is your next creative decision?

**Persona:** I would decide whether the privacy condition first creates a choice
for the brother, the mechanic, or the residents, after the corrected proposal
is available.

## Evaluator-only injected defect

The prepared mutation removed the explicit `PROPOSED / NOT CANON` status from
the Identity proposal after primary authorization. The gate withheld the
proposal before persona exposure. The persona received no evaluator criteria
or mutation description.

## Evaluator transcript

**Evaluator:** The status defect was detected before exposure. Primary-thread
authorization was present, but the gate correctly treated missing status as a
separate blocking condition.

**Evaluator:** No Identity fields appeared in the participant-facing packet.
The safe stop explained the missing repair without presenting an unlabeled
proposal that could be treated as canon.

**Evaluator:** The persona understood the proposal/canon boundary and named the
required status repair without substantive coaching. The next creative decision
was explicit, although the run ended before a corrected proposal and bounded
revision.

**Evaluator:** The ordinary classification is `SIMULATION_PASS` because the
protocol safely withheld the invalid packet and preserved author authority. The
mutation outcome is independently `DETECTED`.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` before Identity exposure |
| Mutation/gate detection | `DETECTED` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | No proposal revision attempted; status repair required before review. |
| Next creative decision | Confirm explicit `PROPOSED / NOT CANON` status before reviewing the corrected proposal. |

## Limitations

This is synthetic evidence for status gating. It does not establish that human
authors would understand a missing status, nor does it test the complete
post-repair revision flow.
