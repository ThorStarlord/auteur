# Mechanism-grounded prospective narrative reasoning: exercise evidence (2026-11-26)

Design: [`../../design/2026-11-26-mechanism-grounded-prospective-reasoning.md`](../../design/2026-11-26-mechanism-grounded-prospective-reasoning.md).
Drivers: `scripts/consequence_exercise.py` (the existing staged driver) and owner calls made from short scratch scripts that do
the same steps. No provider was called. Every answer below is a sub-agent's unedited output, passed through its owner. Sub-agents
were fresh general-purpose agents on the sonnet model, given only their own request file, with no hint about the expected
conclusion. They are not the product's host agent.

Two rounds of owner tightening happened during this work. The first round's analyses were accepted under the first contract and are
kept under `contract-1-accepted-under-earlier-rule/`. The final analyses are the ones under the final contract.

## Exercises

| Exercise | Specimen | Proposal | Final outcome |
|---|---|---|---|
| A, motivating case | Spring Ledger (PR #645 chain, replayed) | question rewording; no component change | analysis accepted under contract 2 after one refusal and a correction |
| A, development | same | investigation of alternative `a3` (integrate) | inquiry accepted; no further revision (warranted no-change) |
| B, contrasting case | same specimen; not a second narrative | one recorded relation changed (`l_compact_hands_in_kind`); no question changed | analysis accepted under contract 2 after one refusal and a correction |

The repository holds no second specimen with a working Architecture, Working Books and a pending proposal of comparable completeness.
Exercise B is therefore a contrast within the same specimen: a mechanism transformation rather than a question rewording.

## Refusals, classified

| Refusal | Class | Disposition |
|---|---|---|
| Contract 1, Exercise A: no refusal on the first answer | — | accepted (archived) |
| Contract 2 replay of the contract-1 A answer: "counterevidence to E26 must cite material other than the mechanism itself" | owner rule added after review; the answer cited its own mechanism as counterevidence | the same agent corrected the answer from the owner's message; the corrected answer was accepted. The replayed answer is archived under `refused-under-contract-2/` |
| Contract 2 replay of the contract-1 B answer: "counterevidence to E13 must cite material other than the mechanism itself" | same rule | corrected by the same agent; accepted |
| Development inquiry, first attempt: "question dec-conversion-settlement is not an open question" | agent compliance failure: a Book decision identifier was cited as a question identifier | archived under `development/refused/`; corrected by the same agent with the owner's message; accepted. The later re-run on the final analysis was accepted first time |

The contract-1 replays show what the owner now checks that it did not before. Each refusal is a rule the owner enforces. No rule was relaxed.

## Exercise A: the motivating case

**Inputs.** The discovery, investigation of `p3`, deliberation answer and revised candidate are the PR #645 recorded answers, replayed
through the driver. Replay request identities differ from PR #645 records (new request identities; the content is the same).
The packet holds 104 evidence items, 55 of them mechanisms (all `preserved` or `historical`), and 24 Working Book elements from
124 eligible.

**Final analysis (contract 2).**
- Reach: `conditional_inheritance`.
- Concerns: five, with a `possibly_displaced` concern about the durability question that the instruction names, and an `introduced`
  concern about purchased draw.
- Mechanisms: six readings. The three links the motivating case turns on are among them. `l_conversion_sets_draw`,
  `l_trade_draws_without_return` and `l_compact_hands_in_kind` are all `preserved`, and each reading says what the record does
  and labels the reading as interpretation.
- Inheritance: two `plausible_inheritance` (one from the question's wording to Book 24's decision; one from the Hands and draw node to Book 24's
  `cons-conversion-blind-spot` element), one `proposed_inheritance` (Book 24's Compact decision), and one `unknown_inheritance` for Book 25, which
  is listed by title and whose decisions on these questions were not read.
- Trajectories: three, each `hypothetical`. Steps are labelled `speculative`, `interpreted` or `recorded`.
- Alternatives: `keep_baseline`, `accept_proposal`, `integrate`, `separate`. Each keeps the wording it names, and the approach names are
  the owner's.
- Not established: six items, including whether the durability wording was intended.

**Comparison with the PR #646 analysis of the same proposal.** That analysis (version 1) could not cite the three links. It
could not separate recorded from plausible inheritance, and it had no hypothetical status on its trajectories. Those are the
differences the capability adds. The comparison is qualitative. It uses one run per arm and different schemas, so it does not show that
one is better.

**Limits found by review, not fixed by the owner.**
- The critic found that the analysis does not connect Book 24's `cons-conversion-blind-spot`, which says the blind spot "makes open
  question 6 concrete", to the Compact question. Question 6 is the Compact question by position. Book text refers to questions by
  position as well as identity, and the owner cannot read that reference. This is a reasoning gap and a source fragility, recorded as
  the next responsibility in the design.
- Alternative `a1` says reach "is left to the Compact-settlement question". The word reach is used in two senses there. This is a
  reasoning error the owner cannot catch.
- The analysis did not choose a `recorded_inheritance`, although Book 24's `inh-uneven-draw` (its record of hand-light draw falling
  since the conversion) was in the packet. It cites the conversion's node, so it was available.

## Exercise A: development

Investigation of alternative `a3` (integrate). The investigation was prepared through the owner's inquiry path with the intent the
served page sends (`compare`, the alternative's two questions, the alternative's suggested wording, `from_consequence`). It was not
prepared by clicking the page's button.

The first answer was refused (see the table above). The corrected answer was accepted. The investigation was then repeated on the
final analysis, because the first investigation's origin had become a superseded analysis. The final investigation was accepted on
its first attempt.

**Result.** Three readings of the two questions, none recorded as decided: shared non-resolution; the Compact as a test of the
conversion's reach; and keeping the questions independent so that `a3` lapses.

**Decision.** No further revision was prepared. The record does not decide among the readings, and any revision would decide one of
them. That choice belongs to the author. This is a legitimate no-change outcome.

## Exercise B: a mechanism transformation (contrasting case)

**Proposal.** A fresh agent changed exactly one component: the Mill Compact's labour duty (`l_compact_hands_in_kind`), from "under B" to
"in every season". No question changed. The owner's pending review lists one changed component and no question changes.

**Final analysis (contract 2).**
- Reach: `conditional_inheritance`.
- Mechanisms: six readings. One is `transformed`, with `changed_fields: [function]`, and states the transformation. Five are `preserved`
  and stated as unchanged, including `l_trade_draws_without_return`, which the analysis puts in tension with the changed relation rather
  than calling it altered.
- Concerns: six, three of them `possibly_displaced` with intent `not_established`.
- Inheritance: two plausible, one unknown, one proposed.
- Trajectories: three, all `hypothetical`, with steps labelled `interpreted` or `speculative`.
- Alternatives: none. The analysis offered none, because no question changed and every alternative must keep the wording of the
  questions it names. This is a legitimate outcome, and the analysis says why.

**Limits.** One mechanism is the only changed record, so this case shows the `transformed` path but not a rich set of transformations.
The owner's `possibly_displaced` status is used for unchanged records under tension, because the status vocabulary has no
"in tension but unchanged" value. The critic flagged this, and it is a vocabulary limit, not fixed here.

## Served journey (final study)

Run on a copy of the final Exercise A study, through the detached served Atelier (`studio.html`, canvas `spring-ledger`).

- The consequence panel shows the current analysis, with the `reach` line and the v2 sections.
- A mechanism opens to its provenance, its recorded text, why it is present, the reading, the change to its operation, the
  conditional consequence, counterevidence and unresolved points. The summary line reads "Preserved in the proposal".
- Inheritance items show their kind and their from and to, and the evidence is one step away.
- Trajectories show the `Hypothetical` badge and steps labelled by basis.
- Alternatives show their approach, the owner's definition, what they keep and what they examine. The labels read "Keep the baseline
  concern", "Accept the proposal as written", "Integrate" and "Separate".
- A Book decision's evidence line reads "question in proposal: reworded". The status describes the question, not the decision.
- The creative panel shows the validated investigation of `a3` and states that there is no architecture revision and no story
  acceptance.
- The proposal stays pending. Apply was not performed.
- The console shows no errors. Page overflow is 0 px at 1440 px and at 390 px. The consequence section is 338 px wide at 390 px.

Screenshots: `served-final/` (final contract), and `exercise-A/contract-1-accepted-under-earlier-rule/served-screenshots/` (contract 1,
kept as evidence of the earlier analysis). The earlier set includes one capture made before the 1440 px emulation; its name says so.

## Automated verification, final code

- `tests/test_architecture_consequence.py`: 51 tests, passed, including the version 2 refusal table (each refusal names the owner message it must give).
- `tests/test_architecture_consequence_mechanisms.py`: 22 tests, passed.
- `tests/test_studio_architecture_consequence.mjs`: 8 tests, passed.
- `tests/test_beginner_studio_consequence_browser.py`: 5 served tests, passed.
- Nearby regression (inquiry, pending review, review, deliberation, discovery, question projection, provenance, apply CLI, questions): run on the final code. The result is recorded in the PR body.

Observation not diagnosed: a single-process pytest run of `tests/test_architecture_consequence.py` on this host exited silently with status
127 after 18 tests, with no traceback. The same tests pass under `-n 4`. The code path has no exit call. The cause is not isolated.

## Limits, consolidated

- One run per exercise and per arm. Refusals are classified, and the comparison is qualitative.
- Sub-agents are sonnet, not the product's host agent. No human author judged the results.
- The owner checks that a citation exists, has the kind and side the claim needs, and supports the basis stated. It does not check
  that the agent's account of the cited item is accurate, nor that a counterevidence item limits the reading. Both reviews and both
  exercises show reasoning errors the owner cannot catch.
- Book text refers to questions by position as well as identity. The owner cannot follow a positional reference.
- The inventory and element selection are capped. On the Spring Ledger proposal, 100 of 124 eligible Book elements are not shown and are counted.
- Exercise B is a contrast within one specimen.
- The served investigation in Exercise A was prepared through the owner's path, not by clicking the page button.
- The critic's inheritance and reach findings are recorded above. They are reasoning issues, not owner defects, and they are not fixed.
