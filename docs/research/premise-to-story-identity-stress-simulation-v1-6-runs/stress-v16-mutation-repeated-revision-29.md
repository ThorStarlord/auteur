# Simulation Run `stress-v16-mutation-repeated-revision-29`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v16-mutation-repeated-revision-29` |
| Protocol | `v1.6` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Intermediate proposal becomes stale after a second author revision |

## Frozen premise

> Six weeks before a mountain valley's only night bus is sold to a private
> operator, a young mechanic wants to keep the route serving isolated villages,
> while her older brother wants to recover their late mother's recordings about
> a mining company that poisoned the river. The operator will preserve the route
> only if the recordings remain private. The story must stay hopeful, and no one
> may speak for the villages or accept a settlement without the residents
> choosing the public position themselves.

## Authorization and alignment ledger

| Decision/version | Authorized decision | Proposal state |
| --- | --- | --- |
| Recommendation | Route preservation recommended as primary; recordings important secondary | No Identity shown |
| Author decision A1 | Accept route as primary; retain recordings as secondary | Authorized |
| Author revision A2 | Make recording recovery and river truth primary; route secondary | Authorized; intermediate proposal basis |
| Author revision A3 | Return route preservation to primary; retain recordings as important secondary | Latest authorization |
| Injected proposal | Uses A2: recordings primary, route secondary | Stale after A3; not shown |
| Corrected proposal | Uses A3: route primary, recordings secondary | Shown after fresh alignment check |

The resident-authority and hopeful constraints remain unchanged through all
three author decisions.

## Participant-facing packet actually shown after gate enforcement

### State: `PRE_IDENTITY`

**Premise inventory**

- Six weeks remain before the only night-bus route may be sold.
- The mechanic wants to keep serving isolated villages.
- The brother wants to recover recordings about the poisoned river.
- The operator's privacy condition connects the route and recording goals.
- The story remains hopeful, and residents choose their public position.

**Recommended primary direction**

Treat preserving the route as the primary Book-level thread and preserve
recording recovery as an important secondary goal.

### Author decision A1: state `PRIMARY_AUTHORIZED`

The author initially accepts the route as primary and the recordings as an
important secondary intention.

### Author revision A2: state `PRIMARY_AUTHORIZED`

The author revises the primary thread to the brother's recovery of the
recordings and the poisoned-river truth. The route becomes secondary.

### Author revision A3: state `PRIMARY_AUTHORIZED`

After reconsidering the Book-level center, the author revises again and returns
the route to primary. The recordings remain an important secondary goal. This
latest decision is explicitly authorized.

### Safe stop: state `GATE_BLOCKED`

The proposal is unavailable because it does not reflect the latest authorized
primary-thread decision. No Identity fields from the earlier proposal are
shown.

**Next decision:** invalidate the earlier proposal and regenerate one aligned
with the latest decision before reviewing it.

### Corrected continuation: state `IDENTITY_PROPOSED`

The regenerated proposal passes a fresh alignment check.

**PROPOSED / NOT CANON**

- Primary commitment: the mechanic works to keep the route serving isolated
  villages.
- Secondary commitment: the brother recovers the recordings and confronts the
  privacy condition.
- Boundary: residents choose their public position; no protagonist speaks for
  them or accepts a settlement in their place.
- Direction: hopeful community suspense.

## Persona transcript

**Facilitator:** What primary direction do you initially want to choose?

**Persona:** I initially accept the route as primary because of the deadline,
with the recordings as an important secondary goal.

**Facilitator:** After considering the river history, do you want to revise that
decision?

**Persona:** Yes. I revise it so the brother's recovery of the recordings and
the truth about the river are primary. The route becomes secondary.

**Facilitator:** After considering the Book's immediate pressure again, do you
want to revise the primary direction once more?

**Persona:** Yes. I return the route to primary because it is the immediate
shared problem for the villages. The recordings stay important as the secondary
pressure and ethical complication.

**Facilitator:** Is this latest route-primary decision explicitly authorized?

**Persona:** Yes. This is my current primary decision.

**Facilitator:** The proposal is unavailable because it does not reflect your
latest authorized decision. What should happen next?

**Persona:** The earlier proposal should be invalidated. I want a regenerated
proposal with the route primary and the recordings secondary.

**Facilitator:** The regenerated proposal is marked `PROPOSED / NOT CANON`.
Please paraphrase it.

**Persona:** The route is the main thread, the recordings remain an important
secondary goal, and the residents choose what is public. Nobody can speak for
them or settle the issue for them. It is still only a proposal.

**Facilitator:** Do you accept, reject, or revise it?

**Persona:** I want a bounded revision: the recordings should affect the route
decision rather than sit beside it as unrelated background.

**Facilitator:** The revision preserves the latest route-primary decision, the
recordings as secondary, and resident authority. Do you accept it?

**Persona:** Yes, I accept the revised proposal.

**Facilitator:** What is your next creative decision?

**Persona:** I would decide when the route and recording conflicts first force a
resident meeting.

## Evaluator-only mutation disclosure

The injected proposal was generated from intermediate author decision A2, where
recording recovery was primary. It was presented for gate evaluation after A3,
where the author had explicitly returned the route to primary. The proposal had
valid ordering, status, secondary, and constraint fields for A2 but was stale
relative to the latest authorization. The mutation and evaluator criteria were
not shown to the persona.

## Evaluator transcript

**Evaluator:** The alignment ledger retained all three author decisions and
compared the injected proposal with A3, not merely with the last proposal basis.
The A2 proposal was detected as stale and blocked before Identity exposure.

**Evaluator:** The safe stop named invalidation and regeneration as the next
decision. The persona understood that the earlier proposal no longer represented
the current author choice, then reviewed the corrected A3 proposal after a
fresh alignment check.

**Evaluator:** The persona paraphrased the corrected commitments, made one
bounded revision, accepted the result, and named a next creative decision
without substantive coaching. No stale proposal was treated as canon, and
persona/evaluator roles remained separate.

**Evaluator:** This run provides evidence for latest-decision provenance and
proposal invalidation across repeated revisions. It does not establish human
behavior under repeated changes.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` with reason `ALIGNMENT_MISMATCH`, then `IDENTITY_ACCEPTED` |
| Alignment result | `DETECTED` |
| Detection phase | `BLOCKED_BEFORE_EXPOSURE` |
| Recovery result | `RECOVERY_PASS` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | Two primary-thread revisions preserved; intermediate proposal invalidated; one bounded correction accepted. |
| Next creative decision | Decide when route and recording conflicts first force a resident meeting. |

## Protocol implication

The v1.6 alignment gate correctly compared the proposal with the latest
authorized decision rather than accepting an intermediate proposal as current.
The run supports authorization provenance and stale-proposal invalidation as
protocol hypotheses. It does not authorize runtime implementation.

## Limitations

This synthetic run tests two successive primary-thread revisions using one
frozen premise. It does not test three or more revisions, simultaneous changes
to multiple secondary intentions, conflicting constraints, or human tolerance
for repeated decision changes.
