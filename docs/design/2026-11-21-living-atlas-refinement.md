# The Living Atlas, with an optional Focused Constellation

**Date:** 2026-11-21
**Builds on:** [the first Atelier study](2026-11-20-living-narrative-atelier-study.md) (PR #627)
**Base:** `main@f6ab6de0`, unchanged since the first study
**Status:** experimental, opt-in (`studio.html?atelier`), presentation only. It is
not the default Narrative Architecture experience. Making it the default needs a
separate owner decision.

> **Corrected by the [acceptance review](2026-11-21-atelier-acceptance-review.md)**
> (same day). Several claims below hold only under the capture's conditions:
> - "0 overlaps" assumes the pointer is away. Right after a click or `Esc`, the hover
>   preview forces names that overlap.
> - "58 of 76 landmarks" excludes unlabelled marks. 59 of 156 concepts are named at
>   rest.
> - "Nothing moves" holds inside the stage. A paragraph-length name can push the whole
>   stage down 21 px.
> - Only three Book headings show at rest.
> - Leaving a dense constellation runs at about 20 fps on real hardware too.

## Owner direction

The owner reviewed the first study and set this direction:

- **A, Progressive revelation, is the primary Living Atlas.**
- **B, Spatial choreography, becomes an optional Focused Constellation** that the
  author opens deliberately to study one concept.
- **C, Contextual unfolding, is deprioritised.**
- The first study's recommendation (switch automatically between A and B by
  density) is **not** implemented.

In short: *A is the world, B is the magnifying glass.* The goal is to make
narrative complexity beautiful and legible, not to reduce density.

## What changed

### The resting atlas

The first atlas named only genres and phase numerals at the whole-story view,
and genre names were truncated (`Institut…`). Everything else was an unlabelled
glyph until it was selected. The atlas is now readable before any selection.

- **Measured labelling around fixed glyphs.** Every label is measured with the
  font it will be set in. It is then placed in one of eight positions around its
  glyph, most important labels first. A label that would overprint another
  label, a glyph or the stage furniture stays **quiet**: its glyph remains, and
  hover, keyboard focus or the folio names it. Glyphs never move to make room.
  This is the pure `placeLabels` function in `studio_atelier_model.js`.
- **Hierarchy.** Kind of idea sets a label's typographic voice: serif genres,
  serif phase names, compact sans for the rest. Priority within a kind follows
  the count of documented relationships, a recorded fact. Glyph size follows the
  same count, and the folio legend says so.
- **Interconnection.** Every recorded relationship is drawn at rest as a quiet
  thread. A thread leaves and enters its concepts vertically and is coloured by
  the kind of idea it reaches, so the score reads as warp threads between bands
  rather than as a tangle. Relationships within a band arc above it.
- **Story-time structure.** Each phase has a hairline that runs through every
  band. Alternate Books are lightly shaded, and each Book is named once as a
  running head above the score.
- **Spacing for the first reading.** The layout is still deterministic and is
  still computed once per Architecture. Its row spacing is now chosen so that
  names have room at the whole-story zoom of the stage it is first opened on. On
  a phone the score fits the stage height and the author travels along story
  time. Nothing in the layout changes while exploring.
- **Folio.** At rest it shows the story summary, the most connected landmarks of
  each kind (by documented relationships), how to read the atlas, and the ways
  of looking.

### Progressive revelation (A)

- **Positions and zoom are kept.** The camera pans only when the focus itself
  would be unreadable at an edge. It never zooms out because a neighbourhood is
  large. The first study's A re-framed every neighbourhood.
- **Rest → focus → reveal → deepen → settle → return.**
  - The focus wears a title card.
  - Neighbours come forward as tinted name pills in the order of their kind,
    with their threads growing from the focus.
  - The rest of the story stays visible underneath, at lower contrast, still
    named wherever there is room.
  - Deepening adds second-order names in a quieter style.
  - Relationship verbs are set along their own threads once motion settles.
  - Return restores the resting hierarchy and marks the concept just left.
- **Distant relationships.** When the author has zoomed in, an edge pin
  (`→ 16 related`) appears for neighbours beyond the stage and brings them into
  view on request. ◎ fits the whole neighbourhood explicitly.

### Focused Constellation (B)

- **Opened deliberately**, never automatically: *Examine as constellation* in the
  folio, the bar's *Focused constellation* button, or the `E` key.
- It recomposes the selected neighbourhood into B's balanced oriented arcs at
  reading scale. The atlas withdraws behind a soft lens, and dotted tethers mark
  each concept's atlas place.
- Following a relationship inside the constellation recomposes around the new
  concept. *Back to the atlas* (or `Esc`) restores the atlas view the author
  left. A second `Esc` returns to the whole atlas.
- It stays distinct from **Focused Unfolding**, the creative-suggestion
  workflow. The constellation proposes nothing, and the folio says so beside
  both actions.

### Research treatment C

C is reachable only with `?atelier=C`, which adds a *C · research* button to the
bar. It is kept for comparison with the first study's evidence. It is not
offered to authors and was not developed further.

## Integrity

The first study's rules all still hold:

- Only recorded relationships are drawn.
- Each relationship keeps its `sourceRef`.
- Position is never evidence.
- No canvas, candidate or story writes.

This refinement adds three rules:

- Glyph size and label priority come only from the count of documented
  relationships and from a concept's kind.
- Thread colour names the kind of idea a relationship reaches. It never encodes
  strength or causality.
- The constellation rearranges only the recorded neighbourhood, for reading.

## Evidence

All measurements come from `atelier_study_capture.py`, run in headless Chromium
against the served Studio at source head `789f5772` with a clean tree, on the
same two recorded specimens:

- small: 68 concepts, 82 relationships;
- dense 14-Book series: 156 concepts, 215 relationships.

Manifest: `docs/qualification-evidence/atelier-refinement-20261121/metrics.json`.

| Dense specimen, 1440×900 | First study A | Refined A | Refined B (constellation) |
|---|---|---|---|
| Resting landmarks named at the whole-story view | genres (truncated) and phase numerals only | 58 of 76 | — |
| Neighbours named on select | 14 of 24 | 22 of 24 | 24 of 24 |
| Second-order names after deepening | about 27 of 60 | 35 of 60 | — |
| Relationship verbs shown | 10 of 32 | 12 of 32 | 16 of 32 |
| Camera on select | re-framed (zoom 0.35) | unchanged | composed at reading scale |
| Concepts moved | 0 | 0 | 24 |
| Rendered label overlaps | 0 | 0 | 0 |
| Settle after select | 1230 ms | 1426 ms | 1081 ms |

On the small specimen, the refined A names 30 of 31 resting landmarks and all
15 neighbours of *Literary mystery*, with nothing moved. On a 390×844 phone, A
names the neighbours on the stage and pins 16 more to the edge; B names 11 of 13.

Invariants checked by the capture on both specimens:

- Revealing, deepening and following relationships never move a concept (0 px).
- Selecting never changes the zoom.
- Leaving a constellation restores the atlas positions and zoom.
- Returning to the atlas leaves 0 px drift and an identical camera, on desktop,
  on a phone, by keyboard only, and with the operating-system reduced-motion
  preference. Under that preference every step settles in 0 frames.

Keyboard-only run: Tab into the atlas, then arrows, `Enter`, `]`, `E`, `Esc`,
`Esc`. Focus stays on the concept throughout. No page errors were recorded.

## Assessment against the brief's questions

- **Resting beauty and density.** The atlas now looks like an interconnected
  world before anything is selected: named landmarks, woven threads, story-time
  meridians and Books. About a quarter of resting landmarks in the dense
  specimen stay quiet; they are named on hover and in the folio and index.
- **Spatial familiarity.** Nothing in A ever moves, and the view is kept, so the
  map the author learns at rest remains the map they explore. B always returns
  to it.
- **Progressive revelation.** Relationships come forward in place and the rest
  of the story stays legible behind them. In a dense neighbourhood, neighbours
  spread across the whole score. A shows *where* they belong; reading them
  side by side is harder.
- **Focused analysis.** B's advantage is real in dense neighbourhoods. It names
  every neighbour and shows half again as many verbs, in one compact reading
  frame. For a small neighbourhood, A already shows everything in context and B
  adds little. That suits an optional mode that is never automatic.
- **Functional integrity.** The study is still opt-in, read-only and reversible.
  The default Studio is unchanged; a browser test pins that.

## Limitations and unverified claims

- **No author has used this.** Every judgement here comes from screenshots,
  recordings, measured behaviour and the builder's own review.
- **Layout and viewport.** Label spacing depends on the stage size when the
  Architecture is first drawn. A very different window later keeps the first
  layout and only refits the camera.
- **Dense neighbourhoods.** Two of 24 neighbours of the densest genre stay quiet
  in A. After deepening, 25 of 60 second-order names stay quiet. Only about a
  third of verbs fit in A; the folio lists every relationship with its reason.
- **Performance.** Frame times are from headless Chromium with software
  rendering. Most steps average 17–24 ms. The first frame of a dense reveal takes
  up to 67 ms. Leaving a dense constellation is the costliest step, averaging
  about 40 ms with a worst frame of about 117 ms, because the camera zooms out
  over the whole score. Two cheap fixes were tried and measured; neither helped,
  and both were reverted. *Update, same day:* the
  [acceptance review](2026-11-21-atelier-acceptance-review.md) measured it on real
  hardware in a windowed browser. Leaving a dense constellation runs at about 20 fps
  there too, and the cost is rasterization and style work, not script.
- **Not tested.** Screen reader, touch pinch-zoom, and Architectures larger than
  156 concepts.

## Recommendation

The refined A plus an optional B realises the owner's preferred experience
convincingly enough to put in front of real authors. That is the next decision
that matters, and it needs real author sessions.

If it holds up, the experimental atlas could replace the category grid in the
Overview, with B as a named tool. That promotion is an owner decision. The
simplest path keeps A alone, which already carries most of the gain.
