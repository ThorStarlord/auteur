# Project Classification Brief

## 1. Project description (input)

The raw fog or project goal as provided.

## 2. Classified project type

Primary type from the classification taxonomy, with confidence score (0-100%).

## 3. Type characteristics

Specific traits from the input that led to this classification.

## 4. Complexity assessment

**Scope**: MVP / Growth / Enterprise
**Technical Depth**: Low / Medium / High
**Stakeholder Count**: Solo / Small Team / Cross-functional

## 5. Recommended execution mode

- **plan_only**: Just plan, no commitment. Good for validation.
- **guided_execution**: User reviews at each step. Good for new domains.
- **autonomous_execution**: Automated gates. Good for familiar types.

Reasoning for mode selection.

## 6. Recommended workflow

The primary workflow from workflow-registry.yaml that aligns with this project type.

## 7. Workflow pipeline (if multi-step)

If the workflow chains to another, note the full sequence:
```
workflow_1 → workflow_2 → workflow_3
```

## 8. Required inputs before execution

What the user/system must provide:
- Repository state (if applicable)
- Raw project description (already provided)
- Domain expertise level
- Timeline constraints
- Budget/resource constraints

## 9. Next immediate step

What the user should do first:
1. Run the recommended workflow
2. Provide additional context
3. Gather team alignment first
4. Other

## 10. Alternative workflows

If the primary recommendation doesn't fit, suggest 1-2 alternatives with trade-offs.

## 11. Machine-readable classification

```yaml
artifact_id: project_classification_brief
project_type: <SaaS/Platform | Content | Developer Tool | Consumer App | Internal/Enterprise | Open Source | Research>
type_confidence_score: 0-100
recommended_workflow_id: <from workflow-registry.yaml>
recommended_execution_mode: <plan_only | guided_execution | autonomous_execution>
execution_mode_rationale: "..."
required_inputs:
  - field_name: <value or "required">
alternative_workflows:
  - id: <workflow_id>
    rationale: "..."
    trade_offs: "..."
```

## 12. Ready-to-execute prompt

Prompt that can be copied directly to invoke the recommended workflow in the orchestrator.

Example:
```
python scripts/orchestration-runner.py <workflow_id> --mode <mode>
```
