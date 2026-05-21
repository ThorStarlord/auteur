---
name: to-issues
description: convert product requirements documents (PRDs) into an issue list with acceptance criteria, effort estimates, and scope tracking.
---

# to-issues

## Workflow

1. **Consume PRD**: Review the product requirements document.
2. **Check Scope Status**: Verify PRD scope matches user goal (no divergence).
3. **Classify Issues**: Separate core features from approved expansions.
4. **Generate Stories**: Create issues for features with acceptance criteria and effort.
5. **Estimate Effort**: Assign realistic effort estimates based on requirements.
6. **Track Scope**: Record which issues are core vs expansion, approval status.
7. **Produce Issue List**: Generate the issue list artifact.

## Output Format

Every response must follow the [Issue List](references/issue-list-template.md) structure.

**CRITICAL**: Every issue list MUST include the **Machine-Readable Handoff** YAML block. Issue lists without this block are invalid and violate the artifact contract.

## Stage 4: Scope Expansion Status Tracking

**Scope Tracking in Issues** documents which stories are core (goal-preserving) vs expansion (approved additions) vs divergent (escalation).

### How to Generate Issues

**Step 1: Check PRD Scope Status**
- Read `user_goal_preserved_as` from PRD
- If diverged: STOP. Escalate to user. Do not generate issues.
- If exact_match: Generate issues for all features
- If core_with_expansion: Generate issues for core + approved expansions only

**Step 2: Classify Features**
- **Core features**: Address the user's stated goal (from intent)
- **Approved expansions**: Beyond stated goal but approved by user (from PRD)
- **Divergent scope**: Contradicts stated goal (trigger escalation)

**Step 3: Generate Issues**
For each feature in PRD:
- Create issue title based on feature name
- Include acceptance criteria from PRD (may expand with technical details)
- Estimate effort based on feature complexity
- Assign priority:
  - **P0**: Core features (unblocking)
  - **P1**: Core features (depends on P0) or approved expansions (moderate priority)
  - **P2**: Approved expansions (lower priority, can defer)
  
**Step 4: Note Scope Tracking**
- Mark each issue as core or expansion
- If expansion, note approval status (approved_by_user)
- If any divergence detected, escalate instead

**Step 5: Emit Machine-Readable Fields**
```yaml
source_intent_ref: ../../00-user-intent.md
user_goal_preserved_as: exact_match | core_with_expansion | diverged
scope_expansion_proposed: true | false
scope_expansion_status: exact_match | approved_by_user | diverged
```

### Three Scenarios

**Scenario A: Exact Match (Core Only)**
```
PRD: user_goal_preserved_as: exact_match, scope_expansion_proposed: false
Issues: Generate for core features only
Priorities: All P0/P1 (core features)
---
user_goal_preserved_as: exact_match
scope_expansion_proposed: false
scope_expansion_status: exact_match
```

**Scenario B: Core + Approved Expansion**
```
PRD: user_goal_preserved_as: core_with_expansion, scope_expansion_status: approved_by_user
Issues: Generate for core + approved expansion features
Priorities: P0 for core (unblocking), P1-P2 for expansions (lower priority)
Phasing: Core first (MVP), then expansions (phases 2+)
---
user_goal_preserved_as: core_with_expansion
scope_expansion_proposed: true
scope_expansion_status: approved_by_user
```

**Scenario C: Divergence (Escalation)**
```
PRD: user_goal_preserved_as: diverged
Action: DO NOT GENERATE ISSUES
Escalation: "PRD scope diverged from stated goal. Options: return to discovery, confirm new direction, narrow to goal"
---
user_goal_preserved_as: diverged
scope_expansion_proposed: N/A
scope_expansion_status: diverged
issues_generated: 0
escalation_required: true
```

### Effort Estimation

Assign effort estimates based on feature complexity:

- **0.5 days**: Simple field addition, trivial UI change
- **1 day**: Straightforward CRUD operation, basic UI component
- **2-3 days**: Moderate complexity, multiple dependencies
- **3-5 days**: Complex logic, error handling, edge cases
- **5+ days**: Very complex features or unknown unknowns

Estimates should account for:
- Code implementation
- Unit/integration testing
- Acceptance testing
- Bug fixes and refinement

### Issue Prioritization Rules

**Core Features** (goal-preserving):
- P0: Foundational features that unblock others (e.g., task creation, list view)
- P1: Features that depend on P0 but are still essential

**Approved Expansions**:
- P1: Moderate priority expansions (e.g., due dates)
- P2: Lower priority expansions (e.g., recurring tasks)
- Can be deferred without breaking MVP

**Divergent Scope**:
- Do not assign priority
- Escalate instead of generating issues

## Issue List Structure

Every issue list must include these sections:

1. **PRD Consumed** — Reference to PRD being converted
2. **Scope Status** — Whether this is core, expansion, or divergence
3. **Issues Generated** — List of all stories with:
   - ID (e.g., TASK-001)
   - Type (Feature, Bug, Tech Debt)
   - Title
   - Acceptance Criteria
   - Effort estimate
   - Priority
4. **Release Scope** — Total issues, effort, timeline
5. **Phasing Strategy** — If applicable, how to phase core + expansions
6. **Out of Scope** — What's explicitly excluded
7. **Machine-Readable Handoff** — YAML block with scope tracking

## Validation Rules

- Issue list must have a valid `source_intent_ref` pointing to 00-user-intent.md
- `user_goal_preserved_as` must match PRD value
- If `user_goal_preserved_as: diverged`: escalation_required: true, issues_generated: 0
- If `user_goal_preserved_as: exact_match`: all issues are core
- If `user_goal_preserved_as: core_with_expansion`: issues marked as core or expansion
- Machine-readable section must be present and parseable YAML

## Escalation Protocol

If PRD diverges from stated goal:

1. DO NOT GENERATE ISSUES
2. Set escalation_required: true in machine-readable section
3. Provide three options:
   - Return to discovery (revise PRD to preserve goal)
   - Confirm new direction (update intent, regenerate PRD)
   - Narrow to goal (remove divergent features)
4. Pause issue generation pending user decision

## References

- [Issue List Template](references/issue-list-template.md)
- [Artifact Contracts](../workflow-orchestrator/references/artifact-contracts.yaml)
- [User Intent](../workflow-orchestrator/references/artifact-contracts.yaml#user_intent)
