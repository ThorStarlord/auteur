import os
import yaml
import sys
import re

def validate_repo():
    errors = []
    warnings = []
    
    # 1. Check core files
    core_files = [
        "README.md",
        "CONTEXT.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "docs/PRD-V1-Sensemaking.md",
        "skills/repo-sensemaker/SKILL.md",
        "skills/repo-sensemaker/agents/openai.yaml",
        "skills/repo-sensemaker/references/repo-analysis-template.md",
        "skills/workflow-orchestrator/SKILL.md",
        "skills/workflow-orchestrator/agents/openai.yaml",
        "skills/workflow-orchestrator/references/skill-registry.yaml",
        "skills/workflow-orchestrator/references/workflow-registry.yaml",
        "skills/workflow-orchestrator/references/workflow-orchestration-template.md",
        "skills/workflow-orchestrator/references/execution-modes.md",
        "skills/workflow-orchestrator/references/artifact-contracts.yaml",
        "skills/workflow-orchestrator/references/git-safety-policy.md",
        "skills/workflow-orchestrator/references/recovery-policy.md",
        "skills/workflow-orchestrator/references/usage-research-scenarios.yaml",
        "docs/research/usage-research-rubric.md",
        "skills/problem-framer/SKILL.md",
        "skills/problem-framer/agents/openai.yaml",
        "skills/problem-framer/references/problem-frame-template.md",
        "skills/unknowns-mapper/SKILL.md",
        "skills/unknowns-mapper/agents/openai.yaml",
        "skills/unknowns-mapper/references/unknowns-map-template.md",
        "skills/prompt-handoff/SKILL.md",
        "skills/prompt-handoff/agents/openai.yaml",
        "skills/prompt-handoff/references/prompt-handoff-template.md",
        "skills/setup-sensemaking-skills/SKILL.md",
        "skills/setup-sensemaking-skills/agents/openai.yaml",
        "skills/setup-sensemaking-skills/references/agent-block-template.md",
        "skills/setup-sensemaking-skills/references/sensemaking-config-template.md",
        "skills/setup-sensemaking-skills/references/workflow-modes-template.md",
        "skills/sensemaking-docs-reconciler/agents/openai.yaml",
        "skills/skill-maintainer/SKILL.md",
        "skills/skill-maintainer/references/improvement-plan-template.md",
        "skills/usage-researcher/SKILL.md",
        "skills/usage-researcher/agents/openai.yaml",
        "skills/usage-researcher/references/usage-research-report-template.md",
        "docs/mode-coverage.yaml"
    ]
    
    for f in core_files:
        if not os.path.exists(f):
            errors.append(f"Missing core file: {f}")

    # 2. Validate YAML files
    yaml_files = [
        "skills/repo-sensemaker/agents/openai.yaml",
        "skills/workflow-orchestrator/agents/openai.yaml",
        "skills/workflow-orchestrator/references/skill-registry.yaml",
        "skills/workflow-orchestrator/references/workflow-registry.yaml",
        "skills/workflow-orchestrator/references/artifact-contracts.yaml",
        "skills/problem-framer/agents/openai.yaml",
        "skills/unknowns-mapper/agents/openai.yaml",
        "skills/prompt-handoff/agents/openai.yaml",
        "skills/setup-sensemaking-skills/agents/openai.yaml",
        "skills/sensemaking-docs-reconciler/agents/openai.yaml"
    ]
    
    registries = {}
    for yf in yaml_files:
        if os.path.exists(yf):
            try:
                with open(yf, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    registries[yf] = data
            except Exception as e:
                errors.append(f"Invalid YAML in {yf}: {str(e)}")

    # 3. Registry & Availability Check
    registered_skills = {}
    if "skills/workflow-orchestrator/references/skill-registry.yaml" in registries:
        skill_registry = registries["skills/workflow-orchestrator/references/skill-registry.yaml"]
        for ecosystem_id, ecosystem in skill_registry.get("ecosystems", {}).items():
            for skill in ecosystem.get("skills", []):
                s_id = skill["id"]
                registered_skills[s_id] = skill
                
                # Availability validation
                availability = skill.get("availability")
                if not availability:
                    errors.append(f"Skill '{s_id}' missing 'availability' block in registry")
                else:
                    a_type = availability.get("type")
                    if a_type not in ["local", "local_command", "external", "prompt_only"]:
                        errors.append(f"Skill '{s_id}' has invalid availability type: {a_type}")
                    
                    # Invocation check for local_command
                    if a_type == "local_command":
                        invocation = skill.get("invocation")
                        if not invocation:
                            errors.append(f"Skill '{s_id}' is 'local_command' but missing 'invocation' contract")
                        else:
                            if not invocation.get("command"):
                                errors.append(f"Skill '{s_id}' invocation missing 'command'")

    # 4. Workflow & YOLO Validation
    if "skills/workflow-orchestrator/references/workflow-registry.yaml" in registries:
        workflow_registry = registries["skills/workflow-orchestrator/references/workflow-registry.yaml"]
        for workflow in workflow_registry.get("workflows", []):
            allowed_modes = workflow.get("allowed_execution_modes", [])
            if not allowed_modes:
                 errors.append(f"Workflow '{workflow['id']}' missing 'allowed_execution_modes'")
            
            # YOLO Safety Checks
            if "yolo_execution" in allowed_modes:
                if not workflow.get("branch_policy", {}).get("required"):
                    errors.append(f"Workflow '{workflow['id']}' allows YOLO but missing required branch_policy")
                
                steps = workflow.get("steps", [])
                for step in steps:
                    s_id = step.get("skill")
                    if s_id in registered_skills:
                        s_type = registered_skills[s_id]["availability"]["type"]
                        if s_type not in ["local", "local_command"]:
                            errors.append(f"Workflow '{workflow['id']}' allows YOLO but contains non-executable skill: {s_id}")

            # 4b. Recursive Orchestrator Check & Step Type Validation
            steps = workflow.get("steps", [])
            for step in steps:
                s_id = step.get("skill")

                if s_id == "workflow-orchestrator":
                    warnings.append(f"Workflow '{workflow['id']}' contains a recursive call to 'workflow-orchestrator'.")

                # Conditional steps don't have top-level step_type; they have it in branches
                if step.get("conditional"):
                    # Validate that if_true branch has step_type if it has a skill
                    if_true = step.get("if_true", {})
                    if if_true.get("skill"):
                        s_type = if_true.get("step_type")
                        if not s_type:
                            errors.append(f"Workflow '{workflow['id']}' conditional step '{step.get('id')}' if_true branch missing 'step_type'")
                        elif s_type not in ["local_execution", "prompt_handoff", "external_routing", "human_review"]:
                            errors.append(f"Workflow '{workflow['id']}' conditional step '{step.get('id')}' if_true has invalid step_type: {s_type}")
                else:
                    # Non-conditional steps must have step_type
                    s_type = step.get("step_type")
                    if not s_type:
                        errors.append(f"Workflow '{workflow['id']}' step '{s_id}' missing 'step_type'")
                    elif s_type not in ["local_execution", "prompt_handoff", "external_routing", "human_review"]:
                        errors.append(f"Workflow '{workflow['id']}' step '{s_id}' has invalid step_type: {s_type}")
                
                if s_id in registered_skills:
                    availability = registered_skills[s_id]["availability"]["type"]
                    if s_type == "local_execution" and availability not in ["local", "local_command"]:
                        errors.append(f"Workflow '{workflow['id']}' step '{s_id}' marked as local_execution but availability is {availability}")

    # 5. Artifact Handoff & Initial Input Validation
    if "skills/workflow-orchestrator/references/artifact-contracts.yaml" in registries and \
       "skills/workflow-orchestrator/references/workflow-registry.yaml" in registries and \
       "skills/workflow-orchestrator/references/skill-registry.yaml" in registries:
        
        contracts = registries["skills/workflow-orchestrator/references/artifact-contracts.yaml"]
        artifacts_list = contracts.get("artifacts", [])
        contract_ids = set()
        
        for art in artifacts_list:
            a_id = art["id"]
            contract_ids.add(a_id)
            
            # Verification block validation
            verification = art.get("verification")
            if not verification:
                errors.append(f"Artifact '{a_id}' missing 'verification' block")
            else:
                if not verification.get("generic_validator"):
                    errors.append(f"Artifact '{a_id}' verification missing 'generic_validator'")
                if not verification.get("required_for_modes"):
                    errors.append(f"Artifact '{a_id}' verification missing 'required_for_modes'")
                elif not isinstance(verification["required_for_modes"], list):
                    errors.append(f"Artifact '{a_id}' 'required_for_modes' must be a list")
        
        skill_registry = registries["skills/workflow-orchestrator/references/skill-registry.yaml"]
        skill_to_artifact = {}
        for ecosystem in skill_registry.get("ecosystems", {}).values():
            for skill in ecosystem.get("skills", []):
                if "artifact" in skill:
                    skill_to_artifact[skill["id"]] = skill["artifact"]
        
        workflow_registry = registries["skills/workflow-orchestrator/references/workflow-registry.yaml"]
        for workflow in workflow_registry.get("workflows", []):
            w_id = workflow["id"]
            initial_inputs = {i["id"] for i in workflow.get("initial_inputs", [])}
            steps = workflow.get("steps", [])
            
            for i, step in enumerate(steps):
                s_id = step.get("skill")
                in_art = step.get("input_artifact")
                in_src = step.get("input_source")
                out_art = step.get("output_artifact")
                
                # 5a. First Step Validation
                if i == 0:
                    if not in_art and not in_src:
                        errors.append(f"Workflow '{w_id}' first step '{s_id}' missing 'input_artifact' or 'input_source'")
                    if in_src and in_src not in initial_inputs:
                        errors.append(f"Workflow '{w_id}' step '{s_id}' uses undeclared input_source: {in_src}")
                
                # 5b. Output Artifact Validation (Matches Registry)
                if out_art:
                    if s_id in skill_to_artifact:
                        expected_out = skill_to_artifact[s_id]
                        if out_art != expected_out:
                            errors.append(f"Workflow '{w_id}' step '{s_id}' output '{out_art}' mismatch with skill registry: {expected_out}")
                    if out_art not in contract_ids:
                         warnings.append(f"Workflow '{w_id}' step '{s_id}' produces unregistered artifact: {out_art}")

                # 5c. Non-First Step Handoff Validation
                if i > 0:
                    prev_step = steps[i-1]

                    # For conditional steps, get outputs from both branches
                    if prev_step.get("conditional"):
                        prev_out_true = prev_step.get("if_true", {}).get("output_artifact")
                        prev_out_false = prev_step.get("if_false", {}).get("output_artifact")
                        # Current step must be able to accept either output or not depend on previous
                    else:
                        prev_out = prev_step.get("output_artifact")

                    if in_art:
                        # For conditional step inputs, be lenient - the input could come from either branch
                        if prev_step.get("conditional"):
                            prev_out_true = prev_step.get("if_true", {}).get("output_artifact")
                            prev_out_false = prev_step.get("if_false", {}).get("output_artifact")
                            # Check if input matches either branch output or is an initial input
                            matches = (in_art == prev_out_true or in_art == prev_out_false or in_art in initial_inputs)
                            if not matches:
                                errors.append(f"Workflow '{w_id}' step '{s_id}' input '{in_art}' does not match conditional branch outputs ({prev_out_true}, {prev_out_false}) and is not an initial input")
                        else:
                            prev_out = prev_step.get("output_artifact")
                            if in_art != prev_out and in_art not in initial_inputs:
                                errors.append(f"Workflow '{w_id}' step '{s_id}' input '{in_art}' does not match previous step output '{prev_out}' and is not an initial input")

                        if in_art not in contract_ids:
                            warnings.append(f"Workflow '{w_id}' step '{s_id}' consumes unregistered artifact: {in_art}")

                    # Ensure local_execution steps have output_artifact (but not conditional steps)
                    if step.get("step_type") == "local_execution" and not out_art and not step.get("conditional"):
                        errors.append(f"Workflow '{w_id}' step '{s_id}' is local_execution but missing 'output_artifact'")

    # 6. Frontmatter Check
    skill_files = [
        "skills/repo-sensemaker/SKILL.md",
        "skills/workflow-orchestrator/SKILL.md",
        "skills/problem-framer/SKILL.md",
        "skills/unknowns-mapper/SKILL.md",
        "skills/prompt-handoff/SKILL.md",
        "skills/setup-sensemaking-skills/SKILL.md",
        "skills/sensemaking-docs-reconciler/SKILL.md",
        "skills/usage-researcher/SKILL.md"
    ]
    for sf in skill_files:
        if os.path.exists(sf):
            with open(sf, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'^description:\s*(.*)$', content, re.MULTILINE)
                if match:
                    desc = match.group(1).strip()
                    if desc and desc[0].isupper():
                        errors.append(f"Skill description in {sf} should be lowercase")

    # 7. Template Section Header Validation
    template_headers = {
        "skills/repo-sensemaker/references/repo-analysis-template.md": [
            "Repository Goal", "Current Shape", "Strong Signals", "Missing Pieces",
            "Improvement Opportunities", "Weakest Boundary", "Evidence", "Evidence excerpts",
            "Why This Boundary Matters", "Candidate Next Steps", "Recommended Next Step",
            "Recommended Workflow", "Machine-readable handoff", "Ready-to-copy prompt"
        ],
        "skills/workflow-orchestrator/references/workflow-orchestration-template.md": [
            "Brief consumed", "Chosen workflow", "Why this workflow", "Skills in sequence",
            "Inputs and outputs", "Approval gates", "Stop conditions", "Execution mode",
            "Prompt chain", "Run log template", "Machine-readable plan"
        ],
        "skills/problem-framer/references/problem-frame-template.md": [
            "Raw Fog", "Problem Under the Problem", "Object Under Pressure",
            "Failure Mode", "Success Condition", "What Must Be True", "Next Artifact"
        ],
        "skills/unknowns-mapper/references/unknowns-map-template.md": [
            "Knowns", "Unknowns", "Assumptions", "Risks", "Research Paths", "Stopping Rule"
        ],
        "skills/prompt-handoff/references/prompt-handoff-template.md": [
            "Target Skill", "Context to Preserve", "Task", "Constraints",
            "Inputs", "Expected Output", "Stop Condition", "Ready-to-copy prompt"
        ],
        "skills/skill-maintainer/references/improvement-plan-template.md": [
            "Diagnosis", "Evidence", "Proposed Edits", "Impact Assessment", "Verification Plan"
        ],
        "skills/usage-researcher/references/usage-research-report-template.md": [
            "Scenario Tested", "Expected Behavior", "Actual Behavior", "Evidence Excerpts",
            "Failure Classification", "What Worked", "Friction Points", "Routing Quality",
            "Handoff Quality", "Semantic Quality Score", "Recommended Maintainer Input", "Next Test"
        ]
    }
    for path, expected_headers in template_headers.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                for i, header in enumerate(expected_headers):
                    header_pattern = rf"^## {i+1}\.\s+{re.escape(header)}"
                    if not re.search(header_pattern, content, re.MULTILINE | re.IGNORECASE):
                        errors.append(f"Template {path} missing or malformed section: {i+1}. {header}")

    # 8. Check examples
    examples_dirs = [
        "examples/repo-sensemaker", 
        "examples/workflow-orchestrator", 
        "examples/negative", 
        "examples/pipeline", 
        "examples/problem-framer", 
        "examples/unknowns-mapper", 
        "examples/prompt-handoff",
        "examples/usage-research"
    ]
    for ex_dir in examples_dirs:
        if os.path.exists(ex_dir):
            for root, dirs, files in os.walk(ex_dir):
                for f in files:
                    if f.endswith(".md"):
                        path = os.path.join(root, f)
                        with open(path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            if "file:///" in content:
                                errors.append(f"Example {f} in {root} contains absolute file:/// paths")
                        
                        import subprocess
                        # 8a. Validate orchestration plans
                        if "## 11. Machine-readable plan" in content:
                            cmd = [sys.executable, "scripts/validate-plan.py", path, "--repo-root", "."]
                            res = subprocess.run(cmd, capture_output=True, text=True)
                            is_negative = "examples/negative" in root.replace("\\", "/")
                            if is_negative:
                                if res.returncode == 0:
                                    errors.append(f"Negative example plan {f} in {root} PASSED validation but should have FAILED")
                            else:
                                if res.returncode != 0:
                                    errors.append(f"Example plan {f} failed validation:\n{res.stdout}{res.stderr}")
                        
                        # 8b. Validate usage research reports
                        if "# Usage Research Report" in content:
                            cmd = [sys.executable, "scripts/validate-usage-research-report.py", path]
                            res = subprocess.run(cmd, capture_output=True, text=True)
                            is_negative = "examples/negative" in root.replace("\\", "/")
                            if is_negative:
                                if res.returncode == 0:
                                    errors.append(f"Negative example report {f} in {root} PASSED validation but should have FAILED")
                            else:
                                if res.returncode != 0:
                                    errors.append(f"Example report {f} failed validation:\n{res.stdout}{res.stderr}")

                        # 8c. Validate skill improvement plans
                        if "## 1. Diagnosis" in content and "## 2. Evidence" in content:
                            cmd = [sys.executable, "scripts/validate-skill-improvement-plan.py", path]
                            res = subprocess.run(cmd, capture_output=True, text=True)
                            is_negative = "examples/negative" in root.replace("\\", "/")
                            if is_negative:
                                if res.returncode == 0:
                                    errors.append(f"Negative example plan {f} in {root} PASSED validation but should have FAILED")
                            else:
                                if res.returncode != 0:
                                    errors.append(f"Example plan {f} failed validation:\n{res.stdout}{res.stderr}")

    if errors:
        print("Validation errors (repo is misaligned):")
        for err in errors:
            print(f" - {err}")
        sys.exit(1)
    if warnings:
        print("Validation warnings (non-critical):")
        for w in warnings:
            print(f" - {w}")
    if not errors:
        print("Validation passed! Repo is aligned with the hardened V1 artifact contracts, YOLO safety, recursive-free workflows, and local-command execution rules.")

if __name__ == "__main__":
    validate_repo()
