# The Living Narrative Atelier: a visual unfolding study

**Date:** 2026-11-20
**Base:** `main@f6ab6de0`
**Status:** experimental, opt-in, presentation only. It is not the default
Narrative Architecture experience, and promoting any treatment needs a separate
owner decision.

> **Superseded in part (2026-11-21).** After reviewing this study, the owner made
> A the primary Living Atlas and B an optional Focused Constellation, and
> deprioritised C. The adaptive A/B recommendation below was **not** adopted. See
> [the refinement](2026-11-21-living-atlas-refinement.md). This document keeps the
> first comparison as research evidence. Its URL forms (`?atelier=A|B`) now open
> the living atlas; `?atelier=C` opens the research comparison.

The study asks how Auteur can make a working Narrative Architecture beautiful
and intellectually rewarding to explore. It is built from a stable global atlas
and a living local constellation, and it compares three ways to unfold a
concept:

- **A — Progressive revelation:** nothing moves; relationships are revealed in place.
- **B — Spatial choreography:** the neighbourhood is recomposed into a balanced constellation.
- **C — Contextual unfolding:** relationships are revealed first; then only the neighbours whose place hurts reading move closer.

All three run inside the served Studio on genuine, schema-validated Architecture
candidates. Each specimen gives every treatment the same task.

## Open it

The study is enabled only by URL: `studio.html?atelier=C` (or `=A`, `=B`, or
`=1` for C). Without the flag, the Studio is unchanged: the Atelier button and
surface stay hidden. A browser test pins this.

With the flag, the Architecture Overview gains a third depth mode, **Atelier
study (experimental)**, beside Focused Unfolding and Full Architecture. The mode
replaces only the graph surface, and the facet rail, reader and tools remain.
Optional URL parameters `focus=<concept id>` and `depth=2` open a constellation
directly, which keeps evidence reproducible.

To reproduce the study, seed a disposable project with two recorded candidates.
The seed script uses the same host-agent request and completion path the Studio
uses, so both candidates are schema-validated:

```bash
PYTHONPATH=src python scripts/seed_atelier_study.py --project <disposable dir>
PYTHONPATH=src python -m auteur.beginner.server --project <disposable dir> --port 8793
python scripts/qualification/atelier_study_capture.py --out <dir> --video
```

| Specimen | Source (recorded agent output) | Atlas |
|---|---|---|
| small | `docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json` | 68 concepts, 82 relationships, 4 phases |
| dense, 14-Book series | `qualification/studio-trace/artifacts/candidate-2.json` | 156 concepts, 215 relationships, 9 phases |

Nothing illustrative was invented. The study reads what each candidate records.

## What was built

| File | Role |
|---|---|
| `studio_atelier_model.js` | Pure model, atlas layout, neighbourhoods, the three compositions, study measures |
| `studio_atelier.js` | Stage, persistent stars and paths, motion engine, folio, keyboard, study readout |
| `studio_atelier.css` | Visual language |
| `studio.js`, `studio.html`, `server.py`, `studio_full_architecture_controller.js` | Opt-in mode, asset registration, mode isolation |
| `scripts/seed_atelier_study.py`, `scripts/qualification/atelier_study_capture.py` | Reproducible specimens and machine-generated evidence |

There are no backend, schema or ontology changes. The only server change is the
allowlist entry for the three new assets.

### Narrative meaning comes only from recorded sources

- **Concepts.** Concepts are the entries of the existing source-qualified
  explanation packet (`AuteurStudioExplanations.project`): genres, reader
  emotions, tropes, structure and phases. The study adds two kinds of recorded
  item the packet omits: complex emotions, and nodes outside the five facets
  (themes, aesthetics, threads, other).
- **Relationships.** Relationships are the packet's links plus recorded fields
  the packet does not express: `complex_emotion_ids`, `parent_id`,
  `parallel_with`, and candidate links that touch an uncovered node.
  - Every relationship carries its `sourceRef`. A unit test resolves each one
    against the candidate, on both specimens.
  - Compositions never add a relationship, and a test asserts this.
- **Reverse verbs.** The study inverts only the explanation contract's own
  fixed verbs (for example, "targets reader emotion" becomes "targeted by").
  Agent-written link text keeps the contract's neutral "related through “…”".
- **Local phrases.** Phrases recorded inside a genre or phase without an
  identity of their own stay distinct entries. The folio says so: equal wording
  elsewhere is not assumed to be the same idea.
- **Provenance.** The study ribbon says throughout that positions are
  presentation, never narrative evidence. Every reading shows "Agent proposal ·
  not accepted story", its source path and its request.

## Design rationale

### Visual language

- **Paper and type.** The stage is ivory paper with a soft vignette. Titles use
  an editorial serif (Iowan Old Style or Palatino, then Georgia), and labels
  and kickers use the system sans.
- **Semantic hues.** The Studio's existing semantic colours are refined, never
  replaced: genre violet, emotion rose, trope ochre, structure teal, story-time
  slate, and sage for themes, aesthetics and threads.
- **Shape as well as colour.** Each kind of idea has its own glyph: a diamond
  for genres, a dot for emotions, a lozenge for tropes, a square for structure,
  a ring station for phases, and a hollow ring for other ideas.
- **Proposals stay dashed.** Highlighted relationship paths keep the Studio's
  "dashed = proposed" convention, with small open arrowheads in the hue of the
  related kind.
- **Atlas versus constellation.** At rest the atlas is quiet: hairline paths
  at 16 % opacity, small glyphs and short labels. A constellation is louder: the
  focus becomes a small card with a kicker and serif title, and neighbours
  become tinted chips.

### Composition

- **The atlas is a narrative score.**
  - Bands, top to bottom: genres, reader emotions, story time, tropes,
    structure, and themes/aesthetics/threads.
  - Phases sit on a spine in recorded order, grouped under their Book or scope
    brackets.
  - A concept's horizontal place follows the phases it is recorded with,
    directly or through its genre or owning phase.
  - Rows are spread by isotonic regression, which minimises total displacement
    while enforcing label room.
  - Local phrases gather in small sunflower clouds beneath their phase or genre.
  - The layout is deterministic (tested) and computed once per Architecture.
    Selection never changes it.
- **Semantic zoom.** Spacing scales with zoom but type does not, so labels stay
  legible and shorten to the room they have. Far away, only genres and phase
  numerals speak, and Book names never overprint one another.
- **Compositions are designed in screen pixels at reading scale.**
  - B and C use two balanced arcs, one either side of the focus. Each neighbour
    keeps its side of the map (west or east) and its vertical order, so the
    constellation stays oriented to the atlas.
  - Second-order concepts form outer arcs ordered by their first-order parent.
  - Moved concepts keep a dotted tether to a small ring at their home.
  - On narrow screens the arcs become a single oriented stem under the focus
    title.
- **One collision etiquette for all treatments.** A label that would overprint
  another goes quiet: its glyph stays, and hover or keyboard focus reveals the
  label. The folio lists every relationship regardless.

### Motion

| | A | B | C |
|---|---|---|---|
| Focus emphasis | 340 ms glyph scale and halo | same | same |
| Neighbours appear | staggered 30 ms by kind of idea | staggered 16 ms | staggered 26 ms |
| Paths grow from the focus | 460 ms | 560 ms | 460 ms |
| Neighbours travel | none | 780 ms, 14 ms stagger | after a 420 ms beat, 660 ms |
| Camera | only if the neighbourhood is off-view | to reading scale | to reading scale, with the moves |
| Return | paths fade back to the atlas; everything glides home in 560 ms; camera returns to the exact resting view | same | same |

- **Easing and verbs.** Moves ease in and out (cubic); reveals decelerate. Zoom
  interpolates geometrically. Relationship verbs wait until the composition has
  settled, then fade in only where they fit.
- **Stillness after settling.** There are no loops, pulses, particles or
  bounce. The animation engine stops once everything has settled, and nothing
  moves while the author reads.
- **Reduced motion.** An operating-system preference gets the Studio's own
  no-transition rule. The in-study toggle keeps 120 ms cross-fades. Either way
  nothing travels: positions, camera and paths change in one frame.

### The folio: editorial reading beside the constellation

- **At rest.** The folio shows the Architecture's summary, how to read the atlas
  (including that nearness is never a relationship), a lens per kind of idea,
  the study task, and a complete atlas index. The index is also the
  linear-access equivalent of the map.
- **Focused.** It shows the kicker, title, recorded fields and coverage notice.
  The fields depend on the kind of idea:
  - genre: engine, pattern, payoffs and aesthetics;
  - emotion: intended effect, eliciting condition, strategy and provenance;
  - phase: place in story order (not a chapter count), scope, function and
    reader experience.
- **Relationships.** Documented relationships are grouped by kind of idea. Each
  shows its verb and target, and its recorded reason (mechanism or risk), which
  is also announced with the button. Hovering or focusing a row lights its path
  and its neighbour on the stage.
- **Deeper and source.** A deeper-connections control appears, and the source
  record lists every recorded field.
- **Actions** reuse existing Studio surfaces:
  - **Open in Studio inspector**, the real source-bound inspector;
  - **Read the full explanation**, the existing facet explanation, from which
    the facet trail returns to the study where you left it;
  - **Develop new possibilities (Focused Unfolding)**, which opens the separate,
    author-governed creative-suggestion workflow.

  The study only reveals what is recorded. It never proposes, adopts or saves.

### Accessibility

- **Keyboard.** The atlas uses a roving tab stop. Arrow keys move spatially to
  the nearest concept in that direction, Enter unfolds, `]` and `[` change
  depth, Backspace steps back along the trail, and Esc returns to the atlas
  with keyboard focus kept on the same concept.
- **Labels and announcements.** Each star's accessible name gives its kind,
  title, number of documented relationships and proposal status. A polite live
  region announces each unfolding, including how many concepts moved, and each
  return.
- **Verified here:** keyboard paths, by script and in the browser pane, and
  reduced motion, by both the operating-system preference and the toggle.
- **Not verified:** a real screen reader and touch pinch-zoom. Zoom is by
  buttons or ctrl/⌘-wheel.

## Evidence

`docs/qualification-evidence/atelier-study-20261120/metrics.json` is generated
by `atelier_study_capture.py` against the served Studio in headless Chromium,
from source head `c85d6e67` with a clean source tree. It holds 12
runs with 0 page errors. These are machine measurements, not a
human usability evaluation. Screenshots of all seven task steps and recordings
of the dense walk for A, B and C were captured with the same script and are
published outside the repository, because no binary evidence is committed here.

Unfolding the task's genre (small: *Literary mystery*; dense: *Institutional
certification procedural*):

| viewport | specimen | treatment | first-order | moved | mean travel px | quiet labels | quiet at depth 2 | verbs shown | mean reach px | settle ms | frame mean/worst ms | return drift | camera restored |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| desktop | small | A | 15 | 0 | 0 | 5 | 34 | 4/20 | 456 | 992 | 17.9/50 | 0 | yes |
| desktop | small | B | 15 | 15 | 395 | 0 | 0 | 6/20 | 196 | 998 | 17.5/50 | 0 | yes |
| desktop | small | C | 15 | 9 | 515 | 0 | 0 | 9/20 | 218 | 1313 | 17.1/50.1 | 0 | yes |
| desktop | dense | A | 24 | 0 | 0 | 10 | 33 | 10/32 | 907 | 1230 | 22.8/50 | 0 | yes |
| desktop | dense | B | 24 | 24 | 823 | 0 | 0 | 9/32 | 210 | 1061 | 26.7/50 | 0 | yes |
| desktop | dense | C | 24 | 20 | 939 | 0 | 0 | 9/32 | 220 | 1363 | 24/50 | 0 | yes |
| narrow | small | B | 15 | 15 | 421 | 0 | 0 | 0/20 | 330 | 1001 | 17.2/33.4 | 0 | yes |
| narrow | small | C | 15 | 15 | 421 | 0 | 0 | 0/20 | 330 | 1303 | 16.7/16.8 | 0 | yes |
| narrow | dense | A | 24 | 0 | 0 | 10 | 33 | 10/32 | 907 | 1222 | 21.8/50 | 0 | yes |
| narrow | dense | B | 24 | 24 | 762 | 0 | 0 | 0/32 | 450 | 1053 | 24.6/33.4 | 0 | yes |
| narrow | dense | C | 24 | 24 | 762 | 0 | 0 | 0/32 | 450 | 1353 | 21.2/50.1 | 0 | yes |
| desktop, reduced motion | dense | C | 24 | 20 | 939 | 0 | 0 | 9/32 | 220 | 32 | 0/0 | 0 | yes |

- **Travel and reach** are in world pixels at reading scale. *Reach* is the
  distance from the focus to a first-order neighbour. *Settle* runs from the
  click to the last frame.
- **Frame times** were measured in software-rendered headless Chromium. A GPU
  browser should do better, but that was not measured.

## Comparative assessment

**A — Progressive revelation.**
- **Strengths:**
  - The calmest and most continuous treatment: nothing moves, so the atlas is
    the constellation.
  - The simplest to maintain.
  - On the small Architecture it reads well: 5 quieted labels, and the folio
    carries the rest.
- **Weaknesses:**
  - In a dense, multi-Book Architecture a governing genre's neighbours span the
    whole score (mean reach 907 px). The camera must pull back to about 0.35, so
    10 of 24 first-order labels and 33 or 34 second-order labels must go quiet.
  - In A, the paths explain more than the labels do.
  - The focus card can also sit over neighbours that happen to be near it,
    because A cannot move anything aside.

**B — Spatial choreography.**
- **Strengths:**
  - The clearest constellations at every density: no quieted labels at depth 1
    or 2, and neighbours within about 200 px of the focus.
  - The most balanced composition, and the strongest feeling that the
    Architecture is alive.
- **Weaknesses:**
  - It moves every neighbour, a mean of 395 px in the small specimen and 823 px
    in the dense one.
  - Orientation then rests on the tethers, the home rings and the kept
    west/east order.
  - Following a relationship reshuffles the whole neighbourhood each time. The
    recordings make this the most "eventful" treatment, and sustained use may
    tire. That was not measured with people.

**C — Contextual unfolding.**
- **Strengths:**
  - On the small Architecture it does what it promises: 6 of 15 neighbours stay
    in their atlas place, 9 come closer, no label goes quiet, and it shows the
    most relationship verbs (9 of 20).
  - It is the best balance of continuity and reading at that density.
- **Weaknesses:**
  - On the dense Architecture its selectivity collapses: 20 of 24 neighbours are
    far away or crowded, so C becomes B with a mixed layout and a 300 ms longer
    two-beat sequence.
  - The kept-plus-arc mixture is less visually unified than B's arcs.
  - The neighbours it does move travel the farthest, because they are the
    distant ones.
  - On narrow screens C and B produce the same stem.

**All three:**
- Return is exact (0 px drift, camera restored).
- Keyboard and reduced-motion behaviour is the same.
- Relationship verbs are hidden on narrow screens, where the stem leaves them no
  room. The folio still states every one.
- Performance is comparable. Dense paints are costlier because every frame
  repaints 156 stars and 215 paths.

## Recommendation

Develop **C's intent with an adaptive rule**, informed by both A and B rather
than C exactly as built.

1. **Reveal in place first.** Unfold in place as A does whenever the
   neighbourhood is legible in the current view, measured as no quieted
   first-order labels and every neighbour within view at a readable zoom.
2. **Otherwise compose.** When it is not legible, compose the whole
   neighbourhood with B's oriented arcs, tethers and home rings, rather than C's
   per-neighbour mixture.

**Why:**
- The measurements show that C's per-neighbour rule mostly behaves like A on
  small neighbourhoods and like B on dense ones.
- Its mixed middle ground is its least convincing state.
- A whole-neighbourhood decision keeps A's calm where it suffices, and gives
  B's clarity where it is needed.

**The atlas, folio and source-bound reading are the larger win.** They are
independent of the treatment, and on their own with A they are a substantial,
low-complexity improvement. If only one step is taken next, take that one and
keep the treatment behind the flag.

## Uncertainties and unfinished work

- **No human evaluation.** Aesthetic and comprehension judgements here come from
  rendered screenshots, recordings, interactive use in the browser pane and
  machine measures. The comfort of motion under sustained use, the risk of
  disorientation in B, and whether the atlas metaphor helps authors all need
  real authors.
- **The adaptive rule above was not built or measured.** It is a hypothesis the
  evidence suggests.
- **Density beyond the specimen is untested.** The dense specimen has 156
  concepts. The candidate limit (80 nodes, 180 links, 32 phases) can produce
  roughly twice that, which has not been tried.
- **Depth 2 in a dense Architecture overflows the stage.** The outer arcs need
  panning.
- **Screen reader and touch are unverified.** No real screen reader was used,
  and there is no pinch-zoom for touch (buttons and ctrl/⌘-wheel only).
- **Layout timing.** The atlas is laid out once per Architecture and is not
  re-laid-out on resize, by design for stability. Its vertical rhythm follows
  the stage proportions at first display.
