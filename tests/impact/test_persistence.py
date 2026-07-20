"""Tests for ImpactStore — persistence, immutability, latest pointer."""

from __future__ import annotations

from pathlib import Path

import pytest

from auteur.impact.models import RepairPlan
from auteur.impact.persistence import ImpactStore


@pytest.fixture
def impact_store(tmp_path: Path) -> ImpactStore:
    root = tmp_path / "project"
    (root / ".auteur").mkdir(parents=True)
    return ImpactStore(root)


class TestSaveAndLoad:
    def test_save_analysis(self, impact_store: ImpactStore) -> None:
        aid = impact_store.save_analysis({"analysis_id": "test001", "data": "test"})
        assert aid == "test001"

    def test_load_latest_analysis(self, impact_store: ImpactStore) -> None:
        impact_store.save_analysis({"analysis_id": "test001", "data": "hello"})
        loaded = impact_store.load_latest_analysis()
        assert loaded is not None
        assert loaded["analysis_id"] == "test001"
        assert loaded["data"] == "hello"

    def test_save_plan(self, impact_store: ImpactStore) -> None:
        plan = RepairPlan(plan_id="plan001")
        pid = impact_store.save_plan(plan)
        assert pid == "plan001"

    def test_load_latest_plan(self, impact_store: ImpactStore) -> None:
        plan = RepairPlan(plan_id="plan001", changes=[], findings=[], actions=[])
        impact_store.save_plan(plan)
        loaded = impact_store.load_latest_plan()
        assert loaded is not None
        assert loaded.plan_id == "plan001"

    def test_immutable_historical_analysis(self, impact_store: ImpactStore) -> None:
        """Historical analyses must not be overwritten."""
        impact_store.save_analysis({"analysis_id": "first", "value": 1})
        impact_store.save_analysis({"analysis_id": "first", "value": 2})  # same ID — should not overwrite
        loaded = impact_store.load_latest_analysis()
        assert loaded["value"] == 1  # original preserved

    def test_latest_pointer_update(self, impact_store: ImpactStore) -> None:
        impact_store.save_analysis({"analysis_id": "v1"})
        impact_store.save_analysis({"analysis_id": "v2"})
        latest = impact_store._read_latest()
        assert latest.get("latest_analysis_id") == "v2"

    def test_list_analyses(self, impact_store: ImpactStore) -> None:
        impact_store.save_analysis({"analysis_id": "a1"})
        impact_store.save_analysis({"analysis_id": "a2"})
        analyses = impact_store.list_analyses()
        assert "a1" in analyses
        assert "a2" in analyses

    def test_list_plans(self, impact_store: ImpactStore) -> None:
        plan1 = RepairPlan(plan_id="p1")
        plan2 = RepairPlan(plan_id="p2")
        impact_store.save_plan(plan1)
        impact_store.save_plan(plan2)
        plans = impact_store.list_plans()
        assert "p1" in plans
        assert "p2" in plans

    def test_no_data_returns_none(self, impact_store: ImpactStore) -> None:
        assert impact_store.load_latest_analysis() is None
        assert impact_store.load_latest_plan() is None

    def test_has_any(self, impact_store: ImpactStore) -> None:
        assert not impact_store.has_any()
        impact_store.save_analysis({"analysis_id": "a1"})
        assert impact_store.has_any()

    def test_old_reports_remain_readable(self, impact_store: ImpactStore) -> None:
        impact_store.save_analysis({"analysis_id": "old", "data": "original"})
        impact_store.save_analysis({"analysis_id": "new", "data": "updated"})
        # Old should still be readable from its file
        old_path = impact_store.analyses_dir / "old.json"
        assert old_path.exists()
        import json
        data = json.loads(old_path.read_text(encoding="utf-8"))
        assert data["data"] == "original"
