# Living Story Studio Explanatory Views and Semantic Navigation Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Integrate the chosen explanatory heroes and source-honest semantic navigation into the actual graph-first Living Story Studio without changing story authority or save semantics.

**Architecture:** Build a read-only adapter over the existing architecture candidate/genre contract and optional verified pack knowledge; render one dedicated explanatory surface per Architecture facet. Reuse the Studio's \`visitFacet\` / \`facetHistory\` / \`rememberFocus\` machinery, enhanced with typed link context, rather than introducing a parallel navigation store. Realization, Story Vision and CanvasStore continue to own working authoring and persistence.

**Tech Stack:** Current Auteur Python >=3.11 / pytest >=8, \`BeginnerWorkspaceServer\`, plain browser JavaScript/CSS, existing Studio IIFE loaded by \`/studio.js\`. No new framework, graph engine, database table or provider calls.

**Spec:** \`docs/superpowers/specs/2026-10-12-explanatory-semantic-navigation.md\`.  
**First dependency:** Execute \`docs/superpowers/plans/2026-10-12-explanatory-semantic-navigation-prototype.md\` and use its selected link/route behavior as the reference, not the illustrative fixture data.

## Global Constraints

- **Base is not main yet:** \`src/auteur/beginner/browser/studio.js\` is absent from \`main\` on 2026-10-12. The Studio PR stack #385–#392 is unmerged; #392 was last observed at \`d33bd2f4aa92b4ff6e29443859bf27751f7e0237\`. Resolve the exact current head and surrounding PRs before implementation; never blindly cherry-pick the stale stack.
- Keep the author-accepted story, working \`CanvasStore\` commands, Story Vision, \`genre_contracts\` review/apply, Story Realization and Quick Draft unchanged by **navigation**. No implicit accept, copy, re-generation or agent request.
- Treat all explanatory surfaces as views of **one existing architecture proposal**, not standalone story knowledge owners. Do not transplant synthetic paladin/hybrid fixture assertions into live stories.
- \`genre_contracts[].trope_functions[]\` and \`phases[].genre_activations[].trope_functions[]\` are **source-scoped phrases**; do not invent globally persistent trope IDs or automatic links.
- A genre-level \`emotion_target_ids\` relation never establishes a causal link from an individual trope to that emotion. Missing pack coverage remains unknown.
- Reuse the existing 12-step \`facetHistory\`, candidate request SHA and local focus preference; preserve graph pan/zoom/search/scope and working-note selection.
- The Studio is served by an explicit allowlist \`_RequestHandler._BROWSER_ASSETS\` in \`src/auteur/beginner/server.py\`. New browser scripts need explicit safe URLs in that allowlist and ordered script tags; do not assume arbitrary static assets are served.
- Scope reviews <=500 changed lines / <=12 files per PR, L1 focused tests by default; browser/persistence checks are the named L2 boundary.
- No production merge based solely on static grep tests or the independent prototype's inline Chromium screenshots.

## Review Focus

1. **No Studio on main / conflicting PR branch:** preflight must identify a valid exact source head and not clobber concurrent UX changes (Task 1).
2. **Source-local trope and absent pack:** a trope phrase in two genre contracts remains two attributed references; no bogus globally canonical trope or invented rule (Task 2).
3. **Navigation affects editor:** clicking a link in Architecture cannot change working notes, save count, scene caret or Story Realization selection (Tasks 4–5).
4. **Stale proposal / wrong source:** request SHA changes while traversing → explicit stale fallback, no accidental equivalent-title remapping (Tasks 2/5).
5. **Empty/detail/mobile:** no permanently empty inspector, no synthetic causal chain, no broken keyboard return or overflow at 390px (Tasks 3–5).

---

## File Map — integration only, not on prototype \`main\` branch

- Create \`src/auteur/beginner/browser/studio_explanations.js\`: browser-safe global \`window.AuteurStudioExplanations\` implementing read-only candidate/genre/phase projection and link resolution; no data writes.
- Create \`src/auteur/beginner/browser/studio_explanation_views.js\`: three lightweight explanatory renderers, source-status/context widgets, no external UI framework.
- Modify \`src/auteur/beginner/browser/studio.html\`: one Architecture hero region plus compact arrival/return context; ordered \`defer\` scripts before \`/studio.js\`.
- Modify \`src/auteur/beginner/browser/studio.css\`: responsive explanatory surface, link/focus states, graph-only Overview.
- Modify \`src/auteur/beginner/browser/studio.js\`: minimal integration through existing \`architectureFacet\`, \`visitFacet\`, \`facetHistory\`, inspector and focus.
- Modify \`src/auteur/beginner/server.py\`: register exact \`/studio_explanations.js\` and \`/studio_explanation_views.js\` assets in \`_BROWSER_ASSETS\`.
- Create \`tests/test_beginner_studio_explanation_navigation.py\`: HTTP delivery, DOM, authority, source and view-state behavior.
- Reuse \`tests/test_beginner_studio_ux_continuity.py\` and current architecture browser tests rather than duplicating their existing invariants.

## Required Adapter Boundary

\`window.AuteurStudioExplanations\` exposes:
- \`project(candidate, requestSha, packEvidence) -> ExplanationProjection\` (deterministic, read-only): genre anatomy, story-specific trope entries, source-defined structural links, phase/emotion references; pack evidence \`null\` is valid and visibly unknown.
- \`linksFor(projection, sourceRef) -> SemanticLink[]\` (read-only): genuine contract/phase/edge references only, with \`sourceRef\`, \`supportStatus\`, \`relationVerb\`, \`targetFacet\` and exact request SHA.
- \`resolve(projection, facet, key, expectedRequestSha) -> ResolvedTarget|null\`: reject unknown, stale or mismatched source identity; never match by text title.

\`window.AuteurStudioExplanationViews\` exposes:
- \`renderGenre(root,projection,genreId,onNavigate,onInspect)\`
- \`renderTrope(root,projection,sourceKey,onNavigate,onInspect)\`
- \`renderStructure(root,projection,sourceKey,onNavigate,onInspect)\`

The callbacks route through the existing Studio \`visitFacet(facet,key,nodeId)\`, augmented by an optional \`semanticLink\`/origin argument (do not introduce a second independent history). Emotions and Timeline retain their existing projections, with trusted target links where actually supported. The graph stays visible in \`Overview\`.

### Task 1: Source/currentness preflight and isolated Studio baseline

**Files:** No mutation in this task; create a feature branch/worktree from the correct current Studio head **only after verifying identity**.  
**Consumes:** current main, open PR ancestry #385–#392, tests, the merged prototype outcome.

- [ ] Step 1 — Verify workspace root, git common dir, HEAD, actual Studio file paths, PR merge state and whether any concurrent branch implemented this responsibility. If the baseline is obsolete, reconcile before selecting a branch.
- [ ] Step 2 — Run the smallest existing Studio test slice, including \`python -m pytest tests/test_beginner_studio_ux_continuity.py tests/test_beginner_studio_architecture_browser.py -q\` when those files exist on the chosen head. Record real failures, not historical expectations.
- [ ] Step 3 — Start the actual local \`BeginnerWorkspaceServer\` against a **disposable** workspace; verify \`/studio.html\`, \`/studio.js\`, \`/studio.css\`, Story Vision persistence and Architecture → Realization navigation at a real browser URL.
- [ ] Step 4 — Commit no code; record the chosen parent SHA and unresolved regressions in the eventual PR description. Stop/re-scope only if a material source/schema conflict makes the next task invalid.

**Acceptance:** A reproducible current Studio baseline exists; no assumption that prototype code is already integrated into it.

### Task 2: Adapt existing architecture data into safe explanation/link records

**Files:** Create \`studio_explanations.js\`; Test \`tests/test_beginner_studio_explanation_navigation.py\`.  
**Consumes:** actual candidate fields (\`nodes\`, \`links\`, \`genre_contracts\`, \`emotion_targets\`, \`genre_interactions\`, \`phases\`) and request SHA.  
**Produces:** \`project\`, \`linksFor\`, \`resolve\` as above.

- [ ] Step 1 — Write failing tests \`test_source_scoped_trope_phrases_do_not_merge\`, \`test_genre_target_is_not_trope_emotion_edge\`, \`test_missing_pack_stays_unknown\`, \`test_changed_request_sha_invalidates_links\`, \`test_only_declared_edges_receive_relationship_verbs\`. Use candidate packets from existing Studio tests, not invented permanent IDs.
- [ ] Step 2 — RED: \`python -m pytest tests/test_beginner_studio_explanation_navigation.py -q\` fails on missing adapter.
- [ ] Step 3 — Implement a small read-only adapter. Use source paths \`genre_contracts/<genreId>/trope_functions/<index>\`, \`phases/<phaseId>/...\`, \`nodes/<id>\` and existing edge endpoints; \`requestSha\` scopes identities. Reuse normalized Genre Pack/legacy evidence only if *actually delivered*; absent evidence is explicit, not inferred.
- [ ] Step 4 — GREEN: rerun focused pytest and JS syntax check; test a reused phrase under two different genres.
- [ ] Step 5 — Commit adapter + tests, keeping this self-contained and reviewable.

**Acceptance:** Every displayed relationship can be traced to source identity; none implies accepted story facts or an invented genre requirement.

### Task 3: Integrate distinct Genres/Tropes/Structure heroes

**Files:** Create \`studio_explanation_views.js\`; modify \`studio.html\`, \`studio.css\`, \`server.py\`, \`studio.js\`; Test \`tests/test_beginner_studio_explanation_navigation.py\`.  
**Consumes:** Task 2 projection and the merged prototype's chosen three visual grammars.

- [ ] Step 1 — Write failing HTTP asset and DOM tests \`test_extra_scripts_are_served_with_expected_mime\`, \`test_one_active_hero_per_facet\`, \`test_overview_keeps_real_spatial_graph\`, \`test_inspector_is_closed_until_inspection\`. Verify \`/studio_explanations.js\` and \`/studio_explanation_views.js\` are initially unavailable.
- [ ] Step 2 — RED: run focused pytest and confirm the missing asset/view failures.
- [ ] Step 3 — Serve two explicitly allowlisted scripts; load both with \`defer\` before \`studio.js\`. Render Anatomy when \`state.architectureFacet==="genres"\`, Convention view for \`"tropes"\`, and source-backed Mechanism Map for \`"structure"\`. Keep \`"overview"\` as existing graph, \`"timeline"\` as compact phases, \`"emotions"\` as its own projection. No duplicate permanent inspector or new schema.
- [ ] Step 4 — GREEN: HTTP pytest, JS parse, and real-browser facet switching. Confirm graph isn't merely dimmed under explanatory heroes and \`[hidden]\` components don't take space.
- [ ] Step 5 — Commit one or several PR-sized changes; separate server/asset plumbing from large renderers if review cap requires.

**Acceptance:** The same live proposal powers distinct explanatory heroes and the spatial Overview.

### Task 4: Link-driven cross-facet navigation and meaning-on-arrival

**Files:** Modify \`studio.js\`, \`studio.html\`, \`studio.css\`, \`studio_explanation_views.js\`; Test \`tests/test_beginner_studio_explanation_navigation.py\`.  
**Consumes:** \`linksFor\`, \`resolve\`, existing \`visitFacet\` and \`facetHistory\`.  
**Produces:** \`visitSemanticLink(link)\` within Studio, extending \`visitFacet\` rather than replacing it.

- [ ] Step 1 — Write failing tests \`test_genre_trope_structure_links_in_order\`, \`test_back_restores_search_scope_phase_and_selection\`, \`test_arrival_context_shows_actual_verb_and_source\`, \`test_multiple_genres_have_distinct_breadcrumbs\`, \`test_link_does_not_open_edit_fields\`.
- [ ] Step 2 — RED: run focused Studio navigation tests.
- [ ] Step 3 — On click validate destination+SHA, push existing focus snapshot, navigate to correct facet, and show **one compact** "From X → verb → Y · source/status" bar with previous-context action. Cap history at 12, show up to 3 breadcrumb hops with accessible overflow. On Back restore original scope, search, phase, neighborhood, selected item, and focus. Explicit \`Inspect source\` remains separate; no automatic edit, accept or agent calls.
- [ ] Step 4 — GREEN: focused pytest plus real-browser keyboard/mouse path "Genre → Trope → Structure → Back → Back". Include a direct attempted unsupported link: no fake destination.
- [ ] Step 5 — Commit navigation behavior in a scoped PR.

**Acceptance:** Authors traverse meaningful source-derived relations without disorientation or authority crossing.

### Task 5: Persistence, stale source and actual-browser regression

**Files:** Modify only necessary narrow fixes in \`studio.js\`, \`studio.css\`, or tests after reproduction.  
**Consumes:** exact implementation head and disposable local Story Vision/working canvas.

- [ ] Step 1 — Add RED regressions for stale/replaced \`candidate_request_sha256\`, removed source ID, switching to Realization with an edited working note, and reopening Architecture after navigation.
- [ ] Step 2 — Implement minimal fixes: drop only obsolete navigation references; visibly explain stale source; never map by identical title; preserve working selection/editor focus and unchanged save revision when only following read-only links.
- [ ] Step 3 — GREEN: run \`python -m pytest tests/test_beginner_studio_explanation_navigation.py tests/test_beginner_studio_ux_continuity.py -q\` and the relevant architecture browser tests at the current head.
- [ ] Step 4 — Real served-browser regression: desktop 1440x900, 900x700, mobile 390x844, keyboard-only/Tab/Enter/Back, visible focus/contrast, large multi-genre packet, unknown links, Story Vision save/reopen, no accidental proposal apply/accept. Note actual testing environment rather than claim a mock is real.
- [ ] Step 5 — Re-read \`main\`/PR ancestry, reconcile the stack and exact SHA before integration/merge. Capture failures and repair evidence. Do not launch paid broad CI purely for this UX iteration; L3 only at a named release candidate.

**Acceptance:** The real Studio satisfies the paladin and hybrid semantic-navigation acceptance journeys without story loss or authority mutation.

## Execution and Merge Boundary

Execute the merged prototype navigation first (separate plan). Next, independently confirm the original Studio PR stack's currentness. Build against its **actual head**, not \`main\` until Studio has landed there. Once both baseline and new implementation are verified, integrate the Studio stack in correct dependency order; report separately which PRs landed and which remain drafts. Do not equate merging research prototypes with shipping these views to the actual Studio.

**Not in scope:** optional hover/focus previews, new Genre Packs, global deep links for private canvas documents, new narrative ontology, analytics, acceptance policy changes or agent-generation prompt changes.
