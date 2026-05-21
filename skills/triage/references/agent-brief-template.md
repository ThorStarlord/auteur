# Agent Brief Template

## 1. Issue List Consumed

Reference the issue list being triaged. Note key scope information:
- Total issues in list
- Core vs expansion breakdown
- Any escalation status

## 2. Escalation Check

State clearly: **No escalation** | **ESCALATION — do not generate brief**

If escalation: surface the escalation reason and options from the issue list. Stop here.

## 3. Dependency Graph

Visual or textual representation of the dependency order:

```
AUTEUR-001 ──► AUTEUR-002 ──► AUTEUR-003
AUTEUR-004  (independent)
```

Note any cycles detected (CYCLE_ERROR).

## 4. Execution Order

Ordered list of issues ready to be worked in sequence:

| Seq | ID | Title | Priority | Effort | Depends On |
|-----|----|-------|----------|--------|------------|
| 1 | ISSUE-001 | ... | P0 | 1 day | — |
| 2 | ISSUE-002 | ... | P0 | 3 days | ISSUE-001 |

## 5. TDD Entry Points

For each issue, the exact failing test to write first (RED phase):

### [ISSUE-ID]: [Title]
**File**: `tests/test_<module>.py`
**Function**: `test_<specific_behaviour>`
**Assert**: `<exact assertion that fails today, passes after implementation>`
**Why this test first**: One sentence explaining why this is the minimal RED assertion.

## 6. Clarification Flags

Issues that need a decision before development can begin:

### [ISSUE-ID]: [Title]
**Flag**: `needs_clarification` | `ready`
**Question**: The specific question that must be answered.
**Blocked by**: Which acceptance criterion is untestable without this answer.
**Default if no response**: Proposed default so development can proceed.

If no flags: state **All issues are clear. No clarification needed.**

## 7. Machine-Readable Handoff

```yaml
artifact_id: agent_brief
schema_version: 1
source_intent_ref: # Path to 00-user-intent.md
issue_list_ref: # Path to issue_list.md
execution_order: # Ordered list of issue IDs
issues_ready: # Count of issues ready to start
issues_flagged: # Count of issues needing clarification
escalation_required: false
created_at: # ISO 8601 timestamp

issues:
  - id: # Issue ID
    title: # Issue title
    sequence: # Execution order (1-indexed)
    priority: # P0 | P1 | P2
    effort_days: # Numeric
    dependencies: # List of issue IDs this depends on
    status: ready | needs_clarification
    tdd_entry_point:
      file: # tests/...
      function: # test_...
      assert: # exact assertion string
```

## Next Steps

- **tdd**: Begin with issue `[ID]` at sequence 1
  - Write the failing test (RED): `[exact test function]`
  - Run `pytest [test file] -k [test function]` — confirm it fails
  - Implement minimal code to make it pass (GREEN)
  - Refactor if needed (REFACTOR)
  - Move to the next issue in sequence
