"""Tests for Plan-diff (v0.16.0)."""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.planning.models import (
    ProjectPlan,
    PlanningNode,
    NodeType,
    PlanDependency,
    DependencyType,
    DependencyStrength,
    PlanMilestone,
    PlanningHorizon,
    MilestoneState,
    PlanBlocker,
    CriticalPath,
    PlanAction,
    ActionAuthority,
)
from auteur.planning.differ import diff_plans


def _make_plan(plan_id: str = "plan-a", **kw) -> ProjectPlan:
    return ProjectPlan(
        plan_id=plan_id,
        project="test",
        horizon=PlanningHorizon.PROJECT,
        **kw,
    )


# =========================================================================
# Differ
# =========================================================================


class TestDiffer:

    def test_identical_plans(self):
        a = _make_plan(nodes=[PlanningNode(node_id="n1", node_type=NodeType.DECISION, label="test")])
        result = diff_plans(a, a)
        assert result.has_changes is False

    def test_node_added(self):
        a = _make_plan()
        b = _make_plan(plan_id="plan-b",
                       nodes=[PlanningNode(node_id="n1", node_type=NodeType.DECISION, label="new")])
        result = diff_plans(a, b)
        assert result.has_changes
        assert len(result.nodes.added) == 1

    def test_node_removed(self):
        a = _make_plan(nodes=[PlanningNode(node_id="n1", node_type=NodeType.DECISION, label="gone")])
        b = _make_plan(plan_id="plan-b")
        result = diff_plans(a, b)
        assert result.has_changes
        assert len(result.nodes.removed) == 1

    def test_edge_count(self):
        a = _make_plan(edges=[PlanDependency(
            edge_id="e1", source_id="n1", target_id="n2",
            dependency_type=DependencyType.PREREQUISITE)])
        b = _make_plan(plan_id="plan-b")
        result = diff_plans(a, b)
        assert result.edges_removed == 1

    def test_milestone_state_change(self):
        a = _make_plan(milestones=[PlanMilestone(
            milestone_id="m1", title="test", scope=PlanningHorizon.PROJECT,
            state=MilestoneState.NOT_STARTED)])
        b = _make_plan(plan_id="plan-b", milestones=[PlanMilestone(
            milestone_id="m1", title="test", scope=PlanningHorizon.PROJECT,
            state=MilestoneState.COMPLETED)])
        result = diff_plans(a, b)
        assert len(result.milestones.state_changed) == 1

    def test_blocker_resolved(self):
        a = _make_plan(blockers=[PlanBlocker(
            blocker_id="b1", source_node_id="n1", description="blocked",
            category="missing_prerequisite")])
        b = _make_plan(plan_id="plan-b")
        result = diff_plans(a, b)
        assert len(result.blockers.resolved) == 1

    def test_new_blocker(self):
        a = _make_plan()
        b = _make_plan(plan_id="plan-b", blockers=[PlanBlocker(
            blocker_id="b1", source_node_id="n1", description="new block",
            category="missing_prerequisite")])
        result = diff_plans(a, b)
        assert len(result.blockers.new) == 1

    def test_action_count(self):
        a = _make_plan(authority_required_actions=[PlanAction(
            action_id="a1", title="do", reason="needed",
            authority=ActionAuthority.READ_ONLY)])
        b = _make_plan(plan_id="plan-b")
        result = diff_plans(a, b)
        assert result.actions_removed == 1

    def test_path_count(self):
        a = _make_plan(critical_paths=[CriticalPath(
            path_id="cp1", ordered_node_ids=["n1"], dependency_edges=[],
            blocked_milestone_ids=[], cumulative_leverage=0.8)])
        b = _make_plan(plan_id="plan-b")
        result = diff_plans(a, b)
        assert result.paths_removed == 1


# =========================================================================
# Service
# =========================================================================


class TestServiceDiff:

    def test_diff_requires_first_plan(self, tmp_path):
        from auteur.planning.service import PlanningService
        (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
        svc = PlanningService(tmp_path)
        with pytest.raises(ValueError, match="Plan not found"):
            svc.diff("nonexistent")

    def test_diff_missing_latest(self, tmp_path):
        from auteur.planning.service import PlanningService
        (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
        svc = PlanningService(tmp_path)
        plan = svc.refresh(save=True)
        with pytest.raises(ValueError, match="Plan not found"):
            svc.diff(plan.plan_id, "nonexistent")

    def test_diff_with_latest(self, tmp_path):
        from auteur.planning.service import PlanningService
        (tmp_path / ".auteur").mkdir(parents=True, exist_ok=True)
        svc = PlanningService(tmp_path)
        plan = svc.refresh(save=True)
        result = svc.diff(plan.plan_id)
        assert isinstance(result, dict)
        assert "plan_a_id" in result


# =========================================================================
# CLI
# =========================================================================


class TestCLI:

    def test_plan_diff_help(self):
        from auteur.cli_parser import build_parser
        parser = build_parser()
        with pytest.raises(SystemExit) as exc:
            parser.parse_args(["plan", "diff", "--help"])
        assert exc.value.code == 0

    def test_plan_diff_no_plans(self, tmp_path):
        from auteur.cli import main
        rc = main(["plan", "diff", "nonexistent", "--project", str(tmp_path)])
        assert rc == 1
