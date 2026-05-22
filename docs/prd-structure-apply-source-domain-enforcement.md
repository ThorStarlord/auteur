# PRD: Enforce Proposal Source Domain In Structure Apply

Status: Approved
Date: 2026-05-13
Source: docs/archived/superpowers/specs/2026-05-13-structure-apply-source-domain-grill.md

## Problem Statement

`StructureProposal` artifacts are now self-describing via `source_domain`, but `auteur structure apply` does not yet enforce command ownership at runtime. This leaves a contract gap where a Bible audit Decision Packet can be passed to the structure apply path, risking incorrect workflow usage and confusion for future agents and authors.

## Solution

Add an ownership guard to `auteur structure apply` so proposals with `source_domain: bible_audit` are rejected before any blueprint load/apply behavior. The command must return exit code `1`, emit a clear guidance message to stderr, and leave the source blueprint unchanged.

## User Stories

1. As an author, I want `auteur structure apply` to reject Bible audit proposals, so that I do not use the wrong resolution path.
2. As an author, I want the rejection message to tell me the correct command, so that I can recover immediately.
3. As an author, I want rejection to happen before any mutation logic, so that my story spine is protected.
4. As a maintainer, I want ownership enforcement at CLI boundary, so that command intent is executable behavior and not just documentation.
5. As a maintainer, I want legacy proposals with missing `source_domain` to continue working, so that existing YAML artifacts remain backward-compatible.
6. As a future agent, I want fixture coverage for this rejection behavior, so that regressions are detected in CI.
7. As a future agent, I want the test to assert blueprint immutability on rejection, so that contract safety is explicit.
8. As a reviewer, I want this slice to be isolated from analyzer/schema expansion work, so that risk stays low.

## Implementation Decisions

- Place enforcement in the CLI command handler for `structure apply`.
- Evaluate `proposal.source_domain` after proposal validation and before blueprint loading.
- Reject only `"bible_audit"` for this slice.
- Keep `None` permissive for backward compatibility.
- Use a direct stderr message that references `auteur audit --accept ... --option ...`.
- Keep scope to one tiny vertical slice; no schema or proposal-generation changes.

## Testing Decisions

- Good tests validate observable CLI behavior through `main([...])`.
- Add one tracer-bullet test in fixture workflow tests:
  - proposal YAML has `source_domain: bible_audit`
  - `main(["structure", "apply", ...]) == 1`
  - stderr indicates Bible audit proposals must use audit acceptance path
  - source blueprint content is unchanged
- Keep existing workflow fixture tests intact to ensure no behavior regressions for structure proposals.

## Out of Scope

- Changing `StructureProposal` schema again.
- Enforcing rejection for unknown string source domains.
- Rejecting legacy `source_domain: null` proposals.
- Moving `bible_audit.py` modules.
- New analyzer rules or LLM-driven behavior.

## Further Notes

This PRD directly operationalizes ADR 002 by turning command ownership from documented guidance into deterministic runtime behavior at the CLI boundary.
