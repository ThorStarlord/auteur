---
name: triage
description: prioritize an issue list into a sequenced, developer-ready agent brief with execution order, TDD entry points, and dependency graph. use as the final step before handing off to tdd.
---

# triage

Converts an `issue_list` artifact into an `agent_brief` — a sequenced, developer-ready execution plan that a TDD agent (or human developer) can follow without ambiguity. Determines the optimal execution order given dependencies, assigns TDD entry points per issue, and flags any issues that need clarification before development can begin.

## Workflow

1. **Consume Issue List**: Read `issue_list.md` and its machine-readable YAML block.
2. **Check Escalation**: If `escalation_required: true`, STOP. Surface the escalation and do not produce a brief.
3. **Dependency Graph**: Build the dependency graph from each issue's `dependencies` field. Detect any cycles (error if found).
4. **Topological Sort**: Order issues from least dependent (P0 unblocks) to most dependent. Issues with no dependencies and the same priority are ordered by effort (smallest first — fast wins unblock momentum).
5. **TDD Entry Point**: For each issue, determine the first failing test to write (the RED phase start point). This is the most minimal, concrete assertion that would fail today and pass after the issue is implemented.
6. **Clarification Flags**: If any issue has an acceptance criterion that is untestable, ambiguous, or missing a key detail, flag it as `needs_clarification` with a specific question. Do not block the entire brief — just flag the specific issue.
7. **Produce Agent Brief**: Write the `agent_brief` artifact following the template in `references/agent-brief-template.md`.

## Output Format

Every response must follow the [Agent Brief](references/agent-brief-template.md) structure.

**CRITICAL**: Every agent brief MUST include the **Machine-Readable Handoff** YAML block with at minimum `source_intent_ref`. Briefs without this block are invalid and violate the artifact contract.

## Boundary Rules

1. **No implementation**: Triage sequences and clarifies. It does not write code, tests, or implementation plans.
2. **No scope expansion**: Do not add issues not in the source `issue_list`. If you see a gap, flag it in `clarification_flags` — do not silently add work.
3. **No PRD re-derivation**: Accept the issue list as the authoritative work scope. Do not re-interpret the PRD.
4. **Concrete TDD entry points only**: Every TDD entry point must be a specific, runnable failing test (module path, function name, assertion). Never write "write a test for..." — write the actual test signature.
5. **Escalation is final**: If `escalation_required: true`, output nothing except the escalation message.

## TDD Entry Point Rules

For each issue, produce a `tdd_entry_point` with:
- **File**: The test file path (relative to repo root)
- **Function**: The exact test function name
- **Assertion**: The single most important assertion that would fail today

Format:
```
File: tests/test_outline_audit.py
Function: test_audit_outline_carriers_location_mismatch
Assert: len(diagnostics) == 1 and diagnostics[0].rule == "representation.carrier_location_mismatch"
```

## Dependency Graph Rules

- If issue A is in B's `dependencies`, A must appear before B in the execution order.
- If two issues have no dependency relationship and equal priority, order by effort (ascending).
- If a dependency cycle is detected, emit a `CYCLE_ERROR` and halt.

## References

- [Agent Brief Template](references/agent-brief-template.md)
- [Artifact Contracts](../workflow-orchestrator/references/artifact-contracts.yaml)
