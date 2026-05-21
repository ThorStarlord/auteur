# Workflow Orchestration Plan

## 1. Brief consumed
Short summary of the `repo-sensemaker` diagnosis, including fog type classification.

## 1.5. Problem classification (fog type)
The primary type of uncertainty identified:
- **product_fog**: Vague user needs, feature requirements unclear
- **ui_fog**: Navigation or screen design issues
- **docs_fog**: Missing documentation, knowledge gaps
- **architecture_fog**: Code structure, design boundary issues (default)

This determines which implementation workflow will be automatically invoked.

## 2. Chosen workflow
Name of the workflow.

## 3. Why this workflow
Why it fits the weakest boundary.

## 4. Skills in sequence
Ordered chain of skills to be used.

## 5. Inputs and outputs
What each skill receives and produces.

## 6. Approval gates
Where the user must approve before continuing.

## 7. Stop conditions
When to stop instead of continuing.

## 8. Execution mode
`plan_only` / `prompt_chain` / `guided_execution` / `autonomous_execution`.

## 9. Prompt chain
Ready-to-copy prompts (if applicable).

## 10. Run log template
How to record what happened during the execution.

## 11. Machine-readable plan

### Stage 1: Intent Context Fields
```yaml
artifact_id: workflow_orchestration_plan
schema_version: 1
source_intent_ref: # Path to 00-user-intent.md artifact
chosen_workflow_id: # Which workflow was actually chosen for execution
execution_mode: # plan_only, prompt_chain, guided_execution, autonomous_execution
status: # ready, in_progress, complete, failed
```

### Stage 2: Routing Audit Fields (Required)
```yaml
system_recommended_workflow: # What repo-sensemaker recommended based on fog type
selected_workflow: # What was actually selected (may differ from system recommendation)
routing_divergence: # true if selected != recommended, false if they match
routing_decision_method: # How decision was made (diagnosis_primary_soft_context, user_explicit_override, diagnosis_mixed_tiebreak_to_user_intent, escalation_recommended_accepted, escalation_recommended_rejected)
escalation_recommended: # Boolean: did the brief recommend escalation?
auto_escalation_allowed: # Boolean: is escalation automatic or user-gated? (default: false)
scope_expansion_requires_approval: # Boolean: does expanding scope beyond initial intent need approval?
```

### Standard Fields
```yaml
initial_inputs: # List of initial artifacts required for this workflow
  - id: # user_intent, repository_state, etc.
    type: # artifact type
    required: # true/false
    description: # human-readable description
steps:
  - id: # step number
    skill: # skill name
    step_type: # skill_execution, decision_point, validation_gate, etc.
    gate: # approval_gate_name, none, or session_close
    output_artifact: # artifact produced by this step
approval_gates:
  behavior: # pause_for_user_decision, auto_proceed, halt_on_failure
gate_behavior:
  default: # default behavior for unspecified gates
stop_conditions: # validator_failure, gate_denial, step_failure, user_interrupt, etc.
subset_run: # boolean: is this a subset of a full workflow?
subset_reason: # if subset_run: true, why was it limited?
included_steps: # list of included step IDs
excluded_steps: # list of excluded step IDs with reasons
created_at: # ISO 8601 timestamp
```

### Complete Example
```yaml
artifact_id: workflow_orchestration_plan
schema_version: 1
source_intent_ref: ../../00-user-intent.md
chosen_workflow_id: product-implementation-workflow
execution_mode: guided_execution
status: ready
system_recommended_workflow: product-implementation-workflow
selected_workflow: product-implementation-workflow
routing_divergence: false
routing_decision_method: diagnosis_primary_soft_context
escalation_recommended: false
auto_escalation_allowed: false
scope_expansion_requires_approval: true
initial_inputs:
  - id: user_intent
    type: artifact
    required: true
    description: "User's problem statement and scope"
steps:
  - id: 1
    skill: discovery
    step_type: skill_execution
    gate: review_discovery_findings
    output_artifact: discovery_findings
  - id: 2
    skill: opportunity-tree
    step_type: skill_execution
    gate: review_opportunity_map
    output_artifact: opportunity_map
  - id: 3
    skill: to-prd
    step_type: skill_execution
    gate: review_prd
    output_artifact: prd
approval_gates:
  behavior: pause_for_user_decision
gate_behavior:
  default: pause_for_user_decision
stop_conditions:
  - validator_failure
  - gate_denial
  - step_failure
subset_run: false
subset_reason: null
included_steps: []
excluded_steps: []
created_at: "2026-05-19T17:00:00Z"
```
