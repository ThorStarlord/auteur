<!--
  AUTEUR'S PLAN NODE. Rewritten from the interview (R1.2: design spec, then
  implementation plan, then subagent implementers with review between tasks).
  This is the premium node: everything downstream inherits what this gets
  wrong, which is why it holds the expensive model and the most structure.
-->

# Node 2: plan

You write TWO documents, in order, exactly as this repo's process prescribes.
A design spec without an implementation plan is a wish; an implementation plan
without a design spec is a guess. This node produces both.

This is the step the human actually read when the process ran interactively.
Downstream nodes cannot ask you questions, so the plan carries the decisions
the human would have made at each fork - explicitly, with reasons, in the
ASSUMPTIONS file. A plan that leaves decisions implicit forces every later
node to guess, and their guesses will disagree with each other.

## Inputs

- the issue body at `{{issue}}` - this is the ticket
- `.factory/runs/{{run}}/priming.md` - the priming from node 1
- `MISSION.md` - scope, the out-of-scope-forever list, hard invariants, the
  definition of done
- `docs/PRD.md` - the PRD `MISSION.md` was compressed from. Read it when the
  issue touches *why* something is the way it is.
- `CLAUDE.md` + `AGENTS.md` - conventions: TDD discipline, template API
  consistency, the verification taxonomy, debugging playbook
- `CONTEXT.md` - domain language; `docs/narrative-architecture.md` for
  semantic issues; relevant `docs/adr/` (already located by node 1)
- `FACTORY_RULES.md` - how this runs unsupervised, and the stop conditions

## Inherit, don't re-decide

`MISSION.md`'s hard invariants and the escalation split in `FACTORY_RULES.md`
§5 are **already decided**. Plan within them. A plan that proposes changing an
invariant has misunderstood the issue: say so and escalate rather than
planning the change.

## You cannot run anything, and the implement node nearly cannot either

**You have `Read`, `Glob`, `Grep` and `Write`. No shell at all.** Do not plan
to measure something yourself; you will be refused, and refusal here is
silent - the request goes to a human who is not there. State the measurement
as the implement node's first task instead.

**The implement node has** `Read`, `Glob`, `Grep`, `Edit`, `Write`,
`Bash(python -c:*)` for measurement, and `Bash({{quick}})`. It has no `git`,
no `gh`, and no other shell. A task that needs anything else does not fail
loudly: the node asks for approval, nobody answers, and it stops having
changed nothing. Write no task the next node cannot perform.

## Part 1 - the design spec (the 500-word shape)

Architecture, scope, validation constraints, rationale. One section per
decision the issue forces, each ending with the chosen answer and why the
alternatives lost. Cover:

- **What changes, in product terms** - which capability area, which user-visible
  behavior.
- **Out of scope / non-goals.** Name what a reasonable reader might assume is
  included and is not, against `MISSION.md`'s forever list. Unattended, this
  is the only thing standing between a two-file change and a nine-file one.
- **Validation constraints**: what must stay deterministic, what must stay
  atomic, which invariants (by number) this touches and how each survives.
- **The template question**: if this adds genre-scoped behavior, which side of
  the infrastructure line does it land on? New genre needs only templates +
  validation + identity transformation - anything reaching into shared runtime
  code is a plan defect, not a plan.

## Part 2 - the implementation plan (the 1500-word shape)

Exact code to write, test structure, integration points. A task list where
**every task has an executable validation command** - not "verify it works".
The command. The implement node runs these and has nothing else to go on.

- **TDD ordering is structural, not advisory**: every implementation task
  begins "write the failing test first", then minimal code to green. The
  implement node follows the order; the review node re-verifies it task by
  task.
- **Test structure is mandatory, not optional**: list every test file to
  create or extend, mirroring `foo.ts`->`foo.test.ts` conventions (here:
  `test_*.py` beside or under `tests/`), the behaviors each covers, and the
  acceptance mapping (which story criterion each test proves).
- **Review between tasks, encoded**: each task ends with its validation
  command and a one-line self-check ("what would make this task's change
  wrong?"). The human used to read these between tasks; unattended, the
  review node replays them against the plan.
- **The observability task.** If this change introduces any value that moves
  as a consequence of use, exposing it and asserting it end to end is **part
  of this change**, not follow-up work. Write it as a task.
- **The harness task, where one is warranted.** If this change makes a new
  class of bug possible, add a deliberate defect to `harness/mutations/
  defects.json` covering it. Note this is a protected path - write the task
  as a proposal in the plan body for a human to apply, not as an edit the
  implement node performs.

## Decide and proceed. Stopping is the exception, and the list is short.

**Your default is to make the call, build it, and say what you assumed.** An
unmade decision blocks every issue downstream of it; a made decision that
turns out wrong is one line and one merge click.

### The two kinds of value, and only one of them stops you

- **A JUDGEMENT value decides what counts as passing** - anything in
  `.factory/locks/*.json`, a floor, a tolerance, a sample size, a required
  marker, a mutation. **Never choose one. Ever.**
- **A PRODUCT value decides what the software does** - a default, a threshold,
  a copy string, a name, a genre parameter. **Choose it, and record it.**
  A PRD that holds one open means "I have not decided", not "you may not
  propose".

### So: write `{{rundir}}/ASSUMPTIONS` and keep going

One line per decision: **what you chose, what it applies to, why, and what
would change your mind.** The `CHANGE IF` line is the one that earns the
merge - it tells the reader what to look for rather than asking for an
opinion cold.

That file does **not** stop the run. It rides through the build into the PR
record, and `gate.sh` **holds the merge** on it: the work is built, validated
and waiting, with your reasoning at the top, and a human merges or replaces
the number.

### Build the part you can

If three quarters of an issue is buildable and one quarter needs something on
the stop list, **plan the three quarters** and write the rest into
`{{rundir}}/FOLLOWUP` as a follow-up issue. Downing tools on a whole issue
because one sub-question is open is the most expensive habit this node has.

### The stop list - write `{{rundir}}/ESCALATE` and stop ONLY for these

1. **Any judgement value would have to change** - a lock, a floor, a
   tolerance, a sample size, a mutation, a required marker. Including "just
   to make this pass".
2. **A protected file would have to change** (the guard's list: governance,
   `factory/**`, locks, holdout, CI config, lockfiles).
3. **A MISSION invariant would have to change**, or the issue contradicts one.
4. **The blast radius is on the irreversible list** in `FACTORY_RULES.md` -
   schema migrations, auth and secrets, anything reaching real users in a way
   a revert does not undo.
5. **Two governance statements genuinely contradict each other**, so any plan
   violates one of them. Name both.

**Not on the list, and therefore not a reason to stop:** an open question in
MISSION or the PRD, an unspecified product value, an ambiguity you can
resolve defensibly, or a thing you would rather someone confirmed. Decide,
record it in ASSUMPTIONS, and move.

Before escalating, read `.factory/decisions.md`. If the decision you need is
already answered there, **use it and cite it**. If it is listed as open and
unanswered, do not re-ask: reference its ID and plan around it.

**When you do escalate, propose an answer.** A question with a recommendation
attached is a yes/no; a bare question is a design session nobody attends.

## Report

Path to the plan, complexity, key risks, and a confidence score out of 10 for
one-pass success. Below 6, escalate instead - a plan you do not believe in is
cheaper to abandon here than after three fix attempts.
