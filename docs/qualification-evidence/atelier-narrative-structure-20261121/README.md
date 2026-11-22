# Atelier narrative-structure study: evidence (2026-11-21)

Evidence for [the study](../../design/2026-11-21-atelier-narrative-structure-study.md).

- **Source:** branch `feat/atelier-narrative-pathways` at `2d1c4b31`, a clean tree, based on
  `main@e48a3ecc`. Every file here was produced at that commit. The next source commit, `42e7acd9`,
  changes one folio sentence (parallel phases are mentioned only where recorded); nothing measured
  here depends on it.
- **Specimens:** two recorded agent proposals and one constructed fixture, seeded by
  `scripts/seed_atelier_study.py`. None is author-owned or accepted story.
  - `atelier-small`: 68 concepts, 82 relationships (coastal literary mystery).
  - `atelier-dense`: 156 concepts, 215 relationships (fourteen-Book series).
  - `atelier-counterexample`: the small specimen with only its genre contracts' governing and
    supporting roles exchanged. No relationship is added or removed.

| File | What it shows | How it was produced |
|---|---|---|
| `comparison.json` | Baseline and candidate on all three canvases: resting names, overlaps, genre mark sizes and role lines, framed parents; and for each named case, the phases Progressive Revelation joins, the phases marked as listed, the phase pills naming a role, neighbour naming, threads, the folio's story-time heading and every phase's sources. Positions, cameras, threads and the canvas revision are compared between the arms. | Headless Chromium at 1440×900 against the served Studio |
| `story-time-records.json` | For every concept that two or more phase records name directly: what Progressive Revelation already shows, what only the phase records add, and the role each phase records | The pure model in Node |
| `live-frame-times.json` | Selecting and releasing two genres in both arms, and the switch at rest and while a concept is selected: synchronous cost and frame times | Windowed Chromium on an NVIDIA RTX 5060 Ti at 60 Hz, in-page `requestAnimationFrame` logger, 3 rounds |

The served-browser regressions are in `tests/test_beginner_studio_atelier_narrative_browser.py`;
the model's are in `tests/test_studio_atelier_model.mjs`.

These are machine measurements and one independent agent review, not a human usability
evaluation. No author has used the candidate. Touch was emulated at phone width, not tested on a
phone. Screenshots and a recording are in the owner's private visual report.
