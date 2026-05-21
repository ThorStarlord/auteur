import yaml
import sys

def test_product_to_issues_workflow_exists():
    """Verify product-to-issues workflow is in registry."""
    with open('skills/workflow-orchestrator/references/workflow-registry.yaml', 'r') as f:
        registry = yaml.safe_load(f)

    # Find product-to-issues workflow
    product_workflow = None
    for workflow in registry.get('workflows', []):
        if workflow.get('id') == 'product-to-issues':
            product_workflow = workflow
            break

    assert product_workflow is not None, "product-to-issues workflow not found in registry"
    print("[PASS] product-to-issues workflow exists")

def test_product_to_issues_structure():
    """Verify product-to-issues has correct 3-step structure."""
    with open('skills/workflow-orchestrator/references/workflow-registry.yaml', 'r') as f:
        registry = yaml.safe_load(f)

    # Find product-to-issues workflow
    product_workflow = None
    for workflow in registry.get('workflows', []):
        if workflow.get('id') == 'product-to-issues':
            product_workflow = workflow
            break

    assert product_workflow is not None, "product-to-issues workflow not found"

    # Verify workflow properties
    assert product_workflow.get('display_name') == 'Product PRD & Implementation Issues'
    assert 'domain alignment report' in product_workflow.get('purpose', '').lower()

    # Verify allowed execution modes
    allowed_modes = product_workflow.get('allowed_execution_modes', [])
    assert 'guided_execution' in allowed_modes, "guided_execution should be allowed"

    # Verify initial inputs
    initial_inputs = product_workflow.get('initial_inputs', [])
    assert len(initial_inputs) > 0, "Should have initial inputs"
    assert initial_inputs[0]['id'] == 'domain_alignment_report'

    # Verify steps
    steps = product_workflow.get('steps', [])
    assert len(steps) == 3, f"Should have 3 steps, got {len(steps)}"

    # Step 1: to-prd
    assert steps[0]['skill'] == 'to-prd', f"Step 1 should be to-prd, got {steps[0]['skill']}"
    assert steps[0]['input_artifact'] == 'domain_alignment_report'
    assert steps[0]['output_artifact'] == 'prd'
    assert steps[0].get('gate') == 'review_prd'

    # Step 2: to-issues
    assert steps[1]['skill'] == 'to-issues', f"Step 2 should be to-issues, got {steps[1]['skill']}"
    assert steps[1]['input_artifact'] == 'prd'
    assert steps[1]['output_artifact'] == 'issue_list'
    assert steps[1].get('gate') == 'review_issues'

    # Step 3: triage
    assert steps[2]['skill'] == 'triage', f"Step 3 should be triage, got {steps[2]['skill']}"
    assert steps[2]['input_artifact'] == 'issue_list'
    assert steps[2]['output_artifact'] == 'agent_brief'
    assert steps[2].get('gate') == 'review_agent_brief'

    print("[PASS] product-to-issues workflow structure verified:")
    print(f"  - Display name: {product_workflow['display_name']}")
    print(f"  - Steps: {len(steps)} (to-prd -> to-issues -> triage)")
    print(f"  - Input: domain_alignment_report")
    print(f"  - Output: agent_brief")

def test_artifact_chain():
    """Verify the artifact flow from docs-architecture to product-to-issues."""
    with open('skills/workflow-orchestrator/references/workflow-registry.yaml', 'r') as f:
        registry = yaml.safe_load(f)

    # Find docs-architecture workflow
    docs_workflow = None
    for workflow in registry.get('workflows', []):
        if workflow.get('id') == 'docs-architecture':
            docs_workflow = workflow
            break

    assert docs_workflow is not None, "docs-architecture workflow not found"

    # Find product-to-issues workflow
    product_workflow = None
    for workflow in registry.get('workflows', []):
        if workflow.get('id') == 'product-to-issues':
            product_workflow = workflow
            break

    assert product_workflow is not None, "product-to-issues workflow not found"

    # Verify docs-architecture produces domain_alignment_report
    docs_steps = docs_workflow.get('steps', [])
    docs_output_artifacts = [s.get('output_artifact') for s in docs_steps]
    assert 'domain_alignment_report' in docs_output_artifacts, \
        "docs-architecture should produce domain_alignment_report"

    # Verify product-to-issues consumes domain_alignment_report
    product_initial_inputs = product_workflow.get('initial_inputs', [])
    product_input_ids = [i['id'] for i in product_initial_inputs]
    assert 'domain_alignment_report' in product_input_ids, \
        "product-to-issues should consume domain_alignment_report"

    print("[PASS] Artifact chain verified:")
    print(f"  - docs-architecture produces: domain_alignment_report")
    print(f"  - product-to-issues consumes: domain_alignment_report")
    print(f"  - product-to-issues produces: agent_brief")

if __name__ == "__main__":
    try:
        test_product_to_issues_workflow_exists()
        test_product_to_issues_structure()
        test_artifact_chain()
        print("\n[SUCCESS] All tests passed!")
    except AssertionError as e:
        print(f"[FAILED] Test failed: {e}")
        sys.exit(1)
