# Atelier × Series/Book context: read-only, owner by owner (2026-11-22)

**Status:** implemented on `feat/atelier-series-context`, opt-in Atelier only (`?atelier`). Read-only.
**Baseline:** `main@0b92409d` (PR #632). **Evidence:** [`../qualification-evidence/atelier-series-context-20261122/`](../qualification-evidence/atelier-series-context-20261122/README.md).

## Author question

While exploring my Narrative Architecture, can I inspect the documented Book and Series plans around a
concept, understand what has been established, and return to the same place?

On `main` the answer was no. A selected concept's folio said nothing about Book or Series plans, and the
Studio had no route to them. The nearest working path was outside the Studio: `book-resume` on the
Working Book CLI, an 85,753-character JSON packet for Book 24 that names `eng_ledger` as a present
constraint but not which Book elements refer to it (`baseline.json`).

## Authority landscape (what exists, who owns it)

| Kind | Owner and location | Status | Link to an Architecture concept |
|---|---|---|---|
| Working Narrative Architecture | Studio canvas, `architecture/current.json` | working, noncanonical | is the concept |
| Working Book architecture | `auteur.series.working_book_architecture`, `<canvas>/architecture/books/<n>/current.json` | working, noncanonical; no Book operation can accept | **recorded**: typed `series_node` refs to Architecture node ids, with node fingerprints and the Architecture request it was written against |
| Full Series plan | `SeriesIdentity`, `<project>/series_identity.yaml` (ADR 012) | author-declared; no acceptance record | none recorded |
| Sparse Series and Book Directions | `VerticalSliceStore`, `.auteur/series/vertical-slice/accepted/*` + provenance sidecars | accepted with revision and content hash; a Book records the Series revision it was accepted against | none recorded |
| Derived continuity | Series dependency graph and setup/payoff check (from the full plan); Global Map/Focus (from the Directions) | derived, not canonical (ADR 012, 013, 019) | none |

A canvas has no Series or Book field. The only association between the Studio and the project-level
plans is that they are kept in the same project. That shows they are available. It does not show they
belong to any one Architecture, and the view says so.

## Alternatives tested

- **A. The existing route is enough.** Rejected. The Studio had no route. The Book CLI is read-only and
  correct, but it leaves the Atelier and returns a packet the author must search by hand. Nothing
  exposed the full Series plan or the Directions to the Studio.
- **B. A contextual read-only bridge.** Chosen. Every record it needs already has an owner with a
  read interface and its own freshness contract. The Working Book records are a real, explicit link.
- **C. Cross-system authoring.** Not warranted yet. Reading answers the author question. Each owner
  already has its own reviewed workflow: Book revise/apply, Series journey propose/accept, and
  editing `series_identity.yaml`. Routing those through the Studio is the next decision (J below), not
  a prerequisite.

## What changed

```text
GET /api/beginner/studio/canvases/{c}/series-context            new, read-only
  studio_series_context.project_series_context(project, canvas)
    working_books   ← working_book_architecture.book_numbers / book_series_references (new, read-only)
                      per referenced node: present, changed since the Book was written, the elements
                      and typed edges that refer to it with the owner's commitment authority;
                      the owner's freshness against the current Architecture
    series_plan     ← SeriesIdentity.from_yaml (absent | invalid | available) + derived graph and
                      setup/payoff check, labelled derived_not_canonical
    series_direction← VerticalSliceStore verified loaders (accepted | unverified | absent);
                      Book: accepted_against_series_revision vs current_series_revision
    architecture_link.recorded = false for the project-level plans; version = fingerprint of sources

Atelier folio (selected concept)
+ Series and Book plans
+   Recorded in Book plans: "Book 24 · The Uncounted Crew · records a reference to this concept in
+     4 elements" + owner freshness → Open Book 24 at this concept
+   Also kept in this project: Series plan / Directions · "Not linked to this concept"
+   none kept: says so, and names each owner's tool
+ Series and Book context (folio view, read-only)
+   Back / Escape → the concept, trail, camera and mode exactly as left; focus on the opener
+   Working Books: what the Book records about this concept; other referenced concepts
+     (select one to see it in the atlas; the trail keeps the way back); how its owner changes it
+   Series plan: Book plans, setups with their recorded payoffs, mysteries, thematic progression,
+     derived graph and checks (not stored)
+   Directions: accepted revision, commitments, Book Directions with their Series revision dependency
+   Ask your coding agent whether this relates → drafts a hypothesis question in the existing
+     coding-agent panel; never sends it, never overwrites an unsent draft
```

No Series record is copied into the Studio store, the canvas or the Architecture. No link field was
added anywhere. No new spatial mode: the atlas does not move while plans are read.

## Integrity rules the code keeps

- A concept is joined to a Book only when that Book records the concept's node id. Equal words never
  join anything (`forNode` matches the id exactly; tested with the concept's own title).
- Project-level plans are always labelled not linked, and the full plan and the Directions are labelled
  as separate owners. Nothing records that they describe the same Series.
- An accepted record is shown as accepted only when its owner's verified loader returns it. A file that
  no longer matches its acceptance record is reported and its content withheld.
- Freshness is the owner's own: Book freshness and semantic impact from `working_book_architecture`,
  and a Book Direction's Series revision dependency from its provenance sidecar. The view re-reads on
  open, on request, and when the Architecture request changes; it says when the plans changed since the
  last read.
- The Series journey keeps every proposal file, accepted ones included. The view counts proposal files
  besides the current accepted records and shows none of them.

## Path to owner-routed editing (not built)

Every record carries `{owner, artifact, path, ref, revision, content_hash}`. A later increment can route
an action to its owner with exactly the source and freshness check that owner already requires:

| Record | Owner action | Check it already enforces |
|---|---|---|
| Working Book element | `book_prepare(store, n, instruction=…, targets=(id,))` → review → `book_apply_review` | Architecture request and Book source unchanged; exact review SHA |
| Series/Book Direction | `propose_series_direction` / `propose_book_direction` → `accept_*` | Book: current Series Direction revision and content hash |
| Full Series plan | author edit of `series_identity.yaml`, then `auteur series validate` | schema validation only; no acceptance record exists |

## Independent review

A read-only reviewer agent that did not build the change drove the served Studio with Playwright on
copies of the four projects. It reproduced seven problems in `1944ba76`. It then re-checked them against
`961ff87d`. Six were fixed. One was partly fixed: a section can still show a read up to 20 seconds old,
but it is now dated. The re-check found one new problem, also now fixed. The full view said no plan
records the concept while a Book could not be read. Each fix has a regression test.

| Finding | Disposition |
|---|---|
| After an applied Architecture revision, the open view kept calling Book 24 current | The view re-reads when the Architecture request changes or the last read is old; a served test applies a revision with the view open |
| An unreadable Book made the section say no plan is kept | An unreadable Book is reported where the concept is read and counts as kept; readable Books no longer settle "no reference" |
| A malformed provenance sidecar returned 500 and hid every source | Each owner, and each record, is read in isolation; damage is reported for that source alone |
| A machine suggestion stayed in the field and named another concept | An untouched suggestion is replaced; only the author's own words are kept |
| The concept section's summary could be stale with no read time | Partly fixed: the section shows its read time and re-reads after 20 seconds; Read again during a read is queued |
| Opening the view announced "Read again: nothing changed" | Opening announces orientation; only Read again announces a re-read result |
| Proposal-file counts assumed an unverified record's proposal | Counted only as far as verified records allow |
| Re-check: with a Book unreadable, the full view said no plan records the concept | It says no readable plan does, and that an unreadable Book might; a damaged sidecar's reason is plain words |

Wording changed after the review: the view's heading names the concept only when a Book records it
("Plans that record …"); "Explore Series and Book context" is no longer a primary button when nothing
is linked; open-decision bindings are not called checked on a stale Book; acceptance dates are local.

## Limits

- Fixtures: the Spring Ledger W6 Architecture and Book 24 record are authentic recorded agent output
  from `docs/qualification-evidence/working-book-architecture-20261112`. The full Series plan is the
  repository's Ash Empire test trilogy with two setups and one payoff added. The Directions are the
  Archive of Lies fixtures, accepted through the Series journey service. None of these was written by
  an author for these projects.
- Working Books refer only to Architecture nodes. Genre contracts, phases and emotion targets cannot be
  referenced by a Book today, and the view says so.
- Global Map and Focus (derived from accepted Realizations) are not shown.
- No author has used this.
