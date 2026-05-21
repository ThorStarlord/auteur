# Git Safety Policy

This policy governs how the `workflow-orchestrator` interacts with the repository's version control system, specifically during `autonomous_execution` and `yolo_execution`.

## 1. Branch Policy
- **No Direct Main Commits**: Committing directly to `main`, `master`, or any protected branch is strictly prohibited.
- **YOLO Branch Pattern**: For `yolo_execution`, a dedicated feature branch must be used or created. 
  - Pattern: `yolo/{workflow-id}/{timestamp}`
- **Clean Worktree**: Automation should ideally start from a clean working tree to ensure rollbacks are clean.

## 2. Commit Standards
- **Atomic Commits**: Every successful workflow step should be its own commit if possible.
- **Descriptive Messages**: Commit messages must include the `run_id` and the skill that performed the action.
- **No Force Push**: The orchestrator must never use force push.

## 3. Opt-in Enforcement
- If the user requests an execution mode that involves commits but provides no branch or an invalid branch, the orchestrator must refuse to proceed.
