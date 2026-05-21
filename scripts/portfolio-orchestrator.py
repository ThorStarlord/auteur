#!/usr/bin/env python3
"""
Portfolio orchestrator: run multiple projects in parallel through their workflows.

Enables multi-project handoffs without cognitive overhead. Automatically:
- Routes each project to optimal workflow
- Executes workflows in parallel
- Manages gates and completions
- Aggregates results for reporting
"""

import os
import sys
import json
import argparse
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict


@dataclass
class ProjectRoutingResult:
    """Result of routing a single project."""
    project_name: str
    project_file: str
    classification_type: str
    confidence: int
    workflow: str
    mode: str
    status: str  # pending, running, completed, failed
    execution_time: float = 0.0
    error_message: str = ""


class PortfolioOrchestrator:
    """Orchestrate parallel execution of multiple projects through their workflows."""

    def __init__(self, projects_dir: str, mode: str = "guided_execution", parallel_count: int = 3):
        self.projects_dir = Path(projects_dir)
        self.mode = mode
        self.parallel_count = parallel_count
        self.repo_root = Path(os.path.dirname(__file__)).parent
        self.results: list[ProjectRoutingResult] = []
        self.lock = threading.Lock()

    def discover_projects(self) -> list[Path]:
        """Discover all project files in the projects directory."""
        if not self.projects_dir.exists():
            print(f"Projects directory not found: {self.projects_dir}")
            return []

        projects = list(self.projects_dir.glob("project-*.md"))
        print(f"Discovered {len(projects)} projects:")
        for p in projects:
            print(f"  - {p.name}")
        return sorted(projects)

    def route_project(self, project_file: Path) -> ProjectRoutingResult:
        """Route a single project using the router.py script."""
        result = ProjectRoutingResult(
            project_name=project_file.stem,
            project_file=str(project_file),
            classification_type="unknown",
            confidence=0,
            workflow="unknown",
            mode=self.mode,
            status="pending"
        )

        try:
            cmd = [
                sys.executable,
                str(self.repo_root / "scripts" / "router.py"),
                str(project_file.resolve()),  # Use absolute path
                "--json",
                "--mode", self.mode
            ]

            start_time = datetime.now()
            # Change to repo root for the subprocess to have correct working directory
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.repo_root)
            )
            elapsed = (datetime.now() - start_time).total_seconds()
            result.execution_time = elapsed

            if proc.returncode != 0:
                result.status = "failed"
                result.error_message = f"Router failed (rc={proc.returncode}): {proc.stderr[:200]}"
                return result

            if not proc.stdout.strip():
                result.status = "failed"
                result.error_message = "Router produced no output"
                return result

            routing_data = json.loads(proc.stdout)
            result.classification_type = routing_data["classification"]["type"]
            result.confidence = routing_data["classification"]["confidence"]
            result.workflow = routing_data["workflow_selection"]["primary_workflow"]
            result.mode = routing_data["workflow_selection"]["recommended_mode"]
            result.status = "routed"

        except json.JSONDecodeError as e:
            result.status = "failed"
            result.error_message = f"Failed to parse router output: {str(e)}"
        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)

        return result

    def execute_workflow(self, result: ProjectRoutingResult) -> ProjectRoutingResult:
        """Execute the workflow for a routed project."""
        try:
            cmd = [
                sys.executable,
                str(self.repo_root / "scripts" / "orchestration-runner.py"),
                result.workflow,
                "--mode", result.mode,
                "--repo-root", str(self.repo_root)
            ]

            start_time = datetime.now()
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            elapsed = (datetime.now() - start_time).total_seconds()
            result.execution_time += elapsed

            if proc.returncode == 0:
                result.status = "completed"
            else:
                result.status = "failed"
                result.error_message = f"Workflow execution failed:\n{proc.stderr}"

        except subprocess.TimeoutExpired:
            result.status = "failed"
            result.error_message = "Workflow execution timed out"
        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)

        return result

    def process_project(self, project_file: Path) -> ProjectRoutingResult:
        """Route and execute a single project (routing + workflow)."""
        print(f"\n{'='*70}")
        print(f"Processing: {project_file.name}")
        print(f"{'='*70}")

        # Route the project
        print("  [1/2] Routing...")
        result = self.route_project(project_file)
        if result.status == "failed":
            print(f"  ✗ Routing failed: {result.error_message}")
            with self.lock:
                self.results.append(result)
            return result

        print(f"  ✓ Type: {result.classification_type} ({result.confidence}%)")
        print(f"  ✓ Workflow: {result.workflow} ({result.mode})")

        # Execute the workflow
        print("  [2/2] Executing workflow...")
        result = self.execute_workflow(result)
        if result.status == "completed":
            print(f"  ✓ Completed in {result.execution_time:.1f}s")
        else:
            print(f"  ✗ Failed: {result.error_message}")

        with self.lock:
            self.results.append(result)

        return result

    def run_portfolio(self) -> dict:
        """Execute all projects in parallel."""
        projects = self.discover_projects()
        if not projects:
            return {"error": "No projects found"}

        print(f"\nStarting portfolio orchestration (parallel={self.parallel_count}, mode={self.mode})")
        print(f"{'='*70}\n")

        start_time = datetime.now()

        with ThreadPoolExecutor(max_workers=self.parallel_count) as executor:
            futures = {executor.submit(self.process_project, p): p for p in projects}
            completed = 0
            for future in as_completed(futures):
                completed += 1
                print(f"\n[{completed}/{len(projects)}] completed")

        total_time = (datetime.now() - start_time).total_seconds()

        return {
            "total_projects": len(projects),
            "total_time": total_time,
            "mode": self.mode,
            "parallel_workers": self.parallel_count,
            "results": [asdict(r) for r in self.results]
        }

    def generate_report(self, run_results: dict) -> str:
        """Generate a portfolio execution report."""
        lines = []
        lines.append("# Portfolio Orchestration Report")
        lines.append("")
        lines.append(f"- **Date**: {datetime.now().isoformat()}")
        lines.append(f"- **Total Projects**: {run_results['total_projects']}")
        lines.append(f"- **Total Time**: {run_results['total_time']:.1f}s")
        lines.append(f"- **Execution Mode**: {run_results['mode']}")
        lines.append(f"- **Parallel Workers**: {run_results['parallel_workers']}")
        lines.append("")

        # Summary stats
        results = run_results["results"]
        completed = sum(1 for r in results if r["status"] == "completed")
        routed = sum(1 for r in results if r["status"] == "routed")
        failed = sum(1 for r in results if r["status"] == "failed")

        lines.append("## Summary")
        lines.append(f"- **Completed**: {completed}/{len(results)}")
        lines.append(f"- **Routed (not executed)**: {routed}/{len(results)}")
        lines.append(f"- **Failed**: {failed}/{len(results)}")
        lines.append("")

        # Results by project
        lines.append("## Results by Project")
        lines.append("")
        for r in results:
            icon = "✓" if r["status"] == "completed" else "✗" if r["status"] == "failed" else "→"
            lines.append(f"### {icon} {r['project_name']}")
            lines.append(f"- **Type**: {r['classification_type']} ({r['confidence']}%)")
            lines.append(f"- **Workflow**: {r['workflow']}")
            lines.append(f"- **Mode**: {r['mode']}")
            lines.append(f"- **Status**: {r['status']}")
            lines.append(f"- **Time**: {r['execution_time']:.1f}s")
            if r["error_message"]:
                lines.append(f"- **Error**: {r['error_message']}")
            lines.append("")

        # Failure analysis
        if failed > 0:
            lines.append("## Failure Analysis")
            lines.append("")
            for r in results:
                if r["status"] == "failed":
                    lines.append(f"### {r['project_name']}")
                    lines.append(f"```")
                    lines.append(r["error_message"])
                    lines.append(f"```")
                    lines.append("")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Portfolio orchestrator: run multiple projects in parallel"
    )
    parser.add_argument(
        "--projects-dir",
        default="test-projects",
        help="Directory containing project description files"
    )
    parser.add_argument(
        "--mode",
        choices=["plan_only", "guided_execution", "autonomous_execution", "yolo_execution"],
        default="guided_execution",
        help="Execution mode for all projects"
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=3,
        help="Number of parallel workers"
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/portfolio_report.md",
        help="Output path for portfolio report"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of markdown"
    )

    args = parser.parse_args()

    # Run portfolio
    orchestrator = PortfolioOrchestrator(args.projects_dir, args.mode, args.parallel)
    results = orchestrator.run_portfolio()

    # Generate report
    if args.json:
        report = json.dumps(results, indent=2)
    else:
        report = orchestrator.generate_report(results)

    # Write report
    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)

    print(f"\n{'='*70}")
    print(f"Portfolio report written to: {report_path}")
    print(f"{'='*70}\n")

    # Print summary
    if not args.json:
        print(report)

    # Return error code if any failed
    return 0 if all(r["status"] != "failed" for r in results["results"]) else 1


if __name__ == "__main__":
    sys.exit(main())
