# Atelier × Series/Book context: evidence (2026-11-22)

Evidence for [the design note](../../design/2026-11-22-atelier-series-context.md).

- **Arms:** `main@0b92409d` (baseline) and branch `feat/atelier-series-context` at `961ff87d`
  (candidate). The arm is named in each file. Each arm served its own copy of the same disposable projects, seeded
  by `scripts/seed_series_context_study.py`.
- **Projects:**
  - `linked`: the Spring Ledger W6 working Architecture and its Book 24 working Book architecture,
    rebuilt through their owners from `docs/qualification-evidence/working-book-architecture-20261112`.
    Recorded agent output, used as a fixture.
  - `context`: the dense fourteen-Book proposal, the repository's Ash Empire test trilogy as
    `series_identity.yaml` (two setups and a payoff added), and the Archive of Lies Series and Book
    Directions accepted through the Series journey, with the Series Direction revised after Book 1.
  - `none`: the small proposal, with no plans.
  - `damaged`: the Spring Ledger after an Architecture revision removed `inst_gate_table`, a malformed
    `series_identity.yaml`, and an accepted Series Direction edited by hand after acceptance.

| File | What it shows | How it was produced |
|---|---|---|
| `baseline.json` | The same two author tasks on `main`: no route from a concept to its Book or the project's Series plans; the route returns 404 | Headless Chromium 1440×900, served Studio |
| `candidate.json` | Concept → the Book that records it (elements, authority, freshness) → Escape back to the same place; concept → project plans, stated as not linked → hypothesis drafted, not sent | Headless Chromium 1440×900, served Studio |
| `book-resume-baseline.txt` | The only path on `main`: the Book owner's CLI packet, its size and what it says about `eng_ledger` | `python -m auteur.series.working_book_architecture … book-resume --book 24` |

Regression tests: `tests/test_beginner_studio_series_context.py` (owner reads, freshness, damaged
records, no writes, route), `tests/test_beginner_studio_atelier_series_browser.py` (served journeys,
keyboard return, phone width, ordinary Studio), `tests/test_studio_atelier_series.mjs` (id-only joins,
freshness wording, hypothesis draft).

These are machine measurements and an independent agent review, not a usability study. No author has
used the change. Screenshots are in the owner's private visual report.
