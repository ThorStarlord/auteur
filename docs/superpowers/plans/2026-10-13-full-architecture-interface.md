# Focus and Full Architecture Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve Auteur's merged Focused Unfolding prototype into one interface that supports local authoring, a coherent Full Architecture overview, per-genre comparisons, and an evidence-linked Book review.

**Architecture:** Reuse the existing Focused Unfolding demo working-state reducer; derive (never independently save) `FullArchitectureProjection` from the sibling projection plan. Render a single graph-first interface with Focus and Full modes and one contextual evidence panel; Review is a reversible state of the Full mode.

**Tech Stack:** Existing `docs/prototypes/focused-unfolding/` HTML, CSS, ES modules and Node tests, plus Python pytest/Chromium interaction tests. No new UI framework, provider, persistence schema or fake genre evidence.

**Spec:** `docs/superpowers/specs/2026-10-12-full-narrative-architecture-synthesis-design.md`

## Global Constraints

- Full is **Book Identity + Structure**, not mandatory scene-by-scene Realization. Never claim completing this prototype accepts Story Identity or creates a durable Book artifact.
- Keep Focus's **2–3 current-neighborhood ghost suggestions**, the emotion-first invitation and alternative starting roles unchanged; unadopted proposals are not a globally expanding graph.
- Full renders **one derived projection** of the same author working state and illustrative candidate fixture, using `projectFullArchitecture` and `reviewFullArchitecture` from `docs/prototypes/full-architecture/`. Do not independently persist Full content.
- Per-genre morphology requires actually supplied versioned-pack or legacy-contract evidence; a candidate's genre phrases are labelled **proposal interpretations**, never genre rules.
- Author-added relative to available evidence is **not** proven original; basic emotions and richer experience remain distinct.
- Preserve focus/inspected ghost/collapsed branch when switching modes; no authoring or provider call from Full/Review.
- Limit PRs to <=500 changed lines/12 files. Real served browser preferred; same-source inline Chromium only if local HTTP navigation is environment blocked, with limitation stated.

## Review Focus

1. **Blank working architecture:** Full opens with an honest empty/readiness scaffold and return-to-Focus action; no invented completed content (Task 1/4).
2. **Missing genre pack + two source roles:** a genre has unknown morphology and its candidate tropes remain visibly provisional, while a shared trope has distinct per-genre rows (Task 2).
3. **Unlinked author working addition:** Full shows the item, an explicit missing-link reason and a click-through to its Focus, never an invented source edge (Task 3/4).
4. **Switching Focus ↔ Full during editing:** selected focus, unadopted ghost state, adoption/dismissal, and presentation-only collapse are preserved with no data loss (Task 1/3).
5. **Dense content, narrow mobile and keyboard:** Full starts collapsed and navigable at 390px without horizontal overflow; keyboard focus returns to initiating control after Review (Task 5).

---

## File map and interfaces

- Modify `docs/prototypes/focused-unfolding/index.html` — mode switch `#mode-focus`/`#mode-full`, `#full-architecture` container and `#review-full-architecture` dialog/panel; retain existing graph.
- Modify `docs/prototypes/focused-unfolding/app.mjs` — mode-only local presentation state, source projection recomputation after author actions, focus/restoration.
- Modify `docs/prototypes/focused-unfolding/styles.css` — compact connected-architecture clusters and readable source-relative comparison; mobile.
- Create `docs/prototypes/focused-unfolding/full-view.mjs` — purely presentational `renderFullArchitecture(root,projection,options)`.
- Create `docs/prototypes/focused-unfolding/review-view.mjs` — purely presentational `renderReviewArchitecture(root,report,options)`.
- Create `tests/test_full_architecture_browser.py` — browser acceptance and source-bound interaction tests.
- Modify `docs/prototypes/focused-unfolding/README.md` — how to inspect Full, Review, fixture source status and testing ceiling.
- Consume fixture source `docs/prototypes/full-architecture/fixtures/paladin.json` and the pure projection/review APIs from the preceding plan; do not duplicate the data or projector.

`renderFullArchitecture(root,projection,{expandedCluster,onToggleCluster,onFocusRef,onReview})` renders exactly one overview graph and one opened comparison cluster. `renderReviewArchitecture(root,review,{onFocusRef,onReturn})` displays coverage items and actionable targets. Both functions render only source-delivered text using safe `textContent`, not untrusted `innerHTML`.

### Task 1: Two modes over one working state

**Files:** `index.html`, `app.mjs`, `tests/test_full_architecture_browser.py`.

- [ ] **Step 1: RED browser tests.** `test_empty_architecture_can_switch_to_full_without_fiction`, `test_focus_mode_preserves_selected_author_node_after_full_roundtrip`, `test_show_full_does_not_auto_adopt_or_request_ai`. Build fixtures with current `createDemoState`.
- [ ] **Step 2: Run RED.** `python -m pytest tests/test_full_architecture_browser.py -q` fails due to missing `#mode-full` or mode transitions.
- [ ] **Step 3: Implement.** Add controls and a single `mode="focus"|"full"` presentation state in `app.mjs`; compute projection on demand from the actual demo state and fixture. Switching mode changes visibility, not working nodes/accepted status/history.
- [ ] **Step 4: Run GREEN.** Same focused pytest plus existing `tests/test_focused_unfolding_browser.py` tests.
- [ ] **Step 5: Commit.** `git add docs/prototypes/focused-unfolding/{index.html,app.mjs} tests/test_full_architecture_browser.py && git commit -m "feat(studio): switch Focus and Full without forking working state"`

### Task 2: Genre constellation and morphology comparison

**Files:** Create `full-view.mjs`; modify `app.mjs`, `styles.css`, and browser tests.

- [ ] **Step 1: RED tests.** `test_full_shows_separate_genre_roles_morphology_and_candidate_interpretation`, `test_missing_pack_is_marked_unknown_not_noncompliant`, `test_same_trope_multiple_genres_has_distinct_attributed_rows`.
- [ ] **Step 2: RED run.** Focused pytest fails on missing per-genre panel.
- [ ] **Step 3: Implement.** `renderFullArchitecture(root,projection,options)` draws collapsed high-level genre and structure clusters. Clicking a genre reveals the matrix of actual source evidence versus proposed/adopted story use with source/badge labels; no unproven conformity or originality claim.
- [ ] **Step 4: GREEN run.** Browser tests pass on paladin and no-evidence fixtures, including keyboard selection and source details.
- [ ] **Step 5: Commit.** `git add docs/prototypes/focused-unfolding/{full-view.mjs,app.mjs,styles.css} tests/test_full_architecture_browser.py && git commit -m "feat(studio): compare each genre's evidence with the story"`

### Task 3: Integrated Identity, emotions, structure and author additions

**Files:** Modify `full-view.mjs`, `app.mjs` and browser tests.

- [ ] **Step 1: RED tests.** `test_reader_basic_emotions_distinct_from_rich_experience`, `test_full_renders_story_structural_phases_and_explicit_relations`, `test_unlinked_working_trope_stays_visible_as_unlinked`, `test_select_full_item_returns_to_original_focus`.
- [ ] **Step 2: RED run.** Focused pytest fails on missing sections/context.
- [ ] **Step 3: Implement.** Render working/accepted Identity distinctions, source-delivered basic emotion roles, Book phase/engine/genre activations, and author-relative additions. Clicking an item returns to Focus using its exact source/local ID and preserved stack; **do not rebind by title** or invent a link.
- [ ] **Step 4: GREEN run.** Focus ↔ Full roundtrip retains adopted working node and Focus ghost/dismissal states; original focused-unfolding tests still pass.
- [ ] **Step 5: Commit.** `git add docs/prototypes/focused-unfolding/{full-view.mjs,app.mjs} tests/test_full_architecture_browser.py && git commit -m "feat(studio): surface entire Book Identity and Structure blueprint"`

### Task 4: Final author review and issue navigation

**Files:** Create `review-view.mjs`; modify `index.html`, `app.mjs`, `styles.css`, tests.

- [ ] **Step 1: RED tests.** `test_review_lists_open_decisions_and_evidence_gaps_separately`, `test_review_unlinked_item_returns_to_its_focus`, `test_optional_scene_plans_do_not_block_book_review`, `test_review_does_not_write_acceptance_or_adoption`.
- [ ] **Step 2: RED run.** Focused pytest fails on missing Review action and issue links.
- [ ] **Step 3: Implement.** `renderReviewArchitecture(root,review,options)` displays actionable `reviewFullArchitecture` results, "Ready for author review" versus "Working design", exact issue links and a return control. It never declares canon accepted, rates writing quality or uses a percentage meter.
- [ ] **Step 4: GREEN run.** Focused pytest and `node --test docs/prototypes/full-architecture/*.test.mjs` pass; source status retained in Review.
- [ ] **Step 5: Commit.** `git add docs/prototypes/focused-unfolding/{review-view.mjs,index.html,app.mjs,styles.css} tests/test_full_architecture_browser.py && git commit -m "feat(studio): review whole-story decisions without canon acceptance"`

### Task 5: Accessibility, density and honest qualification

**Files:** `styles.css`, `app.mjs`, `tests/test_full_architecture_browser.py`, `README.md`.

- [ ] **Step 1: RED tests.** `test_full_compact_at_390_pixels`, `test_only_one_cluster_is_open_by_default`, `test_keyboard_focus_restored_after_review`, `test_dense_14_genre_80_node_fixture_no_page_overflow`, `test_source_revision_invalidates_full_but_preserves_author_work`.
- [ ] **Step 2: RED run.** Focused pytest on 1440x900/900x700/390x844 catches missing behavior.
- [ ] **Step 3: Implement.** Collapse-by-default, semantic buttons, visible focus rings, announced review status, reduced-motion controls and source-stale message. Prevent a full-graph unbounded ghost fan-out.
- [ ] **Step 4: GREEN runs.** `node --test docs/prototypes/full-architecture/*.test.mjs docs/prototypes/focused-unfolding/*.test.mjs`; `python -m pytest tests/test_focused_unfolding_browser.py tests/test_full_architecture_browser.py -q`; `node --check` modified JS.
- [ ] **Step 5: Document and commit.** README lists commands, illustrative fixture limitations, pack evidence gaps, and whether browser tests used real served ESM or inline-source harness. Open PR(s) under budget. **Do not claim live Studio or working-document persistence from this preview.**

**Completion boundary:** The same standalone demo supports both authoring and a read-only Full/Review Book blueprint, with no second story owner. Real Studio deployment is a separate plan.
