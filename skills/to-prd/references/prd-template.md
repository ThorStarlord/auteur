# Product Requirements Document Template

## 1. Executive Summary

Brief description of what this PRD delivers and the key user problem it solves.

## 2. User Goal (As Stated)

Include the exact goal from the user's problem statement. This anchors the PRD to what the user originally asked for.

## 3. Goal Preservation & Expansion

Explain how this PRD addresses the stated goal and whether scope expansion is proposed or approved.

**user_goal_preserved_as**: exact_match | core_with_expansion | diverged

- **exact_match**: PRD addresses ONLY what user asked for
- **core_with_expansion**: PRD addresses goal PLUS features discovered beyond stated goal (expansion proposed or approved)
- **diverged**: PRD significantly diverges from stated goal (escalation needed)

**scope_expansion_proposed**: true | false (are new features proposed beyond stated goal?)

**scope_expansion_requires_approval**: true | false (does user need to approve expansion?)

**scope_expansion_status**: exact_match | pending_user_approval | approved_by_user | diverged

## 4. Features

### Core Features (Goal-Preserving)

List features that directly address the user's stated goal. Each feature includes:
- Feature name
- What it does
- Key requirements
- Acceptance criteria

### Expansion Features (If Any)

If `user_goal_preserved_as: core_with_expansion`:

For PROPOSED expansions:
- Feature name
- Why it's proposed (rationale from discovery)
- Effort estimate
- Risk assessment
- **Status**: REQUIRES USER APPROVAL

For APPROVED expansions:
- Feature name
- Approval timestamp
- Feature details
- Acceptance criteria
- **Status**: APPROVED by user on [date]

## 5. Out of Scope

Explicitly list features that are NOT included in this PRD, even if they were discussed. This manages expectations.

Examples:
- Task categories (separate initiative)
- Mobile app (web only)
- Data persistence (MVP: in-memory)
- Notifications (v2)

## 6. Acceptance Criteria

Testable requirements for "done". Organize by:
1. Core features (must-haves)
2. Approved expansions (if any)

Format:
- [ ] Acceptance criterion (testable, specific)
- [ ] ...

## 7. Non-Functional Requirements

Performance, accessibility, browser support, data, scalability, etc.

Examples:
- Performance: List loads in <500ms
- Accessibility: WCAG 2.1 Level AA
- Browser Support: Chrome 90+, Firefox 88+, Safari 14+
- Data: In-memory only (MVP)

## 8. Approval Gate (If Expansion Proposed)

If `scope_expansion_proposed: true` and `scope_expansion_requires_approval: true`:

Include an approval gate asking user to approve or decline expansion features:

**Example**:
```
[APPROVAL REQUIRED]

Do you approve the following expansion features?

1. Due Dates: YES / NO
2. Recurring Tasks: YES / NO
3. Other [user input]

[Proceed based on user response]
```

## 9. Machine-Readable Handoff

```yaml
artifact_id: prd
schema_version: 1
source_intent_ref: # Path to 00-user-intent.md
user_goal_preserved_as: # exact_match | core_with_expansion | diverged
scope_expansion_proposed: # true | false
scope_expansion_requires_approval: # true | false
scope_expansion_status: # exact_match | pending_user_approval | approved_by_user | diverged
created_at: # ISO 8601 timestamp

# Optional: If scope expansion details needed
scope_expansion_details: # List of expansion features with rationale, effort, risk
  - feature: # Feature name
    rationale: # Why proposed (from discovery)
    effort_days: # Estimated effort
    risk: # Risk assessment
    status: # pending_user_approval | approved_by_user

# If approved expansions, include approval info
scope_expansion_approvals: # List of approved features with timestamps
  - feature: # Feature name
    status: # approved_by_user
    approved_by: # user | system
    approved_at: # ISO 8601 timestamp
```

## Next Steps

Once PRD is approved (or if no expansion approval needed), proceed to:
- **to-issues**: Convert features into stories with acceptance criteria
- **triage**: Prioritize stories
- **tdd**: Begin development with story-driven test writing
