# Agent & Subagent Guidelines

Guidelines for using AI agents (subagents) in auteur development.

## Subagent-Driven Development

### When to Use

Subagent-driven development is ideal for:
- Multi-task implementations with clear specs (3+ independent tasks)
- Architecture pattern validation (implement 2-3 examples to prove the pattern)
- Test-driven development cycles (write tests → implement → review → repeat)
- Parallel task execution with intermediate review gates

### The Workflow

1. **Write design spec** (architecture, constraints, rationale)
2. **Write implementation plan** (exact code, test structure, test cases)
3. **Dispatch Task 1 implementer** (fresh subagent, complete isolation)
4. **Generate review package** (diff from base commit)
5. **Dispatch Task 1 reviewer** (verify spec compliance + code quality)
6. **Mark Task 1 complete** (update progress ledger)
7. **Repeat Steps 3-6** for Task 2, Task 3, etc.
8. **Final whole-branch code review** (architecture coherence, no regressions)
9. **Finish branch** (merge or release)

### Continuous Execution Mode

For independent tasks, proceed without human-in-loop pauses:

```
Dispatch T1 implementer
└─ (running in parallel)
   ... meanwhile ...
Dispatch T1 reviewer (when T1 implementer finishes)
└─ (running in parallel)
   ... meanwhile ...
Dispatch T2 implementer (immediately after T1 marked complete)
```

Benefits:
- No context waste on summaries
- Momentum maintained
- Flow state preserved
- 3 tasks complete in time that would normally take 2

**Key:** Only use this when tasks are genuinely independent (different files, no shared state).

### Preparing Subagents for Success

**Design Spec** (include these sections):
- Executive summary (goal + architecture in 1-2 sentences)
- Emotional cores or design patterns (what makes this genre/feature unique)
- Layer-by-layer specifications (exact names, options, constraints)
- Validation rules (what must be checked, why, what's the failure mode)
- Global constraints (exact values, file paths, API signatures)
- Success criteria (test counts, regression expectations)

**Implementation Plan** (include these sections):
- Global constraints (copied verbatim from spec)
- Per-task breakdown (files, interfaces, exact code)
- Step-by-step TDD workflow (write test → run → implement → run → review)
- Test structure (test classes, test case organization)
- Report contract (where to write results, what to return)

Subagents with complete specs can execute in isolation without questions. Subagents without clear specs will ask round-trip questions, destroying parallelism.

### Review Gates Between Tasks

Review after each task, not at the end:

- **Task 1 Review:** Catches fundamental issues before Task 2 starts
- **Task 2 Review:** Ensures pattern consistency early
- **Task 3 Review:** Final polish before whole-branch review

Early issues are cheaper to fix:
- Fix in Task 1: 1 task rework
- Fix in Task 2: 1-2 tasks rework
- Fix in Task 3: 1-3 tasks rework (discovers pattern is wrong)

### Progress Tracking

Maintain a progress ledger (`.superpowers/sdd/{project}-progress.md`):

```markdown
## Task Completion Summary

- [x] Task 1: Component Name (X tests) — commit_hash ✅ (Spec ✅ Code ✅)
- [x] Task 2: Component Name (Y tests) — commit_hash ✅ (Spec ✅ Code ✅)
- [ ] Task 3: Component Name (Z tests) — In progress...

Total: X+Y tests passing, zero regressions
```

This ledger survives context compaction and guides resumption after interruptions.

## Subagent Instructions

### For Implementers

1. Read the design spec and implementation plan (they are your requirements)
2. Write failing tests first (test-driven development)
3. Run tests to verify failures
4. Implement minimal code to pass
5. Self-review for completeness
6. Commit with message reflecting what was built (not how)

### For Reviewers

1. Verify spec compliance (all requirements met, nothing extra)
2. Verify code quality (type hints, docstrings, error handling, naming)
3. Check for regressions (did existing tests still pass)
4. Report: Spec ✅ Code ✅ (pass), or list findings (fail)

If findings exist, implementer fixes and reviewer re-reviews (loop until approved).

## No Human-in-Loop Pauses

Once you've dispatched Task 1, don't wait for it to complete before prepping Task 2:

```python
# DON'T DO THIS:
agent1 = dispatch(Task1)
agent1.wait()  # BLOCKING
summarize(agent1)  # WASTES CONTEXT
agent2 = dispatch(Task2)

# DO THIS:
agent1 = dispatch(Task1)  # Fire and forget
# prep Task 2 spec, review package while agent1 runs
agent2 = dispatch(Task2)  # Start immediately when ready
# Both run in parallel
```

The first approach burns context on recaps. The second maintains flow.

## Validation Workflow

Three-step validation for genre pipelines:

1. **Task Reviews** (between tasks) — ensure each component is correct in isolation
2. **Whole-Branch Review** (after all tasks) — ensure components work together
3. **End-to-End Verification** (after merge) — run full pipeline with real data

All three must pass before production release.

---

**Last Updated:** 2026-07-08  
**Validated By:** Three complete genre pipelines implemented in parallel with subagent-driven development
