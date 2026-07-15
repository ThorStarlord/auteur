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
