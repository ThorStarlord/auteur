# Focused Unfolding Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a realistic standalone, graph-first interaction prototype combining progressive authoring and explanation with 2–3 focus-local ghost suggestions.

**Architecture:** Keep a pure suggestion selector/state reducer separate from the browser presentation. Reuse the merged proposal fixtures solely as illustrative source data. Never imply fixture adoption updates Studio or accepted story.

**Tech Stack:** Browser ES modules, CSS, `node:test`, Python pytest + Playwright/Chromium for UI qualification.

**Spec:** `docs/superpowers/specs/2026-10-12-focused-unfolding-authoring-explanation-design.md`

## Global Constraints

- Emotion-first is optional, not a required step; any idea can be the starting anchor.
- Only 2–3 current-focus provisional suggestions are visible (2 on 390px mobile), with explicit "More alternatives".
- "Explore" is read-only. "Adopt" affects only the prototype's noncanonical working model. "Dismiss" hides just that ghost.
- No provider calls, story-canon mutation, invented genre rules, or trope→emotion causal assertions.
- Keep a graph as the hero; reserve explanations for a contextual focus region; no permanent competing side rails.
- Each changeset uses <=500 diff lines and <=12 files; use focused test runs.

## Review Focus

1. No pre-existing selected concept: actionable emotion-first invitation and equally usable "Start elsewhere".
2. Empty or unrelated evidence: no invented relationship; explanatory empty state.
3. Repeated Adopt and revisiting focus: no duplicate working node; ghosts do not accumulate globally.
4. Narrow viewport / dense graph: <=2 ghosts at 390px, no page overflow, collapse is reversible.
5. Replaced candidate/source revision: old unadopted ghost is not silently shown/adopted as current evidence.

## File Map

- Create `docs/prototypes/focused-unfolding/model.mjs`: `createDemoState`, `selectFocus`, `suggestForFocus`, `inspectGhost`, `adoptGhost`, `dismissGhost`, `collapseCluster`; pure and deterministic.
- Create `docs/prototypes/focused-unfolding/model.test.mjs`: Node assertions.
- Create `docs/prototypes/focused-unfolding/index.html`, `app.mjs`, `styles.css`: one graph + suggestion/inspector/toolbar surfaces.
- Create `tests/test_focused_unfolding_browser.py`: actual Chromium interaction screenshots/keyboard/mobile tests.
- Create `docs/prototypes/focused-unfolding/README.md`: run commands and epistemic limits.

### Task 1: Pure focus and suggested-neighbor model

**Files:** `model.mjs`, `model.test.mjs`
**Interface:** `createDemoState(story)` returns `{nodes,edges,focusId,ghosts,adoptedIds,dismissed,collapsed,revision}`; `suggestForFocus(state,limit=3)` returns only source-declared/demonstrably labelled hypothetical local suggestion objects.

- [ ] Write tests: empty focus; 2–3 local suggestions; repeated focus switch removes previous ghosts; no duplicate already-adopted proposals; multiple genre scopes remain separate; missing evidence never creates a verified rule.
- [ ] Run `node --test docs/prototypes/focused-unfolding/model.test.mjs` and verify RED.
- [ ] Implement minimal immutable selector with stable source-local IDs and typed `provenance`.
- [ ] Re-run tests GREEN; commit pure model/tests.

### Task 2: Adoption, dismissal, stale and cluster state

**Files:** `model.mjs`, `model.test.mjs`
**Interfaces:** `selectFocus(state,id)`, `adoptGhost(state,ghostId)`, `dismissGhost(state,ghostId)`, `collapseCluster(state,id,collapsed)`, `replaceSourceRevision(state,rev)`.

- [ ] RED tests: adoption is noncanonical and idempotent, does not imply accepted status; dismissal doesn't remove author nodes; source change invalidates ghosts but preserves adopted nodes; collapse loses no node/edge.
- [ ] Run focused Node tests RED, implement pure transitions, rerun GREEN; commit.

### Task 3: Interactive spatial graph and concise explanations

**Files:** `index.html`, `app.mjs`, `styles.css`
**Interfaces:** browser action handlers use only Task 1–2 reducer, never write to real CanvasStore.

- [ ] RED browser test for emotion-first and alternative entry, clicking node focuses correct 2–3 dashed suggestions, inspecting reveals why/source, adopting creates persistent-looking working node and updates graph.
- [ ] Implement central graph canvas with local anchored ghost branches and compact contextual explainer. Make Explore, Adopt, Dismiss and Alternatives real controls; distinguish "Working / not canon" from "AI hypothesis".
- [ ] Run browser test GREEN and check no page errors; commit.

### Task 4: Density, keyboard and navigation

**Files:** `app.mjs`, `styles.css`, `tests/test_focused_unfolding_browser.py`

- [ ] RED tests for switching focus clearing ghosts, collapsible working groups, keyboard focus, 390px two-ghost bound and no horizontal overflow; test unknown ID.
- [ ] Implement proportional mobile layout and reversible presentation-only collapse; preserve keyboard interaction and high-contrast focus.
- [ ] GREEN on desktop 1440x900, intermediate 900x700 and mobile 390x844; commit.

### Task 5: Final falsification and prototype delivery

**Files:** `README.md`, targeted regression corrections only.

- [ ] Test paladin emotion → trope → structure journey; alternate premise-first; stale source; repeated Adopt; dismissal; dense graph/collapse; no silent network calls.
- [ ] Run `node --test docs/prototypes/focused-unfolding/*.test.mjs`, `python -m pytest tests/test_focused_unfolding_browser.py -q`, `node --check` for every module.
- [ ] Attempt actual served static page and browser. If policy blocks HTTP/local file navigation, use exact-source inline harness but **record lower confidence**.
- [ ] Open small reviewed PRs; verify remote file text exactly matches tested source; merge isolated concept work if green. Do **not** declare it integrated into live Studio.
