"""Tests for versioned contract schemas — serialization, backward compat, validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from auteur.decision.contracts import (
    SCHEMA_VERSION,
    compute_snapshot_id,
    make_acceptance_preparation_fixture,
    make_candidate_fixture,
    make_evidence_fixture,
    make_next_action_fixture,
    make_snapshot_fixture,
    upgrade_if_needed,
    upgrade_v0_to_v1,
    validate_snapshot,
)
from auteur.decision.models import AuthorDecision, DecisionReadiness, DecisionTrigger
from auteur.decision.persistence import DecisionStore


class TestContractSchemas:
    """Test versioned contract schema definitions."""

    def test_snapshot_fixture_defaults(self):
        """Snapshot fixture creates valid v1 snapshot."""
        fixture = make_snapshot_fixture()
        assert fixture["schema_version"] == SCHEMA_VERSION
        assert fixture["decision_id"] == "test-decision-0001"
        assert fixture["snapshot_id"] == "test-snapshot-0001"
        assert fixture["preceding_snapshot_id"] is None
        assert fixture["readiness"] == "needs_candidate"
        assert isinstance(fixture["created_at"], str)

    def test_snapshot_fixture_overrides(self):
        """Snapshot fixture respects overrides."""
        fixture = make_snapshot_fixture(decision_id="custom-dec", readiness="ready_for_acceptance")
        assert fixture["decision_id"] == "custom-dec"
        assert fixture["readiness"] == "ready_for_acceptance"

    def test_evidence_fixture(self):
        """Evidence fixture creates valid evidence dict."""
        ev = make_evidence_fixture()
        assert ev["evidence_id"] == "ev-0001"
        assert ev["source_subsystem"] == "impact"
        assert ev["classification"] == "fact"

    def test_candidate_fixture(self):
        """Candidate fixture creates valid candidate dict."""
        cand = make_candidate_fixture()
        assert cand["candidate_id"] == "cand-0001"
        assert cand["freshness"] == "current"
        assert cand["obligations_satisfied"] == ["ob-001"]

    def test_acceptance_preparation_fixture(self):
        """Acceptance prep fixture creates valid dict."""
        prep = make_acceptance_preparation_fixture()
        assert prep["decision_id"] == "test-decision-0001"
        assert prep["is_ready"] is False
        assert prep["candidate_id"] == "cand-0001"

    def test_next_action_fixture(self):
        """Next action fixture creates valid dict."""
        action = make_next_action_fixture()
        assert action["action_id"] == "generate-candidate"
        assert action["safe_to_execute"] is True

    def test_snapshot_id_computation(self):
        """Snapshot ID is deterministic."""
        sid1 = compute_snapshot_id("dec-1", "2026-07-22T12:00:00")
        sid2 = compute_snapshot_id("dec-1", "2026-07-22T12:00:00")
        assert sid1 == sid2
        assert len(sid1) == 16

    def test_snapshot_id_with_preceding(self):
        """Snapshot ID includes preceding in computation."""
        sid1 = compute_snapshot_id("dec-1", "2026-07-22T12:00:00")
        sid2 = compute_snapshot_id("dec-1", "2026-07-22T12:00:00", "prev-abc")
        assert sid1 != sid2

    def test_snapshot_validation_valid(self):
        """Valid snapshot passes validation."""
        fixture = make_snapshot_fixture()
        issues = validate_snapshot(fixture)
        assert issues == []

    def test_snapshot_validation_missing_field(self):
        """Validation catches missing required fields."""
        issues = validate_snapshot({"schema_version": SCHEMA_VERSION})
        assert len(issues) > 0


class TestBackwardCompatibility:
    """Test backward-compatible loading of v0.7.0 snapshots."""

    def test_upgrade_detects_v0(self):
        """upgrade_if_needed detects and upgrades v0.7.0 snapshot."""
        v0 = {
            "decision_id": "old-dec",
            "project": "/test",
            "chapter_index": 1,
            "target_artifact_id": "t-1",
            "trigger_type": "impact_finding",
            "trigger_ids": [],
            "readiness": "needs_candidate",
            "last_updated_at": "2026-06-15T00:00:00",
            "evidence_count": 3,  # triggers v0 detection heuristic
        }
        result = upgrade_if_needed(v0)
        assert result["schema_version"] == SCHEMA_VERSION
        assert result["evidence"] == []
        assert result["candidates"] == []
    def test_upgrade_passes_v1_through(self):
        """upgrade_if_needed passes v1 unchanged."""
        v1 = make_snapshot_fixture()
        result = upgrade_if_needed(v1)
        assert result["schema_version"] == SCHEMA_VERSION
        assert result["decision_id"] == v1["decision_id"]

    def test_upgrade_adds_missing_fields(self):
        """Upgrade adds safe defaults for missing fields."""
        minimal = {"decision_id": "min", "project": "/t", "chapter_index": 1, "target_artifact_id": "t-1", "readiness": "blocked", "last_updated_at": "2026-06-15T00:00:00"}
        result = upgrade_v0_to_v1(minimal)
        assert result["trigger_type"] == "impact_finding"  # default
        assert result["lifecycle_state"] == "open"
        assert result["freshness"] == "current"
        assert result["authority_required"] == "authority_bearing"

    def test_upgrade_removes_count_keys(self):
        """Upgrade removes legacy evidence_count/candidate_count keys."""
        v0 = {
            "decision_id": "d", "project": "/t", "chapter_index": 1, "target_artifact_id": "t-1",
            "readiness": "needs_candidate", "last_updated_at": "2026-06-15T00:00:00",
            "evidence_count": 3, "candidate_count": 1, "conflict_count": 0, "choice_count": 0,
        }
        result = upgrade_v0_to_v1(v0)
        for key in ("evidence_count", "candidate_count", "conflict_count", "choice_count"):
            assert key not in result

    def test_upgrade_unknown_version(self):
        """Upgrade raises for unrecognized versions."""
        with pytest.raises(ValueError, match="Unrecognized"):
            upgrade_if_needed({"schema_version": "v99"})


class TestSerializationRoundtrip:
    """Test serialization roundtrips through DecisionStore."""

    def test_author_decision_roundtrip(self, tmp_path):
        """AuthorDecision → save → load → verify all fields."""
        store = DecisionStore(tmp_path)
        original = AuthorDecision(
            decision_id="rt-dec",
            project=str(tmp_path),
            chapter_index=2,
            scene_id="scene-02-03",
            target_artifact_id="target-scene-03",
            trigger_type=DecisionTrigger.CONVERGENCE_TARGET,
            readiness=DecisionReadiness.NEEDS_EVALUATION,
        )
        sid = store.save_snapshot(original)
        loaded = store.load_snapshot("rt-dec")
        assert loaded is not None
        assert loaded.decision_id == "rt-dec"
        assert loaded.chapter_index == 2
        assert loaded.scene_id == "scene-02-03"
        assert loaded.trigger_type == DecisionTrigger.CONVERGENCE_TARGET
        assert loaded.readiness == DecisionReadiness.NEEDS_EVALUATION
        assert loaded.schema_version == SCHEMA_VERSION
        assert loaded.snapshot_id == sid
        assert loaded.preceding_snapshot_id is None

    def test_v0_snapshot_loadable(self, tmp_path):
        """v0.7.0 snapshot can be loaded and reconstructed."""
        store = DecisionStore(tmp_path)
        store.snapshots_dir.mkdir(parents=True, exist_ok=True)
        v0_path = store.snapshots_dir / "v0-import.json"
        v0_path.write_text(json.dumps({
            "decision_id": "v0-import",
            "project": "/test",
            "chapter_index": 1,
            "target_artifact_id": "t-1",
            "trigger_type": "impact_finding",
            "trigger_ids": [],
            "readiness": "needs_candidate",
            "last_updated_at": "2026-06-15T00:00:00",
        }))
        loaded = store.load_snapshot("v0-import")
        assert loaded is not None
        assert loaded.decision_id == "v0-import"
        assert loaded.readiness.value == "needs_candidate"
        assert loaded.schema_version == SCHEMA_VERSION

    def test_lineage_roundtrip(self, tmp_path):
        """Multiple snapshots preserve lineage chain."""
        store = DecisionStore(tmp_path)
        d1 = AuthorDecision(decision_id="lineage-dec", project=str(tmp_path), chapter_index=1, target_artifact_id="t-1")
        sid1 = store.save_snapshot(d1)

        d2 = AuthorDecision(decision_id="lineage-dec", project=str(tmp_path), chapter_index=1, target_artifact_id="t-1", readiness="needs_evaluation")
        sid2 = store.save_snapshot(d2, preceding_snapshot_id=sid1)
        assert sid2 != sid1

        d3 = AuthorDecision(decision_id="lineage-dec", project=str(tmp_path), chapter_index=1, target_artifact_id="t-1", readiness="ready_for_acceptance")
        sid3 = store.save_snapshot(d3, preceding_snapshot_id=sid2)
        assert sid3 != sid2

        lineage = store.load_lineage("lineage-dec")
        assert len(lineage) == 3
        assert lineage[0]["snapshot_id"] == sid1
        assert lineage[1]["snapshot_id"] == sid2
        assert lineage[1]["preceding_snapshot_id"] == sid1
        assert lineage[2]["snapshot_id"] == sid3

    def test_serialize_author_decision_full(self, tmp_path):
        """Full serialization preserves evidence, candidates, conflicts."""
        store = DecisionStore(tmp_path)
        from auteur.decision.models import DecisionEvidence, EvidenceClassification, EvidenceFreshness, EvidenceSource, EvidenceType

        evidence = [
            DecisionEvidence.create(
                source_subsystem=EvidenceSource.IMPACT,
                source_artifact_id="finding-1",
                claim="Character state inconsistency",
                evidence_type=EvidenceType.IMPACT_FINDING,
                classification=EvidenceClassification.FACT,
            )
        ]
        decision = AuthorDecision(
            decision_id="full-dec",
            project=str(tmp_path),
            chapter_index=1,
            target_artifact_id="t-1",
            evidence=evidence,
        )
        sid = store.save_snapshot(decision)
        loaded = store.load_snapshot("full-dec")
        assert loaded is not None
        assert len(loaded.evidence) == 1
        assert loaded.evidence[0].claim == "Character state inconsistency"
        assert loaded.evidence[0].source_subsystem == EvidenceSource.IMPACT
