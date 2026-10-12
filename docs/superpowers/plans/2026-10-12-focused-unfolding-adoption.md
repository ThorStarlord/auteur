# Durable Working Architecture Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let authors explicitly adopt source-attributed unfolding suggestions into durable, editable **noncanonical** working architecture without losing existing canvases or revising story authority.

**Architecture:** Extend existing CanvasStore `CanvasItem` with nullable working architecture metadata, not a second story owner. Apply adoption using the existing revisioned/idempotent command surface; enforce source-local duplicate rejection and return exact persisted item/revision.

**Tech Stack:** Pydantic v2, Python >=3.11, pytest, existing BeginnerWorkspaceServer and CanvasStore.

**Spec:** `docs/superpowers/specs/2026-10-12-focused-unfolding-authoring-explanation-design.md`

## Global Constraints

- `src/auteur/beginner/studio_store.py` is the working document owner. Never mutate accepted story identity from navigation/adoption.
- Preserve existing `CanvasItem.kind` enum `note|character|scene|place|question`; add optional `architecture_role` and `proposal_origin` only.
- Preserve backward compatibility, old exported documents, deleted-item recovery, exact revision checks, and 200-item/500-connection limits.
- A failed or conflicting save is **not** an adopted item; show retry/error. No invisible copying on Explore or focus.
- Source revision or authored-intent change invalidates unadopted suggestions, **not** author-owned nodes.
- Scope changes in PRs <=500 changed lines / 12 files and verify using local Python tests (no paid CI assumption).

## Review Focus

1. Old working canvas JSON without added keys loads unchanged and round-trips.
2. Same suggestion clicked twice or after retry never creates two working items.
3. Concurrent expected-revision conflict fails atomically; no success claim.
4. Invalid/oversized source identifier, role, or title is rejected by existing validation limits.
5. Source SHA changes after adoption: origin remains historical; editable working item remains.

## File Map

- Modify `src/auteur/beginner/studio_store.py`: optional working metadata and explicit idempotent adoption command (if a new command is proven necessary).
- Create `tests/test_studio_focused_unfolding_store.py`: schema, old docs, duplicate, stale, revision and no accepted-story writes.
- Modify `src/auteur/beginner/server.py` only if an explicit atomic adoption endpoint is needed; otherwise use existing `replace-working-document`.
- Add route/HTTP test to `tests/test_beginner_studio_explanation_navigation.py` if the server surface changes.

### Task 1: Backwards-compatible working architecture metadata

**Files:** `studio_store.py`, `tests/test_studio_focused_unfolding_store.py`
**Interface:** `CanvasItem.architecture_role: Literal[...] | None`, `CanvasItem.proposal_origin: ProposalOrigin | None` (bounded `source_request_sha`, `source_ref`, `source_kind`).

- [ ] RED tests: old canvas loads with nullable fields; valid typed origin round-trips; unknown kind/role and overly long origin reject; working metadata never signals canon.
- [ ] Run `python -m pytest tests/test_studio_focused_unfolding_store.py -q` RED.
- [ ] Implement only nullable Pydantic fields / typed provenance; preserve existing item kinds and defaults.
- [ ] GREEN + pre-existing CanvasStore tests; commit.

### Task 2: Transactional, duplicate-safe adoption

**Files:** `studio_store.py`, same tests; `server.py` only if required.
**Interface:** `CanvasStore.apply("adopt-suggestion", expected_revision, command_id, payload)` where payload contains validated item and position, with a source-local duplicate key. Keep existing atomic save/replay guarantee.

- [ ] RED tests: first adoption increments revision once; same command replay doesn't duplicate; different command same source identity is rejected; another user's revision conflict is atomic; failed validation changes nothing; no acceptance API called.
- [ ] Implement minimal command path following existing `add-item` transaction and idempotency; respect item caps and deleted item restoration rules.
- [ ] GREEN on focused tests + existing store/HTTP suite. If `add-item` with a stable op/source guard already satisfies all checks, prefer reusing it and document no new action.
- [ ] Commit.

### Task 3: Persistence and authoritative integration handoff

**Files:** test corrections and source documentation.

- [ ] Run full existing store tests and new tests with real file reload; test deleting/restoring an adopted item and editing its content without losing historical origin.
- [ ] Check competing PR changes and exact request/revision; open small draft PRs based on current Studio branch #403 (not on `main` while Studio remains unmerged).
- [ ] Attach exact-head test logs and source-to-request boundaries. Do not merge to `main` before original Studio stack is qualified; do not imply browser integration from schema tests.
