# Atelier ↔ Architecture workflow integration: evidence (2026-11-22)

Evidence for [the design note](../../design/2026-11-22-atelier-architecture-integration.md).

- **Arms:** `main@21a4506c` (baseline) and branch `feat/atelier-architecture-integration` at
  `8ea9b22a` (candidate). `baseline.json` comes from `main`; every other file from `8ea9b22a`.
  Each was served from its own worktree against its own disposable project seeded by
  `scripts/seed_atelier_study.py`.
- **Specimen:** `atelier-dense`, the recorded fourteen-Book agent proposal (156 concepts). It was
  recorded on 2026-11-17, before the trope-function reference contract (#625), so none of its
  nine "the first crosser" phrases is joined to the trope node of that name.
- **Coding agent:** the revisions and the inquiry answer in the journeys were written by this
  agent (Claude Opus 5.5) through the Studio's host-agent path, as the author's coding agent
  would. They are working proposals in a disposable project.

| File | What it shows | How it was produced |
|---|---|---|
| `baseline.json` | The same task on `main`: actions offered for a contract function, payoff sources, the inspector route's position, the selection after preparing and after applying a revision, positions moved | Headless Chromium 1440×900, served Studio |
| `journeys.json` | Journey A (shared trope → contextual functions → revision recording which realise it → review → apply → return → one function → revision of that function only) and Journey B (engine → interpretation → challenge → answer → return), with anchors, request contents, focus, positions, announcements and non-mutation checks | Headless Chromium 1440×900, served Studio |
| `phone.json` | Hand-off and return at 390×844 (touch emulated) | Headless Chromium |
| `select-cost.json` | Synchronous cost of selecting four concepts, three rounds, both arms | Windowed Chromium, NVIDIA RTX 5060 Ti, 60 Hz |

Regression tests: `tests/test_beginner_studio_atelier_integration_browser.py` (served),
`tests/test_studio_atelier_model.mjs`, `tests/test_beginner_studio_architecture_graph_intent.py`,
`tests/test_studio_architecture_graph_actions.mjs`, `tests/test_studio_architecture_agent_bridge.mjs`.

These are machine measurements and an independent agent review, not a usability study. No
author has used the change. Screenshots and a recording are in the owner's private visual report.
