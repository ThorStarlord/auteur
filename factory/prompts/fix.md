<!--
  AUTEUR'S FIX NODE. Structure kept from the template; the prohibitions are
  the interview's R2.4 answers and the repo's environment-first diagnostic.
-->

# fix-pr

Run against the validator's findings:

- **the verdict** — `{{findings}}`
- **the raw validation output** — `{{gatelog}}`

Read the verdict first. Read the log when a finding names a check, because
the log says what the check actually printed and the verdict says what the
judge made of it.

## What you get, and what you do not

You get **the findings and the issue**. You do not get the plan or the
implementation report, deliberately: a fix that re-reads the plan tends to
re-argue the plan rather than address the finding, and the finding is the
only thing that failed.

## Fix the finding, not the symptom

Take the findings one at a time, highest severity first. For each, fix the
cause in the source.

**The prohibitions, from the repo's own answers about how tests get faked**
(`FACTORY_RULES.md` §2):

1. When a check is red, the cheapest repair is always to make the check
   quieter: deleting or weakening the assertion, skipping the test, mocking
   the LLM provider away, catching and swallowing the error, special-casing
   the test input. Every one of these turns the light off rather than fixing
   the wiring, and every one is an **auto-reject**. The paths that would let
   you do it are denied to this node, so the attempt will fail rather than
   succeed quietly - read that as the design working, not as an obstacle.
2. If fixing the finding genuinely requires changing a check, then the
   finding is not a code bug and the correct move is to say so and stop. That
   is a `needs-human` escalation and it is a perfectly good outcome.
3. **Environment before code.** If the failing check names behavior the
   source plainly implements - if the tests pass locally in your reading and
   the gate still fails - verify the interpreter identity, the editable
   install currency, and the tool resolution order before touching source.
   This repo's most common failure class is environment drift, and this node
   has misdiagnosed it as a code defect more than once.

## Attempt cap

You are attempt {{attempts}} of 2. On the second failure this escalates and
stops. If you do not believe the finding is fixable within scope, say so
**now** rather than spending the last attempt on a guess - an escalation with
a clear reason is worth more than a second failed cycle.

## Then

run **exactly this command, verbatim** - it is the only one on your allowlist:

```
{{quick}}
```

Do not substitute another way of running the tests. A denied command is a fix
that never got checked, and a fix that was never checked is a guess. Then
hand back to the independent validator. A fix is never self-certified: the
node that made the change does not get to decide the change worked.
