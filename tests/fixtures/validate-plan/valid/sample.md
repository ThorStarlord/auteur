# Workflow Orchestration Plan

## 11. Machine-readable plan
```yaml
artifact_id: workflow_orchestration_plan
chosen_workflow_id: implementation-workflow
execution_mode: guided_execution
initial_inputs:
  - id: context_artifacts
    type: artifact
status: active
stop_conditions:
  - session_close
approval_gates:
  - session_close
steps:
  - sequence: 1
    skill_id: docs-aligner
    step_type: local_execution
    gate: none
    input_artifact: context_artifacts
    output_artifact: domain_alignment_report
    status: pending
  - sequence: 2
    skill_id: to-prd
    step_type: local_execution
    gate: none
    input_artifact: domain_alignment_report
    output_artifact: prd
    status: pending
  - sequence: 3
    skill_id: to-issues
    step_type: local_execution
    gate: none
    input_artifact: prd
    output_artifact: issue_list
    status: pending
  - sequence: 4
    skill_id: triage
    step_type: local_execution
    gate: none
    input_artifact: issue_list
    output_artifact: agent_brief
    status: pending
  - sequence: 5
    skill_id: tdd
    step_type: local_execution
    gate: none
    input_artifact: agent_brief
    output_artifact: code_patch
    status: pending
  - sequence: 6
    skill_id: handoff
    step_type: local_execution
    gate: session_close
    input_artifact: code_patch
    output_artifact: prompt_handoff
    status: pending
```
