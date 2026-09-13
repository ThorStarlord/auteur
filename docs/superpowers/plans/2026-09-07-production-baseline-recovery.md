# Production Baseline Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the unauthorized future-roadmap prototype from the production baseline while preserving the authorized atomic-write change and independent Pack Effect preregistration.

**Architecture:** Reconstruct the intended tree from the live remote `main` using a new corrective branch. The target keeps the pre-prototype production parent (`c75277a`), reapplies the authorized atomic-write commit (`915c124`), and reapplies the independent experiment preregistration (`8f2bca8`) without retaining prototype-dependent follow-up edits.

**Tech Stack:** Git worktrees, Git history inspection, Python/pytest repository checks.

---

### Task 1: Establish the clean recovery baseline

**Files:** None.

- [ ] Verify the worktree root, Git common directory, branch, and exact starting SHA.
- [ ] Run the repository’s focused baseline tests covering serializers, story-design packs, discovery review, and the experiment harness.
- [ ] Record any baseline failures separately from recovery changes.

### Task 2: Remove the unauthorized prototype payload

**Files:** The files introduced or altered by `e3db1a1`, excluding the authorized commits listed below.

- [ ] Reconstruct the tree so the future Tutor, learning, reasoning, narrative-intelligence, counterfactual, and series-context implementation files are absent.
- [ ] Restore the stress harness and dense-trilogy research document deleted by the prototype checkpoint.
- [ ] Remove the prototype status/design/research files from production history; their content remains recoverable from commit `844fc84` if later authorized separately.
- [ ] Remove prototype-only built-in packs and registry/test expectations for `rivals_allies` and `investigation`.
- [ ] Remove the prototype root `tutor` command and related CLI/model/session integrations.

### Task 3: Preserve authorized work on top of the clean baseline

**Files:** `src/auteur/cli_serializers.py`, `tests/test_cli_serializers.py`, and `experiments/story-design-pack-effect-v1/**`.

- [ ] Preserve the atomic Story Identity write and its regression tests from `915c124`.
- [ ] Preserve the independently based Pack Effect preregistration from `8f2bca8`.
- [ ] Drop `08eb279`’s test-only expectation for prototype-added packs because those packs are not part of the recovered V1 baseline.
- [ ] Keep the resulting diff bounded to baseline recovery; do not revise M1 issue files in this branch.

### Task 4: Verify and document the recovered boundary

**Files:** `docs/superpowers/plans/2026-09-07-production-baseline-recovery.md`.

- [ ] Confirm `git diff` contains no future-prototype files, no protected-file edits, and no issue files beyond the existing `0002` file.
- [ ] Run focused tests and the repository’s applicable full source checks.
- [ ] Confirm the recovered tree contains the atomic-write behavior, the independent experiment, and the restored stress assets.
- [ ] Report the exact recovery commit SHA and all test categories/results; publication or merge remains a separate authorization step.
