# Simulation Run `stress-v15-mutation-combined-21`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v15-mutation-combined-21` |
| Protocol | `v1.5` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Combined authorization-order and proposal-status defect |

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

- The route may be sold in six weeks.
- The mechanic wants the route to keep serving isolated villages.
- The brother wants to recover the recordings about the poisoned river.
- Privacy, hope, and resident authority shape the possible choices.

**Recommended primary direction**

The mechanic's route-preservation effort is the recommended primary thread.
The recording-recovery effort remains an important secondary goal.

### Safe stop: state `GATE_BLOCKED`

The story-direction proposal is unavailable at this step. The author decision
needed to authorize a primary thread has not been recorded, and the proposal is
not ready for a valid author-facing review. No Identity fields are shown.

**Next decision:** decide whether the route is primary or revise that direction;
then review the corrected proposal only after the gate confirms that its status
and authorization are explicit.

## Persona transcript

**Facilitator:** What are the main intentions you want preserved?

**Persona:** Keeping the route open is the urgent goal. Recovering the recordings
is also important because it explains the river problem. The villagers should
decide their public position, and the story should stay hopeful.

**Facilitator:** The proposal is unavailable until the required author decision
and review conditions are recorded. What do you want to decide first?

**Persona:** I accept the route as the primary thread. The recordings remain a
secondary goal, and I do not want anyone deciding for the villages.

**Facilitator:** What will you decide next?

**Persona:** I will review the corrected proposal after the gate confirms that
the authorization and proposal status are explicit.

## Evaluator-only injected defect

The prepared combined mutation attempted to show Identity fields before
primary-thread authorization and removed the explicit `PROPOSED / NOT CANON`
status. Both defects were withheld by the v1.5 gate and were not present in the
participant-facing packet or persona transcript.

## Evaluator transcript

**Evaluator:** The gate evaluated ordering and status independently. It blocked
the attempted early presentation at `GATE_BLOCKED`; because the packet was
withheld at that point, the persona never saw either the premature Identity or
the missing-status version.

**Evaluator:** The safe stop did not disclose mutation details. It stated the
missing author decision and the need for a valid review condition, then named a
next decision. The persona retained the route, recordings, hope, and resident
authority intentions.

**Evaluator:** There was no persona confusion, no premature canon treatment,
and no evaluator coaching. This run ends at the safe stop and is not evidence
of the recovery sequence.

**Evaluator:** The combined mutation was `DETECTED` before exposure. The
ordinary classification is reported independently as `SIMULATION_PASS` because
the enforced protocol preserved the authority boundary.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` before Identity exposure |
| Mutation/gate detection | `DETECTED` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | No Identity revision attempted; primary-thread decision was recorded during the safe stop. |
| Next creative decision | Review a corrected proposal after authorization and explicit status are rechecked. |

## Limitations

This synthetic run tests the combined pre-exposure gate only. It does not show
whether a human would distinguish the two underlying defects, and it does not
replace the dedicated recovery run.
