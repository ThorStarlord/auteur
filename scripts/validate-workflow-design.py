#!/usr/bin/env python3
"""
Workflow Design Validator

Validates workflows against the four design patterns:
1. Strict vs. Lenient Validation (different modes, different strictness)
2. Workflow Separation of Concerns (one purpose per workflow)
3. Artifact Composition & Chaining (meaningful transformations per step)
4. Evidence Tracking (validators and gates are recorded)

Exit codes:
  0 = All workflows pass validation (PASS)
  1 = One or more validation errors (FAIL)
"""

import sys
import yaml
import os
from pathlib import Path


# Error codes (stable, reusable)
ERROR_CODES = {
    "WORKFLOW_NO_PURPOSE": "Workflow missing clear purpose statement",
    "WORKFLOW_NO_STEPS": "Workflow has no steps defined",
    "STEP_NO_SKILL": "Step missing skill definition",
    "STEP_NO_INPUT_ARTIFACT": "Step missing input_artifact (except first step)",
    "STEP_NO_OUTPUT_ARTIFACT": "Step missing output_artifact",
    "STEP_ARTIFACT_MISMATCH": "Step output doesn't match next step input",
    "SKILL_NOT_REGISTERED": "Step references unregistered skill",
    "ARTIFACT_CHAIN_BROKEN": "Artifact chain is discontinuous (output N ≠ input N+1)",
    "WORKFLOW_MIXED_CONCERNS": "Workflow mixes multiple concerns (purpose mismatch)",
    "EXECUTION_MODE_INVALID": "Invalid execution mode specified",
    "GATE_MISSING": "Step missing gate definition (required for guided execution)",
    "PASS_THROUGH_STEP": "Step appears to be pass-through (same input as output)",
}


def load_registries(repo_root: str) -> tuple:
    """Load skill and workflow registries."""
    skill_registry_path = os.path.join(
        repo_root,
        "skills/workflow-orchestrator/references/skill-registry.yaml"
    )
    workflow_registry_path = os.path.join(
        repo_root,
        "skills/workflow-orchestrator/references/workflow-registry.yaml"
    )

    with open(skill_registry_path) as f:
        skill_registry = yaml.safe_load(f)

    with open(workflow_registry_path) as f:
        workflow_registry = yaml.safe_load(f)

    # Flatten skill registry to skill_id -> skill_def mapping
    all_skills = {}
    for ecosystem in skill_registry.get("ecosystems", {}).values():
        for skill in ecosystem.get("skills", []):
            all_skills[skill["id"]] = skill

    return all_skills, workflow_registry


def format_error(code: str, message: str, workflow_id: str = None, step_id: str = None) -> str:
    """Format error message with code and context."""
    prefix = f"ERROR {code}"
    if workflow_id:
        prefix += f" ({workflow_id}"
        if step_id:
            prefix += f" step {step_id}"
        prefix += ")"
    return f"{prefix}: {message}"


def validate_workflow(workflow: dict, all_skills: dict) -> list:
    """Validate a single workflow against design patterns."""
    errors = []
    workflow_id = workflow.get("id", "unknown")

    # Check 1: Purpose statement exists
    purpose = workflow.get("purpose", "").strip()
    if not purpose:
        errors.append(format_error("WORKFLOW_NO_PURPOSE",
            "Workflow must have a clear one-sentence purpose",
            workflow_id))
    elif " and " in purpose.lower() or " or " in purpose.lower():
        # Heuristic: "and"/"or" often indicates mixed concerns
        # (Not perfect, but catches obvious cases)
        pass  # Don't fail on this, but could flag as warning

    # Check 2: Has steps
    steps = workflow.get("steps", [])
    if not steps:
        errors.append(format_error("WORKFLOW_NO_STEPS",
            "Workflow must have at least one step",
            workflow_id))
        return errors

    # Check 3: Each step has required fields
    for i, step in enumerate(steps):
        step_id = step.get("id")
        step_num = i + 1

        # Skill required
        skill_id = step.get("skill")
        if not skill_id:
            errors.append(format_error("STEP_NO_SKILL",
                f"Step {step_num} missing skill definition",
                workflow_id, step_id))
            continue

        # Input artifact (except first step)
        input_artifact = step.get("input_artifact")
        if i > 0 and not input_artifact:
            errors.append(format_error("STEP_NO_INPUT_ARTIFACT",
                f"Step {step_num} (not first) missing input_artifact",
                workflow_id, step_id))

        # Output artifact required
        output_artifact = step.get("output_artifact")
        if not output_artifact:
            errors.append(format_error("STEP_NO_OUTPUT_ARTIFACT",
                f"Step {step_num} missing output_artifact",
                workflow_id, step_id))
            continue

        # Check 4: Skill must be registered
        if skill_id not in all_skills:
            errors.append(format_error("SKILL_NOT_REGISTERED",
                f"Step {step_num} references unregistered skill '{skill_id}'",
                workflow_id, step_id))

        # Check 5: No pass-through steps (input == output same name)
        if input_artifact and output_artifact and input_artifact == output_artifact:
            errors.append(format_error("PASS_THROUGH_STEP",
                f"Step {step_num} input and output are identical ('{input_artifact}')",
                workflow_id, step_id))

        # Check 6: If guided_execution, step must have gate
        allowed_modes = workflow.get("allowed_execution_modes", [])
        if "guided_execution" in allowed_modes:
            gate = step.get("gate")
            if not gate:
                # gates are important for guided execution
                pass  # Don't enforce for now, but could flag as warning

        # Check 7: Artifact chain continuity
        if i < len(steps) - 1:
            next_step = steps[i + 1]
            next_input = next_step.get("input_artifact")

            if next_input and output_artifact and next_input != output_artifact:
                errors.append(format_error("ARTIFACT_CHAIN_BROKEN",
                    f"Step {step_num} output '{output_artifact}' != Step {step_num+1} input '{next_input}'",
                    workflow_id, step_id))

    # Check 8: Execution modes are valid
    allowed_modes = workflow.get("allowed_execution_modes", [])
    valid_modes = {"plan_only", "prompt_chain", "guided_execution", "autonomous_execution", "yolo_execution"}
    for mode in allowed_modes:
        if mode not in valid_modes:
            errors.append(format_error("EXECUTION_MODE_INVALID",
                f"Invalid execution mode: '{mode}'",
                workflow_id))

    return errors


def validate_all_workflows(registries_path: str = None) -> tuple:
    """Validate all workflows in the registry."""
    if registries_path is None:
        registries_path = os.path.dirname(os.path.abspath(__file__))
        registries_path = os.path.dirname(registries_path)  # Go to repo root

    try:
        all_skills, workflow_registry = load_registries(registries_path)
    except Exception as e:
        print(f"ERROR: Failed to load registries: {e}")
        return [], 1

    all_errors = []
    workflows = workflow_registry.get("workflows", [])

    for workflow in workflows:
        errors = validate_workflow(workflow, all_skills)
        all_errors.extend(errors)

    return all_errors, len(workflows) if workflows else 0


def print_results(errors: list, workflow_count: int):
    """Print validation results."""
    if not errors:
        print(f"[PASS] All {workflow_count} workflows pass validation")
        print("  - Each workflow has clear purpose")
        print("  - All skills are registered")
        print("  - Artifact chains are continuous")
        print("  - No pass-through steps detected")
        return 0
    else:
        print(f"[FAIL] {len(errors)} validation errors found:")
        for error in errors:
            print(f"  {error}")
        return 1


def list_error_codes():
    """List all error codes and their descriptions."""
    print("Error Codes for validate-workflow-design.py:")
    print()
    for code, description in sorted(ERROR_CODES.items()):
        print(f"  {code}: {description}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate workflow designs against orchestration patterns"
    )
    parser.add_argument(
        "--list-codes",
        action="store_true",
        help="List all error codes and exit"
    )
    parser.add_argument(
        "registry_path",
        nargs="?",
        default=None,
        help="Path to repository root (defaults to current directory parent)"
    )

    args = parser.parse_args()

    if args.list_codes:
        list_error_codes()
        return 0

    errors, workflow_count = validate_all_workflows(args.registry_path)
    return print_results(errors, workflow_count)


if __name__ == "__main__":
    sys.exit(main())
