# Workflow Orchestration Plan: Sample

## 11. Machine-readable plan
```yaml
artifact_id: workflow_orchestration_plan
source_intent_ref: artifacts/00-user-intent.md
chosen_workflow_id: implementation-workflow
system_recommended_workflow: implementation-workflow
selected_workflow: implementation-workflow
routing_divergence: false
routing_decision_method: diagnosis_primary_soft_context
escalation_recommended: false
auto_escalation_allowed: false
scope_expansion_requires_approval: true
execution_mode: guided_execution
status: created
session_id: orchestration-sample
subset_run: false
subset_reason: null
included_steps: []
excluded_steps: []
initial_inputs:
  - id: context_artifacts
    type: artifact
    required: true
    description: Artifacts from sensemaking pipeline (problem-frame, unknowns-map, sensemaking-brief, orchestration-plan).
steps:
  - id: 1
    skill: docs-aligner
    step_type: local_execution
    gate: none
    input_artifact: context_artifacts
    output_artifact: domain_alignment_report
    status: created
  - id: 2
    skill: to-prd
    step_type: local_execution
    gate: none
    input_artifact: domain_alignment_report
    output_artifact: prd
    status: created
  - id: 3
    skill: to-issues
    step_type: local_execution
    gate: none
    input_artifact: prd
    output_artifact: issue_list
    status: created
  - id: 4
    skill: triage
    step_type: local_execution
    gate: none
    input_artifact: issue_list
    output_artifact: agent_brief
    status: created
  - id: 5
    skill: tdd
    step_type: local_execution
    gate: none
    input_artifact: agent_brief
    output_artifact: code_patch
    status: created
  - id: 6
    skill: handoff
    step_type: local_execution
    gate: session_close
    input_artifact: code_patch
    output_artifact: prompt_handoff
    status: created
approval_gates:
  - session_close
gate_behavior:
  session_close: approved_by_user
stop_conditions:
  - validator_failure
  - gate_denial
  - step_failure
```