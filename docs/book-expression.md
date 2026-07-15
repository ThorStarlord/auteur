# Book Manuscript Expression

Book Manuscript V1 is an assembled Expression artifact. It owns Chapter order,
the Book title, and minimal separators. It does not own Chapter prose, Scene
prose, transitions, Realization, Structure, Identity, or Bible/state.

## Accepted-source rule

Composition resolves only accepted Chapter Expressions. Each manifest records
the Chapter ID, accepted Chapter Expression ID, revision, content hash, and
position. Missing, invalid, stale, archived, or ambiguous Chapters block
composition; Chapters are never silently skipped.

## Manifest and storage

```yaml
book_expression_id: book_01:expression_v001
book_id: book_01
revision: 1
authority: derived
lifecycle: proposed
freshness: fresh
chapters:
  - chapter_id: chapter_01
    chapter_expression_id: chapter_01:expression_v001
    accepted_revision: 1
    content_hash: sha256:...
    position: 1
book_owned_content:
  title: The Lantern at Low Water
  separator: "---"
transformation:
  id: expression.compose_book
  version: 1
```

Files are stored under `book/expression/` as `book_vNNN.md` and
`book_vNNN.yaml`, with `accepted.yaml` as the explicit accepted pointer.
Previous revisions remain inspectable.

## Freshness, acceptance, and inspection

A Book becomes stale when an included accepted Chapter revision or hash,
Chapter order, required Chapter lifecycle, separator, or transformation
version changes. Inspection identifies affected Chapters and recommends
recomposition. An unrelated Chapter does not stale the Book.

Book composition is derived until explicit Book acceptance. Acceptance updates
only the Book pointer and preserves prior Book history; it never changes a
Chapter pointer or upstream narrative artifact.

Inspection reports title, revision, lifecycle, Chapter order, source revisions,
freshness, stale sources, and next action. Comparison reports added/removed or
reordered Chapters, changed Chapter revisions, separator changes, and a
deterministic Markdown diff. Export writes clean Markdown without internal
Scene markers.

```bash
auteur expression compose-book PROJECT --chapter chapter_01 --chapter chapter_02
auteur expression inspect-book book_01:expression_v001 --project PROJECT
auteur expression compare-books BOOK_A BOOK_B --project PROJECT
auteur expression accept-book book_01:expression_v001 --project PROJECT --by author
auteur expression export-book book_01:expression_v001 --project PROJECT --output manuscript.md
```

## Canonical dogfood and non-goals

The Lantern at Low Water bootstraps two accepted Chapters in a temporary copy,
composes and accepts a Book, revises Chapter 1 to stale the previous Book,
recomposes, and exports clean Markdown. The committed reference is never a
write target.

V1 does not provide EPUB/PDF/DOCX, Book round-trip reconciliation, Series
composition, Chapter merge/split, automatic rewriting, publication formatting,
collaboration, or generic layout engines.
