# Studio architecture bridge: the working-revision lifecycle

This page is for coding agents that continue a Narrative Architecture through the Studio command-line bridge. It describes the commands as they are, the order to use them, what each refusal means, and what applying a revision does and does not do.

Run every command with the repository's `src` on the path:

    PYTHONPATH=<repo>/src PYTHONUTF8=1 python -m auteur.beginner.studio_architecture --project <project> --canvas <canvas> <action> [options]

## The lifecycle

    resume -> prepare -> complete-file -> show / resume (inspect) -> apply-review -> resume

1. **Recover the working state.** `resume` prints a read-only packet: the story vision, the working candidate (`architecture`), its `architecture_status`, the open questions, the provisional concepts, the author's intentions, any pending review (`pending_review`), and the adoption lineage. Read it before anything else.
2. **Prepare a request.** `prepare` opens a host-agent request. With no instruction it asks for a new architecture. With `--instruction "<text>"` it asks for a revision of the current candidate. It prints the request, including its `request_sha256`, and the instructions the writer must follow.
3. **Submit a candidate.** `complete-file --candidate <file.json>` validates a candidate you wrote against the pending request, using the schema described below.
   - A request **without** an instruction is applied at once. Its candidate becomes the working architecture.
   - A **revision** request is stored as a *reviewed revision awaiting application*. It does not change the working architecture yet. The result has `status: review_ready` and a `review` object with `request_sha256`, the changed components, and the preserved identifiers.
4. **Inspect the review.** `show` or `resume` reports the pending review. Read `review.changes` and `review.preserved` before you apply anything. Confirm that unrelated elements are preserved.
5. **Apply exactly the reviewed request.** `apply-review --request-sha256 <review request_sha256>` applies that revision to the working architecture. The identifier is required. The command never applies the latest request by default. Applying is a separate step from submitting, and `complete-file` never applies a revision by itself.
6. **Recover after applying.** `resume` in a new process returns the applied architecture. Its `pending_review` is `null`, and its `candidate_request_sha256` is the applied request.

## `apply-review`

    apply-review --request-sha256 <64 lowercase hex characters>

It prints one JSON object. The object carries an `application` block:

| `application.result` | Exit code | Meaning |
|---|---|---|
| `applied` | 0 | The reviewed revision is now the working architecture. The rest of the object is the architecture's current projection. |
| `already_applied` | 0 | That request is already the working architecture. Nothing changed. |
| `rejected` | 1 | Nothing changed. `application.error` says why (below). |

Use of an argument that is not supplied is a usage error (exit code 2).

### Why a revision is refused

| `application.error` begins with | Meaning | What to do |
|---|---|---|
| `request_sha256 must be a 64-character` | The identifier is malformed. | Copy the identifier from `complete-file`'s `review.request_sha256`. |
| `no architecture request has this identity` | No request with this identifier exists in this canvas. | Check the canvas and the identifier. |
| `architecture revision has not been completed` | The request was prepared, but no candidate has been submitted for it. | Submit a candidate with `complete-file`, then apply. |
| `a newer architecture request superseded this review` | A later `prepare` has replaced this request. This applies even when the older review was already applied. | Review the newer request, or prepare a new revision on the current state. |
| `the baseline architecture changed; review again` | The working architecture changed after this review was prepared. | Prepare and review a new revision against the current state. |
| `working context changed: story vision, intentions or design context changed; review again` | The story vision, an author intention, or the design context changed after the review. | Prepare and review again. Do not edit the review's candidate to get past this. |
| `there is no current working architecture to revise` | There is no baseline to revise. | Prepare and complete a new architecture first. |

## What applying does and does not do

Applying a reviewed revision writes the working architecture only. It does not accept Story Identity, canonical Structure, Realization or Expression, or shared ontology. It does not change an author intention, promote a provisional concept, select a finale alternative, or convert an `agent_proposed` element into `author_declared`. The applied material keeps its working, noncanonical status.

Working application is therefore a different act from authorial acceptance. An author accepts canon through the author's own actions. The bridge has no command that accepts canon, and `apply-review` does not stand in for one.

## The candidate contract

A candidate is schema version 2 JSON. Its limits are part of the contract, and `complete-file` checks them:

- `summary` up to 3000 characters. `nodes` up to 80, each with a category, a summary of up to 2000 characters, and a `scope`. `links` up to 180, each with a `function` of up to 120 characters. `phases` up to 32, each with a `narrative_function` of up to 1000 characters. `open_questions` up to 16 strings.
- There is no Book node. A Book's function is expressed in a phase narrative, a node summary, or an open question.
- Emotion targets carry a `provenance`: `author_declared` or `agent_proposed`. See *Provenance labels* below.

## Provenance labels

`author_declared` means the author's own visible text names the emotion. The label is a source-origin claim. It is not author acceptance: the intended effect, eliciting condition and aesthetic strategy of a target remain the agent's elaboration until the author reviews them.

The bridge enforces the label mechanically, at `complete-file`:

- A target may be `author_declared` only when every significant word of its `id` (three letters or more, not a function word) appears in the author-visible text of that request: the Story Vision and the non-concept working items the packet shows. Agent working notes, the previous candidate and the revision instruction do not count as author text.
- A revision may keep an author claim that the baseline already carried, changed or unchanged, without that proof. This preserves historical claims.
- Anything else labelled `author_declared` is rejected with `author_declared emotion target '<id>' is not named in the author's source text shown in this request`. Nothing is persisted. The same request stays open for a corrected response.
- Use `agent_proposed` for every other target. Labelling an interpretation as `agent_proposed` is always admissible.

The review reports every author-origin change under `preserved.author_declared_emotion_changes`, with a `status` of `new_author_claim`, `promoted_to_author_declared`, `changed`, `label_removed` or `removed`. Unchanged claims appear under `preserved.author_declared_emotion_targets`. A review never reports an author claim as preserved when it changed.

Grounding is lexical. It establishes that the author's words name the emotion; it does not establish that the author endorsed the agent's elaboration, and it cannot tell whether a working item was typed by the author or by an earlier agent. Those limits are deliberate and are recorded in the provenance evidence.

## Scope of the authoring restrictions

The host-agent writer is told, and the validator enforces, a boundary for architecture-only proposals:

- **Category.** Schema version 2 architecture proposals must not use the `character` or `relationship` categories. The validator rejects them with `architecture-only proposals cannot instantiate characters or relationships`. The schema's category type is shared with other operations, so it lists more categories than this proposal may use. Character and relationship instances belong to other operations.
- **Names.** The writer must not invent names of characters, places, factions, events, plot acts or scenes. It may refer to proper nouns the author supplied. In a **revision**, it may also reuse proper nouns that already appear in the current working architecture. It must never add new ones.
- **Generic illustration.** Generic archetypes may illustrate a structural function. They must not be elaborated into story facts.

These restrictions keep an architecture-only proposal to mechanisms, so that invented story facts cannot enter the working state by way of a structural revision.

## Recording provisional concepts and intentions

- `record-concept --concept <file.json>` records one provisional concept. Its `status` must be `provisional`. It is working material, not shared ontology.
- `keep-intention --title <text> --directive-file <file>` records an author-directed intention. Use it only for a directive the author has given. Do not invent intentions. `set-intention-status` is an author action.
- `intentions` lists the author's intentions and their status.

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
