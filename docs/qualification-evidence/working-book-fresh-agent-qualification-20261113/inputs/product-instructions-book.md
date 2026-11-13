# Auteur Book operation contract (current main)

## Working Book architecture (develop and resume)

A Working Book Architecture holds one Book's detailed function. It references the canvas's working Series architecture and never writes it, accepted Identity, or accepted Book Direction. Its records live under `architecture/books/<n>/` in the canvas. This section covers develop and resume. Reviewed revision, withdrawal and apply follow the separate section below.

    PYTHONPATH=<repo>/src PYTHONUTF8=1 python -m auteur.series.working_book_architecture --project <project> --canvas <canvas> <action> --book <n> [--candidate FILE]

1. **Prepare.** `book-prepare --book <n>` opens a develop request. It needs a current Series working architecture and at least one working item in group `book-<n>` (the Book's source). The request carries the full text of that source, the Story Vision, the creative intentions, and the Series architecture with its open questions indexed and hashed.
2. **Complete.** `book-complete-file --book <n> --candidate <file.json>` validates one schema-v1 JSON object against the pending request and stores it. Every reference must resolve against the Series revision the request was built on. An open-question reference carries the question's index and the SHA-256 of its text. The command never accepts anything.
3. **Resume.** `book-resume --book <n>` is read-only. It returns the freshness status, the Series constraints the Book references, the exports (consequences, possibilities, assumptions with reversals, alternatives by title), the open author decisions, the unresolved items, and the stored artifact.

Refusals:

| Message begins with | Meaning |
|---|---|
| `develop and complete the Series working architecture first` | No current Series architecture. Develop it through the Studio lifecycle first. |
| `record Book <n>'s source` | No working item in group `book-<n>`. |
| `Book <n> already has a working architecture` | Revision is not available in this increment. |
| `the Series architecture or the Book's source changed after this request` | The request is stale. The response is kept as `stale_response.json` as evidence. Prepare again. |
| `provenance '<value>' cannot be written by an agent` | `author_fixed`, `accepted` and `unlabelled` are never valid in an agent's response. |
| `<kind> reference '<id>' does not resolve` | A reference names something absent from the Series revision, the artifact, or the visible source. |

Book elements separate three questions. Write them explicitly:

- `attribution`: what supports the statement. `derived` (cite the source in `refs`; put your own contribution in `interpretation`), `agent_proposed` (your own inference), `unattributed` (the source asserts it without naming a source; do not guess one).
- `epistemic_status`: where the statement stands in the working proposal. `asserted`, `hypothetical` (an alternative not taken), `unresolved` (a genuinely open question or missing information), `conditional` (depends on an assumption or an author decision you cite in `refs`), `rejected`.
- Commitment authority is not written. The read projection derives it: `agent_working`, `not_established`, `undecided`, `author_reserved`, `not_adopted` or `withdrawn`. No Book operation can produce `author_fixed` or `accepted`.

Rules the validator enforces: a source-derived element cites a source reference; an asserted claim may not depend on an author decision (it must be `conditional`); an item listed as unresolved is `unresolved`; an author decision is `derived` from its Series question and stays `unresolved`. An assumption may state no reversal (`reversal` null). That leaves the reversal `unknown`; it does not make the assumption unresolved.

Historical records keep the legacy `provenance` label. Legacy `unresolved` is read as `unknown_legacy` and marked `ambiguous`, never reinterpreted. A legacy element cannot also carry the explicit fields.

Named agents need a `name_source` that is a visible source item or a Series node. Names that appear only in prose are not structured as named agents; record them as an unresolved item instead.

## Working Book revision, withdrawal and apply

A revision changes a named set of a Book's working elements. It never replaces the working Book directly. Every change is reviewed, and applying a review is a separate explicit step. Only the Book's own records under `architecture/books/<n>/` change.

    PYTHONPATH=<repo>/src PYTHONUTF8=1 python -m auteur.series.working_book_architecture --project <project> --canvas <canvas> <action> --book <n> ...

1. **Prepare.** `book-prepare --book <n> --instruction "<text>" --target <element-id> [--target ...]` opens a revision request. Name the elements to change, or pass `--holistic` to permit changes anywhere. The request carries the full text of the targets and of the elements that reference them (explicit book references and typed edges), a manifest of every other element by id and content hash, the full source, the Story Vision and intentions, the assumptions and alternatives, and the Series nodes the scope references. `book-prepare` without `--instruction` still develops only a Book that does not exist yet.
2. **Submit.** `book-complete-file --book <n> --candidate <file.json>` takes the complete revised Book object, not a patch. It validates the object against the Series revision and the baseline the request used, and it stores a reviewed proposal. It never changes the working Book.
3. **Review.** `resume` or the completion result reports the review: `changes.added`, `changes.changed` (each classified `interpretive`, `representation`, `representation_reclassified_from_legacy`, `working_status`, `withdrawal` or `mechanical`), `changes.removed`, `preserved`, `unexpected_changes`, `consequence_candidates`, `dependency_implications`, `series_consequences`, `author_decisions`, `authority_changes` and `unresolved_effects`. Read `unexpected_changes` before anything else.
4. **Apply.** `book-apply-review --book <n> --request-sha256 <reviewed request>` applies only that reviewed request. Applying writes the working Book, advances its revision number, and appends to its lineage.
5. **Recover.** `book-resume` in a new process returns the applied Book with its revision number, lineage, last applied review, and freshness.

Withdrawal is a working decision: `book-withdraw --book <n> --element <id> --rationale "<text>"` proposes rejecting one working element. It produces a review that you then apply with `book-apply-review`. It refuses the Book's function, author decisions, open questions, rejected items and legacy elements.

Refusals:

| Message begins with | Meaning |
|---|---|
| `a revision needs` or `name the elements` | The scope is not explicit. Name targets, or pass `--holistic`. |
| `unknown target elements` | A target id is not in the working Book. |
| `this request has no completed review` | Apply only after completion has produced a review. |
| `a newer Book request superseded this review` | A later prepare replaced it. Review the newer request. |
| `unexpected changes block application` | The candidate changed an element outside the permitted set. Prepare again with that element as a target, or with `--holistic`. |
| `working context changed` or `the Series architecture or the Book's source changed` | The Series or the source changed. Prepare again. |
| `a new or changed element must use explicit attribution and epistemic_status` | A changed element is still in the legacy form. Restate it explicitly. |
| `cannot be settled by a working revision` | An open question stays open. A revision cannot settle it. |
| `Series binding is fixed` | An author decision's index and text hash cannot change. |
| `must be conditional on that decision` | A claim that depends on an author decision must be conditional, not asserted. |
| `which is rejected` | A conditional claim rests on a rejected assumption. Revise the dependent first. |

Re-preparing an identical scope creates a new attempt, so a corrected candidate can be submitted after a blocked review.

What applying does not do: it does not write the Series architecture, accepted Identity or Book Direction, intentions, canvas items or the artifact store, and it does not choose an accepted ending. A mechanical reference in a review is a dependency to inspect. It is not evidence of a narrative contradiction. Series consequences are reported with the Series state unchanged, and the Series changes only through its own revision lifecycle.
