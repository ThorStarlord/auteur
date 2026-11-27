# Question-linked narrative inheritance and cross-Book reasoning: exercise evidence (2026-11-27)

Design: [`../../design/2026-11-27-question-linked-narrative-inheritance.md`](../../design/2026-11-27-question-linked-narrative-inheritance.md).
Every exercise runs in a disposable copy of the Spring Ledger study. Each Book change goes through the Working Book owner, and each Series
change through the Studio's Architecture review path. Nothing edits a persisted record directly, and no provider is called.

Two kinds of agent output are kept, and they are labelled separately:

- **Fresh agent output**: a general-purpose sub-agent on the sonnet model, given only its request file and a neutral task. It
  answered once, and the unedited answer was passed through the owner. These are the only outputs written by a reasoning or
  coding agent in this record.
- **Owner-scripted study material**: a change made by a script through the owner's own functions, as the consequence exercise does. It
  is labelled as study material wherever it appears.

## Summary

| Exercise | What was run | Outcome |
|---|---|---|
| A, Spring Ledger | Referent recovered through the owners; fresh coding agent answered a targeted Book 24 revision; owner completed, reviewed and applied it | Association established: blind-spot element → conversion question. Referent corrected (see below) |
| B, continuity | Owner-scripted steps on a copy of the applied Exercise A study: reorder, reword, unrelated revision, retirement, later association | Original binding kept at every step; nothing moved to a replacement question |
| C, creative reasoning | Owner-scripted proposal (study material): the conversion question is reworded, identity kept. Fresh reasoning agent answered the consequence request; owner accepted it. Independent critic read the packet and answer | Answer used the question-linked evidence; critic found overreach and one missed connection |
| Served journey | Playwright script on a disposable copy: pending association, review before Apply, Apply by the review's button, question reading after Apply, narrow screen | Every step passed; no page errors; no horizontal overflow at 390 px |

## The motivating referent (corrected)

PR #647 read Book 24's "open question 6" as the Mill Compact question. Verified through the owners on a freshly seeded study:

- Book 24's record is written against Series version `dd0448f7…`: 16 open questions, no identities.
- Position 6, counted from one, is index 5: "Is the Book 20 hands-to-draw conversion a lasting settlement, or a stage the
  finale must revisit?" Position 7 is the Compact question.
- Book 24's own engine element says "(open question 6)" for the conversion settlement question, so the Book uses the same
  numeral for the same question. Its Hesper element says "open question 10" for Hesper's motive question (index 9). The one-based
  reading is consistent across the Book's prose.

The earlier mapping was a zero-based misreading. See the project memory note on this numbering.

## Exercise A: establish the association

Inputs and sequence (`reproduce/exercise_a.py`):

1. `seed` seeds the Spring Ledger discovery study, then gives its open questions identities through a disposable Architecture
   revision (`assign_identities`, as the consequence exercise does). The referent facts are read from the exact recorded version
   (`reproduce/exercise-a/referent-recovered.json`).
2. `prepare` makes a targeted revision of the blind-spot element with a neutral instruction: check which open questions the
   element actually engages, record each by identity, and leave the element otherwise as it is. The packet also scopes the
   element's dependent typed edge, `edge-conversion-draw`.
3. A fresh coding agent read the request and the Book's current record and wrote the complete revised Book object. The output is kept
   unedited as `reproduce/exercise-a/candidate-book24-unedited.json`. It changed one element and no other. It added the association
   `q-conversion-settlement` to `cons-conversion-blind-spot`. It also restated the element's legacy `unresolved` label as explicit
   `attribution: unattributed` and `epistemic_status: unresolved`, which the owner requires for a changed element.
4. `complete` passed the output through the owner. The review was applicable, and its only change was the association. The review
   records the question's identity, its recorded index (5) and the version it is bound to.
5. `apply` applied the reviewed request through the owner. The question reading now lists one engagement, at `current_wording`.

Book 24 is still marked stale after Apply, because it was a partial revision of a Book that was already out of date. Its other elements
keep the Book's older baseline. The association is bound to the current Series version, as the design requires.

## Exercise B: continuity (owner-scripted steps; `reproduce/exercise_b.py`, `exercise-b/steps.json`)

| Step | Series or Book change | Association's standing | Recorded binding | Checks |
|---|---|---|---|---|
| start | none | `current_wording` at index 5 | version `7c34d34a…` | |
| B1 reorder | conversion question swapped with its neighbour | `moved`, now index 6 | unchanged | |
| B2 reword | wording changed to name the blind spot | `moved_and_reworded` | unchanged; recorded wording kept | |
| B3 preserve | targeted revision of an unrelated engine element | unchanged | unchanged | all other elements' digests unchanged: true |
| B4 retire | conversion question retired | `removed` | unchanged; recorded index 5 and text kept | the Compact question gained no association |
| B5 introduce | later Book revision adds an association to `agent-mill-compact` | the new association is `current_wording` at index 5 (the Compact question's position after the retirement) | bound to the current version | the retired association is still `removed` |

Reference to the mission's checks: the original binding stayed correct and readable through every step. Nothing silently moved to
a replacement question. Unrelated elements were preserved. A later revision could introduce a new association, bound to the current
version.

## Exercise C: creative reasoning (`reproduce/exercise_c.py`, `exercise-c/`)

Study material (disclosed): the conversion question was reworded to name the hand-light households, identity kept. The review
classified it as `reworded`. The consequence analysis examined it: the packet listed `q-conversion-settlement` as an examined question.

Evidence and selection: the question-linked class selected Book 24's blind-spot element (`E87`). Its row carries the question identity and
is marked as examined. The same wording in Book 25 (`E82`) has no association, and the answer records it as `unknown_inheritance`. The
packet is version 3 and holds 24 Book elements of 124 eligible, as before.

Fresh reasoning agent (sonnet): given the request file alone, with a neutral task. Its unedited answer was accepted by the owner
(`status: ready`, standing `current`). It has reach `conditional_inheritance`. It cites `E87` and classifies the link from a mechanism to `E87`
as `plausible_inheritance`, because an association is not a recorded inheritance. It classes `E82` as `unknown_inheritance`.

Independent critic (sonnet, read-only; packet and answer only, no expected conclusion; report kept at `independent-review/critic-report-exercise-c.md`).
Its findings, with my reading of each:

- Overreach, confirmed by the critic: the analysis asserts that "hand-light" and "those whose draw is cut" are the same households, and that
  "same households" is a defined group. Neither appears in the cited evidence. These are reasoning errors. The owner cannot catch them, and
  they are recorded here, not fixed by a validation rule.
- Overreach, confirmed: one trajectory step labelled `recorded` contains an interpretive clause. Two mechanism readings say more than their
  citations.
- Uncited claims: the comparison fields for the alternatives are not cited.
- Missed connection, confirmed by the owner: Book 25's blind-spot element (`E82`) also says "open question 6". The owner's positional
  observation shows that it resolves, at Book 25's recorded version, to the conversion question. That is a candidate association for a
  reviewed revision of Book 25. It is not recorded.
- A disagreement I record rather than resolve: the critic says the analysis understates `E87` by calling its link plausible. The
  association itself is recorded. The inheritance that would follow from it is not. The contract distinguishes these, and the analysis
  classifies the inheritance. The association is cited as the evidence for it.

Comparison with PR #647's analysis of the same proposal: PR #647's packet already held the blind-spot element (`E95`), and its answer
already cited it, as a plausible inheritance from a mechanism (`E44 → E95`). What changed is not the element's selection but the explicit
typed relation to the question, and the referent is now correct. The comparison is qualitative: one run per arm, and the answers use
different schemas.

## Served journey (`reproduce/served_journey.py`, `served-final/`, `journey` in `served-final/journey.json`)

Run on a disposable copy of the applied study, with the Mill Compact association pending for review. Every step uses the page's own
controls, and each question view is opened on a new page load, as the browser tests do.

1. The Mill Compact question, association pending: no engagement is shown (`01-…pending…png`).
2. The conversion question's engagement card leads to Book 24. The development panel's review reads "Question associations in this
   revision · 1", names the Compact association as "now engages", states the limit, and notes that the existing association is kept at its
   recorded version (`02-…review-before-apply…png`).
3. Apply, through the review's button: "Applied to working Book 24".
4. The Mill Compact question after Apply: "Book elements that engage it · 1", with the Book's own words, the association's standing, the
   element's authority and the limit line (`03-…after-apply-desktop…png`).
5. The same question at 390 px: no horizontal overflow, and the engagement is legible (`04-…narrow-390.png`).

No page errors. The server logged `WinError 10053` tracebacks, from client connections that the browser closed mid-request during the
existing Series-context read. They are logged by the request handler, not raised by the change, and no request returned an error.

The built-in browser pane was also used interactively for the same steps on the desktop viewport. Its screenshots were too small to archive,
so the archived evidence is the Playwright capture.

Automated served tests: `tests/test_beginner_studio_question_links_browser.py` (3 tests) covers the reading, the narrow screen and the pending
review.

## Independent code review and its dispositions

An independent read-only reviewer read the design, the full diff and the reproduce scripts (`independent-review/review-findings-before-fixes.md`).
It found no blocking defect and checked guarantees 1 to 10 on the paths it read. Its important and minor findings, and what was done:

1. Element associations with an unreadable or mismatched binding lost their question identity, so they fell into the unattributed bucket. Fixed: the
   identity is the reference's own and is kept on every element row. Test: `test_an_association_whose_recorded_binding_no_longer_matches_still_names_its_question`.
2. Review rows gave no standing and no authority. Fixed: each added or retained association carries its standing against the version the revision was
   checked on, and the element's own attribution, status and authority. The review names them before Apply. Test: the review assertions in
   `test_a_new_association_is_bound_to_the_identity_bearing_version_it_was_checked_on`.
3. The consequence share test could not fail. Fixed: a competitive case (30 inherited, 10 question-linked) now requires exactly six question-linked rows.
4. The share split (8, 6, 4, 6) was an implementation choice, not an explicit owner decision. The design header now says so, and the owner is asked to confirm it.
5. The design claimed a pinned legacy digest that no test checked. Fixed: the design now says what is tested (a stored record round-trips unchanged; an unbound
   reference serializes as before). Also added: a retained association refuses a changed binding (test), and an inherited claim whose only reference is a
   question has no basis (test).
6. The same question could be associated with one element twice. Fixed and refused. Test: `test_the_same_question_is_associated_with_one_element_once`.
7. The Book panel named the association without linking to its question. Fixed: a "Read this question" control opens the question reading.
8. Positional observations skipped typed-edge prose. Fixed; test: `test_positional_prose_in_a_typed_edge_is_observed_too`.

Exercise A, B, C and the served journey were regenerated after these fixes, from the same unedited agent outputs. The regenerated review rows carry the new
fields. Exercise C's request was rebuilt from the same packet, and the owner accepted the same unedited answer against it.

## Owner and boundary verification

Recorded in the PR body. The verified counts are for the tree at the reviewed head.

## Limits

- The owner checks identity, binding, placement and authority. It does not check whether an element is about a question. The critic's
  overreach findings are reasoning errors of this kind.
- The positional observation assumes the one-based numbering the Book's own prose uses. The other reading is shown beside it. The owner
  does not choose between them.
- The identities in the study were assigned by the test helper (`assign_identities`), not chosen and approved by an author. The
  association is therefore a disposable-study result, not an authored story decision.
- Exercise B's steps are owner-scripted study material, not a coding agent's reasoning. Exercise C's proposal is study material too. Only
  Exercise A's Book revision and Exercise C's answer were written by agents.
- A retained association cannot be re-bound in place. To re-attach a question, a later revision removes the reference and adds a new one.
- Deliberation and discovery are unchanged in this increment. Their Book evidence is still decision-only, so the question-linked
  evidence reaches the consequence analysis only. This is the one reasoning vertical the mission asked for.
- One Series version and one Book record are the only historical sources. No backfill of prose references was attempted.
- No human author has judged the wording, the reading or the served experience. Accessibility conformance was not tested.
- Sub-agents were sonnet, not the product's host agent. Each reasoning output is one run.
