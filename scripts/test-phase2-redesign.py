#!/usr/bin/env python3
"""
Test suite for Phase 2: docs-architecture Workflow Redesign

Verifies that:
1. docs-architecture workflow has exactly 2 steps (docs-aligner, handoff)
2. No to-prd step in docs-architecture (moved to product-to-issues)
3. Artifact flow is correct: domain_alignment_report -> prompt_handoff
4. product-to-issues workflow exists and has to-prd step
5. YAML syntax is valid
"""

import yaml
import sys
from pathlib import Path


def load_workflow_registry():
    """Load and parse the workflow registry YAML."""
    registry_path = Path("skills/workflow-orchestrator/references/workflow-registry.yaml")

    if not registry_path.exists():
        print(f"ERROR: Registry file not found at {registry_path}")
        sys.exit(1)

    try:
        with open(registry_path, 'r') as f:
            registry = yaml.safe_load(f)
        return registry
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse YAML: {e}")
        sys.exit(1)


def find_workflow(registry, workflow_id):
    """Find a workflow by ID in the registry."""
    for workflow in registry.get('workflows', []):
        if workflow.get('id') == workflow_id:
            return workflow
    return None


def test_yaml_syntax():
    """Test 1: YAML syntax is valid."""
    print("Test 1: YAML syntax validation...", end=" ")
    try:
        load_workflow_registry()
        print("[PASS]")
        return True
    except Exception as e:
        print(f"[FAIL]: {e}")
        return False


def test_docs_architecture_structure():
    """Test 2: docs-architecture workflow has exactly 2 steps."""
    print("Test 2: docs-architecture has 2 steps...", end=" ")

    registry = load_workflow_registry()
    docs_arch = find_workflow(registry, "docs-architecture")

    if not docs_arch:
        print("[FAIL]: docs-architecture workflow not found")
        return False

    steps = docs_arch.get('steps', [])

    if len(steps) != 2:
        print(f"[FAIL]: Expected 2 steps, got {len(steps)}")
        return False

    print("[PASS]")
    return True


def test_docs_architecture_step1():
    """Test 3: Step 1 is docs-aligner with correct artifacts."""
    print("Test 3: Step 1 is docs-aligner...", end=" ")

    registry = load_workflow_registry()
    docs_arch = find_workflow(registry, "docs-architecture")
    steps = docs_arch.get('steps', [])

    if not steps:
        print("[FAIL]: No steps found")
        return False

    step1 = steps[0]

    if step1.get('skill') != 'docs-aligner':
        print(f"[FAIL]: Expected 'docs-aligner', got '{step1.get('skill')}'")
        return False

    if step1.get('output_artifact') != 'domain_alignment_report':
        print(f"[FAIL]: Expected output 'domain_alignment_report', got '{step1.get('output_artifact')}'")
        return False

    print("[PASS]")
    return True


def test_docs_architecture_step2():
    """Test 4: Step 2 is handoff with correct artifact mapping."""
    print("Test 4: Step 2 is handoff with correct artifacts...", end=" ")

    registry = load_workflow_registry()
    docs_arch = find_workflow(registry, "docs-architecture")
    steps = docs_arch.get('steps', [])

    if len(steps) < 2:
        print("[FAIL]: Less than 2 steps")
        return False

    step2 = steps[1]

    if step2.get('skill') != 'handoff':
        print(f"[FAIL]: Expected 'handoff', got '{step2.get('skill')}'")
        return False

    if step2.get('input_artifact') != 'domain_alignment_report':
        print(f"[FAIL]: Expected input 'domain_alignment_report', got '{step2.get('input_artifact')}'")
        return False

    if step2.get('output_artifact') != 'prompt_handoff':
        print(f"[FAIL]: Expected output 'prompt_handoff', got '{step2.get('output_artifact')}'")
        return False

    print("[PASS]")
    return True


def test_no_to_prd_in_docs_arch():
    """Test 5: No to-prd step in docs-architecture."""
    print("Test 5: No to-prd step in docs-architecture...", end=" ")

    registry = load_workflow_registry()
    docs_arch = find_workflow(registry, "docs-architecture")
    steps = docs_arch.get('steps', [])

    for step in steps:
        if step.get('skill') == 'to-prd':
            print("[FAIL]: Found to-prd in docs-architecture (should be removed)")
            return False

    print("[PASS]")
    return True


def test_product_to_issues_exists():
    """Test 6: product-to-issues workflow exists with to-prd step."""
    print("Test 6: product-to-issues workflow exists...", end=" ")

    registry = load_workflow_registry()
    product_issues = find_workflow(registry, "product-to-issues")

    if not product_issues:
        print("[FAIL]: product-to-issues workflow not found")
        return False

    steps = product_issues.get('steps', [])

    if not steps:
        print("[FAIL]: product-to-issues has no steps")
        return False

    # First step should be to-prd
    if steps[0].get('skill') != 'to-prd':
        print(f"[FAIL]: Expected first step 'to-prd', got '{steps[0].get('skill')}'")
        return False

    print("[PASS]")
    return True


def test_docs_arch_purpose():
    """Test 7: docs-architecture purpose is updated."""
    print("Test 7: docs-architecture purpose updated...", end=" ")

    registry = load_workflow_registry()
    docs_arch = find_workflow(registry, "docs-architecture")

    purpose = docs_arch.get('purpose', '')

    # Should not mention PRD generation
    if 'prd' in purpose.lower():
        print(f"[WARN]: Purpose still mentions PRD: {purpose}")
        return False

    print("[PASS]")
    return True


def print_workflow_summary():
    """Print a summary of the workflows."""
    print("\n" + "="*70)
    print("WORKFLOW SUMMARY")
    print("="*70)

    registry = load_workflow_registry()

    # docs-architecture
    docs_arch = find_workflow(registry, "docs-architecture")
    print(f"\n1. docs-architecture ({docs_arch.get('display_name')})")
    print(f"   Purpose: {docs_arch.get('purpose')}")
    print(f"   Steps: {len(docs_arch.get('steps', []))}")
    for step in docs_arch.get('steps', []):
        print(f"     Step {step['id']}: {step['skill']}", end="")
        if 'input_artifact' in step:
            print(f" (from {step['input_artifact']})", end="")
        if 'output_artifact' in step:
            print(f" (to {step['output_artifact']})", end="")
        print()

    # product-to-issues
    product_issues = find_workflow(registry, "product-to-issues")
    print(f"\n2. product-to-issues ({product_issues.get('display_name')})")
    print(f"   Purpose: {product_issues.get('purpose')}")
    print(f"   Steps: {len(product_issues.get('steps', []))}")
    for step in product_issues.get('steps', []):
        print(f"     Step {step['id']}: {step['skill']}", end="")
        if 'input_artifact' in step:
            print(f" (from {step['input_artifact']})", end="")
        if 'output_artifact' in step:
            print(f" (to {step['output_artifact']})", end="")
        print()

    print()


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("PHASE 2 TEST SUITE: docs-architecture Workflow Redesign")
    print("="*70 + "\n")

    tests = [
        test_yaml_syntax,
        test_docs_architecture_structure,
        test_docs_architecture_step1,
        test_docs_architecture_step2,
        test_no_to_prd_in_docs_arch,
        test_product_to_issues_exists,
        test_docs_arch_purpose,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"[EXCEPTION]: {e}")
            results.append(False)

    # Print summary
    passed = sum(results)
    total = len(results)

    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*70)

    if passed == total:
        print("SUCCESS: All tests passed! Phase 2 redesign is correct.")
        print_workflow_summary()
        return 0
    else:
        print(f"FAILURE: {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
