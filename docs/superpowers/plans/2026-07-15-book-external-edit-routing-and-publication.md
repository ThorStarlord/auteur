# Book External-Edit Routing and Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement Phase A first. Phase B proceeds only if Phase A verdict is "sound."

**Goal:** Dogfood Book external-edit routing (Phase A), then implement Book-owned proposal planning and atomic publication (Phase B).

**Architecture:** Phase A exercises existing read-only Book inspection and routing against 14 dogfood scenarios. Phase B implements: proposal planning → live freshness validation → atomic publication → durable unaccepted candidates. No Chapter ownership is violated.

**Tech Stack:** Python 3.14, pytest, YAML artifact storage, atomic file operations.

## Global Constraints

- Do not modify, stage, delete, or commit `uv.lock`.
- Commit = Phase A passes and Phase B fully implemented.
- Phase B begins only if Phase A verdict is "Book routing is sound; proceed to Book-owned planning and publication."
- All artifacts remain under version control.
- All timestamps use ISO 8601 format.
- Deterministic IDs must match across plan, candidates, and publication manifests.
- No Chapter Structure, Chapter Expression, or upstream narrative mutation allowed.
- Every publication must be live-revalidated immediately before staging.

---

## PHASE A: Book Routing Dogfood and Defect Inventory

### Task A1: Setup canonical project and establish baselines

**Files:**
- Create: `tests/test_book_external_routing_dogfood.py` (framework only, scenarios follow)
- Modify: None yet
- Test: Existing canonical workflow

**Interfaces:**
- Consumes: `examples/canonical_story/` (Story Identity, Blueprint, Chapter Structure, Scene Realizations/Expressions, Chapter Expressions, Book Expression)
- Produces: Baseline hashes for canonical artifacts and temporary project bootstrap

**Steps:**

- [ ] Bootstrap canonical project: `cd examples/canonical_story && python -m auteur expression bootstrap-canonical-project ./temp_lantern_phase_a`

- [ ] Verify temporary project contains all required artifacts:
```bash
cd ./temp_lantern_phase_a
ls -la .auteur/story/identity/.accepted
ls -la .auteur/story/blueprint/.accepted
ls -la .auteur/story/chapters/structure/.accepted
ls -la .auteur/book/expression/.accepted
```

- [ ] Record baseline hashes:
```bash
python -c "
import json
import hashlib
from pathlib import Path

baselines = {}
for artifact_type in ['identity', 'blueprint', 'structure', 'book_expression']:
    path = Path(f'.auteur/story/{artifact_type}/.accepted/.json')
    if path.exists():
        content = path.read_text()
        baselines[artifact_type] = hashlib.sha256(content.encode()).hexdigest()
        
with open('.auteur/baselines.json', 'w') as f:
    json.dump(baselines, f, indent=2)
"
```

- [ ] Commit baselines snapshot
```bash
git add .auteur/baselines.json
git commit -m "test: establish Phase A canonical baselines"
```

---

### Task A2: Test unchanged marked Book (Scenario 2)

**Files:**
- Modify: `tests/test_book_external_routing_dogfood.py`
- Test: Same file

**Interfaces:**
- Consumes: Canonical temporary project from Task A1
- Produces: Test confirming no-changes detection

**Steps:**

- [ ] Write failing test:
```python
def test_unchanged_marked_book_inspection():
    """Scenario 2: Unchanged marked Book should produce no changes, proposals, or findings."""
    project_root = Path('./temp_lantern_phase_a')
    
    # Inspect the unchanged Book manuscript
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    )
    
    assert result['status'] == 'no_changes'
    assert result['chapter_findings_count'] == 0
    assert result['book_findings_count'] == 0
    assert result['unresolved_findings_count'] == 0
    assert result['routes'] == []
    assert result['proposals'] == []
    assert 'No changes detected' in result['message']
    assert 'No canonical artifacts were changed' in result['message']
```

- [ ] Run test (expect FAIL):
```bash
pytest tests/test_book_external_routing_dogfood.py::test_unchanged_marked_book_inspection -v
```

- [ ] Examine existing book inspection logic in `src/auteur/expression/book_reconciliation/inspection.py` (or equivalent).

- [ ] Create wrapper function in `tests/test_book_external_routing_dogfood.py`:
```python
def inspect_book_external_manuscript(project_root, manuscript_path):
    """Wrapper around existing Book inspection. Returns structured result."""
    from auteur.expression.book_reconciliation.inspection import inspect_external_book
    from auteur.story.canonical import load_canonical_story
    
    story = load_canonical_story(project_root)
    inspection = inspect_external_book(
        story=story,
        external_manuscript_path=manuscript_path
    )
    
    return {
        'status': 'no_changes' if not inspection.findings else 'has_changes',
        'chapter_findings_count': sum(1 for f in inspection.findings if f.scope == 'chapter'),
        'book_findings_count': sum(1 for f in inspection.findings if f.scope == 'book'),
        'unresolved_findings_count': sum(1 for f in inspection.findings if f.scope == 'unresolved'),
        'routes': inspection.routes or [],
        'proposals': inspection.proposals or [],
        'message': inspection.summary()
    }
```

- [ ] Verify existing inspection returns appropriate structure. If not, update inspection logic to match test expectations.

- [ ] Run test (expect PASS):
```bash
pytest tests/test_book_external_routing_dogfood.py::test_unchanged_marked_book_inspection -v
```

- [ ] Commit:
```bash
git add tests/test_book_external_routing_dogfood.py
git commit -m "test: scenario 2 - unchanged marked Book produces no changes"
```

---

### Task A3: Test Chapter-only wording edit (Scenario 3)

**Files:**
- Modify: `tests/test_book_external_routing_dogfood.py`

**Steps:**

- [ ] Create a copy of the marked Book manuscript:
```bash
cp .auteur/book/expression/manuscript.internal.md .auteur/book/expression/manuscript.test_chapter_edit.md
```

- [ ] Edit the copy: modify prose inside one Chapter marker region (e.g., find `<!-- CHAPTER id=ch001 -->` and change text within its boundaries).

- [ ] Write test:
```python
def test_chapter_only_edit_creates_delegated_inspection():
    """Scenario 3: Chapter wording edit → one delegated Chapter inspection, zero Book proposals."""
    project_root = Path('./temp_lantern_phase_a')
    
    # Create edited manuscript
    original_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.internal.md'
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_chapter_edit.md'
    shutil.copy(original_ms, test_ms)
    
    # Modify one Chapter region
    content = test_ms.read_text()
    content = content.replace(
        'Chapter 1 original text',
        'Chapter 1 modified text'
    )
    test_ms.write_text(content)
    
    # Inspect and route
    result = inspect_book_external_manuscript(
        project_root=project_root,
        manuscript_path=test_ms
    )
    
    assert result['status'] == 'has_changes'
    assert result['chapter_findings_count'] == 1
    assert result['book_findings_count'] == 0
    assert result['unresolved_findings_count'] == 0
    
    # Verify delegated Chapter inspection is created
    chapter_routes = [r for r in result['routes'] if r.scope == 'chapter']
    assert len(chapter_routes) == 1
    assert chapter_routes[0].target_chapter_id is not None
    
    # Verify no canonical mutation
    verify_baselines_unchanged(project_root)
```

- [ ] Run test (expect to iterate on inspection logic if needed).

- [ ] Commit:
```bash
git add tests/test_book_external_routing_dogfood.py
git commit -m "test: scenario 3 - Chapter-only edit delegates to Chapter reconciliation"
```

---

### Task A4: Test separator-only edit (Scenario 4)

**Files:**
- Modify: `tests/test_book_external_routing_dogfood.py`

**Steps:**

- [ ] Write test:
```python
def test_separator_edit_creates_book_proposal():
    """Scenario 4: Separator edit → one book_separator_patch proposal."""
    project_root = Path('./temp_lantern_phase_a')
    test_ms = project_root / '.auteur' / 'book' / 'expression' / 'manuscript.test_separator_edit.md'
    shutil.copy(original_ms, test_ms)
    
    # Find and modify a separator region (<!-- SEPARATOR id=sep001 -->)
    content = test_ms.read_text()
    content = content.replace(
        '--- Chapter Break ---',
        '=== Modified Break ==='
    )
    test_ms.write_text(content)
    
    result = inspect_book_external_manuscript(project_root, test_ms)
    
    assert result['book_findings_count'] == 1
    assert result['chapter_findings_count'] == 0
    
    proposals = [p for p in result['proposals'] if p.proposal_type == 'book_separator_patch']
    assert len(proposals) == 1
    assert proposals[0].separator_id is not None
    assert proposals[0].original_text is not None
    assert proposals[0].edited_text is not None
    
    verify_baselines_unchanged(project_root)
```

- [ ] Run and commit as above.

---

### Task A5: Test Chapter reorder (Scenario 5)

- [ ] Write test moving complete Chapter sections without text changes. Verify `book_order_change_proposal`, no Chapter mutation.

- [ ] Commit.

---

### Task A6: Test mixed Chapter and Book edit (Scenario 6)

- [ ] Write test with both Chapter wording and separator edit in same inspection. Verify delegated inspection + Book proposal + routing manifest.

- [ ] Commit.

---

### Task A7: Test markerless manuscript (Scenario 7)

- [ ] Create manuscript with all markers removed.
- [ ] Verify `markerless` unresolved finding, zero routes/proposals, actionable recommendation.
- [ ] Commit.

---

### Task A8: Test malformed marker (Scenario 8)

- [ ] Introduce malformed Chapter marker.
- [ ] Verify `malformed_marker` unresolved finding with line number and recommendation.
- [ ] Commit.

---

### Task A9: Test cross-Chapter movement (Scenario 9)

- [ ] Move paragraph from one Chapter into another.
- [ ] Verify `cross_boundary_move` unresolved finding, both Chapters identified.
- [ ] Commit.

---

### Task A10: Test stale inspection (Scenario 10)

- [ ] Create inspection, then accept newer Chapter Expression revision.
- [ ] Verify routing blocked with `stale` status, no outputs created, original inspection preserved.
- [ ] Repeat for Book revision and separator revision changes.
- [ ] Commit.

---

### Task A11: Test atomic routing failure (Scenario 11)

- [ ] Simulate failure after partial outputs staged (e.g., mock filesystem write failure).
- [ ] Verify no final delegated inspection, no Book proposal, no routing manifest, staging directory removed.
- [ ] Commit.

---

### Task A12: Test author-facing UX (Scenario 12)

- [ ] Run inspection on test manuscript variants.
- [ ] Verify default output answers:
  1. What changed?
  2. Who owns each change?
  3. Which routed to Chapter reconciliation?
  4. Which became Book proposals?
  5. Unresolved?
  6. Stale?
  7. Next action?
  8. Canonical mutation?

- [ ] Commit.

---

### Task A13: File and artifact ergonomics (Scenario 13)

- [ ] Inspect Book inspection layout, routing manifest, delegated inspection linkage, proposal readability, artifact count, deterministic IDs, failure cleanup, repeated-run behavior.

- [ ] Classify friction points (missing capability / poor UX / wrong design / terminology / excessive data / weak critic / unnecessary validation / transformation gap).

- [ ] Document findings (not fixes, just findings).

- [ ] Commit.

---

### Task A14: Phase A verification and reporting

- [ ] Run full test suite:
```bash
pytest tests/test_book_reconciliation.py -q
pytest tests/test_expression_book.py -q
pytest tests/test_expression_composition.py -q
pytest tests/test_canonical_story_dogfood.py -q
pytest -q
python -m compileall -q src/auteur
git diff --check
git status --short
```

- [ ] Create Phase A report document: `.superpowers/sdd/phase-a-dogfood-report.md`

Include:
  - Scenario matrix (pass/partial/fail for each of 14 scenarios)
  - Correctness defects (behavioral failures only)
  - UX defects (author-facing friction only)
  - Ownership evidence (Chapter vs. Book routing)
  - Atomicity evidence (failed routing cleanup)
  - Final verdict (choose exactly one):
    1. "Book routing is sound; proceed to Book-owned planning and publication."
    2. "Book routing needs a targeted fix first."
    3. "Book ownership classification requires revision."
    4. "Book routing is not ready for publication mechanics."

- [ ] Commit:
```bash
git add .superpowers/sdd/phase-a-dogfood-report.md
git commit -m "docs: Phase A dogfood report and verdict"
```

---

## PHASE B: Book-Owned Proposal Planning and Publication

**ONLY PROCEED IF PHASE A VERDICT = "Book routing is sound; proceed to Book-owned planning and publication."**

### Task B1: Implement plan schema and models

**Files:**
- Create: `src/auteur/expression/book_reconciliation/models.py`
- Test: `tests/test_book_reconciliation_planning.py`

**Interfaces:**
- Consumes: Existing proposal types from Phase A (book_separator_patch, book_order_change_proposal, etc.)
- Produces: `BookReconciliationPlan`, `BookCandidate`, `BookReconciliationPublication` dataclasses with lifecycle/authority fields

**Steps:**

- [ ] Write failing tests for plan schema:
```python
def test_plan_schema_fields():
    from auteur.expression.book_reconciliation.models import BookReconciliationPlan
    
    plan = BookReconciliationPlan(
        plan_id='plan-001',
        artifact_type='book_reconciliation_plan',
        authority='derived',
        lifecycle='planned',
        source_inspection_id='inspect-001',
        source_book_expression='book-exp-001',
        source_book_revision=3,
        source_book_hash='abc123',
        external_manuscript_hash='def456',
        selected_proposals=[],
        planned_outputs=[],
        conflicts=[],
        readiness={'status': 'ready', 'reasons': []},
        transformation={'id': 'expression.plan_book_reconciliation', 'version': 1},
        created_at='2026-07-15T12:00:00Z'
    )
    
    assert plan.plan_id == 'plan-001'
    assert plan.authority == 'derived'
    assert plan.lifecycle == 'planned'
```

- [ ] Implement models file with dataclasses (use Python's `dataclasses` module).

- [ ] Add validation method:
```python
def validate_plan(plan: BookReconciliationPlan) -> Tuple[bool, List[str]]:
    """Validate plan rejects stale/conflicted/unsupported proposals."""
    errors = []
    
    for proposal in plan.selected_proposals:
        if proposal.lifecycle != 'fresh':
            errors.append(f"Proposal {proposal.proposal_id} is stale")
        if proposal.proposal_type not in ['book_separator_patch', 'book_order_change_proposal', 'book_title_rendering_patch', 'book_inserted_material_proposal']:
            errors.append(f"Unsupported proposal type: {proposal.proposal_type}")
    
    # Check for duplicate incompatible targets
    separator_targets = [p.target_id for p in plan.selected_proposals if p.proposal_type == 'book_separator_patch']
    if len(separator_targets) != len(set(separator_targets)):
        errors.append("Duplicate separator patch targets")
    
    return len(errors) == 0, errors
```

- [ ] Run tests (expect PASS).

- [ ] Commit.

---

### Task B2: Implement plan creation logic

**Files:**
- Create: `src/auteur/expression/book_reconciliation/planning.py`
- Test: `tests/test_book_reconciliation_planning.py`

**Steps:**

- [ ] Write failing test:
```python
def test_create_plan_from_inspection_and_proposals():
    """Plan creation with fresh proposals generates deterministic plan ID and candidate IDs."""
    inspection = load_test_inspection('inspection_with_separator_and_order')
    
    selected_proposal_ids = [
        'proposal-sep-001',
        'proposal-order-001'
    ]
    
    plan = create_book_reconciliation_plan(
        inspection=inspection,
        selected_proposal_ids=selected_proposal_ids,
        project_root=Path('./temp_lantern_phase_b')
    )
    
    assert plan.plan_id is not None
    assert plan.source_inspection_id == inspection.inspection_id
    assert len(plan.selected_proposals) == 2
    assert len(plan.planned_outputs) == 2
    
    # Verify determinism: same inputs → same IDs
    plan2 = create_book_reconciliation_plan(
        inspection=inspection,
        selected_proposal_ids=selected_proposal_ids,
        project_root=Path('./temp_lantern_phase_b')
    )
    assert plan.plan_id == plan2.plan_id
    assert plan.planned_outputs[0].candidate_id == plan2.planned_outputs[0].candidate_id
```

- [ ] Implement `create_book_reconciliation_plan()`:
```python
def create_book_reconciliation_plan(
    inspection,
    selected_proposal_ids,
    project_root
) -> BookReconciliationPlan:
    """Create plan from inspection and selected proposal IDs."""
    from auteur.expression.book_reconciliation.models import BookReconciliationPlan
    import hashlib
    from datetime import datetime
    
    selected_proposals = [p for p in inspection.proposals if p.proposal_id in selected_proposal_ids]
    is_valid, errors = validate_plan_inputs(inspection, selected_proposals)
    if not is_valid:
        raise ValueError(f"Invalid plan inputs: {errors}")
    
    # Generate deterministic plan ID from inputs
    plan_input_hash = hashlib.sha256(
        (inspection.inspection_id + ''.join(selected_proposal_ids)).encode()
    ).hexdigest()[:12]
    plan_id = f"plan-{plan_input_hash}"
    
    # Generate planned outputs (candidates)
    planned_outputs = []
    for i, proposal in enumerate(selected_proposals):
        candidate_hash = hashlib.sha256(
            (plan_id + proposal.proposal_id).encode()
        ).hexdigest()[:12]
        planned_outputs.append({
            'candidate_id': f"cand-{candidate_hash}",
            'candidate_type': proposal.proposal_type.replace('_proposal', '_candidate').replace('_patch', '_candidate'),
            'target_id': proposal.target_id,
            'deterministic_path': f".auteur/book/expression/reconciliation/candidates/{planned_outputs[i]['candidate_id']}.yaml"
        })
    
    plan = BookReconciliationPlan(
        plan_id=plan_id,
        artifact_type='book_reconciliation_plan',
        authority='derived',
        lifecycle='planned',
        source_inspection_id=inspection.inspection_id,
        source_book_expression=inspection.source_book_expression_id,
        source_book_revision=inspection.source_book_revision,
        source_book_hash=inspection.source_book_hash,
        external_manuscript_hash=inspection.external_manuscript_hash,
        selected_proposals=selected_proposals,
        planned_outputs=planned_outputs,
        conflicts=[],
        readiness={'status': 'ready', 'reasons': []},
        transformation={'id': 'expression.plan_book_reconciliation', 'version': 1},
        created_at=datetime.utcnow().isoformat() + 'Z'
    )
    
    return plan
```

- [ ] Run tests (expect PASS).

- [ ] Commit.

---

### Task B3: Implement publication freshness gate

**Files:**
- Create: `src/auteur/expression/book_reconciliation/freshness.py`
- Test: `tests/test_book_reconciliation_publication.py`

**Steps:**

- [ ] Write failing test:
```python
def test_freshness_gate_rejects_stale_plan():
    """Plan that was ready when created is stale at publication time if Book changed."""
    plan = load_test_plan('plan_ready')
    
    # Simulate Book revision change
    book_path = Path('./temp_lantern_phase_b') / '.auteur' / 'book' / 'expression' / '.accepted'
    update_book_expression_revision(book_path, 4)
    
    is_fresh, issues = validate_freshness_at_publication(
        plan=plan,
        project_root=Path('./temp_lantern_phase_b')
    )
    
    assert not is_fresh
    assert any('BOOK_REVISION_CHANGED' in issue for issue in issues)
```

- [ ] Implement `validate_freshness_at_publication()`:
```python
def validate_freshness_at_publication(plan, project_root) -> Tuple[bool, List[str]]:
    """Revalidate all plan dependencies immediately before publication."""
    from auteur.story.canonical import load_canonical_story
    
    story = load_canonical_story(project_root)
    issues = []
    
    # Check Book revision/hash
    current_book = story.get_book_expression(plan.source_book_expression)
    if current_book.revision != plan.source_book_revision:
        issues.append(f"BOOK_REVISION_CHANGED: expected {plan.source_book_revision}, got {current_book.revision}")
    if hashlib.sha256(current_book.to_yaml().encode()).hexdigest() != plan.source_book_hash:
        issues.append(f"BOOK_HASH_CHANGED")
    
    # Check all proposals
    for proposal in plan.selected_proposals:
        if proposal.lifecycle != 'fresh':
            issues.append(f"PROPOSAL_STALE: {proposal.proposal_id}")
    
    # Check Chapter order, separator revisions, external manuscript
    # ... (similar checks)
    
    return len(issues) == 0, issues
```

- [ ] Run tests (expect PASS).

- [ ] Commit.

---

### Task B4: Implement transactional publication

**Files:**
- Create: `src/auteur/expression/book_reconciliation/publication.py`
- Test: `tests/test_book_reconciliation_publication.py`

**Steps:**

- [ ] Write failing test:
```python
def test_publish_plan_creates_candidates_and_preview():
    """Publication creates candidates and preview atomically; all or none visible."""
    plan = load_test_plan('plan_ready')
    is_fresh, _ = validate_freshness_at_publication(plan, Path('./temp_lantern_phase_b'))
    assert is_fresh
    
    publication = publish_book_reconciliation_plan(
        plan=plan,
        project_root=Path('./temp_lantern_phase_b')
    )
    
    assert publication.publication_id is not None
    assert len(publication.published_candidates) == len(plan.selected_proposals)
    assert publication.preview is not None
    assert publication.preview.lifecycle == 'proposed'
    
    # Verify candidates are durable but unaccepted
    for candidate in publication.published_candidates:
        cand_path = Path('./temp_lantern_phase_b') / '.auteur' / 'book' / 'expression' / 'reconciliation' / 'candidates' / f"{candidate.candidate_id}.yaml"
        assert cand_path.exists()
        content = cand_path.read_text()
        assert 'authority: candidate' in content
        assert 'lifecycle: proposed' in content
```

- [ ] Implement `publish_book_reconciliation_plan()`:
```python
def publish_book_reconciliation_plan(plan, project_root) -> BookReconciliationPublication:
    """Publish plan as durable unaccepted candidates + preview. Atomic or rollback."""
    from auteur.expression.book_reconciliation.models import BookReconciliationPublication
    import tempfile
    import shutil
    
    # 1. Validate freshness
    is_fresh, issues = validate_freshness_at_publication(plan, project_root)
    if not is_fresh:
        return BookReconciliationPublication(
            publication_id=None,
            status='rejected_stale',
            reasons=issues,
            visible_outputs_created=False
        )
    
    # 2. Stage outputs to temporary directory
    staging_dir = Path(tempfile.mkdtemp(prefix='book_pub_'))
    try:
        published_candidates = []
        
        for candidate_spec in plan.planned_outputs:
            candidate = create_candidate_from_proposal(
                proposal=next(p for p in plan.selected_proposals if p.proposal_id == candidate_spec.proposal_id),
                plan=plan
            )
            published_candidates.append(candidate)
            
            # Write to staging
            cand_file = staging_dir / f"{candidate.candidate_id}.yaml"
            cand_file.write_text(candidate.to_yaml())
        
        # 3. Create proposed preview
        preview = compose_book_preview(
            plan=plan,
            candidates=published_candidates,
            project_root=project_root
        )
        preview_file = staging_dir / f"preview-{plan.plan_id}.yaml"
        preview_file.write_text(preview.to_yaml())
        
        # 4. Validate staged state
        errors = validate_staged_publication(staged_candidates=published_candidates, preview=preview)
        if errors:
            shutil.rmtree(staging_dir)
            return BookReconciliationPublication(status='validation_failed', reasons=errors)
        
        # 5. Atomic move to final locations
        candidates_dir = project_root / '.auteur' / 'book' / 'expression' / 'reconciliation' / 'candidates'
        candidates_dir.mkdir(parents=True, exist_ok=True)
        
        for cand_file in staging_dir.glob('*.yaml'):
            if 'preview' not in cand_file.name:
                shutil.move(str(cand_file), str(candidates_dir / cand_file.name))
        
        preview_dir = project_root / '.auteur' / 'book' / 'expression' / 'reconciliation' / 'previews'
        preview_dir.mkdir(parents=True, exist_ok=True)
        for preview_file in staging_dir.glob('preview-*.yaml'):
            shutil.move(str(preview_file), str(preview_dir / preview_file.name))
        
        # 6. Create publication manifest
        publication_id = hashlib.sha256(
            (plan.plan_id + str(len(published_candidates))).encode()
        ).hexdigest()[:12]
        
        publication = BookReconciliationPublication(
            publication_id=f"pub-{publication_id}",
            artifact_type='book_reconciliation_publication',
            authority='derived',
            lifecycle='published',
            source_plan_id=plan.plan_id,
            source_inspection_id=plan.source_inspection_id,
            source_book_expression=plan.source_book_expression,
            source_book_revision=plan.source_book_revision,
            source_book_hash=plan.source_book_hash,
            external_manuscript_hash=plan.external_manuscript_hash,
            published_candidates=published_candidates,
            preview=preview,
            transformation={'id': 'expression.publish_book_application', 'version': 1},
            created_at=datetime.utcnow().isoformat() + 'Z',
            freshness={'valid_at_creation': True}
        )
        
        pub_file = project_root / '.auteur' / 'book' / 'expression' / 'reconciliation' / f"{publication.publication_id}.yaml"
        pub_file.parent.mkdir(parents=True, exist_ok=True)
        pub_file.write_text(publication.to_yaml())
        
        shutil.rmtree(staging_dir)
        return publication
        
    except Exception as e:
        # Rollback: remove staging and any partially-created outputs
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        raise
```

- [ ] Run tests (expect PASS).

- [ ] Commit.

---

### Task B5: Implement CLI commands

**Files:**
- Modify: `src/auteur/cli/cli_book_reconciliation.py` (or create if doesn't exist)

**Steps:**

- [ ] Add command:
```bash
auteur expression plan-book-reconciliation <inspection> \
  --proposal <proposal-id> \
  --project PROJECT
```

- [ ] Add command:
```bash
auteur expression show-book-plan <plan> --project PROJECT
```

- [ ] Add command:
```bash
auteur expression publish-book-reconciliation <plan> \
  --project PROJECT
```

- [ ] Add command:
```bash
auteur expression inspect-book-publication <publication> \
  --project PROJECT
```

- [ ] Implement CLI handlers with clear output:
  - Source Book / Book Expression
  - Selected proposals
  - Readiness (ready / stale / conflicted / unsupported)
  - Published candidates (if already published)
  - Preview status
  - Acceptance status: none
  - Canonical pointers changed: no
  - Recommended next action

- [ ] Run manual tests via CLI.

- [ ] Commit.

---

### Task B6: Write comprehensive tests (50+ required tests)

**Files:**
- Create: `tests/test_book_reconciliation_planning.py`
- Create: `tests/test_book_reconciliation_publication.py`

**Steps:**

- [ ] Organize tests into blocks:
  - Planning tests (1-10): Fresh proposals, stale, duplicates, conflicts, determinism
  - Candidate ownership (11-20): Candidates unaccepted, preview non-canonical, authority/lifecycle fields
  - Freshness gate (21-30): Book revision/hash, Chapter order, separator, external manuscript, transformation version
  - Publication atomicity (31-40): All-or-none visibility, failure rollback, staging cleanup
  - Provenance (41-45): ID linkage, inspection→proposal→plan→publication chain
  - Mutation protection (46-50): No Story/Blueprint/Structure/Expression/Chapter mutation
  - Full suite (51-53): Existing tests green, canonical dogfood green

- [ ] Write each test to PASS.

- [ ] Commit per test block (not one commit for all 50).

---

### Task B7: Documentation

**Files:**
- Create: `docs/book-reconciliation-application.md`
- Modify: `docs/book-reconciliation.md`, `docs/book-expression.md`, `docs/capability-coverage.md`, `docs/architecture-product-completion-review.md`, `examples/canonical_story/README.md`

**Steps:**

- [ ] Write `docs/book-reconciliation-application.md` covering:
  - Planning lifecycle
  - Supported proposal types
  - Candidate ownership model
  - Preview semantics
  - Freshness gate
  - Publication atomicity
  - Duplicate and stale handling
  - CLI reference
  - Authority boundaries
  - Explicit non-goals (no acceptance, no Chapter mutation, no reconciliation completion)

- [ ] Update existing docs with pointers and capability updates.

- [ ] Commit.

---

### Task B8: Verification and final commit

**Files:**
- None (tests only)

**Steps:**

- [ ] Run full test suite:
```bash
pytest tests/test_book_reconciliation.py -q
pytest tests/test_book_reconciliation_planning.py -q
pytest tests/test_book_reconciliation_publication.py -q
pytest tests/test_expression_book.py -q
pytest tests/test_expression_composition.py -q
pytest tests/test_canonical_story_dogfood.py -q
pytest -q
python -m compileall -q src/auteur
git diff --check
git status --short
```

- [ ] Verify no `uv.lock` modification:
```bash
git status | grep uv.lock
# Should show only "?? uv.lock"
```

- [ ] Create final commit:
```bash
git add -A
git commit -m "feat: publish Book reconciliation candidates"
```

- [ ] Report:
  - Phase A verdict and scenario matrix
  - Files changed (exact list)
  - Book plan schema (representative YAML)
  - Candidate and preview model (YAML structure)
  - Freshness gate (revalidation checklist)
  - Atomicity evidence (failure scenario walkthrough)
  - CLI examples (sample output)
  - Authority evidence (pointers unchanged)
  - Verification (test counts, compile result, diff result)
  - Final commit SHA
  - Repository state (worktree clean, uv.lock untouched)

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-15-book-external-edit-routing-and-publication.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per Phase-A task, review between tasks, proceed to Phase B only if Phase A passes.

**2. Inline Execution** — Execute tasks in this session using superpowers:executing-plans, with checkpoints between Phase A completion and Phase B start.

Which approach?
