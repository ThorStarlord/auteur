# Simulation Run `stress-v15-mutation-stale-primary-24`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v15-mutation-stale-primary-24` |
| Protocol | `v1.5` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Stale proposal retains the recommendation after an author-selected primary revision |

## Frozen premise

> Six weeks before a mountain valley's only night bus is sold to a private
> operator, a young mechanic wants to keep the route serving isolated villages,
> while her older brother wants to recover their late mother's recordings about
> a mining company that poisoned the river. The operator will preserve the route
> only if the recordings remain private. The story must stay hopeful, and no one
> may speak for the villages or accept a settlement without the residents
> choosing the public position themselves.

## Decision alignment record

| Decision field | Value |
| --- | --- |
| System recommendation | Night-bus route as primary Book-level thread |
| Author action | Reject recommendation and revise |
| Author-selected primary | Brother's recovery of the recordings and the poisoned-river truth |
| Preserved secondary | Mechanic's effort to keep the night-bus route serving isolated villages |
| Proposal primary actually shown | Night-bus route, retained from the rejected recommendation |
| Proposal status | `PROPOSED / NOT CANON` |

The final two primary-thread fields intentionally disagree. The proposal is
validly ordered and visibly provisional, but stale relative to the latest
authorized author decision.

## Participant-facing packet actually shown

### State: `PRE_IDENTITY`

**Premise inventory**

- Immediate deadline: six weeks before the only night-bus route may be sold.
- The mechanic wants to keep the route serving isolated villages.
- Her brother wants to recover recordings about the poisoned river.
- The operator's privacy condition connects the route and recording goals.
- The story must remain hopeful, and residents choose their own public position.
- No one speaks for the villages or accepts a settlement for them.

**Recommended primary direction**

Treat preserving the night-bus route as the primary Book-level thread. Preserve
recovering the recordings as an important secondary goal.

### Author decision: state `PRIMARY_AUTHORIZED`

The author rejects the recommendation and explicitly revises the primary
direction. The brother's recovery of the recordings and the truth about the
poisoned river are selected as the primary Book-level thread. The route remains
an important secondary goal. The hopeful and resident-authority constraints are
preserved.

### Proposal: state `IDENTITY_PROPOSED`

**PROPOSED / NOT CANON**

- Direction: a hopeful civic suspense story about keeping the night-bus route
  open while deciding what truth can be made public.
- Primary commitment: the mechanic organizes the effort to preserve the route.
- Secondary commitment: the brother recovers the recordings about the poisoned
  river.
- Boundary: the residents choose their public position, and no protagonist
  speaks for them or accepts a settlement in their place.

## Persona transcript

**Facilitator:** What intentions do you want to keep visible in the premise?

**Persona:** The bus route has the deadline and serves the villages. The
recordings explain the river problem and create a conflict about privacy. The
villagers need to choose what they say publicly, and the story should remain
hopeful.

**Facilitator:** The recommended primary direction is preserving the route. Do
you accept or revise that direction?

**Persona:** I reject it as the primary thread. I want the brother's recovery of
the recordings and the truth about the river to be primary. The route should
remain an important secondary goal because it connects the villages.

**Facilitator:** Is that your explicit primary-thread decision?

**Persona:** Yes. I authorize the recording-recovery thread as primary and keep
the route as secondary.

**Facilitator:** The proposal is marked `PROPOSED / NOT CANON`. Please paraphrase
its main commitments.

**Persona:** It says the mechanic's effort to keep the route open is the main
story, and the brother's recordings are secondary. But that is not the decision
I just made. I chose the recordings as primary, so this proposal is stale.

**Facilitator:** What decision do you want to make about the proposal?

**Persona:** I reject it as written. I want a new proposal with the recordings as
primary, the route as secondary, and the resident-choice boundary unchanged.

**Facilitator:** What is your next creative decision?

**Persona:** I would review the regenerated proposal and decide what the
residents need to know before choosing their public position.

## Evaluator-only injected defect

After the persona rejected the route recommendation and explicitly authorized
the recording-recovery thread as primary, the prepared proposal retained the
route as its primary commitment. Ordering and proposal-status fields remained
valid. The evaluator did not disclose the mutation mechanism or evaluator
criteria to the persona.

## Evaluator transcript

**Evaluator:** The ordering gate passed because primary-thread authorization
occurred before the proposal. The status gate also passed because the proposal
was visibly marked `PROPOSED / NOT CANON`. V1.5 therefore did not block the
stale-content mutation before exposure.

**Evaluator:** The persona independently detected the mismatch during
paraphrase. It accurately distinguished the earlier recommendation from the
author-selected primary, rejected the stale proposal, preserved the route as a
secondary goal, and retained the hope and resident-authority constraints.

**Evaluator:** No proposal was treated as canon. The facilitator did not supply
the mismatch diagnosis or story content; no substantive rescue was required.
The persona named a concrete next decision: review a regenerated proposal after
the recording-centered primary is restored.

**Evaluator:** The mutation was detected, but only after exposure to the
persona. This is not evidence that the v1.5 gate can block stale content before
exposure. It is evidence that the current protocol's ordering and status checks
do not cover proposal-to-authorization alignment.

## Results

| Field | Result |
| --- | --- |
| Gate result | `IDENTITY_PROPOSED` with stale content exposed after valid ordering and status checks |
| Mutation detection | `DETECTED` |
| Detection phase | After persona exposure; persona and evaluator independently identified the mismatch |
| Normal classification | `SIMULATION_PASS` |
| Persona treatment | Rejected the stale proposal; did not treat it as canon |
| Facilitator rescue | None substantive |
| Revision status | Primary-thread revision was authorized; stale proposal rejected; corrected proposal not generated in this run. |
| Next creative decision | Review a regenerated proposal with recordings primary, route secondary, and resident authority preserved. |

## Protocol implication

The run confirms a v1.5 coverage gap rather than invalidating the earlier
ordering and status results. A future protocol version could add an explicit
proposal-alignment check, stale-proposal invalidation, or regeneration state.
No v1.6 material was introduced during this run, so this record remains under
v1.5 and is not combined with a future protocol revision.

## Limitations

This is one synthetic stale-content mutation using the frozen premise. The
persona noticed the mismatch without substantive coaching, but that does not
establish that human authors would notice it or that they would prefer a
regenerated proposal. The run also does not test an author who accepts the
stale proposal, fails to notice it, or changes the primary thread repeatedly.
