# Narrative question workspace: historical continuity and contextual inquiry

Status: implemented on `feat/narrative-question-workspace` from `main@cf5c0b5c`. Opt-in Atelier; the ordinary Studio
keeps its behaviour, with one added review line for question changes. Builds on
[persistent narrative questions](2026-11-25-persistent-narrative-questions.md) (PRs #641, #642). Human-author acceptance
is not claimed; the served journey is replayed with recorded coding-agent answers (see Verification).

## A. What existed, and what authors could not do

Verified against source at `cf5c0b5c`:

- The Architecture owner kept every applied revision and could read a question's history (`question_history`,
  `architecture_versions`). **Nothing called `question_history`.** No projection or view used it.
- A Working Book decision could be asked about from its own Book, through "Ask about this question". The Book's
  "Open questions these decisions refer to" list was the only place a question was shown.
- The Studio's reader counted open questions and listed them as uncertainties. No atlas, concept or review surface
  listed them as individual items with their identity and history. The review showed question changes only inside a
  collapsed "Compare visually (experimental)" disclosure.

An author therefore could not start from an unresolved question, read how it had been recorded, see every Book that
recorded a decision about it, and reconsider it, unless they first found a Book decision.

## B. Selected experience

Three surfaces, all inside the Living Narrative Atelier, none a new page:

1. **The overview entry.** The atlas folio gains an "Open questions" section beneath the Working Books summary: up to
   five questions, each with a quiet mark only where it differs from the default (a wording without identity, a change,
   an incomplete history, a Book decision count). "All open questions" opens the list. A concept's folio carries one
   quiet "Open questions" control that opens the same list without moving the atlas or changing the focused concept.
2. **The list.** Three groups: continuing (identity recorded), wording only (no identity yet), and no longer open. Back
   returns to the concept or the atlas the author came from.
3. **The question reading.** A folio view, not a new panel. Order: the question's current wording and its standing;
   how it has been recorded; the Working Books that record a decision about it; investigation with the coding agent;
   source details behind a disclosure. Back returns to the list, or to the Series and Book context, when that is where
   the reading began.

The atlas is not changed. Nothing is drawn on it, no question is a graph node, and no badge appears on the canvas.

Navigation is a short stack, not a route: a question opened from a Book returns to that Book's context; a Book opened
from a question returns to the question; a concept selection leaves the reading; Escape closes one level at a time.

## C. Historical continuity

The projection (`studio_architecture_question_projection.project_architecture_questions`) reads through the owners and
stores nothing.

- **Spans.** Consecutive versions with one recorded state form a span. Each span lists every version it covers. An
  unchanged run is one span, so repeated revisions do not read as events; each underlying version stays reachable from
  the span's disclosure.
- **States.** `present` (index and wording), `absent` (the revision is readable and does not name the identity),
  `no_identity` (a legacy revision that names no identities), `unreadable` (the revision cannot be read).
- **Changes** are judged only against the span before it that was actually read. An unreadable version breaks the
  comparison: the change across it is `unverified`, never claimed. "Introduced" is claimed only when the chain is
  complete and the identity first appears after a readable revision with no identities, or at the first revision.
- **Gaps** are named in `history.gaps`: `chain_incomplete`, `unreadable_before_first_recorded`, `unreadable_within`.
  A gap is shown in words beside the question. Nothing is omitted to make the history look whole.
- **Revision numbers** are given only when the whole chain is read (`current.numbered`). Otherwise a version is named
  by its digest, and no number is invented.
- **Reasons.** For a span that begins with a change, the reason is what that revision's own request records: the
  author's revision instruction, and the inquiry alternative the author chose, if any. When neither is recorded the
  view says so. No reason is inferred from wording.
- **Removal.** A question absent from a readable current version is `no_longer_open`, with its last recorded wording.
  The copy says removing it is not an answer.
- **Wording only.** A question in the current revision with no identity is shown as wording, with no earlier history
  attached. It cannot be asked about as a continuing question until a revision names it.

## D. Cross-Book perspective

Each Working Book's references come from the Working Book owner (`book_series_references`, now including each decision's
text). A decision is attached to a question **only** by its recorded identity (`question_id`), which the owner has
already validated against that Book's version.

- Relationship states are the owner's own (`current_wording`, `moved`, `reworded`, `moved_and_reworded`, `removed`,
  `version_unavailable`, `binding_mismatch`). A reworded or moved question is said to "may warrant reconsideration",
  and the Book is said not to be declared inconsistent. A removed question is said not to be an answer.
- A decision that names no identity itself is attached to the identity its named version carries at the decision's
  position, when that version's wording at that position matches the decision's recorded digest. This is the owner's
  own resolution, the one the existing Ask path already relies on, and it is not a match on wording. The Book's source
  details say the decision records no identity, so the author can see the join is the owner's, not the Book's.
- A decision bound to wording without an identity is counted for the Books as a whole and is **not** joined to any
  question. Similar wording, position or title never joins them.
- A Book that cannot be read is named in the question's Books list. It is never silently treated as unaffected.
- Each Book row keeps its own decision text, the earlier formulation it refers to (when different), and a disclosure
  with the recorded identity, the recorded version and the decision id.

"This Book records a decision connected to this question" is the only relationship asserted. Whether the question
causally affects the Book's story is not asserted anywhere.

## E. Investigation, alternatives, review and Apply

Investigation reuses the existing coding-agent desk and the existing inquiry owner. No operation is added on the
server. A question anchor (`kind: question`, the persistent identity) is the same anchor the Book-originated inquiry
already uses, with no Book evidence attached.

- Three operations are offered from the reading: **explore alternative formulations**, **challenge this formulation**
  and **explain what it asks**. Each opens the desk with a suggested sentence in an empty field. The suggestion is never
  sent. The browser label for an open question's operations now uses question words (`studio_architecture_graph_actions.js`).
- Asking prepares a request and changes nothing. Its answer is advisory.
- Choosing an alternative requires the author's own words about what to develop from it (the desk's existing rule).
  That is a revision request, which the owner prepares; the coding agent answers; the owner reviews it.
- The review lists each question change before Apply: introduced, moved, reworded, moved and reworded, removed. It shows
  the earlier wording. This line is new in the main review list (`studio.js`), so it is visible without opening the
  visual comparison.
- Apply is the existing explicit action. A declined alternative leaves the Architecture, the question and every Book as
  they were, and the test asserts this on disk.
- Afterwards, the desk closes and the question is read again with its updated history, including the recorded reason.

## F. Integrity corrections from #642 that this surface depends on

- A cited question that was reworded or moved still allows the Book to be revised; the reading says the Book may warrant
  reconsideration. The projection maps every state the owner returns; `unattributed` covers the states that carry no
  identity, so none is dropped.
- A recorded identity is never changed by a revision, so the reading never shows an identity moving between questions.
- Legacy decisions keep their dump shape, so they appear as wording references, not as identity-bearing ones.
- The projection is read-only. A test asserts that reading leaves every stored file unchanged, and that a legacy
  Architecture gains no identity by being read.

## G. Limits, stated plainly

- No semantic equivalence is judged. A reworded question is "reworded, identity kept", and the author judges the rest.
- A question's history is shown per question. There is no cross-question timeline and no question graph.
- Legacy wording gains an identity only when a later revision names it, through the Architecture owner.
- The history reader reports gaps; it cannot recover an unreadable version.
- The review lists the question changes of the one revision being reviewed. A question's full history is read from its
  own reading, not from the review.
- No human author has judged the experience. The served journey uses replayed coding-agent answers, and no new
  creative reasoning was run during verification.

## H. Verification

- `tests/test_architecture_question_projection.py`: owner-level states on the Spring Ledger study, including the
  rewording with its recorded reason, one span for unchanged revisions, removal, wording only, an unreadable version
  as a named gap, an incomplete chain with withheld revision numbers, Books attached by identity, and read-only reads.
- `tests/test_beginner_studio_question_workspace_browser.py`: served Atelier journeys in Chromium. Discovery and
  reading; Book navigation and return; a narrow screen without horizontal overflow; wording-only and removed states;
  the full investigate → alternative → revision → review → Apply → return path; and the declined path.
- `tests/test_studio_atelier_questions.mjs` (run through `tests/test_studio_atelier_questions_node.py`): the words the
  helpers produce for each state, so the statements stay within what the owner records.
- Existing Atelier, Architecture, inquiry, review and Working Book suites are re-run as the named-boundary slice.
