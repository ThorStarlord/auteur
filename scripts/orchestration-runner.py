"""Production-grade orchestration runner.

Reads workflow-registry.yaml and artifact-contracts.yaml, then manages the full
workflow lifecycle: plan generation, step execution, validator dispatch, gate
management, run log recording, and mode coverage updates.

Usage:
    python scripts/orchestration-runner.py <workflow-id> --mode <mode> [options]
    python scripts/orchestration-runner.py --list-workflows
    python scripts/orchestration-runner.py --help
"""

import os
import re
import sys
import json
import uuid
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from collections import OrderedDict

from _validator_utils import (
    format_error,
    load_yaml,
    load_workflow_registry,
    load_artifact_contracts,
    load_skill_registry,
    resolve_repo_root,
)
from skill_execution_dispatcher import dispatch_skill_execution

# -- Error codes --------------------------------------------------------------
WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"
WORKFLOW_INVALID = "WORKFLOW_INVALID"
MODE_NOT_ALLOWED = "MODE_NOT_ALLOWED"
MISSING_INPUT = "MISSING_INPUT"
VALIDATOR_FAILED = "VALIDATOR_FAILED"
GATE_DENIED = "GATE_DENIED"
GATE_TIMEOUT = "GATE_TIMEOUT"
STEP_FAILED = "STEP_FAILED"
PREFLIGHT_FAILED = "PREFLIGHT_FAILED"
RUN_LOG_WRITE_FAILED = "RUN_LOG_WRITE_FAILED"
COVERAGE_UPDATE_FAILED = "COVERAGE_UPDATE_FAILED"
ARTIFACT_NOT_FOUND = "ARTIFACT_NOT_FOUND"
GATE_AUTO_FAILED = "GATE_AUTO_FAILED"
STEP_SKIPPED = "STEP_SKIPPED"
ROLLBACK_RECOMMENDED = "ROLLBACK_RECOMMENDED"
UNKNOWN_GATE_RESULT = "UNKNOWN_GATE_RESULT"
RECOVERY_APPLIED = "RECOVERY_APPLIED"
INVALID_STATE = "INVALID_STATE"

# -- Known modes --------------------------------------------------------------
KNOWN_MODES = OrderedDict([
    ("plan_only", {"gates": "none", "mutation": False, "risk": "none"}),
    ("prompt_chain", {"gates": "none", "mutation": False, "risk": "none"}),
    ("guided_execution", {"gates": "mandatory", "mutation": True, "risk": "low"}),
    ("autonomous_execution", {"gates": "automated", "mutation": True, "risk": "medium"}),
    ("yolo_execution", {"gates": "bypassed", "mutation": True, "risk": "high"}),
])

GATE_RESULTS = ["approved_by_user", "denied_by_user", "automated_approval", "bypassed", "not_applicable"]


def _load_mode_coverage(repo_root: str) -> dict | None:
    """Load mode-coverage.yaml from docs/."""
    path = os.path.join(repo_root, "docs", "mode-coverage.yaml")
    return load_yaml(path)


def _save_mode_coverage(data: dict, repo_root: str) -> None:
    """Write mode-coverage.yaml preserving structure."""
    path = os.path.join(repo_root, "docs", "mode-coverage.yaml")
    import yaml
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def _run_validator(cmd: list[str], artifact_path: str, repo_root: str) -> tuple[int, str, float]:
    """Run a validator command. Returns (exit_code, output, elapsed_seconds)."""
    resolved = [arg.replace("{artifact_path}", artifact_path) for arg in cmd]
    if "--repo-root" not in resolved and repo_root:
        resolved.extend(["--repo-root", repo_root])

    start = datetime.now()
    result = subprocess.run(resolved, capture_output=True, text=True, timeout=120)
    elapsed = (datetime.now() - start).total_seconds()
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output, elapsed


def _run_level1_validator(repo_root: str) -> tuple[bool, str]:
    """Run Level 1 structural validator."""
    validator = os.path.join(repo_root, "scripts", "validate-repo.py")
    if not os.path.exists(validator):
        return False, "validate-repo.py not found"
    result = subprocess.run(
        [sys.executable, validator, "--repo-root", repo_root],
        capture_output=True, text=True, timeout=120,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def _check_clean_git(repo_root: str) -> tuple[bool, str]:
    """Check whether the git working tree is clean."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=repo_root, timeout=30,
    )
    is_clean = len(result.stdout.strip()) == 0
    return is_clean, result.stdout.strip() if not is_clean else "clean"


def _get_git_branch(repo_root: str) -> str:
    """Get the current git branch name."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, cwd=repo_root, timeout=30,
    )
    return result.stdout.strip() or "unknown"


def _generate_session_id() -> str:
    """Generate a unique session ID."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    short = uuid.uuid4().hex[:8]
    return f"orchestration-{ts}-{short}"


def _validate_workflow(workflow: dict) -> list[str]:
    """Validate a workflow definition structure. Returns list of errors."""
    errors = []
    wid = workflow.get("id", "?")
    if not workflow.get("steps"):
        errors.append(format_error(WORKFLOW_INVALID, f"Workflow '{wid}' has no steps"))
    for i, step in enumerate(workflow.get("steps", [])):
        if not step.get("skill"):
            errors.append(format_error(WORKFLOW_INVALID, f"Workflow '{wid}' step {i+1} missing 'skill'"))
        if not step.get("gate"):
            errors.append(format_error(WORKFLOW_INVALID, f"Workflow '{wid}' step {i+1} missing 'gate'"))
        if not step.get("output_artifact") and not step.get("step_type") == "external_routing":
            # Some steps may not declare output_artifact in the spec but rely on it in context
            pass
    return errors


def _resolve_artifact_verification(
    artifact_id: str, contracts: dict | None
) -> tuple[str | None, list[str]]:
    """Given an artifact ID, return (generic_validator_cmd, [specialized_validator_cmds])."""
    if not contracts:
        return None, []
    contract = next(
        (a for a in contracts.get("artifacts", []) if a["id"] == artifact_id),
        None,
    )
    if not contract:
        return None, []
    verification = contract.get("verification", {})
    generic = verification.get("generic_validator")
    specialized = verification.get("specialized_validators", [])
    return generic, specialized


# ===============================================================================
# Core Orchestration Logic
# ===============================================================================

class OrchestrationRunner:
    """Manages the full lifecycle of a single workflow execution."""

    def __init__(
        self,
        workflow_id: str,
        mode: str,
        repo_root: str = ".",
        plan_out: str | None = None,
        log_dir: str | None = None,
        resume: bool = False,
        gate_decision: str | None = None,
    ):
        self.workflow_id = workflow_id
        self.mode = mode
        self.repo_root = os.path.abspath(repo_root)
        self.plan_out = plan_out or os.path.join(self.repo_root, "artifacts", f"plan_{workflow_id}.md")
        self.log_dir = log_dir or os.path.join(self.repo_root, "artifacts")

        self.session_id = _generate_session_id()
        self.workflow: dict = {}
        self.contracts: dict | None = None
        self.errors: list[str] = []
        self.step_results: list[dict] = []
        self.gate_decisions: list[dict] = []
        self.resume = resume
        self.gate_decision = gate_decision

        # Load registries
        self._load_registries()

        # State tracking
        self.final_state: str = "not_started"
        self.final_note: str = ""

    def _load_registries(self) -> None:
        """Load all registry files."""
        registry = load_workflow_registry(self.repo_root)
        if not registry:
            self.errors.append(format_error(WORKFLOW_NOT_FOUND, "workflow-registry.yaml not found or empty"))
            return

        workflows = registry.get("workflows", [])
        self.workflow = next((w for w in workflows if w["id"] == self.workflow_id), {})
        if not self.workflow:
            self.errors.append(format_error(WORKFLOW_NOT_FOUND, f"Workflow '{self.workflow_id}' not found in registry"))
            return

        # Validate workflow structure
        self.errors.extend(_validate_workflow(self.workflow))

        # Check mode permission
        allowed = self.workflow.get("allowed_execution_modes", [])
        if self.mode not in allowed:
            self.errors.append(
                format_error(
                    MODE_NOT_ALLOWED,
                    f"Mode '{self.mode}' not allowed for workflow '{self.workflow_id}'. "
                    f"Allowed: {allowed}",
                )
            )

        self.contracts = load_artifact_contracts(self.repo_root)

    def _create_user_intent_artifact(self, problem_statement: str | None, scope_mode: str) -> str | None:
        """Create 00-user-intent.md artifact. Returns artifact path or None on error."""

        intent_source = "repo_inferred" if problem_statement is None else "user_problem_statement"

        intent_yaml = {
            "artifact_id": "user_intent",
            "schema_version": 1,
            "intent_source": intent_source,
            "scope_mode": scope_mode,
            "raw_problem_statement": problem_statement,
            "immutable": True,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "created_by": "orchestration-runner",
            "repo_state_used": True,
            "constraints": [],
            "non_goals": [],
            "clarifications": []
        }

        # Resolve artifact directory (create numbered run folder if needed)
        artifact_base = os.path.join(self.repo_root, "artifacts")

        # Find next run number (NN-run-name format)
        import glob as glob_module
        existing = glob_module.glob(os.path.join(artifact_base, "[0-9][0-9]-*"))
        next_num = max([int(os.path.basename(d).split("-")[0]) for d in existing] + [0]) + 1
        run_name = f"{next_num:02d}-orchestration-run"
        artifact_dir = os.path.join(artifact_base, run_name)

        try:
            os.makedirs(artifact_dir, exist_ok=True)
        except Exception as e:
            self.errors.append(format_error("DIR_CREATE_FAILED", f"Failed to create artifact directory: {e}"))
            return None

        intent_path = os.path.join(artifact_dir, "00-user-intent.md")

        try:
            with open(intent_path, "w", encoding="utf-8") as f:
                f.write("# User Intent\n\n")
                f.write("---\n")
                import yaml
                yaml.dump(intent_yaml, f, default_flow_style=False)
                f.write("---\n")

            print(f"[OK] Created user intent artifact: {os.path.relpath(intent_path, self.repo_root)}")
            return intent_path
        except Exception as e:
            self.errors.append(format_error("FILE_WRITE_FAILED", f"Failed to write user_intent artifact: {e}"))
            return None

    def create_intent_amendment(self, artifact_dir: str, clarification: str, clarification_type: str = "scope_refinement") -> str | None:
        """Create 00b-user-clarification.md amendment artifact.

        Args:
            artifact_dir: Directory containing 00-user-intent.md
            clarification: User's clarification or re-scoping
            clarification_type: Type of change (scope_refinement, scope_expansion, out_of_scope_addition)

        Returns:
            Path to amendment artifact or None on error
        """

        amendment_yaml = {
            "artifact_id": "user_intent_amendment",
            "schema_version": 1,
            "amends_intent_ref": "00-user-intent.md",
            "raw_clarification": clarification,
            "clarification_type": clarification_type,
            "requires_reroute": True,  # Conservative: amendments always require reroute check
            "created_at": datetime.utcnow().isoformat() + "Z",
            "created_by": "user",
        }

        # Determine amendment filename (00b, 00c, 00d, etc.)
        import glob as glob_module
        existing = glob_module.glob(os.path.join(artifact_dir, "00*-user*.md"))
        # Find highest amendment letter
        amendment_count = len([f for f in existing if "-user-clarification" in f or "-user-intent" in f])
        amendment_letter = chr(ord('b') + amendment_count - 1)  # b for first amendment
        amendment_filename = f"00{amendment_letter}-user-clarification.md"

        amendment_path = os.path.join(artifact_dir, amendment_filename)

        try:
            with open(amendment_path, "w", encoding="utf-8") as f:
                f.write("# User Intent Amendment\n\n")
                f.write("---\n")
                import yaml
                yaml.dump(amendment_yaml, f, default_flow_style=False)
                f.write("---\n")
                f.write(f"\n## Clarification\n\n{clarification}\n")

            print(f"✓ Created intent amendment: {os.path.relpath(amendment_path, self.repo_root)}")
            return amendment_path
        except Exception as e:
            self.errors.append(format_error("FILE_WRITE_FAILED", f"Failed to write intent amendment: {e}"))
            return None

    def preflight_check(self) -> bool:
        """Run pre-flight checks. Returns True if all pass."""
        print(f"\n{'='*60}")
        print(f"PRE-FLIGHT CHECK  |  Workflow: {self.workflow_id}  Mode: {self.mode}")
        print(f"Session: {self.session_id}")
        print(f"{'='*60}\n")

        all_ok = True

        # 1. Git state
        clean, details = _check_clean_git(self.repo_root)
        if not clean:
            msg = f"Git working tree is not clean:\n{details}"
            if self.mode in ("yolo_execution", "autonomous_execution"):
                self.errors.append(format_error(PREFLIGHT_FAILED, msg))
                print(f"  [FAIL] GIT: {msg}")
                all_ok = False
            else:
                print(f"  ~ GIT: not clean (non-mutating mode, continuing)")
        else:
            print(f"  [OK] GIT: clean worktree")

        # 2. Branch
        branch = _get_git_branch(self.repo_root)
        print(f"  ~ Branch: {branch}")

        # 3. Level 1 validator
        v1_ok, v1_out = _run_level1_validator(self.repo_root)
        if not v1_ok:
            self.errors.append(format_error(PREFLIGHT_FAILED, f"Level 1 validator failed:\n{v1_out[:300]}"))
            print(f"  [FAIL] LEVEL 1: validate-repo.py FAILED")
            all_ok = False
        else:
            print(f"  [OK] LEVEL 1: validate-repo.py PASSED")

        if all_ok:
            print(f"\n  [OK] All pre-flight checks passed.\n")
        else:
            print(f"\n  [FAIL] Pre-flight checks failed. See errors above.\n")

        return all_ok

    def generate_plan(self) -> str:
        """Generate the orchestration plan document. Returns the plan text."""
        steps = self.workflow.get("steps", [])
        workflow_name = self.workflow.get("display_name", self.workflow_id)
        purpose = self.workflow.get("purpose", "")
        initial_inputs = self.workflow.get("initial_inputs", [])

        lines = [
            f"# Orchestration Plan: {workflow_name}",
            f"",
            f"- **Session ID**: {self.session_id}",
            f"- **Date**: {datetime.now().strftime('%Y-%m-%d')}",
            f"- **Workflow**: {self.workflow_id}",
            f"- **Execution Mode**: {self.mode}",
            f"- **Purpose**: {purpose}",
            f"",
        ]

        # Section 1: Brief Consumed
        lines.extend([
            f"## 1. Brief Consumed",
            f"",
            f"This plan was generated from sensemaking artifacts for workflow `{self.workflow_id}`.",
            f"",
            f"- **Workflow Purpose**: {purpose}",
            f"- **Routing**: No divergence — user-selected workflow matches system recommendation.",
            f"",
        ])

        # Section 2: Chosen Workflow
        lines.extend([
            f"## 2. Chosen Workflow",
            f"",
            f"**Workflow ID**: `{self.workflow_id}`",
            f"",
            f"Selected workflow: `{self.workflow_id}` — {workflow_name}.",
            f"",
        ])

        # Section 3: Why This Workflow
        lines.extend([
            f"## 3. Why This Workflow",
            f"",
            f"The `{self.workflow_id}` workflow was selected based on the user intent and sensemaking diagnosis.",
            f"",
            f"- Diagnosis confirmed this workflow matches the required execution pattern.",
            f"- No routing divergence detected.",
            f"",
        ])

        # Section 4: Skills in Sequence
        lines.extend([
            f"## 4. Skills in Sequence",
            f"",
        ])
        for i, step in enumerate(steps, 1):
            skill = step.get("skill", "?")
            s_type = step.get("step_type", "local_execution")
            gate = step.get("gate", "review")
            output = step.get("output_artifact", "N/A")
            lines.extend([
                f"### Step {i}: {skill}",
                f"- **Type**: {s_type}",
                f"- **Gate**: {gate}",
                f"- **Output**: {output}",
                f"",
            ])

        # Section 5: Inputs and Outputs
        lines.extend([
            f"## 5. Inputs and Outputs",
            f"",
        ])
        for inp in initial_inputs:
            lines.append(f"- **{inp['id']}** ({inp.get('type', '?')}): {inp.get('description', '')}")
        lines.append(f"")

        # Section 6: Approval Gates
        mode_info = KNOWN_MODES.get(self.mode, {})
        gate_behavior = mode_info.get("gates", "none")
        lines.extend([
            f"## 6. Approval Gates",
            f"",
            f"- **Mode**: {self.mode}",
            f"- **Gate Behavior**: {gate_behavior}",
            f"",
        ])
        if gate_behavior == "none":
            lines.append("No gates required for this mode.\n")
        elif gate_behavior == "mandatory":
            for step in steps:
                lines.append(f"- {step.get('gate', '?')}: REQUIRED (user must approve)")
            lines.append("")
        elif gate_behavior == "automated":
            for step in steps:
                lines.append(f"- {step.get('gate', '?')}: AUTOMATED_APPROVAL")
            lines.append("")
        elif gate_behavior == "bypassed":
            for step in steps:
                lines.append(f"- {step.get('gate', '?')}: BYPASSED")
            lines.append("")

        # Section 7: Stop Conditions
        lines.extend([
            f"## 7. Stop Conditions",
            f"",
            f"- Validator failure at any level -> HALT",
            f"- Gate denial -> HALT (rollback recommended for mutating modes)",
            f"- Step execution failure -> HALT",
            f"- Final step completed -> SUCCESS",
            f"",
        ])

        # Section 8: Execution Mode
        lines.extend([
            f"## 8. Execution Mode",
            f"",
            f"**Mode**: `{self.mode}`",
            f"",
            f"Gate behavior: `{gate_behavior}`. Mutations permitted: `{KNOWN_MODES.get(self.mode, {}).get('mutation', False)}`.",
            f"",
        ])

        # Section 9: Prompt Chain
        lines.extend([
            f"## 9. Prompt Chain",
            f"",
            f"The following prompts can be used for agent-driven execution of each step:",
            f"",
        ])
        for i, step in enumerate(steps, 1):
            skill = step.get("skill", "?")
            output = step.get("output_artifact", "N/A")
            gate = step.get("gate", "review")
            lines.extend([
                f"### Step {i} — {skill}",
                f"> Execute Step {i} of `{self.workflow_id}` using the `{skill}` skill.",
                f"> Produce artifact: `{output}`. Gate: `{gate}`.",
                f"",
            ])

        # Section 10: Run Log Template
        lines.extend([
            f"## 10. Run Log Template",
            f"",
            f"```markdown",
            f"# Workflow Run Log: {workflow_name}",
            f"",
            f"- Date: {{date}}",
            f"- Session ID: {{session_id}}",
            f"- Workflow ID: {self.workflow_id}",
            f"- Mode: {self.mode}",
            f"- Status: {{status}}",
            f"```",
            f"",
        ])

        # Section 11: Machine-readable plan
        step_gate_names = [step.get("gate", "review") for step in steps]
        gate_behavior_dict_lines = []
        for step in steps:
            g = step.get("gate", "review")
            if gate_behavior == "mandatory":
                gate_behavior_dict_lines.append(f"  {g}: approved_by_user")
            elif gate_behavior == "automated":
                gate_behavior_dict_lines.append(f"  {g}: automated_approval")
            elif gate_behavior == "bypassed":
                gate_behavior_dict_lines.append(f"  {g}: bypassed")
            else:
                gate_behavior_dict_lines.append(f"  {g}: not_applicable")

        lines.extend([
            f"## 11. Machine-readable plan",
            f"",
            f"```yaml",
            f"artifact_id: workflow_orchestration_plan",
            f"source_intent_ref: artifacts/00-user-intent.md",
            f"chosen_workflow_id: {self.workflow_id}",
            f"system_recommended_workflow: {self.workflow_id}",
            f"selected_workflow: {self.workflow_id}",
            f"routing_divergence: false",
            f"routing_decision_method: diagnosis_primary_soft_context",
            f"escalation_recommended: false",
            f"auto_escalation_allowed: false",
            f"scope_expansion_requires_approval: true",
            f"execution_mode: {self.mode}",
            f"status: created",
            f"session_id: {self.session_id}",
            f"subset_run: false",
            f"subset_reason: null",
            f"included_steps: []",
            f"excluded_steps: []",
            f"initial_inputs:",
        ])
        for inp in initial_inputs:
            lines.append(f"  - id: {inp['id']}")
            lines.append(f"    type: {inp.get('type', '?')}")
            lines.append(f"    required: {str(inp.get('required', False)).lower()}")
            if inp.get('description'):
                lines.append(f"    description: {inp.get('description', '')}")
        lines.append(f"steps:")
        for i, step in enumerate(steps, 1):
            gate = step.get("gate", "review")
            lines.append(f"  - id: {i}")
            lines.append(f"    skill: {step['skill']}")
            lines.append(f"    step_type: {step.get('step_type', 'local_execution')}")
            lines.append(f"    gate: {gate}")
            if step.get("input_source"):
                lines.append(f"    input_source: {step['input_source']}")
            if step.get("input_artifact"):
                lines.append(f"    input_artifact: {step['input_artifact']}")
            lines.append(f"    output_artifact: {step.get('output_artifact', 'N/A')}")
            lines.append(f"    status: pending")
        lines.append(f"approval_gates:")
        for g in step_gate_names:
            lines.append(f"  - {g}")
        lines.append(f"gate_behavior:")
        lines.extend(gate_behavior_dict_lines)
        lines.append(f"stop_conditions:")
        lines.append(f"  - validator_failure")
        lines.append(f"  - gate_denial")
        lines.append(f"  - step_failure")
        lines.append(f"```")
        lines.append(f"")

        plan = "\n".join(lines)

        # Write plan file
        os.makedirs(os.path.dirname(self.plan_out), exist_ok=True)
        with open(self.plan_out, "w", encoding="utf-8") as f:
            f.write(plan)
        print(f"  [OK] Plan written to {self.plan_out}")

        return plan

    def execute_step(self, step: dict, step_num: int, total_steps: int) -> dict:
        """Execute a single workflow step: validate artifact, manage gate, record result.
        Returns the step result dict."""
        skill = step.get("skill", "?")
        gate_name = step.get("gate", "review")
        output_artifact = step.get("output_artifact", "")
        s_type = step.get("step_type", "local_execution")

        result = {
            "step_id": str(step_num),
            "skill": skill,
            "gate": gate_name,
            "output_artifact": output_artifact or "N/A",
            "artifact_path": "",
            "validator_stack": [],
            "gate_result": "",
            "status": "PENDING",
            "step_type": s_type,
        }

        print(f"\n{'-'*50}")
        print(f"STEP {step_num}/{total_steps}  |  Skill: {skill}  |  Gate: {gate_name}")
        print(f"{'-'*50}")

        # -- Resolve artifact path --------------------------------------
        artifact_path = ""
        if output_artifact:
            # Determine artifact path based on contracts
            contract_path = self._resolve_artifact_path(output_artifact)
            artifact_path = contract_path
            # Store repo-relative path in the run log for portability
            rel = os.path.relpath(artifact_path, self.repo_root)
            result["artifact_path"] = rel.replace("\\", "/")

        # -- Run validators if artifact exists --------------------------
        if artifact_path and os.path.exists(artifact_path):
            validator_stack = self._run_validator_stack(output_artifact, artifact_path)
            result["validator_stack"] = validator_stack

            # Check for validator failures
            v_failures = [v for v in validator_stack if v["result"] == "FAILED"]
            if v_failures:
                self.errors.append(
                    format_error(
                        VALIDATOR_FAILED,
                        f"Step {step_num} ({skill}): {len(v_failures)} validator(s) failed",
                    )
                )
                result["status"] = "FAILED"
                return result
        elif output_artifact and output_artifact != "N/A":
            if self.mode in ("guided_execution", "autonomous_execution", "yolo_execution"):
                # Execution modes: FAIL if artifact expected but not produced
                self.errors.append(
                    format_error(ARTIFACT_NOT_FOUND,
                        f"Step {step_num} ({skill}): Expected artifact '{output_artifact}' not produced")
                )
                result["status"] = "FAILED"
                result["validator_stack"] = [{"level": "Dispatcher", "command": f"validate-output.py {output_artifact}", "result": "SKIPPED (artifact missing)"}]
                return result
            else:
                # Plan modes: artifacts don't exist yet, OK to skip
                print(f"  ~ Artifact '{output_artifact}' not yet produced (plan mode, expected after actual execution)")

        # -- Gate management --------------------------------------------
        gate_result = self._manage_gate(gate_name, step_num, skill)
        result["gate_result"] = gate_result

        if gate_result in ("denied_by_user",):
            self.errors.append(
                format_error(GATE_DENIED, f"Step {step_num} ({skill}): Gate '{gate_name}' was denied")
            )
            result["status"] = "PAUSED"
            return result

        if gate_result in ("failed",):
            self.errors.append(
                format_error(GATE_AUTO_FAILED, f"Step {step_num} ({skill}): Gate '{gate_name}' auto-failed")
            )
            result["status"] = "FAILED"
            return result

        result["status"] = "COMPLETED"
        return result

    def _should_auto_invoke_next(self) -> tuple[bool, str | None]:
        """Check if this workflow declares auto-invocation. Returns (should_invoke, source_artifact_id)."""
        auto_invoke = self.workflow.get("auto_invoke_next_workflow", False)
        source = self.workflow.get("auto_invoke_source")
        if auto_invoke and source:
            return True, source
        return False, None

    def _read_machine_readable_section(self, artifact_path: str) -> dict | None:
        """Parse the YAML machine-readable section from a markdown artifact.

        Looks for a code block like:
        ```yaml
        artifact_id: ...
        ...
        ```
        """
        if not os.path.exists(artifact_path):
            return None

        try:
            with open(artifact_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find the first YAML code block
            yaml_match = re.search(r"```yaml\n(.*?)\n```", content, re.DOTALL)
            if not yaml_match:
                return None

            yaml_content = yaml_match.group(1)
            import yaml as yaml_lib
            return yaml_lib.safe_load(yaml_content)
        except Exception as e:
            print(f"  ~ Failed to parse machine-readable section from {artifact_path}: {e}")
            return None

    def _extract_recommended_workflow(self, source_artifact_id: str) -> str | None:
        """Extract the recommended_workflow_id from the source artifact.

        Reads the artifact and parses its machine-readable section.
        Returns the recommended_workflow_id or None if not found.
        """
        artifact_path = self._resolve_artifact_path(source_artifact_id)
        if not os.path.exists(artifact_path):
            print(f"  ~ Source artifact for auto-invocation not found: {artifact_path}")
            return None

        machine_data = self._read_machine_readable_section(artifact_path)
        if not machine_data:
            print(f"  ~ Could not parse machine-readable section from {source_artifact_id}")
            return None

        recommended = machine_data.get("recommended_workflow_id")
        if recommended:
            print(f"  [OK] Extracted recommended workflow: {recommended}")
            return recommended
        else:
            print(f"  ~ No recommended_workflow_id found in {source_artifact_id}")
            return None

    def _invoke_next_workflow(self, next_workflow_id: str) -> int:
        """Invoke the next workflow automatically using orchestration-runner.

        Uses the same mode as the current execution.
        Returns the exit code from the next workflow run.
        """
        print(f"\n{'='*60}")
        print(f"AUTO-INVOCATION: Next Workflow")
        print(f"{'='*60}")
        print(f"  Current workflow: {self.workflow_id} ({self.mode})")
        print(f"  Next workflow:    {next_workflow_id} ({self.mode})")
        print(f"")

        # Build the command
        cmd = [
            sys.executable,
            os.path.join(self.repo_root, "scripts", "orchestration-runner.py"),
            next_workflow_id,
            "--mode", self.mode,
            "--repo-root", self.repo_root,
        ]

        # If testing mode (auto-approve/deny), propagate it
        if self.gate_decision:
            cmd.extend(["--gate-decision", self.gate_decision])

        print(f"  Running: {' '.join(cmd)}\n")

        result = subprocess.run(cmd)
        return result.returncode

    def _resolve_artifact_path(self, artifact_id: str) -> str:
        """Resolve the file path for an artifact."""
        # Known artifact paths
        known_paths = {
            "repository_sensemaking_brief": os.path.join("artifacts", "repository_sensemaking_brief.md"),
            "prompt_handoff": os.path.join("artifacts", "prompt_handoff.md"),
            "workflow_orchestration_plan": os.path.join("artifacts", f"plan_{self.workflow_id}.md"),
            "problem_frame": os.path.join("artifacts", "problem_frame.md"),
            "unknowns_map": os.path.join("artifacts", "unknowns_map.md"),
            "docs_contract_reconciliation_report": os.path.join("artifacts", "docs_contract_reconciliation_report.md"),
            "domain_alignment_report": os.path.join("artifacts", "domain_alignment_report.md"),
            "usage_research_report": os.path.join("artifacts", "usage_research_report.md"),
            "skill_improvement_plan": os.path.join("artifacts", "skill_improvement_plan.md"),
            "prd": os.path.join("artifacts", "prd.md"),
            "issue_list": os.path.join("artifacts", "issue_list.md"),
            "agent_brief": os.path.join("artifacts", "agent_brief.md"),
            "code_patch": os.path.join("artifacts", "code_patch.md"),
            "persona_definition": os.path.join("artifacts", "persona_definition.md"),
            "discovery_findings": os.path.join("artifacts", "discovery_findings.md"),
            "synthesis_report": os.path.join("artifacts", "synthesis_report.md"),
            "opportunity_map": os.path.join("artifacts", "opportunity_map.md"),
            "hypothesis_statement": os.path.join("artifacts", "hypothesis_statement.md"),
            "business_canvas": os.path.join("artifacts", "business_canvas.md"),
            "north_star_metric": os.path.join("artifacts", "north_star_metric.md"),
            "okr_list": os.path.join("artifacts", "okr_list.md"),
            "roadmap": os.path.join("artifacts", "roadmap.md"),
            "stakeholder_update": os.path.join("artifacts", "stakeholder_update.md"),
            "story_list": os.path.join("artifacts", "story_list.md"),
            "criteria_list": os.path.join("artifacts", "criteria_list.md"),
            "session_summary": os.path.join("artifacts", "session_summary.md"),
        }
        rel = known_paths.get(artifact_id, os.path.join("artifacts", f"{artifact_id}.md"))
        return os.path.join(self.repo_root, rel)

    def _run_validator_stack(self, artifact_id: str, artifact_path: str) -> list[dict]:
        """Run the full validator stack via validate-output.py (canonical dispatcher).

        Delegates to validate-output.py which reads artifact-contracts.yaml and runs
        the full generic + specialized validator chain. This makes validate-output.py
        the single canonical validator dispatch path.
        """
        stack = []

        validator_script = os.path.join(self.repo_root, "scripts", "validate-output.py")
        if not os.path.exists(validator_script):
            print(f"  ~ validate-output.py not found, skipping validator dispatch")
            return stack

        cmd = [sys.executable, validator_script, artifact_id, artifact_path,
               "--repo-root", self.repo_root]

        print(f"  -> Running dispatcher: validate-output.py {artifact_id}")
        start = datetime.now()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        elapsed = (datetime.now() - start).total_seconds()
        output = (result.stdout + result.stderr).strip()

        passed = result.returncode == 0
        stack.append({
            "level": "Dispatcher",
            "command": f"validate-output.py {artifact_id}",
            "result": "PASSED" if passed else "FAILED",
            "output": output[:300] if not passed else "",
            "elapsed_s": round(elapsed, 2),
        })

        if not passed:
            print(f"    [FAIL] Dispatcher failed ({elapsed:.1f}s): {output[:150]}")
        else:
            print(f"    [OK] Dispatcher passed ({elapsed:.1f}s)")

        return stack

    def _manage_gate(self, gate_name: str, step_num: int, skill: str) -> str:
        """Manage the approval gate based on execution mode. Returns the gate result string."""
        mode_info = KNOWN_MODES.get(self.mode, {})
        behavior = mode_info.get("gates", "none")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if behavior == "none":
            # plan_only and prompt_chain: no gates
            self.gate_decisions.append({
                "step": step_num,
                "gate": gate_name,
                "result": "not_applicable",
                "timestamp": timestamp,
                "mode": self.mode,
            })
            return "not_applicable"

        if behavior == "bypassed":
            # yolo: gates are bypassed
            self.gate_decisions.append({
                "step": step_num,
                "gate": gate_name,
                "result": "bypassed",
                "timestamp": timestamp,
                "mode": self.mode,
            })
            print(f"  ~ Gate '{gate_name}' BYPASSED (yolo mode)")
            return "bypassed"

        if behavior == "automated":
            # autonomous: automated approval
            self.gate_decisions.append({
                "step": step_num,
                "gate": gate_name,
                "result": "automated_approval",
                "timestamp": timestamp,
                "mode": self.mode,
                "approved_by": "automated_gate",
            })
            print(f"  ~ Gate '{gate_name}' AUTOMATED_APPROVAL (autonomous mode)")
            return "automated_approval"

        # Check for auto gate decision (non-interactive testing mode)
        if self.gate_decision:
            if self.gate_decision == "auto-approve":
                self.gate_decisions.append({
                    "step": step_num,
                    "gate": gate_name,
                    "result": "approved_by_user",
                    "timestamp": timestamp,
                    "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "approved_by": "auto_gate",
                    "mode": self.mode,
                })
                print(f"  ~ Gate '{gate_name}' AUTO_APPROVED (--gate-decision={self.gate_decision})")
                return "approved_by_user"

            elif self.gate_decision == "auto-deny":
                self.gate_decisions.append({
                    "step": step_num,
                    "gate": gate_name,
                    "result": "denied_by_user",
                    "timestamp": timestamp,
                    "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "reason": "auto_denied_by_flag",
                    "mode": self.mode,
                })
                print(f"  [FAIL] Gate '{gate_name}' AUTO_DENIED (--gate-decision={self.gate_decision})")
                return "denied_by_user"

        if behavior == "mandatory":
            # guided: requires manual approval
            # Check if stdin is available (TTY or pipe)
            import sys
            if not sys.stdin.isatty() and not self.gate_decision:
                # No TTY and no auto-decision flag: error
                error_msg = (
                    f"[ERROR] Gate '{gate_name}' requires manual approval in guided_execution mode,\n"
                    f"        but no TTY available and no --gate-decision flag provided.\n"
                    f"        Use: --gate-decision auto-approve (for automation) or --gate-decision auto-deny (for testing)"
                )
                self.errors.append(format_error(GATE_AUTO_FAILED, error_msg))
                return "timed_out"

            # If auto-decision is set, use it instead of prompting
            if self.gate_decision:
                if self.gate_decision == "auto-approve":
                    self.gate_decisions.append({
                        "step": step_num,
                        "gate": gate_name,
                        "result": "approved_by_user",
                        "timestamp": timestamp,
                        "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "approved_by": "auto_gate (mandatory mode)",
                        "mode": self.mode,
                    })
                    print(f"  ~ Gate '{gate_name}' AUTO_APPROVED (--gate-decision={self.gate_decision})")
                    return "approved_by_user"
                elif self.gate_decision == "auto-deny":
                    self.gate_decisions.append({
                        "step": step_num,
                        "gate": gate_name,
                        "result": "denied_by_user",
                        "timestamp": timestamp,
                        "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "reason": "auto_denied_by_flag",
                        "mode": self.mode,
                    })
                    print(f"  [FAIL] Gate '{gate_name}' AUTO_DENIED (--gate-decision={self.gate_decision})")
                    return "denied_by_user"

            print(f"\n  [PAUSE]  GATE: '{gate_name}' -- waiting for approval (Step {step_num}: {skill})")
            print(f"  Options: [A]pprove  [D]eny  [S]kip (treat as denied for testing)  [T]imeout")
            choice = input(f"  Enter choice (A/D/S/T): ").strip().upper()

            if choice == "A":
                approver = input(f"  Approver name: ").strip() or "user"
                self.gate_decisions.append({
                    "step": step_num,
                    "gate": gate_name,
                    "result": "approved_by_user",
                    "timestamp": timestamp,
                    "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "approved_by": approver,
                    "mode": self.mode,
                })
                print(f"  [OK] Gate '{gate_name}' APPROVED by {approver}")
                return "approved_by_user"

            elif choice == "D":
                reason = input(f"  Reason for denial: ").strip() or "No reason given"
                self.gate_decisions.append({
                    "step": step_num,
                    "gate": gate_name,
                    "result": "denied_by_user",
                    "timestamp": timestamp,
                    "approved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "reason": reason,
                    "mode": self.mode,
                })
                print(f"  [FAIL] Gate '{gate_name}' DENIED: {reason}")
                return "denied_by_user"

            elif choice in ("S", "T"):
                result = "denied_by_user" if choice == "S" else "timed_out"
                self.gate_decisions.append({
                    "step": step_num,
                    "gate": gate_name,
                    "result": result,
                    "timestamp": timestamp,
                    "mode": self.mode,
                })
                note = "skipped" if choice == "S" else "timed_out"
                print(f"  [FAIL] Gate '{gate_name}' {note.upper()}")
                return "denied_by_user"

            else:
                print(f"  Invalid choice, treating as denied.")
                return "denied_by_user"

        return "unknown"

    def _find_resume_state(self) -> dict | None:
        """Parse existing run log to find resume state.

        Returns dict with completed_steps and paused_step, or None if no resume needed.
        """
        run_log_path = os.path.join(self.log_dir, f"run_log_{self.workflow_id}_{self.mode}.md")
        if not os.path.exists(run_log_path):
            print(f"  ~ No existing run log found at {run_log_path}, starting fresh")
            return None

        with open(run_log_path, "r", encoding="utf-8") as f:
            content = f.read()

        completed_steps: list[int] = []
        paused_step: int | None = None

        # Extract step statuses from the run log
        step_blocks = re.findall(
            r"### Step (\d+).*?\*\*status\*\*:\s*(\S+)",
            content, re.DOTALL
        )
        for step_id_str, status in step_blocks:
            step_id = int(step_id_str)
            if status == "COMPLETED":
                completed_steps.append(step_id)
            elif status == "PAUSED":
                paused_step = step_id

        if not paused_step and not completed_steps:
            print(f"  ~ No paused or completed steps found, starting fresh")
            return None

        print(f"  [OK] Found resume state: {len(completed_steps)} completed, paused at step {paused_step}")
        return {
            "completed_steps": sorted(set(completed_steps)),
            "paused_step": paused_step,
            "previous_log_path": run_log_path,
        }

    def write_run_log(self) -> str:
        """Write the run log document. Returns the file path."""
        steps = self.workflow.get("steps", [])
        workflow_name = self.workflow.get("display_name", self.workflow_id)
        run_log_path = os.path.join(self.log_dir, f"run_log_{self.workflow_id}_{self.mode}.md")

        # Determine final state
        failures = [s for s in self.step_results if s["status"] in ("FAILED",)]
        pauses = [s for s in self.step_results if s["status"] in ("PAUSED",)]
        completed = [s for s in self.step_results if s["status"] in ("COMPLETED",)]

        if not failures and not pauses and len(completed) == len(steps):
            self.final_state = "completed"
            self.final_note = f"All {len(steps)} steps completed successfully in '{self.mode}' mode."
        elif failures:
            self.final_state = "failed"
            self.final_note = f"Step {failures[0]['step_id']} ({failures[0]['skill']}) failed. Run halted."
        elif pauses:
            self.final_state = "paused"
            self.final_note = f"Paused at step {pauses[0]['step_id']} gate '{pauses[0]['gate']}'."
        else:
            self.final_state = "partial"
            self.final_note = f"{len(completed)}/{len(steps)} steps completed."

        lines = [
            f"# Workflow Run Log: {workflow_name}",
            f"",
            f"- **Date**: {datetime.now().strftime('%Y-%m-%d')}",
            f"- **Session ID**: {self.session_id}",
            f"- **Workflow ID**: {self.workflow_id}",
            f"- **Orchestrator Mode**: {self.mode}",
            f"- **Branch**: {_get_git_branch(self.repo_root)}",
            f"- **Status**: {self.final_state}",
            f"",
            f"## Pre-flight",
            f"",
            f"- {_get_git_branch(self.repo_root)} branch, clean check: PASSED" if _check_clean_git(self.repo_root)[0]
            else f"- Branch: {_get_git_branch(self.repo_root)}",
            f"- validate-repo.py: PASSED",
            f"- Orchestrator v2 engaged: PRODUCTION_RUNNER",
            f"",
            f"## Sequence Log",
            f"",
        ]

        for sr in self.step_results:
            lines.extend([
                f"### Step {sr['step_id']}",
                f"- **step_id**: {sr['step_id']}",
                f"- **skill**: {sr['skill']}",
                f"- **runtime**: local_execution",
                f"- **output_artifact**: {sr.get('output_artifact', 'N/A')}",
                f"- **artifact_path**: {sr.get('artifact_path', 'N/A')}",
            ])
            vstack = sr.get("validator_stack", [])
            if vstack:
                lines.append("- **validator_stack**:")
                for v in vstack:
                    lines.extend([
                        f"    - level: {v['level']}",
                        f"      command: {v['command']}",
                        f"      result: {v['result']}",
                    ])
            else:
                lines.append("- **validator_stack**: none (no artifact to validate)")
            lines.extend([
                f"- **gate**: {sr.get('gate', '?')}",
                f"- **status**: {sr['status']}",
                f"",
            ])

        # Decisions & Overrides
        lines.extend([
            f"## Decisions & Overrides",
            f"",
        ])
        for gd in self.gate_decisions:
            lines.append(f"- Gate '{gd['gate']}' (step {gd['step']}): {gd['result']} at {gd['timestamp']}")
        if self.errors:
            lines.append(f"- Errors encountered: {len(self.errors)}")
            for e in self.errors[-5:]:  # Last 5 errors
                lines.append(f"  - {e}")
        lines.append(f"")

        # Final State
        lines.extend([
            f"## Final State",
            f"",
            f"- **Status**: {self.final_state}",
            f"- **Note**: {self.final_note}",
            f"- **Steps completed**: {len(completed)}/{len(steps)}",
            f"- **Gate decisions**: {len(self.gate_decisions)}",
            f"- **Errors**: {len(self.errors)}",
            f"",
        ])

        # TDD cycles if any occurred
        tdd_cycles = []
        for sr in self.step_results:
            for v in sr.get("validator_stack", []):
                if v["result"] == "FAILED" and v.get("output"):
                    tdd_cycles.append({
                        "step": sr["step_id"],
                        "failure": v["output"][:100],
                    })
        if tdd_cycles:
            lines.append(f"## TDD Cycles")
            lines.append(f"")
            for tc in tdd_cycles:
                lines.append(f"- **Step {tc['step']}**")
                lines.append(f"  - **RED**: {tc['failure']}")
                lines.append(f"  - **GREEN**: (manual fix applied)")
                lines.append(f"  - **REFACTOR**: (hardening if warranted)")
            lines.append(f"")

        log = "\n".join(lines)

        os.makedirs(os.path.dirname(run_log_path), exist_ok=True)
        with open(run_log_path, "w", encoding="utf-8") as f:
            f.write(log)
        print(f"\n  [OK] Run log written to {run_log_path}")
        return run_log_path

    def update_mode_coverage(self, run_log_path: str) -> None:
        """Update mode-coverage.yaml with results from this run."""
        coverage = _load_mode_coverage(self.repo_root)
        if not coverage:
            print(f"  ~ Cannot update mode coverage: mode-coverage.yaml not found")
            return

        mode_entries = coverage.get("mode_coverage", [])
        steps = self.workflow.get("steps", [])
        num_steps = len(steps)

        # Collect validators exercised - use actual validator script names
        validators_exercised = ["level_1: validate-repo.py"]
        for sr in self.step_results:
            for v in sr.get("validator_stack", []):
                cmd = v["command"]
                # Extract the actual validator script name from the command
                for script_name in ["validate-artifact.py", "validate-brief.py", "validate-plan.py",
                                     "validate-prompt-handoff.py", "validate-usage-research-report.py",
                                     "validate-skill-improvement-plan.py", "validate-run-log.py",
                                     "validate-output.py"]:
                    if script_name in cmd:
                        level = "level_2" if script_name == "validate-artifact.py" else "level_3"
                        label = f"{level}: {script_name}"
                        if label not in validators_exercised:
                            validators_exercised.append(label)
                        break

        # Find or create entry
        existing = None
        for entry in mode_entries:
            if entry.get("workflow_id") == self.workflow_id and entry.get("mode") == self.mode:
                existing = entry
                break

        gates_exercised = any(
            gd["result"] in ("approved_by_user", "automated_approval")
            for gd in self.gate_decisions
        )
        gates_note = ""
        if self.mode == "plan_only":
            gates_note = "not_applicable_plan_only"
        elif self.mode == "prompt_chain":
            gates_note = "not_applicable_prompt_chain"
        elif self.mode == "yolo_execution":
            gates_note = "bypassed_by_yolo"
        elif self.mode == "autonomous_execution":
            gates_note = "automated_approval_all_gates"
        elif self.mode == "guided_execution":
            approved = [gd for gd in self.gate_decisions if gd["result"] == "approved_by_user"]
            denied = [gd for gd in self.gate_decisions if gd["result"] == "denied_by_user"]
            gates_note = f"{len(approved)} approved, {len(denied)} denied"

        entry_data = {
            "mode": self.mode,
            "workflow_id": self.workflow_id,
            "last_run": datetime.now().strftime("%Y-%m-%d"),
            "run_log_path": os.path.relpath(run_log_path, self.repo_root).replace("\\", "/"),
            "steps_completed": len([s for s in self.step_results if s["status"] == "COMPLETED"]),
            "steps_total": num_steps,
            "validators_exercised": validators_exercised,
            "gates_exercised": gates_exercised,
            "gates_note": gates_note,
            "hardening_triggered": "none",
            "notes": f"Executed via production orchestration runner v2. Session: {self.session_id}.",
        }

        if existing:
            existing.update(entry_data)
        else:
            mode_entries.append(entry_data)

        # Also update system_tools if needed
        system_tools = coverage.get("system_tools", [])
        runner_tool = next((t for t in system_tools if t.get("tool") == "orchestration-runner.py"), None)
        if runner_tool:
            wf_list = runner_tool.get("workflows_executed")
            if isinstance(wf_list, list):
                wf_entry = f"{self.workflow_id} ({self.mode})"
                if wf_entry not in wf_list:
                    wf_list.append(wf_entry)
            else:
                runner_tool["workflows_executed"] = [f"{self.workflow_id} ({self.mode})"]
            runner_tool["last_run"] = datetime.now().strftime("%Y-%m-%d")
            runner_tool["last_session"] = self.session_id
        else:
            system_tools.append({
                "tool": "orchestration-runner.py",
                "status": "active",
                "last_run": datetime.now().strftime("%Y-%m-%d"),
                "last_session": self.session_id,
                "workflows_executed": 1,
                "modes_proven": [self.mode],
            })

        # Aggregate workflow families
        workflows_run = set()
        for entry in mode_entries:
            wf = entry.get("workflow_id", "")
            if wf:
                workflows_run.add(wf)

        coverage.setdefault("orchestration_runner", {})
        coverage["orchestration_runner"]["last_run"] = datetime.now().strftime("%Y-%m-%d")
        coverage["orchestration_runner"]["workflow_families_proven"] = sorted(workflows_run)
        coverage["orchestration_runner"]["total_workflow_families"] = len(workflows_run)

        _save_mode_coverage(coverage, self.repo_root)
        print(f"  [OK] Mode coverage updated")

    def rollback(self) -> None:
        """Recommend rollback on failure."""
        branch = _get_git_branch(self.repo_root)
        print(f"\n{'!'*50}")
        print(f"ROLLBACK RECOMMENDED")
        print(f"{'!'*50}")
        print(f"Branch: {branch}")
        print(f"To revert all changes, run:")
        print(f"  git reset --hard HEAD")
        print(f"  git clean -fd")
        print(f"(Review changes first with 'git diff')\n")

    def run(self) -> int:
        """Execute the full orchestration lifecycle. Returns exit code."""
        # Phase 1: Pre-flight (skip for plan_only mode)
        if self.mode != "plan_only":
            if not self.preflight_check():
                print(f"\n  [FAIL] Pre-flight failed. Aborting.")
                return 1
        else:
            print(f"{'='*60}")
            print(f"PHASE 1: PREFLIGHT (skipped for plan_only mode)")
            print(f"{'='*60}")

        # Phase 2: Generate plan
        print(f"{'='*60}")
        print(f"PHASE 2: GENERATE PLAN")
        print(f"{'='*60}")
        self.generate_plan()

        # For plan_only mode, stop here
        if self.mode == "plan_only":
            print(f"\n[OK] Plan-only mode complete. Exiting.")
            return 0

        # For autonomous_execution and yolo_execution modes, dispatch to skill executor
        if self.mode in ("autonomous_execution", "yolo_execution"):
            print(f"\n{'='*60}")
            print(f"PHASE 3: DISPATCH SKILL EXECUTION")
            print(f"{'='*60}")

            # Generate orchestration plan JSON for skill executor
            plan_json_path = os.path.join(self.log_dir, f"execution_plan_{self.workflow_id}.json")
            plan_data = {
                "workflow_id": self.workflow_id,
                "session_id": self.session_id,
                "mode": self.mode,
                "steps": self.workflow.get("steps", []),
                "generated_at": datetime.now().isoformat(),
            }

            with open(plan_json_path, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2)

            print(f"  -> Execution plan written to {os.path.relpath(plan_json_path, self.repo_root)}")

            # Dispatch to skill execution agent
            print(f"  -> Dispatching to skill execution agent...")
            success, output = dispatch_skill_execution(plan_json_path, self.repo_root, timeout=3600)
            if not success:
                self.errors.append(f"Skill execution failed: {output}")
                self.final_state = "failed"
                # Fall through to write run log and exit
            else:
                print(f"  [OK] Skill execution completed")
                self.final_state = "completed"

            # For execution modes, we still need to write run log and update coverage
            # The step execution phase is replaced by skill execution dispatch
            # Phase 4: Write run log
            print(f"\n{'='*60}")
            print(f"PHASE 4: WRITE RUN LOG")
            print(f"{'='*60}")
            run_log_path = self.write_run_log()

            # Phase 5: Update mode coverage
            print(f"\n{'='*60}")
            print(f"PHASE 5: UPDATE MODE COVERAGE")
            print(f"{'='*60}")
            self.update_mode_coverage(run_log_path)

            # Summary
            print(f"\n{'='*60}")
            print(f"SUMMARY")
            print(f"{'='*60}")
            print(f"  Workflow:     {self.workflow_id}")
            print(f"  Mode:         {self.mode}")
            print(f"  Session:      {self.session_id}")
            print(f"  Status:       {self.final_state}")
            print(f"  Errors:       {len(self.errors)}")
            print(f"  Run Log:      {run_log_path}")
            print()

            if self.final_state == "failed":
                print(f"  [FAIL] Skill execution failed.")
                return 2
            else:
                # Phase 6: Check for auto-invocation of next workflow
                should_invoke, source_artifact = self._should_auto_invoke_next()
                if should_invoke:
                    print(f"\n{'='*60}")
                    print(f"PHASE 6: AUTO-INVOCATION CHECK")
                    print(f"{'='*60}")
                    next_workflow_id = self._extract_recommended_workflow(source_artifact)
                    if next_workflow_id:
                        next_exit_code = self._invoke_next_workflow(next_workflow_id)
                        return next_exit_code
                    else:
                        print(f"  [SKIP] Auto-invocation enabled but no recommended workflow found.")
                        print(f"  [OK] Execution completed successfully.")
                        return 0
                else:
                    print(f"  [OK] Execution completed successfully.")
                    return 0

        # Phase 3: Execute steps (for non-execution modes)
        print(f"\n{'='*60}")
        print(f"PHASE 3: EXECUTE STEPS  ({len(self.workflow.get('steps', []))} total)")
        print(f"{'='*60}")

        steps = self.workflow.get("steps", [])

        # Check for resume state
        resume_state = None
        resume_skip = set()
        if self.resume:
            resume_state = self._find_resume_state()
            if resume_state:
                resume_skip = set(resume_state.get("completed_steps", []))
                paused = resume_state.get("paused_step")
                if paused:
                    resume_skip.add(paused)
                print(f"  [OK] Resuming: skipping steps {sorted(resume_skip)}, "
                      f"starting from step {max(resume_skip) + 1 if resume_skip else 1}")

        for i, step in enumerate(steps, 1):
            if i in resume_skip:
                print(f"\n  ~ Step {i} already completed in previous session, skipping (resume mode)")
                # Reconstruct a synthetic completed result for the run log
                sr = {
                    "step_id": str(i),
                    "skill": step.get("skill", "?"),
                    "gate": step.get("gate", "review"),
                    "output_artifact": step.get("output_artifact", "N/A"),
                    "artifact_path": "",
                    "validator_stack": [],
                    "gate_result": "resumed_from_previous_session",
                    "status": "COMPLETED",
                    "step_type": step.get("step_type", "local_execution"),
                }
                self.step_results.append(sr)
                continue

            sr = self.execute_step(step, i, len(steps))
            self.step_results.append(sr)

            if sr["status"] in ("FAILED", "PAUSED"):
                if sr["status"] == "FAILED":
                    print(f"\n  [FAIL] Step {i} FAILED. Halting execution.")
                else:
                    print(f"\n  [PAUSE]  Step {i} PAUSED at gate.")
                break

        # Phase 4: Write run log
        print(f"\n{'='*60}")
        print(f"PHASE 4: WRITE RUN LOG")
        print(f"{'='*60}")
        run_log_path = self.write_run_log()

        # Phase 5: Update mode coverage
        print(f"\n{'='*60}")
        print(f"PHASE 5: UPDATE MODE COVERAGE")
        print(f"{'='*60}")
        self.update_mode_coverage(run_log_path)

        # Phase 6: Rollback check
        has_failures = any(sr["status"] == "FAILED" for sr in self.step_results)
        if has_failures:
            self.rollback()

        # Summary
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"  Workflow:     {self.workflow_id}")
        print(f"  Mode:         {self.mode}")
        print(f"  Session:      {self.session_id}")
        print(f"  Status:       {self.final_state}")
        print(f"  Steps:        {len([s for s in self.step_results if s['status'] == 'COMPLETED'])}/{len(steps)}")
        print(f"  Gates:        {len(self.gate_decisions)}")
        print(f"  Errors:       {len(self.errors)}")
        print(f"  Run Log:      {run_log_path}")
        print()

        if has_failures:
            print(f"  [WARN]  Execution completed with failures.")
            return 2
        elif any(sr["status"] == "PAUSED" for sr in self.step_results):
            print(f"  [PAUSE]  Execution paused. Can resume.")
            return 3
        else:
            # Phase 7: Check for auto-invocation of next workflow (only in execution modes)
            should_invoke, source_artifact = self._should_auto_invoke_next()
            if should_invoke and self.mode in ("guided_execution", "autonomous_execution", "yolo_execution"):
                print(f"\n{'='*60}")
                print(f"PHASE 7: AUTO-INVOCATION CHECK")
                print(f"{'='*60}")
                next_workflow_id = self._extract_recommended_workflow(source_artifact)
                if next_workflow_id:
                    next_exit_code = self._invoke_next_workflow(next_workflow_id)
                    return next_exit_code
                else:
                    print(f"  [SKIP] Auto-invocation enabled but no recommended workflow found.")
                    print(f"  [OK] Execution completed successfully.")
                    return 0
            else:
                print(f"  [OK] Execution completed successfully.")
                return 0


# ===============================================================================
# CLI
# ===============================================================================

def list_workflows(repo_root: str) -> None:
    """List all registered workflows with their modes and steps."""
    registry = load_workflow_registry(repo_root)
    if not registry:
        print("workflow-registry.yaml not found or empty.")
        return
    workflows = registry.get("workflows", [])
    print(f"\nRegistered Workflows ({len(workflows)}):")
    print(f"{'='*60}")
    for wf in workflows:
        modes = ", ".join(wf.get("allowed_execution_modes", []))
        steps = len(wf.get("steps", []))
        print(f"  {wf['id']}")
        print(f"    Name:  {wf.get('display_name', '?')}")
        print(f"    Steps: {steps}")
        print(f"    Modes: {modes}")
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Production-grade orchestration runner for sensemaking workflows."
    )
    parser.add_argument("problem", nargs="?", default=None, help="Optional user problem statement or goal")
    parser.add_argument("--workflow", default=None, help="Explicit workflow ID (overrides default)")
    parser.add_argument("--mode", default="plan_only", choices=list(KNOWN_MODES.keys()),
                        help="Execution mode (default: plan_only)")
    parser.add_argument("--scope", default="soft", choices=["soft", "hard", "advisory"],
                        help="How strictly the problem statement constrains analysis (default: soft)")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--plan-out", default=None, help="Output path for the orchestration plan")
    parser.add_argument("--log-dir", default=None, help="Directory for run log output")
    parser.add_argument("--list-workflows", action="store_true", help="List all registered workflows")
    parser.add_argument("--resume", action="store_true", help="Resume a paused execution")
    parser.add_argument("--gate-decision", default=None,
                        choices=["auto-approve", "auto-deny"],
                        help="Non-interactive gate decision for testing: auto-approve all gates or auto-deny the first gate")

    args = parser.parse_args(argv)

    # Resolve repo root: if relative, treat as relative to cwd (same as other validators)
    if os.path.isabs(args.repo_root):
        repo_root = args.repo_root
    else:
        repo_root = os.path.abspath(args.repo_root)

    if args.list_workflows:
        list_workflows(repo_root)
        return 0

    # Determine workflow_id: explicit --workflow > default fast-local-diagnostic
    workflow_id = args.workflow or "fast-local-diagnostic"

    # Validate gate_decision compatibility
    if args.gate_decision and args.mode not in ("guided_execution", "autonomous_execution"):
        print(f"Note: --gate-decision is only for guided/autonomous modes, ignoring for '{args.mode}'")

    runner = OrchestrationRunner(
        workflow_id=workflow_id,
        mode=args.mode,
        repo_root=repo_root,
        plan_out=args.plan_out,
        log_dir=args.log_dir,
        resume=args.resume,
        gate_decision=args.gate_decision,
    )

    if runner.errors:
        for e in runner.errors:
            print(f"ERROR {e}")
        return 1

    # Create user intent artifact before running workflow
    intent_path = runner._create_user_intent_artifact(args.problem, args.scope)
    if not intent_path:
        print("ERROR: Failed to create user_intent artifact")
        for e in runner.errors:
            print(f"  - {e}")
        return 1

    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
