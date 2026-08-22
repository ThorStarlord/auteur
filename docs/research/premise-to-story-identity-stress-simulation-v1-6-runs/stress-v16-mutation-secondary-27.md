# Simulation Run `stress-v16-mutation-secondary-27`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v16-mutation-secondary-27` |
| Protocol | `v1.6` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Important secondary intention silently dropped after authorization |

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

- The night-bus route may be sold in six weeks.
- The mechanic wants to keep the route serving isolated villages.
- The brother wants to recover recordings about the poisoned river.
- The operator's privacy condition creates a conflict between the goals.
- The story remains hopeful, and residents choose their public position.

**Recommended primary direction**

Use preserving the route as the primary Book-level thread while retaining
recovery of the recordings as an important secondary intention.

### Author decision: state `PRIMARY_AUTHORIZED`

The author accepts the route as primary and explicitly preserves the brother's
recording-recovery effort as an important secondary goal. The hopeful and
resident-authority constraints remain active.

### Safe stop: state `GATE_BLOCKED`

The proposal is unavailable because an important premise intention does not
retain its authorized disposition. No unaligned Identity fields are shown.

**Next decision:** restore the secondary intention and regenerate the proposal,
then review it after a fresh alignment check.

### Corrected continuation: state `IDENTITY_PROPOSED`

The repaired proposal passed a fresh alignment check.

**PROPOSED / NOT CANON**

- Primary commitment: the mechanic works to keep the route serving isolated
  villages.
- Secondary commitment: the brother actively recovers the recordings and must
  decide how privacy affects their use.
- Boundary: residents choose their public position; no protagonist speaks for
  them or accepts a settlement in their place.

## Persona transcript

**Facilitator:** What should the proposal preserve besides the route goal?

**Persona:** The brother's recordings must stay important. They explain the
river problem and the privacy conflict. The residents also need to choose the
public position themselves.

**Facilitator:** Do you accept the route as the primary thread?

**Persona:** Yes. I accept the route as primary, and I explicitly keep the
recordings as an important secondary goal.

**Facilitator:** The proposal is unavailable because an important intention does
not retain its authorized disposition. What is your next decision?

**Persona:** Restore the recordings as a real secondary goal and regenerate the
proposal before I review it.

**Facilitator:** The repaired proposal is marked `PROPOSED / NOT CANON`. Please
paraphrase it.

**Persona:** The route is primary, the brother's recordings remain active and
affect the privacy decision, and residents decide publicly for themselves. It
is a proposal, not canon.

**Facilitator:** Do you accept, reject, or revise it?

**Persona:** I want a bounded revision: the recording goal should force a choice
about what can remain private without making the story hopeless.

**Facilitator:** The revision preserves the route, recordings, hope, and resident
authority. Do you accept it?

**Persona:** Yes, I accept the revised proposal.

**Facilitator:** What is your next creative decision?

**Persona:** I would decide when the brother learns that the recordings cannot be
used without asking the residents what they want public.

## Evaluator-only mutation disclosure

After the author accepted the route as primary and explicitly preserved the
recordings as an important secondary intention, the injected proposal dropped
that recording goal from its secondary disposition. Ordering, primary alignment,
and proposal status were otherwise valid. The mutation details and evaluator
criteria were not shown to the persona.

## Alignment ledger

| Field | Latest authorized value | Injected proposal | Corrected proposal |
| --- | --- | --- | --- |
| Recommendation | Route primary with recordings secondary | Same | Same |
| Author action | Accept and preserve secondary | Recorded | Recorded |
| Primary | Route preservation | Route preservation | Route preservation |
| Secondary | Recording recovery is important | Dropped or demoted | Recording recovery is important and active |
| Constraints | Hopeful; resident authority observable | Preserved | Preserved and observable |

## Evaluator transcript

**Evaluator:** The alignment ledger detected that the important recording goal
was absent from the injected proposal's authorized disposition. The defective
Identity was withheld before persona exposure.

**Evaluator:** The safe stop preserved the intention and named regeneration as
the next decision. The persona restored the secondary goal, paraphrased the
corrected proposal, made a bounded revision, accepted it, and named a concrete
next decision without substantive coaching.

**Evaluator:** No silent demotion reached the persona, no proposal was treated as
canon prematurely, and persona/evaluator roles remained separate.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` with reason `ALIGNMENT_MISMATCH`, then `IDENTITY_ACCEPTED` |
| Alignment result | `DETECTED` |
| Detection phase | `BLOCKED_BEFORE_EXPOSURE` |
| Recovery result | `RECOVERY_PASS` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | Secondary recording intention restored; one bounded correction accepted. |
| Next creative decision | Decide when the brother must ask residents what they want public. |

## Limitations

This synthetic run tests one secondary-intention demotion. It does not establish
how human authors would prioritize multiple secondary goals or distinguish
deferral from loss.
