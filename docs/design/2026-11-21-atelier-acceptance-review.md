# Living Narrative Atelier: visual acceptance review

**Date:** 2026-11-21
**Reviews:** [the Living Atlas refinement](2026-11-21-living-atlas-refinement.md), merged in PR #627
**Source:** `origin/main@6fc59cbf`, served from the tree-identical `c5f09a30`
**Status:** review only. The Atelier stays experimental and opt-in (`studio.html?atelier`).
**Visual report:** screenshots, recordings and this walkthrough at
https://claude.ai/artifact/CvWiHNR7Umr1i9SccYTP9q. It is private until the owner shares it.

> **No author has used the Atelier yet.** This review records verified behaviour,
> browser measurements, the reviewer's judgement and one independent critique. Author
> acceptance is still pending. The exercise below is how to obtain it.

## Question

Does the actual author experience convincingly realise the intended Living Narrative
Atelier, where A is the world and B is the magnifying glass? Is it ready for author
evaluation and, later, a default-UI decision?

## Environment

- **Served Studio.** A disposable project was seeded with `scripts/seed_atelier_study.py`
  (the command in the exercise below) and served by `python -m auteur.beginner.server` on
  port 8793. The served `studio_atelier.js` hash matched the file at `c5f09a30`.
- **Specimens.** Both are recorded agent proposals kept in the repository as
  qualification evidence. Neither is author-owned or accepted story, and no author-owned
  Architecture was available.
  - small: a literary mystery, 68 concepts and 82 relationships;
  - dense: a fourteen-Book series, 156 concepts and 215 relationships.
- **Hands-on review** in the Claude desktop browser pane at 1440×900, with real clicks
  and keys.
- **Captures.** `atelier_study_capture.py` in headless Chromium at 1440×900 and 390×844,
  with recordings. Manifest: `../qualification-evidence/atelier-acceptance-20261121/capture-metrics.json`.
- **Live motion.** A normal windowed Chromium on this machine's GPU (NVIDIA RTX 5060 Ti,
  60 Hz). The pane's own timings were discarded: while the pane was hidden it was
  throttled to about one frame per second. Measurements:
  `../qualification-evidence/atelier-acceptance-20261121/live-frame-times.json`.
- **Independent critique** by a separate read-only reviewer that did not build the
  Atelier. Summarised below.

## Verified behaviour

- `origin/main` has not changed since the merge, and no open PR touches the Atelier.
- Without `?atelier`, the Studio has no Atelier button or section.
- The capture reproduced the recorded baseline exactly:
  - dense: 58 of 76 resting landmarks named, 22 of 24 neighbours named, 35 of 60
    second-order names after deepening, and 24 of 24 in the constellation;
  - every invariant held: revealing, deepening and following move nothing and keep the
    zoom, leaving B restores positions and zoom, and return leaves 0 px drift with the
    same camera;
  - this held on desktop, at phone width, keyboard-only and with reduced motion (0
    frames), with 0 page errors.
- Both canvases stayed at revision 1 throughout, and their files were never rewritten.
- Real mouse clicks never scrolled the page.
- Keyboard access:
  - the atlas has one tab stop, with arrow keys moving between concepts;
  - concepts announce their kind, relationship count and status;
  - a polite live region reports each reveal.
- **Not done:** no screen reader, touch device or pinch-zoom was used.

## Assessment

### Resting atlas (Journey A)

**What works.**
- It has a recognisable literary identity: paper ground, serif genres and phases,
  small-caps bands, hairline meridians.
- Story progression is legible along the named phase spine.
- The converging threads make the dense story read as one connected world before any
  click.
- On the small Architecture every phase and nearly every landmark is named in full.

**What is weak.**
- Only 59 of 156 dense concepts carry a name at rest (38%). By design, 42 of 48 tropes
  and 38 of 53 structure entries are unlabelled marks. The refinement's "58 of 76
  landmarks" is accurate but excludes those marks.
- Three of seven genres are unnamed at rest, one of them with 18 relationships, while
  21 of 25 reader-emotion entries are named. The folio lists only the top three genres.
- Long names end in "…", including the first phase.
- Book headings show raw data ("OPENING BOOKS DURATION UNKNOWN").

### Progressive revelation (Journey B)

**What works.**
- The focus is unmistakable.
- Relationships read as verbs on their own threads.
- Nothing moves, and the view is kept.
- The screen is still once settled.

**What is weak.**
- The focus's own engine and structural pattern appear as two words in A.
- Two phase neighbours get an arrow but no name.
- Deepening cuts sentence-length names mid-word, and does not show which first-order
  neighbour leads to each second-order name.

### Long-horizon discovery (Journey C)

Following the record across phases works. The trail and stable positions make
returning easy, and zooming in gives names room. The atlas can prompt real creative
questions. For example, *Evidence inquiry* is active only in phases 2 and 8, so what
carries inquiry between them?

The atlas shows *that* and *where*. The folio gives the recorded reason. Absence is
correctly never presented as evidence.

### Focused Constellation (Journey D)

**Where it helps.**
- For dense neighbourhoods, B earns its place. Every neighbour is named in a scannable
  frame, which is easier than tracing 24 threads.
- Its purpose is clearly stated, and it is kept apart from Focused Unfolding.
- Return is exact.

**Where it falls short.**
- Verbs knot where the spokes converge.
- Tethers fan out to an atlas that has faded away.
- For small neighbourhoods it adds little, because A already names everything in place.

### Phone, keyboard and motion (Journey E)

**Phone.**
- A starts at a reading zoom and pins off-stage neighbours to the edge.
- B becomes one long column, and its threads bunch into a hatched band.

**Live motion on real hardware.** Three rounds per step, mean and worst frame:

| Step | Small | Dense | Dense frames over 33 ms |
|---|---|---|---|
| Select (A) | 17–19 / 33–67 ms | 21–28 / 50–183 ms | 4–8 of ~70 |
| Reveal deeper | 16.7 / 17 ms | 16.7–17.3 / 17–50 ms | 0–1 of ~108 |
| Follow | 17 / 33 ms | 20–21 / 33–83 ms | 3–6 of ~57 |
| Examine (B) | 17–18 / 33 ms | 27–28 / 67–83 ms | 10 of ~44 |
| Leave B | 17 / 17–33 ms | **46–51 / 117–150 ms** | **7–9 of ~19** |
| Return | 16.7 / 17 ms | 24 / 67 ms | 4–6 of ~34 |

**The slow return from a dense constellation is real on real hardware**, not a
headless artefact. It runs at about 20 fps for about 0.75 s.

A Chromium trace shows where the time goes:
- the page's JavaScript costs 1–3 ms per frame;
- about 440 ms is rasterization while the camera zooms out over all 215 threads;
- about 140 ms is style recalculation across 156 concepts, each on its own compositing
  layer (`will-change: transform`).

This points to a contained rendering fix.

## Independent critique

A separate read-only reviewer explored the served Studio on its own: both specimens at
1440×900 and 390×844, by mouse, keyboard and emulated touch. It was asked to challenge
the builder's claims and was not shown this review's findings. Every claim it added was
re-checked here before being recorded.

**Where it agreed.**
- The identity is real; it reads like "an annotated score", not a generic graph.
- The small specimen is calm and readable at rest.
- Positions are stable through select, follow, the trail and `Esc`.
- Following distant links is satisfying.
- B is the clearest reading view of a dense neighbourhood.

**What it found that this review had missed.** All verified.
- **The hover preview lingers after a click or `Esc`.** With the pointer still on the
  clicked focus, two forced phase names sit under phase marks; with the pointer moved
  away, there are none. After `Esc`, the "rest" view shows 6 label-on-label overlaps
  until the pointer moves.
- **A paragraph-length name moves the stage.** Selecting a concept with a 251-character
  name wraps the caption above the stage and pushes the whole stage down 21 px.
- **The constellation loses story order.** Phases read 4, 1, 3, 2 and 9, 7, 6, 5,
  because neighbours are placed by direction.
- **The phone reveal is not readable.** It prints over the title card. The stage is
  74vh with `touch-action: none`, so vertical swipes over it pan the atlas instead of
  scrolling the page. This was checked in code and emulation, not on a real phone.
- **Only three Book headings show at rest.** More appear when zoomed in, for example
  "Book 12".

**Where it says the refinement doc overclaims, and this review agrees:**
- "0 overlaps" holds only with the pointer away;
- "58 of 76 landmarks" is a pre-filtered set;
- "nothing moves" holds inside the stage, not on screen;
- "each Book is named once" is true of three groups;
- "24 of 24 named" in B counts a pill reading *Repetition with…*.

**Its verdict.** Ready for real authors on desktop, with the small specimen first and
the dense one as a stress test. First fix the lingering hover, the stage shift, and the
missing genre names and Book headings. Leave the phone out of first sessions, and order
B by story time.

## Findings

### A. Blocking interaction defects

None found.

### B. Consequential visual or usability deficiencies

1. **The atlas is not on the first screen.** With `?atelier` at 1440×900 the Atelier
   starts 1,224 px down, below the Story Vision, the agent controls and the Overview
   summary. This is inherited layout, but promotion needs the atlas first.
2. **The hover preview lingers after a click or `Esc`.** Every mouse user meets this:
   two names sit under marks during a reveal, and the "rest" view after `Esc` shows six
   overlapping labels until the mouse moves.
3. **Leaving a dense constellation stutters**: about 20 fps, worst frames 117–150 ms,
   on a fast GPU. The cost is rendering, not script.
4. **Names that carry meaning are cut, and long ones move the stage.** This affects the
   focus's engine and pattern in A and B, phase 1 at rest, and second-order sentence
   names. Kind prefixes repeated inside titles spend the space. A paragraph-length name
   pushes the stage down 21 px.
5. **The resting hierarchy names emotions before genres and hides the Books.** Three of
   seven genres are unnamed, while 21 of 25 emotion entries are named. Only three Book
   headings show, and they read "DURATION UNKNOWN".
6. **The constellation loses story order.** Its phases read 4, 1, 3, 2 and 9, 7, 6, 5.
7. **The phone experience is not ready.** The reveal prints over the title card, pills
   are cut, and the stage captures vertical swipes.

### C. Optional polish

- Glyphs touch the band counts, top arcs are clipped, and the fixed status bar covers
  the bottom of the stage.
- The constellation's verb knot and tethers, and the hatched threads on a phone.
- Zoomed views mix Roman numerals with phase names. A phase's kicker reads
  "PHASE · PHASE", and linked phase marks turn white on cream.
- Some accessible names repeat a kind ("Trope: Trope: …").
- `seed_atelier_study.py` still prints the first study's `?atelier=A|B|C` links.

### D. Unverified hypotheses

Only author use can settle these:
- that the resting density rewards rather than exhausts;
- that stable positions build spatial memory over long work;
- that B helps analysis more than the folio's relationship list;
- that the paper-and-serif identity reads as a creative instrument rather than
  decoration;
- that the atlas prompts better creative questions;
- that the faint resting threads carry information: at rest their colours are too
  pale to tell apart.

Screen readers, touch and Architectures larger than 156 concepts remain untested.

## Recommendation

**Ready for the owner's desktop acceptance session now. Not ready for default
promotion, and not ready on a phone.**

- There are no blocking defects. The A-first direction is realised in the parts that
  are hardest to retrofit: stable positions, a kept view, exact return, and a clear
  boundary between reading and proposing.
- Before any default-UI decision, one targeted refinement should address B1 to B7:
  - show the atlas first;
  - clear the hover preview after a click or `Esc`;
  - make the dense return smooth;
  - keep meaningful names, every genre and the Book headings readable without moving
    the stage;
  - order the constellation by story time;
  - make the phone reveal readable.
- Each item is a contained fix within the existing design, not a new model.
- Promotion remains an owner decision, made after real use.

## Owner acceptance exercise (about five minutes)

Start the Studio from a fresh worktree of `main` in PowerShell. Seeding writes only to a
disposable folder.

```powershell
git -C H:\GithubRepositories\auteur fetch origin
git -C H:\GithubRepositories\auteur worktree add --detach H:\auteur-atelier-review origin/main
cd H:\auteur-atelier-review
$env:PYTHONPATH = "src"
python scripts/seed_atelier_study.py --project "$env:TEMP\atelier-review"
python -m auteur.beginner.server --project "$env:TEMP\atelier-review" --port 8793
```

`PYTHONPATH=src` makes Python load this worktree rather than another editable install.
Open `http://127.0.0.1:8793/studio.html?canvas=atelier-dense&atelier`, then:

1. **Find the atlas.** Use a desktop browser window and scroll down to *The Living
   Narrative Atelier*. If labels overlap right after a click or `Esc`, move the mouse
   (finding B2), and note whether it bothered you.
2. **Rest for one minute.** Do not click. Say what the story is and how it is organised.
3. **Reveal.** Click *Institutional certification procedural*, the large diamond in the
   top row. Read the folio. Then press `]` to reveal deeper connections.
4. **Follow.** In the folio, click a phase it is active in, then one more relationship.
   Go back with the trail. Zoom in with **+** and follow again.
5. **Examine.** Press `E` (or *Examine as constellation*). Read it, click one neighbour
   inside it, then press `Esc` to return to the atlas. Press `Esc` again for the whole
   atlas.
6. **Compare.** Repeat steps 3 and 5 on `canvas=atelier-small` with *Literary mystery*.

Questions:

1. **Resting experience:** before you selected anything, did the atlas feel rich,
   beautiful and meaningfully interconnected?
2. **Progressive revelation:** did exploring an idea make the story easier to understand
   without losing the broader narrative?
3. **Focused analysis:** was the constellation genuinely useful when you needed close
   analysis? On which Architecture?
4. **Overall experience:** would you enjoy using this regularly to develop a long
   narrative? What one thing would stop you?

Stop the server with `Ctrl+C`. Remove the worktree with
`git -C H:\GithubRepositories\auteur worktree remove H:\auteur-atelier-review`.

## Resolution (added 2026-11-21)

The seven consequential findings above, B1 to B7, were addressed inside the existing
design by the [author-experience refinement](2026-11-21-atelier-author-experience-refinement.md).
That document records the before and after evidence and what remains open. This review
is kept as written; author acceptance is still pending.
