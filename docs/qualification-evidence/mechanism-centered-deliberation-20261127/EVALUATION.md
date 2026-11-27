# Mechanism-centred deliberation: evaluation record (2026-11-27)

Design: [`docs/design/2026-11-27-mechanism-centered-deliberation.md`](../../design/2026-11-27-mechanism-centered-deliberation.md).
Branch `feat/mechanism-centered-deliberation`, from `main@55cd1da9`. Tool: `scripts/mechanism_exercise.py`.

This record states what was built, what the authentic exercises produced, and what was not achieved. It names every replayed
step. No outcome here is claimed beyond what the owner accepted.

## 1. Outcome in one paragraph

The contract (version 3) lets a consequence analysis anchor an alternative on a mechanism alone, states relations between two
mechanisms with an epistemic standing that the owner checks against the recorded graph, and lets an investigation and a revision
keep the mechanisms they concern. The served page renders that and the owner's tests pass. The authentic exercises did **not**
produce an accepted version 3 analysis. Exercise A was refused five times and Exercise C once; every refusal is kept. The
refusals are compliance failures against contract rules the instruction states, plus one instruction defect now repaired. The
structured-output contract, not the reasoning, was the bottleneck in this run. The revision and the inquiry from Exercise C were
accepted by the owner.

## 2. What was built (owner, page, tests)

| Area | Change | Verified by |
|---|---|---|
| Recorded relation between mechanisms | `relation_status` in `studio_architecture_mechanisms.py`: `joined_by_link`, `shared_endpoint`, `adjacent_by_link`, `no_recorded_relation`, read from both candidates. One-hop adjacency is never a relation between the two. | `test_architecture_consequence_v3.py` (pure cases) |
| Version 3 answer | `ConsequenceAnswerV3`: alternatives anchored on questions (0-3), mechanisms (0-3), at most three anchors, `keeps` covering every anchor; `retire` added; `connections` (0-4) with standing `recorded`, `inferred`, `hypothetical`, `unestablished` and a basis for the last. | `test_architecture_consequence_v3.py` (31 tests in that file) |
| Owner checks | `recorded` refused unless the graph joins or shares a node; `graph_miss` refused where the graph records a relation; a historical record is never an anchor; a mechanism introduced by the proposal is accepted as proposed but never investigated on the current Architecture. | same |
| Stored analysis | Each connection stores the owner's graph reading beside the agent's standing; `investigation_anchors` read from the evidence. | same |
| Instruction | Key names are generated from the models; identifiers are cited by evidence identifier, never by record name. | `test_the_version_three_instruction_lists_the_exact_key_names...` |
| Investigation hand-off | `from_consequence` accepts mechanism anchors when they match the alternative exactly. | `test_a_mechanism_only_alternative_is_investigated_on_its_current_anchors...` |
| Revision scope | `considered_mechanisms` beside `considered_questions`; the owner does not widen scope from it. | `test_a_revision_made_from_a_mechanism_investigation...` |
| Single Book element | `question_associations` in the element's evidence packet, each read against the current open questions; an open engaged question may anchor. An association is engagement only. | `test_architecture_inquiry_book_element_questions.py` (5 tests) |
| Served page | Mechanism-only alternatives render without a question; a "How the mechanisms relate" section shows standing beside the recorded graph line; Investigate passes the owner's anchors. | `test_beginner_studio_consequence_browser.py` (6 served tests, including `test_a_mechanism_alone_is_read_as_a_connection...`); `tests/test_studio_architecture_consequence.mjs` (10) |
| Compatibility | Version 2 analyses are read unchanged. `prepare_architecture_consequence(contract_version=2)` still writes version 2 deliberately; a version 2 answer is refused for a version 3 request. | owner suites (version 1 and 2 suites, 73 tests, unchanged in behaviour) |

Regression: the nearby owner set (consequence, mechanisms, version 3, Book-element, inquiry, pending-review, review, deliberation,
discovery, question projection, provenance, Apply CLI, questions, continuity, thread) passed **225 of 225** on the current code.

## 3. Authentic exercises

Every answer below is a fresh sub-agent's output, given only its request file, and passed through the owner unedited. No
expected conclusion was given. Refused outputs are kept under `owner-kept/`.

### Exercise A: PR #647's mechanism transformation (Exercise B there)

- **Baseline matched.** The seeded Spring Ledger baseline's request is `7c34d34a…`, the request PR #647's proposal was made
  against (`exercise-A/baseline-check.json`). The recorded candidate therefore replays exactly.
- **Proposal.** One component changed: `l_compact_hands_in_kind` (function: "under B" → "in every season"). No question changed
  (`exercise-A/pending-review.json`). It was prepared and completed through the owner and not applied.
- **Analysis.** Five owner-refused attempts, no accepted analysis:

| Attempt | Owner refusal (summary) | Layer that owns the fault | What was done |
|---|---|---|---|
| 1 | 64 errors: key names the contract does not have (`disposition`, `mechanism`, `provenance`, `books`, `order`, `hypothetical`), record names used where evidence identifiers are required | **Instruction defect**: "identifier" meant both record names and evidence identifiers, and key names were not stated | Repaired: exact key names generated from the models; evidence identifier rule stated |
| 2 | 12 errors, all value-level: concerns missing a required `intent`; inheritance `to` written as a book range; trajectory `stage` and `basis` filled with descriptions | **Agent compliance** against stated literal values | Same agent given the owner's refusal and the same request |
| 3 | 5 errors: concern `intent` filled with step-basis words (`recorded`, `interpreted`, `speculative`) | **Agent compliance**, a confusion between two literal sets | Same agent, same request |
| 4 | 1 error: a concern claims `instruction_names_it` but cites no instruction item | **Agent compliance** against a stated rule | Same agent, same request |
| 5 | 1 error: an inheritance `to` cites a `recorded_phase` item; it must be a later Book's item | **Agent compliance** against a stated rule | Stopped here |

  The owner runs its checks in order (schema, then semantic rules), so later rules may still be unseen after an earlier
  refusal. Attempt 5 may not be the last defect.
- **Substance, from the refused attempt 5 (read by the operator, not accepted by the owner).** The reading states the single
  recorded change and that no question changed. It cites a recorded connection through a shared node (`inst_mill_compact`,
  `th_maintenance`), which the owner's graph check would accept. It labels an unlinked comparison as inferred. It offers
  alternatives with no question at all (`questions: []`), which is the mechanism-only case this work exists for. These are the
  operator's reading of an unaccepted answer; they are not an owner result.
- **Not done.** No investigation or revision was taken from Exercise A, since no alternative was accepted.

### Exercise C: author-directed exploration of an unchanged mechanism

- **Direction.** The operator wrote the author text (no human author is present), directing exploration of the declined-share link
  `l_declined_goes_wild`: whether refusing a share could carry a consequence for the one who refuses. It names no conclusion.
- **Inquiry (accepted first attempt).** Operation `explore` on the link. Four hypotheses on four axes: `causal_engine` ("refusal
  drains to the refuser's own ground"), `character_agency` ("refusal stays at the breach, in person"), `social_scale` ("refusal
  exists only as a whole terrace's refusal"), `structure` ("declined water is held upstream in the high cistern"). The uncertainties
  name a recorded gap (the refuser's branch layout) and a value that is not established (`exercise-C/result-inquiry.json`).
- **Choice.** The operator selected `h1`, the alternative closest to the direction's question. This is an operator choice, not an
  author choice, and is disclosed as such.
- **Revision (accepted first attempt).** Prepared through the owner with the selected alternative and its scope. The fresh agent's
  candidate was accepted as a pending revision. Exactly one component changed: `l_declined_goes_wild` (function). No question
  changed. The revision record names the considered mechanism (`exercise-C/request-revision.json`, `pending-review.json`). Not
  applied.
- **Analysis.** Refused on its first attempt, 23 errors, all in the same compliance classes as Exercise A: `intent` written as
  prose; `counterevidence` given as objects where the concern field takes strings; `unresolved` given as a string where it takes a
  list; a list of four evidence identifiers where three is the limit; inheritance `to` as a range; trajectory `stage` and `basis`
  given descriptions; `keeps` given a question identifier where an evidence identifier is required (`exercise-C/owner-kept/`).
  No accepted analysis.

## 4. Served evidence

- `served/consequence-desktop-1440.png` and `served/consequence-phone-390.png` show the consequence panel for Exercise A's pending
  proposal (the compact link), with the "How the mechanisms relate" section, a Recorded chip and the owner's graph line
  ("Both name the same node as an endpoint (node inst_mill_compact)").
- **These captures show a replay, not an agent's reasoning.** The served study was completed with the owner-validated test answer
  `mechanism_answer` from `test_architecture_consequence_v3.py`, which the operator wrote to pass the owner's checks. It is
  disclosed here because the authentic Exercise A analysis was not accepted.
- `served/served-record.json`: overflow 0 px at 1440 and at 390; no page errors; the connection and the mechanism-only alternative are
  present at both widths.
- `served/capture_served.py` reproduces the captures.

## 5. Follow-ups: disposition

- **16A, explicit decline or withdrawal: not built.** The Book lifecycle has no withdrawn state, and adding one changes recorded
  state. Leaving a proposal unapplied remains the non-destructive path, and it records nothing. Needs an owner decision on a
  record-state for withdrawal; no historical evidence is deleted by anything in this change.
- **16B, single Book element: built.** The packet carries question associations and anchors open engaged questions. No seeded
  element carries an association, so the behaviour is tested through the owner's packet function with only the element read
  stubbed. This is weaker evidence than an end-to-end study.
- **16C, historical reproduction: documented, not rewritten.** `question-linked-narrative-inheritance-20261127/reproduce/README.md`
  records PR #648's execution context (merge `77c5848a`), the field mapping, and that the scripts were not run on `main`. Evidence is
  untouched. Whether the recorded values match current code was not checked.
- **§10, discovery basis: deferred.** A discovery's relation was not made explicit. It needs a discovery answer contract of its own.
- **Exercise B (ledger hours, PR #649): not run.**
- **Critic pass (§18): not run.** No independent read-only critic examined the accepted or refused answers.

## 6. Limits

- One run per attempt. Refusals are classified by the operator from the owner's messages, not by an independent reviewer.
- Exercise A and Exercise C produced no accepted version 3 analysis, so the authentic claims are limited to the inquiry, the revision
  and the owner's refusals. The contract's ability to hold a fresh agent's reasoning is not demonstrated.
- The graph reading is structural. A shared node is a fact about endpoints, not a claim about what the characters do.
- The served captures use an owner-validated replay answer.

## 7. Strategic learning and the next responsibility

The refusals say that fresh agents reason well enough to produce the substance (a single relation changed, a recorded connection
through a shared node, mechanism-only alternatives), and fail the literal shape of about thirty owner rules on the first and
later attempts. The owner did its job each time: every refusal named the rule, and no refused text was stored as the analysis.

The warranted next responsibility is **structured-answer reliability for host agents**: derive typed output shapes (not only key
names) from the owner's models; have the host-agent protocol supply the schema and a bounded correction loop; and measure acceptance
rate per attempt before judging the reasoning. This is not Long-Horizon Creative Synthesis. Long-horizon synthesis would multiply the
same literal rules, and the present bottleneck would dominate it. This is a recommendation; it has not been implemented.

## 8. Verification (exit codes as run)

- Owner consequence suites on the final code: 109 passed (exit 0). This is version 2 (`test_architecture_consequence.py`, 51 and
  `test_architecture_consequence_mechanisms.py`, 22), version 3 (`test_architecture_consequence_v3.py`, 31) and the Book-element
  association tests (`test_architecture_inquiry_book_element_questions.py`, 5).
- Nearby owner set: 225 passed (exit 0), on the final owner code.
- Served consequence journey (system Python 3.14): 6 passed (exit 0), re-run on the final code.
- Node labels: 10 passed (exit 0), re-run on the final code.
