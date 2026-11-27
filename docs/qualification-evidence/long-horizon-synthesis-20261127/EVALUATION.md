# Long-horizon creative synthesis: evaluation record (2026-11-27)

Scope: the initial trajectory-centred synthesis increment, as built on `feat/long-horizon-synthesis` from `main@077edc09` (PR #652).
Design: `docs/design/2026-11-27-long-horizon-creative-synthesis.md`. Owner: `src/auteur/beginner/studio_architecture_synthesis.py`.

This record preserves every authentic answer, critique, failed preparation, and revision, in the order they happened. It does not
claim creative quality for Auteur as a whole. The sample is a single study, a single mechanism family, and a small number of runs.

## 1. Claim ceiling

- Demonstrated: the owner accepts and refuses answers mechanically (identifiers, references, Book numbers, quotes, criticism
  identities); the served journey works end to end with exact request equivalence; each authentic answer is stored unedited beside
  its request.
- Not demonstrated: that a synthesis reads the record correctly. The independent grounding critic found misreadings in the first
  contract's answers that the owner accepted. Section 5 records them. Section 6 records the revision that tries to make the owner
  check the words of the basis, which is a check on quotation, not on meaning.
- Not demonstrated: that a trajectory form produces better creative understanding than an ordinary inquiry. The comparison arm
  had less evidence (section 4), so the comparison is confounded.
- No human author evaluation is claimed.

## 2. Reconsideration exercise count (correction to the earlier record)

The earlier reconsideration evaluation (`docs/qualification-evidence/evidence-reconsideration-20261127/EVALUATION.md`, section 8)
read "Five reconsiderations and one inquiry". The inventory holds four reconsiderations (A run 1, A run 2, B, C) and one inquiry (D),
five agent answers in total. That file now carries a dated correction. The zero-refusal and five-run statements were right.

## 3. Runs under the first contract (v1, schema 1)

Study: the seeded Spring Ledger study (`scripts/consequence_exercise.py seed`), Books 24 and 25, 182 Working Book elements read,
16 persistent questions. No record was changed by any synthesis. All answers were produced by fresh subagents from the saved request,
returned as text, and saved verbatim.

| Run | Developments and inputs | Request (sha256, prefix) | Owner | Standing at the end of v1 | Stages |
|---|---|---|---|---|---|
| A, run 1 | mechanism `th_maintenance`; question (exercise-A-question.txt) | `c71b…` is a pre-fix preparation; run 1 is `b6ba…` | accepted, first attempt | stale: the packet changed when the same-text coverage was added | 5 |
| A, run 2 | same | `55f1…` | accepted, first attempt | superseded by the follow-up D | 5 |
| B | mechanisms `th_maintenance` and `inst_mill_compact` | `5972…` | accepted, first attempt | current | 4 |
| C | mechanism `str_long_return` and question `q-finale-mechanism`; culmination named (exercise-C-culmination.txt) | `00a0…` | accepted, first attempt | current | 3 |
| D | follow-up of A run 2; two criticisms (exercise-D-criticism.txt) | `825b…` | accepted, first attempt | current | 4 |
| Inquiry arm | ordinary inquiry (`explore`, node `th_maintenance`) on the same question, same study | `2060…` | accepted by the inquiry owner | n/a | n/a |

Every answer passed the owner on its first attempt, with zero mechanical refusals. The owner checks citations, references, Book
numbers and criticism identities. It does not check meaning. That is the limit that the critics exposed.

Exercise E (served journey, `exercise-E/`): a fresh seeded study. The page itself prepared the run-2 request, and its fingerprint
equalled the recorded one, so the authentic run-2 answer was pasted for that exact request. The page then prepared the follow-up
request, equal to D's recorded fingerprint, and the authentic D answer was pasted. Desktop (1440 px) and phone (390 px) captures
recorded zero horizontal overflow and no page errors. Five served tests (`tests/test_beginner_studio_synthesis_browser.py`) and the
served consequence and reconsideration tests (10) passed at the same revision.

## 4. The comparison arm

The ordinary inquiry was prepared by the existing inquiry owner on the same node and the same question. It saw the whole working
candidate (47 KB of request) and no Working Book excerpts. The synthesis saw 11 to 19 cited Book elements (about 16 to 20 KB of
request) and the coverage record. Its evidence was therefore not comparable. The comparison can say what the two forms produced
from different inputs, and no more. A fair comparison would give the inquiry the same excerpts, which the owner does not accept as
input; that test is not run here (section 9).

## 5. Independent critique of the v1 answers (verbatim reports in `critics-v1/`)

**Grounding critic** (read-only fresh subagent; each claim checked against the evidence text in its own request). It counted
claims per answer and classified them: A, 30 claims: 17 supported, 5 overreaching, 2 misread, 5 unsupported, 1 not checkable.
B, 26: 21 supported, 4 overreaching. C, 46: 35 supported, 4 overreaching, 4 misread, 1 unsupported, 2 not checkable. D, 40: 34
supported, 1 overreaching, 2 misread, 3 not checkable. Its most serious findings:

1. A and D treat "now practising both counted and uncounted return" (E8, a present-tense statement of the cohort) as something stage 3
   must produce. A's prerequisite relation says "only s3 brings that practice about." I checked E8 and the stage: the critic is right.
2. C turns E5's conditional ("Accepting her granddaughter's crew means accepting a gap in the tally she keeps") into an event, "the
   steward's accepted gap", used in five places. I checked E5: the critic is right.
3. C treats the duplicated Book 25 text as a persisting condition, and makes a chronology claim the record does not state.
4. A states the Book 24 review point as recorded and drops the source's reversal (E7).
5. B's strongest opportunity drops the condition the record gives (E24).

The grounding critic also found that the owner's checks were all satisfied in every case: the cited identifiers existed, the stages'
references resolved, and no Book number was invented. The failures were of reading, which the owner cannot see.

**Creative-substance critic** (read-only fresh subagent). Its verdict: the ordinary inquiry gave the author more usable direction on the
question asked, while the synthesis found one fact the inquiry could not reach: Book 25 repeats Book 24's elements word for word.
The trajectory form was better at stating how each stage makes the next possible ("becomes_available", "changes") and at giving
alternative paths their viability. It was worse on load-bearing grounding (the same misreading as above), and more elaborate for what
it yields. It also said the comparison was confounded by evidence access, and that Exercise D changed the criticised judgements
correctly but made changes its `changes_from_prior` did not disclose: all three alternatives were replaced, and two of three
opportunities were dropped. The owner cannot check the completeness of a `changes_from_prior` list.

## 6. Revision: grounded quotes (contract v2)

Because the critics found misreadings that the owner could not detect, the contract was revised, not the prose. Each claim that cites
evidence must now carry `quote`: the exact words, up to 240 characters, from one of its cited items that carry its premise. The owner
verifies the quote as a substring of a cited item after whitespace is normalised, and refuses a claim whose quote is missing or not
in its evidence. It does not judge meaning, so the revision is a check on the words the author can read, and a test of whether the
misreadings survive a requirement to quote. The prompt adds three rules: quote only words the items contain; state an absence as "not
stated in the cited items", never as a fact about the story; and read tense and attribution exactly as the words give them. The page
shows each stage's quoted basis. Commit `914d1789`.

v2 runs and their critique follow in section 7, when they are complete.

## 7. v2 runs (contract with grounded quotes)

Each v2 request has its own fingerprint, because the output contract changed. Each v2 request supersedes the v1 request for the same
developments, as the owner's standing rule requires (`standings-final.txt`).

| Run | Developments | Request (sha256, prefix) | Owner | Independent grounding critique (verbatim in `critics-v2/`) |
|---|---|---|---|---|
| A, run 3 | `th_maintenance` | `b9bf…` | accepted, first attempt | All 15 quotes verbatim in their cited items. The critic listed 10 overreaching verdicts, 1 misread and 2 unsupported, with no denominator reported. |
| B, v2 | `th_maintenance`, `inst_mill_compact` | `4430…` | accepted, first attempt | 22 claims checked: 14 supported, 5 overreaching, 2 misread, 1 unsupported. |
| C, v2 | `str_long_return`, `q-finale-mechanism`, culmination named | `e82c…` | accepted, first attempt | 31 claims checked: 20 supported, 10 overreaching, 1 misread. |
| D, v2 follow-up of run 3 | `th_maintenance`; the four criticisms are the A critic's four, verbatim (`exercise-D-v2/criticism.txt`) | `ba44…` | attempt 1 refused, attempt 2 accepted | Attempt 1 added a field the strict contract does not define (`book_check`), and the owner refused it by name (`refusal-synthesis-attempt-1.txt`). Attempt 2 was given the same request, with one added sentence in the operator prompt reminding the agent that only the named fields are allowed. That sentence is a deviation from the earlier protocol, which used an identical prompt. The request, its fingerprint and the binding are unchanged. |

Exercise D v2 accepted all four criticisms. I checked each against the cited texts: E7 does call the review point "agent-proposed as P1";
E8 says the cohort "may claim standing" and does not mention a record; E7 makes the Right conditional on training and does not make the review
depend on training. Each criticism is therefore correct about the text, and the follow-up's revisions follow from them. The creative
substance of the v2 follow-up was not separately re-evaluated.

**What the quote contract achieved and what it did not.** The owner verified every quote as an exact substring of a cited item (no v2
refusal was for a quote). The critics confirmed the same: every quote is verbatim. The contract therefore removed invented or mistyped
anchors. It did not remove misreading. The critic found accurate quotes attached to claims they do not carry (for example a quote on
"a public capability record" under an opportunity about who is counted, and a quote on "Labour readiness has begun" under a claim that
Book 25 builds on Book 24, when identical text shows repetition). It also found conditionals read as events (E11's hypothetical read as
"now practising", and "if it is credited" dropped), and agent-proposed text labelled "recorded".

Rough comparison of the share of claims the grounding critic flagged as overreaching, misread or unsupported. The denominators and the
counting differ between rounds, so this is a rough signal, not a measure:

| Exercise | v1 flagged | v2 flagged |
|---|---|---|
| A | 12 of 30 (40%) | 13 verdicts, no denominator reported |
| B | 4 of 26 (15%) | 8 of 22 (36%) |
| C | 9 of 46 (20%) | 11 of 31 (35%) |
| D | 3 of 40 (8%) | not separately critiqued in v2 |

The v2 rate is higher for B and C. Two readings are possible: the quote requirement made the basis of each claim visible, so the critic
could test it (more verdicts, not more errors), or the constraint made the answers commit to more specific claims. This record does not
distinguish them. It is the reason the next responsibility is a claim-level verification of the basis, not another prompt.

**Served journey, v2 (`exercise-E-v2/`).** The page prepared the run-3 request and its fingerprint equalled the recorded one; the authentic
run-3 answer was pasted for it. The page then prepared the Exercise D v2 follow-up, equal to the recorded fingerprint, and the accepted
attempt-two answer was pasted. The trajectory (5 stages), the follow-up's four criticism verdicts and its four changes rendered at 1440 px
and at 390 px, with zero horizontal overflow and no page errors. The page shows each stage's quoted basis.

**Final owner standing (`standings-final.txt`).** The v2 requests are current for their developments; the v1 requests they replace are
superseded. The A run-3 request is superseded by its follow-up, as the rule requires.

**Not run.** A v2 creative-substance critique (the v1 one is in `critics-v1/`) and the fair comparison with the ordinary inquiry on
identical Book excerpts. The v2 creative claim therefore rests on the v1 comparison, which was confounded (section 4).

## 8. Bugs and failed attempts found along the way (preserved)

These are process findings, each fixed and tested. Each is a defect in code or in the probes, not in a model answer.

1. A coverage bug: the first Exercise A coverage listing was capped at six identifiers, so run 1 under-reported citing elements. The
   bound was widened to 24 identifier rows and a regression test added (PR #652 history).
2. A same-text measurement that compared element content hashes (which include book context) and so found no repeats. It was caught
   by a failing test, and the comparison was keyed on the element text instead (`studio_architecture_synthesis.py`, coverage).
3. A standing bug: a synthesis was superseded by any later synthesis on the canvas, including of other developments. Superseding is
   now per set of developments (`latest_by_developments/`), with a regression test. The stored results were re-prepared to write the
   pointers; the request identities did not change.
4. A fingerprint bug: the Story Vision was clipped to 800 characters in the packet, so an edit beyond the clip did not change the
   fingerprint and the standing stayed current. The fingerprint now covers the whole source each record was read from.
5. A served placement bug: the synthesis section was placed inside the hidden review section, so it never showed. Moved beside it;
   the served tests then passed.
6. A draft-loss bug: a refused response was lost on re-render. The response draft is now held in the panel state.
7. Probing with the wrong script name (`inspect.py`) shadowed a standard module; renamed.
8. Exercise B and C first used question-only developments, which carry no Working Book citations in this seed (the question texts are
   not cited by element `question_refs`). Those preparations were replaced by mechanism developments, which carry the evidence. The
   question-only preparations remain in the study as superseded or unanswered records and are not part of the evidence.

## 9. Limits and what is not run

- The ordinary inquiry arm is not given the same Book excerpts. The fair test is not run; it is the first item of the next increment.
- The grounding critic is one fresh subagent per round, and its counts vary with its sampling. The v1 and v2 counts are therefore
  comparable only as a rough signal.
- Handoffs from accepted reconsiderations are implemented and owner-tested, and the served picker is implemented, but no authentic
  synthesis used a handoff. Exercise D used criticism only, which the mission allows.
- Natural-language selection of developments is not built. The author selects up to three developments on the page.
- Stages beyond the existing Books are proposals. The seeded study has two Working Books, so the synthesis cannot read the Series it
  would project.
