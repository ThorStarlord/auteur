"""Tests for Author Decision Workspace."""

import pytest
from pathlib import Path
from datetime import datetime, timezone

from auteur.decision.models import (
    AuthorDecision,
    CandidateSummary,
    DecisionAction,
    DecisionConflict,
    DecisionEvidence,
    DecisionReadiness,
    DecisionTrigger,
    EvidenceClassification,
    EvidenceFreshness,
    EvidenceSource,
    EvidenceType,
    LifecycleState,
    UnresolvedChoice,
)
from auteur.decision.assembler import DecisionAssembler
from auteur.decision.persistence import DecisionStore
from auteur.workflow.models import AuthorityLevel


class TestDecisionModels:
    """Test decision model construction and properties."""

    def test_decision_evidence_create(self):
        """Create decision evidence with factory method."""
        evidence = DecisionEvidence.create(
            source_subsystem=EvidenceSource.CONVERGENCE,
            source_artifact_id="target-123",
            claim="Candidate A is fresh",
            evidence_type=EvidenceType.STRUCTURAL_FACT,
            classification=EvidenceClassification.FACT,
            freshness=EvidenceFreshness.CURRENT,
        )

        assert evidence.evidence_id
        assert evidence.source_subsystem == EvidenceSource.CONVERGENCE
        assert evidence.claim == "Candidate A is fresh"
        assert evidence.classification == EvidenceClassification.FACT
        assert evidence.freshness == EvidenceFreshness.CURRENT
        assert evidence.authority == AuthorityLevel.READ_ONLY

    def test_unresolved_choice_create(self):
        """Create unresolved choice with factory method."""
        choice = UnresolvedChoice.create(
            question="Preserve original ending or rewrite?",
            options=["preserve", "rewrite"],
            affected_candidates=["cand-1", "cand-2"],
            blocking_status=True,
        )

        assert choice.choice_id
        assert choice.question == "Preserve original ending or rewrite?"
        assert choice.options == ["preserve", "rewrite"]
        assert choice.blocking_status is True

    def test_candidate_summary_multidimensional(self):
        """Candidate summary preserves all dimensions."""
        summary = CandidateSummary(
            candidate_id="cand-1",
            status="evaluated",
            freshness=EvidenceFreshness.CURRENT,
            obligations_satisfied=["ob-1", "ob-2"],
            obligations_unsatisfied=["ob-3"],
            preserved_regions=["B01", "B02"],
            continuity_conflicts=["conflict-1"],
        )

        assert summary.candidate_id == "cand-1"
        assert len(summary.obligations_satisfied) == 2
        assert len(summary.obligations_unsatisfied) == 1
        assert "conflict-1" in summary.continuity_conflicts

    def test_author_decision_stale_detection(self):
        """Decision detects stale state."""
        stale_decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            freshness=EvidenceFreshness.STALE,
        )

        assert stale_decision.is_stale() is True

    def test_author_decision_has_open_choices(self):
        """Decision detects open author choices."""
        choice = UnresolvedChoice.create(
            question="Which ending?",
            blocking_status=True,
        )

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            unresolved_choices=[choice],
        )

        assert decision.has_open_choices() is True

    def test_decision_readiness_ready_for_acceptance(self):
        """Decision can be marked ready for acceptance."""
        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            readiness=DecisionReadiness.READY_FOR_ACCEPTANCE,
        )

        assert decision.is_ready_for_acceptance() is True


class TestDecisionAssembler:
    """Test decision assembly from subsystems."""

    def test_compute_decision_id_stable(self):
        """Decision ID is stable and deterministic."""
        assembler = DecisionAssembler(Path("."))

        id1 = assembler.compute_decision_id(
            project="proj",
            trigger_type=DecisionTrigger.IMPACT_FINDING,
            chapter_index=3,
            scene_id="scene_03_04",
            beat_ids=[],
            target_artifact_id="target-1",
            trigger_ids=["impact-1"],
        )

        id2 = assembler.compute_decision_id(
            project="proj",
            trigger_type=DecisionTrigger.IMPACT_FINDING,
            chapter_index=3,
            scene_id="scene_03_04",
            beat_ids=[],
            target_artifact_id="target-1",
            trigger_ids=["impact-1"],
        )

        # Same inputs produce same ID
        assert id1 == id2
        # ID is reasonable length
        assert len(id1) == 16

    def test_compute_decision_id_different_for_different_inputs(self):
        """Decision ID differs for different scenarios."""
        assembler = DecisionAssembler(Path("."))

        id1 = assembler.compute_decision_id(
            project="proj",
            trigger_type=DecisionTrigger.IMPACT_FINDING,
            chapter_index=3,
            scene_id="scene_03_04",
            beat_ids=[],
            target_artifact_id="target-1",
            trigger_ids=["impact-1"],
        )

        id2 = assembler.compute_decision_id(
            project="proj",
            trigger_type=DecisionTrigger.IMPACT_FINDING,
            chapter_index=4,  # Different chapter
            scene_id="scene_03_04",
            beat_ids=[],
            target_artifact_id="target-1",
            trigger_ids=["impact-1"],
        )

        assert id1 != id2

    def test_assemble_from_impact(self):
        """Assemble decision from impact finding."""
        assembler = DecisionAssembler(Path("."))

        decision = assembler.assemble_from_impact(
            project="proj",
            chapter_index=3,
            scene_id="scene_03_04",
            impact_finding_id="impact-1",
            target_artifact_id="target-1",
        )

        assert decision.project == "proj"
        assert decision.chapter_index == 3
        assert decision.scene_id == "scene_03_04"
        assert decision.trigger_type == DecisionTrigger.IMPACT_FINDING
        assert "impact-1" in decision.trigger_ids
        assert decision.readiness == DecisionReadiness.NEEDS_CANDIDATE

    def test_assemble_from_convergence(self):
        """Assemble decision from convergence target."""
        assembler = DecisionAssembler(Path("."))

        decision = assembler.assemble_from_convergence(
            project="proj",
            chapter_index=3,
            scene_id="scene_03_04",
            target_id="target-1",
            target_artifact_id="target-1",
        )

        assert decision.trigger_type == DecisionTrigger.CONVERGENCE_TARGET
        assert "target-1" in decision.trigger_ids

    def test_compute_readiness_no_candidates(self):
        """Readiness is NEEDS_CANDIDATE when no candidates exist."""
        assembler = DecisionAssembler(Path("."))

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            candidates=[],
        )

        readiness = assembler.compute_readiness(decision)
        assert readiness == DecisionReadiness.NEEDS_CANDIDATE

    def test_compute_readiness_needs_evaluation(self):
        """Readiness is NEEDS_EVALUATION when candidate lacks reasoning."""
        assembler = DecisionAssembler(Path("."))

        candidate = CandidateSummary(
            candidate_id="cand-1",
            status="generated",
            freshness=EvidenceFreshness.CURRENT,
            reasoning_evidence=[],  # No reasoning
        )

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            candidates=[candidate],
        )

        readiness = assembler.compute_readiness(decision)
        assert readiness == DecisionReadiness.NEEDS_EVALUATION

    def test_compute_readiness_stale(self):
        """Readiness reflects stale state."""
        assembler = DecisionAssembler(Path("."))

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            freshness=EvidenceFreshness.STALE,
        )

        readiness = assembler.compute_readiness(decision)
        assert readiness == DecisionReadiness.STALE

    def test_detect_freshness_current(self):
        """Freshness is current when no stale evidence."""
        assembler = DecisionAssembler(Path("."))

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            evidence=[
                DecisionEvidence.create(
                    source_subsystem=EvidenceSource.CONVERGENCE,
                    source_artifact_id="target-1",
                    claim="Candidate A is fresh",
                    evidence_type=EvidenceType.STRUCTURAL_FACT,
                    classification=EvidenceClassification.FACT,
                    freshness=EvidenceFreshness.CURRENT,
                )
            ],
        )

        freshness = assembler.detect_freshness(decision)
        assert freshness == EvidenceFreshness.CURRENT

    def test_detect_freshness_stale(self):
        """Freshness detects stale evidence."""
        assembler = DecisionAssembler(Path("."))

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            evidence=[
                DecisionEvidence.create(
                    source_subsystem=EvidenceSource.IMPACT,
                    source_artifact_id="target-1",
                    claim="Impact is stale",
                    evidence_type=EvidenceType.IMPACT_FINDING,
                    classification=EvidenceClassification.FACT,
                    freshness=EvidenceFreshness.STALE,
                )
            ],
        )

        freshness = assembler.detect_freshness(decision)
        assert freshness == EvidenceFreshness.STALE

    def test_derive_lifecycle_state_blocked(self):
        """Lifecycle state is BLOCKED when readiness is blocked."""
        assembler = DecisionAssembler(Path("."))

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            readiness=DecisionReadiness.BLOCKED,
            blockers=["malformed provenance"],
        )

        state = assembler.derive_lifecycle_state(decision)
        assert state == LifecycleState.BLOCKED

    def test_compute_next_action_needs_candidate(self):
        """Recommend candidate generation when needed."""
        assembler = DecisionAssembler(Path("."))

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            scene_id="scene_03_04",
            readiness=DecisionReadiness.NEEDS_CANDIDATE,
        )

        action = assembler.compute_next_action(decision)
        assert action is not None
        assert "generate" in action.title.lower()
        assert action.safe_to_execute is True

    def test_compute_next_action_needs_evaluation(self):
        """Recommend evaluation when needed."""
        assembler = DecisionAssembler(Path("."))

        candidate = CandidateSummary(
            candidate_id="cand-1",
            status="generated",
            freshness=EvidenceFreshness.CURRENT,
        )

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            readiness=DecisionReadiness.NEEDS_EVALUATION,
            candidates=[candidate],
        )

        action = assembler.compute_next_action(decision)
        assert action is not None
        assert "evaluate" in action.title.lower()

    def test_compute_next_action_ready_for_acceptance(self):
        """Recommend acceptance prep when ready."""
        assembler = DecisionAssembler(Path("."))

        candidate = CandidateSummary(
            candidate_id="cand-1",
            status="evaluated",
            freshness=EvidenceFreshness.CURRENT,
        )

        decision = AuthorDecision(
            decision_id="dec-1",
            project=".",
            chapter_index=3,
            target_artifact_id="target-1",
            readiness=DecisionReadiness.READY_FOR_ACCEPTANCE,
            candidates=[candidate],
        )

        action = assembler.compute_next_action(decision)
        assert action is not None
        assert "acceptance" in action.title.lower()
        assert action.safe_to_execute is True


class TestDecisionStore:
    """Test decision persistence."""

    def test_store_init(self, tmp_path):
        """Initialize store with paths."""
        store = DecisionStore(tmp_path)
        assert store.snapshots_dir == tmp_path / ".auteur" / "decisions" / "snapshots"
        assert store.latest_dir == tmp_path / ".auteur" / "decisions" / "latest"

    def test_list_snapshots_empty(self, tmp_path):
        """List snapshots returns empty list when no snapshots exist."""
        store = DecisionStore(tmp_path)
        snapshots = store.list_snapshots()
        assert snapshots == []

    def test_save_snapshot(self, tmp_path):
        """Save decision snapshot."""
        store = DecisionStore(tmp_path)

        decision = AuthorDecision(
            decision_id="dec-1",
            project="proj",
            chapter_index=3,
            target_artifact_id="target-1",
        )

        store.save_snapshot(decision)

        # Verify file was created
        snapshot_path = store.snapshots_dir / "dec-1.json"
        assert snapshot_path.exists()

    def test_list_snapshots_after_save(self, tmp_path):
        """List snapshots after saving."""
        store = DecisionStore(tmp_path)

        decision1 = AuthorDecision(
            decision_id="dec-1",
            project="proj",
            chapter_index=3,
            target_artifact_id="target-1",
        )

        decision2 = AuthorDecision(
            decision_id="dec-2",
            project="proj",
            chapter_index=4,
            target_artifact_id="target-2",
        )

        store.save_snapshot(decision1)
        store.save_snapshot(decision2)

        snapshots = store.list_snapshots()
        assert len(snapshots) == 2
        assert "dec-1" in snapshots
        assert "dec-2" in snapshots

    def test_save_latest_pointer(self, tmp_path):
        """Save latest pointer."""
        store = DecisionStore(tmp_path)

        decision = AuthorDecision(
            decision_id="dec-1",
            project="proj",
            chapter_index=3,
            target_artifact_id="target-1",
            readiness=DecisionReadiness.NEEDS_EVALUATION,
        )

        store.save_latest_pointer(decision)

        # Verify pointer was created
        latest_path = store.latest_dir / "latest.json"
        assert latest_path.exists()

    def test_get_latest_decision_id(self, tmp_path):
        """Retrieve latest decision ID."""
        store = DecisionStore(tmp_path)

        decision = AuthorDecision(
            decision_id="dec-1",
            project="proj",
            chapter_index=3,
            target_artifact_id="target-1",
        )

        store.save_latest_pointer(decision)

        latest_id = store.get_latest_decision_id()
        assert latest_id == "dec-1"

    def test_conflicting_write_rejected(self, tmp_path):
        """Conflicting write is rejected."""
        store = DecisionStore(tmp_path)

        decision1 = AuthorDecision(
            decision_id="dec-1",
            project="proj",
            chapter_index=3,
            target_artifact_id="target-1",
            readiness=DecisionReadiness.NEEDS_CANDIDATE,
        )

        decision2 = AuthorDecision(
            decision_id="dec-1",
            project="proj",
            chapter_index=3,
            target_artifact_id="target-1",
            readiness=DecisionReadiness.READY_FOR_ACCEPTANCE,
            last_updated_at=datetime.now(timezone.utc),
        )

        store.save_snapshot(decision1)

        # Conflicting write should raise
        with pytest.raises(ValueError):
            store.save_snapshot(decision2)


class TestDecisionIntegration:
    """Integration tests for complete decision workflow."""

    def test_impact_triggered_decision_workflow(self, tmp_path):
        """Create decision from impact finding through next action."""
        assembler = DecisionAssembler(tmp_path)

        # Assemble from impact finding
        decision = assembler.assemble_from_impact(
            project="proj",
            chapter_index=3,
            scene_id="scene_03_04",
            impact_finding_id="impact-1",
            target_artifact_id="target-1",
        )

        assert decision.readiness == DecisionReadiness.NEEDS_CANDIDATE

        # Compute next action
        action = assembler.compute_next_action(decision)
        assert action is not None
        assert "generate" in action.title.lower()

        # Persist decision
        store = DecisionStore(tmp_path)
        store.save_snapshot(decision)
        store.save_latest_pointer(decision)

        # Verify retrieval
        snapshot_ids = store.list_snapshots()
        assert "dec" in decision.decision_id or len(snapshot_ids) > 0

    def test_evidence_lifecycle(self):
        """Track evidence through decision."""
        evidence_items = [
            DecisionEvidence.create(
                source_subsystem=EvidenceSource.CONVERGENCE,
                source_artifact_id="target-1",
                claim="Candidate A is fresh",
                evidence_type=EvidenceType.STRUCTURAL_FACT,
                classification=EvidenceClassification.FACT,
                freshness=EvidenceFreshness.CURRENT,
            ),
            DecisionEvidence.create(
                source_subsystem=EvidenceSource.IMPACT,
                source_artifact_id="impact-1",
                claim="Impact finding shows stale dependency",
                evidence_type=EvidenceType.IMPACT_FINDING,
                classification=EvidenceClassification.DERIVED_INFERENCE,
                freshness=EvidenceFreshness.STALE,
            ),
        ]

        decision = AuthorDecision(
            decision_id="dec-1",
            project="proj",
            chapter_index=3,
            target_artifact_id="target-1",
            evidence=evidence_items,
        )

        # Evidence is multidimensional
        assert len(decision.evidence) == 2
        assert decision.evidence[0].classification == EvidenceClassification.FACT
        assert decision.evidence[1].classification == EvidenceClassification.DERIVED_INFERENCE

        # Freshness is detected
        assembler = DecisionAssembler(Path("."))
        freshness = assembler.detect_freshness(decision)
        assert freshness == EvidenceFreshness.STALE
