# Consequence-aware narrative development: what a proposed revision preserves, transforms and may displace

Status: implemented on `feat/consequence-aware-development` from `main@37e71b3a` (PR #645). Builds on the
[persistent questions](2026-11-25-persistent-narrative-questions.md), the
[narrative deliberation](2026-11-26-narrative-deliberation.md) and the
[opportunity discovery](2026-11-26-narrative-opportunity-discovery.md). Opt-in Atelier. Advisory output only: a
consequence analysis changes no Architecture, Working Book, Series, or accepted record, and it never blocks Apply.

## A. Starting capability, and the gap the development exercise exposed

Verified against `origin/main@37e71b3a`:

- **Pending revisions are reviewed deterministically.** `complete_architecture` stores a review under
  `architecture/requests/<sha>/review.json`: the proposed candidate, the component comparison, the question changes
  (`question_changes`: `introduced`, `unchanged`, `moved`, `reworded`, `moved_and_reworded`, `removed`), the question
  scope of a comparison, and the author-declared emotion preservation. Apply writes the reviewed candidate as current.
- **A pending-review inquiry already exists in the owner.** `prepare_architecture_inquiry` with
  `target: pending_review` lets an agent examine the proposal with the applied baseline, under an author question. The
  served Atelier never calls it. Its context carries no question history and no Working Book decisions for the changed
  question, and its answer is free text: it has no concern statuses, no prospective items and no alternatives.
- **The question history and Book decisions are reachable only for applied, current questions.**
  `project_architecture_questions` and `build_question_deliberation` read applied versions. Neither knows a pending
  proposal, so neither can say which Book decisions refer to a question the proposal rewords.
- **The development exercise (PR #645) showed what is missing.** The rewording of `q-conversion-settlement` was
  reviewed, applied and traced, but the record could not tell the author that the earlier concern about settlement
  durability and the finale had left the question's wording, or that Book 24's decision about that question now refers to
  a question whose wording the revision changed.

What is already expressible through existing capabilities: the observable change, the identity continuity, the recorded
reason for each change, the Book decision texts and their standing, and transfer of an investigation into deliberation.
What is not: a reading, bound to the exact proposal, that says which earlier concern the proposal keeps, transforms or
may displace; which of those displacements the author's own instruction names; what the proposal may make possible for
later Books; and developable alternatives that the author can take forward through the existing workflow.

## B. Decision: a proposal-specific advisory analysis, reusing the owners

A new owner module, `studio_architecture_consequence.py`, holds an explicitly invoked, host-agent analysis of one
**exact pending review**. It follows the discovery lifecycle (request, response, result, stored beside the Architecture),
because an analysis is advisory and is never a revision lifecycle of its own.

| Need | Existing owner reused |
|---|---|
| The exact proposal and its baseline | `project_architecture` (pending review, applied baseline), `review.json` |
| Question wording and history | `project_architecture_questions`; `_history_for` and `_book_item` of the deliberation owner |
| Book decisions and whether they still read as recorded | `book_series_references`, `deliberation_standing` |
| Observable component changes | `build_architecture_review` output stored in the review |
| Instruction, selected alternative, discovery origin | the review's `requested_change`, `selected_creative_alternative`, `from_discovery` |
| Freshness and host-agent envelope | `_live`-style checks as in discovery; `build_host_agent_request`, `validate_host_agent_response` |
| Developing an alternative | `prepare_architecture_inquiry` with `from_consequence`, a new transfer key checked by this owner |

The analysis writes nothing into the Architecture, the review, the inquiry or a Working Book. Apply remains available
whatever the analysis says.

## C. Evidence packet: what the agent is shown, and what is only a fact

The packet is deterministic, bounded and counted. Every fact the agent may cite has an identifier (`E1`, `E2`, ...), and
each item says what kind of fact it is:

- `instruction` (the author's requested change), `selected_alternative` (the author's chosen inquiry alternative),
  `discovery_origin` (the possibility it came from), `author_vision` (the Story Vision, clipped), `accepted_constraint`
  and `accepted_not_this` (from the review's preserved record).
- For each examined question (every question the proposal changes or removes, and every question the instruction
  considered, at most four): `baseline_wording`, `proposed_wording` or `removed`, `recorded_history` (the same bounded
  items the deliberation packet gives, with their recorded reasons), and `book_decision` for each Working Book decision
  that refers to it (at most four, the rest counted). A `book_decision` states whether it touches the proposal: the
  question's wording or existence changes under the decision. That is a fact of identity, not a judgment of meaning.
- `proposed_component` for each changed node, link, phase, emotion target, complex emotion, genre contract or genre
  interaction (at most ten, the rest counted), with before and after summaries from the review.
- `recorded_phase` for the baseline's narrative phases (ten at most), and `working_book` for each readable Working Book
  title (twelve at most). These give a later Book's title and its phase, not its content.
- `named_gap` for each history gap, unreadable Working Book, or unreadable version. A gap is never filled in.

The request also carries the full baseline candidate and the full proposed candidate, so the agent examines the actual
proposal and not only the instruction.

A Working Book is listed as examined only when it records a decision about an examined question. A Book that records none
is named as read by title only. The packet and the view say so: a Book with no recorded decision is not thereby
"unaffected".

## D. Agent answer: a structured reading, not a verdict

The answer has five parts, all bounded and validated:

- `reading` (what the proposal accomplishes and what it changes, observed facts kept apart from interpretation).
- `concerns` (at most six). Each names a creative concern, its status, and the evidence it rests on:
  - `preserved`: the concern is still represented in the proposed wording or structure;
  - `transformed`: the concern is still in play but its formulation or function has changed;
  - `possibly_displaced`: the concern may no longer be represented, or may need separate consideration; the evidence
    does not establish whether this was intended;
  - `introduced`: a new uncertainty, tension or opportunity the proposal brings.
  A transformed or possibly displaced concern states its **intent basis**: `instruction_names_it` (must cite the
  instruction), `selected_alternative_names_it` (must cite the alternative), or `not_established`. Each concern may also
  give its counterevidence and a competing reading. A concern is never assigned a replacement identity.
- `prospective` (at most four). `recorded_relationship` items must cite a Book decision or a recorded history item:
  a relationship the record states. `proposed_possibility` items are the agent's suggestions for later development.
- `alternatives` (at most four). Each is one of six approaches, `replace`, `integrate`, `separate`, `retain`, `defer`
  or `reframe`, names two or three continuing questions of the current baseline, and states its gains and its costs.
  The prompt says every approach is legitimate, that integration is not presumed better, and that an alternative
  which is the agent's own recommendation must be justified against the others. An alternative is developed only
  through deliberation, on its own baseline questions. `separate` names the questions it keeps. The distinct question
  it would introduce is described in the summary and is not given an identity.
- `not_established` (what the record cannot establish), and `no_concern_reason` when `concerns` is empty.

Deterministic checks refuse an answer that cites an unknown evidence identifier, asserts an intent basis without citing
the instruction or the alternative, asserts a recorded relationship without a Book decision or history item, names a
question that is not a continuing baseline question, or repeats a title. The owner never judges whether two wordings mean
the same thing, and never reads a semantic result into a changed wording.

## E. Lifecycle and provenance

- **Subject.** Each analysis records the exact pending review (`review_request_sha256`), the digest of the proposed
  candidate, the baseline request it compares against, the source and design-guidance digests, the evidence digest, and
  an invocation nonce (so an identical request on an unchanged proposal is still a new ask).
- **Standing, read at each projection, never stored.** `current`: the examined proposal is still the pending review, the
  baseline is unchanged, and the review's own working context (sources, design guidance, creative intentions) is unchanged,
  which is the same predicate Apply uses. This analysis must also be the latest one asked for that proposal. `applied`:
  the examined revision has been applied, so the analysis is historical about an applied change. `superseded`: a different
  revision has replaced the proposal, or a later analysis of the same proposal has. `stale_context`: the working Architecture
  or the review's context changed under it. Only `current` is presented as about the proposal on screen; the others are
  labelled as such, and an earlier analysis is never shown as current.
- **Freshness at completion.** A response that arrives after the proposal, the baseline, the source or the design
  guidance changed is retained as stale evidence and refused, as in discovery.
- **Transfer.** `from_consequence` names the analysis and its alternative. The inquiry owner checks that the analysis
  completed, the alternative exists, its questions equal the inquiry's question anchors as a set, and each question is
  still a continuing question of the current baseline. An investigation never rebinds an alternative to replacement
  questions by wording. It starts only from a `current` analysis: an applied, superseded or stale analysis is read, not
  investigated from here. The inquiry result and the selected alternative carry the reference, but not a standing
  snapshot, since standing is never stored. The revision review names that origin; it never widens the question scope.
- **Decline.** The author may leave a pending proposal unapplied. Nothing is recorded for that, and nothing changes.

## F. Served journey

In the Studio review panel, beside the revision the author is reading:

1. "Ask about consequences" prepares the exact analysis request, which the author copies to their coding agent. The
   request names what it examines: the proposal, the baseline, the examined questions with their history and Book
   decisions, and the counts that were omitted.
2. The author pastes the agent's response, which is validated by the owner and stored.
3. The result reads as: the reading (labelled as interpretation); concerns grouped by status, each one's evidence
   disclosed; recorded Book relationships apart from possibilities; what the record does not establish; and alternatives
   with their gains and costs, each with "Investigate this alternative" (an inquiry on its own questions, through the
   existing deliberation).
4. Apply is never gated by the analysis, so a deliberately transformative revision is not blocked.

The analysis panel appears only with a pending review. A stale, applied or superseded analysis is labelled as such.

## G. Exercise plan (recorded in `docs/qualification-evidence/consequence-aware-narrative-development-20261126/`)

- **Exercise A (the motivating case).** Rebuild the PR #645 chain in a disposable study through the owners, using the
  recorded authentic answers: discovery, investigation of p3, the h2 alternative, the revised candidate. Stop before
  Apply, so the rewording is a pending proposal. Then two arms, each a fresh sub-agent, one run each, unedited:
  - *Arm 1, the existing capability*: the pending-review inquiry (`explain`, `target: pending_review`), under the question
    "What does this change accomplish, and what may it displace?", with no hint.
  - *Arm 2, consequence-aware*: the consequence analysis request, with no hint about the answer.
  The prompt names no expected conclusion. A recommendation to narrow the question is as legitimate as one to integrate.
- **Exercise B (a contrasting case, same specimen).** A deliberate removal: the author's instruction retires the
  conversion question as no longer part of the story. The same owner, the same analysis. This asks whether the analysis
  recognises a deliberate abandonment without treating it as a mistake. The case is operator-authored and is disclosed as
  such. It is not an independent narrative specimen; no second specimen was built.

## H. Limits this design does not remove

- The analysis reads the recorded question history, Book decisions and the candidate. It does not read Working Book
  prose, which the owners do not expose for this purpose. A later Book is judged by its title and recorded decisions only.
- No author judgment of the creative quality is recorded. The exercise results are one run per arm.
- Prospective reasoning is bounded to the recorded relationships of the examined questions and the phase titles. It does
  not predict a Series.
- Semantic identity is never established by the owner. A changed wording keeps its identity and stays for the author.

## I. Recorded outcomes

Details and the unedited results are in `docs/qualification-evidence/consequence-aware-narrative-development-20261126/EVALUATION.md`.

- **The motivating case reproduces.** The PR #645 proposal, rebuilt through the owners and stopped before Apply, is the same
  pending review: one reworded question, identity kept, origin p3.
- **Both arms found the central displacement.** The settlement concern may be displaced, the record does not show whether
  that was meant, and the reach question is new. The existing pending-review inquiry reasoned through recorded mechanisms
  that the consequence packet cannot cite. The consequence analysis adds the recorded Book 24 relationship, a stated intent
  basis for each concern, and alternatives that can be investigated.
- **Two defects were found and repaired during the exercise, and both are pinned by tests.** A removal's position shifts
  crowded the removed question out of the examined set; the owner now examines removals and rewordings first. The
  instruction omitted a citation rule the owner enforces; the rule is stated now.
- **Known gaps, not repaired here.** Recorded links and nodes cannot be cited as evidence. The approach names are not defined
  in the instruction. Both are the next build.
