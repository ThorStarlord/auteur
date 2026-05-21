# Recovery Policy

This policy defines how the orchestrator handles failures and how it ensures the repository can be restored to a safe state.

## 1. Before Mutation
- **Snapshot**: Record the current `HEAD` SHA and branch name in the [Run Log](run-log-template.md).
- **Checklist**: Verify that core architectural files are present and valid before starting.

## 2. On Failure
- **Immediate Stop**: If any step fails (test failure, validator failure, or skill error), stop the workflow immediately. Do not attempt the next step.
- **Reporting**: Report the exact failure and the list of files modified during the current run.
- **Rollback Suggestion**: Provide the specific git command to revert changes to the pre-run `HEAD`.

## 3. Preservation List
The orchestrator must NEVER delete or silently overwrite the following core files without explicit user approval in `guided_execution` mode:
- `README.md`
- `CONTEXT.md`
- `CONTRIBUTING.md`
- `scripts/validate-repo.py`
- `skills/*/SKILL.md`
- `references/artifact-contracts.yaml`
- `skills/workflow-orchestrator/references/skill-registry.yaml`

## 4. Rollback Command
Example rollback instruction to be provided to the user:
`git reset --hard {PRE_RUN_SHA}`
