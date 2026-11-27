# Evidence-grounded reconsideration: evaluation record (2026-11-27)

Branch `feat/evidence-grounded-reconsideration`, from `main@8199e720` (PR #651 merged). Design:
`docs/design/2026-11-27-evidence-grounded-reconsideration.md`. Owner: `src/auteur/beginner/studio_architecture_reconsideration.py`.
Driver: `scripts/reconsideration_exercise.py`. Every replayed step is named and every refused output is kept; nothing is claimed beyond what the owner accepted.

## 1. Outcome in one paragraph

An author can now reconsider one consequential claim of an accepted consequence analysis, through the served page. The reconsideration is bound to that analysis's
exact result bytes and to the claim as the analysis stated it. The owner recovers the exact source wording the claim needs from the candidates the analysis read,
and, for claims about later Books, an exact coverage count of Working Book elements. A fresh agent answers a focused contract; the owner validates it and stores it
beside the analysis, which is never rewritten. In the authentic runs the agents' reconsiderations corrected two claims, qualified one, and kept a speculative
connection, qualified it, and partly accepted the criticism that asked for its withdrawal (verdict `partly_accepted`, as stored in `exercise-C/`). The coverage recovery exposed a real overstatement in the accepted analysis, and the second run found the
Compact citations exactly. Acceptance was first-attempt in every reconsideration. The sample is small, and it does not establish general reasoning quality.

## 2. What was built

| Area | Change | Verified by |
|---|---|---|
| Binding | A reconsideration request records the analysis request sha, the sha of the result bytes it reads, the claim kind, reference and content sha, and the instruction and criticism shas. Its identity is deterministic (no nonce), so an exact replay is possible. Completion refuses when the result has changed. | `tests/test_architecture_reconsideration.py` (binding, idempotence, unchanged result, refused unknown claim) |
| Exact recovery | Mechanism records are read in full from the baseline and proposed candidates that the analysis's own request carries, with each record's version digest and freshness `as_analysed`. Cut at 2,000 characters with a flag. | recovery test (`version_sha256` equals the digest of the analysed candidate) |
| Coverage recovery | For reach and inheritance claims: every readable Working Book element is counted now (`elements_read`), the packet's considered count (`elements_considered_by_packet`), the supplied count (`elements_supplied_to_analysis`), and the elements citing the claim's nodes (`citing_count`), listed in full up to 24 identifier rows. | coverage test (the three counts are distinct and ordered); listing test |
| Focused contract | `ReconsiderationAnswer`: disposition (eight literals), new consideration, reconsidered judgment, evidence, criticism assessments, creative significance, remaining uncertainty, downstream effects. Generated through `model_output_contract`. | contract test (the schema names the model) |
| Owner rules | Every identifier must be in the analysis packet or the recovered set. A correction must cite a recovered record. Each criticism assessed must be one the request supplied, once. A refused answer is kept beside its message. | rule tests (named identifier; correction rule; criticism identity) |
| Projection | `status`, `standing` (`current` only while the analysis is the live analysis; otherwise `historical`), the claim's original text as the owner holds it, the recovered records, the answer, and the awaiting request for copying. | row tests; served tests |
| Routes | `GET …/consequence/<sha>/reconsiderations`; `POST …/consequence/reconsider` (prepare, returns the request and the record); `POST …/consequence/reconsider-response` (complete). | served tests (prepare, paste, submit) |
| Served control | "Reconsider this claim" beneath each concern, mechanism, inheritance, connection, alternative and the reach. Visible labels; the owner's original text; the verdict; judgment; criticism weighed; remaining uncertainty; recovered evidence in progressive disclosure. Unsent text and open state survive redraws and refusals. | `tests/test_beginner_studio_reconsideration_browser.py` (4 tests, including 390 px) |

Reuse decision (design, section 2): the consequence owner's lineage, storage, standing and refusal pattern are reused. The inquiry `challenge` operation was examined and
not used, because it binds to no claim of an earlier analysis and recovers no source. The pipeline reasoning runtime and the Critic Integration Contract were not
routed through: they govern deterministic pipeline critics, whose reports are not host-agent records. Their invariants (read-only, provenance, observation apart from
hypothesis) are honoured.

## 3. Failure model, from the authentic PR #651 evidence

| Failure | Evidence | Layer | Addressed by |
|---|---|---|---|
| Misreading from a clipped source | The packet clipped the maintenance record mid-word ("channel repai"); the analysis read "the rota carries channel repair". The full record names lineage crews under a Special Draw Right. | Evidence usability | Exact recovery of the full record from the analysed candidate |
| Overstated coverage | "Books 24 and 25 do not cite the Compact" was stated from 24 of 124 considered elements. The full set contains 8 citing elements (4 per Book). | Coverage accounting | Coverage recovery with exact counts |
| Inference presented as record | The `eng_source` observation in the inquiry asserted a physical response the record does not state. | Epistemic standing | Not automated; the reconsideration contract asks the agent to separate statements, and it was checked in the inquiry critic's report |
| Omitted record | Special Draw Right, shares unit, Book 15 precedent, Conflict A, cost-of-counting target | Selection | Not recovered in this increment except where a claim names it; see section 8 |
| Clipped non-mechanism text | The selected alternative's text (E2) was clipped in the packet and is not in the analysis's request | Evidence usability | Not recoverable from the request; the agent named it as unread (Exercise B, section 5) |

## 4. Authentic reconsiderations

Each run is one fresh sub-agent given only its request file, and the agent's unedited answer is passed through the owner. No critic was run on any reconsideration.
Saved copies are byte-identical to the agents' files apart from line endings.

### Exercise A: coverage and relational reconsideration

- **Claim.** The reach claim of the accepted Mill Compact analysis (request `0b2decb0…`). The author's question (`instructions/exercise-A-instruction.txt`) asks whether the
  claims about later Books and the Compact's mechanisms are supported; it does not name the known errors.
- **Run 1 (truncated listing).** Request `de842869…`. Owner-accepted, disposition `corrected`, evidence E11, E90, E91, E92
  (`exercise-A/run-1-truncated-listing/`). The coverage record listed 6 of 19 citing elements. The agent correctly found the Compact-node citations contradicting the
  claim, but it reported two Book 24 Compact citations where there are four, because the listing had been cut. It said so only for Book 25.
- **Owner defect and the change.** The listing bound (6 identifier rows) was too small for the set it claimed to cover. It was widened to 24 identifier rows, which
  covers every citing element in a study of this size; a truncated listing still says so. This changed the recovered evidence, so run 2 is a new execution condition,
  not a retry.
- **Run 2 (complete listing).** Request `0d14a92d…` (the fingerprint the served page reproduced, section 6). Owner-accepted, disposition `corrected`, evidence E11,
  E90, E91, E92 (`exercise-A/run-2-complete-listing/`). Its judgment: the Compact-node statement is contradicted (8 elements cite inst_mill_compact and 11 cite
  th_maintenance; the agent cites exact counts from the complete listing); the reach to Books 27–29 and the Book 30 choice stay hypotheses because no recovered
  record covers them; the claims touching E5, E13, E19, E30, E31 and E63 are left unresolved; and the later reach is qualified because the coverage record relates
  citations and does not say what they assert.
- **Checked by the operator.** The counts (8 Compact-node, 11 maintenance-thread, 0 both, 19 total; Book 24 holds 10 of the 19 and Book 25 holds 9) were recomputed
  against the study before this record was written.

### Exercise B: correcting a narrative misreading

- **Claim.** The `mechanism` reading of `E32` (th_maintenance) in the accepted declined-share analysis (request `1c821d4a…`). The question asks for the maintenance
  responsibility to be reconsidered against exact source, and does not give the correction.
- **Recovery.** The full `th_maintenance` node from both candidates (E91 baseline, E92 proposed), untruncated, containing "From Book 20 lineage crews carry channel
  repair under a Special Draw Right, and households that can meet the rota carry the rest."
- **Result.** Request `b08948d7…`. Owner-accepted, disposition `corrected`, evidence E91, E92, E32, E2. The agent states that the reading was wrong and that the
  record gives repair to lineage crews, names the dependent claim that must change, reconsiders the refusal-cost statement against E2 (the refuser's own fields and
  well), and keeps four uncertainties (flood effect on labour, the meaning of "the rest", who carried channel work in Books 12–19, and the clipped E2 text, which it
  says it did not read). The clipped E2 is the one limit of exact recovery here (section 3).

### Exercise C: protecting legitimate speculation

- **Claim.** Connection 2 of the accepted Mill Compact analysis: `E11`–`E30`, standing `inferred`, with its stated reasoning and assumptions. The author asks whether the
  inference is defensible and what the record supports.
- **Criticism supplied.** One criticism (`c1`): the connection should be withdrawn, because no recorded relation joins the duty to the thread, and the record says draw
  follows shares alone until Book 19. It overstates: the claim already stands as an inference with a stated basis.
- **Result.** Request `e7b78910…`. Owner-accepted, disposition `qualified`, evidence E11, E30, E90–E93. `c1` was `partly_accepted`: the agent accepted that no recorded
  relation joins the two and that the reading must state a Book 20 start, and rejected the withdrawal because the connection is already labelled inferred. The
  speculative significance (purchased draw as a possible second place where return labour bears on who is counted) is kept and labelled as not established by the packet.
  The agent also read E30's direction as matching the inference, which resolves the direction question that the PR #651 critic had raised.

### Exercise D: creative follow-through

- **Choice of alternative.** The reconsidered Exercise B correction changes the premise of the `integrate` alternative (a4: "Answer the refusal's first loss with the
  rota's labour"), whose anchors are the changed link and the maintenance node. The alternative is investigated through the existing inquiry, bound by
  `from_consequence` to the original alternative and its fingerprint. The reconsideration is not an input the inquiry reads; the author carries the corrected
  understanding into the author text (`instructions/exercise-D-author-text.txt`).
- **Request.** Inquiry `785e2f8a…`, operation `compare`, anchors: link `l_declined_goes_wild`, node `th_maintenance`. Owner-accepted on the first attempt, three
  hypotheses (`exercise-D/`): the rota answer tests belonging and the lineage answer tests competence; the lineage answer adds skill as a claim on water; the
  lineage answer re-stages custody as expertise.
- **No revision.** A subsequent reviewed revision was not prepared. The hypotheses are substantive, but choosing among them is the author's creative judgment, and no
  one of them is established enough to be written as a candidate Architecture without that choice. The warranted outcome here is no change. This is recorded as the
  outcome, not as a gap.

## 5. Reconsideration measurements

Host-reported subagent tokens and durations are as the host gave them. They are not billable increments, and no cost figure is exposed.

| Run | Request | Records recovered | Model calls | Acceptance | Subagent tokens | Duration | Request size |
|---|---|---|---|---|---|---|---|
| A, run 1 | `de842869…` | 3 (2 mechanism, 1 coverage) | 1 | accepted, first attempt | 91,441 | 89.8 s | ≈16 KB |
| A, run 2 | `0d14a92d…` | 3 | 1 | accepted, first attempt | 94,485 | 89.6 s | ≈18 KB |
| B | `b08948d7…` | 2 (one node, both sides) | 1 | accepted, first attempt | 86,492 | 65.1 s | ≈16 KB |
| C | `e7b78910…` | 4 | 1 | accepted, first attempt | 92,516 | 86.3 s | ≈20 KB |
| D (inquiry) | `785e2f8a…` | inquiry packet | 1 | accepted, first attempt | 123,350 | 126.6 s | ≈60 KB |

No critic calls were made, so the reconsiderations added no independent model call. The mechanical owner refusals were zero for all five runs. Every answer passed the owner
on the first submission. Correction budget: none used. The one repeated run (A) is a re-run under a changed owner recovery, recorded as a new condition.

## 6. Served journey

Captured by `served/capture_reconsideration.py` (Paths A and B) and `structured-answer-reliability-20261127/served/capture_investigation.py` (Path C), on temporary copies of
the accepted studies. Desktop 1440 px and phone 390 px were both captured; overflow was 0 px and there were no page errors in every capture.

- **Path A (correction).** The author opened "Reconsider this claim" beneath the reach claim, asked the question, and pressed prepare. The page's own request had the
  fingerprint `0d14a92d…` (`page_request_equals_recorded: true`), so the pasted authentic run-2 answer was the answer to exactly that request. The card shows Corrected, the
  original text (owner-derived), the judgment, the "what prompted it" line, the uncertainty list, and the recovered evidence disclosure.
  `served/path-a-reach-correction/`.
- **Path B (qualified, no change).** The same control under connection 2, with the criticism typed into the criticism field. The page's request was `e7b78910…`
  (equal). The card shows Qualified and `c1` weighed as partly accepted with its reason. Nothing was applied, and the connection stands as an inference.
  `served/path-b-qualified-no-change/`.
- **Path C (investigation prepared).** Investigate, on the declined-share analysis's first alternative (keep baseline), prepared an inquiry. The creative panel names the
  original alternative and says that its question is the analysis's suggested wording, not the author's. "Nothing in the Architecture has changed." This path
  prepares only: its completion is the owner's inquiry in Exercise D, which is a different request. `served/path-c-investigate-prepared/`.
- **Narrative unchanged.** The served runs drove copies. The owner tests assert that the narrative snapshot and the analysis result bytes are unchanged after a
  reconsideration, and the served test asserts the same on the page path.
- **Not performed.** Apply was not pressed in any path (this is the no-change outcome). Path D did not prepare a revision (section 4).
- **Presentation.** The screenshots were inspected: labels are visible on both text areas, and the original claim sits above the judgment. This is an engineering check,
  not a human-author satisfaction or accessibility-conformance claim.

## 7. Verification (exit codes, final code)

- Owner suite: 261 passed, exit 0. That is the nearby set from PR #651 (248) plus the 13 new reconsideration tests.
- Served suites: 22 passed, exit 0 (4 new reconsideration browser tests, the consequence browser suite, and the interactive, deliberation and question-workspace
  browser suites).
- Node consequence labels: 10 passed, exit 0.
- Driver and capture scripts parse; the served captures ran and recorded exit 0.

## 8. Limits

- Four reconsiderations and one inquiry, five fresh sub-agent runs in total, each by one fresh sub-agent. The reconsiderations are A run 1, A run 2 (the same reach claim, run again after the listing bound was fixed), B and C, so they concern three distinct claims. The model is not reported by the host. This is a sample for the mechanism, not a measure of reasoning.
- Correction (2026-11-27, long-horizon mission): an earlier version of this limit read "Five reconsiderations and one inquiry". The inventory in `exercise-A/`, `exercise-B/`, `exercise-C/` and `exercise-D/` holds four reconsiderations and one inquiry. The count of five agent answers, and the zero refusals across them, were right.
- The coverage listing had a defect (bound too small). It is fixed, and run 1 is kept as recorded. The fix changed the recovered evidence, so run 2 is the authority for
  the coverage counts.
- Recovery reads mechanism records and coverage only. The selected alternative's text (E2) was clipped in the packet and is not in the analysis's request, so the agent
  could not recover it (Exercise B said so). Other omitted records (the Special Draw Right, the shares unit of counting, the Book 15 precedent, Conflict A, the
  cost-of-counting target) are not recovered unless a claim names them. Recovery is bounded, not exhaustive, and the record says so.
- The study has Working Books for Books 24 and 25 only. The coverage record says which Books were read and which were unreadable, and it says that Books 27–29 and 30
  were not in the books read.
- The reconsideration does not show whether each sub-agent read the `output_contract` field. The host transcripts are not inspected here.
- No critic was run on any reconsideration. The corrections above were checked by the operator against the study (counts recomputed), not by an independent reviewer.
- The served captures drive a temporary copy of an accepted study, with exact request equivalence for the pasted answers. They are engineering evidence, not an
  author's session.

## 9. Strategic learning

The reconsideration capability now does what the mission asked at the level of mechanism: it binds to an actual earlier claim, recovers exact source and exact coverage,
validates a focused response, keeps the original, and lets an author carry a corrected understanding into an investigation. The authentic runs show that the recovery
changes what the agent can see: the clipped misreading and the overstated coverage were both corrected from exact source. They also show two limits: the recovery cannot
reach text the packet clipped without the candidate, and the reasoning remains a judgement that an owner cannot check beyond its contract.

The next responsibility the evidence supports is not Long-Horizon Creative Synthesis. The reconsideration capability is a sufficient foundation for building up the
author's use of it, but a broader reasoning layer would multiply the two limits above. The evidence supports a narrow next step: make the recovery of non-mechanism clipped
text owner-qualified where the candidate or the originating record still holds it, and measure whether recovered text changes the disposition in a larger sample. This is a
recommendation and has not been implemented.
