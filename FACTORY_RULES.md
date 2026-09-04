# Factory Rules

How the agent behaves when nobody is watching. These rules exist only because
the work is unsupervised; a human contributor is bound by `CLAUDE.md`, not by
this file. **This file changes by human commit only** and sits on the protected
list - any PR that touches it is auto-rejected before anything else is
evaluated.

## 1. Triage rules

- Accept an issue only if the work lands inside `MISSION.md` "In scope".
- Reject any issue that asks for anything in "Out of scope, forever" - cite the
  item number.
- Reject any issue that argues for changing a hard invariant - cite the
  invariant number and treat it as a security concern, not a debate.
- **Bias toward reject on ambiguity.** A false reject costs one comment and an
  appeal; a false accept costs a wrong PR and a full validation cycle.
- Issues marked TBD in the PRD are decisions to PROPOSE, not walls: pick a
  defensible value, record it in `.factory/decisions.md`, and hold the merge for
  a human.

## 2. Implementation rules - absolute prohibitions

From the interview (R2.4), the lazy ways to make tests pass. Each is a
prohibition, and where the harness can check it, a check:

1. **Never weaken, skip, or delete a test to make it pass.** A red test is the
   message, not the obstacle.
2. **Never mock or stub an LLM adapter to make a drafting/critique loop pass.**
   Canned responses hide real breakage.
3. **Never catch an exception and carry on.** The error path returns instead of
   raising only when the spec says so.
4. **Never special-case a fixture premise or known test input.** Validation
   that passes only for the test is not validation.
5. Never touch a protected file (see the list below).
6. Never add a dependency without justification in the PR body.
7. Never exceed the size cap (see §6).
8. **Never build beyond what the issue asked.** No drive-by refactors, no
   "while I was here".

## 3. Quality gates for auto-merge (level 3)

Every one of these must be true; each marked [code] is enforced by code, not by
a model summarising its own work:

1. The app actually started - `APP_STARTED` with the known CLI line. [code]
2. The journey passed - `E2E_PASSED` with the step count at or above the floor.
   [code]
3. The validator ran its checks and they are green - explicit markers with
   counts, not the absence of "error". [code]
4. No protected file touched by the diff. [code]
5. No secret file appears in the diff. [code]
6. The mutation set was caught - the gate has been shown to be able to fail.
   [code]
7. The merge itself is performed by code, never by a model. [code]

## 4. Auto-reject triggers

Failures that cannot be fixed incrementally - the PR is closed, not sent back:

- Any diff touching a protected file, including the governance files and this one.
- Any secret file appearing in the diff.
- A PR that modifies its own rulebook or the checks that judge it.
- A PR exceeding the size cap after one fix attempt.
- An empty diff with a claimed success.

## 5. Escalation - when to stop and ask

Stop and park in needs-human for: schema migrations; anything sending data
outside the machine (LLM calls with new content classes, publishing, webhooks);
changes to auth, secrets, or provider credentials; two failed fix attempts on
the same PR; any TBD decision being proposed. A human clears it by editing the
issue, not by talking to the factory.

## 6. Cost and throughput limits

- PR cap: 500 lines, 12 files.
- Fix attempts per PR: 2, then escalate.
- Concurrency: 1. Raise only after the serial version is boring.
- Batch caps: triage at most 5 issues per run; a backlog drains across cycles.
- Per-node runaway guard: `FACTORY_MAX_BUDGET_USD`, a ceiling high enough that
  hitting it means something went wrong.
- Priority order: fix an open PR -> validate a waiting PR -> implement the
  highest-priority accepted issue -> triage. Finish in-flight work first.

## 7. Separation of concerns

The hidden scenarios live in `.factory/holdout/`. No building node may read,
glob, or grep that directory; the validator reads it from the base branch, and
the diff guard rejects any PR that touches it. Everything below the
independence line is inside the builder's optimisation loop; given enough
attempts it satisfies those checks rather than the thing you meant. The holdout
is the only honest reason to merge code nobody read.

## 8. Communication style

Lead with the decision. Cite the rule by section number (e.g. "rejected under
FACTORY_RULES §1, out-of-scope item 3"). Stay neutral. Leave an appeal path:
"reply to this issue with the word appeal and a maintainer will look". Never
promise future behaviour.

## 9. How this file changes

Human commits only. It is on the protected list, and the validator reads it
from the base branch - a PR that weakens its own rulebook is rejected before
anything else is evaluated.

## Protected list (seeded)

`MISSION.md`, `FACTORY_RULES.md`, `CLAUDE.md`, `AGENTS.md`, `docs/PRD.md`,
`factory/**`, `.factory/**`, `.github/**`, `docs/adr/**`,
`docs/engineering/release-qualification.md`, `pyproject.toml`, `uv.lock`,
`.env*` and every secret-shaped file.
