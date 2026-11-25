# Persistent narrative questions and cross-Book decision continuity

Status: implemented on `feat/persistent-narrative-questions` from `main@acc78479`. Opt-in Atelier and ordinary
Studio compatibility preserved. Human-author acceptance remains unverified and is not a gate.

## A. Starting state, and the demonstrated limitation

- The working Architecture represents open questions as `open_questions: list[str]`.
- A Working Book author decision binds to one question by `series_question_index` and `series_question_sha256`
  (a digest of the wording at that position). The Book record also names the Series request it was written against
  (`series_request_sha256`).
- Consequence (Spring Ledger, Book 24, `dec-gate-table`): when the Architecture changed, the binding could only say
  "stale". Nothing identified which question the decision meant, so a reworded or reordered question could not be
  followed, and a binding could not be interpreted against the version it was written against.

## B. Responsibility and the chosen representation

Chosen: an optional, parallel `open_question_ids` on the candidate (schema v2), declared by the coding agent and
validated by the Architecture owner (`studio_architecture`) before a response is stored.

Why this owner: the Architecture owner already owns candidates, their revision chain, review and Apply. Identity
belongs with the question itself, so no second persistence owner is introduced.

Alternatives rejected:
- **Position only** (status quo): cannot survive reordering.
- **Wording as identity** (a digest of the text): a reworded question loses its identity, and identical wording
  merges distinct questions.
- **Inferring continuity from similarity:** forbidden by the brief; not implemented.
- **A side registry with its own persistence:** a competing owner. Rejected.
- **Making questions graph nodes:** not needed for inquiry; would add visual clutter.

## C. Identity, version, semantic continuity and authority

Kept distinct:
- **Identity** (`open_question_ids[i]`): the continuing problem. Declared by the agent, checked by the owner. Never
  taken from position or wording.
- **Version**: the exact `text` and `text_sha256` at one applied version (`request_sha256`). Read from the revision
  chain; historical versions are never rewritten.
- **Semantic continuity**: not decided by the code. A changed wording stays `reworded` in the review, with the
  earlier wording shown, for the author to judge. A stable identity does not prove equivalent meaning.
- **Authority**: an identity cannot settle a question. A question that disappears is `removed`, never answered.
  Apply remains the explicit author step. Identity declarations are reviewed like any other revision.

Owner rules enforced at completion (`question_identity_problems`):
- identities must be unique, well-formed and one per question;
- once identities exist they cannot be dropped;
- an identity already used by any earlier version cannot name a different question (no recycling);
- if an earlier version cannot be read, new identities are refused (their history cannot be ruled out).

## D. Historical compatibility

- Legacy candidates (no `open_question_ids`) remain readable and unchanged. Their questions have no identity.
- A later version may introduce identities. They begin at that version; no earlier history is claimed for them.
- Working Book decisions keep `series_question_index` and `series_question_sha256`. A decision's Series version is the
  Book record's `series_request_sha256`. Resolution reads that exact version's question at the recorded index and
  requires the digest to match; otherwise the reference is `binding_mismatch` or `version_unavailable`.
- A legacy decision (its version has no identities) reports `identity_not_established`: a wording reference, not
  continuity. It cannot ground a question-level inquiry until its Book is written against an identity-bearing version.
- Stored records are not rewritten. The only new stored key is `open_question_ids` on new candidates (null for legacy
  candidates) and `question_changes` on new review records. Existing request identities and fingerprints are unchanged.
- A new Working Book decision may carry `series_question_id`. When the Series version has identities, a decision
  naming the question must carry the matching id; a mismatch is refused by the Working Book owner.
- Each decision records the Series version its question binding was written against (`series_question_version`).
  The owner sets it; a response cannot. A revision that moves the Book onto a Series version (a holistic revision, or a
  targeted one of a current Book) checks every decision's index and wording against that version, and each decision
  takes it: this is how a legacy decision becomes identity-bearing. A partial revision of an out-of-date Book keeps the
  Book's older baseline for what it does not touch, so each decision keeps the version it already had. A new decision
  takes the version its revision was validated against. A decision stored before this field existed takes the Book's
  recorded baseline when it is next revised, the only version it could have been bound to. Before this correction a
  decision added by a partial revision resolved against the older baseline (a mixed-version Book could misattribute
  its question); a reproduction test records that defect.

## E. Cross-Book decision continuity

- Each decision's question reference is resolved per Book (`book_series_references` → `question_references`).
- States: `current_wording`, `moved`, `reworded`, `moved_and_reworded`, `removed`, `identity_not_established`,
  `version_unavailable`, `binding_mismatch`.
- A Book's own freshness status is unchanged by question changes. The Atelier reports reworded or moved questions
  as "may warrant reconsideration", and a removed question as "not an answer".
- Multiple Books reference the same identity through their own decisions; each keeps its own version and wording.

## F. Question-grounded inquiry

- The graph-intent contract gains an anchor kind `question`, validated against `open_question_ids`. It is not a node.
- Book-originated inquiry: a decision grounds an inquiry on its question only while the question is anchorable
  (`current_wording`, `moved`, `reworded`, `moved_and_reworded`). `removed` and legacy references cannot anchor.
- The agent's observations may cite a question; they are resolved by the same owner resolver.
- The inquiry remains advisory. Nothing in it changes the question, the decision or the Architecture.

## G. Revision review

- Each version records `question_changes`: per question `introduced`, `unchanged`, `moved`, `reworded`,
  `moved_and_reworded`, `no_identity`, and `removed` items with earlier wording. A question-only revision is
  reviewable even when no node changes. The revision view shows these changes beside the node changes.

## H. Not implemented (explicit limitations)

- **Atelier ask action on a question** is implemented: a decision whose question is anchorable offers "Ask about this
  question", which opens the desk on the question with the Book element as evidence. It is verified by a served browser
  test and by the probe on the Spring Ledger study. It has not been judged by a human author.
- **Rebinding an existing Book decision to a new Series version** is not a flow. The owner keeps each decision's
  recorded binding (the revision rules fix it). An author who wants a decision to name a reworded or moved question
  writes a new decision against the current version; the earlier one stays as it was recorded.
- **Split and merge lineage** is represented as removal plus introduction, as the brief allows. No general lineage
  engine was built.
- **Semantic equivalence** is not judged by the system. It is left to the author through review.
- **Architecture question list in the working context** is not yet a separate panel; questions appear in the revision
  review, in each Book's decision list and in the Atelier's per-Book impact lines.
- **Revision history for a question** is available through the owner's history reader (`question_history`) and the
  revision chain. It has no dedicated Atelier view yet.

## I. Verification

- `tests/test_studio_architecture_questions.py`: the pure identity rules (reordering, rewording, replacement, removal,
  duplicate wording, retired identities, legacy introduction, unreadable history, relation to current).
- `tests/test_persistent_narrative_questions.py`: the Spring Ledger journey through the real owners. Legacy reading,
  introduction, reordering with rewording (question-only), removal, rejected identity recycling, history, advisory
  inquiry, unknown anchors refused, legacy decisions refused as question grounds, Book-originated grounding after
  identities are established, reopening in a fresh process, and stale inquiries refused.
- The existing Architecture, Working Book, inquiry and host-agent contract suites are re-run for compatibility.
