---
name: project-classifier
description: analyze a raw project description to classify project type and recommend the optimal workflow. use when you have a project goal but don't know which workflow to use.
---

# project-classifier

Automatically classifies project types from raw descriptions and recommends the optimal orchestration workflow. This skill eliminates the need for users to know which workflow to invoke.

## Workflow

1. **Fog Capture**: Listen to the raw project description (product idea, business goal, technical problem, etc.)
2. **Type Classification**: Identify the project type from predefined categories
3. **Complexity Assessment**: Evaluate scope (MVP vs. scaling, technical depth, stakeholder count)
4. **Execution Mode Selection**: Recommend appropriate mode (plan_only, guided_execution, autonomous_execution)
5. **Workflow Matching**: Select the most suitable workflow from registry
6. **Input Specification**: Identify required inputs for the selected workflow
7. **Synthesis**: Produce a Project Classification Brief with clear routing

## Project Type Classification

Map raw descriptions to these categories:

- **SaaS/Platform**: Multi-user, recurring revenue, cloud-hosted (e.g., CRM, observability tool, marketplace)
- **Content/Creator**: Publishing, distribution, audience building (e.g., learning platform, blog network)
- **Developer Tool**: CLI, library, package, build system, testing framework
- **Consumer App**: Mobile-first, retention-focused, gamification (e.g., fitness app, social)
- **Internal/Enterprise**: Workflow optimization, data aggregation, admin tools
- **Open Source**: Community-driven, ecosystem contribution
- **Research/Experimental**: Proof-of-concept, validation focus, limited scope

## Workflow Selection Logic

| Project Type | Primary Workflow | Fallback |
|:---|:---|:---|
| SaaS/Platform | product-discovery-sprint → product-strategy-sprint | product-autonomous-sprint |
| Content/Creator | product-discovery-sprint → full-local-sensemaking | product-autonomous-sprint |
| Developer Tool | docs-architecture → full-local-sensemaking | autonomous-sprint-preflight |
| Consumer App | product-discovery-sprint → product-autonomous-sprint | full-local-sensemaking |
| Internal/Enterprise | autonomous-sprint-preflight → docs-architecture | fast-local-diagnostic |
| Open Source | full-local-sensemaking | fast-local-diagnostic |
| Research/Experimental | fast-local-diagnostic → full-local-sensemaking | plan_only |

## Output Format

Every response must follow the [Project Classification Brief](references/project-classification-template.md) structure.

## Boundary Rules

1. **No Implementation**: Output is diagnostic only. Do not execute recommended workflows.
2. **Registry Grounding**: All `recommended_workflow_id` values MUST be verified against `skills/workflow-orchestrator/references/workflow-registry.yaml`.
3. **Type Confidence**: If classification confidence is below 70%, recommend `plan_only` mode and note the ambiguity.
4. **Input Clarity**: If critical inputs for the selected workflow are missing from the description, explicitly call them out as "Required Before Execution".

## References

- [Project Classification Brief Template](references/project-classification-template.md)
- [Workflow Registry](../workflow-orchestrator/references/workflow-registry.yaml)
