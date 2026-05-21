#!/usr/bin/env python3
"""
Automatic workflow router: takes raw project description and selects optimal workflow.

This script eliminates the need for users to know which workflow to invoke.
"""

import os
import sys
import argparse
import json
from pathlib import Path


def classify_project(description: str) -> dict:
    """Classify project type from raw description."""

    keywords = {
        "saas": {
            "primary": ["crm", "saas", "platform", "multi-user", "recurring revenue", "subscription",
                       "businesses", "customers", "pricing", "retention", "team", "integration"],
            "secondary": ["cloud", "api", "service", "scheduling", "management"]
        },
        "content": {
            "primary": ["learning", "courses", "education", "bootcamp", "students", "interactive",
                       "feedback", "teaching", "mentor", "platform"],
            "secondary": ["publishing", "content", "audience", "engagement"]
        },
        "tool": {
            "primary": ["package", "library", "cli", "framework", "instrumentation", "monitoring",
                       "observability", "developer", "engineering", "integration"],
            "secondary": ["build", "test", "debug", "performance"]
        },
        "consumer": {
            "primary": ["app", "mobile", "fitness", "game", "social", "engagement", "users",
                       "retention", "coaching", "ai-powered", "personalization"],
            "secondary": ["workout", "experience", "community", "progress"]
        },
        "enterprise": {
            "primary": ["internal", "dashboard", "analytics", "data", "admin", "workflow",
                       "enterprise", "companies", "teams", "visibility"],
            "secondary": ["management", "tracking", "optimization"]
        },
        "marketplace": {
            "primary": ["marketplace", "freelance", "providers", "suppliers", "transactions",
                       "commission", "specialized", "services", "retainer"],
            "secondary": ["platform", "business", "pricing", "relationships"]
        },
    }

    desc_lower = description.lower()
    scores = {}

    for project_type, kw_dict in keywords.items():
        primary_score = sum(2 for kw in kw_dict["primary"] if kw in desc_lower)
        secondary_score = sum(1 for kw in kw_dict["secondary"] if kw in desc_lower)
        scores[project_type] = primary_score + secondary_score

    if not any(scores.values()):
        return {"type": "research", "confidence": 40}

    primary_type = max(scores, key=scores.get)
    max_score = scores[primary_type]
    confidence = min(100, (max_score / 8) * 100)

    return {"type": primary_type, "confidence": int(confidence)}


def select_workflow(project_type: str, confidence: int, execution_mode: str = None) -> dict:
    """Select optimal workflow based on project type and confidence."""

    # Workflow selection matrix
    workflows = {
        "saas": {
            "primary": "product-discovery-sprint",
            "fallback": "product-autonomous-sprint",
            "modes": ["plan_only", "guided_execution", "autonomous_execution"]
        },
        "content": {
            "primary": "product-discovery-sprint",
            "fallback": "full-local-sensemaking",
            "modes": ["plan_only", "guided_execution", "autonomous_execution"]
        },
        "tool": {
            "primary": "full-local-sensemaking",
            "fallback": "docs-architecture",
            "modes": ["plan_only", "guided_execution", "autonomous_execution"]
        },
        "consumer": {
            "primary": "product-discovery-sprint",
            "fallback": "product-autonomous-sprint",
            "modes": ["plan_only", "guided_execution", "autonomous_execution"]
        },
        "enterprise": {
            "primary": "autonomous-sprint-preflight",
            "fallback": "docs-architecture",
            "modes": ["plan_only", "guided_execution", "autonomous_execution"]
        },
        "marketplace": {
            "primary": "product-discovery-sprint",
            "fallback": "product-autonomous-sprint",
            "modes": ["plan_only", "guided_execution", "autonomous_execution"]
        },
        "research": {
            "primary": "fast-local-diagnostic",
            "fallback": "full-local-sensemaking",
            "modes": ["plan_only", "guided_execution", "autonomous_execution"]
        },
    }

    workflow_info = workflows.get(project_type, workflows["research"])

    if confidence < 70:
        selected_mode = "plan_only"
        rationale = f"Low confidence ({confidence}%) classification. Starting in plan_only mode for validation."
    elif not execution_mode:
        selected_mode = "guided_execution"
        rationale = "User-recommended mode for review at each step."
    else:
        selected_mode = execution_mode if execution_mode in workflow_info["modes"] else "guided_execution"
        rationale = f"Requested mode: {execution_mode}"

    return {
        "primary_workflow": workflow_info["primary"],
        "fallback_workflow": workflow_info["fallback"],
        "recommended_mode": selected_mode,
        "supported_modes": workflow_info["modes"],
        "rationale": rationale,
        "command": f"python scripts/orchestration-runner.py {workflow_info['primary']} --mode {selected_mode}"
    }


def route_project(description_file: str, execution_mode: str = None) -> dict:
    """Route a project from raw description to recommended workflow."""

    if not os.path.exists(description_file):
        return {"error": f"File not found: {description_file}"}

    description = Path(description_file).read_text()

    classification = classify_project(description)
    workflow = select_workflow(classification["type"], classification["confidence"], execution_mode)

    routing = {
        "input_file": description_file,
        "classification": classification,
        "workflow_selection": workflow,
        "ready_to_execute": True,
        "next_step": f"Run: {workflow['command']}"
    }

    return routing


def main():
    parser = argparse.ArgumentParser(
        description="Automatic workflow router: classify project and select optimal workflow"
    )
    parser.add_argument(
        "project_description",
        help="Path to project description file (markdown)"
    )
    parser.add_argument(
        "--mode",
        choices=["plan_only", "guided_execution", "autonomous_execution", "yolo_execution"],
        help="Override recommended execution mode"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    routing = route_project(args.project_description, args.mode)

    if args.json:
        print(json.dumps(routing, indent=2))
    else:
        print("\n" + "="*70)
        print("PROJECT ROUTING ANALYSIS")
        print("="*70)
        print(f"\nInput: {routing['input_file']}")
        print(f"\nCLASSIFICATION")
        print(f"  Type: {routing['classification']['type']}")
        print(f"  Confidence: {routing['classification']['confidence']}%")
        print(f"\nWORKFLOW SELECTION")
        print(f"  Primary: {routing['workflow_selection']['primary_workflow']}")
        print(f"  Fallback: {routing['workflow_selection']['fallback_workflow']}")
        print(f"  Recommended Mode: {routing['workflow_selection']['recommended_mode']}")
        print(f"  Supported Modes: {', '.join(routing['workflow_selection']['supported_modes'])}")
        print(f"  Rationale: {routing['workflow_selection']['rationale']}")
        print(f"\nNEXT STEP")
        print(f"  $ {routing['workflow_selection']['command']}")
        print()


if __name__ == "__main__":
    main()
