---
name: tdd
description: execute implementation work from an agent_brief using strict RED-GREEN-REFACTOR cycles. writes failing tests first, implements minimal code to pass them, then refactors. produces a code_patch artifact.
---

# tdd

Implements features from an `agent_brief` using Test-Driven Development. Follows the RED → GREEN → REFACTOR cycle strictly, one issue at a time in the execution order defined by the brief.

## Workflow

1. **Consume Brief**: Read `agent_brief.md`. Note execution order, TDD entry points, and clarification flags.
2. **Resolve Flags**: For each `needs_clarification` flag, apply the documented default and note it.
3. **Issue Loop**: For each issue in execution order:
   a. **RED**: Write the failing test(s) as specified in `tdd_entry_point`. Run the test suite — confirm the new test(s) fail and all existing tests still pass.
   b. **GREEN**: Implement the minimal code to make the failing test(s) pass. No more code than needed.
   c. **VERIFY**: Run the full test suite — confirm all tests pass.
   d. **REFACTOR**: Clean up implementation if needed. Re-run tests.
4. **Produce Code Patch**: Write `code_patch.md` artifact summarizing all changes.

## Output Format

Every response must produce changes to source files and tests, then produce a `code_patch` artifact.

**CRITICAL**: The `code_patch` artifact MUST include the **Machine-Readable Handoff** YAML block with `source_intent_ref`. Patches without this block violate the artifact contract.

## Boundary Rules

1. **No test skipping**: Never skip a RED phase. The test must fail before implementation begins.
2. **Minimal GREEN**: Implement only what is needed to pass the specified tests. Do not add features not in the issue's acceptance criteria.
3. **One issue at a time**: Complete RED → GREEN → VERIFY for one issue before moving to the next.
4. **No scope expansion**: If implementation reveals a needed change not in the issue list, flag it in the code_patch under `discovered_work` — do not implement it silently.
5. **All prior tests must stay green**: After each issue, the full existing test suite must pass.

## Code Patch Structure

1. **Issues Implemented** — List of issues completed
2. **Changes Made** — File-by-file summary of changes
3. **Test Results** — Before/after test counts
4. **Clarification Flags Applied** — How each flag was resolved
5. **Discovered Work** — Any new issues found during implementation
6. **Machine-Readable Handoff** — YAML block

## References

- [Agent Brief](../../artifacts/agent_brief.md)
- [Artifact Contracts](../workflow-orchestrator/references/artifact-contracts.yaml)
