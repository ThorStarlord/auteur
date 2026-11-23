# Atelier × Working Book development: through the Book's own owner (2026-11-23)

**Status:** implemented on `feat/atelier-book-authoring`, in the opt-in Atelier only (`?atelier`).
**Baseline:** `main@19ec9dc2` (PR #633).
**Evidence:** [`../qualification-evidence/atelier-book-development-20261123/`](../qualification-evidence/atelier-book-development-20261123/README.md).

## Author journey

**Living Atlas → Working Book context → targeted creative revision → review → explicit Apply → Living Atlas.**

On `main`, PR #633 showed what a working Book records about a concept, read-only. To change it, the author had to leave the Studio. The same task then took three Working Book CLI commands (`baseline.json`):
- prepare, which printed about 160 KB;
- complete, whose review is 6.9 KB of raw JSON keyed by element ids;
- apply, which needs the review's 64-character identity copied by hand.

## Who owns what

| Responsibility | Owner | What the Studio does |
|---|---|---|
| Working Book records, revision lifecycle, review, applicability, lineage | `auteur.series.working_book_architecture` | Calls the owner's functions; reimplements none of their logic |
| Which Book elements a concept may lead to | The Book's typed `series_node` references (PR #633) | Offers **Develop** only on elements that record the concept's node id |
| Executing the request | The author's coding agent (host-agent protocol) | Shows the request and the owner's commands. It never calls a model. |
| Deciding to apply | The author | Applies only the exact reviewed request, and only when the author asks |

## Alternatives considered

- **Reuse the Architecture coding-agent panel and review.**
  - Rejected for revision. That panel is bound to the Architecture's anchors and request lifecycle. A Book request has its own owner, packet, review and identity.
  - Kept for investigation. **Ask your coding agent about it instead** drafts a question there and never sends it, as PR #632 already does.
- **A new Book editor.** Rejected. It would be a second revision engine.
- **A thin server adapter plus a folio section inside the existing Book context view.** Chosen.
  - The owner already has targeted and holistic revisions, dependent scope, stale-response evidence, unexpected-change blocking, lineage, and repeat-apply as a no-op.
  - Only a read projection and two author-facing guards were missing.

## What changed

```text
owner (auteur.series.working_book_architecture)
  read-only: book_elements, book_review_elements (the reviewed candidate's elements), book_revision_scope,
             book_pending_state, book_series_references(...).last_applied, CLI book-show
  book_prepare(..., expect=RevisionExpectation)   optional; None keeps every existing caller unchanged
    checked under the canvas lock, at the moment the request is written:
      the Book is still the revision the author read
      a waiting request is replaced only when it is the one, in the state (reviewed or not), the author saw
      current_only: a Book out of date with the Architecture or its source takes only a whole-Book revision

Studio adapter (auteur.beginner.studio_book_development)
  GET  /books/<n>                phase: none | awaiting_coding_agent | review_ready | review_blocked | stale
  GET  /books/<n>/scope?targets= the owner's scope rule, before anything is prepared
  POST /books/<n>/prepare        + the Book is still the revision the author read
                                 + a waiting request is replaced only when the author says so
                                 → book_prepare
  POST /books/<n>/host-agent-response   manual fallback → book_complete (a schema error becomes a readable 400)
  POST /books/<n>/apply          exact request_sha256 → book_apply_review (the owner checks again at the write)
series-context: each working Book gains last_applied and development (its phase)

Atelier (Series and Book context view)
  What Book n records about “concept”
    each element: Develop this element · “Changed in working Book revision N” after an apply
  Developing Book n · working revision
    composer: the target in words, its standing and freshness, exact identifiers (disclosed)
              scope: only this element (+ the elements that refer to it) | the whole Book
              “What should change?” · replace a waiting request (explicit) · Prepare · Not now
              Ask your coding agent about it instead (drafts a question, never sends it)
    waiting:  what you asked · Check for your coding agent’s response
              What to give your coding agent: a message with the owner’s commands · the exact request
              Paste its response instead (manual fallback)
    review:   changed (before/after) · added · removed · N unchanged · outside what you allowed
              to re-read (recorded links, not established consequences) · Architecture concepts cited
              author decisions (stay yours) · standing changes · request identity and baseline
              Apply this revision to working Book n | Prepare again (wider or whole Book)
    stale:    why · Prepare it again against the current Book
    applied:  “Only this working Book changed. The Architecture …, the Series plan and the Directions are unchanged.”
```

## Integrity rules the code keeps

- **Joins by node id only.** A concept leads to a Book element only through the node id that element records. Project-level Series plans and Directions offer no Develop action.
- **Scope is the owner's.** A targeted request stays targeted. The whole Book is a separate, explained choice. If the agent changes something outside the scope, the review is blocked. The author can then prepare again with a wider scope, never silently.
- **No assumed success.**
  - A refused prepare, response or apply leaves the Book unchanged.
  - The view re-reads the owner's state, and the author's words are kept.
  - Apply is refused at the write when the Architecture or the Book's source changed after the review, or when a newer request superseded it. The view's refresh interval is not relied on.
- **A Book revision is not an Architecture revision.**
  - Applying does not change the Architecture request SHA, so the atlas keeps every position, the camera and the trail.
  - No concept is marked as revised.
  - The change is labelled "Changed in working Book revision N".
- **No cross-attachment.** Every Book call is tagged with its canvas. An answer for another canvas or Book is dropped. Switching canvas reloads the page.
- **Typing survives re-renders.** A field the author is typing in is kept as the same element when a read finishes. Its words, caret and scroll do not move.

## Independent review and dispositions

Two independent reviewers drove and probed `e1bc13a9`; neither had built it. One reviewed authority and freshness by script against disposable projects; one reviewed interaction and adversarial use in the served Studio at 1440 and 390 px. Neither found a write outside the Book's own records, or an undamaged state in which the view offered an Apply the owner refused.

| Finding | Disposition |
|---|---|
| A targeted revision of one element of a Book already out of date with the Architecture marked the whole Book current on Apply (owner behaviour on `main`; the Studio made it one click) | The Studio offers only a whole-Book revision for an out-of-date Book and says why before the author writes; the owner enforces it under its lock (`current_only`). The owner's CLI is unchanged. |
| The adapter's prepare guards were check-then-act outside the canvas lock (two tabs; an apply between check and prepare) | Moved into the owner, under the lock, as an optional `RevisionExpectation` |
| Replacing a waiting request could discard a review that arrived after the author looked | The expectation includes whether the waiting request has a review; the view words the choice as "whose review is ready" |
| A malformed pasted response, damaged review or missing request file gave a 500 or a false "canvas not found" | Each is a readable 400 for that Book; reasons carry no absolute paths; a damaged review is reported, never offered for Apply |
| Unsent words followed the author to another element | One draft per Book and scope; words move with the author only when they switch scope |
| Refusals were drawn but not announced; the live region kept saying the opposite | Every refusal is announced |
| Disclosures collapsed on every re-render | Opened disclosures stay open; after Prepare the coding-agent message opens, with a Copy button |
| Long reviews: Apply far below, the same sentence on every item, whole paragraphs repeated | Summary and decision first; each explanation once per list; changed words marked; long lists folded; Apply repeated at the end |
| Jargon: typed edge, legacy field names, the owner's internal note | "Link", "Working status: asserted → conditional", "Restated in the explicit form"; the owner's note sits under the request identity |
| "Unchanged since the Book was written." beside "Changed in working Book revision 1" | It now names its subject: the Architecture concept |
| Escape inside a text field closed the view | A text field keeps Escape |
| A request replaced from another tab went unannounced | Checking says so |

Recorded, not changed: a response for a superseded request is refused without being kept as stale evidence (owner behaviour); the atlas keeps showing a node the Architecture removed until the author asks for the new Architecture (PR #632 behaviour); every Studio load creates its canvas if missing (pre-existing).

## Limits

- No author has used this. The authentic journey was operated by agents, with a separate coding agent fulfilling the request through the owner's CLI.
- The review is the owner's. The view words it, but it cannot say whether a changed element still reads true. It lists the recorded links to re-read.
- Withdrawal (`book-withdraw`) and developing a Book that has no working architecture yet are not offered in the Studio.
- Full `SeriesIdentity` and sparse Direction editing are out of scope, as is canonical acceptance.
