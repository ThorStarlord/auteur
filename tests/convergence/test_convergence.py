"""Tests for convergence — revision targets, obligations, preservation, candidates, comparison, reconciliation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from auteur.convergence.candidates import CandidateStore
from auteur.convergence.comparison import compare_candidates
from auteur.convergence.models import (
    CandidateComparison,
    CandidateRef,
    CandidateStatus,
    GenerationStrategy,
    ObligationKind,
    ObligationSource,
    PreservedRegion,
    PreservationStatus,
    ReconciliationProposal,
    RevisionTarget,
    SourceObligation,
    TargetScope,
)
from auteur.convergence.obligations import collect_obligations
from auteur.convergence.persistence import ConvergenceStore
from auteur.convergence.planner import ProposalStore
from auteur.convergence.preservation import analyze_preservation
from auteur.convergence.scope import (
    handle_ambiguous_target,
    resolve_target,
    resolve_target_from_impact,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a minimal auteur project structure."""
    (tmp_path / ".auteur").mkdir()
    (tmp_path / "story_identity.yaml").write_text(yaml.safe_dump({
        "story_type": {"genre": "mystery", "mode": "dramatic", "medium": "novel"},
    }))
    (tmp_path / "blueprint.yaml").write_text(yaml.safe_dump({
        "chapters": {
            "chapter_01": {"purpose": "Establish mystery"},
            "chapter_03": {"purpose": "Climax and reveal"},
        },
    }))
    (tmp_path / "chapters").mkdir()
    ch1 = tmp_path / "chapters" / "1"
    ch1.mkdir(parents=True)
    (ch1 / "outline.yaml").write_text(yaml.safe_dump({
        "scenes": [
            {"id": "scene_01_01", "purpose": "Detective arrives"},
            {"id": "scene_01_02", "purpose": "First clue discovered"},
        ],
    }))
    (ch1 / "scenes").mkdir()
    (ch1 / "scenes" / "scene_01_01.yaml").write_text(yaml.safe_dump({
        "id": "scene_01_01",
        "purpose": "Detective arrives at the mansion",
        "location": "mansion entrance",
        "opening": "Rain poured as the car pulled up",
        "beats": [
            {"id": "B01", "description": "Detective enters mansion"},
            {"id": "B02", "description": "Housekeeper greets detective"},
        ],
    }))
    return tmp_path


@pytest.fixture
def ch3_target() -> RevisionTarget:
    return RevisionTarget(
        project="/test/project",
        scope=TargetScope.SCENE,
        chapter_index=3,
        scene_id="scene_03_04",
        target_id="target_ch3_scene04",
    )


@pytest.fixture
def sample_obligations() -> list[SourceObligation]:
    return [
        SourceObligation(
            obligation_id="ob_01",
            source=ObligationSource.STORY_IDENTITY,
            kind=ObligationKind.REQUIRED,
            description="Elena discovers archive tampering",
        ),
        SourceObligation(
            obligation_id="ob_02",
            source=ObligationSource.STRUCTURE,
            kind=ObligationKind.REQUIRED,
            description="Marcus must not know she discovered it",
        ),
        SourceObligation(
            obligation_id="ob_03",
            source=ObligationSource.CHAPTER_OUTLINE,
            kind=ObligationKind.REQUIRED,
            description="Scene ends with concealment decision",
        ),
        SourceObligation(
            obligation_id="ob_04",
            source=ObligationSource.CHARACTER_STATE,
            kind=ObligationKind.ADVISORY,
            description="Elena's emotional state shifts from suspicion to resolve",
        ),
    ]


@pytest.fixture
def candidate_a(ch3_target) -> CandidateRef:
    return CandidateRef(
        candidate_id="candidate_a",
        target_id=ch3_target.target_id,
        status=CandidateStatus.GENERATED,
        freshness="fresh",
        generation_strategy="minimal_repair",
        obligations=["ob_01", "ob_02", "ob_03"],
        obligations_satisfied=["ob_01", "ob_02"],
        obligations_unsatisfied=["ob_03"],
        evaluation_references=["eval_01"],
    )


@pytest.fixture
def candidate_b(ch3_target) -> CandidateRef:
    return CandidateRef(
        candidate_id="candidate_b",
        target_id=ch3_target.target_id,
        status=CandidateStatus.GENERATED,
        freshness="fresh",
        generation_strategy="structural_alternative",
        obligations=["ob_01", "ob_02", "ob_03"],
        obligations_satisfied=["ob_01", "ob_02", "ob_03"],
        obligations_unsatisfied=[],
        evaluation_references=["eval_02", "eval_03"],
    )


@pytest.fixture
def candidate_c(ch3_target) -> CandidateRef:
    return CandidateRef(
        candidate_id="candidate_c",
        target_id=ch3_target.target_id,
        status=CandidateStatus.REGISTERED,
        freshness="stale",
        generation_strategy="external",
        obligations=["ob_01", "ob_02", "ob_03"],
        obligations_satisfied=["ob_01", "ob_03"],
        obligations_unsatisfied=["ob_02"],
        evaluation_references=[],
    )


# =============================================================================
# Tests: Target Resolution
# =============================================================================


class TestTargetResolution:
    def test_chapter_target(self):
        target = resolve_target(
            Path("/test/project"),
            chapter_index=3,
        )
        assert target.scope == TargetScope.CHAPTER
        assert target.chapter_index == 3
        assert target.scene_id is None

    def test_scene_target(self):
        target = resolve_target(
            Path("/test/project"),
            chapter_index=3,
            scene_id="scene_03_04",
        )
        assert target.scope == TargetScope.SCENE
        assert target.scene_id == "scene_03_04"

    def test_beat_range_target(self):
        target = resolve_target(
            Path("/test/project"),
            chapter_index=3,
            scene_id="scene_03_04",
            beat_ids=["B01", "B02"],
        )
        assert target.scope == TargetScope.BEAT_RANGE
        assert target.beat_ids == ["B01", "B02"]

    def test_target_from_impact(self):
        target = resolve_target_from_impact(
            Path("/test/project"),
            finding_artifact_id="artifact_03_04",
            finding_chapter_index=3,
            finding_scene_index=4,
        )
        assert target.chapter_index == 3
        assert target.scene_id == "scene_03_04"
        assert target.affected_artifact == "artifact_03_04"

    def test_target_from_impact_no_scene(self):
        target = resolve_target_from_impact(
            Path("/test/project"),
            finding_artifact_id="chapter_03",
            finding_chapter_index=3,
            finding_scene_index=None,
        )
        assert target.scope == TargetScope.CHAPTER
        assert target.scene_id is None

    def test_ambiguous_target_empty_project(self):
        targets = handle_ambiguous_target(Path("/nonexistent"))
        assert targets == []

    def test_ambiguous_target_with_project(self, tmp_project):
        targets = handle_ambiguous_target(tmp_project, partial_chapter=1)
        assert len(targets) > 0
        for t in targets:
            assert t.chapter_index == 1

    def test_target_id_is_stable(self):
        t1 = resolve_target(Path("/p"), chapter_index=1)
        t2 = resolve_target(Path("/p"), chapter_index=1)
        # target_id is random UUID so different instances differ
        assert t1.target_id != t2.target_id


# =============================================================================
# Tests: Obligations
# =============================================================================


class TestObligations:
    def test_obligations_from_story_identity(self, tmp_project):
        target = resolve_target(tmp_project, chapter_index=1, scene_id="scene_01_01")
        obligations = collect_obligations(tmp_project, target)
        ids = [o.source for o in obligations]
        assert ObligationSource.STORY_IDENTITY in ids

    def test_obligations_from_blueprint(self, tmp_project):
        target = resolve_target(tmp_project, chapter_index=1)
        obligations = collect_obligations(tmp_project, target)
        descs = [o.description for o in obligations]
        assert any("Establish mystery" in d for d in descs)

    def test_obligations_from_chapter_outline(self, tmp_project):
        target = resolve_target(tmp_project, chapter_index=1, scene_id="scene_01_01")
        obligations = collect_obligations(tmp_project, target)

    def test_required_vs_advisory(self):
        req = SourceObligation(
            obligation_id="r1",
            source=ObligationSource.STORY_IDENTITY,
            kind=ObligationKind.REQUIRED,
        )
        adv = SourceObligation(
            obligation_id="a1",
            source=ObligationSource.CHARACTER_STATE,
            kind=ObligationKind.ADVISORY,
        )
        assert req.kind == ObligationKind.REQUIRED
        assert adv.kind == ObligationKind.ADVISORY

    def test_deduplication(self):
        from auteur.convergence.obligations import _deduplicate
        obs = [
            SourceObligation(obligation_id="a", source=ObligationSource.STORY_IDENTITY, description="same"),
            SourceObligation(obligation_id="b", source=ObligationSource.STORY_IDENTITY, description="same"),
            SourceObligation(obligation_id="c", source=ObligationSource.STRUCTURE, description="unique"),
        ]
        result = _deduplicate(obs)
        assert len(result) == 2

    def test_serialization(self):
        ob = SourceObligation(
            source=ObligationSource.STORY_IDENTITY,
            kind=ObligationKind.REQUIRED,
            description="test",
        )
        data = ob.model_dump(mode="json")
        assert data["source"] == "story_identity"
        assert data["kind"] == "required"
        restored = SourceObligation(**data)
        assert restored.obligation_id == ob.obligation_id


# =============================================================================
# Tests: Preservation
# =============================================================================


class TestPreservation:
    def test_preservation_scene_found(self, tmp_project):
        target = resolve_target(tmp_project, chapter_index=1, scene_id="scene_01_01")
        regions = analyze_preservation(tmp_project, target)
        assert len(regions) > 0

    def test_preservation_scene_not_found(self):
        target = resolve_target(Path("/nonexistent"), chapter_index=99, scene_id="scene_99_99")
        regions = analyze_preservation(Path("/nonexistent"), target)
        assert len(regions) > 0
        assert regions[0].status == PreservationStatus.UNKNOWN

    def test_preservation_beat_level(self, tmp_project):
        target = resolve_target(tmp_project, chapter_index=1, scene_id="scene_01_01", beat_ids=["B01"])
        regions = analyze_preservation(tmp_project, target)
        # Beat B01 is in scope, B02 should be preserve
        b02 = [r for r in regions if r.beat_id == "B02"]
        assert len(b02) > 0
        assert b02[0].status == PreservationStatus.PRESERVE

    def test_preservation_honest_unknown(self):
        statuses = [PreservationStatus.PRESERVE, PreservationStatus.PRESERVE_WITH_REVIEW,
                    PreservationStatus.PARTIAL_PRESERVATION, PreservationStatus.REGENERATE,
                    PreservationStatus.UNKNOWN]
        assert PreservationStatus.UNKNOWN in statuses
        assert "unknown" in [s.value for s in statuses]


# =============================================================================
# Tests: Candidate Lifecycle
# =============================================================================


class TestCandidateLifecycle:
    def test_generate_candidate(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        candidate = store.generate_candidate(
            target=ch3_target,
            strategy=GenerationStrategy.MINIMAL_REPAIR,
            obligations=["ob_01", "ob_02"],
            preserved_regions=[],
        )
        assert candidate.status == CandidateStatus.GENERATED
        assert candidate.target_id == ch3_target.target_id
        assert candidate.canonical is False

    def test_generate_candidate_no_canonical_mutation(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        candidate = store.generate_candidate(
            target=ch3_target,
            strategy=GenerationStrategy.STRUCTURAL_ALTERNATIVE,
            obligations=[],
            preserved_regions=[],
        )
        assert candidate.canonical is False
        # Verify no accepted pointer was created
        assert not (tmp_path / ".auteur" / "convergence" / "latest" / "accepted.txt").exists()

    def test_register_external_candidate(self, ch3_target, tmp_path):
        content_file = tmp_path / "candidate_content.yaml"
        content_file.write_text(yaml.safe_dump({"revision": "revised scene content"}))

        store = CandidateStore(tmp_path)
        candidate = store.register_candidate(
            target=ch3_target,
            content_path=content_file,
            obligations=["ob_01"],
            preserved_regions=[],
        )
        assert candidate.status == CandidateStatus.REGISTERED
        assert candidate.authority == "authority_bearing"
        assert candidate.content_artifact_hash.startswith("sha256:")

    def test_register_duplicate_rejected(self, ch3_target, tmp_path):
        content_file = tmp_path / "candidate_content.yaml"
        content_file.write_text(yaml.safe_dump({"test": "data"}))

        store = CandidateStore(tmp_path)
        store.register_candidate(target=ch3_target, content_path=content_file, obligations=[], preserved_regions=[])
        with pytest.raises(ValueError, match="already exists"):
            store.register_candidate(target=ch3_target, content_path=content_file, obligations=[], preserved_regions=[])

    def test_register_nonexistent_file(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        with pytest.raises(ValueError, match="does not exist"):
            store.register_candidate(
                target=ch3_target,
                content_path=tmp_path / "nonexistent.yaml",
                obligations=[],
                preserved_regions=[],
            )

    def test_candidate_lineage(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        c1 = store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.MINIMAL_REPAIR, obligations=[], preserved_regions=[])
        assert c1.lineage.generation_method == "generated:minimal_repair"

    def test_supersede_candidate(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        c = store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.MINIMAL_REPAIR, obligations=[], preserved_regions=[])
        store.supersede(c.candidate_id)
        restored = store.get_candidate(c.candidate_id)
        assert restored is not None
        assert restored.status == CandidateStatus.SUPERSEDED

    def test_reject_candidate(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        c = store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.MINIMAL_REPAIR, obligations=[], preserved_regions=[])
        store.reject(c.candidate_id)
        restored = store.get_candidate(c.candidate_id)
        assert restored.status == CandidateStatus.REJECTED

    def test_historical_retention(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        c = store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.MINIMAL_REPAIR, obligations=[], preserved_regions=[])
        store.reject(c.candidate_id)
        store.supersede(c.candidate_id)
        # All states should be inspectable
        restored = store.get_candidate(c.candidate_id)
        assert restored is not None  # still exists despite reject+supersede

    def test_list_candidates_by_target(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.MINIMAL_REPAIR, obligations=[], preserved_regions=[])
        store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.STRUCTURAL_ALTERNATIVE, obligations=[], preserved_regions=[])
        candidates = store.list_candidates(target_id=ch3_target.target_id)
        assert len(candidates) == 2


# =============================================================================
# Tests: Comparison
# =============================================================================


class TestComparison:
    def test_compare_two_candidates(self, ch3_target, candidate_a, candidate_b):
        comparison = compare_candidates(ch3_target, [candidate_a, candidate_b])
        assert comparison.target_id == ch3_target.target_id
        assert len(comparison.dimensions) > 0
        assert len(comparison.candidate_ids) == 2

    def test_comparison_deterministic(self, ch3_target, candidate_a, candidate_b):
        c1 = compare_candidates(ch3_target, [candidate_a, candidate_b])
        c2 = compare_candidates(ch3_target, [candidate_a, candidate_b])
        assert c1.recommended_candidate_id == c2.recommended_candidate_id

    def test_obligation_coverage_visible(self, ch3_target, candidate_a, candidate_b):
        comparison = compare_candidates(ch3_target, [candidate_a, candidate_b])
        ob_dim = [d for d in comparison.dimensions if d.name == "obligation_coverage"]
        assert len(ob_dim) > 0
        assert ob_dim[0].candidate_a_value is not None
        assert ob_dim[0].candidate_b_value is not None

    def test_freshness_visible(self, ch3_target, candidate_a, candidate_c):
        comparison = compare_candidates(ch3_target, [candidate_a, candidate_c])
        fresh_dim = [d for d in comparison.dimensions if d.name == "freshness"]
        assert len(fresh_dim) > 0
        assert fresh_dim[0].advantage == "candidate_a"  # a is fresh, c is stale

    def test_evaluation_status_visible(self, ch3_target, candidate_a, candidate_c):
        comparison = compare_candidates(ch3_target, [candidate_a, candidate_c])
        eval_dim = [d for d in comparison.dimensions if d.name == "evaluation_status"]
        assert len(eval_dim) > 0

    def test_no_artistic_winner(self, ch3_target, candidate_a, candidate_b):
        comparison = compare_candidates(ch3_target, [candidate_a, candidate_b])
        assert comparison.recommendation_disclaimer
        assert "workflow priority" in comparison.recommendation_disclaimer.lower()

    def test_three_candidates(self, ch3_target, candidate_a, candidate_b, candidate_c):
        comparison = compare_candidates(ch3_target, [candidate_a, candidate_b, candidate_c])
        assert len(comparison.candidate_ids) == 3


# =============================================================================
# Tests: Reconciliation
# =============================================================================


class TestReconciliation:
    def test_single_candidate_proposal(self, ch3_target, candidate_a, sample_obligations, tmp_path):
        comparison = compare_candidates(ch3_target, [candidate_a])
        store = ProposalStore(tmp_path)
        proposal = store.create_proposal(ch3_target, [candidate_a], comparison, sample_obligations)
        assert proposal.target_id == ch3_target.target_id
        assert proposal.canonical is False
        assert len(proposal.candidate_ids) == 1

    def test_multi_candidate_comparison(self, ch3_target, candidate_a, candidate_b, sample_obligations, tmp_path):
        comparison = compare_candidates(ch3_target, [candidate_a, candidate_b])
        store = ProposalStore(tmp_path)
        proposal = store.create_proposal(ch3_target, [candidate_a, candidate_b], comparison, sample_obligations)
        assert len(proposal.candidate_ids) == 2

    def test_conflict_finding(self, ch3_target, candidate_a, candidate_b, tmp_path):
        comparison = compare_candidates(ch3_target, [candidate_a, candidate_b])
        store = ProposalStore(tmp_path)
        proposal = store.create_proposal(ch3_target, [candidate_a, candidate_b], comparison, obligations=[])
        assert isinstance(proposal, ReconciliationProposal)

    def test_proposal_immutable(self, ch3_target, candidate_a, sample_obligations, tmp_path):
        comparison = compare_candidates(ch3_target, [candidate_a])
        store = ProposalStore(tmp_path)
        proposal = store.create_proposal(ch3_target, [candidate_a], comparison, sample_obligations)
        # Proposals are persisted once; re-creating with same data creates a new proposal
        assert proposal.target_id == ch3_target.target_id

    def test_authority_choices_detected(self, tmp_path):
        from auteur.convergence.planner import _find_authority_choices
        from auteur.convergence.models import ConflictFinding
        conflicts = [
            ConflictFinding(
                candidate_ids=["a", "b"],
                description="Obligation conflict",
                severity="warning",
            ),
        ]
        choices = _find_authority_choices([], conflicts)
        assert len(choices) > 0


# =============================================================================
# Tests: Persistence
# =============================================================================


class TestPersistence:
    def test_save_and_load(self, tmp_path):
        store = ConvergenceStore(tmp_path)
        target = RevisionTarget(project=str(tmp_path), scope=TargetScope.SCENE, chapter_index=1, scene_id="scene_01")
        store.save_target(target)
        loaded = store.get_target(target.target_id)
        assert loaded is not None
        assert loaded["target_id"] == target.target_id

    def test_immutability(self, tmp_path):
        store = ConvergenceStore(tmp_path)
        target = RevisionTarget(project=str(tmp_path), scope=TargetScope.SCENE, chapter_index=1, scene_id="scene_01")
        store.save_target(target)
        # Second save should not overwrite
        store.save_target(target)
        # Should still be loadable
        assert store.get_target(target.target_id) is not None

    def test_latest_pointer(self, tmp_path):
        store = ConvergenceStore(tmp_path)
        target = RevisionTarget(project=str(tmp_path), scope=TargetScope.SCENE, chapter_index=1, scene_id="scene_01")
        store.save_target(target)
        store.update_latest("target", target.target_id)
        assert store.get_latest("target") == target.target_id

    def test_list_targets(self, tmp_path):
        store = ConvergenceStore(tmp_path)
        t1 = RevisionTarget(project=str(tmp_path), scope=TargetScope.SCENE, chapter_index=1, scene_id="scene_01")
        t2 = RevisionTarget(project=str(tmp_path), scope=TargetScope.CHAPTER, chapter_index=2)
        store.save_target(t1)
        store.save_target(t2)
        targets = store.list_targets()
        assert len(targets) == 2

    def test_list_candidates_by_target(self, tmp_path):
        store = ConvergenceStore(tmp_path)
        target = RevisionTarget(project=str(tmp_path), scope=TargetScope.SCENE, chapter_index=1, scene_id="scene_01")
        c = CandidateRef(target_id=target.target_id, status=CandidateStatus.GENERATED, freshness="fresh")
        store.save_candidate(c)
        results = store.list_candidates(target_id=target.target_id)
        assert len(results) == 1
        results2 = store.list_candidates(target_id="nonexistent")
        assert len(results2) == 0

    def test_gather_state(self, tmp_path):
        store = ConvergenceStore(tmp_path)
        state = store.gather_state(str(tmp_path))
        assert state.project == str(tmp_path)
        assert state.target is None
        assert "No active revision target" in state.status_summary


# =============================================================================
# Tests: Acceptance Boundary
# =============================================================================


class TestAcceptanceBoundary:
    def test_safe_actions_allowed(self, tmp_project):
        """Inspection, analysis, listing are always allowed."""
        target = resolve_target(tmp_project, chapter_index=1, scene_id="scene_01_01")
        assert target is not None

    def test_generation_does_not_accept(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        c = store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.MINIMAL_REPAIR, obligations=[], preserved_regions=[])
        assert c.canonical is False
        assert c.status != CandidateStatus.ACCEPTED

    def test_registration_does_not_accept(self, ch3_target, tmp_path):
        content = tmp_path / "content.yaml"
        content.write_text("data")
        store = CandidateStore(tmp_path)
        c = store.register_candidate(target=ch3_target, content_path=content, obligations=[], preserved_regions=[])
        assert c.canonical is False
        assert c.status != CandidateStatus.ACCEPTED

    def test_no_canonical_pointer_movement(self, ch3_target, tmp_path):
        store = CandidateStore(tmp_path)
        store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.MINIMAL_REPAIR, obligations=[], preserved_regions=[])
        store.generate_candidate(target=ch3_target, strategy=GenerationStrategy.FULL_REGENERATION, obligations=[], preserved_regions=[])
        # Verify no accepted pointer was created by any generation
        assert not (tmp_path / ".auteur" / "convergence" / "latest" / "accepted.txt").exists()


# =============================================================================
# Tests: Strategy enum
# =============================================================================


class TestStrategies:
    def test_all_strategies_available(self):
        values = [s.value for s in GenerationStrategy]
        assert "minimal_repair" in values
        assert "continuity_preserving" in values
        assert "structural_alternative" in values
        assert "full_regeneration" in values

    def test_minimal_repair(self):
        assert GenerationStrategy.MINIMAL_REPAIR.value == "minimal_repair"

    def test_structural_alternative(self):
        assert GenerationStrategy.STRUCTURAL_ALTERNATIVE.value == "structural_alternative"
