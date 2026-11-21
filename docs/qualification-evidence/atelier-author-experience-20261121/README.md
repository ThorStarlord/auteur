# Atelier author-experience refinement: evidence (2026-11-21)

Evidence for [the refinement](../../design/2026-11-21-atelier-author-experience-refinement.md).
That refinement answers [the acceptance review](../../design/2026-11-21-atelier-acceptance-review.md).

- **Source:** branch `feat/atelier-author-experience` at `1b13a46d`, a clean tree,
  reconciled with `main@08279f7c` (PR #629). Every file here was produced at that commit;
  `live-frame-times.json` also keeps the before measurements, the diagnosis and PR #629's
  reported figures.
- **Specimens:** two recorded agent proposals seeded by `scripts/seed_atelier_study.py`.
  Neither is author-owned or accepted story.

| File | What it shows | How it was produced |
|---|---|---|
| `capture-metrics.json` | Journey invariants, label and settle measures on both specimens, plus phone width, keyboard only and reduced motion | `scripts/qualification/atelier_study_capture.py --video`, headless Chromium |
| `live-frame-times.json` | Frame times before and after the rendering change, and the feature-by-feature diagnosis | Windowed Chromium on an NVIDIA RTX 5060 Ti at 60 Hz, with an in-page `requestAnimationFrame` logger, 3 rounds |
| `phone-touch.json` | Vertical swipes scroll the page, horizontal drags travel the atlas, tap to select, the phone constellation, leave and return | Playwright at 390×844 with emulated touch through Chrome's input pipeline (CDP `Input.dispatchTouchEvent`) |
| `review-findings.json` | Each consequential finding of the second independent review, re-checked | Playwright Chromium at 1440×900 and 390×844 |
| `thread-freshness.json` | No background thread is left stale after interrupted, rapid, resized or reduced-motion transitions, or during zooms and pans | Windowed Chromium, dense specimen; each thread end must lie within 16 px of its concept mark |

The served-browser regressions are in
`tests/test_beginner_studio_atelier_experience_browser.py`.

These are machine measurements, not a human usability evaluation, and touch was
emulated rather than tested on a phone. Screenshots and recordings are in the owner's
private visual report.
