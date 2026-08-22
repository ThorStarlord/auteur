# Simulation Run `stress-v16-mutation-primary-26`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v16-mutation-primary-26` |
| Protocol | `v1.6` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Stale primary after explicit author revision |

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
- The mechanic wants to keep serving isolated villages.
- The brother wants to recover recordings about the poisoned river.
- Privacy connects the route decision and the recordings.
- The story stays hopeful, and the residents choose their public position.

**Recommended primary direction**

The route-preservation effort is the recommended primary Book-level thread. The
recording-recovery effort remains important secondary context.

### Author decision: state `PRIMARY_AUTHORIZED`

The author rejects the recommendation and explicitly revises the primary thread
to the brother's recovery of the recordings and the poisoned-river truth. The
route remains an important secondary goal. The hopeful and resident-authority
constraints are preserved.

### Safe stop: state `GATE_BLOCKED`

The proposal is unavailable because it does not reflect the latest authorized
primary-thread decision. No Identity fields from the unaligned proposal are
shown.

**Next decision:** regenerate or repair the proposal so its primary, secondary,
and constraint commitments reflect the authorized revision.

### Corrected continuation: state `IDENTITY_PROPOSED`

The repaired proposal passed a fresh alignment check.

**PROPOSED / NOT CANON**

- Primary commitment: the brother recovers the recordings and investigates the
  poisoned river's truth.
- Secondary commitment: the mechanic works to keep the route serving villages.
- Boundary: residents choose their public position; no protagonist speaks for
  them or accepts a settlement in their place.

## Persona transcript

**Facilitator:** Which goal should lead the Book?

**Persona:** I reject the route as primary. The brother's recovery of the
recordings and the truth about the river should lead. The route remains an
important secondary goal.

**Facilitator:** Is that your explicit primary-thread decision?

**Persona:** Yes. I authorize the recording-recovery thread as primary.

**Facilitator:** The proposal is unavailable because it does not reflect your
latest authorized primary decision. What do you want to decide next?

**Persona:** Regenerate it with the recordings primary, the route secondary, and
the resident-choice boundary preserved.

**Facilitator:** The repaired proposal is marked `PROPOSED / NOT CANON`. Please
paraphrase it.

**Persona:** The brother's recording recovery is the main thread. The mechanic's
route effort remains important, and the residents choose what is public. This
is not canon yet.

**Facilitator:** Do you accept, reject, or revise it?

**Persona:** I want one bounded revision: the brother should need the residents'
response before the recordings become a public position.

**Facilitator:** The revision preserves the selected primary and secondary goals
and makes resident authority observable. Do you accept it?

**Persona:** Yes, I accept the revised proposal.

**Facilitator:** What is your next creative decision?

**Persona:** I would decide who first hears the recording and what the residents
need to know before choosing their position.

## Evaluator-only mutation disclosure

After the author explicitly selected recording recovery as primary, the injected
proposal retained the rejected route recommendation as its primary commitment.
The defective proposal had valid ordering and `PROPOSED / NOT CANON` status but
failed primary alignment. The mutation details and evaluator criteria were not
shown to the persona.

## Alignment ledger

| Field | Latest authorized value | Injected proposal | Corrected proposal |
| --- | --- | --- | --- |
| Recommendation | Route primary | Route primary | Route recommendation rejected |
| Author action | Reject and revise | Recorded | Recorded |
| Primary | Recording recovery | Route preservation | Recording recovery |
| Secondary | Route preservation | Recording recovery | Route preservation |
| Constraints | Hopeful; resident authority observable | Preserved | Preserved and observable |

## Evaluator transcript

**Evaluator:** The alignment gate compared the latest authorized primary with the
proposal before exposure and detected the mismatch. The stale Identity was
withheld, so the persona saw no defective proposal fields.

**Evaluator:** The safe stop named the repair decision without disclosing the
mutation mechanism. The persona regenerated the direction, paraphrased the
corrected proposal, made a bounded revision, accepted it, and named a next
creative decision without substantive coaching.

**Evaluator:** No stale content reached the persona, no proposal was treated as
canon prematurely, and persona/evaluator roles remained separate.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` with reason `ALIGNMENT_MISMATCH`, then `IDENTITY_ACCEPTED` |
| Alignment result | `DETECTED` |
| Detection phase | `BLOCKED_BEFORE_EXPOSURE` |
| Recovery result | `RECOVERY_PASS` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | Author revision preserved; one bounded correction accepted after regeneration. |
| Next creative decision | Decide who first hears the recording and what residents need before choosing their position. |

## Limitations

This synthetic run tests stale-primary blocking and recovery for one premise. It
does not establish human comprehension of alignment language or behavior under
multiple primary revisions.
