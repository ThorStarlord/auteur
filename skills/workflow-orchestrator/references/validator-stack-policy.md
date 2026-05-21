# Validator Stack Policy

This policy defines the hierarchy, execution order, and enforcement rules for the validator ecosystem in the `sensemaking-skills` repository.

## 1. Validator Hierarchy

Validators are organized into three levels of increasing specificity:

| Level | Type | Scope | Primary Script |
| :--- | :--- | :--- | :--- |
| **Level 1** | **Structural** | Repository integrity, registries, and branch safety. | `scripts/validate-repo.py` |
| **Level 2** | **Generic** | Artifact contract compliance (sections, machine fields, paths). | `scripts/validate-artifact.py` |
| **Level 3** | **Specialized** | Semantic fidelity, evidence grounding, and domain-specific logic. | `scripts/validate-brief.py`, `scripts/validate-plan.py` |

## 2. Execution Order

The orchestrator MUST execute validators in the following order. If any level fails, execution MUST stop immediately.

1.  **Pre-flight (Level 1)**: Run Level 1 validators before starting any workflow that can mutate the repository.
2.  **Post-Step (Level 2)**: Run Level 2 validators immediately after a skill produces its declared `output_artifact`.
3.  **Post-Step (Level 3)**: Run all Level 3 validators registered for the specific `artifact_id` in `artifact-contracts.yaml`.

## 3. Enforcement Rules

- **Zero Tolerance**: In `yolo_execution` and `autonomous_execution` modes, any validator failure triggers an immediate hard stop and rollback recommendation.
- **Contract as Source of Truth**: The `artifact-contracts.yaml` file is the canonical registry of which Level 2 and Level 3 validators apply to each artifact.
- **Run Log Recording**: Every validator execution (command and result) MUST be recorded in the `run_log.md` for that session.
- **Relative Path Mandate**: All validators MUST check for absolute `file:///` links and reject artifacts containing them.

## 4. Failure Protocol

When a validator fails:
1.  **Log**: Append the failure details to the `run_log.md`.
2.  **Halt**: Stop the orchestrator loop.
3.  **Advise**: In `yolo_execution`, provide the specific `git reset --hard` command to revert the workspace.
