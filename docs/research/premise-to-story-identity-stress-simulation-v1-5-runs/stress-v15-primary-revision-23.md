# Simulation Run `stress-v15-primary-revision-23`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v15-primary-revision-23` |
| Protocol | `v1.5` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Author rejects the recommended primary thread and explicitly revises it during recovery |

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
- Candidate thread: the mechanic's effort to keep the route serving isolated
  villages.
- Competing thread: the brother's effort to recover recordings about the
  mining company's poisoned-river history.
- Connection: the operator preserves the route only if the recordings remain
  private.
- Non-negotiables: the story stays hopeful, and residents choose the public
  position themselves. No one speaks for them or accepts a settlement for them.

**Recommended primary direction**

Treat preserving the night-bus route as the primary Book-level thread. Preserve
recovery of the recordings as an important secondary goal.

### Initial safe stop: state `GATE_BLOCKED`

The proposal is unavailable until the author explicitly accepts or revises the
recommended primary direction. No Identity fields are shown at this blocked
step.

**Next decision:** accept the route as primary or revise the primary direction.

### Author revision: state `PRIMARY_AUTHORIZED`

The author rejects the recommended primary direction and explicitly revises it:
the brother's recovery of the recordings and the truth about the poisoned river
will be the primary Book-level thread. Keeping the night-bus route serving the
villages remains an important secondary goal. The resident-authority and hopeful
constraints remain unchanged.

The revised primary-thread decision is now authorized. A fresh gate check may
show the corrected proposal.

### Corrected proposal: state `IDENTITY_PROPOSED`

**PROPOSED / NOT CANON**

- Direction: a hopeful community mystery about recovering the recordings while
  deciding what truth can be made public without taking the residents' choice
  away from them.
- Primary commitment: the brother recovers and interprets the recordings about
  the poisoned river, while the community decides what follows from them.
- Secondary commitment: the mechanic works to keep the night-bus route serving
  the villages and tests whether its future can coexist with private evidence.
- Boundary: no protagonist speaks for the villages or accepts a settlement in
  their place.

## Persona transcript

**Facilitator:** What intentions do you see in the premise?

**Persona:** The bus route has the urgent deadline, but the recordings explain
why the river and the operator's condition matter. The villages need to decide
what they say publicly.

**Facilitator:** The recommended primary direction is preserving the night-bus
route. The proposal is unavailable until you accept or revise that direction.
What do you want to decide?

**Persona:** I do not accept the route as primary. I want to revise the primary
thread to the brother recovering the recordings and uncovering what happened to
the river. The route should remain an important secondary goal because it is how
the villages are connected.

**Facilitator:** Your revision is recorded. The brother's recording-recovery
thread is primary, the route is secondary, and the hopeful and resident-choice
constraints remain. Do you authorize this revised primary direction?

**Persona:** Yes. I explicitly authorize that revision.

**Facilitator:** The corrected proposal is now marked `PROPOSED / NOT CANON`.
Please paraphrase its main commitments.

**Persona:** The brother's recovery of the recordings is the main story thread.
The mechanic's route effort is still important. The story stays hopeful, and
the residents decide what to say publicly. This is a proposal, not canon.

**Facilitator:** Do you accept, reject, or revise the proposal?

**Persona:** I want one bounded revision: the brother should not decide what the
recordings mean by himself. He should need the residents' response before the
evidence becomes a public position.

**Facilitator:** The revision keeps the recordings primary, the route
secondary, and resident authority observable. Do you accept the revised
proposal?

**Persona:** Yes, I accept it.

**Facilitator:** What is your next creative decision?

**Persona:** I would decide who first hears the recording and what information
the residents need before choosing their public position.

## Evaluator-only disclosure

This is a recovery run seeded in `GATE_BLOCKED` before the author had accepted
or revised the primary-thread recommendation. The gate must not expose an
Identity proposal in that state. The evaluator did not disclose its criteria or
the seeded recovery condition to the persona.

## Evaluator transcript

**Evaluator:** The initial safe stop withheld all Identity fields and required an
explicit author decision. The persona rejected the recommended route primary
thread and supplied a coherent alternative rather than being pushed toward the
recommendation.

**Evaluator:** The revised primary-thread decision was explicitly authorized
before the proposal appeared. The corrected proposal carried the exact
`PROPOSED / NOT CANON` label, and the persona paraphrased the primary recording
goal, secondary route goal, hopeful direction, and resident-authority boundary.

**Evaluator:** The bounded revision strengthened the resident-authority
constraint without changing the author-selected primary direction. The persona
accepted it and named a concrete next creative decision without substantive
coaching.

**Evaluator:** No Identity was exposed before authorization, no proposal was
treated as canon, and no facilitator intervention supplied story content. This
is successful recovery evidence and is classified separately from ordinary
protocol performance.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` initially; then `IDENTITY_ACCEPTED` after explicit primary revision and recheck |
| Mutation/gate detection | `RECOVERY_PASS` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | Author rejected the recommended primary, explicitly authorized a recording-centered revision, then accepted one bounded proposal revision. |
| Next creative decision | Decide who first hears the recording and what residents need before choosing their public position. |

## Limitations

This synthetic run tests author rejection and revision of a recommended primary
thread during gate recovery. It does not establish that human authors would
prefer the alternative direction, understand authorization states, or retain
the same intentions in ordinary product use.
