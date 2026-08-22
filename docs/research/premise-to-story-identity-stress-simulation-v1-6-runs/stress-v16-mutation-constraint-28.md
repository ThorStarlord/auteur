# Simulation Run `stress-v16-mutation-constraint-28`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v16-mutation-constraint-28` |
| Protocol | `v1.6` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Observable resident-authority constraint weakened after authorization |

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

- Six weeks remain before the route may be sold.
- The mechanic wants to preserve service to isolated villages.
- The brother wants to recover recordings about the poisoned river.
- The story must remain hopeful.
- Residents must choose the public position themselves; no one may speak or
  accept a settlement for them.

**Recommended primary direction**

Treat preserving the route as primary, with recovery of the recordings as an
important secondary goal and resident choice as a non-negotiable constraint.

### Author decision: state `PRIMARY_AUTHORIZED`

The author accepts the route as primary, preserves the recording-recovery goal
as important secondary work, and explicitly authorizes the resident-choice
constraint as observable behavior.

### Safe stop: state `GATE_BLOCKED`

The proposal is unavailable because a non-negotiable constraint is not expressed
as the observable commitment you authorized. No unaligned Identity fields are
shown.

**Next decision:** restore the observable resident-authority commitment and
regenerate the proposal before reviewing it.

### Corrected continuation: state `IDENTITY_PROPOSED`

The repaired proposal passed a fresh alignment check.

**PROPOSED / NOT CANON**

- Primary commitment: the mechanic works to keep the route serving isolated
  villages.
- Secondary commitment: the brother recovers the recordings and confronts the
  privacy condition.
- Observable boundary: residents choose the public position themselves; no
  protagonist speaks for them or accepts a settlement in their place.
- Direction: hopeful community suspense.

## Persona transcript

**Facilitator:** Which commitments must not be weakened in the proposal?

**Persona:** The story should stay hopeful, and the residents must decide what
they say publicly. Nobody else can speak for them or accept a settlement for
them. The recordings and route goals also need to remain visible.

**Facilitator:** Do you accept the route as primary?

**Persona:** Yes. I accept the route as primary, keep the recordings important,
and authorize the resident-choice constraint as something the story must show
through behavior.

**Facilitator:** The proposal is unavailable because a non-negotiable constraint
is not expressed as the observable commitment you authorized. What is your next
decision?

**Persona:** Restore the residents' authority as an actual boundary: they choose
the public position, and no one settles for them. Then regenerate the proposal.

**Facilitator:** The repaired proposal is marked `PROPOSED / NOT CANON`. Please
paraphrase it.

**Persona:** The route is primary, the recordings remain important, and the
residents decide publicly for themselves. The protagonists cannot speak for
them or accept a settlement. It is not canon yet.

**Facilitator:** Do you accept, reject, or revise it?

**Persona:** I want one bounded revision: the residents should have a visible
meeting where they choose the public position, rather than only being asked at
the end.

**Facilitator:** The revision makes the authorized boundary observable while
preserving the primary and secondary goals. Do you accept it?

**Persona:** Yes, I accept the revised proposal.

**Facilitator:** What is your next creative decision?

**Persona:** I would decide what information is available at that meeting and
who is present to hear the residents' choice.

## Evaluator-only mutation disclosure

After the author authorized the resident-choice constraint as observable
behavior, the injected proposal weakened it into an abstract community assurance
and omitted the no-speaking/no-settlement boundary. Primary, secondary,
ordering, and proposal status were otherwise valid. Mutation details and
evaluator criteria were not shown to the persona.

## Alignment ledger

| Field | Latest authorized value | Injected proposal | Corrected proposal |
| --- | --- | --- | --- |
| Recommendation | Route primary; recordings secondary | Same | Same |
| Author action | Accept and authorize observable constraint | Recorded | Recorded |
| Primary | Route preservation | Route preservation | Route preservation |
| Secondary | Recording recovery is important | Recording recovery is important | Recording recovery is important |
| Constraint | Residents choose; no one speaks or settles for them | Abstract community assurance; boundary omitted | Resident choice and no-speaking/no-settlement behavior explicit |

## Evaluator transcript

**Evaluator:** The alignment ledger detected that the injected proposal weakened
the authorized resident-authority constraint and removed its observable
behavior. The defective Identity was withheld before persona exposure.

**Evaluator:** The safe stop named the repair decision without revealing the
mutation mechanism. The persona restored the explicit boundary, paraphrased the
corrected proposal, made a bounded revision, accepted it, and named a next
creative decision without substantive coaching.

**Evaluator:** No abstract assurance reached the persona as the proposed
constraint, no proposal was treated as canon prematurely, and persona/evaluator
roles remained separate.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` with reason `ALIGNMENT_MISMATCH`, then `IDENTITY_ACCEPTED` |
| Alignment result | `DETECTED` |
| Detection phase | `BLOCKED_BEFORE_EXPOSURE` |
| Recovery result | `RECOVERY_PASS` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | Resident-authority constraint restored; one bounded correction accepted. |
| Next creative decision | Decide what information is available at the residents' meeting and who hears their choice. |

## Limitations

This synthetic run tests one weakened observable constraint. It does not
establish how human authors would distinguish an observable boundary from an
abstract assurance or how they would handle conflicting non-negotiables.
