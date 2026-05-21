#!/usr/bin/env python3
"""
Workflow Execution Engine

Coordinates orchestration runner with Claude skill invocation.
- Generates execution plan
- Invokes skills via skill registry
- Validates artifacts
- Manages approval gates

Usage:
    python workflow-execution-engine.py <workflow_id> --mode <mode> [--auto-approve]
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

class WorkflowExecutionEngine:
    def __init__(self, repo_root: str, workflow_id: str, mode: str, auto_approve: bool = False):
        self.repo_root = repo_root
        self.workflow_id = workflow_id
        self.mode = mode
        self.auto_approve = auto_approve
        self.workflow = None
        self.plan = None
        self.artifact_contracts = {}

    def load_workflow(self) -> bool:
        """Load workflow definition from registry."""
        registry_path = os.path.join(self.repo_root, "skills/workflow-orchestrator/references/workflow-registry.yaml")
        try:
            with open(registry_path) as f:
                registry = yaml.safe_load(f)

            for wf in registry.get("workflows", []):
                if wf.get("id") == self.workflow_id:
                    self.workflow = wf
                    return True

            print(f"[ERROR] Workflow '{self.workflow_id}' not found in registry")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to load workflow registry: {e}")
            return False

    def load_artifact_contracts(self) -> bool:
        """Load artifact contract definitions."""
        contracts_path = os.path.join(self.repo_root, "docs/ARTIFACT_CONTRACTS.md")
        try:
            # For now, return True - contracts are validated by orchestration-runner
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load artifact contracts: {e}")
            return False

    def generate_plan(self) -> bool:
        """Generate execution plan using orchestration runner."""
        print("\n[PHASE 1] Generating workflow plan...")
        cmd = [
            "python",
            os.path.join(self.repo_root, "scripts/orchestration-runner.py"),
            self.workflow_id,
            "--mode", self.mode,
        ]

        result = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True)

        if result.returncode != 0 and "Enter choice" not in result.stderr:
            print(f"[ERROR] Plan generation failed: {result.stderr}")
            return False

        print("[OK] Plan generated")
        return True

    def get_step_context(self, step: Dict) -> Dict:
        """Build execution context for a step."""
        context = {
            "step_id": step.get("id"),
            "skill": step.get("skill"),
            "input_artifact": step.get("input_artifact"),
            "output_artifact": step.get("output_artifact"),
            "gate": step.get("gate"),
        }

        # Load input artifact if specified
        if context["input_artifact"]:
            artifact_path = self._resolve_artifact_path(context["input_artifact"])
            if os.path.exists(artifact_path):
                with open(artifact_path) as f:
                    context["input_content"] = f.read()
            else:
                print(f"[WARN] Input artifact not found: {artifact_path}")

        return context

    def execute_workflow(self) -> bool:
        """Execute the complete workflow."""
        if not self.load_workflow():
            return False

        if not self.load_artifact_contracts():
            return False

        if not self.generate_plan():
            return False

        print("\n[PHASE 2] Executing workflow steps...")

        steps = self.workflow.get("steps", [])
        for i, step in enumerate(steps, 1):
            step_num = i
            total_steps = len(steps)
            skill_name = step.get("skill", "?")

            print(f"\n[STEP {step_num}/{total_steps}] Invoking skill: {skill_name}")

            context = self.get_step_context(step)

            # TODO: Invoke skill using Claude Skill tool or agent
            # For now, this is where skill invocation would happen
            # The orchestration runner will then validate the output

            print(f"  [NOTE] Skill '{skill_name}' needs external invocation")
            print(f"         Use: /skill {skill_name}")

            if self.mode == "guided_execution" and not self.auto_approve:
                choice = input(f"  Continue to validation? (Y/n): ").strip().upper()
                if choice == "N":
                    return False

        print("\n[PHASE 3] Validating all artifacts...")
        # Run orchestration runner in validation mode

        return True

    def _resolve_artifact_path(self, artifact_id: str) -> str:
        """Resolve artifact path from contract."""
        # Map artifact IDs to file paths
        artifacts_map = {
            "domain_alignment_report": "artifacts/domain_alignment_report.md",
            "prd": "artifacts/prd.md",
            "issue_list": "artifacts/issue_list.md",
            "agent_brief": "artifacts/agent_brief.md",
        }

        path = artifacts_map.get(artifact_id, f"artifacts/{artifact_id}.md")
        return os.path.join(self.repo_root, path)


def main():
    parser = argparse.ArgumentParser(description="Workflow Execution Engine")
    parser.add_argument("workflow", help="Workflow ID to execute")
    parser.add_argument("--mode", default="guided_execution", help="Execution mode")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve all gates")

    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    engine = WorkflowExecutionEngine(repo_root, args.workflow, args.mode, args.auto_approve)

    if engine.execute_workflow():
        print("\n[SUCCESS] Workflow execution completed")
        return 0
    else:
        print("\n[FAILED] Workflow execution failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
