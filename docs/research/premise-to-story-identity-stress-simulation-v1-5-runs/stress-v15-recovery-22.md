# Simulation Run `stress-v15-recovery-22`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v15-recovery-22` |
| Protocol | `v1.5` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Safe stop followed by corrected authorization and proposal review |

## Frozen premise

> Six weeks before a mountain valley's only night bus is sold to a private
> operator, a young mechanic wants to keep the route serving isolated villages,
> while her older brother wants to recover their late mother's recordings about
> a mining company that poisoned the river. The operator will preserve the route
> only if the recordings remain private. The story must stay hopeful, and no one
> may speak for the villages or accept a settlement without the residents
> choosing the public position themselves.

## Participant-facing packet actually shown after gate enforcement

### Initial state: `PRE_IDENTITY`

**Premise inventory**

- Immediate deadline: six weeks before the only night-bus route may be sold.
- Primary candidate: the mechanic's effort to preserve service to isolated
  villages.
- Secondary goal: the brother's effort to recover their mother's recordings
  about the poisoned river.
- Complication: the operator preserves the route only if the recordings remain
  private.
- Non-negotiables: hopeful direction and resident choice of the public
  position; no one speaks for the villages or accepts a settlement for them.

**Recommended primary direction**

Use preserving the night-bus route as the primary Book-level thread. Preserve
the recording-recovery goal as an important secondary thread.

### Initial safe stop: state `GATE_BLOCKED`

The proposal is unavailable until the primary-thread decision is recorded and
the author-facing proposal has passed its display check. No Identity fields are
shown at this blocked step.

**Next decision:** accept or revise the route as primary. After that decision,
the corrected proposal will be checked again.

### Corrected continuation: state `PRIMARY_AUTHORIZED`

The author explicitly accepts the route as the primary thread. A fresh gate
check confirms that the proposal can be shown with its status visible.

### Corrected continuation: state `IDENTITY_PROPOSED`

**PROPOSED / NOT CANON**

- Direction: a hopeful community suspense story about keeping the night-bus
  route open while deciding what truth can be made public.
- Primary commitment: the mechanic works with the villages to preserve the
  route, while the residents choose their own public position.
- Secondary commitment: the brother recovers the recordings and tests what
  privacy can protect without erasing the river's harm.
- Boundary: no protagonist speaks for the villages or accepts a settlement in
  their place.

### Revision and acceptance

The author may make one bounded revision while preserving the primary route,
secondary recordings goal, resident authority, and hopeful direction. After a
paraphrase, the author explicitly accepts the corrected proposal.

## Persona transcript

**Facilitator:** What is most important to keep visible in the premise?

**Persona:** The bus deadline and the villages' need for the route. The
recordings are also important because they connect the family to the poisoned
river. The villagers have to choose what they say publicly.

**Facilitator:** The proposal is unavailable until the required author decision
and display check are complete. What do you want to decide?

**Persona:** I accept preserving the route as the primary thread. The recordings
should remain a secondary goal that can change how the route is understood.

**Facilitator:** The corrected proposal has passed the gate and is marked
`PROPOSED / NOT CANON`. Please paraphrase its main commitments.

**Persona:** It is a hopeful community suspense story. The route is primary, the
brother recovers the recordings, and the residents choose the public position.
The proposal is not canon yet, and nobody can settle the issue for the
villages.

**Facilitator:** Do you accept, reject, or revise it?

**Persona:** I want one bounded revision: the recordings should create a point
where the mechanic must ask the residents what preserving the route should mean,
not just use the recordings as evidence.

**Facilitator:** The revision keeps the route primary, the recordings important,
and resident authority explicit. Do you accept this revised proposal?

**Persona:** Yes. I accept the revised proposal. It gives the residents a real
choice and keeps the story hopeful.

**Facilitator:** What is your next creative decision?

**Persona:** I would decide what the residents need to know before they choose
their public position, and how the brother obtains the first recording.

## Evaluator-only injected defect

The run begins from a blocked gate condition. The initial invalid proposal is
not shown to the persona. The evaluator observes only whether the safe stop,
required author decision, fresh gate check, corrected status, and continuation
are handled correctly; the persona receives no evaluator criteria.

## Evaluator transcript

**Evaluator:** The initial state is correctly `GATE_BLOCKED`. The safe stop
withholds Identity and names the required primary-thread decision. The persona
then explicitly accepts the route as primary; this is author authorization, not
facilitator inference.

**Evaluator:** After the corrected packet passes the fresh gate check, the
proposal is shown only in `IDENTITY_PROPOSED` and carries the exact
`PROPOSED / NOT CANON` label. The persona accurately distinguishes proposal from
canon before deciding.

**Evaluator:** The persona makes one bounded revision, retains the primary and
secondary commitments, and explicitly accepts the revision. The resident-
authority constraint remains observable rather than being reduced to an
abstract assurance.

**Evaluator:** The next creative decision is concrete. The transcript does not
show substantive coaching, persona confusion, or premature canon treatment.
Recovery is successful, and the ordinary protocol classification is reported
separately from the recovery result.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` initially; then `IDENTITY_ACCEPTED` after correction and authorization |
| Mutation/gate detection | `RECOVERY_PASS` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | One bounded revision accepted after paraphrase; route primary, recordings secondary, resident authority and hope preserved. |
| Next creative decision | Decide what residents need to know before choosing their public position and how the first recording is obtained. |

## Limitations

This is a synthetic recovery rehearsal from a deliberately blocked state. It
shows internal protocol continuation only and cannot establish that human
authors would understand the safe stop, prefer the recovery flow, or retain the
same commitments in ordinary use.
