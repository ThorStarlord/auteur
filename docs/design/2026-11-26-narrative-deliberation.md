# Narrative deliberation: evidence-grounded cross-question inquiry

Status: implemented on `feat/narrative-deliberation` from `main@3bb63109`. Builds on the
[persistent narrative questions](2026-11-25-persistent-narrative-questions.md) (#641, #642) and the
[narrative question workspace](2026-11-25-narrative-question-workspace.md) (#643). Opt-in Atelier. Human-author
acceptance is not claimed.

## A. Starting capability, and what prevented cross-question reasoning

Verified against `origin/main@3bb63109`:

- **Anchors already allow several questions.** `GraphIntent.anchors` accepts one to three typed anchors, and a
  `question` anchor is a persistent identity (`studio_architecture_graph_intent.py`). `compare` needs at least two
  anchors and `connect_to_ask` exactly two. `explore`, `explain` and `challenge` accept any count the intent allows.
  The desk's graph selection appends up to three anchors (`studio_architecture_graph_selection.js`, `select(anchor,
  {append:true})`), and the agent bridge checks the same limit.
- **The inquiry owner already prepares and completes them.** `prepare_architecture_inquiry` resolves each anchor
  against the current candidate (`recordedSupport`, `sourceRef`) and sends the whole working Architecture, the
  author's text, same-baseline prior exchanges and at most one Working Book element. `complete_architecture_inquiry`
  validates the response and retains it. Nothing here needs a new operation.
- **What prevented it.** (1) The Atelier's question reading sends one anchor only (`askArchitectureQuestion`), so
  the author cannot start a comparison from questions. (2) The packet contains **no history**: no earlier
  formulation, no recorded change, no revision reason, no earlier selected alternative and no Book decision for a
  question. The coding agent sees only today's strings. (3) A Book decision reaches an inquiry only as one element,
  and only through the Book's own element (`book_evidence`), which admits one anchorable question at most.

Conclusion: the contracts support multi-question inquiry. The missing construction is the evidence packet for
several questions, the entry point that selects them, and the presentation that keeps evidence and interpretation
apart.

## B. Selected architecture: reuse first

| Responsibility | Owner (existing) | Change |
|---|---|---|
| Anchor identity and limits | `studio_architecture_graph_intent` | none |
| Operations | `compare`, `connect_to_ask`, `explore`, `challenge`, `explain` | none; no new operation |
| History reading | `studio_architecture_question_projection.project_architecture_questions` (read-only) | none; the deliberation packet is built from its output |
| Book references | `working_book_architecture.book_series_references` | none |
| Inquiry prepare/complete | `studio_architecture_inquiry` | attaches a `deliberation` packet when two or three question anchors are given; records its digest |
| Revision from an alternative | `studio_architecture.prepare_architecture` / `complete_architecture` / `apply_architecture_review` | records which questions the inquiry concerned, and which of them the revision changed |
| Develop over an existing Architecture | `studio_architecture` | **defect fixed** (section E) |
| Entry and comparison | `studio_atelier.js` | a comparison tray of up to three questions |
| Desk | `studio.js`, `studio_architecture_creative_panel.js` | multi-anchor hand-off; evidence disclosure in the answer |

New code is limited to one owner module (`studio_architecture_deliberation.py`) that assembles the bounded,
labelled packet from existing owner reads, plus the wiring above. No new store, no relationship database, no graph
mode, no automatic settlement.

## C. Historical grounding: what is supplied and how it is selected

For each selected question (two or three, the anchor limit):

- **Current formulation**: index, wording, `text_sha256`, identity, and the anchor's `sourceRef`.
- **Formulation history**: the first recorded span, the two most recent spans, and a count of omitted spans. Each
  span names its applied request, its version digests and any recorded change label. Spans beyond the window are
  counted, not inlined. Reason and chosen alternative appear only where that revision's own request records them.
- **Recorded reasons**: the author's revision instruction for a changed span, and the alternative the author chose
  in the desk, marked as an agent interpretation the author selected.
- **Working Book decisions**: at most four per question, by Book number. Each carries the decision text, the Book's
  request digest and the decision's text digest, the recorded version the decision names, and its state
  (`current_wording`, `moved`, `reworded`, `moved_and_reworded`, `removed`, `version_unavailable`,
  `binding_mismatch`, `identity_not_established`).
- **Named gaps**: `chain_incomplete`, `unreadable_before_first_recorded`, `unreadable_within`, unreadable Books.
- **Recorded co-reference**: for each Book that references two or more selected questions, one fact saying it
  references them. This is a recorded reference, not a relationship in the story.

Bounds are fixed constants in the owner module and are part of the packet (`limits`), so the agent is told what was
omitted. Texts are truncated with the digest of the full text retained.

Every item carries `basis` and `authority` (section D). The whole packet is frozen into the request's user payload,
and its digest is stored in the request settings and the saved result. A later revision of the Architecture or a
Book does not rewrite the packet of an earlier inquiry.

## D. Epistemic categories: how the packet keeps them apart

Each item names exactly one basis:

| Basis | Authority label | Meaning |
|---|---|---|
| `current_wording` | `working_noncanonical` | The current working Architecture's question text |
| `recorded_wording` | `historical_recorded` | An earlier formulation, as one applied version recorded it |
| `recorded_change` | `historical_recorded` | A change in recorded wording, judged against the readable previous span only |
| `recorded_reason` | `author_instruction_recorded` | The author's revision instruction for that revision; not proof the consequence was achieved |
| `recorded_selected_alternative` | `historical_agent_interpretation_selected_by_author` | An alternative the agent proposed and the author chose; its text is an interpretation |
| `book_decision` | `working_book_proposal_noncanonical` | A Working Book decision; `identity_basis` says how it reached the question |
| `recorded_co_reference` | `recorded_reference` | Two or more selected questions named by one Book |
| `named_gap` | `unverified` | A history or Book reading that is missing or unreadable |

Freshly generated interpretation has no basis in the packet. The agent's answer uses the labels in its
`recorded_observations` and `hypotheses`, and its prompt tells it to keep three things apart: what is recorded,
what it interprets, and what remains the author's decision. An explicit "no meaningful connection" answer is a
legitimate outcome and is stated as such.

## E. Concern A: developing over an existing Architecture

**Question.** Can an accessible owner workflow overwrite or bypass the revision history that question continuity
depends on?

**Finding (confirmed, not refuted).** The Studio's "Develop architecture with coding agent" button is always
rendered (`studio.html`) and sends an empty instruction (`studio.js`, `requestArchitecture("")`). When an
Architecture already exists, `prepare_architecture` accepts it and `complete_architecture` writes `current.json`
directly. That record has no `prior_request_sha256` and no `review.json`. `architecture_revision_chain` then
reads the new version as a first version (empty instruction), so it reports `complete: True` with one version. The
earlier history is no longer reachable, and the question projection reports the history as whole.

Reproduced on the Spring Ledger study (probe in the scratchpad): after a removal retired `q-other-0`, a develop
over the existing Architecture made the chain report one complete version; a later revision then introduced
`q-other-0` for a different question, and the identity check accepted it. Retaining the identity was the rule the
owner exists to keep.

**Authorized or accidental?** Regenerating an Architecture from the same author's sources is a legitimate
workflow (the stale-source copy in `studio.js` says "Regenerate or revise"). Losing the lineage is not authorized by
anything. The fix preserves regeneration and keeps the lineage.

**Fix.**

- `prepare_architecture`: a develop over an existing Architecture records `prior_request_sha256` in the request
  settings (a new key; no other request shape changes).
- `complete_architecture`: such a completion is refused as stale unless the prior version is still current, and it
  writes `requests/<sha>/lineage.json` naming the prior version.
- `architecture_revision_chain`: a version with no review reads `lineage.json` for its prior link. A version with
  neither remains the first version, as before.

**Residual, stated plainly.** A develop over an existing Architecture made before this fix has no lineage record and
still reads as a first version. Nothing in the record distinguishes it from a true first version, so the chain
cannot be repaired from the record alone. The projection will keep reporting such a canvas's history as complete
from that point. This is a record-level limit; no migration is attempted (owner-reserved: destructive or irreversible
migration).

## F. Concern B: decision identity association

A Book decision reaches a question in two ways, and the packet keeps them apart:

- `identity_basis: recorded_by_decision`: the decision names the question's identity itself
  (`decision_records_identity: true`).
- `identity_basis: resolved_by_owner_from_recorded_version`: the decision names no identity; the Working Book owner
  resolved it from the version it names and the digest it recorded. The owner's resolution is the Book owner's, not
  the author's assertion.

A decision whose recorded wording has no identity is counted, not attached. Similar wording never joins a decision to a
question. The agent is told the basis of each Book item; its answer must not describe an owner-resolved link as an
author statement.

## G. Freshness and currency

- **Current Architecture.** The existing baseline check (`_live_matches`) applies unchanged. A changed baseline
  makes the inquiry stale, and its response is retained as stale.
- **Historical records.** Versions and recorded reasons are immutable records. They do not become stale because the
  narrative moved on. The packet is frozen at preparation.
- **Book decisions.** At completion (not live) the packet's Book decisions are read again and saved as `deliberation_standing`. Each is reported as `current` (same
  decision digest and Book request digest), `book_revised` (the Book changed but the decision is unchanged) or
  `decision_changed` or `unreadable`. The result is retained as ready, and `deliberation_standing` names every
  changed decision, so the answer reads as written against the decision as it stood. This is a bounded extension of
  the single-element `book_evidence` rule: a changed decision annotates the answer rather than discarding it, because
  the historical reading remains true.

## H. Revision scope

A revision made from an alternative of a multi-question inquiry records `considered_questions` (the questions the
inquiry concerned, with their wording at that time) and `changed_questions` (those the revision changed, from the
existing `question_changes` judgement). The review states the scope in one line: "This inquiry concerned three
questions. This revision changes one." A revision never changes questions it was not asked about; the owner does not
expand scope. A change to a question the inquiry did not concern is named in a second line
(`changed_outside_ids`), never folded into the first.

## I. Interaction

- **Entry.** A question reading and the question list carry a comparison tray. "Add to comparison" adds the current
  question (up to three). "Investigate together" opens the desk with every selected question as an anchor.
- **Operations offered.** Compare, explore a possible relationship (only with exactly two), challenge, and explore
  alternatives. Each offers a suggested sentence drawn from the mission's illustrative intentions. A suggestion fills
  an empty field only and is never sent.
- **Return.** The comparison tray survives navigation. Closing the desk returns the author to the question or list
  they came from, with the tray intact.
- **Evidence.** The answer shows an "Evidence this answer was given" disclosure, grouped by basis, with each item's
  label. The answer's own text is shown separately.
- **Narrow screens.** The tray and disclosures follow the existing Atelier responsive rules; no horizontal overflow.

## J. Non-goals (stated so they are not mistaken for omissions)

- No relationship database, graph mode, timeline visualization or semantic-equivalence judgment.
- No new inquiry operation and no change to the response contract. Relation kinds (complementary, tension, shared
  mechanism and so on) are expressed in the existing hypotheses and observations, and the guidance names them. If a
  consequential reasoning requirement cannot be expressed this way, the exercise's evaluation records it as a limit.
- No automatic cross-question revision, no automatic settlement, no automatic cross-Book reconciliation.
- Single-question inquiries keep their existing packet. The history packet attaches only to two or three question
  anchors, so the baseline and the deliberation can be compared on the same owner.
- Proactive discovery of connections is not part of this responsibility.

## K. Verification (as run on this branch)

- Owner: `tests/test_architecture_deliberation.py` (packet bounds, bases, identity basis, co-reference, gaps, freeze
  across later revisions, Book standing at completion, read-only reads, baseline without history) and
  `tests/test_architecture_develop_lineage.py` (concern A: the probe's sequence is refused; a first develop still
  reads complete with one version; a develop over an existing Architecture keeps the chain).
- Node: helpers for the comparison tray and suggestions.
- Served Chromium: select two questions, investigate together, replayed coding-agent answer, alternative, revision
  with an explicit instruction, review scope line, Apply, return to the comparison, and a declined path that leaves
  every record byte-identical.
- Exercise A/B: fresh sub-agents with the same creative question, model and budget. A receives the current-state
  packet; B receives the historically grounded packet. Recorded in `docs/qualification-evidence/narrative-deliberation-20261126/`.

## L. Recorded outcomes

- **Concern A.** Reproduced on the Spring Ledger study before the fix (develop over an existing Architecture
  reported a complete one-version chain, and a retired identity was accepted). Fixed by lineage. Tests:
  `tests/test_architecture_develop_lineage.py`.
- **Instruction defect (found by the exercise).** Both fresh coding agents wrote `source_kind` and `source_id` because
  the inquiry instruction said "source kind, id". The owner rejected both answers. Corrected to name the exact keys, and
  pinned by a test. The rejected attempt is kept under `docs/qualification-evidence/narrative-deliberation-20261126/
  attempt-1-instruction-defect/`.
- **Exercise.** One cross-question inquiry on three Ledger questions, baseline against historically grounded.
  Recorded and evaluated in `docs/qualification-evidence/narrative-deliberation-20261126/EVALUATION.md`. One run per arm.
- **Independent read-only reviews.** Two reviewers (owner authority and browser interaction) found items that were
  checked against the code. Fixed: review scope hid changes outside the inquiry; `unverified` versions were labelled as
  gaps; history could read out of order; an unaskable question could be added to a comparison; focus fell to the folio
  title after removal; a part-made selection survived a failed hand-off; the standing docstring said "now". Refuted: the
  explore instruction omitted the divergence values (it lists them). Kept as defensive: the stale-develop guard, which
  no ordinary path reaches.

