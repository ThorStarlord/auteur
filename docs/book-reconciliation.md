# Book External-Edit Inspection and Routing

Book routing is a read-only adapter. Chapter Expression owns Chapter prose;
Book Expression owns Chapter order, separators, title rendering, and assembly.

## Marker contract

```html
<!-- auteur:chapter id=chapter_01 expression_revision=3 -->
...
<!-- auteur:end-chapter id=chapter_01 -->
<!-- auteur:book-separator id=separator_01 revision=1 -->
---
<!-- auteur:end-book-separator id=separator_01 -->
```

IDs are unique, opening and closing IDs must match, nesting is invalid, and
marker order must agree with the accepted Book manifest. Clean Book export
removes markers. Markerless manuscripts remain readable but cannot be routed
automatically.

## Inspection artifact

Inspections are derived under `book/expression/reconciliation/inspections/` and
record the accepted Book revision/hash, external manuscript hash, marker
contract, Chapter revisions/hashes, Chapter-local findings, Book-owned findings,
unresolved findings, transformation provenance, and freshness.

## Change taxonomy and routing

- Chapter-local wording changes delegate to the existing Chapter reconciliation
  inspection. No parallel Chapter proposal format is introduced.
- Book-owned separator, title, insertion, and order changes create
  noncanonical Book proposal artifacts.
- Markerless, malformed, cross-boundary, merge, split, and ambiguous changes
  remain unresolved and receive no automatic proposal.

External text is preserved separately. No route applies, publishes, accepts, or
completes any change.

## Freshness and atomicity

Routing revalidates the Book and affected accepted Chapters immediately before
delegation. A changed Book, Chapter, order, or external manuscript blocks
routing. Inspection remains preserved, while no routes, proposals, or routing
manifest are finalized.

Routing stages derived outputs and either publishes the complete routing result
or removes staged proposals, delegated inspection records, and the routing
manifest. Canonical pointers and source artifacts are never changed.

## CLI

```bash
auteur expression inspect-book-manuscript edited_book.md \
  --against book_01:expression_v003 --project PROJECT
auteur expression route-book-inspection inspection_ID --project PROJECT
auteur expression show-book-inspection inspection_ID --project PROJECT
```

Normal output is concise; `--json` and `--verbose` expose hashes and provenance.
There are intentionally no Book proposal apply, publish, accept, or complete
commands.

## Application planning and publication (Phase B)

Book-owned proposals can be assembled into a derived, deterministic application
plan and published transactionally into durable, unaccepted Book candidates plus
a noncanonical preview and a publication manifest. Publication is not acceptance:
no accepted Book or Chapter pointer, and no Structure/Identity/Blueprint/Scene
artifact, is ever changed. See
[book-reconciliation-application.md](book-reconciliation-application.md) for the
plan schema, candidate model, preview behavior, live freshness gate, atomicity,
duplicate/stale handling, CLI, and non-goals.

## Dogfood scenarios and non-goals

The adapter is designed for Chapter wording edits, separator edits, explicit
order proposals, unchanged marked Books, markerless Books, stale inspections,
and cross-Chapter movement. Phase B adds Book proposal planning and atomic
candidate publication. It does not implement Book candidate acceptance, Book
recomposition from candidates, reconciliation completion, automatic markerless
reconstruction, Chapter merge/split, front/back matter, publishing formats, or
collaboration.
