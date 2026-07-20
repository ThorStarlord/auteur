"""Tests for impact workflow integration — impact repair outranks unrelated work."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.impact.analyzer import ImpactAnalyzer
from auteur.impact.models import ImpactSeverity


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


class TestUnresolvedImpact:
    def test_has_unresolved_impact(self) -> None:
        """BLOCKED or RECONCILE impact should be detected as unresolved."""
        from auteur.impact.models import ArtifactRef, ChangeRecord, ImpactFinding
        analyzer = ImpactAnalyzer.__new__(ImpactAnalyzer)
        analyzer.project_root = Path(".")

        findings = [
            ImpactFinding(
                affected_artifact=ArtifactRef(artifact_id="ch1"),
                severity=ImpactSeverity.BLOCKED,
            )
        ]
        assert analyzer.has_unresolved_impact(findings)

    def test_no_unresolved_impact(self) -> None:
        """NONE or REVIEW impact should not be unresolved."""
        from auteur.impact.models import ArtifactRef, ImpactFinding
        analyzer = ImpactAnalyzer.__new__(ImpactAnalyzer)
        analyzer.project_root = Path(".")

        findings = [
            ImpactFinding(
                affected_artifact=ArtifactRef(artifact_id="ch1"),
                severity=ImpactSeverity.NONE,
            ),
            ImpactFinding(
                affected_artifact=ArtifactRef(artifact_id="ch2"),
                severity=ImpactSeverity.REVIEW,
            ),
        ]
        assert not analyzer.has_unresolved_impact(findings)

    def test_workflow_actions_generated(self) -> None:
        """Impact findings should generate workflow-compatible actions."""
        from auteur.impact.models import ArtifactRef, ChangeRecord, ImpactFinding
        analyzer = ImpactAnalyzer.__new__(ImpactAnalyzer)
        analyzer.project_root = Path(".")

        findings = [
            ImpactFinding(
                affected_artifact=ArtifactRef(artifact_id="ch1_expression"),
                severity=ImpactSeverity.REGENERATE_CANDIDATE,
                authority_required="candidate_generation",
                reason="Ch1 outline changed",
            )
        ]
        actions = analyzer.workflow_actions(findings)
        assert len(actions) == 1
        assert actions[0]["authority"] == "candidate_generation"
        assert "impact_finding_id" in actions[0]
        assert actions[0]["auto_executable"] is True

    def test_authority_bearing_actions_not_auto(self) -> None:
        """BLOCKED severity should not be auto-executable."""
        from auteur.impact.models import ArtifactRef, ImpactFinding
        analyzer = ImpactAnalyzer.__new__(ImpactAnalyzer)
        analyzer.project_root = Path(".")

        findings = [
            ImpactFinding(
                affected_artifact=ArtifactRef(artifact_id="book"),
                severity=ImpactSeverity.BLOCKED,
                authority_required="authority_bearing",
            )
        ]
        actions = analyzer.workflow_actions(findings)
        assert len(actions) == 1
        assert actions[0]["auto_executable"] is False

    def test_no_impact_preserves_normal_workflow(self) -> None:
        """With no impact, workflow should behave normally."""
        analyzer = ImpactAnalyzer.__new__(ImpactAnalyzer)
        analyzer.project_root = Path(".")

        actions = analyzer.workflow_actions([])
        assert len(actions) == 0
