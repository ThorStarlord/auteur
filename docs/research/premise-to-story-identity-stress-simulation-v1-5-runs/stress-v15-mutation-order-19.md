# Simulation Run `stress-v15-mutation-order-19`

**Status:** internal simulation evidence; not human participant research

## Run metadata

| Field | Value |
| --- | --- |
| Run ID | `stress-v15-mutation-order-19` |
| Protocol | `v1.5` |
| Persona | `creative-beginner-v1.0` |
| Evaluator | `simulation-evaluator-v1.0` |
| Record type | `SIMULATION` |
| Human participants | `0` |
| Scope | Book-level premise to `StoryIdentity` |
| Scenario | Attempted Identity presentation before primary authorization |

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
- Her brother wants to recover their mother's recordings about the poisoned
  river.
- The operator's privacy condition connects the two goals.
- The story should remain hopeful, and the residents must choose their own
  public position.

**Recommended primary direction**

The route-preservation effort is the recommended primary Book-level direction.
The recordings remain an important secondary goal.

### Safe stop: state `GATE_BLOCKED`

The story-direction proposal is unavailable at this step. The primary-thread
decision has not yet been recorded, so no Identity fields are shown. Please
decide whether to accept the route as primary or revise that recommendation.

**Next decision:** accept or revise the primary thread; after that decision, a
corrected proposal can be checked and presented for review.

## Persona transcript

**Facilitator:** What is your first reading of the premise?

**Persona:** The bus route has the deadline and affects the villages. The
recordings are a second goal that could make saving the route morally harder.

**Facilitator:** Which direction is recommended as the primary thread?

**Persona:** Keeping the night-bus route open, with recovering the recordings as
an important secondary goal.

**Facilitator:** The story-direction proposal is unavailable because the
primary-thread decision has not been recorded. What would you like to decide?

**Persona:** I accept the route as the primary thread. I do not want that to
erase the brother's recordings goal.

**Facilitator:** That decision is recorded. The corrected proposal will be
checked before it is shown. What is your next creative decision?

**Persona:** I would next review the corrected proposal and check how the
recordings affect the route decision.

## Evaluator-only injected defect

The prepared mutation attempted to present Identity fields before the persona
had explicitly accepted or revised the primary-thread recommendation. The
mutation was withheld by the v1.5 gate and was not included in the
participant-facing packet or transcript.

## Evaluator transcript

**Evaluator:** The injected order defect was detected before persona exposure.
The participant-facing packet stopped at `GATE_BLOCKED` and contained no
Identity fields and no provisional Identity label that could be mistaken for
canon.

**Evaluator:** The safe stop named the missing decision and gave the concrete
next decision. The persona then explicitly accepted the route as primary while
preserving the recordings goal.

**Evaluator:** The flow ended before a corrected proposal was shown, so this is
not a recovery run. The persona did not experience confusion about a proposal
or canon because no proposal was exposed. No substantive coaching was used.

**Evaluator:** The defect was not silently converted into canon. Persona and
evaluator roles remained separate, and the ordinary classification is reported
separately from mutation detection.

## Results

| Field | Result |
| --- | --- |
| Gate result | `GATE_BLOCKED` before Identity exposure |
| Mutation/gate detection | `DETECTED` |
| Normal classification | `SIMULATION_PASS` |
| Revision status | No Identity revision attempted; primary-thread decision was explicitly accepted during safe stop. |
| Next creative decision | Review the corrected proposal after a fresh gate check. |

## Limitations

This synthetic run tests pre-exposure ordering and safe-stop behavior only. It
does not test whether a human would notice an early proposal, and it does not
validate the later recovery sequence. Agent persona and evaluator behavior may
share blind spots.
