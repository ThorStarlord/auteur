# Explanatory Semantic Navigation Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Make the merged Genre Anatomy, Convention vs. Invention, Mechanism Map and Story Map prototypes navigable through source-honest, reversible relationships rather than unrelated inspector actions.

**Architecture:** Add one read-only link projection and one independent pure navigation-state module. The existing `app.mjs` coordinates views, browser history and compact context; existing visual components only emit explicit navigation intentions. No story persistence or new canonical data owner.

**Tech Stack:** Vanilla browser ES modules, Node `node:test` (existing), Python >=3.11 / pytest >=8 (existing), HTML/CSS, standalone static HTTP server; no runtime package, framework or paid GitHub Actions requirement.

**Spec:** `docs/superpowers/specs/2026-10-12-explanatory-semantic-navigation.md`.

## Global Constraints

- Target the merged `main` concept study at `docs/prototypes/studio-explanations/`; recheck current head before editing.
- Preserve `model.mjs`'s `normalizeEvidence`, `entriesForPerspective`, `connectionsForSelection` contracts and strict source-authority rules.
- Make links out of recorded `genre_links` and `proposal_edges`; **no** invented trope→emotion or presumed genre convention from missing coverage.
- `model.items[].id` and `model.genres[].id` are fixture-local. Avoid global trope identities, canonical acceptance and new store/schema migrations.
- Immediate navigation is the default. Do **not** implement popup previews, added permanent sidebars or new genre packs.
- Keep the previously chosen one-hero-per-perspective visual hierarchy and close-by-default explicit inspector.
- Prototype URL fragments may expose **fixture IDs only**, never story prose. Keep focus, source explanations and trail as browser-local presentation state.
- Limit each PR to <=500 changed lines and <=12 files; split on tested responsibilities. Tests are focused L1 unless a genuine integration defect requires more.
- Each task follows RED → GREEN → commit. Do not confuse source assertions, synthetic fixture browser tasks or HTTP 200 with author comprehension or live Studio qualification.

## Review Focus

1. **Shared trope / multiple genres:** clicking each attributed genre from the same trope opens its own Anatomy explanation; Back returns to the same trope and appropriate genre row. Tested Task 1/4.
2. **Unsupported link / missing pack:** no clickable causation from trope to emotion or false curated rule; show honest explanatory absence. Tested Task 1/4.
3. **History correctness:** direct-deep-link load, Back/Forward, repeated same link, view switch, and fixture change do not manufacture back destinations or mismatched focus. Tested Task 2/3.
4. **Stale or replaced source:** incoming invalid link or deleted fixture item results in an explicit unavailable state and safe return; never select a similarly titled item. Tested Task 2/3.
5. **Keyboard, long labels, mobile:** semantic labels, return focus, browser tab order and 390px layout work without hidden-only cues or horizontal overflow. Tested Task 5/6.

---

## Exact File Map

- Create `docs/prototypes/studio-explanations/semantic-links.mjs` — pure evidence-preserving link derivation.
- Create `docs/prototypes/studio-explanations/semantic-links.test.mjs` — real Node tests on shared fixtures and missing-link cases.
- Create `docs/prototypes/studio-explanations/navigation-state.mjs` — pure route/trail/deep-link interpretation, no DOM.
- Create `docs/prototypes/studio-explanations/navigation-state.test.mjs` — state/history/invalid-target behavior.
- Modify `docs/prototypes/studio-explanations/app.mjs` — source-aware dispatch and browser History API.
- Modify `docs/prototypes/studio-explanations/index.html` — compact origin/Back/breadcrumb/arrival-context landmarks.
- Modify `docs/prototypes/studio-explanations/views/anatomy.mjs` — send linked story elements to appropriate explanation.
- Modify `docs/prototypes/studio-explanations/views/comparison.mjs` — attributed genre links and actual linked mechanism navigation.
- Modify `docs/prototypes/studio-explanations/views/mechanism.mjs` — navigation across related elements and types.
- Modify `docs/prototypes/studio-explanations/styles.css` — semantic-link affordance, responsive context, focus.
- Modify `tests/test_studio_explanatory_prototypes.py` — DOM and event behavior contracts.
- Modify `docs/prototypes/studio-explanations/README.md` — navigate/Back/deep-link/qualification limits.

## Shared Interfaces

`semantic-links.mjs` exports:
- `deriveSemanticLinks(model) -> SemanticLink[]`: only fixture-declared genre relationships and candidate edges; preserves `sourceRef/sourceKind/supportStatus`, compatible `ownerGenreId` and `phaseId` when supported.
- `linksForFocus(links, focus) -> SemanticLink[]`: returns traversable, source-scoped relations touching `focus:{kind,id}`, with context-specific link direction and wording; no generated causal edges.
- `preferredPerspective(model, target) -> "anatomy"|"comparison"|"mechanism"|"overview"|null`: genres→Anatomy, tropes→Comparison, engines/structures→Mechanism, remaining items→Overview; unknown/unsupported→null.

`navigation-state.mjs` exports:
- `visitRoute(current, destination, viaLinkId, snapshot) -> Route`: pushes a bounded origin snapshot (max 12), including source perspective, focus, active control ID, scroll/focus locator; ignores identical consecutive hops.
- `returnRoute(current) -> Route`: pops to the exact prior route, or leaves current unchanged when trail empty.
- `reconcileRoute(route, model) -> {route, issue:null|string}`: validates `storyId`, perspective, IDs and link source; invalid target remains an explicit unavailable-state issue with fallback to valid Overview.
- `serializeFixtureRoute(route) -> string` and `parseFixtureRoute(hash) -> Partial<Route>|null`: allowlisted public fixture routing only, with `story/view/kind/key` tokens and no prose.

**Presenter callback in the three views:** `onNavigate(semanticLink, destinationRef)`. Preserve separate `onFocus(id)` for ordinary local selection and `onInspect(id)` for explicitly requested detail. No component may call another perspective renderer directly to simulate cross-view navigation.

### Task 1: Generate trustworthy links from existing fixture evidence

**Files:** Create `semantic-links.mjs`, `semantic-links.test.mjs`.  
**Consumes:** `normalizeEvidence(story,genreEvidence)`; fixtures `paladin.json`, `hybrid.json`.  
**Produces:** `deriveSemanticLinks`, `linksForFocus`, `preferredPerspective`.

- [ ] Step 1 — Write Node tests `keeps_each_genre_role_distinct`, `does_not_create_trope_to_emotion`, `labels_hypothesis_without_pack_authority`, `preserves_declared_edge_source`, `returns_no_destination_for_unknown_kind`. Assert both inverse directions use one recorded relationship, not fabricated independent evidence.
- [ ] Step 2 — RED: `node --test docs/prototypes/studio-explanations/semantic-links.test.mjs` fails with missing module/exports.
- [ ] Step 3 — Implement exported functions. Compose stable ephemeral IDs from source-local keys + source record scope; do not infer semantic links by string similarity, optional hero text or neighboring categories.
- [ ] Step 4 — GREEN: rerun the same Node tests and `node --test docs/prototypes/studio-explanations/model.test.mjs`.
- [ ] Step 5 — Commit: `git add docs/prototypes/studio-explanations/semantic-links* && git commit -m "feat(studio): derive source-scoped semantic navigation links"`.

**Acceptance:** Independent multi-genre links, honest missing source and no unsupported emotional causality.

### Task 2: Pure route, focus and bounded history semantics

**Files:** Create `navigation-state.mjs`, `navigation-state.test.mjs`.  
**Consumes:** `SemanticLink` from Task 1 and valid `model` IDs.  
**Produces:** pure `visitRoute`, `returnRoute`, `reconcileRoute`, `serializeFixtureRoute`, `parseFixtureRoute`.

- [ ] Step 1 — Write failing Node tests `cross_view_returns_exact_origin`, `deduplicates_repeated_click`, `caps_trail_at_twelve`, `invalid_id_reports_unavailable`, `direct_load_has_no_fake_back`, `hash_does_not_expose_story_text`, `source_replacement_invalidates_hop`. Compare complete route snapshots, not only selected IDs.
- [ ] Step 2 — RED: `node --test docs/prototypes/studio-explanations/navigation-state.test.mjs` fails for missing exports.
- [ ] Step 3 — Implement the pure navigation functions. Store scroll and focus selector in route snapshots, not story storage; parse only explicit allowlisted fixture IDs and perspective names. No browser globals in this module.
- [ ] Step 4 — GREEN: rerun Node tests for Task 1 and Task 2; verify state objects from frozen fixture data are not mutated.
- [ ] Step 5 — Commit: `git add docs/prototypes/studio-explanations/navigation-state* && git commit -m "feat(studio): reversible source-aware explanation routes"`.

**Acceptance:** A user can follow multiple semantic hops and return without loss or stale remapping.

### Task 3: Coordinate actual navigation and arrival context

**Files:** Modify `app.mjs`, `index.html`; Test `tests/test_studio_explanatory_prototypes.py`.  
**Consumes:** Task 1/2 exports; preserves `showDetail` as explicitly invoked inspector.  
**Produces:** `navigateByLink(link,target)`, `renderArrivalContext(route)`, `restoreBrowserRoute(event)` internal functions.

- [ ] Step 1 — Write failing tests `test_context_bar_is_conditional_and_source_labelled`, `test_navigation_is_distinct_from_inspect`, `test_browser_back_forward_and_direct_hash`, `test_unknown_destination_renders_recoverable_notice`. Replace the existing brittle `test_exploratory_selection_history_can_return_without_losing_view` source-string assertion with a behavioral route/return invariant. Require one origin bar and no extra sidebar or auto-opening inspector.
- [ ] Step 2 — RED: `python -m pytest tests/test_studio_explanatory_prototypes.py -q` and the Task 2 Node tests fail at expected missing behavior.
- [ ] Step 3 — Wire route rendering to browser `pushState/replaceState/popstate` for the public fixture URL. Use one route owner, not existing unused `state.history` plus a second competing `selectionHistory`. Preserve modified clicks/native new-tab semantics on anchor links. Focus destination title; on Back restore the originating control and scroll when still valid.
- [ ] Step 4 — GREEN: rerun focused tests. With the static HTTP server, load a direct `#story=paladin&view=...` route, follow links, browser Back/Forward and reload; note failures rather than silently defaulting.
- [ ] Step 5 — Commit: `git add docs/prototypes/studio-explanations/app.mjs docs/prototypes/studio-explanations/index.html tests/test_studio_explanatory_prototypes.py && git commit -m "feat(studio): connect explanatory routes to accessible context"`.

**Acceptance:** Clicking a relationship changes the **correct explanatory perspective** and names the source/verb/evidence on arrival, with exact Back restoration.

### Task 4: Connect all three visual grammars

**Files:** Modify `views/anatomy.mjs`, `views/comparison.mjs`, `views/mechanism.mjs`; Test `tests/test_studio_explanatory_prototypes.py`.  
**Consumes:** `onNavigate(link,destinationRef)`, `onFocus(id)`, `onInspect(id)`.

- [ ] Step 1 — Write failing view tests: `test_anatomy_story_use_opens_trope_explanation`, `test_comparison_genre_opens_specific_anatomy`, `test_comparison_only_links_declared_mechanisms`, `test_mechanism_neighbor_moves_with_back`, `test_undocumented_relation_is_not_clickable`. Include two genre roles for the same trope.
- [ ] Step 2 — RED: run `python -m pytest tests/test_studio_explanatory_prototypes.py -q`; ensure failure is missing cross-view callback, not a syntax typo.
- [ ] Step 3 — Render links with relationship-specific text (e.g. "Explore how Earned Breakthrough illustrates Challenge/Learning"), source status and a valid `href`. Keep an independently labelled `Inspect source` control separate from navigation. Unsupported cross-view edges get a factual empty explanation, not a dead button.
- [ ] Step 4 — GREEN: focused Python + both new Node test files, and `node --check` on all modified `.mjs` files. Click each target from the actual paladin fixture.
- [ ] Step 5 — Commit: `git add docs/prototypes/studio-explanations/views tests/test_studio_explanatory_prototypes.py && git commit -m "feat(studio): navigate between explanatory genre trope and structure heroes"`.

**Acceptance:** Genre → trope → mechanism → Back → Back follows declared links and returns to the original genre; a direct mechanism → genre link exists only where explicitly supported, without fabricating emotional connections.

### Task 5: Compact breadcrumbs, keyboard focus and mobile behavior

**Files:** Modify `styles.css`, `index.html`, `app.mjs`; Test `tests/test_studio_explanatory_prototypes.py`.  
**Consumes:** `Route.trail` and `viaLinkId`.

- [ ] Step 1 — Write failing UI checks `test_compact_breadcrumbs_show_current_origin`, `test_links_have_text_and_focus_styles`, `test_no_empty_inspector_until_inspect`, `test_return_focus_after_navigation`.
- [ ] Step 2 — RED: run focused Python UI tests.
- [ ] Step 3 — Show at most three trail hops plus "Earlier" overflow; one-line reason context (with expandable source details); focus ring and polite destination announcement; wrap at 390px; use `prefers-reduced-motion` for transitions. No hover-preview tooltip and no persistent second navigation rail.
- [ ] Step 4 — GREEN: focused tests and real browser at 1440x900 / 900x700 / 390x844. Keyboard-only Tab/Enter/Back; verify inspector stays closed and no page-wide horizontal overflow.
- [ ] Step 5 — Commit: `git add docs/prototypes/studio-explanations/{styles.css,index.html,app.mjs} tests/test_studio_explanatory_prototypes.py && git commit -m "style(studio): compact semantic trail and accessible link focus"`.

**Acceptance:** Meaningful movement is apparent with no more competing UI surfaces than the present concept.

### Task 6: End-to-end falsification and documentation

**Files:** Modify `README.md`, optionally focused tests only.  
**Consumes:** exact final prototype head, the two common fixtures, Task 1–5 tests.  
**Produces:** reproducible verification notes and honest remaining qualification gap.

- [ ] Step 1 — Execute the spec's paladin sequence, hybrid two-genre fork, absent-pack scenario, unknown item, repeated click and a stale/replaced source. Turn each discovered functional regression into a failing test before repairing it.
- [ ] Step 2 — Run `node --test docs/prototypes/studio-explanations/*.test.mjs` and `python -m pytest tests/test_studio_explanatory_fixtures.py tests/test_studio_explanatory_prototypes.py -q`; confirm full output/exit status, not just the final line.
- [ ] Step 3 — Start `python -m http.server 8765` at repo root; inspect actual served ES modules + both fixtures at desktop/intermediate/mobile, including browser Back/Forward and keyboard. If the environment blocks live navigation, say so and use same-source inline browser harness only as a lower-confidence fallback.
- [ ] Step 4 — Update README with tested commands, keyboard behavior, direct fixture links and provenance gaps. No promotion to live Studio or acceptance. Commit: `git add docs/prototypes/studio-explanations/README.md && git commit -m "docs(studio): document semantic navigation and verification ceiling"`.
- [ ] Step 5 — Open reviewable PR(s) within the size/file caps, reconcile exact changed heads against current `main`, and hand off production integration using the **separate** plan `docs/superpowers/plans/2026-10-12-studio-semantic-navigation-integration.md`.

**Acceptance:** All semantic navigation tasks are reproducible and source-honest, with a clear production integration boundary.

## Execution Decision

Implement Tasks 1–5 directly in an isolated workspace with small tested commits, independent review at route/link boundaries, then Task 6 adversarial browser review. This is **product construction**, not another open-ended redesign study. Prototype implementation is reversible and can land on `main` without declaring live Studio integrated.
