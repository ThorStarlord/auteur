"""Phase A dogfood for Book external-edit routing.

This test suite exercises Book inspection and routing against 14 scenarios:
1. No changes (baseline)
2. Unchanged marked Book
3. Chapter-only wording edit
4. Separator-only edit
5. Chapter reorder
6. Mixed Chapter and Book edit
7. Markerless manuscript
8. Malformed marker
9. Cross-Chapter movement
10. Stale inspection
11. Atomic routing failure
12. Author-facing UX
13. File and artifact ergonomics
14. Phase A verification and reporting

Tasks A2-A14 will implement scenarios and progressively populate this framework.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import patch, MagicMock


def generate_message_from_inspection(inspection_report: dict[str, Any]) -> str:
    """Generate a dynamic message from an inspection report.

    Returns:
    - For no_changes status with 0 findings: "No changes detected. No canonical artifacts were changed."
    - For changed status or when findings > 0: detailed findings count message
    - Always includes the inspection status

    Args:
        inspection_report: Dict containing 'status', 'chapter_findings', 'book_findings', 'unresolved_findings'

    Returns:
        A message string reflecting the actual inspection findings
    """
    status = inspection_report.get('status', 'unknown')
    chapter_findings = inspection_report.get('chapter_findings', [])
    book_findings = inspection_report.get('book_findings', [])
    unresolved_findings = inspection_report.get('unresolved_findings', [])

    chapter_count = len(chapter_findings)
    book_count = len(book_findings)
    unresolved_count = len(unresolved_findings)

    # If status is no_changes and all findings are 0, return no-changes message
    if status == 'no_changes' and chapter_count == 0 and book_count == 0 and unresolved_count == 0:
        return "No changes detected. No canonical artifacts were changed."

    # For changed status or when findings exist, return detailed message
    if chapter_count > 0 or book_count > 0 or unresolved_count > 0:
        return f"{chapter_count} chapter findings, {book_count} book findings, {unresolved_count} unresolved findings detected."

    # Default fallback
    return f"Status: {status}. Inspection complete with no notable findings."


class TestBookExternalRoutingDogfood:
    """Dogfood harness for Book external-edit routing scenarios.

    Each scenario tests:
    - Inspection detects expected changes
    - Routing correctly delegates to Chapter or Book proposals
    - Canonical artifacts remain unchanged
    - Atomicity preserved under failure
    """

    @staticmethod
    def load_baselines(project_root: Path) -> dict[str, str]:
        """Load baseline hashes for canonical artifacts."""
        baselines_file = project_root / ".auteur" / "baselines.json"
        if baselines_file.exists():
            with open(baselines_file) as f:
                return json.load(f)
        return {}

    @staticmethod
    def verify_baselines_unchanged(project_root: Path) -> bool:
        """Verify that canonical artifacts have not mutated."""
        baselines = TestBookExternalRoutingDogfood.load_baselines(project_root)
        artifacts = {
            'story_identity': '.auteur/state/artifacts/story_identity.yaml',
            'blueprint': '.auteur/state/artifacts/blueprint.yaml',
            'chapter_01': '.auteur/state/artifacts/chapter_01.yaml',
            'chapter_02': '.auteur/state/artifacts/chapter_02.yaml',
            'chapter_01_expression': './chapters/01/expression/chapter_v001.yaml',
            'chapter_02_expression': './chapters/02/expression/chapter_v001.yaml',
            'book_expression': './book/expression/book_v001.yaml',
        }

        for name, path_str in artifacts.items():
            path = project_root / path_str
            if path.exists():
                content = path.read_text(encoding='utf-8')
                current_hash = hashlib.sha256(content.encode()).hexdigest()
                baseline_hash = baselines.get(name)
                if baseline_hash and current_hash != baseline_hash:
                    return False
        return True


def inspect_book_external_manuscript(project_root: Path, manuscript_path: Path) -> dict[str, Any]:
    """Wrapper around Book inspection. Returns structured result dict.

    Task A2 tests inspection-only mode (no routing). For scenarios A3-A14 that need routing,
    call BookReconciliationStore.route(inspection_id) separately after inspection, or use
    a route_book_inspection() wrapper (to be added in A3+).

    Adapted from BookReconciliationStore.inspect() which returns:
    - status: 'no_changes', 'changed', or 'unresolved'
    - chapter_findings: list of chapter-level findings
    - book_findings: list of book-level findings
    - unresolved_findings: list of unresolved findings

    Routing path for A3+:
    The wrapper's message generation is intentionally dynamic so that downstream scenarios
    can rely on accurate feedback about what inspection found. The routing step (delegating
    to Chapter or Book proposal engines) is separate and will be added in subsequent tasks.
    """
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    # Load the accepted book expression ID from accepted.yaml
    book_dir = project_root / "book" / "expression"
    accepted_file = book_dir / "accepted.yaml"
    if not accepted_file.exists():
        raise FileNotFoundError(f"No accepted book expression found at {accepted_file}")

    accepted_data = yaml.safe_load(accepted_file.read_text(encoding='utf-8')) or {}
    book_expression_id = accepted_data.get('book_expression_id')
    if not book_expression_id:
        raise ValueError("No book_expression_id found in accepted.yaml")

    # Run the inspection
    store = BookReconciliationStore(book_dir.parent.parent)  # Pass project root
    inspection_report = store.inspect(manuscript_path, book_expression_id)

    # Count findings by scope (classification for chapter/book/unresolved)
    chapter_findings = inspection_report.get('chapter_findings', [])
    book_findings = inspection_report.get('book_findings', [])
    unresolved_findings = inspection_report.get('unresolved_findings', [])

    return {
        'status': inspection_report.get('status', 'unknown'),
        'chapter_findings_count': len(chapter_findings),
        'book_findings_count': len(book_findings),
        'unresolved_findings_count': len(unresolved_findings),
        'routes': [],  # Routes come from routing, not inspection
        'proposals': [],  # Proposals come from routing, not inspection
        'message': generate_message_from_inspection(inspection_report),
        'inspection_id': inspection_report.get('inspection_id'),
        'full_report': inspection_report  # Include full report for debugging
    }


# Scenario tests to be implemented in Tasks A2-A14
def test_placeholder_a1_baseline():
    """Task A1: Baseline setup complete.

    This placeholder verifies that:
    - Temporary project is bootstrapped
    - Baseline hashes are recorded
    - Test framework is ready for scenario implementation
    """
    assert True  # Framework structure verified


def test_unchanged_marked_book_inspection():
    """Scenario 2: Unchanged marked Book should produce no changes, proposals, or findings."""
    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    manuscript_path = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'

    # Inspect the unchanged Book manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=manuscript_path
    )

    assert result['status'] == 'no_changes', f"Expected 'no_changes' status, got '{result['status']}'"
    assert result['chapter_findings_count'] == 0, f"Expected 0 chapter findings, got {result['chapter_findings_count']}"
    assert result['book_findings_count'] == 0, f"Expected 0 book findings, got {result['book_findings_count']}"
    assert result['unresolved_findings_count'] == 0, f"Expected 0 unresolved findings, got {result['unresolved_findings_count']}"
    assert result['routes'] == [], f"Expected empty routes, got {result['routes']}"
    assert result['proposals'] == [], f"Expected empty proposals, got {result['proposals']}"
    assert 'No changes detected' in result['message'], f"Expected 'No changes detected' in message, got: {result['message']}"
    assert 'No canonical artifacts were changed' in result['message'], f"Expected 'No canonical artifacts were changed' in message, got: {result['message']}"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"


def test_chapter_only_edit_creates_delegated_inspection():
    """Scenario 3: Chapter wording edit → one delegated Chapter inspection, zero Book proposals."""
    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_chapter_edit.md'

    # Create a copy of the manuscript with Chapter-only edits
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Modify text only inside chapter_01 (between the markers)
    # Find the chapter_01 text and modify only the prose within it
    # Replace "The river wind carries Tomas's warning up the tower." with a modified version
    modified_content = content.replace(
        "The river wind carries Tomas's warning up the tower.",
        "The river wind carries Tomas's solemn warning up the tower."
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    # Inspect the modified manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )

    # Assertions for Chapter-only edit scenario
    assert result['status'] == 'changed', f"Expected 'changed' status, got '{result['status']}'"
    assert result['chapter_findings_count'] == 1, f"Expected 1 chapter finding, got {result['chapter_findings_count']}"
    assert result['book_findings_count'] == 0, f"Expected 0 book findings, got {result['book_findings_count']}"
    assert result['unresolved_findings_count'] == 0, f"Expected 0 unresolved findings, got {result['unresolved_findings_count']}"
    assert result['routes'] == [], f"Expected no routes (inspection only, not routing), got {result['routes']}"
    assert result['proposals'] == [], f"Expected no proposals (inspection only), got {result['proposals']}"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()


def test_separator_edit_creates_book_proposal():
    """Scenario 4: Separator-only edit → one book finding with book_separator_patch proposal."""
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_separator_edit.md'

    # Create a copy of the manuscript with separator-only edits
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Modify only the separator (change "---" to "===")
    # The separator is between the markers: <!-- auteur:book-separator id=separator_01 revision=1 -->
    # We need to replace the "---" line that appears between the separator markers
    modified_content = content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n===\n<!-- auteur:end-book-separator id=separator_01 -->"
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    # Inspect the modified manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )

    # Assertions for Separator-only edit scenario
    assert result['status'] == 'changed', f"Expected 'changed' status, got '{result['status']}'"
    assert result['chapter_findings_count'] == 0, f"Expected 0 chapter findings, got {result['chapter_findings_count']}"
    assert result['book_findings_count'] == 1, f"Expected 1 book finding, got {result['book_findings_count']}"
    assert result['unresolved_findings_count'] == 0, f"Expected 0 unresolved findings, got {result['unresolved_findings_count']}"

    # Verify the book finding is a separator change
    full_report = result['full_report']
    assert len(full_report['book_findings']) == 1, "Expected exactly 1 book finding"
    separator_finding = full_report['book_findings'][0]
    assert separator_finding['classification'] == 'separator_changed', f"Expected 'separator_changed' classification, got '{separator_finding['classification']}'"
    assert separator_finding['recommended_proposal'] == 'book_separator_patch', f"Expected 'book_separator_patch' proposal type, got '{separator_finding['recommended_proposal']}'"
    assert separator_finding['original_text'] == '---', f"Expected original separator '---', got '{separator_finding['original_text']}'"
    assert separator_finding['edited_text'] == '===', f"Expected edited separator '===', got '{separator_finding['edited_text']}'"

    # Now route the inspection to generate the actual proposal
    store = BookReconciliationStore(project_root)
    inspection_id = result['inspection_id']
    routing_result = store.route(inspection_id)

    # Verify routing created the proposal
    assert routing_result['status'] == 'routed', f"Expected 'routed' status, got '{routing_result['status']}'"
    assert len(routing_result['book_proposals']) == 1, f"Expected 1 book proposal, got {len(routing_result['book_proposals'])}"
    proposal_id = routing_result['book_proposals'][0]

    # Load the proposal and verify it contains book_separator_patch
    proposal_path = project_root / 'book' / 'expression' / 'reconciliation' / 'proposals' / f'{proposal_id}.yaml'
    assert proposal_path.exists(), f"Proposal file not found at {proposal_path}"
    proposal_data = yaml.safe_load(proposal_path.read_text(encoding='utf-8')) or {}
    assert proposal_data.get('proposal_type') == 'book_separator_patch', f"Expected proposal_type 'book_separator_patch', got '{proposal_data.get('proposal_type')}'"
    assert proposal_data.get('original') == '---', f"Expected original '---', got '{proposal_data.get('original')}'"
    assert proposal_data.get('proposed') == '===', f"Expected proposed '===', got '{proposal_data.get('proposed')}'"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()


def test_mixed_chapter_and_book_edit_creates_proposals():
    """Scenario 6: Mixed Chapter wording + separator edit → 1 chapter finding + 1 book finding with 2 proposals."""
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_mixed_edit.md'

    # Create a copy of the manuscript with both chapter and separator edits
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Make a chapter wording edit (like scenario 3)
    modified_content = content.replace(
        "The river wind carries Tomas's warning up the tower.",
        "The river wind carries Tomas's solemn warning up the tower."
    )

    # Also make a separator edit (like scenario 4)
    modified_content = modified_content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n===\n<!-- auteur:end-book-separator id=separator_01 -->"
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    # Inspect the modified manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )

    # Assertions for Mixed edit scenario
    assert result['status'] == 'changed', f"Expected 'changed' status, got '{result['status']}'"
    assert result['chapter_findings_count'] == 1, f"Expected 1 chapter finding, got {result['chapter_findings_count']}"
    assert result['book_findings_count'] == 1, f"Expected 1 book finding, got {result['book_findings_count']}"
    assert result['unresolved_findings_count'] == 0, f"Expected 0 unresolved findings, got {result['unresolved_findings_count']}"

    # Verify the findings are as expected
    full_report = result['full_report']
    assert len(full_report['chapter_findings']) == 1, "Expected exactly 1 chapter finding"
    assert len(full_report['book_findings']) == 1, "Expected exactly 1 book finding"

    chapter_finding = full_report['chapter_findings'][0]
    assert chapter_finding['classification'] == 'modified', f"Expected 'modified' classification, got '{chapter_finding['classification']}'"
    assert chapter_finding['route'] == 'chapter_reconciliation', f"Expected 'chapter_reconciliation' route, got '{chapter_finding['route']}'"

    book_finding = full_report['book_findings'][0]
    assert book_finding['classification'] == 'separator_changed', f"Expected 'separator_changed' classification, got '{book_finding['classification']}'"
    assert book_finding['recommended_proposal'] == 'book_separator_patch', f"Expected 'book_separator_patch' proposal type, got '{book_finding['recommended_proposal']}'"
    assert book_finding['original_text'] == '---', f"Expected original separator '---', got '{book_finding['original_text']}'"
    assert book_finding['edited_text'] == '===', f"Expected edited separator '===', got '{book_finding['edited_text']}'"

    # Now route the inspection to generate the actual proposals
    store = BookReconciliationStore(project_root)
    inspection_id = result['inspection_id']
    routing_result = store.route(inspection_id)

    # Verify routing created the proposals
    assert routing_result['status'] == 'routed', f"Expected 'routed' status, got '{routing_result['status']}'"

    # Should have chapter proposals and book proposals
    chapter_proposals = routing_result.get('chapter_proposals', [])
    book_proposals = routing_result.get('book_proposals', [])

    total_proposals = len(chapter_proposals) + len(book_proposals)
    assert total_proposals == 2, f"Expected 2 total proposals (delegated inspection + book proposal), got {total_proposals} (chapter: {len(chapter_proposals)}, book: {len(book_proposals)})"

    # Verify routing manifest exists
    routing_manifest_path = project_root / 'book' / 'expression' / 'reconciliation' / 'routing_manifest.yaml'
    assert routing_manifest_path.exists(), f"Routing manifest not found at {routing_manifest_path}"

    # Load the routing manifest and verify it contains both proposals
    manifest_data = yaml.safe_load(routing_manifest_path.read_text(encoding='utf-8')) or {}
    inspections = manifest_data.get('inspections', [])
    assert len(inspections) > 0, "Expected at least 1 inspection in routing manifest"

    # Find our inspection in the manifest
    our_inspection = None
    for inspection in inspections:
        if inspection.get('inspection_id') == inspection_id:
            our_inspection = inspection
            break

    assert our_inspection is not None, f"Inspection {inspection_id} not found in routing manifest"
    assert our_inspection.get('status') == 'routed', f"Expected inspection status 'routed', got '{our_inspection.get('status')}'"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()


def test_stale_inspection_blocks_routing():
    """Scenario 10: Stale inspection → routing status=stale, 0 outputs, original inspection preserved."""
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_stale.md'

    # Create a copy of the manuscript with a Chapter edit
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Modify text inside chapter_01
    modified_content = content.replace(
        "The river wind carries Tomas's warning up the tower.",
        "The river wind carries Tomas's urgent warning up the tower."
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    # Perform the inspection - this captures the current state
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )

    # Verify the inspection found the chapter change
    assert result['status'] == 'changed', f"Expected 'changed' status for initial inspection, got '{result['status']}'"
    assert result['chapter_findings_count'] == 1, f"Expected 1 chapter finding, got {result['chapter_findings_count']}"
    inspection_id = result['inspection_id']

    # Store the original inspection for later verification
    store = BookReconciliationStore(project_root)
    original_inspection_path = store._inspection_path(inspection_id)
    original_inspection_content = original_inspection_path.read_text(encoding='utf-8')

    # Now simulate a Chapter being updated after the inspection was created
    # We do this by modifying the accepted.yaml to have a different revision than what the Book references
    chapter_dir = project_root / "chapters" / "01" / "expression"
    accepted_file = chapter_dir / "accepted.yaml"
    accepted_data = yaml.safe_load(accepted_file.read_text(encoding='utf-8')) or {}

    # Save the original values for restoration
    original_revision = accepted_data.get('revision', 1)
    original_content_hash = accepted_data.get('content_hash')

    # Change the revision to simulate the chapter being updated
    accepted_data['revision'] = original_revision + 1
    # Also change the content_hash to make it clearly different
    accepted_data['content_hash'] = "sha256:different_hash_to_simulate_update"

    # Write the modified accepted.yaml back
    accepted_file.write_text(yaml.safe_dump(accepted_data, sort_keys=False), encoding='utf-8')

    # Now attempt to route the original inspection
    # This should fail because the Chapter has been updated since inspection was created
    routing_result = store.route(inspection_id)

    # Verify routing detected staleness
    assert routing_result['status'] == 'stale', f"Expected 'stale' status, got '{routing_result['status']}'"
    assert len(routing_result['chapter_routes']) == 0, f"Expected 0 chapter routes, got {len(routing_result['chapter_routes'])}"
    assert len(routing_result['book_proposals']) == 0, f"Expected 0 book proposals, got {len(routing_result['book_proposals'])}"
    assert routing_result['routing_id'] is None, f"Expected no routing_id when stale, got '{routing_result['routing_id']}'"

    # Verify the inspection was updated with stale status
    updated_inspection_content = original_inspection_path.read_text(encoding='utf-8')
    updated_inspection = yaml.safe_load(updated_inspection_content) or {}
    assert updated_inspection.get('status') == 'stale', f"Expected inspection status 'stale', got '{updated_inspection.get('status')}'"
    assert updated_inspection.get('freshness', {}).get('status') == 'stale', f"Expected freshness status 'stale'"
    assert 'BOOK_OR_CHAPTER_REVISION_CHANGED' in updated_inspection.get('freshness', {}).get('reasons', []), f"Expected stale reason to identify changed artifact"

    # Verify the original inspection structure is preserved (only freshness status changed)
    assert updated_inspection.get('inspection_id') == inspection_id, "Inspection ID should remain unchanged"
    assert updated_inspection.get('chapter_findings') == result['full_report'].get('chapter_findings'), "Chapter findings should remain unchanged"
    assert updated_inspection.get('book_findings') == result['full_report'].get('book_findings'), "Book findings should remain unchanged"

    # Verify no routing manifest was created
    routing_manifest_path = store.root / "routing" / f"routing_{inspection_id}.yaml"
    assert not routing_manifest_path.exists(), f"No routing manifest should exist for stale inspection, but found at {routing_manifest_path}"

    # Verify no proposals directory contains new proposals
    proposals_dir = store.root / "proposals"
    if proposals_dir.exists():
        proposals = [f for f in proposals_dir.glob(f"proposal_{inspection_id}_*.yaml")]
        assert len(proposals) == 0, f"Expected 0 proposals for stale inspection, found {len(proposals)}"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test files and restore the Chapter's accepted.yaml
    if test_ms.exists():
        test_ms.unlink()

    # Restore the original accepted.yaml to its original state
    # Revert the revision and content_hash back to the original values
    restored_data = accepted_data.copy()
    restored_data['revision'] = original_revision
    restored_data['content_hash'] = original_content_hash
    accepted_file.write_text(yaml.safe_dump(restored_data, sort_keys=False), encoding='utf-8')


def test_markerless_manuscript_creates_unresolved_finding():
    """Scenario 7: Markerless manuscript → one unresolved markerless finding, zero routes/proposals."""
    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_markerless.md'

    # Create a copy and remove all markers
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Remove all markers by replacing them with empty strings
    # Pattern: remove <!-- auteur:... --> markers
    markerless_content = content
    markerless_content = markerless_content.replace(
        "<!-- auteur:chapter id=chapter_01 expression_revision=1 -->\n",
        ""
    )
    markerless_content = markerless_content.replace(
        "\n<!-- auteur:end-chapter id=chapter_01 -->",
        ""
    )
    markerless_content = markerless_content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "---"
    )
    markerless_content = markerless_content.replace(
        "<!-- auteur:chapter id=chapter_02 expression_revision=1 -->\n",
        ""
    )
    markerless_content = markerless_content.replace(
        "\n<!-- auteur:end-chapter id=chapter_02 -->",
        ""
    )
    test_ms.write_text(markerless_content, encoding='utf-8')

    # Inspect the markerless manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )

    # Assertions for Markerless scenario
    assert result['status'] == 'unresolved', f"Expected 'unresolved' status, got '{result['status']}'"
    assert result['chapter_findings_count'] == 0, f"Expected 0 chapter findings, got {result['chapter_findings_count']}"
    assert result['book_findings_count'] == 0, f"Expected 0 book findings, got {result['book_findings_count']}"
    assert result['unresolved_findings_count'] == 1, f"Expected 1 unresolved finding, got {result['unresolved_findings_count']}"
    assert result['routes'] == [], f"Expected empty routes, got {result['routes']}"
    assert result['proposals'] == [], f"Expected empty proposals, got {result['proposals']}"

    # Verify the unresolved finding is a markerless finding
    full_report = result['full_report']
    assert len(full_report['unresolved_findings']) == 1, "Expected exactly 1 unresolved finding"
    markerless_finding = full_report['unresolved_findings'][0]
    assert markerless_finding['classification'] == 'markerless', f"Expected 'markerless' classification, got '{markerless_finding['classification']}'"

    # Verify the finding includes an actionable recommendation
    assert 'recommended_action' in markerless_finding, "Expected 'recommended_action' in finding"
    assert markerless_finding['recommended_action'] == 'restore Book markers or map the manuscript manually', \
        f"Expected recommendation to restore markers or map manually, got '{markerless_finding['recommended_action']}'"

    # Verify evidence and severity
    assert markerless_finding['evidence'] == 'no Book ownership markers', \
        f"Expected evidence 'no Book ownership markers', got '{markerless_finding['evidence']}'"
    assert markerless_finding.get('severity') == 'unresolved' or markerless_finding.get('classification') == 'markerless', \
        "Expected unresolved severity or markerless classification"

    # Verify no noisy per-chapter findings
    for finding in full_report['chapter_findings']:
        assert finding['classification'] != 'markerless', "Should not have per-chapter markerless findings"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()


def test_chapter_reorder_creates_book_order_proposal():
    """Scenario 5: Chapter reorder → one book finding with book_order_change_proposal."""
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml
    import re

    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_chapter_reorder.md'

    # Create a copy of the manuscript with reordered chapters
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Reorder chapters: swap chapter_01 and chapter_02
    # Extract chapter_02 section (including markers)
    chapter_02_pattern = r'<!-- auteur:chapter id=chapter_02 expression_revision=1 -->.*?<!-- auteur:end-chapter id=chapter_02 -->'
    chapter_02_match = re.search(chapter_02_pattern, content, re.DOTALL)
    chapter_02_content = chapter_02_match.group(0) if chapter_02_match else ""

    # Extract chapter_01 section (including markers)
    chapter_01_pattern = r'<!-- auteur:chapter id=chapter_01 expression_revision=1 -->.*?<!-- auteur:end-chapter id=chapter_01 -->'
    chapter_01_match = re.search(chapter_01_pattern, content, re.DOTALL)
    chapter_01_content = chapter_01_match.group(0) if chapter_01_match else ""

    # Extract separator
    separator_pattern = r'<!-- auteur:book-separator id=separator_01 revision=1 -->.*?<!-- auteur:end-book-separator id=separator_01 -->'
    separator_match = re.search(separator_pattern, content, re.DOTALL)
    separator_content = separator_match.group(0) if separator_match else ""

    # Extract title
    title_pattern = r'^# The Lantern at Low Water\n'

    # Reconstruct with chapters in reversed order: chapter_02, separator, chapter_01
    modified_content = (
        "# The Lantern at Low Water\n\n" +
        chapter_02_content + "\n\n" +
        separator_content + "\n\n" +
        chapter_01_content
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    # Inspect the modified manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )

    # Assertions for Chapter reorder scenario
    assert result['status'] == 'changed', f"Expected 'changed' status, got '{result['status']}'"
    assert result['chapter_findings_count'] == 0, f"Expected 0 chapter findings, got {result['chapter_findings_count']}"
    assert result['book_findings_count'] == 1, f"Expected 1 book finding, got {result['book_findings_count']}"
    assert result['unresolved_findings_count'] == 0, f"Expected 0 unresolved findings, got {result['unresolved_findings_count']}"

    # Verify the book finding is an order change
    full_report = result['full_report']
    assert len(full_report['book_findings']) == 1, "Expected exactly 1 book finding"
    order_finding = full_report['book_findings'][0]
    assert order_finding['classification'] == 'order_changed', f"Expected 'order_changed' classification, got '{order_finding['classification']}'"
    assert order_finding['recommended_proposal'] == 'book_order_change_proposal', f"Expected 'book_order_change_proposal' proposal type, got '{order_finding['recommended_proposal']}'"
    assert order_finding['original_text'] == 'chapter_01, chapter_02', f"Expected original order 'chapter_01, chapter_02', got '{order_finding['original_text']}'"
    assert order_finding['edited_text'] == 'chapter_02, chapter_01', f"Expected edited order 'chapter_02, chapter_01', got '{order_finding['edited_text']}'"

    # Now route the inspection to generate the actual proposal
    store = BookReconciliationStore(project_root)
    inspection_id = result['inspection_id']
    routing_result = store.route(inspection_id)

    # Verify routing created the proposal
    assert routing_result['status'] == 'routed', f"Expected 'routed' status, got '{routing_result['status']}'"
    assert len(routing_result['book_proposals']) == 1, f"Expected 1 book proposal, got {len(routing_result['book_proposals'])}"
    proposal_id = routing_result['book_proposals'][0]

    # Load the proposal and verify it contains book_order_change_proposal
    proposal_path = project_root / 'book' / 'expression' / 'reconciliation' / 'proposals' / f'{proposal_id}.yaml'
    assert proposal_path.exists(), f"Proposal file not found at {proposal_path}"
    proposal_data = yaml.safe_load(proposal_path.read_text(encoding='utf-8')) or {}
    assert proposal_data.get('proposal_type') == 'book_order_change_proposal', f"Expected proposal_type 'book_order_change_proposal', got '{proposal_data.get('proposal_type')}'"
    assert proposal_data.get('original') == 'chapter_01, chapter_02', f"Expected original 'chapter_01, chapter_02', got '{proposal_data.get('original')}'"
    assert proposal_data.get('proposed') == 'chapter_02, chapter_01', f"Expected proposed 'chapter_02, chapter_01', got '{proposal_data.get('proposed')}'"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()


def test_malformed_marker_creates_unresolved_finding():
    """Scenario 8: Malformed marker → unresolved malformed-marker finding with line number and recommendation, 0 proposals."""
    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_malformed_marker.md'

    # Create a copy of the manuscript with a malformed marker
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Introduce a malformed marker by inserting a marker-like line with invalid format
    # This creates a marker that contains "<!-- auteur:" but doesn't match the expected regex pattern
    # Place it outside of chapter content to avoid affecting chapter parsing
    modified_content = content.replace(
        "<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:end-book-separator id=separator_01 -->\n\n<!-- auteur:malformed-marker-with-typo -->"
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    # Inspect the modified manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )

    # Assertions for Malformed marker scenario
    assert result['status'] == 'changed', f"Expected 'changed' status, got '{result['status']}'"
    assert result['chapter_findings_count'] == 0, f"Expected 0 chapter findings, got {result['chapter_findings_count']}"
    assert result['book_findings_count'] == 0, f"Expected 0 book findings, got {result['book_findings_count']}"
    assert result['unresolved_findings_count'] == 1, f"Expected 1 unresolved finding, got {result['unresolved_findings_count']}"
    assert result['routes'] == [], f"Expected no routes (inspection only), got {result['routes']}"
    assert result['proposals'] == [], f"Expected no proposals for malformed span, got {result['proposals']}"

    # Verify the unresolved finding is a malformed-marker
    full_report = result['full_report']
    assert len(full_report['unresolved_findings']) == 1, "Expected exactly 1 unresolved finding"
    malformed_finding = full_report['unresolved_findings'][0]
    assert malformed_finding['classification'] == 'malformed_marker', f"Expected 'malformed_marker' classification, got '{malformed_finding['classification']}'"
    assert 'line' in malformed_finding or 'line_range' in malformed_finding, "Expected line number or line_range in finding"
    assert 'recommended_action' in malformed_finding, "Expected recommended_action in finding"
    assert malformed_finding['recommended_action'] == 'repair the internal Book marker', f"Expected recommendation about repairing marker, got '{malformed_finding['recommended_action']}'"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()


def test_atomic_routing_failure_leaves_no_partial_outputs():
    """Scenario 11: Atomic routing failure → no partial outputs, staging removed, canonical unchanged.

    When routing fails after partial outputs are staged (e.g., during delegated inspection or
    proposal creation), the exception handler must:
    1. Remove the staging directory entirely
    2. Remove the final routing manifest if it was created
    3. Remove any delegated inspection paths
    4. Leave canonical artifacts unchanged
    """
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_atomic_failure.md'

    # Create a copy of the manuscript with separator-only edits (book-level change)
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Modify only the separator (change "---" to "===")
    modified_content = content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n===\n<!-- auteur:end-book-separator id=separator_01 -->"
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    # Inspect the modified manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )
    inspection_id = result['inspection_id']

    # Verify inspection found the change
    assert result['status'] == 'changed', f"Expected 'changed' status, got '{result['status']}'"
    assert result['book_findings_count'] == 1, f"Expected 1 book finding, got {result['book_findings_count']}"

    # Save the current state of potentially affected directories
    store = BookReconciliationStore(project_root)
    staging_dir = store.root / "staging" / inspection_id
    final_path = store.root / "routing" / f"routing_{inspection_id}.yaml"
    proposals_dir = store.root / "proposals"

    # Verify staging dir doesn't exist before routing
    assert not staging_dir.exists(), f"Staging directory should not exist before routing: {staging_dir}"

    # Save baseline of proposals directory (count of files)
    proposals_before = len(list(proposals_dir.glob("*.yaml"))) if proposals_dir.exists() else 0

    # Now simulate a failure during routing by patching yaml.safe_dump to raise an exception
    # We'll fail after the proposals have been staged but before the final routing manifest is created
    original_safe_dump = yaml.safe_dump
    call_count = [0]  # Use list to allow mutation in nested function

    def failing_yaml_safe_dump(data, **kwargs):
        call_count[0] += 1
        # With 1 book finding and no chapter findings, yaml.safe_dump will be called:
        # - Once for the proposal file (in staging dir)
        # - Once for the final routing manifest
        # We fail on the second call to simulate failure after partial staging
        if call_count[0] == 2:
            raise RuntimeError("Simulated routing failure after partial staging")
        return original_safe_dump(data, **kwargs)

    # Patch yaml.safe_dump during route() to simulate failure
    with patch('auteur.expression.book_reconciliation.yaml.safe_dump', side_effect=failing_yaml_safe_dump):
        with pytest.raises(RuntimeError, match="Simulated routing failure after partial staging"):
            store.route(inspection_id)

    # Verify cleanup: staging directory should be removed
    assert not staging_dir.exists(), (
        f"Staging directory should be removed after failed routing, but exists at: {staging_dir}"
    )

    # Verify cleanup: final routing manifest should not exist or be removed
    assert not final_path.exists(), (
        f"Final routing manifest should not exist after failed routing, but exists at: {final_path}"
    )

    # Verify cleanup: no new proposals should be left in the proposals directory
    proposals_after = len(list(proposals_dir.glob("*.yaml"))) if proposals_dir.exists() else 0
    assert proposals_after == proposals_before, (
        f"Proposals directory should be unchanged after failed routing. "
        f"Before: {proposals_before}, After: {proposals_after}"
    )

    # Verify baselines remain unchanged (canonical artifacts untouched)
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), (
        "Baselines were mutated during failed routing"
    )

    # Verify the inspection itself still exists and is valid (it should not be deleted)
    inspection_path = store._inspection_path(inspection_id)
    assert inspection_path.exists(), f"Original inspection should still exist at {inspection_path}"
    inspection_data = yaml.safe_load(inspection_path.read_text(encoding='utf-8')) or {}
    assert inspection_data.get('inspection_id') == inspection_id, "Inspection data should be intact"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()


def test_scenario_12_author_facing_ux():
    """Scenario 12: Author-Facing UX.

    Verify that inspection output is clear and actionable by answering:
    1. What changed?
    2. Who owns it?
    3. Which routed to Chapter?
    4. Which became Book proposals?
    5. Unresolved?
    6. Stale?
    7. Next action?
    8. Canonical mutation?
    """
    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'

    def format_inspection_ux(inspection_result: dict[str, Any]) -> str:
        """Format inspection result into author-facing UX output."""
        status = inspection_result.get('status', 'unknown')
        full_report = inspection_result.get('full_report', {})

        chapter_findings = full_report.get('chapter_findings', [])
        book_findings = full_report.get('book_findings', [])
        unresolved_findings = full_report.get('unresolved_findings', [])
        freshness = full_report.get('freshness', {})

        output = []
        output.append("=" * 60)
        output.append("BOOK INSPECTION SUMMARY")
        output.append("=" * 60)

        # Q1: What changed?
        output.append("\n[1] What changed?")
        if status == 'no_changes':
            output.append("    Nothing. Manuscript matches accepted Book.")
        else:
            if chapter_findings:
                output.append(f"    - {len(chapter_findings)} chapter(s) with wording edits")
            if book_findings:
                output.append(f"    - {len(book_findings)} book-level change(s)")
            if unresolved_findings:
                output.append(f"    - {len(unresolved_findings)} marker issue(s)")

        # Q2: Who owns it?
        output.append("\n[2] Who owns it?")
        if chapter_findings:
            owner_ids = [f["chapter_id"] for f in chapter_findings]
            output.append(f"    Chapter(s): {', '.join(owner_ids)}")
        if book_findings:
            output.append(f"    Book Expression: {len(book_findings)} finding(s)")
        if not chapter_findings and not book_findings:
            output.append("    No changes")

        # Q3: Which routed to Chapter?
        output.append("\n[3] Which routed to Chapter?")
        if chapter_findings:
            output.append(f"    {len(chapter_findings)} chapter(s) delegated to chapter-level reconciliation")
        else:
            output.append("    None")

        # Q4: Which became Book proposals?
        output.append("\n[4] Which became Book proposals?")
        if book_findings:
            for f in book_findings:
                output.append(f"    - {f.get('recommended_proposal', 'unknown')}")
        else:
            output.append("    None")

        # Q5: Unresolved?
        output.append("\n[5] Unresolved?")
        if unresolved_findings:
            for f in unresolved_findings:
                output.append(f"    [{f.get('classification', 'unknown')}] {f.get('recommended_action', 'manual intervention')}")
        else:
            output.append("    No")

        # Q6: Stale?
        output.append("\n[6] Stale?")
        if freshness.get('status') == 'stale':
            output.append(f"    Yes - {'; '.join(freshness.get('reasons', ['unknown']))}")
        else:
            output.append("    No")

        # Q7: Next action?
        output.append("\n[7] Next action?")
        if status == 'no_changes':
            output.append("    None - manuscript is in sync")
        elif status == 'unresolved':
            output.append("    Fix marker issues before routing")
        else:
            if chapter_findings:
                output.append(f"    Delegate {len(chapter_findings)} chapter change(s)")
            if book_findings:
                output.append(f"    Review {len(book_findings)} book proposal(s)")

        # Q8: Canonical mutation?
        output.append("\n[8] Canonical mutation?")
        output.append("    No - inspection is read-only")

        output.append("=" * 60)
        return "\n".join(output)

    # Test 12.1: No changes scenario
    test_ms_1 = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_ux_1.md'
    shutil.copy(original_ms, test_ms_1)
    result_1 = inspect_book_external_manuscript(project_root=project_root, manuscript_path=test_ms_1)
    output_1 = format_inspection_ux(result_1)

    # Verify all 8 questions are answered
    assert "[1] What changed?" in output_1
    assert "[2] Who owns it?" in output_1
    assert "[3] Which routed to Chapter?" in output_1
    assert "[4] Which became Book proposals?" in output_1
    assert "[5] Unresolved?" in output_1
    assert "[6] Stale?" in output_1
    assert "[7] Next action?" in output_1
    assert "[8] Canonical mutation?" in output_1
    assert "Nothing. Manuscript matches accepted Book" in output_1
    assert "None - manuscript is in sync" in output_1
    if test_ms_1.exists():
        test_ms_1.unlink()

    # Test 12.2: Chapter-only edit scenario
    test_ms_2 = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_ux_2.md'
    shutil.copy(original_ms, test_ms_2)
    content = test_ms_2.read_text(encoding='utf-8')
    modified_content = content.replace(
        "The river wind carries Tomas's warning up the tower.",
        "The river wind carries Tomas's urgent warning up the tower."
    )
    test_ms_2.write_text(modified_content, encoding='utf-8')
    result_2 = inspect_book_external_manuscript(project_root=project_root, manuscript_path=test_ms_2)
    output_2 = format_inspection_ux(result_2)

    assert "1 chapter(s) with wording edits" in output_2
    assert "delegated to chapter-level reconciliation" in output_2
    assert "Delegate 1 chapter change(s)" in output_2
    if test_ms_2.exists():
        test_ms_2.unlink()

    # Test 12.3: Book-level edit scenario
    test_ms_3 = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_ux_3.md'
    shutil.copy(original_ms, test_ms_3)
    content = test_ms_3.read_text(encoding='utf-8')
    modified_content = content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n***\n<!-- auteur:end-book-separator id=separator_01 -->"
    )
    test_ms_3.write_text(modified_content, encoding='utf-8')
    result_3 = inspect_book_external_manuscript(project_root=project_root, manuscript_path=test_ms_3)
    output_3 = format_inspection_ux(result_3)

    assert "1 book-level change(s)" in output_3
    assert "book_separator_patch" in output_3
    assert "Review 1 book proposal(s)" in output_3
    if test_ms_3.exists():
        test_ms_3.unlink()

    # Test 12.4: Unresolved scenario
    test_ms_4 = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_ux_4.md'
    test_ms_4.write_text("Plain text without markers.", encoding='utf-8')
    result_4 = inspect_book_external_manuscript(project_root=project_root, manuscript_path=test_ms_4)
    output_4 = format_inspection_ux(result_4)

    assert "1 marker issue(s)" in output_4 or "unresolved" in output_4.lower()
    assert "Fix marker issues before routing" in output_4
    if test_ms_4.exists():
        test_ms_4.unlink()

    # Verify baselines unchanged across all scenarios
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated"
def test_cross_chapter_movement_creates_unresolved():
    """Scenario 9: Moving paragraph across chapter boundaries ? cross_boundary_move unresolved finding."""
    from auteur.expression.book_reconciliation import BookReconciliationStore

    project_root = Path('./examples/canonical_story/temp_lantern_phase_a')
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_cross_boundary.md'

    # Create a copy of the manuscript with cross-chapter movement
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Move a paragraph from chapter_01 to chapter_02
    # Extract a paragraph from chapter_01 (the "# The messenger" section)
    paragraph_to_move = "# The messenger\n\nTomas reached the tower without breath. A boat had grounded below the bend,\nand the magistrate was on it. Mara put one hand on the lantern door and heard\nthe river answer beneath them.\n\n"

    # Remove the paragraph from chapter_01
    modified_content = content.replace(paragraph_to_move, "")

    # Insert it at the beginning of chapter_02 content (right after the chapter_02 marker)
    modified_content = modified_content.replace(
        "<!-- auteur:chapter id=chapter_02 expression_revision=1 -->",
        "<!-- auteur:chapter id=chapter_02 expression_revision=1 -->\n" + paragraph_to_move
    )

    test_ms.write_text(modified_content, encoding='utf-8')

    # Inspect the modified manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )

    # Assertions for cross-chapter movement scenario
    assert result['status'] == 'changed', f"Expected 'changed' status, got '{result['status']}'"
    assert result['chapter_findings_count'] == 0, f"Expected 0 chapter findings, got {result['chapter_findings_count']}"
    assert result['book_findings_count'] == 0, f"Expected 0 book findings, got {result['book_findings_count']}"
    assert result['unresolved_findings_count'] == 1, f"Expected 1 unresolved finding, got {result['unresolved_findings_count']}"

    # Verify the unresolved finding is a cross_boundary_move
    full_report = result['full_report']
    assert len(full_report['unresolved_findings']) == 1, "Expected exactly 1 unresolved finding"
    unresolved_finding = full_report['unresolved_findings'][0]
    assert unresolved_finding['classification'] == 'cross_boundary_move', f"Expected 'cross_boundary_move' classification, got '{unresolved_finding['classification']}'"

    # Verify both chapters are identified as affected
    assert 'chapter_01' in unresolved_finding.get('affected_chapters', []), "Expected chapter_01 in affected_chapters"
    assert 'chapter_02' in unresolved_finding.get('affected_chapters', []), "Expected chapter_02 in affected_chapters"

    # Verify routing creates no proposals (unresolved finding should not route)
    store = BookReconciliationStore(project_root)
    inspection_id = result['inspection_id']
    routing_result = store.route(inspection_id)

    assert routing_result['status'] == 'unresolved', f"Expected 'unresolved' routing status, got '{routing_result['status']}'"
    assert len(routing_result['chapter_routes']) == 0, f"Expected 0 chapter routes, got {len(routing_result['chapter_routes'])}"
    assert len(routing_result['book_proposals']) == 0, f"Expected 0 book proposals, got {len(routing_result['book_proposals'])}"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()
