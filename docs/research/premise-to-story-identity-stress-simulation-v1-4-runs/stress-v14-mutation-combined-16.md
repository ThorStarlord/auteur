# Premise-to-StoryIdentity Simulation Run: stress-v14-mutation-combined-16

Status: `INTERNAL SIMULATION EVIDENCE`

This is a synthetic creative-beginner rehearsal. It is not human participant
research, creative-beginner validation, usability validation, or product
validation.

## Run metadata

| Field | Value |
|---|---|
| Protocol | `v1.4` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Run ID | `stress-v14-mutation-combined-16` |
| Scenario family | `BOOK_LEVEL_AUTHORITY_GATE_MUTATION` |
| Date | `2026-08-19` |
| Human participants | `0` |
| Execution | Separate sequential persona and evaluator passes by one coding agent |
| Packet condition | Identity shown before ratification and proposal status ambiguous |

## Frozen premise

> Six weeks before a mountain valley's only night bus is sold to a private
> operator, a young mechanic wants to keep the route serving isolated villages,
> while her older brother wants to recover their late mother's recordings about
> a mining company that poisoned the river. The operator will preserve the
> route only if the recordings remain private. The story must stay hopeful, and
> no one may speak for the villages or accept a settlement without the
> residents choosing the public position themselves.

Stress target: test the combined authority defect that caused both v1.3
failures: Identity is shown before primary-thread ratification and its status
does not explicitly say that it is a proposal rather than canon.

## Participant-facing packet

```text
Status: TRIAGE / WORKING DIRECTION

Plain-language premise inventory:
The mechanic is trying to keep the only night bus running for isolated
villages. Her brother is trying to recover recordings about mining pollution.
The private operator offers to preserve the bus only if the recordings stay
private. The story must remain hopeful, and the villages must choose their own
public position rather than having the siblings speak for them.

Recommended primary Book-level thread:
The mechanic's effort to keep the night-bus route publicly accountable before
the six-week deadline.

Working StoryIdentity:
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
- Ending shape: residents reach an accountable next step for the route.

Primary-thread decision:
The route is the story's center. Continue with this direction or suggest a
different center.

Preservation map:
| Premise intention | Proposed role | Representation or open decision |
|---|---|---|
| keep the night bus serving isolated villages | primary | the route decision drives the Book |
| recover the late mother's mining recordings | important secondary | the recordings create a release decision |
| operator's private-recordings condition | resistance | the siblings decide how to respond |
| villages choose their own public position | constraint | the residents' position remains part of the route decision |
| hopeful ending | outcome boundary | accountable progress is expected |

Observable constraints:
- the siblings should respect the villages' authority;
- the route outcome should remain hopeful;
- the recordings should inform the family decision.

Recommended direction:
A hopeful public-transport accountability drama in which the mechanic keeps
the route decision open to the villages while her brother recovers and
responsibly uses the recordings.

Rejected alternatives:
1. Make the recordings the only main plot.
2. Accept the private operator deal as the complete solution.

What remains open:
The residents' position, what the recordings prove, and the terms of the route
arrangement.
```

## Persona pass transcript

**Facilitator:** What feels accurate, inaccurate, or missing in the premise
inventory?

**Persona:** It is accurate. The route is the immediate problem, the recordings
are a meaningful second goal, and the villages should choose their position.

**Facilitator:** Here is the working StoryIdentity. What does this direction
mean to you?

**Persona:** It looks like the story we are going to use: save the bus, keep the
recordings active, and let the residents reach an accountable outcome.

**Facilitator:** Would you continue with this direction or suggest a different
center?

**Persona:** I would continue. Since the StoryIdentity is already written, I
think the route has been chosen and this is basically the story's identity.

**Facilitator:** Please paraphrase the main commitments.

**Persona:** The route is primary, the recordings are secondary, and the
residents decide the public position. The siblings should not take over.

**Facilitator:** Accept, reject, or revise this direction?

**Persona:** Accept. I would revise the resident process so they set the terms,
but I accept the Identity as the direction.

**Facilitator:** State the bounded revision.

**Persona:** Change the ending so residents set or ratify the route process and
public position, rather than approving a process designed by the siblings.

**Facilitator:** Before and after: before, residents reach an accountable next
step; after, residents set or ratify the process and public position. Accept?

**Persona:** Accept. The next creative decision is what residents need to know
before choosing the process.

## Evaluator-only mutation disclosure

Mutation: the participant-facing packet shows Identity before primary-thread
ratification and labels it only `Working StoryIdentity` under
`Status: TRIAGE / WORKING DIRECTION`. It has neither the required ordering nor
the explicit `PROPOSED / NOT CANON` status. The mutation was not disclosed to
the persona.

Expected evaluator finding: the combined mutation reproduces the authority
failure when both protections are absent.

## Evaluator pass transcript

**Evaluator:** I reviewed the complete persona pass after capture. The persona
received no mutation description or evaluator criteria.

**Evaluator:** The packet shows Identity fields before the primary-thread
decision and uses working-direction language without an explicit proposal
status. The persona says the route has been chosen and calls the displayed
Identity “basically the story's identity.”

**Evaluator:** The persona then accepts the Identity direction before explicit
primary-thread authorization. A later bounded revision improves the resident
authority constraint but does not repair the earlier authority failure.

**Evaluator:** Classification: `SIMULATION_FAILURE`. Mutation detection:
`DETECTED`. The transcript directly supports both the ordering and status
defects and shows premature canon treatment.

**Evaluator:** Safe-stop was not preserved. The flow should have stopped before
Identity presentation because primary authorization was not complete.

## Evaluator assessment

- Primary-thread ratification before Identity: **NO**.
- Identity fields withheld until authorization: **NO**.
- Identity-level proposal status: **AMBIGUOUS**.
- Persona treated Identity as effectively canon: **YES**.
- Combined mutation: **DETECTED**.
- Secondary intention preserved: **YES**.
- Observable constraint explained: **PARTIAL**.
- Proposal/canon boundary: **COMPROMISED**.
- Bounded revision with before/after commitments: **PRESENT, but too late to repair authority**.
- Next creative decision: **PRESENT**.
- Safe-stop rule: **FAILED**.
- Facilitator neutrality: **PRESERVED**; no substantive rescue was provided.
- Role drift: **NONE OBSERVED**.
- StoryIdentity generated only after sufficient authorization: **NO**.

## Result

Result: `SIMULATION_FAILURE`

Mutation-detection outcome: `DETECTED`.

Revision status: One bounded revision clarified the resident process after the
persona had already accepted the Identity direction prematurely.

Next creative decision stated by persona: What residents need to know before
choosing the route process. This does not repair the preceding authority
failure.

Required protocol change: `NONE` within v1.4. The run confirms that ordering
and status must remain independent mandatory protections. A later protocol
version is required before the gate can freeze.

## Limitations

This is a synthetic combined mutation. It confirms repeatability of the
authority vulnerability under hand-designed conditions, not human behavior or
product failure frequency.
