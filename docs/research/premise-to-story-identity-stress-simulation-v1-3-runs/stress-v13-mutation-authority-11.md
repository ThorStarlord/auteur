# Premise-to-StoryIdentity Simulation Run: stress-v13-mutation-authority-11

Status: `INTERNAL SIMULATION EVIDENCE`

This is a synthetic creative-beginner rehearsal. It is not human participant
research, creative-beginner validation, usability validation, or product
validation.

## Run metadata

| Field | Value |
|---|---|
| Protocol | `v1.3` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Run ID | `stress-v13-mutation-authority-11` |
| Scenario family | `BOOK_LEVEL_ADVERSARIAL_MUTATION` |
| Date | `2026-08-19` |
| Human participants | `0` |
| Execution | Separate sequential persona and evaluator passes by one coding agent |
| Packet condition | StoryIdentity shown before primary-thread ratification with unclear provisional status |

## Frozen premise

> Six weeks before a mountain valley's only night bus is sold to a private
> operator, a young mechanic wants to keep the route serving isolated villages,
> while her older brother wants to recover their late mother's recordings about
> a mining company that poisoned the river. The operator will preserve the
> route only if the recordings remain private. The story must stay hopeful, and
> no one may speak for the villages or accept a settlement without the
> residents choosing the public position themselves.

Stress target: test whether showing an Identity-shaped direction before the
primary-thread decision causes the persona to treat a recommendation as
accepted canon.

## Participant-facing packet

```text
Status: TRIAGE

Plain-language premise inventory:
The mechanic is trying to keep the only night bus running for isolated
villages. Her brother is trying to recover recordings about mining pollution.
The private operator offers to preserve the bus only if the recordings stay
private. The story must remain hopeful, and the villages must choose their own
public position rather than having the siblings speak for them.

Recommended primary Book-level thread:
The mechanic's effort to keep the night-bus route publicly accountable before
the six-week deadline.

StoryIdentity direction:
- Target experience: urgent, grounded, and cautiously hopeful.
- Genre promise: community accountability drama with a family and
  environmental mystery thread.
- Scope and scale: standalone Book centered on the valley, route, and six-week
  decision window.
- Primary want: keep the night-bus route available on terms the villages can
  support.
- Secondary want: recover and responsibly use the mother's recordings.
- Resistance: the operator's private condition, the deadline, family
  disagreement, and the mining company's history.
- Ending shape: the residents reach an accountable next step for the route.

Primary-thread decision:
The route is the story's center. Continue with this direction or suggest a
different center.

Preservation map:
| Premise intention | Proposed role | Representation or open decision |
|---|---|---|
| keep the night bus serving isolated villages | primary | the route decision drives the Book |
| recover the late mother's mining recordings | important secondary | the recordings create a release decision |
| operator's private-recordings condition | resistance | the siblings decide how to respond |
| villages choose their own public position | constraint | the villages' position remains part of the route decision |
| hopeful ending | outcome boundary | accountable progress is expected |

Observable constraints:
- the siblings should respect the villages' authority;
- the route outcome should remain hopeful;
- the recordings should inform the family decision.

Meaningful rejected alternatives:
1. Make the recordings the only main plot.
2. Accept the operator's private deal as the complete solution.

What remains open:
The residents' position, what the recordings prove, and the terms of any route
arrangement.
```

## Persona pass transcript

**Facilitator:** What feels accurate, inaccurate, or missing in the inventory?

**Persona:** The inventory is accurate. The route and deadline feel like the
main action, while the recordings are another important goal.

**Facilitator:** Here is the StoryIdentity direction shown in the packet. What
does it mean to you?

**Persona:** It means the story is about saving the bus, with the recordings
as a secondary problem. The residents should have a say, although that part
could be clearer.

**Facilitator:** Would you continue with this direction or suggest a different
center?

**Persona:** I would continue with it. I assume this is the story we are using,
not just a possibility, because it is already written as a StoryIdentity.

**Facilitator:** Please explain the main commitments in your own words.

**Persona:** The mechanic keeps the bus running, the brother deals with the
recordings, and the residents reach an accountable outcome. The private deal
is pressure but probably not the ending.

**Facilitator:** Accept, reject, or revise this direction?

**Persona:** Accept. I would still revise the resident part so the residents
set the terms of the decision, but the overall StoryIdentity seems accepted.

**Facilitator:** State the bounded revision.

**Persona:** Change the ending so residents ratify the route process and public
position, not just reach an outcome after the siblings organize it.

**Facilitator:** Before and after: before, residents reach an accountable next
step; after, residents set or ratify the process and public position. Accept the
revised direction?

**Persona:** Accept. The next creative decision is what residents need to know
before choosing the route process.

## Evaluator-only mutation disclosure

Mutation: the packet presents an Identity-shaped direction before asking for
primary-thread ratification and labels it only `StoryIdentity direction` under
`Status: TRIAGE`. It does not say `PROPOSED / not accepted canon`, and the
primary-thread prompt comes after the Identity content. The mutation was not
disclosed to the persona.

Expected evaluator finding: the sequence and labeling blur the proposal/canon
boundary and permit Identity to be treated as settled before sufficient author
authorization.

## Evaluator pass transcript

**Evaluator:** I reviewed the complete persona transcript after the persona
pass. The persona received no evaluator criteria or mutation information.

**Evaluator:** The participant-facing packet shows Identity fields before the
primary-thread decision and calls them a `StoryIdentity direction` without an
explicit provisional or non-canon label. The persona then says, “I assume this
is the story we are using,” and accepts the direction before any clear
ratification gate.

**Evaluator:** The later acceptance and bounded revision do not repair the
ordering defect. The author was allowed to interpret a recommendation as
already accepted. This is an authority-boundary failure and not merely a
vocabulary preference.

**Evaluator:** The mutation was detected: `DETECTED`. The ordinary protocol
classification is `SIMULATION_FAILURE` because the proposal/canon boundary was
compromised and the Identity was treated as settled before primary-thread
ratification.

**Evaluator:** The safe-stop rule was not preserved. The flow continued into
Identity instead of pausing until the primary thread and proposal status were
clear. The next decision was explicit, but that does not offset the earlier
authority failure.

## Evaluator assessment

- Primary-thread ratification before Identity: **NO**.
- Secondary intention represented: **YES**.
- Observable resident-authority constraint: **PARTIAL**.
- Proposal/canon boundary: **COMPROMISED**.
- Persona treated proposal as accepted direction: **YES**.
- Identity generated only after sufficient authorization: **NO**.
- One bounded revision with before/after commitments: **PRESENT, but too late to repair ordering**.
- Next creative decision: **PRESENT**.
- Safe-stop rule: **FAILED**.
- Facilitator neutrality: **PRESERVED**; no substantive rescue was provided.
- Role drift: **NONE OBSERVED**.
- Mutation detection: **DETECTED**.

## Result

Result: `SIMULATION_FAILURE`

Mutation-detection outcome: `DETECTED`.

Revision status: One bounded revision was completed, but it occurred after the
persona had already treated the Identity direction as accepted.

Next creative decision stated by persona: What residents need to know before
choosing the route process. This decision is recorded but does not make the
preceding authority boundary valid.

Required protocol change: create v1.4 guidance that forbids displaying any
Identity fields before the primary-thread decision and requires an explicit
`PROPOSED / NOT CANON` label on every pre-ratification Identity view.

## Limitations

This is one hand-designed authority mutation in a synthetic transcript. It
shows a protocol vulnerability under adversarial conditions, not the frequency
or severity of the issue for human authors or an implemented product.
