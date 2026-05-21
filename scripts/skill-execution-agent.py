"""
Skill Execution Agent: Reads orchestration plans and invokes skills in sequence.

Usage:
    python scripts/skill-execution-agent.py <plan_json_path> --repo-root <root>
"""

import os
import sys
import json
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# Import shared utilities
from _validator_utils import (
    format_error,
    load_yaml,
    resolve_repo_root,
)

# ============================================================================
# Skill Execution Error Codes
# ============================================================================
SKILL_NOT_FOUND = "SKILL_NOT_FOUND"
SKILL_INVOCATION_FAILED = "SKILL_INVOCATION_FAILED"
PLAN_LOAD_FAILED = "PLAN_LOAD_FAILED"
ARTIFACT_VERIFICATION_FAILED = "ARTIFACT_VERIFICATION_FAILED"
EXECUTION_TIMEOUT = "EXECUTION_TIMEOUT"
INVALID_PLAN_FORMAT = "INVALID_PLAN_FORMAT"


def load_orchestration_plan(plan_path: str) -> Tuple[bool, dict, str]:
    """Load and validate an orchestration plan JSON file.

    Returns (success: bool, plan_data: dict, error_msg: str)
    """
    if not os.path.exists(plan_path):
        return False, {}, format_error(PLAN_LOAD_FAILED, f"Plan file not found: {plan_path}")

    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
    except json.JSONDecodeError as e:
        return False, {}, format_error(INVALID_PLAN_FORMAT, f"Invalid JSON: {str(e)}")

    # Validate plan structure
    if "workflow_id" not in plan_data:
        return False, {}, format_error(INVALID_PLAN_FORMAT, "Plan missing 'workflow_id'")
    if "steps" not in plan_data or not isinstance(plan_data["steps"], list):
        return False, {}, format_error(INVALID_PLAN_FORMAT, "Plan missing 'steps' array")

    return True, plan_data, ""


def get_skill_invocation_command(skill_id: str, repo_root: str) -> Optional[str]:
    """Get the invocation command for a skill from the skill registry.

    Returns the command string (e.g. "/docs-aligner") or None if not found.
    """
    skill_registry_path = os.path.join(repo_root, "skills", "workflow-orchestrator", "references", "skill-registry.yaml")
    if not os.path.exists(skill_registry_path):
        return None

    registry = load_yaml(skill_registry_path)
    if not registry:
        return None

    # Search for skill in registry
    for ecosystem_name, ecosystem_data in registry.get("ecosystems", {}).items():
        for skill in ecosystem_data.get("skills", []):
            if skill.get("id") == skill_id:
                invocation = skill.get("invocation", {})
                if invocation.get("runtime") == "claude_code":
                    return invocation.get("command")

    return None


class SkillExecutionAgent:
    """Manages sequential skill execution for orchestration workflows."""

    def __init__(self, plan_data: dict, repo_root: str):
        self.plan_data = plan_data
        self.repo_root = os.path.abspath(repo_root)
        self.workflow_id = plan_data.get("workflow_id", "unknown")
        self.session_id = plan_data.get("session_id", "unknown")
        self.execution_log = []
        self.failed = False
        self.error_messages = []

    def invoke_skill(self, skill_id: str, step_context: dict, timeout: int) -> Tuple[bool, dict]:
        """
        Invoke a skill and wait for completion.

        For now, returns a placeholder indicating skill would be invoked.
        In production, this integrates with Claude Code Skill dispatcher.

        Returns (success: bool, result_data: dict)
        """
        # Create a skill invocation record
        result = {
            "skill_id": skill_id,
            "status": "invoked",
            "command": f"/{skill_id}",
            "timestamp": datetime.now().isoformat(),
            "context": step_context,
            "output_artifact": step_context.get("expected_output_artifact"),
            "timeout_seconds": timeout,
        }

        # TODO: In Task 3, this will actually invoke the skill via Anthropic SDK
        # For now, mark as ready for invocation
        result["ready_for_invocation"] = True

        return True, result

    def execute(self, timeout_per_skill: int = 600) -> Tuple[bool, str]:
        """Execute all steps in the plan sequentially.

        Returns (success: bool, summary_message: str)
        """
        steps = self.plan_data.get("steps", [])
        if not steps:
            return False, "Plan has no steps to execute"

        step_count = 0
        for i, step in enumerate(steps, start=1):
            step_id = step.get("step_id", i)
            skill_id = step.get("skill")

            # Get the skill invocation command
            command = get_skill_invocation_command(skill_id, self.repo_root)
            if not command:
                msg = format_error(SKILL_NOT_FOUND, f"Step {step_id}: Skill '{skill_id}' not in registry")
                self.execution_log.append(msg)
                self.error_messages.append(msg)
                self.failed = True
                continue

            # Invoke the skill
            success, result = self.invoke_skill(skill_id, step, timeout_per_skill)
            if not success:
                self.error_messages.append(f"Step {step_id}: Failed to invoke {skill_id}")
                self.failed = True

            self.execution_log.append(result)
            step_count += 1

        if self.failed:
            summary = f"Execution failed with {len(self.error_messages)} errors after {step_count} steps"
            return False, summary

        summary = f"All {step_count} steps prepared for skill invocation"
        return True, summary


def main():
    parser = argparse.ArgumentParser(description="Execute skills from an orchestration plan")
    parser.add_argument("plan_path", help="Path to orchestration plan JSON")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per skill in seconds")

    args = parser.parse_args()
    repo_root = resolve_repo_root(args.repo_root)

    # Load plan
    success, plan_data, error_msg = load_orchestration_plan(args.plan_path)
    if not success:
        print(error_msg)
        sys.exit(1)

    # Execute plan
    agent = SkillExecutionAgent(plan_data, repo_root)
    success, summary = agent.execute(timeout_per_skill=args.timeout)

    print(f"\n{'='*60}")
    print(f"SKILL EXECUTION COMPLETE")
    print(f"Workflow: {agent.workflow_id}")
    print(f"Session: {agent.session_id}")
    print(f"Result: {summary}")
    print(f"{'='*60}\n")

    if not success:
        for err in agent.error_messages:
            print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
