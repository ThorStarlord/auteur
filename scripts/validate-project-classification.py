#!/usr/bin/env python3
"""Validate project classification against test projects."""

import os
import json
from pathlib import Path

def classify_project(description: str) -> dict:
    """Classify a project based on description."""

    # Enhanced keyword detection with weighted scoring
    keywords = {
        "saas": {
            "primary": ["crm", "saas", "platform", "multi-user", "recurring revenue", "subscription",
                       "businesses", "customers", "pricing", "retention", "team", "integration"],
            "secondary": ["cloud", "api", "service", "scheduling", "management"]
        },
        "content": {
            "primary": ["learning", "courses", "education", "bootcamp", "students", "interactive",
                       "feedback", "teaching", "mentor"],
            "secondary": ["publishing", "content", "platform", "audience", "engagement"]
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
    # Confidence: max_score / (total_keywords * 2) but capped at 100%
    confidence = min(100, (max_score / 8) * 100)

    return {"type": primary_type, "confidence": int(confidence)}

def recommend_workflow(project_type: str, confidence: int) -> dict:
    """Recommend workflow based on project type."""

    workflows = {
        "saas": ("product-discovery-sprint", "product-autonomous-sprint"),
        "content": ("product-discovery-sprint", "full-local-sensemaking"),
        "tool": ("docs-architecture", "full-local-sensemaking"),
        "consumer": ("product-discovery-sprint", "product-autonomous-sprint"),
        "enterprise": ("autonomous-sprint-preflight", "docs-architecture"),
        "marketplace": ("product-discovery-sprint", "product-autonomous-sprint"),
        "research": ("fast-local-diagnostic", "full-local-sensemaking"),
    }

    if confidence < 70:
        return {
            "primary": "plan_only",
            "fallback": workflows.get(project_type, ("full-local-sensemaking", "fast-local-diagnostic"))[0],
            "rationale": f"Low confidence ({confidence}%) classification. Start with planning mode."
        }

    primary, fallback = workflows.get(project_type, ("full-local-sensemaking", "fast-local-diagnostic"))
    return {
        "primary": primary,
        "fallback": fallback,
        "rationale": f"High confidence ({confidence}%) {project_type} classification."
    }

def test_classification():
    """Test classification on all test projects."""

    test_dir = Path("test-projects")
    if not test_dir.exists():
        print(f"Test projects directory not found: {test_dir}")
        return

    results = []

    for project_file in sorted(test_dir.glob("project-*.md")):
        print(f"\n{'='*60}")
        print(f"Testing: {project_file.name}")
        print(f"{'='*60}")

        content = project_file.read_text()

        # Extract just the fog section for classification
        fog_start = content.find("## Raw Fog")
        fog_end = content.find("## Target Market") if "## Target Market" in content else len(content)
        fog_text = content[fog_start:fog_end] if fog_start > 0 else content

        classification = classify_project(fog_text)
        workflow = recommend_workflow(classification["type"], classification["confidence"])

        result = {
            "project": project_file.name,
            "classification": classification,
            "recommended_workflow": workflow
        }
        results.append(result)

        print(f"Type: {classification['type']}")
        print(f"Confidence: {classification['confidence']}%")
        print(f"Primary Workflow: {workflow['primary']}")
        print(f"Fallback: {workflow['fallback']}")
        print(f"Rationale: {workflow['rationale']}")

    # Write results
    results_file = Path("artifacts/classification_test_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2))
    print(f"\n\nResults written to: {results_file}")

    return results

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__) + "/..")
    test_classification()
