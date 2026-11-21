# Atelier author-experience refinement

**Date:** 2026-11-21
**Answers:** [the visual acceptance review](2026-11-21-atelier-acceptance-review.md), PR #628
**Builds on:** [the Living Atlas refinement](2026-11-21-living-atlas-refinement.md), PR #627,
reconciled with PR #629 (see below)
**Visual report:** before and after screenshots, recordings and an owner walkthrough at
https://claude.ai/artifact/AABw84n8jgKCvka8V48LGn. It is private until the owner shares it.
**Status:** experimental and opt-in (`studio.html?atelier`). The default Narrative
Architecture view is unchanged. Making the Atelier the default is a separate owner
decision.

> **Not yet used by an author.** Everything below is verified behaviour, browser
> measurement or reviewer judgement. Author acceptance is still pending.

The direction is unchanged: *A is the world, B is the magnifying glass.* This
refinement does not add a visualization model. It corrects the seven consequential
findings of the acceptance review inside the existing design.

## The seven findings, and what changed

### B1 · The atlas is now the first surface

- **Before:** at 1440×900 the Atelier began 1,224 px down the page, below the Story
  Vision, the agent tools and the written Architecture overview.
- **Now:** while the Atelier is the chosen view, the depth switch and the study move
  directly beneath the workflow switch. The atlas fills the first screen: its stage
  starts at about 254 px and ends above the fixed status bar.
- The Architecture summary, Story Vision, agent tools, canvas tools and written
  overview follow below, unchanged and still usable.
- Every other view keeps the ordinary layout. The Studio without `?atelier` is
  untouched.
- The atlas's own header and caption were compacted to make room.

### B2 · Hover, focus and selection share one rule

- **Cause:** a pointer left on a just-clicked concept kept its hover preview. The
  preview's ring class also forced quiet neighbours' labels on, outside the placement
  engine, so they overlapped. The mouse had to move to clear them.
- **Now:** emphasis follows one precedence: the concept under a pointer that has
  really moved, then what the pointer rests on in the folio, then what keyboard
  navigation (Tab, arrows) reached.
  - Emphasis only rings glyphs, lifts threads and raises one call-out with the
    complete name. It never forces other labels on.
  - Every change of composition or camera suspends pointer emphasis until the pointer
    genuinely moves. Synthetic moves under a still pointer are ignored.
  - Keyboard emphasis resets on every change of composition, so Esc after a mouse
    click returns a clean resting view.
  - The revealed focus is never emphasised again.
- The focus title card now tries every side, and may stand slightly off its mark
  rather than cover a neighbour's.

### B3 · Leaving a dense constellation is smooth

- **Cause:** about 190 background threads were rewritten every frame while each faded
  its own opacity. This was found by switching single rendering features off and
  measuring each one.
- **Now:**
  - Background threads live in one group that dims as a whole and rests during a
    change of composition, then fades back in as the view settles.
  - Paint writes a path, transform or position only when it changes.
  - The constellation's lens moves as a composited transform.
- Plain zooms and pans keep the threads drawn.

### B4 · Meaningful names are readable and never move the stage

- Labels drop a leading kind that only repeats the band ("Trope:", "Theme:",
  "Reader Experience:"). Recorded titles are unchanged, and full titles stay in the
  folio, call-outs and accessible names.
- A kind of idea that the band alone does not tell apart (theme, aesthetic, thread)
  keeps it in the kicker of its title card and call-out.
- Shortened text ends at a word.
- The focus title card shows its whole name, set smaller when long; a slimmer form is
  used in crowded places.
- Relationship pills prefer the whole name, then two lines, then a phrase cut at a
  word.
- Phase names prefer their complete form.
- The caption above the stage has a fixed height, so a 251-character name no longer
  pushes the stage down. A long folio title is set smaller.

### B5 · Genres and Books are readable landmarks

- Story time spreads across a wide stage instead of leaving its right side empty.
- Genres get room for their names: wider spacing, and a first row set below the Book
  headings.
- Book headings show the recorded scope as words: "opening_books_duration_unknown"
  reads "Opening Books", "book_12" reads "Book 12", and "books_13_14" reads
  "Books 13–14". A recorded unknown duration stays in the heading's tooltip and the
  folio.
- A crowded heading takes a second line instead of disappearing.
- The band-name gutter is wider, so counts are not covered.

### B6 · The constellation keeps recorded story order

- Phases the focus is recorded with run in recorded order, left to right, along a
  story-time rail beneath it, as in the atlas. Each name sits directly above or below
  its own phase, never diagonally.
- Other kinds of idea, which have no recorded order, keep to two arcs grouped by kind.
- Nothing is ordered by nearness, and no relationship is added.

### B7 · The phone is usable

- **Gestures:** the stage allows vertical page panning (`touch-action: pan-y
  pinch-zoom`), so a vertical swipe over the atlas scrolls the page.
  - A horizontal drag travels the atlas along story time, including one that begins
    on a concept; a still tap still selects it.
  - Mouse panning is unchanged.
- **Constellation:** on a phone it becomes one list.
  - The focus sits at the top left with its card beside it.
  - Related concepts hang from a single trunk, grouped by kind with phases in story
    order, each pill carrying its relationship's verb.
  - The stage grows to hold the list, so the page scrolls to it, and gives the height
    back on leaving.
- **Layout:**
  - The way back to the atlas sits at the top of a phone stage, clear of the zoom
    buttons.
  - A revealed title card is kept clear of the stage edges and controls.
  - The depth switch is one scrolling row.

## Integrity

All earlier rules still hold:
- only recorded relationships are drawn, each with its `sourceRef`;
- position is never evidence;
- nothing is written to the canvas, candidate or story;
- revealing and following move nothing and keep the zoom;
- leaving a constellation restores positions and zoom exactly;
- the opt-in gate is unchanged, and C stays research-only.

The new rules are:
- presented names only remove a redundant leading kind;
- Book headings only reword the recorded scope;
- the rail orders phases only by recorded `order`.

## Evidence

Source: this branch's final head `1b13a46d`, reconciled with `main@08279f7c` (PR #629). Specimens are the two recorded
agent proposals, not author-owned:
- small: 68 concepts, 82 relationships;
- dense: 156 concepts, 215 relationships.

Machine evidence is in `../qualification-evidence/atelier-author-experience-20261121/`.

### Verified behaviour

**Headless capture at `1b13a46d`, clean tree:**
- every journey invariant holds on both specimens: revealing and following move
  nothing and keep the zoom, leaving a constellation restores positions and zoom, and
  return leaves 0 px drift;
- this holds on desktop, at 390×844, keyboard-only and with reduced motion, with
  0 page errors and 0 rendered label overlaps at every step.

| Dense specimen, 1440×900 | Acceptance review (`6fc59cbf`) | Now (`1b13a46d`) |
|---|---|---|
| Atelier stage starts | 1,344 px down the page | 253 px (first screen) |
| Genres named at rest | 4 of 7 | 7 of 7 |
| Book headings shown | 3 of 7, as raw scope | 7 of 7, as words |
| Landmarks named at rest | 58 of 76 | 66 of 76 |
| Neighbours named on select | 22 of 24 | 22 of 24 |
| Second-order names after deepening | 35 of 60 | 41 of 60 |
| Neighbours named in the constellation | 24 of 24, two cut short | 23 of 24, none cut |
| Constellation phase order | 4, 1, 3, 2 / 9, 7, 6, 5 | 1 to 9, left to right |
| Stage shift for a 251-character name | 21 px | 0 px |

The small specimen names all 31 resting landmarks.

**Served-browser regressions**, in `tests/test_beginner_studio_atelier_experience_browser.py`:
- **Still pointer.** With the pointer left where it clicked, select, deepen and Esc
  leave no call-out, ring, preview or label overlap, measured on rendered geometry.
  Hover works again once the pointer moves, and arrow keys still emphasise.
- **Long name.** A 251-character name moves neither the stage nor the caption.
- **Story order.** The constellation keeps recorded story order.
- **Phone, emulated touch:**
  - a vertical swipe scrolls the page;
  - a horizontal drag travels the atlas;
  - the phone constellation keeps story order;
  - leaving gives the stage its height back.

**Model tests** cover:
- constellation chronology on a wide and a phone stage;
- presented names dropping only redundant kinds;
- Book headings.

**Thread freshness.** After an interrupted leave, rapid re-selection, a resize during
travel, reduced motion, and during zooms and pans, 0 of 215 background threads were
stale. Every thread end lay within 9 px of its mark, and none was left in the travel
state.

### Measured motion

Windowed Chromium, NVIDIA RTX 5060 Ti, 60 Hz, dense specimen, 3 rounds at `1b13a46d`.
Mean / worst frame:

| Step | Before | After |
|---|---|---|
| Leave a constellation | 46–80 / 117–150 ms | **17.0–18.5 / 33–35 ms, 0–3 slow frames** |
| Return to the atlas | 24 / 67 ms | 16.7 / 17–32 ms |
| Examine as a constellation | 27–35 / 67–100 ms | 21.7–23.0 / 35–50 ms |
| Select a concept | 21–28 / 50–183 ms | 17.2–21.1 / 34–100 ms |

For comparison, PR #629's own windowed measurement on the same host reported 33–38 ms
mean (100 ms worst) for leaving a constellation.

The small specimen holds 60 fps at every step.

The diagnosis disabled one rendering feature at a time; its results are in
`live-frame-times.json`. Hiding the background threads alone brought leaving a
constellation to 17.9 ms. Removing star layers, dashes or text shadows changed little.

## Independent review

A second read-only reviewer that did not build the Atelier tested the served Studio at
1440×900, 1280×800 and phone width, with mouse, keyboard and emulated touch.

**Its verdict on the seven findings:**
- resolved: atlas first, lingering hover, the dense return (seen headless) and story
  order;
- partly resolved: names and landmarks, because cuts and Roman-numeral phases remain at
  1280 and Book headings are staggered;
- phone: resolved, but with new problems.

**Consequential findings, all reproduced and fixed:**
- the focus title card hid neighbours' names, and after deepening its own mark;
- a deepened constellation pushed four direct relatives off the stage;
- on a phone, entering or leaving a constellation left the stage out of view;
- a sideways swipe slid the phone list away.

**Smaller items fixed:** the folio kept its scroll on a new focus; the phone caption
showed part of a third line; a phone drag could run past the story's ends.

**Left as polish:**
- staggered Book headings;
- neighbour pills over faded band labels;
- labels that re-place when deepening.

## Reconciliation with PR #629

PR #629 addressed the same seven findings independently and reached `main` while this
work was being built. The two cannot simply stack. They implement atlas-first, hover
release, the return transition, Book headings, names and phone gestures in different
ways, and an automatic merge duplicated functions and mechanisms. The integrated Atelier
is reconstructed on current `main`.

**Kept from this refinement, where both solved the same problem:**
- atlas first by moving the study in the document, so reading and Tab order match what
  is seen, rather than reordering with CSS;
- one emphasis precedence with a pointer latch;
- background threads resting as one group, measured at about 17 ms per frame against
  PR #629's 33–38 ms when leaving a dense constellation;
- the story-time rail;
- the phone list constellation and gesture model;
- scored card placement;
- the fixed-height caption.

**Adopted from PR #629:**
- presentation titles without a redundant kind everywhere, including the folio and
  accessible names, with the recorded title kept as `recordTitle`;
- `bookLabel` as the running-head string, with the worded scope moved to `bookScope`;
- every genre among the folio's landmarks;
- no bare Roman-numeral phase names;
- no repeated kind in the card kicker;
- stronger resting priority for genres and phases;
- Esc at rest releasing a hover preview;
- a safe edge inset and larger phone focus margins;
- smaller Book running heads;
- the `--windowed` capture flag.

**PR #629's tests were kept.** Two assertions that named its implementation now check
the behaviour instead:
- the `.workspace.atelier-first` class became "the atlas precedes the Story Vision in
  document order";
- touch-action exactly `pan-y` became "`pan-y` is allowed".

They exposed two real gaps, both fixed:
- the first pointer movement of a session now counts as real travel;
- a phone title card never covers the trail or leaves the stage.

## Limitations

- **No author has used it.** Every judgement here comes from measurements, tests, the
  builder and an independent reviewer.
- **Density:**
  - At rest, 10 of 76 dense landmarks stay unnamed and are named on hover and in the
    folio. Most tropes and engines are unlabelled marks by design.
  - At 1280×800 the dense atlas names fewer landmarks, and a crowded phase name may be
    shortened (never a bare numeral).
- **Crowding:**
  - In the densest columns, stacked neighbours can stay unnamed; the selected engine
    loses two of ten.
  - After deepening the densest genre, its title card can cover one faint second-order
    mark rather than move.
- **Motion:** opening a dense constellation runs at about 42–45 fps with a few slow
  frames. Everything else is about 60 fps on the measured machine.
- **Not tested:** a real phone (touch was emulated through Chrome's input pipeline), a
  screen reader, pinch-zoom of the atlas itself (pinch zooms the page), and Architectures
  over 156 concepts.
- **Phone constellation:** its verbs are cut when a neighbour has several
  relationships; the folio lists them all with their reasons.

## Recommendation

Ready for the owner's acceptance session on desktop and phone. Making the Atelier the
default Narrative Architecture view remains a separate owner decision, made after
direct use.
