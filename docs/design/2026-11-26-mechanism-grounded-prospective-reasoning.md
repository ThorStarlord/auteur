# Mechanism-grounded prospective narrative reasoning (design)

Status: implemented on `feat/mechanism-grounded-prospective-reasoning`. The evidence record (`docs/qualification-evidence/mechanism-grounded-prospective-reasoning-20261126/`) states what was run and what was refused. This document states the contract as built.

Consequence analysis remains advisory, explicit, noncanonical and never gates Apply. This design adds a second answer contract, `studio-revision-consequence/2`, to the consequence analysis of a pending working revision (see [`2026-11-26-consequence-aware-narrative-development.md`](2026-11-26-consequence-aware-narrative-development.md)). Version 1 analyses stay readable and keep their stored meaning.

## 1. Starting capability and the gap

The consequence packet gave the agent the baseline and proposed candidates in full, the examined questions with their recorded history and Working Book decisions, the author's instruction and a bounded set of Working Book titles. Its evidence vocabulary could not cite a recorded node, link, interaction or phase. The motivating case showed the cost. In the Spring Ledger proposal the single change is a question rewording: `changed_components` is empty. A selection that started from changed records would return nothing, while the mechanisms the case turns on (`l_conversion_sets_draw`, `l_trade_draws_without_return`, `l_compact_hands_in_kind`) are unchanged. The inquiry arm reached them through the recorded relations around anchors. The consequence arm could not cite them.

Existing owners reused:

| Need | Existing owner |
| --- | --- |
| typed anchors and source references | `studio_architecture_graph_intent.resolve_anchors`, `_recorded_relations` (one-hop recorded links, genre interactions and reference memberships) |
| deterministic record diff and recorded rendering | `studio_architecture_review._COMPONENT_FIELDS`, `_title`, `_summary` |
| Working Book references to Architecture nodes, with standing | `series.working_book_architecture.book_series_references` |
| Working Book elements with typed `series_refs`, collection and attribution | `series.working_book_architecture.book_elements` |
| applied revision chain for historically recorded records | `studio_architecture.architecture_versions` |
| question history and Book decisions on each examined question | `studio_architecture_deliberation` (`_history_for`, `_book_item`, `deliberation_standing`) |

Seeded Spring Ledger facts (`scripts/consequence_exercise.py seed`, applied revision 3):

- Book 24 references 20 Architecture nodes, including `inst_mill_compact` and `th_hands_and_draw`. Book 25 references 20, including `eng_ledger` (changed against the current record) and `inst_gate_table` (no longer in the Architecture).
- Book 24's `open_author_decisions` elements cite no node. The nodes come from the Book's other elements.
- Book 24's `inherited`, `later_possibilities` and `series_consequences` elements cite nodes in typed `series_refs`. Book 24's `cons-conversion-blind-spot` says the blind spot "makes open question 6 concrete", where question 6 is the Compact question by position. Books refer to questions by position as well as by identity; that is recorded text, not a typed link.

No recorded path from an examined question to a node exists in the owners. Relevance must come from recorded Book references and one-hop recorded relations, never from lexical similarity to the question wording.

## 2. Mechanism evidence (version-qualified)

The packet v2 adds one evidence kind, `mechanism`, for each record in the **mechanism inventory**. Records are the owner's typed collections (`nodes`, `links`, `phases`, `emotion_targets`, `complex_emotions`, `genre_contracts`, `genre_interactions`). Provenance is an identity fact, computed by comparing each record with its identifier on the applied baseline, on the proposal and in earlier applied versions:

| Provenance | Meaning | Source |
| --- | --- | --- |
| `preserved` | same identifier, identical record, on baseline and proposal | diff |
| `transformed` | same identifier, the recorded content differs; `changed_fields` names what differs | diff |
| `removed` | on the baseline, absent from the proposal | diff |
| `introduced` | absent from the baseline, on the proposal | diff |
| `historical` | on neither side, but recorded in an earlier applied version (newest first, bounded to 6 versions) | `architecture_versions` |

A mechanism's identifier does not establish that its function is unchanged. A `preserved` record is one whose recorded content is identical. What it means in relation to a reworded question is the agent's interpretation, labelled as such.

Each mechanism evidence item carries `record_kind`, `record_id`, `provenance`, `changed_fields`, `routes`, `book_references`, `endpoints`, and the text and digest for the side it is on:

- `baseline_text`, `baseline_sha256` for a record on the applied baseline;
- `proposed_text`, `proposed_sha256` for a record on the proposal;
- `historical_text`, `historical_sha256` and `version_request_sha256` for a historical record. Such a record is on neither side. Its text and digest come from the earlier applied version it names. The stored request holds only the baseline and the proposal, so a historical item is checked against the applied revision chain, not against the stored request.

`endpoints` are the node identifiers a record involves: a node is its own endpoint, a link or interaction has two.

Inferred or hypothetical mechanisms are not records and are never inventory items. They appear only as conditional consequences, trajectory steps or proposed inheritance, each labelled.

### Selection (bounded recovery)

Seeds, in order:

1. records the proposal changes (`transformed`, `removed`, `introduced`);
2. nodes referenced by any readable Working Book (`book_series_references`), annotated with those Books;
3. records of earlier applied versions (`historical`).

Expansion is one hop only: each link or genre interaction with a seed endpoint, the route naming every seed endpoint (`adjacent_to:<a>,<b>`). Nodes are never expanded from an expansion.

The inventory is capped at `MAX_MECHANISMS` (80). Overflow is counted in `limits` and never listed. When the cap applies, seed order decides, so an unchanged node a Working Book cites outranks an adjacent link. On the Spring Ledger proposal the inventory has 55 records (all `preserved` or `historical`), so nothing is omitted.

Routes explain membership; they are not ranks. Relevance is judged by the agent. The packet's job is to make unchanged but consequential records citable and to say why each is present.

## 3. Inheritance evidence

The packet adds `book_element` evidence: elements of readable Working Books whose typed `series_refs` cite a seed node. The owner's collection and attribution are carried unchanged. Bounded to `MAX_BOOK_ELEMENTS` (24) in three reserved classes:

- the Book's own `inherited` declarations: 10;
- forward-looking records `later_possibilities` and `series_consequences`: 10;
- the rest: 4.

Within a class, elements are taken round by round, one Book at a time, in the Book's order, so one Book cannot crowd another out. A class that does not use its share passes the rest on in class order. Each element notes whether its Book records a decision on an examined question.

On the Spring Ledger proposal this gives 24 of 124 eligible elements; the other 100 are counted in `limits`. The reserved share for inherited declarations is what keeps Book 24's `inh-uneven-draw` (its record of hand-light draw falling since the Book 20 conversion) in the packet. A selection ordered by forward records alone left it out.

A Working Book listed by title is `working_book` evidence. Title evidence never supports a recorded or plausible inheritance.

## 4. Answer contract v2

v1 keys are unchanged. v2 adds, and tightens:

- `reach`, required: `local`, `conditional_inheritance`, `long_horizon` or `not_established`.
  - `local` allows no `long_horizon` step, no `inheritance` step, and no inheritance other than `unknown_inheritance`.
  - `conditional_inheritance` needs an inheritance other than `unknown_inheritance`.
  - `long_horizon` needs a `long_horizon` or `inheritance` step.
  - `not_established` allows no `recorded_inheritance`.
- `mechanisms` (0-6): `evidence` (a mechanism item, read once), `reading` (what the record does; interpretation), `transformation` (required for `transformed`, `removed` and `introduced`; optional for `preserved`), `conditional_consequence` (labelled "if ..."), `counterevidence` (0-3 objects, each with `text` and 1-3 evidence identifiers that are recorded material other than this mechanism itself), `unresolved` (0-3 strings).
- `inheritance` (0-6): `kind`, `from` (an earlier-side item), `to` (a later-side item), `text`, `evidence` (0-4).
  - `recorded_inheritance`: `to` is a `book_element` in collection `inherited`; `from` is a mechanism; the element cites a node that `from` involves (the mechanism's endpoints). Without that citation the claim is at most plausible.
  - `plausible_inheritance`: `to` is a `book_element` or `book_decision`.
  - `proposed_inheritance` and `unknown_inheritance`: `to` may be a `working_book` title, and they are stored as proposal or unknown.
  - A Working Book title never supports a recorded or plausible claim.
- `trajectories` (0-3): `title`, `steps` (2-5: `stage`, `text`, `evidence` 0-3, `basis`), optional `assumptions` and `comparison`. A step with `basis: recorded` must cite a recorded item: a baseline wording, recorded history, a Book decision or element, a recorded phase, or a preserved, removed or historical mechanism. A proposal item, an instruction or a title alone is never recorded. Every trajectory is stored with status `hypothetical`.
- `alternatives[]`: `approach` (section 5), `questions` (1-3 continuing baseline questions), `keeps` (1-3 items), `mechanisms` (0-4 mechanism items to examine), `gains`, `costs`, `next_investigation`. The alternative's `keeps` must cover every named question with wording of that question, and nothing else: baseline wording for every approach except `accept_proposal`, which keeps proposal-side wording only. An alternative may name only questions whose wording the packet gives.

Evidence rules from v1 are kept and extended. Mechanism items count as earlier-side when `preserved`, `transformed`, `removed` or `historical`, and as proposed-side when `transformed`, `introduced` or `removed`. Book elements and titles count as neither.

## 5. Approach vocabulary

The v1 names were undefined in the instruction, and `retain` was used both for keeping the baseline concern and for accepting a retirement. v2 offers seven approaches, defined once in the owner's table and read by the instruction and the served page:

| Approach | Meaning | `keeps` |
| --- | --- | --- |
| `keep_baseline` | keep the earlier concern as recorded; the proposal's change to it is not adopted | baseline wording of each named question |
| `accept_proposal` | accept the proposal as written, including any displacement it causes; the displacement is recorded as accepted, not resolved | proposal-side wording of each named question |
| `replace` | put a different formulation in place of the earlier concern; a new question is described, not given an identity | baseline wording |
| `integrate` | hold two or three named concerns in one development; the summary says what the combined development gives up | baseline wording of each named question |
| `separate` | split a concern into parts developed independently; the parts keep the named questions | baseline wording |
| `defer` | postpone reconsideration; name what would settle it; the named questions keep their current wording | baseline wording |
| `reframe` | restate the creative problem at another level, keeping the named questions' identities | baseline wording |

`retain` is not offered in v2. v1 analyses keep their stored `retain` values, and the served page labels them as having no fixed meaning. No historical approach is reinterpreted.

## 6. Served experience

- The consequence panel shows: a `reach` line; mechanisms (each a single summary line with provenance, opened for the recorded text, observed change, reading, transformation, conditional consequence, counterevidence and unresolved points); inheritance (kind chip, from, to, reading); trajectories (a `Hypothetical` badge on each, steps labelled by basis).
- Each alternative shows its approach with the owner's definition, what it keeps, and the mechanisms to examine.
- A proposed future never uses accepted-fact wording, and conditional text is labelled.
- An evidence line for a Book decision says "question in proposal: reworded", because the status describes the question under the proposal, not the decision's own record.
- Investigating an alternative remains an explicit author action. It uses `compare` for two or more questions and `explain` for one. It carries the alternative's `keeps` and `mechanisms` provenance into the inquiry as `from_consequence` context. It does not widen the revision's authorized scope, and it runs no provider.

## 7. Invariants preserved

- Advisory and noncanonical. No Architecture, Working Book, review or accepted record changes. The owner writes only under the analysis's own folder.
- Apply is never gated. The shared Apply and consequence-context predicate (`review_context_changed`) is unchanged.
- Standing is read at projection: `current`, `applied`, `superseded`, `stale_context`. Only the latest current analysis can be investigated, as in PR #646.
- Exact-source binding. Baseline and proposed items resolve against the candidates the stored request holds in full. Historical items resolve against the applied revision chain, as section 2 states.
- A valid citation is not literary correctness. The owner checks that a cited item exists, has the kind and side the claim needs, and supports the basis stated. It does not check that the agent's account of the item is accurate. Recorded relations are not causal laws, and each mechanism reading is labelled.

## 8. Verification

- L1 focused, Python: `tests/test_architecture_consequence.py` (owner contract, including the version 2 refusal table) and `tests/test_architecture_consequence_mechanisms.py` (provenance, selection, class shares, recorded-inheritance citation, historical fields, the Spring Ledger packet, transformation refusal and acceptance, investigation carry-through).
- L1 node: `tests/test_studio_architecture_consequence.mjs` (labels and the evidence line).
- One named integration boundary, a served journey: `tests/test_beginner_studio_consequence_browser.py`. The served page renders the new answer fields and the investigation carries the alternative's provenance, so the boundary is named.
- Regression: the nearby inquiry, review and deliberation suites (`test_beginner_studio_architecture_inquiry.py`, `test_beginner_studio_inquiry_pending_review.py`, `test_beginner_studio_architecture_review.py`, `test_architecture_deliberation.py`, `test_architecture_discovery.py`, `test_architecture_question_projection.py`, `test_beginner_studio_architecture_provenance.py`, `test_beginner_studio_architecture_apply_cli.py`, `test_studio_architecture_questions.py`).

## 9. Exercises and the correction loop

Exercise A reuses the pending proposal recorded for PR #645 (a rewording of the Book 20 conversion question, with no component change). It is replayed from the recorded chain, then examined under the final contract. Exercise B is a contrasting case, not a second narrative: the repository holds no second specimen with a working Architecture, Working Books and a pending proposal of comparable completeness. Exercise B's proposal changes one recorded relation (the Mill Compact's labour duty) and no question, so it exercises the `transformed` path that Exercise A does not.

Sub-agents writing the answers receive only their request file, with no hint about the expected conclusion. Each answer is passed through the owner unedited. When the owner refuses an answer, the refusal is archived, and the same agent receives the owner's exact refusal message and writes a corrected answer. Both the refused and the corrected answers are kept. The refusal and correction protocol is the one the owner's own design intends: a refused answer is stored as evidence and never as the analysis.

Exercise A's first analysis was accepted under a rule that let a proposal item count as a recorded basis, and a counterevidence item could cite the mechanism it limited. The owner was tightened after the critic review in section 10 (below). The first analyses are kept under `contract-1-accepted-under-earlier-rule/`, and the final analyses are re-run under the final contract.

## 10. Review

Two independent read-only reviews ran on the first version of the owner and the analyses:

- an implementation review found six consequential gaps: recorded inheritance not tied to the element's own citations; alternatives whose keeps could mix proposal and baseline wording and need not cover every named question; reach that did not constrain inheritance; a class share that starved the classes behind it; historical records carrying a baseline digest they do not have; and counterevidence that could cite its own mechanism. Each is fixed and tested. The counterevidence rule checks only that the cited material is other than the mechanism itself. Whether it limits the reading is not checked.
- a semantic critic, given the stored analyses without the expected conclusion, found that a trajectory step could claim a recorded basis while citing a proposal item, and that a Book decision's proposal status was easy to misread. Both are fixed. The critic also found that one analysis missed the Book 24 reference to the Compact question by position, and that a second analysis read a Book as title-only when its decisions were read. Those are reasoning errors and are not fixed by the owner.

## 11. Recommended next responsibility (not implemented here)

Recorded Book text refers to questions by position as well as by identity. Position is fragile once questions move. A next responsibility could make such references typed, so that a Book's cross-question reference survives a reordering and can be checked by the owner rather than read from prose. The present design can cite a recorded link only where a Book element already records it.
