---
name: to-prd
description: convert opportunity maps and discovery findings into a product requirements document (PRD) with scope expansion tracking.
---

# to-prd

## Workflow

1. **Consume Input**: Review opportunity map and domain alignment report.
2. **Extract User Goal**: Reference the source intent to understand what user originally asked for.
3. **Identify Scope**: Determine if the PRD addresses the user's goal alone or includes expansion.
4. **Document Goal Preservation**: Record how the user's goal is preserved (exact match, core with expansion, etc.)
5. **Propose Expansions**: If discovery revealed opportunities beyond stated goal, propose them for user approval.
6. **Produce PRD**: Generate the Product Requirements Document with features, acceptance criteria, and expansion details.

## Output Format

Every response must follow the [Product Requirements Document](references/prd-template.md) structure.

**CRITICAL**: Every PRD MUST include the **Machine-Readable Handoff** YAML block. PRDs without this block are invalid and violate the artifact contract.

## Stage 3: Scope Expansion Tracking

**Scope Expansion Fields** track whether features beyond the user's stated goal are being included in the PRD.

### How to Determine Scope Expansion

**Step 1: Extract User Goal**
- Read `source_intent_ref` → `00-user-intent.md`
- Note the user's original problem statement
- Identify what the user explicitly asked for (stated goal)

**Step 2: Compare Against Discovery**
- Review opportunity map: What did discovery reveal?
- Are there features beyond the user's stated goal?
- Did interviews reveal "nice-to-have" features not mentioned by user?

**Step 3: Document Goal Preservation**
- If PRD addresses ONLY the stated goal: `user_goal_preserved_as: exact_match`
- If PRD addresses goal PLUS identified opportunities: `user_goal_preserved_as: core_with_expansion`
- If PRD significantly diverges from goal: `user_goal_preserved_as: diverged` (escalate to user)

**Step 4: Propose or Document Expansions**
If `user_goal_preserved_as: core_with_expansion`:
- List each proposed feature beyond the stated goal
- Explain the discovery rationale (e.g., "5/8 users mentioned...")
- Estimate effort/risk for each expansion
- Set `scope_expansion_proposed: true`
- Set `scope_expansion_requires_approval: true` (user must approve)
- Set `scope_expansion_status: pending_user_approval`

If expansions were already approved by user:
- List approved expansions with approval timestamp
- Set `scope_expansion_status: approved_by_user`
- Include all approved features in the PRD

**Step 5: Emit Machine-Readable Fields**
```yaml
source_intent_ref: ../../00-user-intent.md
user_goal_preserved_as: exact_match | core_with_expansion | diverged
scope_expansion_proposed: true | false
scope_expansion_requires_approval: true | false
scope_expansion_status: exact_match | pending_user_approval | approved_by_user | diverged
```

### Three Scenarios

**Scenario A: Exact Match (No Expansion)**
```
User goal: "Task list management"
Discovery finds: Need for priorities
PRD includes: Task creation, priority management, completion tracking
---
user_goal_preserved_as: exact_match
scope_expansion_proposed: false
scope_expansion_requires_approval: false
scope_expansion_status: exact_match
```

**Scenario B: Core + Expansion Proposed (Requires Approval)**
```
User goal: "Task list management"
Discovery finds: Need for priorities + due dates + recurring tasks (user didn't mention these)
PRD includes: Core (task creation, priority, completion) + proposes due dates and recurring (not yet approved)
---
user_goal_preserved_as: core_with_expansion
scope_expansion_proposed: true
scope_expansion_requires_approval: true
scope_expansion_status: pending_user_approval
```

**Scenario C: Expansion Approved (Included in Development)**
```
User goal: "Task list management"
User approved: Due dates + recurring tasks in workflow-orchestrator gate
PRD includes: All features (core + due dates + recurring)
---
user_goal_preserved_as: core_with_expansion
scope_expansion_proposed: true
scope_expansion_requires_approval: false  (already approved, no longer needs approval)
scope_expansion_status: approved_by_user
```

### When to Escalate (Divergence)

If discovery suggests features that contradict or significantly diverge from the user's stated goal:
- Example: User asked for "simple task list" but discovery reveals "complex workflow engine" needed
- Action: Set `user_goal_preserved_as: diverged` and escalate to workflow-orchestrator or user
- Do not force expansion; let user decide if new direction is acceptable

## PRD Structure

Every PRD must include these sections:

1. **Executive Summary** — What this PRD delivers
2. **User Goal** — The goal as user stated it (exact quote from intent)
3. **Goal Preservation & Expansion** — How this PRD addresses the goal and what (if anything) is proposed beyond it
4. **Features** — Organized by core features first, then approved expansions
5. **Out of Scope** — Explicitly listed to manage expectations
6. **Acceptance Criteria** — Testable requirements (organized by core + expansions if applicable)
7. **Non-Functional Requirements** — Performance, accessibility, browser support, etc.
8. **Approval Gate** (if expansion proposed) — Request user approval for expansion features
9. **Machine-Readable Handoff** — YAML block with all required fields

## Validation Rules

- PRD must have a valid `source_intent_ref` pointing to 00-user-intent.md
- `user_goal_preserved_as` must be one of: exact_match, core_with_expansion, diverged
- If `scope_expansion_proposed: true`, then `scope_expansion_requires_approval` must be true (expansion always needs approval before dev starts)
- If `scope_expansion_status: pending_user_approval`, PRD should include approval gate asking user to decide
- If `scope_expansion_status: approved_by_user`, approval timestamps should be documented
- Machine-readable section must be present and parseable YAML

## References

- [Product Requirements Document Template](references/prd-template.md)
- [Artifact Contracts](../workflow-orchestrator/references/artifact-contracts.yaml)
- [Intent Contract](../workflow-orchestrator/references/artifact-contracts.yaml#user_intent)
