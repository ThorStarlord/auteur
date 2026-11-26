# Narrative opportunity discovery: evidence-grounded creative possibility discovery

Status: implemented on `feat/narrative-opportunity-discovery` from `main@e42061cd` (PR #644). Builds on the
[persistent questions](2026-11-25-persistent-narrative-questions.md), the
[question workspace](2026-11-25-narrative-question-workspace.md) and the
[narrative deliberation](2026-11-26-narrative-deliberation.md). Opt-in Atelier. Advisory output only: nothing is
accepted, settled, adopted or applied by discovery.

## A. What existed, and what prevented agent-directed discovery

Verified against `origin/main@e42061cd`:

- **Incidental opportunities already exist.** `ArchitectureCandidate.opportunities` holds at most three
  `ArchitectureOpportunity` records. The architecture prompt asks the agent to note at most one or two while doing
  requested work, and to omit them when nothing consequential appears. An author can deepen one through
  `selected_opportunity` (a develop-style revision). This is a recorded part of the working Architecture, reviewed when
  the Architecture is revised.
- **Deliberation exists, but starts from the author.** Narrative deliberation takes two or three question anchors the
  author has already chosen. Nothing selects questions for the author.
- **What prevented agent-directed discovery.** No request asks the agent to survey the whole working Architecture and
  its question history for possibilities worth investigating. The existing incidental opportunities are a by-product
  of other work and are capped at three; they cannot serve as a deliberate survey.

## B. Decision: discovery is advisory, and does not write into the Architecture

A discovered possibility is **not** added to `candidate.opportunities`. Reasons:

1. Candidate opportunities are part of the working Architecture. Writing discovery results there would modify the
   Architecture without the review and Apply the author already controls, and would create a second opportunity
   system inside it.
2. Candidate opportunities carry no question identities and no evidence references. The discovery needs both.

Instead, discovery is a separate, explicitly invoked host-agent request and result, stored like an inquiry under
`architecture/discoveries/`. It reads the candidate's recorded opportunities as evidence (`candidate_opportunity`
references). A possibility whose title duplicates one is flagged, not refused.

Discovery reuses the existing mechanisms rather than new ones:

| Need | Existing mechanism reused |
|---|---|
| The narrative material | the working Architecture as the inquiry already reads it (`_candidate`, `_source`, design guidance) |
| Question history and Book decisions | `project_architecture_questions` (read-only) |
| Freshness of the baseline | the inquiry's `_live_matches`-style check, with a stale response retained |
| Investigation | `prepare_architecture_inquiry`, with two or three question anchors |
| Historical packet at investigation | `build_question_deliberation` (bounded, labelled, frozen) |
| Alternative, revision, review, Apply | `prepare_architecture` with `selected_alternative`, `apply_architecture_review` |

The only new owner module is `studio_architecture_discovery.py`: the request, the validation of an agent's proposals,
the lifecycle projection, and the transfer check.

## C. Discovery process: stages, and where each runs

- **Stage A, orientation (in the request).** The full working Architecture (bounded by the candidate's own schema
  limits), every continuing question with its current wording, its number of readable recorded formulations, its last
  recorded change and that change's recorded reason (clipped), and up to two of its Book decision texts (clipped), with
  the rest counted. No-longer-open questions are listed as historical and not anchorable. The author may give an
  optional goal or area of concern.
- **Stage B, identification (the agent's answer).** The agent selects up to four possibilities. Each names two or three
  continuing questions, evidence references, whether it is grounded in a recorded mechanism or speculative, its
  assumptions and counterevidence, and a next investigation. An empty answer must say why no possibility is worthwhile.
- **Stage C, focused recovery (at investigation, not in discovery).** When the author takes a possibility forward, the
  existing deliberation packet recovers the bounded history of exactly that possibility's questions, with their Book
  decisions and reasons. Discovery does not do a second agent round. A second round would be a general retrieval
  protocol, which is out of scope.
- **Stage D, creative assessment.** The existing deliberation answer refines, challenges or discards the possibility.

Stage C therefore uses the existing packet at the point of use. Its bounds and omissions are already reported.

## D. Evidence selection, bounds and provenance

- Bounds are fixed in the owner module and reported in the request (`limits`), including omitted counts.
- Each evidence item in the request has a `source` basis from the deliberation legend (`current_wording`,
  `recorded_change`, `recorded_reason`, `book_decision`, `named_gap`) or a recorded-structure label
  (`recorded_architecture`, `candidate_opportunity`).
- The packet is frozen into the request. Its digest is kept in the settings and in the result.
- Completion checks the live baseline. A changed baseline retains the response as stale. A completed result is never
  invalidated merely because the narrative moved on.

## E. Possibility validation: what an answer must carry

Validation is deterministic and refuses an answer that breaks any of these rules:

- at most four possibilities; an empty answer must carry `no_possibility_reason`;
- each possibility names exactly two or three question identities, all continuing in the current request, and no
  wording is used for matching;
- every evidence reference resolves inside the request: a node, link, genre interaction, question, Book decision
  (book number and decision id) or candidate opportunity;
- a `grounded` possibility cites at least one recorded mechanism (node, link or genre interaction). Shared Book
  references and question wording alone never ground a possibility;
- a `speculative` possibility is labelled as such and cites what it is imaginative about;
- titles are unique within an answer; text is bounded.

Kind labels are optional reasoning aids: thematic_resonance, shared_mechanism, productive_tension,
overlooked_consequence, narrative_inheritance, productive_independence and consolidation. They are not required in
every answer.

## F. Lifecycle: historical discovery and current suitability

A discovery result is a historical record and stays readable. Each possibility's transferability is judged when it is
read, never stored:

- `transferable`: its questions are continuing and their wording is what the discovery packet recorded.
- `reworded`: its questions are continuing but reworded since the discovery. It remains transferable and says it was
  formulated against an earlier wording.
- `not_transferable`: a named question is no longer open. It is never rebound to a replacement question.

Evidence references record whether each item is still present in the current Architecture (`present_now`). A
discovery made against an earlier baseline is labelled as such. It is not invalid because newer material exists.

## G. Author control and the transfer

- The author invokes discovery explicitly. Nothing runs in the background.
- Each possibility can be investigated, declined, or left unselected. Declining writes a decision record in the
  discovery folder (with an optional reason). It changes no Architecture and no Book.
- **Transfer.** Investigating a possibility prepares a deliberation inquiry with the possibility's questions as
  anchors and a `from_discovery` reference (request, possibility id). The owner checks: the discovery is completed, the
  possibility exists, the inquiry's question anchors equal the possibility's questions as a set, and the possibility
  is transferable or reworded. The inquiry result records the reference and the possibility's digest.
- The author's sentence for the investigation is the possibility's next investigation as a suggestion in an empty
  field. It is never sent without the author's action.
- The alternative a deliberation produces, and the revision made from it, carry the discovery reference, so the review
  can say which possibility a revision came from. Revision scope is still the inquiry's questions; the owner never
  widens it.

## H. Epistemic integrity

- Discovery output is labelled as agent interpretation. A grounded possibility is grounded in recorded mechanisms; it is
  not established fact.
- A shared Book reference is never presented as a relationship in the story.
- A reason recorded for a revision says what was asked, not what was achieved.
- Identity is never inferred from wording. The lineage limitation from PR #644 is unchanged: developments made before
  that correction still read as first versions, and nothing here reconstructs them.
- No possibility is accepted, settled or applied by discovery. The no-change outcome is always available: no possibility
  at all, or every possibility declined.

## I. Served experience

- The entry is the existing "Open questions" section of the atlas folio ("Look for opportunities"). It opens a folio
  view. It is not a new dashboard and not a graph mode.
- The view has an optional goal, a prepared request to copy to the author's coding agent, a response field, and a result
  list. Each possibility shows its title, kind, the possibility, its significance, the questions it concerns with their
  current wording, and a status chip. Evidence, uncertainty, assumptions, counterevidence and the next investigation sit
  behind disclosures.
- Investigating a possibility places its questions in the comparison tray and opens the desk with the possibility's
  next investigation as the suggested sentence. From there the existing deliberation, alternative, revision, review and
  Apply path applies unchanged.

## J. Verification

- Owner tests: validation (bounds, references, grounding, speculative labelling, empty answers, duplicate titles),
  lifecycle (transferable, reworded, not transferable, no rebinding), freshness (stale retention, historical results
  kept), transfer checks, decision records, no-change path, and read-only projections.
- Served Chromium: the discovery journey end to end (invoke, review, inspect, investigate, alternative, revision,
  review, Apply, return), the no-change path, and the narrow screen.
- Exercises: one authentic discovery run by a fresh sub-agent with the actual request and no hints about the answer, plus
  a small arm comparison between compact current-state evidence and the full compact orientation. One possibility is
  developed through deliberation, a revision and Apply on a disposable study. Outputs are recorded unedited under
  `docs/qualification-evidence/narrative-opportunity-discovery-20261126/`.

## K. Recorded outcomes

- **Instruction defect (first exercise attempt).** Both arms' answers exceeded length limits that the instruction did not
  state. The owner refused the baseline answer. The limits are now named once, generated into the instruction, and
  enforced by the model; a test pins the instruction to the model. The rejected attempt is kept under
  `docs/qualification-evidence/narrative-opportunity-discovery-20261126/attempt-1-instruction-bounds/`.
- **Re-invocation.** An identical discovery request on an unchanged Architecture resolved to the already-completed record,
  so no pending request appeared. Each explicit invocation now carries a unique invocation identifier in its settings;
  the evidence digest is unchanged.
- **Name collision (found in browser testing).** The Atelier already had `openDiscovery`, `closeDiscovery` and
  `renderDiscovery` for the earlier Book-discovery feature. The later declarations silently shadowed the new ones. The new
  functions are renamed with the `Opportunit` prefix; no existing call site changed.
- **Independent reviews.** The owner review found an unreadable request folder that would hide every discovery on a
  canvas (fixed: named as unreadable), a window of the newest fifty discoveries that could misreport an older one (fixed:
  the named discovery is read directly), non-dict origins that raised internal errors (fixed), and an unchecked decision
  type (fixed). Refuted: that an answer could inject a discovery origin (the inquiry result model forbids extra keys), and
  that duplicate anchors could pass (the graph intent rejects them). The interaction review found that a concept click left
  the discovery view open (fixed), that Decline and Reopen changed the focused control's key (fixed: one shared decision
  key), that errors were not announced (fixed), that investigating a possibility silently replaced the comparison tray
  (now announced), that a question no longer open was described as still in the Architecture (fixed in the owner), and
  that the goal and response fields lost their caret on redraw (fixed).
- **Exercise, discovery.** One run per arm, the corrected instruction, the current-state baseline against the full
  orientation. Two of four possibilities converged across arms; the grounded arm alone found an open consequence (the
  Book 20 conversion and purchased draw) and cited Book decisions. Recorded in `narrative-opportunity-discovery-20261126/EVALUATION.md`.
- **Exercise, development.** The purchased-draw possibility was carried through investigation, an alternative, a reviewed
  revision of one question (identity kept, scope honest), and Apply in a disposable study. The rewording narrowed the
  question's framing, which the author should weigh in review. Recorded in `development/DEVELOPMENT.md`.
