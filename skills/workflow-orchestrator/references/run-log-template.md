# Workflow Run Log: [Workflow Name]

- **Date**: [YYYY-MM-DD]
- **Session ID**: [ID]
- **Orchestrator Mode**: [Mode]

## Sequence Log

### Step [ID]
- **step_id**: [ID]
- **skill**: [Skill Name]
- **runtime**: [local | local_command | external]
- **invocation**: [exact command or local function]
- **input_artifact**: [Artifact ID or N/A]
- **input_source**: [Source ID or N/A]
- **output_artifact**: [Artifact ID]
- **artifact_path**: [Relative path, e.g., artifacts/name.md]
- **validator_stack**:
    - level: [Generic | Specialized]
      command: [Exact command]
      result: [PASSED | FAILED]
- **gate**: [Gate Name]
- **gate_behavior**: [required | skipped_by_design | bypassed_by_yolo | paused_for_approval]
- **status**: [COMPLETED | PAUSED | FAILED]
- **error** (if FAILED):
    - **type**: [error_category, e.g., test_failure, validation_error, missing_artifact]
    - **message**: [Error description]
    - **log_file**: [Path to detailed error log if available]
    - **remediation**: [Recovery command, e.g., git reset --hard {SHA}]
    - **recommendation**: [Suggested next action]

## Decisions & Overrides
- [List any manual interventions or logic changes made during the run]

## Final State
- [Summary of what was achieved]
