# Living Story Studio Focused Unfolding Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Combine author-directed, focus-local suggestion/Adopt behavior with the existing live spatial graph, explanatory lenses, and source-bound host-agent architecture workflow.

**Architecture:** Compose the standalone unfolding model into Studio's graph presentation. Work stays owned by existing CanvasStore / source candidate. Reuse `visitFacet`, `facetHistory`, local focus and explicit asset allowlist; do not introduce a rival router or paid provider runner.

**Tech Stack:** Vanilla browser JS/CSS, Python BeginnerWorkspaceServer, CanvasStore, `node:test`, pytest, Chromium.

**Spec:** `docs/superpowers/specs/2026-10-12-focused-unfolding-authoring-explanation-design.md`

## Global Constraints

- Studio UX lineage #386–#392, explanatory integration #401–#403 are draft/unmerged; **verify exact current heads and dependency ancestry** before editing. `main` does not contain real Studio UX.
- Graph remains the primary Overview. Genre/Trope/Structure perspectives are semantic lenses; proposals are not new canonical story knowledge.
- Focus, selection and semantic links never save authoring data. Explicit Adopt is the only write transition; accepted story requires separate review.
- Immediate suggestions are selected from existing valid proposal/source evidence. No silent model call or fabricated genre convention; offer explicit `Develop more possibilities` host-agent handoff.
- Browser assets require `_RequestHandler._BROWSER_ASSETS` whitelist in `src/auteur/beginner/server.py`.
- All work segmented <=500 changed lines/12 files per PR. Do not merge an unqualified stacked Studio ancestor as a side effect.

## Review Focus

1. Missing architecture candidate: show optional starting invitation and usable local manual authoring, no false AI suggestions.
2. Stale request SHA / focus or canvas ID switching: old proposal branches can't be adopted into wrong story.
3. Working-note editing / open scene caret: switching workspace or following a ghost doesn't lose unsaved text.
4. Double Adopt and server write conflict: reject duplication and false success; restore recoverable working UI.
5. Dense graph / 390px / keyboard: at most 3 local ghosts (2 mobile), navigation and inspectors don't compete for space.

## File Map

- Create `src/auteur/beginner/browser/studio_unfolding.js`: selection projection and focus-local ghost renderer orchestration against exact request SHA; no direct save.
- Modify `src/auteur/beginner/browser/studio.js`: selection, overlays, explicit Adopt callback to CanvasStore, host-agent request handoff, focus continuity.
- Modify `src/auteur/beginner/browser/studio.html` and `studio.css`: compact controls and local overlays, accessible narration, mobile layout.
- Modify `src/auteur/beginner/server.py`: explicit asset whitelist and only necessary route mapping.
- Create `tests/test_studio_unfolding_integration.mjs` and `tests/test_beginner_studio_unfolding.py`: source-ID/persistence/browser handoff regression.
- Reuse existing `src/auteur/beginner/browser/studio_explanations.js` and existing continuity tests.

### Task 1: Exact-head baseline and local suggestion projection

**Files:** `studio_unfolding.js`, `tests/test_studio_unfolding_integration.mjs`

- [ ] Verify current `main`/Studio PR heads, working tree identity and smallest existing Studio test slice; use a clean feature branch from the correct descendant of #403.
- [ ] RED tests for genuine declared neighbor projection, no pack-as-truth and bounded 2–3 items, source SHA mismatch, adopted/dismissed exclusion.
- [ ] Implement `projectLocalSuggestions(candidate, sourceSha, focus, workingItems, dismissed, limit)`, returning honest source-local ghosts with no provider calls.
- [ ] GREEN in Node and existing source unit tests; commit.

### Task 2: Graph focus-local presentation and author journeys

**Files:** `studio.js`, `studio.html`, `studio.css`, `server.py`; same focused tests.

- [ ] RED tests for working emotion-first optional invitation, alternative starts, suggestion provenance, local ghost focus switch, graph retained in Overview, compact explainer, no automatic inspector edits.
- [ ] Implement helper script allowlist/load order, ghost cards near focus, click-to-explain, dismiss, Adopt trigger and bounded alternatives UI; do not mutate `state.items` on ghost exploration.
- [ ] GREEN in actual browser at 1440x900, 900x700, 390x844; test noncanonical Story Realization focus preservation; commit.

### Task 3: Durable adoption and source-bound host-agent handoff

**Files:** `studio.js` / relevant tests; consumes adoption command from sibling plan.

- [ ] RED tests for first adoption persists after reload, double-click cannot duplicate, exact revision conflict surfaces explicit error without disappearing ghost, valid origin pointer, stale focus refused.
- [ ] Implement one explicit authoritative CanvasStore adoption call, await response before claiming success, then refresh working nodes; neither follow nor dismiss calls the API.
- [ ] RED tests for "Develop more possibilities" creating only a bounded focus/revision-specific handoff request, never executing a provider implicitly.
- [ ] Implement existing host-agent request preparation and stale-response rejection; GREEN with real server tests; commit.

### Task 4: Adversarial integration qualification and merge decisions

**Files:** regression fixes + docs only.

- [ ] Run entire targeted store/navigation/Studio suite, real served-browser with source agent packet, selection/caret, back trail, change of author emotion, dense candidate, unknown source, duplicate Adopt, restoration and no accepted-story mutation.
- [ ] Verify actual server/JS asset MIME, full HTTP behavior, and no request on render; compare source SHA and revision in each writable callback.
- [ ] Open reviewable PRs with exact-head and test evidence; merge only after current Studio ancestor chain and these integration tests qualify. Otherwise retain draft and identify the precise unresolved test/boundary.
