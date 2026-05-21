# PRD: Sensemaking Skills V1 (Refactored Release)

## Status: Refactored (Five-Skill Pipeline)
## Date: 2026-05-13

## 1. Executive Summary
Sensemaking Skills V1 establishes a robust "meta-routing" layer for AI agents. It standardizes the transition from project "fog" (uncertainty) to actionable implementation through a five-stage pipeline: `problem-framer`, `unknowns-mapper`, `repo-sensemaker`, `workflow-orchestrator`, and `prompt-handoff`.

## 2. Problem Statement
Agents often jump into implementation ("building") before they understand the "problem under the problem" or the repository-level "fog". This leads to misaligned PRDs, incorrect architectural choices, and technical debt.

## 3. Goals
- Provide five package-valid core skills: `problem-framer`, `unknowns-mapper`, `repo-sensemaker`, `workflow-orchestrator`, and `prompt-handoff`.
- Enforce structural integrity via canonical output templates (14-section Repository Brief / 10-section Orchestration Plan).
- Enforce evidence-backed diagnosis with file-level citations.
- Maintain safety-first human-in-the-loop control through explicit execution modes and approval gates.

## 4. Key Features
- **Five-Skill Sensemaking Pipeline**: Sequential reduction of uncertainty from raw fog to prompt handoff.
- **Evidence-Backed Diagnosis**: `repo-sensemaker` must cite specific file evidence for the "Weakest Boundary."
- **Execution Mode Matrix**: Permissioned levels from `plan_only` to `autonomous_execution`.
- **Structured Registries**: Valid YAML for both skills and workflows.
- **Handoff Contracts**: Machine-readable handoff blocks to prevent ambiguous routing.
- **Negative Fixtures**: Examples proving the system refuses unsafe autonomous actions.
- **Governance**: Automated validation of artifact contracts via `validate-repo.py`.

## 5. Functional Requirements
- **Problem Framing**: Identify the "object under pressure" before mapping technical unknowns.
- **Unknowns Mapping**: Separate knowns from assumptions and define stopping rules for research.
- **Diagnostic Brief**: Produce a 14-section brief naming the weakest boundary and citing evidence.
- **Orchestration Planning**: Produce a 10-section plan naming the workflow, mode, and safety gates.
- **Prompt Handoff**: Package the sensemaking trace into a ready-to-copy prompt for downstream skills.
- **Safe Refusal**: Refuse to route downstream if unknowns are fundamental or the execution request is unsafe.

## 6. Non-Functional Requirements
- **Decoupling**: Diagnosis (`repo-sensemaker`) must remain separate from Action (`workflow-orchestrator`).
- **Portability**: No absolute file paths in examples or templates.
- **Validation-as-Policy**: All core artifacts must pass the governance script.

## 7. Success Metrics
- 100% compliance with canonical 14-section (Brief) and 10-section (Plan) templates.
- 0 instances of unapproved autonomous execution.
- Successful self-dogfooding of the five-skill pipeline on the `sensemaking-skills` repository.

## 8. V1 Skill Set
1. `problem-framer`: Capture fog and identify root pressure.
2. `unknowns-mapper`: Map knowledge gaps and research paths.
3. `repo-sensemaker`: Analyze repository health and weakest boundaries.
4. `workflow-orchestrator`: Plan and coordinate execution.
5. `prompt-handoff`: Bridge the sensemaking gap to specialized tools.
