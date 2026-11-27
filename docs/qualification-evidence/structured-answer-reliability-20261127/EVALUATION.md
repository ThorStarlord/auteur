# Structured-answer reliability and mechanism-centred reasoning: evaluation record (2026-11-27)

Branch `feat/structured-answer-reliability`, from `main@157d243c` (PR #650 merged). Tool: `scripts/mechanism_exercise.py`.
Every replayed step is named. Every refused output is kept with the owner's message. Nothing is claimed beyond what the owner accepted,
and every independent review is reconciled against the packet below.

## 1. Outcome in one paragraph

PR #650's version 3 consequence analysis never delivered its output contract to the responding agent. The consequence request carried
no machine-readable schema, although the Architecture and Working Book paths already attached one. This increment attaches the
authoritative contract, generated from the owner's model, to every new consequence request and to every new inquiry request. It adds a
citation index that says which identifiers each field may take, reports every failing rule of one answer together, keeps each refusal
beside the owner's exact message, and gives a bounded correction. Under this contract, fresh agents produced accepted analyses or
inquiry results in four of five attempts that reached the owner, and every accepted result was reviewed by an independent critic who
found real problems the owner cannot detect. Reliable delivery is demonstrated for this small sample. Reliable creative quality is not.

## 2. What was built

| Area | Change | Verified by |
|---|---|---|
| Consequence contract | `prepare_architecture_consequence` attaches `model_output_contract(ConsequenceAnswerV3)` (or `ConsequenceAnswerV2` when a version 2 request is asked for). | `tests/test_structured_answer_reliability.py` |
| Inquiry contract | `prepare_architecture_inquiry` attaches `model_output_contract(ArchitectureInquiryResult)`. | `test_an_inquiry_request_carries_the_authoritative_output_contract...` |
| Historical requests | Not rewritten. A request without the key keeps its fingerprint. | `tests/test_host_agent_output_contract.py` (existing, unchanged) |
| Citation index | `consequence_packet.citation_index`: `instruction`, `selected_alternative`, `question_wording`, `current_mechanisms`, `inheritance_from`, `inheritance_to`, `inheritance_to_recorded`, `recorded_steps`. Derived from the owner's kind and provenance rules; the owner still checks every citation. | `test_the_packet_says_which_identifiers_each_field_may_take...` |
| Shape guidance | Version 3 instruction states what the schema cannot: intent is never a basis word; concern counterevidence is strings, mechanism counterevidence is objects; a recorded phase, history item or mechanism is never an inheritance target; the citation rule. | `test_the_version_three_instruction_states_the_shapes...` |
| Combined refusals | Every failing rule of one answer is reported together, numbered, each stated once; a single failure keeps its own wording. Versions 2 and 3; acceptance unchanged. | `test_every_failing_rule...`, `test_a_single_failing_rule...`; the 56 version 2 and 3 owner tests pass unchanged |
| Refusal kept | A refused response is kept as `refused/NN-<digest>.json` with the owner's exact message beside it (`.refusal.txt`). Identical refusals are counted separately. | `test_a_refused_answer_keeps_the_owner_refusal...` |
| Completion record | An accepted analysis records `completion: {attempt, refused_attempts, first_pass}`. Historical analyses carry none. | `test_a_first_pass_acceptance...` |
| Correction brief | `consequence_correction_brief` quotes the owner's message unedited and asks for the same analysis, changed only where the message names a rule. It adds no claims, identifiers or mechanisms. | `test_the_correction_brief_quotes...` |
| Exercise tooling | `mechanism_exercise.py`: Book-element evidence reads the owner's freshness values (`book_element_evidence`); inquiry prepare takes `--book-evidence`. | Used in sections 4 and 5 |

## 3. Diagnosis of PR #650's refusals

The PR #650 refusal messages (in `docs/qualification-evidence/mechanism-centered-deliberation-20261127/`) were reread against the
contract the agents never received:

| Class | Examples from the record | Layer that owns the fault | Addressed by |
|---|---|---|---|
| Key names not stated | `disposition` for `status`; `mechanism`, `provenance`, `books`, `order` | Delivery: no schema in the request | Contract attached (not present in PR #650's requests) |
| Literal values confused | `intent` filled with `recorded`, `interpreted`, `speculative` (basis words) | Delivery and instruction | Schema enum; instruction states intent is never a basis word |
| Prose where a literal is required | `intent` given a sentence (Exercise C) | Delivery | Schema enum |
| Object where a string is required | concern `counterevidence` given objects (Exercise C) | Delivery | Schema: strings; mechanism counterevidence objects, stated in the instruction |
| Conditional field omitted | `intent` missing for transformed and possibly displaced concerns | Semantic rule the schema cannot express | Stated in the instruction; not defaulted by the owner |
| Evidence identifier confused with record name | `keeps` given a question identifier (Exercise C) | Evidence usability | `citation_index`; the owner still refuses it |
| Inheritance target outside the rule | `to` given a `recorded_phase`, a Book range | Evidence usability | `citation_index.inheritance_to` lists the eligible targets |
| Cited counterevidence not independent | Exercise A (this increment) attempt 1 cites the mechanism itself | Model compliance against a stated rule | Unchanged rule; corrected once (section 4) |
| One refusal per attempt | PR #650 Exercise A attempts 4 and 5 each named one rule | Owner reporting | Combined refusals |

Two classes the contract does not solve: a conditional rule and a counterevidence-independence rule. Both are stated in the instruction and
remain owner-enforced.

## 4. Authentic exercises

Each answer is a fresh sub-agent's output, given only its request file, and passed through the owner unedited. Saved copies differ from the
agents' files only in line endings (the Windows text write stores `\r\n`); the JSON text is identical. Responding model and runtime are not
reported by the host. The owner calls no provider.

### Exercise A: PR #647's mechanism transformation (`l_compact_hands_in_kind`)

- **Baseline matched.** Rebuilt request `7c34d34a…`, the one PR #647 recorded (`exercise-A/baseline-check.json`).
- **Proposal reproduced.** One component changed (`l_compact_hands_in_kind`, function); no question changed (`exercise-A/pending-review.json`).
- **Request.** Version 3, with the authoritative contract (`ConsequenceAnswerV3`), citation index and 89 evidence items
  (`exercise-A/request-analysis.json`, request `0b2decb0…`).
- **Attempt 1, initial answer: refused.** Two rules, reported together:
  1. `counterevidence to E13 must cite material other than the mechanism itself`
  2. `counterevidence to E12 must cite material other than the mechanism itself`
  The rule is stated in the instruction. The agent cited the mechanism's own record as its counterevidence. The refused answer and the owner's
  message are kept (`exercise-A/answer-analysis-attempt-1-refused.json`, `refusal-analysis-attempt-1.txt`, and under `refused/` in the request
  folder).
- **Attempt 2, correction (same agent, the owner's brief quoted unedited): accepted.** The brief is `exercise-A/correction-brief-attempt-2.txt`;
  the accepted answer is `exercise-A/answer-analysis-attempt-2-unedited.json`; `exercise-A/result-analysis.json` records
  `completion: {attempt 2, refused_attempts 1, first_pass false}`.
- **Not first-pass.** Acceptance after one correction is not a first-pass success.
- **Accepted content.** Reach `long_horizon`; five concerns; four mechanism-only alternatives (`questions: []`); four connections (two recorded
  through a shared node, one inferred with no recorded relation, one unestablished). The independent critic's findings on this answer are in
  section 8.

### Exercise C: author-directed exploration of `l_declined_goes_wild`

Upstream records were replayed through their owners, not re-reasoned, because each replayed fingerprint matched the recorded one:

- Inquiry `e4e7da12…` rebuilt from the recorded anchor, operation and author text: equal. The recorded accepted answer completed it (four hypotheses h1–h4).
- Revision `214aa190…` rebuilt from h1 and the recorded instruction: equal. The recorded accepted revision completed it. The pending review
  matches the recorded one exactly: one link changed, no question changed.
- **Note.** The `e4e7da12…` fingerprint was reproduced before this increment added the inquiry contract. Under the new code the same inputs give a
  different request. The replay files in `exercise-C/replay/` were produced before that change. Historical records are not rewritten.

- **Attempt 1, initial answer: accepted on the first attempt.** Reach `not_established`; four mechanism-only alternatives anchored on E12, one also
  on E32; connections: one recorded through a shared node, one inferred through adjacency (the owner's reading `adjacent_by_link`, not a
  relation), one inferred with no recorded relation, one unestablished (`exercise-C/answer-analysis-attempt-1-unedited.json`,
  `exercise-C/result-analysis.json`).

### Exercise B: the ledger-hours relation (PR #649, discovery possibility 2)

- **The record.** PR #649's discovery possibility 2 ("hours recorded in the ledger could expose the conversion's blind spot") went into
  deliberation and was found under-supported (`narrative-reference-stewardship-20261127/EVALUATION.md`).
- **Pathway.** The inquiry, with Book 24's element `cons-conversion-blind-spot` as one bounded evidence item (PR #649's single-element path).
  The owner's own read of the element supplies the freshness values.
- **Finding about the anchor.** The owner accepts only anchors the element records a reference to. The element records `th_hands_and_draw` alone.
  Its question reference is by position ("open question 6"), which the owner cannot read. The ledger link and the conversion link therefore
  cannot be anchors on this path; they reach the agent only through the working Architecture in the payload.
- **Attempt 1, operation `explore`: refused, a preparation defect.** The owner's rule: `explore requires at least two alternative hypotheses`.
  The agent returned no hypotheses and gave an assessment of the relation, which is what the author text asked for. The defect is the operator's:
  I chose `explore` for a text that asks for an assessment, not for alternatives. The refused answer is kept
  (`exercise-B/attempt-1-explore-refused/`). I did not count it as a correction of the same request.
- **Attempt 2, operation `challenge` (new request, chosen to match the author text before any answer was read): accepted on the first attempt.**
  Three hypotheses on three axes, eight recorded observations, eight uncertainties (`exercise-B/attempt-2-challenge/`). The answer separates what
  the ledger records from the unrecorded claim that draw can be read from hours.
- **Budget.** The re-preparation is a second fresh request for Exercise B. It is recorded as such, not as a correction.

## 5. Reliability measurements

Counts are per request. Subagent token and duration figures are as the host reported them for each sub-agent run. They are not cost; the
host exposes no cost figure.

| Run | Request | Schema supplied | Constrained generation | Outcome | Errors | Subagent tokens | Duration | Tool uses |
|---|---|---|---|---|---|---|---|---|
| A, attempt 1 | consequence `0b2decb0…` | yes | no | refused | 2 (counterevidence self-citation) | 214,869 | 274.8 s | 23 |
| A, attempt 2 (correction) | same | yes | no | accepted | none | 224,827 | 34.2 s | 1 |
| B, `explore` | inquiry `287a417e…` | yes | no | refused (preparation defect) | 1 (zero hypotheses for `explore`) | 121,778 | 130.9 s | 3 |
| B, `challenge` | inquiry `91f014e9…` | yes | no | accepted | none | 128,231 | 161.9 s | 3 |
| C | consequence `1c821d4a…` | yes | no | accepted | none | 224,596 | 292.3 s | 5 |
| Served inquiry | inquiry from the page | yes | no | accepted | none | 115,357 | 104.8 s | 3 |

Constrained generation was not used by any run: the host does not constrain decoding, so the schema is context, and the owner validates
afterwards. Sample: four first attempts reached the owner, excluding the operator-defect `explore` request: Exercise A (refused), Exercise C (accepted),
Exercise B `challenge` (accepted) and the served inquiry (accepted). That is three of four on first attempt, plus one accepted correction. This is a
small sample, not an estimate.

## 6. Verification (exit codes, final code)

- Baseline on untouched `origin/main` before any change: 116 passed (exit 0).
- New module `tests/test_structured_answer_reliability.py`: 10 passed.
- Nearby owner set (consequence, version 2 and 3, mechanisms, inquiry, Book-element questions, pending review, review, deliberation, discovery,
  question projection, provenance, Apply CLI, continuity, thread, host-agent handoff and output contract, proposal accept/apply): 248 passed (exit 0).
- Served consequence journey (system Python 3.14, Playwright): 6 passed (exit 0).
- Served inquiry-facing browser suites (interactive, deliberation, question workspace): 12 passed (exit 0).
- Node consequence labels: 10 passed (exit 0).
- Served captures: no horizontal overflow at 1440 px and 390 px; no page errors (section 7).

## 7. Served evidence

- `served/consequence-desktop-1440.png`, `served/consequence-phone-390.png`: the accepted Exercise A analysis, with its reading, reach, each
  concern's status and counterevidence, captured by `served/capture_served.py` from a temporary copy of the study.
- `served/prepare-*.png`, `served/prepare-record.json`: the Investigate control pressed on the first alternative (a mechanism-only alternative,
  accept_proposal); the status line reads that the investigation was prepared for the coding agent and that the Architecture is unchanged.
  The record's `creative_origin` field in `prepare-record.json` came from the first version of the check and is not evidence of the origin line; the
  screenshot and the owner's inquiry request (`served/prepare-*.png`, and the request in the working copy) are the evidence for the prepare step.
- `served/inquiry-from-page/`: the inquiry answer accepted by the owner, from a fresh agent, for the page's own request.
- `served/result/result-desktop-1440.png`, `served/result/result-phone-390.png` (captured by `served/capture_investigation.py result`): the owner's
  inquiry result in the coding-agent panel (opened by the page's own disclosure), with both hypothesis titles visible at both widths and no
  overflow or errors.
- **Steps not performed in the served run.** Step 8 (preparing a subsequent reviewed revision from the investigation) was not performed. Step 9
  is the no-change outcome: nothing was applied, and the pending revision stays pending. The served runs used a temporary copy of the study
  throughout; the exercise record was not driven.
- These captures show accepted fresh-agent output, not a replayed test answer.

## 8. Independent critics and reconciliation

Three read-only critics examined the three accepted results: A (consequence), C (consequence) and B (inquiry). Each received only the request and
the accepted answer, and no expected conclusion. The critics' full reports, as returned, are in `exercise-A/critic-report.md`,
`exercise-C/critic-report.md`, and `exercise-B/critic-report.md`. The critics' write calls were refused by the harness, so each returned its
report as text. Each finding was checked against the packet or the answer text. Confirmed findings are listed below; the owner accepted each
answer in spite of them, because the owner checks references and rules, not reasoning quality.

**Exercise A (critic A).** Confirmed:
- Books 24 and 25 are described as "recorded only as a title". The packet holds their book elements (E66–E71 and others). Overstated.
- "Books 24 and 25 do not cite the Compact" holds only for the 24 elements shown of 124 considered. The answer does not say so. Confirmed.
- "each conflict is recorded but not resolved". Only the E11–E19 disagreement is recorded. Overstated.
- E31's counterevidence cites E48 for the Special Draw Right, which E48 does not mention (E49 does). Citation mismatch.
- The mechanism comparison covers links and nodes only (34 links, 21 nodes); "no other relation changes" needs that scope stated. Confirmed.
- Conflict A (phase 4, E7) and the Books 19–21 maintenance shortfall (E52) are not considered. Confirmed omission; relevance is conditional.
- "The rebuild" is never defined for the every-season duty. Unresolved.
- Minor: "touches the hands-and-draw thread (E30)" implies an endpoint that E11 does not have.
Not confirmed or not adopted: the direction of the E11–E30 connection (F8) is an alternative reading the packet allows in both directions; recorded as such.
Legitimate speculation not offered (F11) is recorded as a creative option, not as a defect.

**Exercise C (critic C).** Confirmed:
- The reading of E32 attributes channel repair to the rota. The record says lineage crews carry channel repair; the rota carries the rest. Confirmed
  misreading (the critic's index was off by one, its substance is correct).
- "Reach is not established: no indexed Book element cites the changed link" rests on 24 of 124 Book elements shown. Confirmed as a missing condition.
- The earlier side of concern 1 uses the proposed word "unkept". Confirmed wording slip.
- Open question "Which channel takes the Long Return's surge…" is not considered. Confirmed omission.
- E53 (the Lowfen channel's link to maintenance) is not cited. Confirmed omission.
- The inferred connection E12–E32 rests on a labour claim no packet item supports; the standing is overstated. Plausible; the critic's proposed standing is an owner-level judgement the agent should make.
Not confirmed: none of the critic's quoted phrases were absent from the answer except the open-question text, which is correctly described as absent.

**Exercise B (critic B).** Confirmed:
- The eng_source recorded observation contains an inference: "A physical response does not depend on how the conversion counts return". Confirmed.
- "Not decided." is attached to open question 6, which the record does not mark that way. Confirmed.
- The Special Draw Right (l_lineage_right_on_draw), a second credit channel introduced in Book 20, is not mentioned. Confirmed omission.
- The shares as a unit of counting (str_measured_turn) is not in the unit list. Confirmed omission.
- The Book 15 trial's "surplus" construction, which is the closest recorded precedent for hypothesis 2, is not cited. Confirmed omission.
- The cost-of-counting emotion target (et_cost_of_counting, phase 4) is not engaged. Confirmed omission.
Not confirmed: "the relation … is undecided". The answer's "undecided" refers to the element's commitment authority, not to the ledger relation.

**Summary of the reviews.** Every accepted result had confirmed defects that the owner cannot detect. They are of three kinds: misreadings (E32), inferences inside recorded
text (eng_source), and omissions of recorded material that bears on the answer (Conflict A, the Special Draw Right, shares, E53, the Book 15 precedent,
the cost-of-counting target). None of the critics found an invented identifier. This is the main limit of the contract work: it makes acceptance
reliable, but not the completeness or accuracy of the reasoning the answer carries.

## 9. Limits

- Three accepted results, five owner submissions for the analyses and inquiries, and one correction. A small sample.
- Each run is one attempt by one fresh sub-agent. The model is not reported by the host.
- Exercise A's first refusal and Exercise C's first acceptance are one run each. The difference is not attributed to the contract alone.
- The schema was supplied in each request file. The record does not show whether each sub-agent read the `output_contract` field. The host transcripts
  are not inspected here.
- The inquiry replay in Exercise C predates the inquiry contract (section 4).
- Exercise B's first request was an operator defect (the operation), not an agent failure. It is recorded as a second request.
- The served run used the page's own controls for prepare, investigate and result. Step 8 was not performed.
- Critic findings are the critics' judgements, checked here against the packet. They are not an independent measure of reasoning quality.

## 10. Next responsibility

Structured-answer delivery is now reliable enough to test reasoning: a fresh agent receives the authoritative contract, its refusals are kept and
corrected in one step, and its accepted results are inspectable on the page. The reviews show that the remaining defects are in the reasoning
the answers carry: completeness of recorded material, and inferences written into recorded text. That is a creative-reasoning problem, not a
contract problem, and it is the next thing to measure. Long-horizon synthesis would multiply it, so it is not the next responsibility. The next
responsibility the evidence supports is a bounded reasoning-quality measure for the consequence analysis: a checklist that the critic applies to
each accepted analysis (recorded material cited, inference labelled, scope stated), measured across more analyses, before any further construction.
This is a recommendation; it has not been implemented.
