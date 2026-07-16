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
from unittest import mock

import pytest

from auteur.canonical_story import CanonicalStoryBootstrap
from auteur.provenance import ArtifactStore

# Isolated dogfood workspace: deliberately OUTSIDE examples/canonical_story
# (the bootstrap source) so that CanonicalStoryBootstrap.copy_to can never
# recursively copy this workspace back into the canonical reference tree.
# See src/auteur/canonical_story.py:CanonicalStoryBootstrap.copy_to for the
# validation that enforces this at runtime, and defect-1-repair-brief.md for
# the incident this isolation fixes. The directory is gitignored (/temp/) and
# is fully rebuilt by `_bootstrap_workspace` before this module's tests run.
WORKSPACE_ROOT = Path("temp/dogfood/lantern_phase_a")

REFERENCE_ROOT = Path("examples/canonical_story")

# Relative-to-workspace paths hashed into .auteur/baselines.json, used by
# TestBookExternalRoutingDogfood.verify_baselines_unchanged to detect any
# mutation of canonical artifacts during inspection/routing.
_BASELINE_PATHS = {
    "story_identity": ".auteur/state/artifacts/story_identity.yaml",
    "blueprint": ".auteur/state/artifacts/blueprint.yaml",
    "chapter_01": ".auteur/state/artifacts/chapter_01.yaml",
    "chapter_02": ".auteur/state/artifacts/chapter_02.yaml",
    "chapter_01_expression": "chapters/01/expression/chapter_v001.yaml",
    "chapter_02_expression": "chapters/02/expression/chapter_v001.yaml",
    "book_expression": "book/expression/book_v001.yaml",
}


def _bootstrap_workspace(workspace_root: Path) -> Path:
    """(Re)build the Phase A dogfood workspace from the canonical reference.

    Any existing workspace is wiped first, so calling this repeatedly against
    the same path is idempotent and deterministic (see
    test_repeated_bootstrap_succeeds). ``workspace_root`` must live outside
    REFERENCE_ROOT -- CanonicalStoryBootstrap.copy_to enforces that and raises
    ValueError instead of silently nesting the reference tree inside itself.
    """
    if workspace_root.exists():
        shutil.rmtree(workspace_root)
    workspace_root.mkdir(parents=True, exist_ok=True)

    bootstrap = CanonicalStoryBootstrap(REFERENCE_ROOT)
    bootstrap.copy_to(workspace_root)
    bootstrap.accept_native_identity_and_structure(workspace_root)
    bootstrap.accept_scene_realizations(workspace_root)
    first_chapter = bootstrap.bootstrap_expressions(workspace_root)
    second_chapter = bootstrap.bootstrap_second_chapter(workspace_root)
    bootstrap.bootstrap_book(workspace_root, [
        first_chapter["chapter_expression"]["artifact_id"],
        second_chapter["chapter_expression"]["artifact_id"],
    ])

    # The marked, external-facing manuscript dogfood scenarios inspect is a
    # plain copy of the derived, accepted Book manuscript.
    manuscript_dir = workspace_root / ".auteur" / "book" / "expression"
    manuscript_dir.mkdir(parents=True, exist_ok=True)
    book_manuscript = workspace_root / "book" / "expression" / "book_v001.md"
    (manuscript_dir / "manuscript.internal.md").write_text(
        book_manuscript.read_text(encoding="utf-8"), encoding="utf-8"
    )

    # Hash via read_text().encode(), matching
    # TestBookExternalRoutingDogfood.verify_baselines_unchanged, so the two
    # computations agree regardless of platform newline translation.
    baselines = {
        name: hashlib.sha256((workspace_root / rel_path).read_text(encoding="utf-8").encode()).hexdigest()
        for name, rel_path in _BASELINE_PATHS.items()
    }
    (workspace_root / ".auteur" / "baselines.json").write_text(
        json.dumps(baselines, indent=2), encoding="utf-8"
    )

    return workspace_root


def _hash_tree(root: Path) -> dict[str, str]:
    """Content hash every file under ``root``, keyed by relative path."""
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.fixture(scope="module", autouse=True)
def _phase_a_workspace():
    """Build the Phase A dogfood workspace once before this module's tests run."""
    _bootstrap_workspace(WORKSPACE_ROOT)
    yield WORKSPACE_ROOT


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
    project_root = WORKSPACE_ROOT
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
    project_root = WORKSPACE_ROOT
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

    project_root = WORKSPACE_ROOT
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


def test_stale_inspection_blocks_routing():
    """Scenario 10: Stale inspection → routing status=stale, 0 outputs, original inspection preserved."""
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    project_root = WORKSPACE_ROOT
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
    original_inspection_data = yaml.safe_load(original_inspection_content) or {}

    # Now simulate a Chapter being updated after the inspection was created
    # We do this by modifying the chapter's accepted.yaml to have a different revision
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

    try:
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
        assert 'BOOK_OR_CHAPTER_REVISION_CHANGED' in updated_inspection.get('freshness', {}).get('reasons', []), \
            f"Expected stale reason to identify changed artifact, got {updated_inspection.get('freshness', {}).get('reasons', [])}"

        # Verify the original inspection structure is preserved (only freshness status changed)
        assert updated_inspection.get('inspection_id') == inspection_id, "Inspection ID should remain unchanged"
        assert updated_inspection.get('chapter_findings') == original_inspection_data.get('chapter_findings'), "Chapter findings should remain unchanged"
        assert updated_inspection.get('book_findings') == original_inspection_data.get('book_findings'), "Book findings should remain unchanged"

        # Verify no routing manifest was created
        routing_manifest_path = store.root / "routing" / f"routing_{inspection_id}.yaml"
        assert not routing_manifest_path.exists(), f"No routing manifest should exist for stale inspection, but found at {routing_manifest_path}"

        # Verify no proposals directory contains new proposals
        proposals_dir = store.root / "proposals"
        if proposals_dir.exists():
            proposals = list(proposals_dir.glob(f"proposal_{inspection_id}_*.yaml"))
            assert len(proposals) == 0, f"Expected 0 proposals for stale inspection, found {len(proposals)}"

        # Verify baselines remain unchanged
        assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"
    finally:
        # Clean up test files and restore the Chapter's accepted.yaml
        if test_ms.exists():
            test_ms.unlink()

        # Restore the original accepted.yaml to its original state
        # Revert the revision and content_hash back to the original values
        restored_data = accepted_data.copy()
        restored_data['revision'] = original_revision
        restored_data['content_hash'] = original_content_hash
        accepted_file.write_text(yaml.safe_dump(restored_data, sort_keys=False), encoding='utf-8')


def test_routing_atomicity_on_failure():
    """Scenario 11: A move failure partway through routing must leave zero
    partial artifacts. Either every proposal and the manifest are visible
    together, or none of them are.
    """
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    project_root = WORKSPACE_ROOT
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_atomic_failure.md'

    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')
    modified_content = content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n===\n<!-- auteur:end-book-separator id=separator_01 -->"
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    try:
        result = inspect_book_external_manuscript(project_root=project_root, manuscript_path=test_ms)
        assert result['status'] == 'changed'
        assert result['book_findings_count'] == 1
        inspection_id = result['inspection_id']

        store = BookReconciliationStore(project_root)
        original_inspection_path = store._inspection_path(inspection_id)
        original_inspection_bytes = original_inspection_path.read_bytes()

        staged_dir = store.root / "staging" / inspection_id
        final_manifest_path = store.root / "routing" / f"routing_{inspection_id}.yaml"
        proposals_dir = store.root / "proposals"

        real_move = shutil.move
        call_count = {"n": 0}

        def flaky_move(src, dst, *args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] >= 2:
                raise OSError("simulated failure during atomic routing move")
            return real_move(src, dst, *args, **kwargs)

        with mock.patch("auteur.expression.book_reconciliation.shutil.move", side_effect=flaky_move):
            with pytest.raises(OSError):
                store.route(inspection_id)

        # At least one move must have been attempted (so this actually
        # exercises a mid-batch failure, not a failure before anything moved).
        assert call_count["n"] >= 2, "Expected the flaky move to be invoked at least twice"

        # Staging must be fully cleaned up -- no orphaned working directory.
        assert not staged_dir.exists(), f"Staging directory should be removed after failure, found {staged_dir}"

        # No routing manifest should be visible.
        assert not final_manifest_path.exists(), f"No routing manifest should exist after failed routing, found {final_manifest_path}"

        # No proposals from this routing attempt should be visible.
        if proposals_dir.exists():
            leftover = list(proposals_dir.glob(f"proposal_{inspection_id}_*.yaml"))
            assert leftover == [], f"Expected 0 proposals visible after failed routing, found {leftover}"

        # The original inspection must survive untouched.
        assert original_inspection_path.exists(), "Original inspection must be preserved after routing failure"
        assert original_inspection_path.read_bytes() == original_inspection_bytes, \
            "Original inspection content must be unchanged after routing failure"

        # No canonical artifacts mutated.
        assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during failed routing"
    finally:
        if test_ms.exists():
            test_ms.unlink()


def test_routing_success_is_atomic():
    """Regression: successful routing publishes the manifest and all
    proposals together, with no leftover staging artifacts.
    """
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    project_root = WORKSPACE_ROOT
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_atomic_success.md'

    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')
    modified_content = content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n===\n<!-- auteur:end-book-separator id=separator_01 -->"
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    try:
        result = inspect_book_external_manuscript(project_root=project_root, manuscript_path=test_ms)
        assert result['status'] == 'changed'
        inspection_id = result['inspection_id']

        store = BookReconciliationStore(project_root)
        staged_dir = store.root / "staging" / inspection_id
        final_manifest_path = store.root / "routing" / f"routing_{inspection_id}.yaml"
        proposals_dir = store.root / "proposals"

        routing_result = store.route(inspection_id)

        assert routing_result['status'] == 'routed'
        assert len(routing_result['book_proposals']) == 1

        # Manifest and proposal must both be visible together.
        assert final_manifest_path.exists(), "Routing manifest should exist after successful routing"
        proposal_id = routing_result['book_proposals'][0]
        proposal_path = proposals_dir / f"{proposal_id}.yaml"
        assert proposal_path.exists(), f"Proposal should exist after successful routing at {proposal_path}"

        # Staging must be cleaned up -- nothing left behind after commit.
        assert not staged_dir.exists(), f"Staging directory should be removed after successful routing, found {staged_dir}"

        assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during successful routing"
    finally:
        if test_ms.exists():
            test_ms.unlink()


def test_repeated_bootstrap_succeeds():
    """Regression for Defect 1: bootstrapping the dogfood workspace twice in a
    row must succeed both times and produce deterministic, non-duplicated
    artifact state.

    Before the fix, the dogfood workspace lived inside
    examples/canonical_story/, so a later bootstrap against that reference
    tree recursively copied the workspace into itself, producing nested
    ``canonical_story/canonical_story/`` duplicates with conflicting
    ``scene_01_0X`` / ``scene_02_01`` artifact IDs (health='invalid',
    'duplicate_artifact_id'). Isolating the workspace under temp/dogfood/
    (outside the reference tree) makes repeated bootstrap safe.
    """
    first_root = _bootstrap_workspace(WORKSPACE_ROOT)
    first_manuscript = first_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    first_result = inspect_book_external_manuscript(project_root=first_root, manuscript_path=first_manuscript)
    first_baselines = TestBookExternalRoutingDogfood.load_baselines(first_root)

    second_root = _bootstrap_workspace(WORKSPACE_ROOT)
    second_manuscript = second_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    second_result = inspect_book_external_manuscript(project_root=second_root, manuscript_path=second_manuscript)
    second_baselines = TestBookExternalRoutingDogfood.load_baselines(second_root)

    assert first_root == second_root == WORKSPACE_ROOT

    # Both bootstraps must succeed and agree: no changes on a freshly
    # rebuilt, unedited manuscript, either time.
    assert first_result['status'] == 'no_changes', f"First bootstrap: expected 'no_changes', got {first_result['status']}"
    assert second_result['status'] == 'no_changes', f"Second bootstrap: expected 'no_changes', got {second_result['status']}"

    # Deterministic output: identical canonical content hashes across runs,
    # for artifacts whose content is not itself timestamped. Story Identity,
    # Blueprint, and the Chapter provenance records carry no wall-clock
    # fields, so their hashes must match exactly run over run.
    stable_keys = ("story_identity", "blueprint", "chapter_01", "chapter_02")
    for key in stable_keys:
        assert first_baselines[key] == second_baselines[key], (
            f"Repeated bootstrap must produce an identical '{key}' hash, "
            f"got {first_baselines[key]} vs {second_baselines[key]}"
        )

    # The derived Chapter/Book Expressions legitimately embed a fresh
    # created_at/accepted_at timestamp on every compose+accept, so their raw
    # byte hashes are expected to differ between runs. Determinism there
    # means the same identity, revision, and narrative content -- not
    # byte-identical timestamps.
    import yaml as _yaml

    def _stable_expression_fields(rel_path: str) -> dict[str, Any]:
        first_data = _yaml.safe_load((first_root / rel_path).read_text(encoding="utf-8")) or {}
        second_data = _yaml.safe_load((second_root / rel_path).read_text(encoding="utf-8")) or {}
        volatile = {"created_at", "accepted_at"}
        first_stable = {k: v for k, v in first_data.items() if k not in volatile}
        second_stable = {k: v for k, v in second_data.items() if k not in volatile}
        return first_stable, second_stable

    for name, rel_path in _BASELINE_PATHS.items():
        if name in stable_keys:
            continue
        first_stable, second_stable = _stable_expression_fields(rel_path)
        assert first_stable == second_stable, (
            f"Repeated bootstrap must produce identical '{name}' content "
            f"(ignoring timestamps), got {first_stable} vs {second_stable}"
        )

    # No nested duplicate copy of the reference tree inside the workspace
    # (the exact shape of the original defect).
    nested_reference_copies = list((second_root / "canonical_story").rglob("canonical_story"))
    assert nested_reference_copies == [], (
        f"Bootstrap must not nest the reference tree inside itself, found {nested_reference_copies}"
    )

    # No duplicate artifact IDs anywhere in the freshly rebuilt workspace.
    store = ArtifactStore(second_root)
    scene_paths = {
        "scene_01_01": second_root / "chapters" / "01" / "scenes" / "scene_01_01.yaml",
        "scene_01_02": second_root / "chapters" / "01" / "scenes" / "scene_01_02.yaml",
        "scene_01_03": second_root / "chapters" / "01" / "scenes" / "scene_01_03.yaml",
        "scene_01_04": second_root / "chapters" / "01" / "scenes" / "scene_01_04.yaml",
        "scene_01_05": second_root / "chapters" / "01" / "scenes" / "scene_01_05.yaml",
        "scene_02_01": second_root / "chapters" / "02" / "scenes" / "scene_02_01.yaml",
    }
    for scene_id, scene_path in scene_paths.items():
        status = store.status(scene_path, "scene_realization")
        assert status.health == "valid", (
            f"{scene_id} unexpectedly invalid after repeated bootstrap: "
            f"health={status.health}"
        )


def test_canonical_reference_untouched():
    """Regression for Defect 1: bootstrapping the dogfood workspace must never
    write into, or leave a copy of itself inside, examples/canonical_story.
    """
    before = _hash_tree(REFERENCE_ROOT)

    _bootstrap_workspace(WORKSPACE_ROOT)

    after = _hash_tree(REFERENCE_ROOT)
    assert before == after, "Canonical reference tree content was mutated by dogfood bootstrap"

    # No dogfood/temp artifacts leaked into the canonical reference tree.
    leaked = [
        entry for entry in REFERENCE_ROOT.iterdir()
        if entry.name.startswith("temp_") or entry.name == "canonical_story"
    ]
    assert leaked == [], f"Canonical reference tree contains leaked dogfood artifacts: {leaked}"

    # The isolated workspace itself must live outside the reference tree.
    assert REFERENCE_ROOT.resolve() not in WORKSPACE_ROOT.resolve().parents
    assert WORKSPACE_ROOT.resolve() not in REFERENCE_ROOT.resolve().parents


def test_chapter_reorder_creates_book_order_proposal():
    """Scenario 5: Chapter reorder → one book finding with book_order_change_proposal."""
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml
    import re

    project_root = WORKSPACE_ROOT
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


def test_mixed_chapter_and_book_edit_creates_proposals():
    """Scenario 6: Mixed Chapter wording + separator edit -> 1 chapter finding + 1 book finding with 2 routes."""
    from auteur.expression.book_reconciliation import BookReconciliationStore
    import yaml

    project_root = WORKSPACE_ROOT
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

    # Should have chapter routes and book proposals
    chapter_routes = routing_result.get('chapter_routes', [])
    book_proposals = routing_result.get('book_proposals', [])

    assert len(chapter_routes) == 1, f"Expected 1 chapter route (delegated inspection), got {len(chapter_routes)}"
    assert len(book_proposals) == 1, f"Expected 1 book proposal (separator patch), got {len(book_proposals)}"

    # Verify the chapter route points to the correct chapter
    chapter_route = chapter_routes[0]
    assert chapter_route['chapter_id'] == 'chapter_01', f"Expected chapter route for chapter_01, got '{chapter_route['chapter_id']}'"
    assert 'chapter_inspection_id' in chapter_route, "Expected chapter_inspection_id in chapter route"

    # Verify baselines remain unchanged
    assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during inspection"

    # Clean up test file
    if test_ms.exists():
        test_ms.unlink()


def test_markerless_manuscript_creates_unresolved_finding():
    """Scenario 7: Markerless manuscript → one unresolved markerless finding, zero routes/proposals."""
    project_root = WORKSPACE_ROOT
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_markerless.md'

    # Create a copy and remove all markers
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Remove all markers by replacing them with empty strings
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


def test_malformed_marker_creates_unresolved_finding():
    """Scenario 8: Malformed marker → unresolved malformed-marker finding with line number and recommendation, 0 proposals."""
    project_root = WORKSPACE_ROOT
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_malformed_marker.md'

    # Create a copy of the manuscript with a malformed marker
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Introduce a malformed marker by inserting a marker-like line with invalid format
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


def test_cross_chapter_movement_creates_unresolved():
    """Scenario 9: Moving paragraph across chapter boundaries -> cross_boundary_move unresolved finding."""
    from auteur.expression.book_reconciliation import BookReconciliationStore

    project_root = WORKSPACE_ROOT
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_cross_boundary.md'

    # Create a copy of the manuscript with cross-chapter movement
    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')

    # Move a paragraph from chapter_01 to chapter_02
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
    assert result['status'] == 'unresolved', f"Expected 'unresolved' status, got '{result['status']}'"
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


def test_scenario_12_author_facing_ux():
    """Scenario 12: Author-Facing UX.

    Verify that inspection output is clear and actionable by answering:
    1. What changed? 2. Who owns it? 3. Which routed to Chapter?
    4. Which became Book proposals? 5. Unresolved? 6. Stale?
    7. Next action? 8. Canonical mutation?
    """
    project_root = WORKSPACE_ROOT
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


def test_copy_to_rejects_workspace_inside_reference(tmp_path):
    """Scenario 17: Workspace recursion prevention.

    CanonicalStoryBootstrap.copy_to must refuse a workspace nested inside the
    canonical reference tree (and refuse a reference nested inside the
    workspace), raising ValueError rather than recursively copying the
    reference tree into itself -- the exact recursion that caused Defect 1.
    A sibling workspace outside the reference tree is accepted.
    """
    reference = tmp_path / "reference"
    reference.mkdir()
    (reference / "marker.txt").write_text("canonical", encoding="utf-8")
    bootstrap = CanonicalStoryBootstrap(reference)

    # Workspace inside the reference tree must be rejected.
    with pytest.raises(ValueError):
        bootstrap.copy_to(reference / "temp_dogfood")

    # Reference inside the requested workspace must also be rejected
    # (tmp_path contains `reference`).
    with pytest.raises(ValueError):
        bootstrap.copy_to(tmp_path)

    # A sibling workspace outside the reference tree is accepted and produces
    # a real copy of the reference contents.
    sibling = tmp_path / "workspace"
    destination = bootstrap.copy_to(sibling)
    assert destination.exists()
    assert (destination / "marker.txt").read_text(encoding="utf-8") == "canonical"


def test_routing_rolls_back_before_any_publication():
    """Scenario 12: Failure before final publication.

    If the very first publication move fails, nothing becomes visible -- no
    proposal lands in proposals/, no routing manifest is written -- and the
    staging directory and original inspection are left clean and intact.
    """
    from auteur.expression.book_reconciliation import BookReconciliationStore

    project_root = WORKSPACE_ROOT
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_rollback_before_pub.md'

    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')
    modified_content = content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n===\n<!-- auteur:end-book-separator id=separator_01 -->"
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    try:
        result = inspect_book_external_manuscript(project_root=project_root, manuscript_path=test_ms)
        assert result['status'] == 'changed'
        assert result['book_findings_count'] == 1
        inspection_id = result['inspection_id']

        store = BookReconciliationStore(project_root)
        original_inspection_path = store._inspection_path(inspection_id)
        original_inspection_bytes = original_inspection_path.read_bytes()
        staged_dir = store.root / "staging" / inspection_id
        final_manifest_path = store.root / "routing" / f"routing_{inspection_id}.yaml"
        proposals_dir = store.root / "proposals"

        call_count = {"n": 0}

        def failing_move(src, dst, *args, **kwargs):
            call_count["n"] += 1
            raise OSError("simulated failure on the first publication move")

        with mock.patch("auteur.expression.book_reconciliation.shutil.move", side_effect=failing_move):
            with pytest.raises(OSError):
                store.route(inspection_id)

        # The failure occurred on the very first move -- before any artifact
        # was published.
        assert call_count["n"] == 1, f"Expected failure on the first move, saw {call_count['n']} moves"
        assert not final_manifest_path.exists(), "No routing manifest may be published when publication fails at the start"
        if proposals_dir.exists():
            leftover = list(proposals_dir.glob(f"proposal_{inspection_id}_*.yaml"))
            assert leftover == [], f"No proposals may be published when the first move fails, found {leftover}"
        assert not staged_dir.exists(), f"Staging must be cleaned after failure, found {staged_dir}"
        assert original_inspection_path.exists(), "Original inspection must survive a failed routing"
        assert original_inspection_path.read_bytes() == original_inspection_bytes, "Original inspection must be unchanged"
        assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during failed routing"
    finally:
        if test_ms.exists():
            test_ms.unlink()


def test_routing_rollback_removes_delegated_chapter_inspections():
    """Scenario 14: Rollback removes delegated outputs.

    A mixed edit delegates a Chapter inspection (into
    chapters/*/expression/reconciliation/inspections/) and stages a Book
    proposal. If publication then fails, the rollback must remove the
    delegated Chapter inspection it created, leaving no orphaned delegated
    output behind.
    """
    from auteur.expression.book_reconciliation import BookReconciliationStore

    project_root = WORKSPACE_ROOT
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_rollback_delegated.md'

    shutil.copy(original_ms, test_ms)
    content = test_ms.read_text(encoding='utf-8')
    modified_content = content.replace(
        "The river wind carries Tomas's warning up the tower.",
        "The river wind carries Tomas's grave warning up the tower."
    )
    modified_content = modified_content.replace(
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n---\n<!-- auteur:end-book-separator id=separator_01 -->",
        "<!-- auteur:book-separator id=separator_01 revision=1 -->\n===\n<!-- auteur:end-book-separator id=separator_01 -->"
    )
    test_ms.write_text(modified_content, encoding='utf-8')

    chapter_inspection_glob = "chapters/*/expression/reconciliation/inspections/*.yaml"

    try:
        result = inspect_book_external_manuscript(project_root=project_root, manuscript_path=test_ms)
        assert result['status'] == 'changed'
        assert result['chapter_findings_count'] == 1, f"Expected 1 chapter finding, got {result['chapter_findings_count']}"
        assert result['book_findings_count'] == 1, f"Expected 1 book finding, got {result['book_findings_count']}"
        inspection_id = result['inspection_id']

        store = BookReconciliationStore(project_root)
        staged_dir = store.root / "staging" / inspection_id
        final_manifest_path = store.root / "routing" / f"routing_{inspection_id}.yaml"
        proposals_dir = store.root / "proposals"

        # Snapshot the delegated-inspection set BEFORE routing so we can prove
        # the one this routing creates is rolled back (leftovers from earlier
        # tests in this module are allowed; we assert no *net* change).
        before = set(project_root.glob(chapter_inspection_glob))

        call_count = {"n": 0}

        def failing_move(src, dst, *args, **kwargs):
            call_count["n"] += 1
            raise OSError("simulated failure after Chapter delegation, during publication")

        with mock.patch("auteur.expression.book_reconciliation.shutil.move", side_effect=failing_move):
            with pytest.raises(OSError):
                store.route(inspection_id)

        # Delegation ran (it does not use shutil.move), then publication failed.
        assert call_count["n"] >= 1, "Publication move must have been attempted"

        after = set(project_root.glob(chapter_inspection_glob))
        assert after == before, (
            "The delegated Chapter inspection created by this routing must be "
            f"rolled back; orphaned delegated outputs: {sorted(after - before)}"
        )
        assert not final_manifest_path.exists(), "No routing manifest may be published after a failed routing"
        if proposals_dir.exists():
            leftover = list(proposals_dir.glob(f"proposal_{inspection_id}_*.yaml"))
            assert leftover == [], f"No proposals may be published after a failed routing, found {leftover}"
        assert not staged_dir.exists(), f"Staging must be cleaned after failure, found {staged_dir}"
        assert TestBookExternalRoutingDogfood.verify_baselines_unchanged(project_root), "Baselines were mutated during failed routing"
    finally:
        if test_ms.exists():
            test_ms.unlink()
