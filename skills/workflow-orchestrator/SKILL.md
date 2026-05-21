---
name: workflow-orchestrator
description: select and stage a workflow from a repository sensemaking brief. use when the user has a diagnostic brief and wants a workflow plan, prompt chain, guided execution plan, or guarded orchestration with approval gates.
---

# workflow-orchestrator

## Workflow
1. **Consume Brief**: Review the diagnostic brief from `repo-sensemaker`.
2. **Select Workflow**: Match the recommended path to an available workflow in the `workflow-registry.yaml`.
3. **Plan**: Produce a Workflow Orchestration Plan with ordered steps and approval gates.
4. **Mode Selection**: Determine the execution mode (Default: `plan_only`).
5. **Execute/Generate**:
   - `plan_only`: produce the plan artifact and stop. No workflow steps are executed, and no repository files are modified (except the plan itself if explicitly requested).
   - `prompt_chain`: produce copy/paste prompts and stop.
   - `guided_execution`: execute one eligible step, validate its output artifact, write/update the run log, then stop for approval.
   - `autonomous_execution`: execute eligible steps until the next approval gate, failed validation, non-executable skill, or stop condition. **After sensemaking completes**: if the orchestration-plan recommends external workflows, automatically invoke `implementation-workflow` with sensemaking artifacts and continue without stopping between steps.
    - `yolo_execution`: [STABLE] execute only eligible steps with no intermediate approval. **MANDATORY**: Run `Post-Step Verification` after each skill execution. Stop immediately on missing artifact, invalid handoff, failed verification (script or LLM), non-executable skill, dirty git state, or run-log failure. **After sensemaking completes**: if the orchestration-plan recommends external workflows, automatically invoke `implementation-workflow` with sensemaking artifacts and continue without stopping between steps.
6. **Implementation Workflow (autonomous modes only)**: If mode is `autonomous_execution` or `yolo_execution` and the orchestration-plan recommends external workflows, automatically execute the `implementation-workflow` (docs-aligner → to-prd → to-issues → triage → tdd → handoff) with `gate: none` between steps. Pass sensemaking artifacts as initial context. Do not pause between steps.

## Stage 2: Routing Audit

**Routing Audit Fields** track the gap between what the system recommended and what was actually selected. These fields enable visibility into routing decisions, conflicts, and overrides.

### Recording Routing Decisions

**Step 1: Capture System Recommendation**
- Read `recommended_workflow_id` from the repository sensemaking brief
- Record this as `system_recommended_workflow` in the plan
- This is what repo-sensemaker diagnosed based on fog type and conflict analysis

**Step 2: Determine User Selection**
- If in `guided_execution` mode and the user is presented a choice, record their explicit selection
- If user explicitly overrides the recommendation, record the selected workflow (which differs from system recommendation)
- If no override provided, selected workflow equals system recommendation

**Step 3: Calculate Routing Divergence**
- `routing_divergence: true` if `system_recommended_workflow != selected_workflow`
- `routing_divergence: false` if they match

**Step 4: Record Decision Method**
Valid routing_decision_method values:
- `diagnosis_primary_soft_context` — System recommendation based on primary fog type; user intent confirmed recommendation (no override)
- `diagnosis_mixed_tiebreak_to_user_intent` — Diagnosis showed mixed fog; user intent broke the tie to select workflow
- `user_explicit_override` — User explicitly selected different workflow than system recommended (routing divergence: true)
- `escalation_recommended_accepted` — System recommended escalation to full-fog-workflow; user accepted
- `escalation_recommended_rejected` — System recommended escalation; user stayed with narrower workflow (routing divergence: true)

**Example Scenarios:**

*Scenario A: Agreement (no override)*
```yaml
system_recommended_workflow: product-implementation-workflow
selected_workflow: product-implementation-workflow
routing_divergence: false
routing_decision_method: diagnosis_primary_soft_context
```

*Scenario B: User Override*
```yaml
system_recommended_workflow: full-fog-workflow
selected_workflow: product-implementation-workflow
routing_divergence: true
routing_decision_method: user_explicit_override
```

*Scenario C: Tie-breaker to User Intent*
```yaml
system_recommended_workflow: product-implementation-workflow
selected_workflow: product-implementation-workflow
routing_divergence: false
routing_decision_method: diagnosis_mixed_tiebreak_to_user_intent
```

### Escalation in Routing Audit

When `escalation_recommended: true` in the brief:
- System recommends full-fog-workflow or other escalation path
- Record `system_recommended_workflow: full-fog-workflow` (or appropriate escalation)
- If user accepts: selected matches system, routing_divergence: false, decision_method: `escalation_recommended_accepted`
- If user rejects: selected is narrower workflow, routing_divergence: true, decision_method: `escalation_recommended_rejected`

Always include `escalation_recommended` and `auto_escalation_allowed` from brief. Escalation recommendations are informational; users always control final selection unless auto_escalation is enabled.

## Output Format
Every response must follow the [Workflow Orchestration Plan](references/workflow-orchestration-template.md) structure. 

**CRITICAL**: Every plan MUST include the **Section 11: Machine-readable plan** YAML block. Plans without this block are invalid and violate the artifact contract.

Use [Run Log Template](references/run-log-template.md) only when recording an actual guided or autonomous run.

## Execution Modes
Use [Execution Modes](references/execution-modes.md) as the source of truth. The inline behavior summary in the workflow above is only a control-plane shortcut.

## Approval Gate Handling
- **`gate: none`**: Step executes without approval. Used for high-velocity workflows where intermediate gates would introduce unnecessary delays. The orchestrator skips approval wait for this step and immediately proceeds to the next step.
- **`gate: <gate_name>`**: Standard approval gate. The orchestrator halts and requests approval before proceeding.
- **`gate: session_close`**: Final gate. The orchestrator stops after completing this step and summarizes the session.

## Automatic Implementation Workflow Invocation

**When does it trigger:**
- Only in `autonomous_execution` or `yolo_execution` modes
- Only after sensemaking completes and the orchestration-plan is produced
- Only if the plan recommends external workflows (not local sensemaking only)

**What happens:**
1. Orchestrator produces the orchestration-plan
2. Parses the plan's problem classification to determine the implementation workflow type
3. Routes to the appropriate workflow:
   - **`product-implementation-workflow`**: For product/feature fog (includes discovery, opportunity-tree)
   - **`ui-implementation-workflow`**: For UI/frontend fog (includes ui-flow, ui-screen-spec)
   - **`implementation-workflow`**: For architecture/code design fog (default: docs-aligner → prd → issues → tdd)
   - **`docs-implementation-workflow`**: For documentation fog (default: docs-aligner → docs spec)
4. Invokes the selected workflow with sensemaking artifacts as `context_artifacts` input
5. All steps marked `gate: none` execute without pausing; only final `session_close` gate pauses for approval
6. Artifacts flow between steps automatically; no user intervention required between steps

**Workflow routing logic:**
- Parse orchestration-plan's fog classification (product_fog, architecture_fog, ui_fog, docs_fog, or other)
- If `fog_type == "product"`: use `product-implementation-workflow`
- If `fog_type == "ui"` or `fog_type == "frontend"`: use `ui-implementation-workflow`
- If `fog_type == "docs"` or `fog_type == "documentation"`: use `docs-implementation-workflow`
- If `fog_type == "uncertain"` or unclassified: use default `implementation-workflow` (graceful degradation)
- Can override with explicit `recommended_implementation_workflow` field in orchestration-plan

**For guided_execution mode:**
- Orchestrator produces the orchestration-plan and presents it to the user
- Shows which implementation workflow will be used based on fog type
- Asks: "Continue to [workflow-name] with these recommendations?"
- Only proceeds if user approves

## Error Handling in Implementation Workflows

**When a step fails:**
1. **Capture error**: Record step ID, skill name, error type, error message in run log
2. **Stop immediately**: Do not continue to next step (fail-fast approach)
3. **Record recovery**: Provide git reset command for rollback to pre-execution state
4. **Recommend next action**: Suggest reviewing error logs, fixing issues, switching to guided_execution mode
5. **Update run log**: Mark step as failed with remediation instructions

**Graceful degradation for uncertain fog_type:**
- If fog classification is uncertain or mixed, default to `implementation-workflow`
- Log a note in machine-readable plan: `fog_type_confidence: low`
- This prevents routing errors and ensures safe default behavior

**Execution mode selection:**
- If no mode specified: default to `plan_only` (safest)
- If step fails in `autonomous_execution`: suggest switching to `guided_execution` for inspection
- No automatic retry (manual intervention required)

## Boundary Rules
- **Safety First**: Default to `plan_only` mode. 
- **Contract Enforcement**: If a brief does not contain a valid machine-readable handoff, or the requested execution mode is not allowed by [Execution Modes](references/execution-modes.md), the orchestrator MUST refuse the request or downgrade to `plan_only` or `guided_execution`.
- **Validator Stack Compliance**: The orchestrator MUST follow the [Validator Stack Policy](references/validator-stack-policy.md) for every step. ALL registered validators (Generic and Specialized) MUST pass before a step is considered complete.
- **Machine Verifiability**: The orchestrator MUST generate Section 11 (Machine-readable plan) in every orchestration plan. Failure to do so renders the artifact non-verifiable.
- **Handoff Compliance**: Transitions between skills in a workflow MUST comply with the [Artifact Contracts](references/artifact-contracts.yaml).
- **Plan-only Hygiene**: In `plan_only` mode, the orchestrator MUST NOT populate `Section 9: Prompt Chain` with copy-pasteable prompts. Section 9 should explicitly state: `N/A - mode is plan_only. No prompt chain generated.`
- **Path Normalization**: Generated artifacts, plans, and run logs MUST use relative paths and NEVER use absolute `file:///` links. Pipeline runs MUST follow `artifacts/NN-project-name/NN-file-name.md` (e.g., `artifacts/03-my-run/01-problem-frame.md`). Run folders nest directly under `artifacts/` with no `runs/` subfolder. Historical artifacts at `artifacts/` root are left in place — do not migrate them.
- **Execution Authority**: The orchestrator may execute only registry-approved steps where `availability.executable_by_orchestrator: true` and `availability.type` is either `local` or `local_command`.
  - `local` means the skill is bundled in this repository.
  - `local_command` means the skill is installed in the local working environment and MUST define an `invocation` block with `runtime`, `command`, `input_artifact`, and `output_artifact`.
  - `external`, `external_required`, and `prompt_only` steps must be treated as routing targets, not executable steps.
- **YOLO Safety Heuristics (Pre-flight)**:
    - **Context Check**: Before starting a YOLO chain, estimate the total repository context + task description. If it exceeds 100k tokens (or 80% of the model's comfortable limit), the orchestrator MUST automatically downgrade to `guided_execution` or `autonomous_execution` with mandatory gates.
    - **Clean State**: Verify `git status` is clean. Record the current `HEAD` SHA in the Run Log as `PRE_YOLO_COMMIT`.
    - **Explicit Pre-flight Log**: Every YOLO run log MUST include a `Preflight` block documenting the Level 1 structural validation (`python scripts/validate-repo.py`), current branch safety, and dry-run status.
- **YOLO Post-Step Verification**:
    - After every skill execution in YOLO mode, the orchestrator MUST perform the full validator stack defined in `artifact-contracts.yaml`:
        1. **Level 2 (Generic)**: Execute the `verification.generic_validator` for the produced artifact.
        2. **Level 3 (Specialized)**: Execute all scripts listed in `verification.specialized_validators`.
        3. **LLM Self-Review**: Perform a 1-shot internal review of the artifact against the `verification.llm_criteria` if present. 
    - **Failure Protocol**: If ANY check fails, the orchestrator MUST:
        - Stop the execution loop immediately.
        - Report the failure details in the Run Log.
        - Recommend the specific rollback command: `git reset --hard {PRE_YOLO_COMMIT}`. For no-mutation dry-runs, use `rollback_recommendation: "No mutation occurred; no reset required."`
- **YOLO Step Completion**:
    - A YOLO step is not complete when a command is merely named.
    - A YOLO step is complete only when the declared `output_artifact` exists, satisfies `artifact-contracts.yaml`, and is recorded in the run log.
    - For `local_command` steps, the orchestrator MUST use the exact `invocation.command`; it must not invent command names.
    - After each step, preserve only the declared output artifact, compact run-log entry, and fields required by the next step.
    - Stop immediately if the command output cannot be mapped to the declared `output_artifact`.
- **Approval Gates**: 
    - **`gate: none`**: No approval required. Execute immediately and continue to the next step. Record `gate_behavior: skipped_by_design` in run log.
    - Do not bypass standard approval gates in `guided_execution` or `autonomous_execution` mode. 
    - In `guided_execution`, the orchestrator MUST record an explicit `gate_result: approved_by_user` (including `approved_at` and `approved_by`) in the run log before proceeding. Implicit approval is forbidden.
    - In `yolo_execution`, approval gates are operationally bypassed only after eligibility checks, but they MUST remain present in the machine-readable plan and run log with `gate_behavior: bypassed_by_yolo`.
- **Research & Subset Runs**:
    - Research-mode or subset workflow runs (e.g., executing only Steps 1 & 2) MUST still produce contract-valid `workflow_orchestration_plan` and `run_log` artifacts. 
    - Research mode may limit steps, but it MUST NOT relax Section 11 (must use `artifact_id` and `chosen_workflow_id`), `validator_stack`, path normalization, or approval-gate logging requirements.
    - **Formal Subset Semantics**: When executing a subset of a registry workflow, the plan MUST set `subset_run: true` and define `included_steps` (contiguous from step 1), `excluded_steps` (with reasons), and matching `steps` entries. This allows `validate-plan.py` to verify the subset against the full registry definition.
- **Strict Path Hygiene**:
    - Generated artifacts, plans, run logs, and user-facing summaries MUST use relative paths and NEVER use absolute `file:///` links. This applies to both the file content and the final response text.

## Local Command Execution

When executing a `local_command` step, the orchestrator MUST:

1. Read the skill's `invocation` block from `skill-registry.yaml`.
2. **Environment Pre-flight**: Verify the `invocation.runtime` is available in the local environment. If the runtime is missing, stop and report the environment mismatch.
3. Pass only the declared `input_artifact` plus the minimal necessary context.
4. Invoke the declared `command`; do not invent command names.
5. Treat the declared `output_artifact` as the only valid result of the step.
6. Append a compact run-log entry before continuing.
7. Summarize prior full artifacts once more than one artifact exists in context.
8. **Ghost Artifact Handling**: If a skill produces files or artifacts not declared in the `output_artifact` contract, the orchestrator MUST NOT pass them forward as context. Record undeclared outputs in the run log and require user approval before proceeding if they contaminate the workspace.
9. Stop if the command, input artifact, output artifact, or runtime is missing.

A `local_command` step is not complete until its declared `output_artifact` exists and satisfies the next handoff contract.

## Hard Stop Conditions
The orchestrator MUST stop and report instead of continuing when any of these occur:
- The skill is `external`, `external_required`, or `prompt_only` **and is not part of an automatic `implementation-workflow` invocation**.
- The next step is `workflow-orchestrator` itself, unless the mode is `plan_only`.
- The expected output artifact is missing, malformed, or does not satisfy `artifact-contracts.yaml`.
- The selected workflow does not explicitly allow the requested execution mode.
- The run log cannot be created or updated.
- The working tree is dirty before `autonomous_execution` or `yolo_execution`.
- The current branch is `main` or `master` during a mode that can mutate files.
- **Interrupt Protocol**: If execution is interrupted, the orchestrator MUST attempt to save a partial Run Log to preserve the state of completed steps.
- More than one retry would be required for the same step.
- The current context contains more than one full artifact from prior steps; summarize earlier artifacts before continuing.

**Exception for implementation-workflow:** Steps within `implementation-workflow` that have `gate: none` do NOT trigger hard stops—they continue to the next step automatically.

## References
- [Validator Stack Policy](references/validator-stack-policy.md)
- [Workflow Orchestration Template](references/workflow-orchestration-template.md)
- [Skill Registry](references/skill-registry.yaml)
- [Workflow Registry](references/workflow-registry.yaml)
- [Artifact Contracts](references/artifact-contracts.yaml)
- [Execution Modes](references/execution-modes.md)
- [Git Safety Policy](references/git-safety-policy.md)
- [Recovery Policy](references/recovery-policy.md)
- [Approval Gates](references/approval-gates.md)
- [Run Log Template](references/run-log-template.md)
- [Usage Research Scenarios](references/usage-research-scenarios.yaml)
- [Usage Research Rubric](../../docs/usage-research-rubric.md)

