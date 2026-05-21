"""Specialized Level 3 validator for workflow-orchestration-plan artifacts."""

import os
import sys
import re
import yaml
import argparse

from _validator_utils import format_error, load_workflow_registry, load_artifact_contracts, load_skill_registry

# Stable error codes
WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"
EXECUTION_MODE_DENIED = "EXECUTION_MODE_DENIED"
INPUT_MISMATCH = "INPUT_MISMATCH"
STEP_COUNT_MISMATCH = "STEP_COUNT_MISMATCH"
STEP_SKILL_MISMATCH = "STEP_SKILL_MISMATCH"
STEP_TYPE_MISMATCH = "STEP_TYPE_MISMATCH"
GATE_MISMATCH = "GATE_MISMATCH"
INPUT_ARTIFACT_MISMATCH = "INPUT_ARTIFACT_MISMATCH"
OUTPUT_ARTIFACT_MISMATCH = "OUTPUT_ARTIFACT_MISMATCH"
ARTIFACT_NOT_CONTRACTED = "ARTIFACT_NOT_CONTRACTED"
GATE_BEHAVIOR_MISSING = "GATE_BEHAVIOR_MISSING"
SIMULATED_GATE_CLASH = "SIMULATED_GATE_CLASH"
STOP_CONDITIONS_EMPTY = "STOP_CONDITIONS_EMPTY"
SUBSET_NOT_CONTIGUOUS = "SUBSET_NOT_CONTIGUOUS"
SECTION_11_MALFORMED = "SECTION_11_MALFORMED"
ABSOLUTE_PATH_DETECTED = "ABSOLUTE_PATH_DETECTED"
HALLUCINATED_SKILL = "HALLUCINATED_SKILL"
MISSING_DECISION_FIELD = "MISSING_DECISION_FIELD"
INVALID_CONDITIONAL_BRANCH = "INVALID_CONDITIONAL_BRANCH"


def _validate_conditional_step(step, workflow_id, repo_root="."):
    """
    Validate a conditional workflow step.

    Args:
        step: The step dictionary with conditional=true
        workflow_id: The workflow ID (for error messages)
        repo_root: Repository root for loading registries

    Returns:
        List of error strings (empty if no errors)
    """
    errors = []

    # Check for required decision_field
    decision_field = step.get("decision_field")
    if not decision_field:
        errors.append(format_error(MISSING_DECISION_FIELD, f"Step {step.get('id')} missing 'decision_field'"))
        return errors

    # Load skill registry to validate skill references
    skill_reg = load_skill_registry(repo_root)
    if skill_reg is None:
        errors.append(format_error(WORKFLOW_NOT_FOUND, "Failed to load skill-registry.yaml"))
        return errors

    # Collect all valid skill IDs from all ecosystems
    valid_skills = set()
    for ecosystem in skill_reg.get("ecosystems", {}).values():
        for skill in ecosystem.get("skills", []):
            valid_skills.add(skill["id"])

    # Validate if_true branch
    if_true = step.get("if_true")
    if if_true:
        if_true_skill = if_true.get("skill")
        if if_true_skill and if_true_skill not in valid_skills:
            errors.append(
                format_error(HALLUCINATED_SKILL, f"Step {step.get('id')} if_true branch references non-existent skill '{if_true_skill}'")
            )

        # Check that if_true has a way forward (skill or next_step)
        has_forward = if_true_skill or if_true.get("next_step")
        if not has_forward:
            errors.append(
                format_error(INVALID_CONDITIONAL_BRANCH, f"Step {step.get('id')} if_true branch must have either 'skill' or 'next_step'")
            )

    # Validate if_false branch
    if_false = step.get("if_false")
    if if_false:
        if_false_skill = if_false.get("skill")
        if if_false_skill and if_false_skill not in valid_skills:
            errors.append(
                format_error(HALLUCINATED_SKILL, f"Step {step.get('id')} if_false branch references non-existent skill '{if_false_skill}'")
            )

        # Check that if_false has a way forward (skill or next_step)
        has_forward = if_false_skill or if_false.get("next_step")
        if not has_forward:
            errors.append(
                format_error(INVALID_CONDITIONAL_BRANCH, f"Step {step.get('id')} if_false branch must have either 'skill' or 'next_step'")
            )

    return errors


def validate_plan(plan_path, repo_root="."):
    errors = []

    # 1. Load Registries using shared utilities
    workflow_reg = load_workflow_registry(repo_root)
    artifact_con = load_artifact_contracts(repo_root)
    skill_reg = load_skill_registry(repo_root)

    if workflow_reg is None or artifact_con is None or skill_reg is None:
        errors.append(format_error(WORKFLOW_NOT_FOUND, "Failed to load one or more registries from workflow-orchestrator references."))
        return errors

    # 2. Extract Section 11 from Plan
    if not os.path.exists(plan_path):
        errors.append(format_error(SECTION_11_MALFORMED, f"Plan file not found: {plan_path}"))
        return errors

    with open(plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r"## 11\. Machine-readable plan\s+```yaml\s+(.*?)\s+```", content, re.DOTALL | re.IGNORECASE)
    if not match:
        errors.append(format_error(SECTION_11_MALFORMED, "Section 11 YAML block not found or malformed."))
        return errors

    yaml_text = match.group(1)
    try:
        plan_data = yaml.safe_load(yaml_text)
    except Exception as e:
        errors.append(format_error(SECTION_11_MALFORMED, f"Failed to parse Section 11 YAML: {e}"))
        return errors

    # 3. Basic Field Checks
    if plan_data.get("artifact_id") != "workflow_orchestration_plan":
        errors.append(format_error(SECTION_11_MALFORMED, f"artifact_id mismatch: expected 'workflow_orchestration_plan', got '{plan_data.get('artifact_id')}'"))

    if "status" not in plan_data:
        errors.append(format_error(SECTION_11_MALFORMED, "Missing 'status' in Section 11"))

    chosen_id = plan_data.get("chosen_workflow_id")
    if not chosen_id:
        errors.append(format_error(WORKFLOW_NOT_FOUND, "Missing chosen_workflow_id in Section 11"))
        return errors

    workflow = next((w for w in workflow_reg.get("workflows", []) if w["id"] == chosen_id), None)
    if not workflow:
        errors.append(format_error(WORKFLOW_NOT_FOUND, f"chosen_workflow_id '{chosen_id}' not found in workflow-registry.yaml"))
        return errors

    # 4. Path Hygiene Check (No absolute paths in YAML)
    yaml_dump = yaml.dump(plan_data)
    abs_path_patterns = [r"[a-zA-Z]:\\", r"/[Uu]sers/", r"/[Hh]ome/"]
    for pattern in abs_path_patterns:
        if re.search(pattern, yaml_dump):
            errors.append(
                format_error(ABSOLUTE_PATH_DETECTED, f"Absolute path detected in YAML block (pattern: {pattern}). All paths must be relative.")
            )

    # 5. Execution Mode Check
    exec_mode = plan_data.get("execution_mode")
    if exec_mode not in workflow.get("allowed_execution_modes", []):
        errors.append(format_error(EXECUTION_MODE_DENIED, f"execution_mode '{exec_mode}' not allowed for workflow '{chosen_id}'"))

    # 6. Initial Inputs Check
    plan_inputs = plan_data.get("initial_inputs", [])
    reg_inputs = workflow.get("initial_inputs", [])

    plan_input_ids = {i["id"] for i in plan_inputs}
    reg_input_ids = {i["id"] for i in reg_inputs}

    if plan_input_ids != reg_input_ids:
        errors.append(format_error(INPUT_MISMATCH, f"initial_inputs mismatch: plan has {plan_input_ids}, registry expects {reg_input_ids}"))

    for i in plan_inputs:
        if "type" not in i or "required" not in i:
            errors.append(format_error(INPUT_MISMATCH, f"Initial input '{i.get('id')}' missing 'type' or 'required' fields"))

    # 7. Step Validation
    plan_steps = plan_data.get("steps", [])
    reg_steps = workflow.get("steps", [])
    subset_run = plan_data.get("subset_run", False)

    if subset_run:
        if not plan_data.get("subset_reason"):
            errors.append(format_error(SUBSET_NOT_CONTIGUOUS, "Missing 'subset_reason' for subset_run"))

        included_ids = plan_data.get("included_steps", [])
        excluded_data = plan_data.get("excluded_steps", [])
        excluded_ids = [s.get("id") for s in excluded_data]

        all_reg_ids = [s["id"] for s in reg_steps]
        all_plan_ids = set(included_ids) | set(excluded_ids)

        if set(all_reg_ids) != all_plan_ids:
            errors.append(format_error(SUBSET_NOT_CONTIGUOUS, f"Subset mismatch: registry steps {all_reg_ids} not fully accounted for in plan ({all_plan_ids})"))

        # Contiguity Check: included_steps must be a contiguous subsequence of registry steps
        if included_ids:
            try:
                first_idx = all_reg_ids.index(included_ids[0])
                last_idx = all_reg_ids.index(included_ids[-1])
                expected_subsequence = all_reg_ids[first_idx : last_idx + 1]
                if included_ids != expected_subsequence:
                    errors.append(
                        format_error(SUBSET_NOT_CONTIGUOUS, f"Non-contiguous subset: included_steps {included_ids} is not a contiguous sequence in workflow registry")
                    )
            except ValueError as e:
                errors.append(format_error(SUBSET_NOT_CONTIGUOUS, f"Step ID in included_steps not found in registry: {e}"))

        steps_to_validate = []
        for s_id in included_ids:
            p_step = next((s for s in plan_steps if s["id"] == s_id), None)
            r_step = next((s for s in reg_steps if s["id"] == s_id), None)
            if not p_step:
                errors.append(format_error(SUBSET_NOT_CONTIGUOUS, f"Included step {s_id} missing from 'steps' list"))
            elif not r_step:
                errors.append(format_error(WORKFLOW_NOT_FOUND, f"Included step {s_id} not found in registry"))
            else:
                steps_to_validate.append((p_step, r_step))
    else:
        if len(plan_steps) != len(reg_steps):
            errors.append(format_error(STEP_COUNT_MISMATCH, f"Step count mismatch: plan has {len(plan_steps)}, registry expects {len(reg_steps)}"))
        steps_to_validate = list(zip(plan_steps, reg_steps))

    for p_step, r_step in steps_to_validate:
        s_id = p_step.get("id")
        if "status" not in p_step:
            errors.append(format_error(SECTION_11_MALFORMED, f"Step {s_id} missing 'status'"))

        # For conditional steps in plans, skip the normal field comparison since they store data in branches
        if p_step.get("conditional") and r_step.get("conditional"):
            # Validate conditional steps
            conditional_errors = _validate_conditional_step(p_step, chosen_id, repo_root)
            errors.extend(conditional_errors)
            # Skip the normal field validations for conditional steps
            continue

        skill = p_step.get("skill")
        if skill != r_step.get("skill"):
            errors.append(format_error(STEP_SKILL_MISMATCH, f"Step {s_id} skill mismatch: plan='{skill}', reg='{r_step.get('skill')}'"))

        s_type = p_step.get("step_type")
        if s_type != r_step.get("step_type"):
            errors.append(format_error(STEP_TYPE_MISMATCH, f"Step {s_id} step_type mismatch: plan='{s_type}', reg='{r_step.get('step_type')}'"))

        gate = p_step.get("gate")
        if gate != r_step.get("gate"):
            errors.append(format_error(GATE_MISMATCH, f"Step {s_id} gate mismatch: plan='{gate}', reg='{r_step.get('gate')}'"))

        p_in_src = p_step.get("input_source")
        r_in_src = r_step.get("input_source")
        if p_in_src != r_in_src:
            errors.append(format_error(INPUT_ARTIFACT_MISMATCH, f"Step {s_id} input_source mismatch: plan='{p_in_src}', reg='{r_in_src}'"))

        p_in_art = p_step.get("input_artifact")
        r_in_art = r_step.get("input_artifact")
        if p_in_art != r_in_art:
            errors.append(format_error(INPUT_ARTIFACT_MISMATCH, f"Step {s_id} input_artifact mismatch: plan='{p_in_art}', reg='{r_in_art}'"))

        p_out_art = p_step.get("output_artifact")
        r_out_art = r_step.get("output_artifact")
        if p_out_art != r_out_art:
            errors.append(format_error(OUTPUT_ARTIFACT_MISMATCH, f"Step {s_id} output_artifact mismatch: plan='{p_out_art}', reg='{r_out_art}'"))

        if p_out_art:
            contract = next((a for a in artifact_con.get("artifacts", []) if a["id"] == p_out_art), None)
            if not contract:
                errors.append(format_error(ARTIFACT_NOT_CONTRACTED, f"Step {s_id} output_artifact '{p_out_art}' not found in artifact-contracts.yaml"))
            else:
                skill_meta = None
                for ecosystem in skill_reg.get("ecosystems", {}).values():
                    skill_meta = next((s for s in ecosystem.get("skills", []) if s["id"] == skill), None)
                    if skill_meta:
                        break

                actual_producer = None
                if skill_meta and skill_meta.get("artifact") == p_out_art:
                    actual_producer = skill
                elif contract.get("produced_by") == skill:
                    actual_producer = skill

                if not actual_producer:
                    errors.append(
                        format_error(ARTIFACT_NOT_CONTRACTED, f"Step {s_id} skill '{skill}' is not contracted to produce '{p_out_art}'")
                    )

    # 8. Approval Gates & Behavior Check
    plan_gates = plan_data.get("approval_gates", [])
    step_gates = [s.get("gate") for s in plan_steps if s.get("gate")]
    if plan_gates != step_gates:
        errors.append(format_error(GATE_MISMATCH, f"approval_gates mismatch: plan has {plan_gates}, steps have {step_gates}"))

    gate_behavior = plan_data.get("gate_behavior", {})
    for g in plan_gates:
        if g not in gate_behavior:
            errors.append(format_error(GATE_BEHAVIOR_MISSING, f"Missing gate_behavior for gate '{g}'"))
        elif gate_behavior[g] == "simulated_for_research":
            for s in plan_steps:
                if s.get("gate") == g and s.get("approved_by_user") is True:
                    errors.append(
                        format_error(SIMULATED_GATE_CLASH, f"Gate clash: step {s.get('id')} claims 'approved_by_user: true' but gate '{g}' is simulated")
                    )

    # 9. Stop Conditions Check
    stop_conds = plan_data.get("stop_conditions", [])
    if not stop_conds or not isinstance(stop_conds, list) or len(stop_conds) == 0:
        errors.append(format_error(STOP_CONDITIONS_EMPTY, "stop_conditions missing or empty in Section 11"))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a workflow orchestration plan artifact.")
    parser.add_argument("artifact_path", nargs="?", help="Path to the .md plan file")
    parser.add_argument("--repo-root", default=".", help="Root directory of the repository")
    parser.add_argument("--list-codes", action="store_true", help="List all error codes and exit")
    args = parser.parse_args(argv)

    if args.list_codes:
        codes = [
            WORKFLOW_NOT_FOUND,
            EXECUTION_MODE_DENIED,
            INPUT_MISMATCH,
            STEP_COUNT_MISMATCH,
            STEP_SKILL_MISMATCH,
            STEP_TYPE_MISMATCH,
            GATE_MISMATCH,
            INPUT_ARTIFACT_MISMATCH,
            OUTPUT_ARTIFACT_MISMATCH,
            ARTIFACT_NOT_CONTRACTED,
            GATE_BEHAVIOR_MISSING,
            SIMULATED_GATE_CLASH,
            STOP_CONDITIONS_EMPTY,
            SUBSET_NOT_CONTIGUOUS,
            SECTION_11_MALFORMED,
            ABSOLUTE_PATH_DETECTED,
            HALLUCINATED_SKILL,
            MISSING_DECISION_FIELD,
            INVALID_CONDITIONAL_BRANCH,
        ]
        print("Stable error codes for plan validation:")
        for code in codes:
            print(f"  {code}")
        return 0

    if not args.artifact_path:
        parser.print_usage()
        return 1

    errs = validate_plan(args.artifact_path, args.repo_root)
    if errs:
        for e in errs:
            print(f"ERROR {e}")
        return 1
    else:
        print("Plan validation passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
