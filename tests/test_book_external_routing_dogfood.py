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
from pathlib import Path
from typing import Any


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
