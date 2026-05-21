# Issue List Template

## 1. PRD Consumed

Reference the PRD being converted. Note key scope information:
- PRD scope classification (user_goal_preserved_as)
- Whether scope expansion was proposed or approved
- Any divergence detected

## 2. Scope Status

Clearly state the scope classification:
- **Exact Match**: Core features only (no expansion)
- **Core + Expansion**: Core features + approved expansion features
- **Divergence (Escalation)**: PRD diverged from stated goal; no issues generated; escalation required

## 3. Issues Generated

### For Each Issue Include:

- **ID**: Unique identifier (e.g., TASK-001)
- **Type**: Feature, Bug, Tech Debt, etc.
- **Title**: Clear, action-oriented title
- **Acceptance Criteria**: Testable conditions for "done"
- **Effort**: Estimated days (0.5, 1, 2, 3, 5+)
- **Priority**: P0 (unblocking), P1 (essential), P2 (lower priority)
- **Dependencies**: If any other issues must complete first
- **Note**: If expansion, indicate approval status

### Example:

```
### Story 1: Task Creation
**ID**: TASK-001  
**Type**: Feature  
**Title**: Create tasks with title and optional description

**Acceptance Criteria**:
- User can input task title (required, max 100 chars)
- User can input optional description (max 500 chars)
- Task is created with auto-generated ID and timestamp
- Success message shows "Task created"

**Effort**: 2 days  
**Priority**: P0 (unblocks all other features)
```

## 4. Release Scope

Summary of all issues:
- Total issue count
- Count by type (Feature, Bug, etc.)
- Total effort estimate
- Projected timeline
- MVP vs Phase 2+ breakdown

## 5. Phasing Strategy (If Applicable)

If core + expansion:

- **Phase 1 (MVP)**: Core features only
  - Issues: [list]
  - Effort: [total days]
  - Timeline: [duration]

- **Phase 2 (Expansion)**: Approved expansion features
  - Issues: [list]
  - Effort: [total days]
  - Timeline: [duration]

- **Phase 3+ (Future)**: Deferred features (if any)

## 6. Out of Scope

Explicitly list features NOT generated as issues:
- Features from PRD marked as future work
- Features explicitly deferred (from PRD out-of-scope section)
- Anything divergent (if escalation case)

## 7. Testing Plan

High-level testing strategy:
- Unit tests: Which components tested
- Integration tests: Which flows tested
- Acceptance tests: Which stories have E2E tests
- Manual testing: Scope and approach

## 8. Escalation (If Divergence Case)

If `user_goal_preserved_as: diverged`:

```
⚠️ **ESCALATION**: PRD scope diverged from user's stated goal.

**User's Goal**: [stated goal from intent]

**PRD Scope**: [divergent scope from PRD]

**Issue**: Scope is fundamentally different.

**Options**:
1. Return to Discovery: Revise PRD to preserve goal
2. Confirm New Direction: User approves new scope as goal
3. Narrow to Goal: Remove divergent features; keep MVP focused

**Action**: [Choose one option before proceeding]
```

## 9. Machine-Readable Handoff

```yaml
artifact_id: issue_list
schema_version: 1
source_intent_ref: # Path to 00-user-intent.md
user_goal_preserved_as: # exact_match | core_with_expansion | diverged
scope_expansion_proposed: # true | false
scope_expansion_status: # exact_match | approved_by_user | diverged
issues_generated: # Total number of issues
core_issues_count: # Number of core issues (if applicable)
expansion_issues_count: # Number of expansion issues (if applicable)
escalation_required: # true (if divergence) | false
escalation_reason: # If escalation_required: true, explain why
escalation_options: # If divergence: list of resolution options
decision_required_from: # user (if divergence) | none
issues: # List of all issues with id, title, type, effort, priority, etc.
created_at: # ISO 8601 timestamp
```

## Next Steps

**If Core Only or Core + Expansion (No Divergence)**:
- **triage** — Prioritize issues per phasing strategy
- **tdd** — Begin with P0 issue (story-driven test writing)
- Development follows test-driven development workflow

**If Divergence (Escalation Case)**:
- **NO ISSUES GENERATED**
- Escalate to user for decision
- Based on user choice, regenerate PRD and re-run to-issues
