# Atelier visual acceptance review: evidence (2026-11-21)

Evidence for [the acceptance review](../../design/2026-11-21-atelier-acceptance-review.md)
of the opt-in Living Narrative Atelier.

- **Source:** `c5f09a30`, a clean tree identical to `origin/main@6fc59cbf`.
- **Specimens:** two recorded agent proposals seeded into a disposable project by
  `scripts/seed_atelier_study.py`. Neither is author-owned or accepted story.

| File | What it is | How it was produced |
|---|---|---|
| `capture-metrics.json` | Journey invariants and the study's own label and settle measures on both specimens; also phone width, keyboard-only and reduced motion | `scripts/qualification/atelier_study_capture.py --video` in headless Chromium |
| `live-frame-times.json` | Frame intervals for select, deeper, follow, examine, leave and return, three rounds each, plus a Chromium trace summary for the dense steps | A windowed Chromium on an NVIDIA RTX 5060 Ti at 60 Hz, with an in-page `requestAnimationFrame` logger between each action and `atelier:settled` |

These are machine measurements, not a human usability evaluation. Screenshots and
recordings are in the owner's private visual report, not in the repository.
