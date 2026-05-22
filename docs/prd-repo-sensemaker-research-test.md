# PRD: Repo Sensemaker Research-Test Hardening

Status: Approved (auto-approved)
Date: 2026-05-14
Input: docs/archived/superpowers/plans/2026-05-14-grill-with-docs-repo-sensemaker.md

## Problem Statement

The repository has strong structure and workflow logic, but the weakest contract boundary is at repository entry: README status wording can drift from implemented behavior. In addition, the draft repo-sensemaker process references documentation assets that are not currently present in-repo, making reproducible diagnosis dependent on implicit knowledge.

## Solution

Harden repository sensemaking as an in-repo, testable workflow by:
- Aligning README capability/status statements to current implemented behavior.
- Adding in-repo reference documents used by repo-sensemaker output contracts.
- Introducing deterministic repository validation checks and tests for these boundaries.

## User Stories

1. As a maintainer, I want README capability claims to match actual CLI behavior, so that contributors and agents do not make wrong implementation assumptions.
2. As an agent, I want required repo-sensemaker references to exist in-repo, so that diagnostic output format is consistent and reproducible.
3. As a reviewer, I want automated checks for documentation-contract drift, so that stale claims are caught in CI/local runs.
4. As a contributor, I want a clear weakest-boundary diagnosis framework, so that next-step prioritization is concrete and evidence-based.
5. As a maintainer, I want validation scripts to fail with actionable messages, so that remediation is fast.
6. As an agent operator, I want local issue slices that can be executed without issue-tracker publishing, so that workflow experiments can happen safely in-repo.
7. As a project lead, I want deterministic checks over subjective "vibe" assessments, so that repository decisions are auditable.
8. As a new collaborator, I want references that define weakness types and evidence rules, so that diagnostics are comparable across sessions.

## Implementation Decisions

- Create a docs-backed contract for repo-sensemaker references under docs/references.
- Treat README status statements as contract text; regressions are test failures.
- Add a deterministic validator entrypoint for documentation-boundary checks.
- Keep workflow recommendation local to existing repo conventions (next-step-discovery) unless workflow-orchestrator is introduced.
- Preserve existing domain vocabulary from CONTEXT.md and AGENTS.md.

## Testing Decisions

- Good tests assert observable repository contracts (text claims and file existence), not helper internals.
- Modules to test:
  - Repository contract validator behavior (pass/fail + messages).
  - README stale-claim guard.
  - Presence of required reference docs.
- Prior art:
  - CLI contract tests and workflow fixture tests under tests/test_cli.py and tests/test_structure_workflow_fixture.py.

## Out of Scope

- Publishing issues to GitHub.
- Introducing a new workflow-orchestrator subsystem.
- Deep redesign of structure engine internals.
- New ADRs for this documentation/validation hardening slice.

## Further Notes

This PRD intentionally favors small, AFK-executable slices that harden boundaries without architectural churn.
