# Glass Archive Browser review and interface direction

**Date:** 2026-10-15  
**Scope:** automated Browser review of the reconstructed, disposable Glass Archive Book; no human UX session  
**Integrated product source:** `ef5ae8c7910fe7b3db38f6e2af87d1f45ed6182c` (current `main`)  
**Local repair candidate:** `bb98998baeedb1aaae1c564a48f5dd79732e4383` (`codex/glass-archive-x3-ux-review`)

## Provenance and setup

The full six-Chapter simulated-author qualification is recorded separately in
[the fixture-complete report](glass-archive-fixture-complete-20261015.md).
That report's source checkout was clean at `ef5ae8c7910fe7b3db38f6e2af87d1f45ed6182c`.
GitHub's `main` ref matched that SHA at review time. All six accepted `final.md`
files in the fixture were independently re-hashed and matched the report's
Chapter 1–6 SHA-256 values.

The served Browser used another disposable copy:

`C:/Users/Admin/AppData/Local/Temp/glass-archive-x3-browser-review-20261015/project`

It was copied from:

`C:/Users/Admin/AppData/Local/Temp/glass-archive-fixture-complete-20261015/project`

The browser copy gained only a local empty Studio canvas and its lock under
`.auteur/beginner/studio/canvases/`. Hash comparison found no changed or missing
source-project files, including all story files, accepted Chapters, Bible,
outlines, and author-decision receipts. This is a new browser-test copy, not the
original project.

The UI was served by Auteur's local Beginner server and inspected with
Playwright Chromium at 1365×900 and 390×844. The desktop UI connector had no
available Browser provider, so this was automated Browser evidence, not a
visible user-browser or human walkthrough. Screenshots were retained locally
under `C:/Users/Admin/AppData/Local/Temp/glass-archive-x3-browser-review-20261015/`
and are not committed.

## Observed behavior on integrated `main`

At the root route, the Studio opened in **Narrative Architecture** with a new
empty working canvas, while the existing Book was not shown. The Book overview
was buried under **More tools**. After selecting it from that default tab:

- the map showed Chapters 1–6 plus a false **Chapter 7 · Working** node;
- the next action incorrectly said **Write Chapter 7**, although the fixture
  had six accepted Chapters and a six-Chapter plan;
- the Story Architecture empty-state card remained over the chapter map;
- the Book orientation panel was hidden because the workspace remained in
  Narrative Architecture;
- Chapter nodes were read-only positions. Selecting Chapter 2 did not open its
  manuscript; it showed `position only` and chapter-order links;
- the pending list exposed six unreviewed proposals, including rough fragments
  such as `Then Beatrice` and `treat the convent`. They remained Suggested and
  noncanonical; no author decision was made in the browser;
- the recent-history panel displayed five long event summaries, including
  multiple entries from Chapters 5 and 6.

At 390px the document width remained 390px. The graph and menu were still dense;
this measures overflow only and does not establish mobile usability. No browser
page errors occurred.

## Small repair and verification

The progress adapter resolved its displayed planned count from discovered
Chapters, then passed only the blueprint's absent count (`0`) to the orientation
projection. The fix passes the already resolved count to that projection.
The Studio's Book-view command now switches to Story Realization, hides the
irrelevant empty-canvas prompt and generic inspector prompt, and presents the
existing read-only orientation panel. No story files, canon, discovery proposal,
or authority workflow changed.

At exact local candidate `bb98998baeedb1aaae1c564a48f5dd79732e4383`, a fresh
served Browser run from the default Architecture tab verified:

- Book overview selects Story Realization and shows the orientation panel;
- six Chapter nodes are present, with Chapter 6 marked `Kept · current`;
- the heading reads **Chapter 6 · Kept** and the next action reads **Review your
  Book**;
- the empty-canvas and generic inspector prompts are hidden;
- at 390px, document width equals viewport width; no page errors occurred;
- the only added files in the Browser project are its disposable empty Studio
  canvas and lock; the story-state files remain byte-identical.

Focused tests: 4 passed. Existing Stage B Chromium check: 16/16 passed,
including save/reopen, conflict safety, no canonical file changes, and no page
errors. A separate assertion in the pre-existing book-progress test fails on
both this candidate and unchanged `main` (`test_book_progress_reuses_accepted_book_as_publication_preflight` expects
two accepted prose Chapters where the fixture contains zero). It is recorded as
a baseline-identical test failure and was excluded from the four focused pass
count.

## Separate dispositions

- **F2 narrative behavior:** bounded simulated-author pass for this reconstructed
  six-Chapter journey only. The exact Chapter decisions and source freshness are
  in the fixture-complete report. No general story-quality claim follows.
- **X3 persistence:** API/file-level pass for that reconstructed project; all six
  accepted prose files matched their recorded hashes after fresh-process load.
- **X3 Browser experience:** initially failed at the completed-Book re-entry
  projection. The bounded repair fixes the incorrect Chapter 7 action and makes
  Book overview visible when opened from the default tab. The overall Browser
  experience remains **not qualified**: chapter-to-manuscript navigation is
  absent, recent history is dense, pending discovery labels need author review,
  and reopening the Studio starts in the working canvas rather than restoring
  Book orientation.
- **Human UX:** not tested. No comfort, preference, cognitive-load, product
  quality, or production-readiness claim is made.

## Follow-up graph-first navigation and re-entry evidence

The owner-selected direction remains the graph-first Studio documented in
`docs/design/2026-10-09-living-story-studio.md`. The earlier comparison of
compact, graph-first, and manuscript/map compositions is retained as tradeoff
analysis; the manuscript/map layout is an interaction composition, not a
replacement product direction.

At exact code SHA `aabfe577068f383887709e7bbc695261634e3d66`, an automated
Chromium run used the disposable project
`C:/Users/Admin/AppData/Local/Temp/glass-archive-navigation-v2-20261015/project`,
copied from the complete fixture at
`C:/Users/Admin/AppData/Local/Temp/glass-archive-fixture-complete-20261015/project`.
It observed: a completed Book orientation on Studio entry; Chapter 2 marked
Kept in the graph; the Chapter action opening the existing
`/beginner.html?chapter=2` review route with its 8,269-character accepted prose;
browser Back returning to the Book graph; and completed Book orientation after
reopening the explicit canvas URL. At 390px the document had no horizontal
overflow. No page errors occurred, and all 89 non-Studio fixture files matched
the source hashes after the journey.

`node --check` passed for both affected Browser scripts. Focused Browser tests
passed, and `scripts/studio_stage_b_check.py` passed 16/16 on that SHA. One
intermediate Stage B attempt failed during its restart/reopen step; a repeat on
the same source passed all 16 checks. The focused check does not test author
comprehension. The baseline-identical `test_book_progress_reuses_accepted_book_as_publication_preflight`
failure remains a separate Python test issue and was not weakened or skipped.
This is bounded automated Browser behavior evidence, not human UX validation
or product readiness.

## Interface concepts explored

The concepts below are low-fidelity interaction sketches grounded in the
observed Book task. They are not human-tested mockups.

### A. Graph-first spatial authoring

```text
Narrative Architecture | Map / Relationships / Consequences
[Structure graph with linked characters, events, and Chapters]
                                      [Selected item inspector]
```

It is strongest for comparing relationships and seeing whole-story shape.
The current screen puts many tools and graph vocabulary in view before the
author can resume a manuscript. Its Chapter nodes currently orient by position
but do not navigate to prose. A production graph-first experience would require
stronger links from accepted story state to writing and review actions.

### B. Compact progressive-disclosure workspace

```text
The Glass Archive                         Chapter 6 · Kept · 6/6
Review your Book
Recently changed: forecasting system exposed                 [Details]
Suggested updates: 6                                      [Review]
Chapters   1 Kept — 2 Kept — 3 Kept — 4 Kept — 5 Kept — 6 Kept
```

It gives the next author action and accepted/Working status the strongest
hierarchy. Rationale, provenance, continuity detail, and long change summaries
can open only when requested. This is compact and comparatively cheap to build
over the existing Book projection, but it is weaker for authors who actively
think spatially about plot and relationship structure.

### C. Hybrid manuscript-and-map workspace

```text
The Glass Archive             Chapters / Map / Updates
Chapter 6 · Kept · 6/6        1  2  3  4  5  6
Review your Book               Kept … Kept; 6 current
------------------------------------------------------
Accepted manuscript / current writing surface
------------------------------------------------------
Recent change (collapsed)   Suggested updates (explicit review)
Map opens as a derived, read-only whole-story view.
```

This keeps manuscript work and the next action primary, with a compact Chapter
navigator and an optional spatial map. Accepted history, Working prose, and
Suggested discoveries remain visibly separate. Map and evidence views stay
derived; existing domain services remain the owners of review, acceptance,
reconciliation, and canon.

| Dimension | Graph-first | Compact progressive disclosure | Hybrid |
|---|---|---|---|
| Product value | High for spatial structure work; weaker re-entry to prose in the observed screen | High for resume/write/review flow | High across prose, navigation, and structural inspection |
| Cognitive load | Highest in the current implementation: broad toolbar, facets, graph, inspector | Lowest default load; detail is on demand | Low-to-medium if map and evidence remain optional |
| Information architecture | Graph is primary; accepted text is secondary | One current task with clear status and next action | Manuscript is primary; compact navigator and optional map |
| Implementation cost | Existing graph has substantial surface; connecting it to every author task is high | Low-to-medium using current read-only progress projection | Medium; needs reliable navigation and shared current-state projection |
| Maintenance | High if graph views duplicate story-state rules | Lowest if UI remains a projection of existing domain owners | Medium if graph remains derived and no parallel state is added |
| Extensibility | Strong for multi-thread/relationship exploration | Strong for linear drafting but spatial work is less expressive | Strongest potential while preserving a single story authority |
| Architectural consequence | Risks making graph/visualization the default interaction owner | Adds no new owner; projection plus progressive disclosure | Adds no semantic owner; composes manuscript, navigator, and read-only graph |

## Selected direction and next boundary

The owner-selected **graph-first Studio** remains the product direction, as
specified in `docs/design/2026-10-09-living-story-studio.md`. The hybrid and
compact concepts are useful interaction compositions and comparison points;
they do not replace the spatial work surface. The documented tradeoffs remain
useful: graph-first supports spatial structure work, compact progressive
disclosure emphasizes current status and next action, and a manuscript/map
composition can bring prose closer to structural context while keeping the map
derived.

The bounded implementation now connects the graph-first Chapter node to the
existing manuscript/review route and restores Book orientation when a saved
Studio canvas is reopened. This is a reversible interaction repair over
existing source-bound Book state, not a second story owner. Further work should
follow observed Browser defects; automated evidence does not establish a
design-quality baseline, human usability, or product readiness.
