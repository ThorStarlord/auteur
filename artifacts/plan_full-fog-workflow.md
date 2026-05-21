# Orchestration Plan: Full Fog Path - Comprehensive Sensemaking & Orchestration

- **Session ID**: orchestration-20260519-185844-8d4496f8
- **Date**: 2026-05-19
- **Workflow**: full-fog-workflow
- **Execution Mode**: guided_execution
- **Purpose**: Comprehensively analyze ambiguous projects from raw fog through diagnosis to automatic implementation workflow invocation.

## 1. Brief Consumed

This plan was generated from sensemaking artifacts for workflow `full-fog-workflow`.

- **Workflow Purpose**: Comprehensively analyze ambiguous projects from raw fog through diagnosis to automatic implementation workflow invocation.
- **Routing**: No divergence — user-selected workflow matches system recommendation.

## 2. Chosen Workflow

**Workflow ID**: `full-fog-workflow`

Selected workflow: `full-fog-workflow` — Full Fog Path - Comprehensive Sensemaking & Orchestration.

## 3. Why This Workflow

The `full-fog-workflow` workflow was selected based on the user intent and sensemaking diagnosis.

- Diagnosis confirmed this workflow matches the required execution pattern.
- No routing divergence detected.

## 4. Skills in Sequence

### Step 1: problem-framer
- **Type**: local_execution
- **Gate**: review_problem_frame
- **Output**: problem_frame

### Step 2: unknowns-mapper
- **Type**: local_execution
- **Gate**: review_unknowns_map
- **Output**: unknowns_map

### Step 3: repo-sensemaker
- **Type**: local_execution
- **Gate**: review_diagnosis
- **Output**: repository_sensemaking_brief

### Step 4: workflow-orchestrator
- **Type**: local_execution
- **Gate**: review_orchestration_plan
- **Output**: workflow_orchestration_plan

## 5. Inputs and Outputs

- **user_intent** (artifact): User's problem statement and scope mode (created by orchestration-runner)
- **raw_fog** (external_context): Vague problem statement, project goals, team context, and current state of confusion.
- **repository_state** (external_context): Current repository files, folder structure, README, documentation, and git state.

## 6. Approval Gates

- **Mode**: guided_execution
- **Gate Behavior**: mandatory

- review_problem_frame: REQUIRED (user must approve)
- review_unknowns_map: REQUIRED (user must approve)
- review_diagnosis: REQUIRED (user must approve)
- review_orchestration_plan: REQUIRED (user must approve)

## 7. Stop Conditions

- Validator failure at any level -> HALT
- Gate denial -> HALT (rollback recommended for mutating modes)
- Step execution failure -> HALT
- Final step completed -> SUCCESS

## 8. Execution Mode

**Mode**: `guided_execution`

Gate behavior: `mandatory`. Mutations permitted: `True`.

## 9. Prompt Chain

The following prompts can be used for agent-driven execution of each step:

### Step 1 — problem-framer
> Execute Step 1 of `full-fog-workflow` using the `problem-framer` skill.
> Produce artifact: `problem_frame`. Gate: `review_problem_frame`.

### Step 2 — unknowns-mapper
> Execute Step 2 of `full-fog-workflow` using the `unknowns-mapper` skill.
> Produce artifact: `unknowns_map`. Gate: `review_unknowns_map`.

### Step 3 — repo-sensemaker
> Execute Step 3 of `full-fog-workflow` using the `repo-sensemaker` skill.
> Produce artifact: `repository_sensemaking_brief`. Gate: `review_diagnosis`.

### Step 4 — workflow-orchestrator
> Execute Step 4 of `full-fog-workflow` using the `workflow-orchestrator` skill.
> Produce artifact: `workflow_orchestration_plan`. Gate: `review_orchestration_plan`.

## 10. Run Log Template

```markdown
# Workflow Run Log: Full Fog Path - Comprehensive Sensemaking & Orchestration

- Date: {date}
- Session ID: {session_id}
- Workflow ID: full-fog-workflow
- Mode: guided_execution
- Status: {status}
```

## 11. Machine-readable plan

```yaml
artifact_id: workflow_orchestration_plan
source_intent_ref: artifacts/00-user-intent.md
chosen_workflow_id: full-fog-workflow
system_recommended_workflow: full-fog-workflow
selected_workflow: full-fog-workflow
routing_divergence: false
routing_decision_method: diagnosis_primary_soft_context
escalation_recommended: false
auto_escalation_allowed: false
scope_expansion_requires_approval: true
execution_mode: guided_execution
status: created
session_id: orchestration-20260519-185844-8d4496f8
subset_run: false
subset_reason: null
included_steps: []
excluded_steps: []
initial_inputs:
  - id: user_intent
    type: artifact
    required: true
    description: User's problem statement and scope mode (created by orchestration-runner)
  - id: raw_fog
    type: external_context
    required: true
    description: Vague problem statement, project goals, team context, and current state of confusion.
  - id: repository_state
    type: external_context
    required: true
    description: Current repository files, folder structure, README, documentation, and git state.
steps:
  - id: 1
    skill: problem-framer
    step_type: local_execution
    gate: review_problem_frame
    input_source: raw_fog
    output_artifact: problem_frame
    status: pending
  - id: 2
    skill: unknowns-mapper
    step_type: local_execution
    gate: review_unknowns_map
    input_artifact: problem_frame
    output_artifact: unknowns_map
    status: pending
  - id: 3
    skill: repo-sensemaker
    step_type: local_execution
    gate: review_diagnosis
    input_source: repository_state
    output_artifact: repository_sensemaking_brief
    status: pending
  - id: 4
    skill: workflow-orchestrator
    step_type: local_execution
    gate: review_orchestration_plan
    input_artifact: repository_sensemaking_brief
    output_artifact: workflow_orchestration_plan
    status: pending
approval_gates:
  - review_problem_frame
  - review_unknowns_map
  - review_diagnosis
  - review_orchestration_plan
gate_behavior:
  review_problem_frame: approved_by_user
  review_unknowns_map: approved_by_user
  review_diagnosis: approved_by_user
  review_orchestration_plan: approved_by_user
stop_conditions:
  - validator_failure
  - gate_denial
  - step_failure
```
