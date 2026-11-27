# Narrative reference stewardship and integrated deliberation: exercise evidence (2026-11-27)

Design: [`../../design/2026-11-27-narrative-reference-stewardship.md`](../../design/2026-11-27-narrative-reference-stewardship.md).
Every exercise runs in a disposable copy of the Spring Ledger study. Each Book or Architecture change goes through its owner, and
nothing edits a persisted record directly. No provider is called.

Three kinds of material are kept apart, and each is labelled where it appears:

- **Fresh agent output.** A general-purpose sub-agent on the sonnet model, given only its request file (and, for Exercise A, the
  Book's current record) and a neutral task. Its output is kept unedited and passed through the owner. Where an owner refused an
  output, the refusal is kept as evidence.
- **Owner-scripted study material.** Setup that the study needs and that no agent wrote: the identities an Architecture revision
  gives its questions, and Book 25's whole-Book reconciliation with the Architecture. Disclosed where used.
- **Replayed interaction.** The served journey's steps are driven by Playwright on the page's own controls. They are not agent
  reasoning, and the Book 25 answer they complete is the Exercise A agent output.

## Summary

| Exercise | What ran | Outcome |
|---|---|---|
| Setup and referent | PR #648's applied Book 24 association replayed from its unedited answer; identities; Book 25 reconciled | Book 25's blind-spot prose reads at its origin version (2c26a7c5, written at its first version); index 5 is the conversion question |
| A, Book 25 | Served control prepared a request; a fresh agent answered it; the owner reviewed and applied it | Association recorded at the blind spot. The agent changed only that element. Question reading lists Books 24 and 25 |
| B, cross-Book deliberation | Conversion vs Compact questions, neutral author text, production inquiry owner | The records establish no relation between the questions. Books 24 and 25 engage the question through one element with identical text. Compact has no element engagement |
| C, opportunity discovery | Production discovery owner, no goal | Four possibilities. One cites the conversion element as evidence alongside mechanisms. Taken into deliberation, the proposal is tested and found to overstate its join |
| D, focused critique | Independent read-only critic on the B and C answers; a critic-assisted revision of the C answer | The critic's quotations all check out. Its findings are mostly accepted. The revision is recorded separately and is not a first attempt |
| Served journey | 11 steps on the page's controls; 4 served tests, including a no-change path and 390 px | All passed; screenshots and a step record are kept |

## Setup: the referent, checked against the owner's records

- Book 25's blind-spot element says "open question 6". Read at the version its prose was written against (its develop version
  2c26a7c5, which has no identities), position 6 is index 5: the conversion settlement question. Position 7 is the Compact question.
- Book 24's record and its prose agree with that reading. The Book-wide version for Book 25 is the same version, so the reading is
  the same under either rule here. The origin rule matters where a later revision rewrites the prose (covered by the owner tests).
- The study's identities are assigned by the study's helper, not chosen by an author, as in PR #648. The association is therefore a
  study result, not an authored story decision.

## Exercise A: Book 25 reference stewardship

Stages (`reproduce/exercise_a.py`, run in order into `reproduce/exercise-a/`):

1. `seed`: the discovery study, identities, PR #648's Book 24 association replayed (`candidate-book24-unedited.json` from PR #648),
   and Book 25 brought up to date by a whole-Book revision that stops citing the concept the Architecture removed (owner-scripted
   study setup; it adds no association). `seed-summary.json`.
2. `prepare`: the request the served control sends for the conversion question, by identity, on the blind-spot element.
   `observation-book25.json` is the observation the author sees. `request-book25.json` is the request the fresh agent reads.
3. A fresh sonnet agent read only `request-book25.json` and `book25-current-record.json`, and wrote the complete Book object to
   `candidate-book25-unedited.json`. It changed one element, `cons-conversion-blind-spot`. It added the reference to
   `q-conversion-settlement` and restated the element's legacy provenance in the explicit form, as the owner requires. Its one-line
   reason: the element's prose calls the blind spot concrete for open question 6.
4. `complete`: the owner accepted the answer as applicable, with one changed element and one association added. The review says the
   requested association was recorded, and gives the question's wording (`review-book25.json`).
5. `apply`: applied (`apply-result-book25.json`). The question reading lists Book 24 and Book 25 engaging the conversion question
   (`question-reading-after-apply.json`). Book 25's lead is gone. Book prose in the two engine elements still names the question by
   position: those remain leads, which is correct, since no association is recorded for them.

The request sha (`4b1694e3…`) is stable across regenerations, and the served journey test checks the served page prepares exactly
that request. A change to the packet would fail the test rather than let an answer written for another request pass.

## Exercise B: cross-Book deliberation

Request: `exercise-b/request-B.json`, built by the production inquiry owner for a comparison of the conversion question and the
Compact question, with neutral author text. Its packet: `packet-B.json`. The owner's standing for the evidence at completion:
`standing-B.json`.

The packet's facts, before any agent reasoned about them:

- The conversion question has two engagements: the blind-spot element in Book 24 and in Book 25, each with its own status
  (unattributed, unresolved, commitment undecided).
- The Compact question has no engagements, and one decision in Book 25.
- One recorded co-reference: Book 25's decisions about both questions. The packet says it is a recorded reference, not a relation.
- Six positional names are untied: their versions recorded no identity. The packet counts them as a named gap.

The agent's answer (`answer-B-unedited.json`, accepted by the owner): it found no recorded relation between the questions, since
`between.status` is `no_recorded_relation`. It noted that the two Books show the same element with the same text, so the records do
not show different dimensions developed. It kept three labelled hypotheses. It named the untied positional names and did not
resolve them. It stated that whether the two questions are one problem is the author's decision.

What the records support, against the critic's check (below): the no-relation finding, the identical element in two Books, and the
untied names. What the agent asserted beyond them is labelled interpretation, and the critic found one "only" claim it could not
support (see Exercise D).

## Exercise C: opportunity discovery

Request: `exercise-c/request-C.json`, built by the production discovery owner with no author goal. Packet: `packet-C.json`, which
carries the conversion question's two element engagements alongside its decisions.

The fresh agent's answer (`answer-C-unedited.json`, accepted by the owner) gave four possibilities:

1. The cistern's storage limit may decide whether the Long Return can be routed (grounded in recorded nodes and links; interpretation
   labelled).
2. Hours recorded in the ledger could expose the conversion's blind spot (grounded, with the element as one of four evidence items).
3. A reading that activates Alternative C would be the Old Hand engine acting on the spring (grounded).
4. Testing Hesper's motive by placing her where authorial preference cannot choose (speculative, labelled as imaginative).

**Taking possibility 2 into deliberation.** This was done through the existing workflow, with its three questions as anchors.
Three runs were needed, and each is kept:

- Run 1 (`answer-C-possibility-deliberation-REFUSED-analysis-over-5000-chars.json`): refused by the owner, because the analysis was
  over 5000 characters. The inquiry prompt did not state that limit, although the owner enforces it. This was an instruction defect.
  The prompt now states the limits, and the owner's tests still pass.
- Run 2 (`answer-C-possibility-deliberation-title-only-unedited.json`): accepted. The agent reported that the packet carried only the
  possibility's title and hashes, so it could test only the title's three claims. This was an evidence-packet defect: the discovery
  origin carried no account of the possibility. The origin now carries the discovery agent's own account and cited evidence, labelled
  as its noncanonical proposal.
- Run 3 (`answer-C-possibility-deliberation-unedited.json`, accepted): the agent tested the proposal's join. It found the cited
  elements exist and say what the proposal says. It found that nothing records hours bearing on the blind spot, that the proposal's
  gain depends on an unrecorded assumption, and that "grounded" overstates the join. It separated recorded from interpreted claims and
  kept four labelled hypotheses. This is the outcome the mission asked for: the possibility was investigated, and the investigation
  found it under-supported rather than developing it.

No possibility was accepted, applied or promoted. Discovery's grounded label was left as the discovery agent stated it; the
investigation's disagreement is recorded beside it.

## Exercise D: focused critique and a critic-assisted revision

**The critic.** A read-only sonnet critic read the B and C requests and answers, and checked each consequential claim against the
packets. It classified findings as confirmed error, unsupported, plausible but uncertain, legitimate speculation, alternative
reading, or unresolved disagreement (`exercise-d/critic-report-D.md`). The critic was not told the expected conclusion.

**Checking the critic.** Every phrase the critic quoted was found in the packet it cited: "clause of B or C", "Partial readings of the
script", "responds to balance rather than to any character's intention", "open question 5", "Oona's offer", and "Alternatives B and C
depend on it". The critic did not fabricate evidence. Its findings are weighed below, not taken on its word.

**Findings on the deliberation answer (B).** The critic found no confirmed error. It found one unsupported "only" (the thread
`th_hands_and_draw` as the sole link between the questions, where the packet records other paths through the ledger and the
Compact's maintenance thread), and an alternative reading the answer did not use (the finale alternatives both questions touch).
These are minor and are noted as limits of the B answer.

**Findings on the discovery answer (C).** The critic found one confirmed error: the coverage note said the Compact settlement has no
recorded mechanism tying it to other questions, and the packet's finale-clause text ("the Compact's settlement is a clause of B or C")
is one. It found the cistern possibility's counterevidence did not mention the unaccepted construction addition its core node is. It
found possibility 2's "links ... through one recorded mechanism" unsupported, and possibility 3's "Old Hand engine" equation
unsupported (nothing records a threshold reading as an Old Hand reading), and that the answer ignored the recorded Book 12 partial
reading. Possibility 4 was correctly labelled speculative.

**The revision.** A fresh reasoning agent, which is the discovery agent again, was given the request, its original answer and the
critic's report. It accepted most findings, narrowed one, and rejected one partly. It wrote a separate file,
`answer-C-critic-assisted-corrected.json`. The revision validates against the discovery answer model and the reference check, but it
was not sent to the owner, because it is a demonstration and not a new stored answer. The differences: possibility 2 is now
speculative; possibility 3 is replaced by a speculative question about whether a Balance Stones threshold reading would behave like
the earlier readings; possibility 1 keeps its grounded label and gains the Hollow Gate counterevidence; the uncertainties are longer.

This revision is critic-assisted. It is not an independent first-attempt result, and it is not used as one anywhere in this record.

**What the critic did and did not do well.** It caught a confirmed error the answer's own packet contradicted, and several
overreaches. It did not catch the answer's strongest weakness, which the title-only investigation found: that possibility 2 rested
on evidence the packet did not carry. That defect was found by the investigation's agent in its own run, and then fixed upstream. The
critic's value here is in checking claims against a packet it could read whole. It was less useful for a join that the packet did not
state.

## Served journey

Two sets of evidence, which test different things.

- `reproduce/served_journey.py` (run into a fresh study; the screenshots and step record are in `served-final/`): 11 steps, all passed.
  The steps are the question's lead; Book 25's observation with the owner's choices; the prepare request, which matches the request the
  evidence answers; the owner's review of the unedited answer as applicable with the requested association recorded; the served Apply
  recording the association; the question reading listing Books 24 and 25; Book 25's lead gone; no horizontal overflow at 390 px;
  and no page errors.
- `tests/test_beginner_studio_reference_stewardship_browser.py` (4 served tests): reading the question writes nothing; the adoption
  journey (with the owner's binding checked at the write); the narrow screen; and the no-change path (a lead opened and left alone
  changes nothing on disk).

Screenshots (`served-final/`): `01-question-lead.png` (three leads: two engines and one consequence, all labelled as leads),
`02-observation-desktop.png` (Book 25's development panel with the observation and choices), `03-review-before-apply.png` (the
requested association in the review, before Apply), `04-question-after-apply.png` (the question reading with Books 24 and 25),
`05-question-narrow-390.png` (the 390 px width).

Not tested: human author judgement of wording or of the reading; screen-reader and keyboard conformance; any non-desktop browser.

## Compatibility, measured

The pre-#648 owner module (`git show 77c5848a^1:src/auteur/series/working_book_architecture.py`) read the same Book records:

- Legacy record: read by both the pre-#648 and the current code.
- Record with an applied `series_question` reference: refused by the pre-#648 code (`ValidationError`), read by the current code.

The design doc (section K) states the rollback boundary this implies. Pending requests keep the new setting in a dictionary the
request model does not validate, so the boundary is the first applied association, not the code revert.

## Defects found during the exercises, and what was done

- **Instruction defect.** The inquiry prompt did not state the owner's length limits. Run 1 was refused for that. The prompt now states
  them, and the refused output is kept.
- **Evidence-packet defect.** A discovered possibility, taken into deliberation, carried only its title and hashes. The investigation
  could test only the title. The origin now carries the discovery's own account and cited evidence, labelled as its noncanonical
  proposal. Run 2's answer is kept.
- **Lead placement.** A lead for a question still showed after its association was applied, and the question's Book view did not reach
  the observation. Both fixed; the served tests cover them.
- **Element standing wording.** An element association's "current" standing used the decision's wording. A separate element wording
  now applies, and a Node test checks it.
- **Test assumptions.** Three existing assertions were tightened: one PR #648 assertion named an element in two Books, which now
  correctly matches two cards; a served fixture used the wrong folder; and a served test used an off-by-one Book number. All are fixed.

## Verification

- Owner and consumer suites: the stewardship file (13 tests), the engagement file (10), the existing question-reference file (17),
  and the related owner, deliberation, discovery, consequence and Book suites, about 380 tests in all, with no failures.
- Node suites for the touched Atelier modules: 57 tests passed, and 3 new engagement-evidence tests passed.
- Served suites (Playwright, system Python with the browsers installed): the 4 new served tests, the question-links, deliberation,
  discovery, question, question-workspace, consequence, Book and architecture-interactive suites, all passing.
- Exit codes and summaries were read from each run. The project venv does not have Playwright, so served tests ran under the system
  Python 3.14 with the package on `PYTHONPATH`.

## Independent review of commit bcac8345

A read-only sonnet reviewer read the committed diff of the owner, the adapter, the deliberation, discovery and projection modules, the
Atelier modules, the new tests and the design (`independent-review/review-commit-bcac8345.md`). It found no blocking defect, and it
found two important ones. Each finding was checked in the code before any change. Dispositions:

- **F1 (important): an incomplete origin was still tied to a question.** When an earlier version could not be read, the reading still
  resolved at a later version, and leads and the deliberation packet tied the name by identity. Fixed: such a name gets the state
  `origin_not_established` (no proposal, choices offered), is not a lead, and is counted as untied in deliberation. Test:
  `test_an_origin_that_cannot_be_established_is_neither_proposed_nor_tied_to_a_question`.
- **F2 (important): deliberation standing rows have a new shape.** Nothing in the tree broke, because the fixtures have no element
  associations, but two tests indexed rows by `decision_id`. The tests now filter rows by kind. The row change is additive.
- **M1 (duplicate keys and ids).** Keys are now suffixed only when one Book element has a second card, so the first keeps its plain
  key. The served tests' selectors are unchanged.
- **M2 (silent fallback for the current request).** The fallback is now marked, and its origin is not established.
- **M3 (choice lost on re-render).** The chosen question is kept until the request is prepared.
- **M4 (held question offered again).** Questions the element already records are removed from the choices.
- **M5 (dependents' associations unflagged).** The review lists `unrequested_question_associations`, and the Atelier names them before
  Apply. The test asserts the list is empty when nothing extra was added. No test covers a non-empty list; the reviewer's scenario
  is not reproduced here.
- **M6 (out-of-date Book).** The reviewer read the owner's partial-on-stale path as available to the served control. It is not: the
  adapter prepares against the current Architecture only, so an out-of-date Book takes a whole-Book request. The code comment was right.
  The card now says so.
- **M7 (wording leads by coincidence).** Accepted as labelled leads. Not changed.
- **Test strength.** The read-basis assertion accepted either outcome; it now requires `element_origin`.

After these changes: the owner, consumer and Node suites pass, the served suites pass, and the served journey was regenerated from the
final code (11 steps, all passed).

## Limits

- One specimen, one author study, identities assigned by a helper. This is an existence and mechanism result, not evidence of general
  reasoning quality. No "additional specimen" was built.
- Each agent output is one run. Exercise B and C agent outputs were not repeated. The Exercise D revision is one run.
- The owner checks identity, binding, placement, scope and authority. It does not check that an element is about a question. The
  critic's findings are the only semantic check in this record.
- No human author has judged the wording or the reading, and no accessibility conformance was tested.
- Sensemaking skills were not invoked for this work. This is a deviation from the mission's optional use, recorded here.
