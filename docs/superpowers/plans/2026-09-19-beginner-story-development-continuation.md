# Beginner Story Development Continuation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Carry an accepted Beginner Workspace foundation through outline review, Chapter 1 planning, lightweight scene planning, first-draft handoff, and post-draft orientation without silently mutating canonical story state.

**Architecture:** Add a small continuation projection and persistence model owned by `auteur.beginner`. It adapts accepted StoryIdentity/Structure references and existing project artifacts into derived proposals, records explicit author acceptance in the workspace session, and exposes existing Cartographer/draft operations as named next actions. Outline and chapter-plan artifacts remain proposals until acceptance; scene plans are planning inputs and only become realization candidates after explicit review.

**Tech Stack:** Python 3.11+, Pydantic v2, existing BeginnerWorkspaceApplication/server/browser, existing Cartographer outline models/compiler, pytest.

---

### Task 1: Reconcile status and record the milestone

**Files:**
- Modify: `STATUS.md`
- Create: `docs/design/2026-09-beginner-story-development-continuation.md`
- Test: `tests/test_beginner_story_development_docs.py`

- [ ] **Step 1: Write the failing documentation contract test** asserting the selected milestone, deferred L3/human qualification posture, and Structure → Realization boundary are named.
- [ ] **Step 2: Run the focused test and verify it fails because the new milestone is absent.**
- [ ] **Step 3: Update the status and design documents with the bounded milestone and artifact authority rules.**
- [ ] **Step 4: Run the focused test and verify it passes.**

### Task 2: Add continuation contracts and persistence

**Files:**
- Modify: `src/auteur/beginner/contracts.py`
- Modify: `src/auteur/beginner/persistence.py`
- Create: `src/auteur/beginner/continuation.py`
- Test: `tests/test_beginner_story_development_contracts.py`

- [ ] **Step 1: Write failing model tests for outline proposals, chapter plans, scene plans, draft readiness, explicit acceptance, and strict round-trip persistence.**
- [ ] **Step 2: Run the focused tests and verify the new types/fields are missing.**
- [ ] **Step 3: Implement minimal Pydantic contracts and add an optional continuation payload to `SessionEnvelope`; preserve strict validation and atomic store behavior.**
- [ ] **Step 4: Run the focused tests and verify they pass.**

### Task 3: Build the Structure → Outline adapter

**Files:**
- Modify: `src/auteur/beginner/application.py`
- Modify: `src/auteur/beginner/projections.py`
- Test: `tests/test_beginner_story_development_application.py`

- [ ] **Step 1: Write failing tests that require accepted Structure before outline generation, produce a derived proposal from project blueprint/Cartographer output, and keep canonical files unchanged.**
- [ ] **Step 2: Run the focused tests and verify they fail.**
- [ ] **Step 3: Implement proposal generation, review, and explicit outline acceptance commands using the existing outline validator/model; never overwrite `blueprint.yaml` or `story_identity.yaml`.**
- [ ] **Step 4: Add projection fields and next actions for foundation-ready, outline-review, and outline-accepted states.**
- [ ] **Step 5: Run the focused tests and verify they pass.**

### Task 4: Add guided Chapter 1 and scene planning

**Files:**
- Modify: `src/auteur/beginner/application.py`
- Modify: `src/auteur/beginner/projections.py`
- Modify: `src/auteur/beginner/server.py`
- Test: `tests/test_beginner_story_development_application.py`
- Test: `tests/test_beginner_story_development_server.py`

- [ ] **Step 1: Write failing tests for Chapter 1 purpose/threads/setup/payoff/reader-outcome fields, explicit plan acceptance, lightweight scene cards, and realization-boundary wording.**
- [ ] **Step 2: Run the focused tests and verify they fail.**
- [ ] **Step 3: Implement deterministic chapter-plan and scene-plan derivation from the accepted outline, plus explicit review/accept commands.**
- [ ] **Step 4: Expose the new commands and projection data through the existing JSON API.**
- [ ] **Step 5: Run the focused application/server tests and verify they pass.**

### Task 5: Connect draft readiness and post-draft orientation

**Files:**
- Modify: `src/auteur/beginner/application.py`
- Modify: `src/auteur/beginner/projections.py`
- Modify: `src/auteur/beginner/server.py`
- Modify: `src/auteur/beginner/browser/app.js`
- Modify: `src/auteur/beginner/browser/index.html`
- Test: `tests/test_beginner_story_development_application.py`
- Test: `tests/test_beginner_story_development_server.py`
- Test: `tests/test_beginner_story_development_browser.py`

- [ ] **Step 1: Write failing tests for draft readiness, explicit draft handoff, and navigator states after a draft exists.**
- [ ] **Step 2: Run the focused tests and verify they fail.**
- [ ] **Step 3: Implement a draft handoff that records the exact accepted inputs and points to the existing `auteur draft <project> 1` operation; do not invoke an LLM from the read-only workspace API.**
- [ ] **Step 4: Render the continuation navigator and recommended next step in the beginner browser.**
- [ ] **Step 5: Run focused tests and verify they pass.**

### Task 6: Verification and evidence

**Files:**
- Modify: `STATUS.md`
- Create: `docs/engineering/beginner-story-development-continuation-verification.md`

- [ ] **Step 1: Run the focused continuation tests and the existing Beginner Workspace suite.**
- [ ] **Step 2: Run the repository validation command required by the release policy for the changed boundary.**
- [ ] **Step 3: Record exact SHA, test categories, and any deferred L3/human qualification evidence.**
- [ ] **Step 4: Review the diff for unrelated changes and document the implemented boundary.**
