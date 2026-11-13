# Working Book revision, withdrawal and apply: Book 24 craft-mark counterfactual

**Date:** 2026-11-12. **Baseline:** `origin/main` at `fe06f2c4` (PR #559 merged). **Branch:** `feat/book-working-revision`.
**Authority:** Book 24 is the noncanonical cold-start experiment (PR #555, commit `fa85b7f1`) used as a creative fixture. The Series input is the W6 working candidate, not an accepted architecture. Nothing here is accepted canon, and the counterfactual is a hypothetical working revision.

## 1. What was built

- **Semantic integrity (PR #559, merged):** Book elements separate source attribution (`derived`, `agent_proposed`, `unattributed`), epistemic status (`asserted`, `hypothetical`, `unresolved`, `conditional`, `rejected`), and a source-derived `interpretation`. Commitment authority is projected on read and never stored. Legacy `provenance` records stay readable, and legacy `unresolved` is exposed as ambiguous.
- **Reviewed revision (PR B):** `book-prepare --instruction ... --target ID` (or `--holistic`) prepares a revision with full text for the targets and their mechanical dependents. `book-complete-file` stores a reviewed proposal and never replaces the working Book. `book-apply-review --request-sha256` applies one applicable review. `book-withdraw` proposes a working rejection through the same review path. `book-resume` reports the revision number, the lineage, and the last applied review.
- **Bridge guide:** `docs/agents/studio-architecture-bridge.md`, sections "Provenance labels" and "Working Book revision, withdrawal and apply".

## 2. Decisions and why

- **Lifecycle stays local to the Book module.** Extracting `auteur.working_revision` now would share a pointer-and-record pattern, while the comparator and the review rules differ. The Book path reuses the canvas lock, the atomic writer and the host-agent records.
- **Changed and new elements must use the explicit form.** Legacy elements that do not change keep their form, so historical records are preserved, not migrated.
- **Unexpected changes block application, and nothing overrides them.** The agent must re-prepare with the element as a target, or use `--holistic`.
- **Requests are identified by attempt as well as content.** This was a defect found in this run (section 4).
- **Series consequences are reported, not propagated.** The Book never writes the Series. A Studio revision handoff is deferred.

## 3. The Book 24 run

Reproduced by `reproduce/craft_run.py` on a disposable canvas built from the W6 baseline and the Book 24 source items. Every Book step is a real CLI call in a separate process. Outputs are in `clean-run/`, candidates in `candidates/`.

| Step | Result |
|---|---|
| Develop from the recorded PR #558 candidate (legacy form) | accepted, revision 0; 83 elements, 49 `unknown_legacy` (ambiguous) |
| Representation correction (Cases 1, 2, 4): 9 targets | applied; 8 legacy labels restated explicitly, 1 interpretive addition; 82 preserved; re-apply is `already_applied`; ambiguous 49 to 41 |
| Probe: an out-of-scope edit to `assume-p4` | review `review_blocked`; apply refused with `unexpected changes block application: assume-p4` |
| Counterfactual, corrected attempt: 13 declared targets | applied, revision 2; 2 added (premise, cost), 15 changed (13 interpretive, 2 mechanical), 76 preserved, 0 unexpected |
| Probe: withdraw the premise while 8 conditional statements rest on it | refused: each of the 8 conditional statements must be revised first |
| Probe: assert a finale claim that depends on `dec-finale-mechanism` (Case 3) | refused: it must be conditional on that decision |
| Withdrawal of `later-books-25-26` (a working decision with no dependents) | applied, revision 3; authority `withdrawn` |
| Fresh process resume at the end | revision 3, lineage of 4 entries, freshness `ready`, `clear` |

**File audits** (`snap-*.json`): at every step, the only files that changed were the Book's own records under `architecture/books/24/`. The Studio Series record, the canvas items, the intentions and the accepted state were byte-identical before and after each step (`summary.json`: `representation_audit`, `counterfactual_audit`, `withdrawal_audit`).

### 3.1 What the counterfactual review shows

The review is `candidates/` plus `clean-run/13-craft-complete.json`.

- **Mechanical reach from the craft-mark is small.** The engine `eng-record-form` has two typed edges (`edge-capability-hands`, `edge-capability-lineage`) and nothing else. Seventeen elements mention the craft-mark, the capability record, or the training condition in their text, but the representation records no link between them. The other twelve targets were declared by the operator after reading the context. Only the two edges were found mechanically.
- **Series references to inspect (11), with the Series state unchanged:** `th_hands_and_draw`, `inst_lineage_crews`, `eng_ledger`, `str_long_return`, `th_maintenance`, `th_custody`, `rx_belonging`, `rx_consequence`, and `alt_a/b/c` (through `later-finale-capability`). Each is `inspection_recommended`.
- **Author decisions touched: 0.** This is a finding, not a clean result. The counterfactual bears on the Right's revocability (`dec-right-revocable`) and on the finale mechanism (`dec-finale-mechanism`) in substance, but the representation records no reference to them, so the review cannot report that link. It is a representation gap.
- **Unresolved effects (6):** interpretive changes with no typed dependency (`assume-p5`, `assume-p6`, `choice-craft-mark`, `inh-right-condition`, `later-books-25-26`, `opt-craft-mark`).
- **Authority shifts (5):** the explicit restatement moved legacy-unresolved consequences to `agent_working`. Those statements were agent proposals in the source. The review surfaces the shift; it is not an author act.
- **Preserved:** 76 of the 91 indexed items (83 elements and 8 edges), unchanged by identity and content hash.

## 4. A defect found and fixed in this run

Requests were content-addressed, so re-preparing the same scope after a blocked review returned the same request and its blocked review. A corrected candidate was then refused as "a different response already completed this request." The fix adds an attempt number to the request settings, so a deliberate re-prepare gets a new identity. A regression test covers it (`test_reprepared_scope_after_a_blocked_review_gets_a_fresh_request`).

A second defect, found in the first run and fixed before the clean run: the review rejected an unrelated changed legacy element at completion, before scope was checked. That is the intended form rule, so the probe was retargeted to an explicit out-of-scope element to exercise the scope check.

## 5. Tests

- `tests/test_working_book_semantics.py`: 20 tests (legacy readability, the four Book 24 cases, promotion refusal, projection invariants, the conditional-on-rejected rule, classification of interpretation changes).
- `tests/test_working_book_revision.py`: 33 tests (scope, targeted and holistic review, unexpected-change blocking, legacy relabelling, unresolved and decision rules, apply, idempotence, supersession, stale Series and stale completion, withdrawal and its refusals, authority preservation, fresh-process recovery, attempt identity, removal and child attribution, reference-only changes, story-vision truncation flag).
- `tests/test_series_working_book_architecture.py` (the PR #558 develop and resume tests, unchanged): all pass.
- Focused run at the commit that carries this evidence: 78 passed (20 semantics, 33 revision, 25 Book develop and resume); lint clean. Hosted validation: none (all workflows are `workflow_dispatch`).

## 6. Not completed

- **Independent code challenge.** A read-only reviewer was launched against the seven challenge questions. It did not return a result within the session, and it was stopped. **No independent review of the code was obtained.** The verification in sections 3 to 5 is self-verification, and it is labelled as such.
- **Fresh-context explanation.** A fresh agent was launched to answer the six questions about the revised Book, from `resume-revised`. It was stopped before it returned. **No fresh-context answer is recorded.**

## 7. Limits of the mechanical and semantic evidence

- The review detects only explicit references (Book element refs, typed edges, Series refs). It cannot see that a statement's meaning depends on another element's meaning. The counterfactual shows this: two typed edges, and seventeen semantically related elements.
- `consequence_candidates` came out empty in the counterfactual. That is a fact about the explicit graph, not evidence that nothing else changed.
- The counterfactual content was written by the coding agent in this session. It is a working proposal and a test of the lifecycle, not a creative judgment that was reviewed by an author.
- Lexical grounding of author declarations (PR #558) and the explicit-form rules do not establish that a statement is true or that it is well written.

## 8. Next responsibility

Before a broader Book revision, two owner decisions are needed: whether phase and link references become typed (so that the review can reach them), and how named characters from prose are sourced. The Studio handoff for Series consequences (the explicit change proposal) is a separate responsibility that should be designed after those decisions.

## Files

- `clean-run/` — outputs of every step, file-hash snapshots, and `summary.json`.
- `candidates/` — the representation candidate, the counterfactual candidate, the unexpected-change probe, and the decision probe.
- `reproduce/` — the driver and helper scripts. They read and write scratch paths and are recorded as they ran, not as portable tools.
