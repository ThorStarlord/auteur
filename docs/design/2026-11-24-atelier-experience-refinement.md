# Atelier: integrated visual and interaction refinement

Status: implemented on `feat/atelier-experience-refinement` (builds on #631–#637). Opt-in Atelier only
(`?atelier`).

## What the served Atelier was at `main@2db01cc5`

The same journeys were walked on three projects at 1440 × 900 and 390 × 844, with the captures under
`docs/qualification-evidence/atelier-experience-refinement-20261124/`:
- a small Architecture (68 concepts);
- a dense fourteen-Book Architecture (156 concepts);
- Spring Ledger with Working Books 24 and 25.

**Strengths, kept unchanged:**
- **The atlas:** a calm, legible first screen on both projects, with bands, Books, phases and glyphs.
- **Focused Constellation:** opens in about 1.4 s and returns to the same place.
- **The folio:** quiet and literary.

**Consequential problems:**
1. **Two different places, two different looks.**
   - **Where the work happens:** inquiry, the agent's answer and the revision review happen in the Studio's
     generic panels below the Atelier. On desktop, the page grows to 5,700 px at the answer and 8,800 px at
     the review.
   - **What they look like:** a plain three-column workbench, a wall of sans text for the answer, raw ids
     in the review graph, and 64-character hashes beside what changed.
2. **The author was stranded after Apply.** Focus fell to the page body at scrollY 1,877 (9,634 on a phone),
   while the status line said "The atlas marks what changed".
3. **Writing happened in a narrow column.** The Book composer and the discovery card were about 300 px
   wide, under long explanations.
4. **Labels contradicted the capability.** "Visual study · experimental · presentation only" and "nothing
   is saved" had been untrue since the Atelier began preparing and applying revisions through owners.
5. **The opened Book was not first.** Opening Book 24 from a concept showed a full-width "Read again", a
   paragraph and the cross-Book overview (starting with Book 25) before Book 24's own record.

## Design direction

The three qualities are one workspace at three distances:
- **Narrative Atelier:** the shared language. Ivory paper, an editorial serif for what the author reads and
  writes, a quiet sans for controls, semantic colour used only for meaning, and one filled button per
  decision.
- **Living Narrative Atlas:** the world, unchanged and always the place the author returns to.
- **Quiet Precision Studio:** two desks.
  - The **writing desk** widens the folio over the atlas edge while the author composes, and never moves
    the atlas.
  - The **agent desk** below the atlas gives inquiry, answer and review the Atelier's reading language.

Semantic colour keeps the meanings the previous work established:
- **green** — what a record holds;
- **amber** — an agent's interpretation;
- **violet-grey and dashed** — the author's own Book evidence;
- **neutral** — a working Book's own change, or a concept that is gone;
- **red** — only what blocks.

## What changed

1. **The agent desk** (`studio_atelier_desk.css`, scoped under `.studio-atelier-desk`). `studio.js` sets this
   class on `.studio` only while the Atelier is the eligible view. It covers:
   - **Tools row:** a quiet row of controls.
   - **Panel:**
     - one reading column, with the recorded relationship and component lists placed after the panel
       instead of beside it;
     - the evidence shown apart from the question;
     - pressed choices shown as a tint, so the only filled button is the one that acts.
   - **Answer:**
     - the question it answers and its Book evidence first;
     - the agent's interpretation (amber) beside the records it cites (green);
     - alternatives as cards side by side, a line saying how choosing works, and a line saying that choosing
       none leaves the Architecture as it is.
   - **Review:**
     - serif headings, and nodes named by title (the id kept as a tooltip);
     - source hashes small and quiet;
     - one filled Apply.
2. **Apply returns to the atlas.** When the Atelier is shown, the author goes back to the concept, or to the
   discovery they came from.
3. **The writing desk** (`.atl-writing`) widens the folio over the atlas edge while a Book composer is open,
   or while a discovery is being considered and not yet taken to the coding agent:
   - the composer gets a serif writing field and a calm focus ring;
   - the stage keeps its size, camera and positions;
   - narrow screens are unchanged;
   - under reduced motion (the operating-system setting or the in-study toggle) there is no animation.
4. **Reading order and labels:**
   - the Series and Book view leads with the Book the author opened, and leads with the overview only when the
     author asked for it;
   - "Read again" and per-element actions are quiet text actions;
   - the header reads "Working Architecture · noncanonical";
   - the ribbon says records change only when the author applies a reviewed revision.
5. **Coherence after a revision:**
   - an open discovery says when an Architecture revision was applied after it was asked;
   - once alternatives arrive, the question already sent is cleared from the instruction field, so it is
     never reused as a revision instruction by an unthinking click.

## What did not change

- **Unchanged contracts:**
  - the Narrative Architecture, Working Book and Series ownership;
  - graph intent and typed references;
  - inquiry, selected alternatives and Book evidence;
  - host-agent request and response contracts;
  - revision, review and Apply;
  - cross-Book impact;
  - freshness and concurrency.
- **Payload equality:** the independent technical review replayed the same journey on main and on the
  branch. The request and response bodies are byte-identical, except a client-generated command id.
- **No new behaviour:** no new persistent state, no new spatial mode, and no new narrative relationship.
- **Opt-in:** the Atelier stays opt-in.

**The ordinary Studio:** without `?atelier`, the desk sheet does not apply. Three shared panel changes are
intended improvements that also appear there, with compact fallback styling:
- the alternative structure;
- the decline line;
- the plain "No question asked yet" status.

## Measured continuity (agent-operated; `journeys-before.json` and `journeys-after.json`)

| Step | Before (desktop / phone) | After (desktop / phone) |
|---|---|---|
| Focus after Apply | page body, scrollY 1,877 / 9,634 | the discovery the author came from, scrollY 168 / 3,344 |
| Page height when the answer arrives | 5,739 / 15,349 px | 4,935 / 14,934 px |
| Page height at the review | 8,765 / 19,012 px | 8,595 / 18,776 px |

**Inherited, and recorded rather than changed:**
- **Two-page layout:** the agent desk is still below the atlas, so the hand-off still scrolls the page.
- **Check agent result:** sits above the panel.
- **Old Studio controls:** the find bar and Story Vision sit between the atlas and the desk.
- **Backspace:** after following a relation from the folio, it does nothing (also on main).

## Limits

- **No real author:** these are agent walkthroughs and agent critiques. No author has used the refined
  interface, so its aesthetic and comfort remain unvalidated.
- **One-page workspace:** bringing the agent desk beside the atlas would remove the remaining page scroll
  between atlas and desk. It is a larger information-architecture change and was not attempted here.
