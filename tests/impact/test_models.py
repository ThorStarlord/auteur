"""Tests for impact data models — serialization, roundtrip, enum values."""

from __future__ import annotations

from auteur.impact.models import (
    ArtifactRef,
    ChangeRecord,
    ChangeType,
    DependencyEdge,
    ImpactFinding,
    ImpactSeverity,
    PreservationStatus,
    RepairAction,
    RepairPlan,
)


class TestArtifactRef:
    def test_roundtrip(self) -> None:
        ref = ArtifactRef(
            artifact_id="chapter_03",
            artifact_type="chapter_outline",
            chapter_index=3,
            content_hash="sha256:abc123",
            accepted=True,
        )
        d = ref.to_dict()
        ref2 = ArtifactRef.from_dict(d)
        assert ref2.artifact_id == "chapter_03"
        assert ref2.chapter_index == 3
        assert ref2.accepted is True

    def test_minimal(self) -> None:
        ref = ArtifactRef(artifact_id="test")
        d = ref.to_dict()
        ref2 = ArtifactRef.from_dict(d)
        assert ref2.artifact_id == "test"
        assert ref2.chapter_index is None


class TestDependencyEdge:
    def test_roundtrip(self) -> None:
        edge = DependencyEdge(
            source_id="a",
            target_id="b",
            kind="structural",
            source="inferred",
            fields=("field1", "field2"),
            rule_id="R001",
        )
        d = edge.to_dict()
        edge2 = DependencyEdge.from_dict(d)
        assert edge2.source_id == "a"
        assert edge2.target_id == "b"
        assert edge2.fields == ("field1", "field2")
        assert edge2.rule_id == "R001"

    def test_defaults(self) -> None:
        edge = DependencyEdge(source_id="a", target_id="b")
        d = edge.to_dict()
        edge2 = DependencyEdge.from_dict(d)
        assert edge2.kind == "structural"
        assert edge2.source == "inferred"
        assert edge2.fields == ()


class TestChangeRecord:
    def test_roundtrip(self) -> None:
        ref = ArtifactRef(artifact_id="test", artifact_type="test_type")
        cr = ChangeRecord(
            artifact_ref=ref,
            change_type=ChangeType.CONTENT_CHANGED,
            previous_hash="sha256:old",
            current_hash="sha256:new",
            evidence="hash changed",
        )
        d = cr.to_dict()
        cr2 = ChangeRecord.from_dict(d)
        assert cr2.change_type == ChangeType.CONTENT_CHANGED
        assert cr2.previous_hash == "sha256:old"
        assert cr2.current_hash == "sha256:new"
        assert cr2.artifact_ref is not None
        assert cr2.artifact_ref.artifact_id == "test"

    def test_change_types(self) -> None:
        for ct in ChangeType:
            assert ct.value  # all have values


class TestImpactFinding:
    def test_roundtrip(self) -> None:
        ref = ArtifactRef(artifact_id="target", artifact_type="scene_expression")
        finding = ImpactFinding(
            affected_artifact=ref,
            is_direct=True,
            severity=ImpactSeverity.REGENERATE_CANDIDATE,
            rule_id="R004",
            reason="Realization changed",
            dependency_path=["realization", "expression"],
            preservation=PreservationStatus.REGENERATE,
            recommended_action="Regenerate expression",
            authority_required="candidate_generation",
        )
        d = finding.to_dict()
        finding2 = ImpactFinding.from_dict(d)
        assert finding2.severity == ImpactSeverity.REGENERATE_CANDIDATE
        assert finding2.preservation == PreservationStatus.REGENERATE
        assert finding2.dependency_path == ["realization", "expression"]
        assert finding2.authority_required == "candidate_generation"

    def test_severity_values(self) -> None:
        assert ImpactSeverity.NONE.value == "none"
        assert ImpactSeverity.REVIEW.value == "review"
        assert ImpactSeverity.RECONCILE.value == "reconcile"
        assert ImpactSeverity.REGENERATE_CANDIDATE.value == "regenerate_candidate"
        assert ImpactSeverity.BLOCKED.value == "blocked"

    def test_preservation_values(self) -> None:
        assert PreservationStatus.PRESERVE.value == "preserve"
        assert PreservationStatus.PRESERVE_WITH_REVIEW.value == "preserve_with_review"
        assert PreservationStatus.PARTIAL_PRESERVATION.value == "partial_preservation"
        assert PreservationStatus.REGENERATE.value == "regenerate"
        assert PreservationStatus.UNKNOWN.value == "unknown"


class TestRepairAction:
    def test_roundtrip(self) -> None:
        ref = ArtifactRef(artifact_id="ch1", artifact_type="chapter_expression")
        preserved = [ArtifactRef(artifact_id="ch2_s1", artifact_type="scene_expression")]
        action = RepairAction(
            title="Reconcile chapter 1",
            description="Chapter outline changed",
            affected_artifact=ref,
            command="auteur reconcile ch1",
            authority="candidate_generation",
            safe_to_execute=True,
            blocking=False,
            reason="Outline changed",
            preserved_artifacts=preserved,
        )
        d = action.to_dict()
        action2 = RepairAction.from_dict(d)
        assert action2.title == "Reconcile chapter 1"
        assert action2.command == "auteur reconcile ch1"
        assert action2.safe_to_execute is True
        assert len(action2.preserved_artifacts) == 1
        assert action2.preserved_artifacts[0].artifact_id == "ch2_s1"


class TestRepairPlan:
    def test_roundtrip(self) -> None:
        plan = RepairPlan(
            plan_id="plan_001",
            changes=[ChangeRecord(evidence="test change")],
            findings=[ImpactFinding(reason="test finding")],
            actions=[RepairAction(title="Test action")],
            preserved_artifacts=[ArtifactRef(artifact_id="preserved_art")],
        )
        d = plan.to_dict()
        plan2 = RepairPlan.from_dict(d)
        assert plan2.plan_id == "plan_001"
        assert len(plan2.changes) == 1
        assert len(plan2.findings) == 1
        assert len(plan2.actions) == 1
        assert len(plan2.preserved_artifacts) == 1
        assert plan2.authority == "derived"
        assert plan2.canonical is False
        assert plan2.tool_version == "0.5.0"

    def test_defaults(self) -> None:
        plan = RepairPlan()
        assert plan.authority == "derived"
        assert plan.canonical is False
        assert plan.tool_version == "0.5.0"
