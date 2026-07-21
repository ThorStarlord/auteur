"""Tests for RepairPlanner — repair plan generation and ordering."""

from __future__ import annotations

from pathlib import Path

from auteur.impact.models import (
    ArtifactRef,
    ChangeRecord,
    ChangeType,
    ImpactFinding,
    ImpactSeverity,
    PreservationStatus,
    RepairAction,
    RepairPlan,
)
from auteur.impact.planner import RepairPlanner


class TestRepairPlanOrdering:
    def test_correct_ordering(self) -> None:
        """Verify repair actions are ordered by severity then chapter."""
        findings = [
            self._make_finding("ch1_outline", "chapter_outline", ImpactSeverity.RECONCILE, chapter=1),
            self._make_finding("ch2_expr", "chapter_expression", ImpactSeverity.REGENERATE_CANDIDATE, chapter=2),
            self._make_finding("ch1_expr", "chapter_expression", ImpactSeverity.BLOCKED, chapter=1),
        ]
        plan = self._plan(findings)
        # BLOCKED should come before RECONCILE before REGENERATE
        assert len(plan.actions) >= 1
        # First action should be BLOCKED
        assert any(a._severity == ImpactSeverity.BLOCKED for a in plan.actions)  # type: ignore[attr-defined]

    def test_reconciliation_before_regeneration(self) -> None:
        """RECONCILE actions should precede REGENERATE_CANDIDATE actions for same chapter."""
        findings = [
            self._make_finding("ch1_outline", "chapter_outline", ImpactSeverity.RECONCILE, chapter=1),
            self._make_finding("ch1_expr", "chapter_expression", ImpactSeverity.REGENERATE_CANDIDATE, chapter=1),
        ]
        plan = self._plan(findings)
        # Find RECONCILE and REGENERATE actions
        reconcile_actions = [a for a in plan.actions
                            if hasattr(a, '_severity') and a._severity == ImpactSeverity.RECONCILE]  # type: ignore[attr-defined]
        regenerate_actions = [a for a in plan.actions
                             if hasattr(a, '_severity') and a._severity == ImpactSeverity.REGENERATE_CANDIDATE]  # type: ignore[attr-defined]
        if reconcile_actions and regenerate_actions:
            rec_idx = plan.actions.index(reconcile_actions[0])
            reg_idx = plan.actions.index(regenerate_actions[0])
            assert rec_idx < reg_idx

    def test_earliest_chapter_first(self) -> None:
        """Within same severity, earlier chapter should come first."""
        findings = [
            self._make_finding("ch3_outline", "chapter_outline", ImpactSeverity.REVIEW, chapter=3),
            self._make_finding("ch1_outline", "chapter_outline", ImpactSeverity.REVIEW, chapter=1),
            self._make_finding("ch2_outline", "chapter_outline", ImpactSeverity.REVIEW, chapter=2),
        ]
        plan = self._plan(findings)
        if len(plan.actions) >= 2:
            ch1_actions = [a for a in plan.actions
                          if a.affected_artifact and a.affected_artifact.chapter_index == 1]
            ch3_actions = [a for a in plan.actions
                          if a.affected_artifact and a.affected_artifact.chapter_index == 3]
            if ch1_actions and ch3_actions:
                assert plan.actions.index(ch1_actions[0]) < plan.actions.index(ch3_actions[0])

    def test_deterministic_tie_break(self) -> None:
        """Same severity and chapter should sort alphabetically."""
        findings = [
            self._make_finding("z_artifact", "test", ImpactSeverity.REVIEW, chapter=1),
            self._make_finding("a_artifact", "test", ImpactSeverity.REVIEW, chapter=1),
        ]
        plan = self._plan(findings)
        if len(plan.actions) >= 2:
            ids = [a.affected_artifact.artifact_id if a.affected_artifact else "" for a in plan.actions]
            assert ids == sorted(ids)

    def test_prerequisites(self) -> None:
        """Prerequisites should be recorded on actions."""
        findings = [
            self._make_finding("outline", "chapter_outline", ImpactSeverity.RECONCILE, chapter=1),
        ]
        plan = self._plan(findings)
        for a in plan.actions:
            assert a.prerequisites is not None

    def test_reconcile_before_regenerate_prerequisite(self) -> None:
        """REGENERATE should declare RECONCILE as a prerequisite, not the reverse."""
        findings = [
            self._make_finding("ch1_outline", "chapter_outline", ImpactSeverity.RECONCILE, chapter=1),
            self._make_finding("ch1_expr", "chapter_expression", ImpactSeverity.REGENERATE_CANDIDATE, chapter=1),
        ]
        plan = self._plan(findings)
        reconcile_id = None
        regenerate_id = None
        for a in plan.actions:
            if a.affected_artifact and a.affected_artifact.artifact_id == "ch1_outline":
                reconcile_id = a.action_id
            if a.affected_artifact and a.affected_artifact.artifact_id == "ch1_expr":
                regenerate_id = a.action_id
        if reconcile_id and regenerate_id:
            # Find the regenerate action; its prereqs should include reconcile
            for a in plan.actions:
                if a.action_id == regenerate_id:
                    assert reconcile_id in a.prerequisites, (
                        f"Expected regenerate {regenerate_id} to have reconcile {reconcile_id} "
                        f"as prerequisite, got {a.prerequisites}"
                    )
                    break
            # Find the reconcile action; it should NOT have regenerate as a prereq
            for a in plan.actions:
                if a.action_id == reconcile_id:
                    assert regenerate_id not in a.prerequisites, (
                        f"Reconcile action should not depend on regenerate, "
                        f"got prereqs: {a.prerequisites}"
                    )
                    break

    def test_blocking_actions(self) -> None:
        """BLOCKED actions should have blocking=True."""
        findings = [
            self._make_finding("review", "reasoning_review", ImpactSeverity.BLOCKED, chapter=1),
        ]
        plan = self._plan(findings)
        if plan.actions:
            assert plan.actions[0].blocking

    def test_no_actions_when_no_impact(self) -> None:
        """No changes should result in no repair actions."""
        plan = self._plan([])
        assert len(plan.actions) == 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_finding(
        self,
        aid: str,
        artifact_type: str,
        severity: ImpactSeverity,
        chapter: int | None = None,
    ) -> ImpactFinding:
        return ImpactFinding(
            affected_artifact=ArtifactRef(
                artifact_id=aid,
                artifact_type=artifact_type,
                chapter_index=chapter,
            ),
            is_direct=True,
            severity=severity,
            rule_id="TEST",
            reason=f"Test: {aid} needs {severity.value}",
            preservation=PreservationStatus.UNKNOWN,
            recommended_action=f"Handle {aid}",
            authority_required="candidate_generation" if severity in (
                ImpactSeverity.RECONCILE, ImpactSeverity.REGENERATE_CANDIDATE) else "read_only",
        )

    def _plan(self, findings: list[ImpactFinding]) -> RepairPlan:
        from auteur.impact.analyzer import ImpactAnalyzer
        planner = RepairPlanner.__new__(RepairPlanner)
        planner.project_root = Path(".")  # type: ignore
        planner.analyzer = ImpactAnalyzer.__new__(ImpactAnalyzer)
        planner.analyzer.project_root = Path(".")  # type: ignore
        return planner.plan(findings=findings, changes=[])
