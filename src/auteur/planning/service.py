"""Planning service — application-service boundary used by CLI and workflow."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from auteur.planning.models import (
    PlanningHorizon,
    ProjectPlan,
)
from auteur.planning.assembler import PlanAssembler
from auteur.planning.planner import Planner
from auteur.planning.persistence import PlanStore
from auteur.planning.milestones import MilestoneEngine

logger = logging.getLogger(__name__)


class PlanningService:
    """Application-service boundary for project-level planning.

    Composes real state from DecisionWorkspaceService, ReviewService, and
    other subsystems to produce deterministic project plans.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self._validate_project()
        self.assembler = PlanAssembler(self.project_root)
        self.planner = Planner(self.project_root)
        self.milestone_engine = MilestoneEngine(self.project_root)
        self.store = PlanStore(self.project_root)

    def _validate_project(self) -> None:
        """Verify this is a valid Auteur project."""
        marker = self.project_root / ".auteur"
        if not marker.exists():
            raise ValueError(f"Not an Auteur project (no .auteur directory): {self.project_root}")

    # ------------------------------------------------------------------
    # Main plan operations
    # ------------------------------------------------------------------

    def status(
        self,
        horizon: PlanningHorizon = PlanningHorizon.PROJECT,
        chapter_index: int | None = None,
    ) -> dict[str, Any]:
        """Get project plan status summary."""
        try:
            # Load latest plan info for quick status
            latest = self.store.load_latest_info()
            if latest:
                return {
                    "has_plan": True,
                    "plan_id": latest.get("plan_id", ""),
                    "created_at": latest.get("created_at", ""),
                    "open_decision_count": latest.get("open_decision_count", 0),
                    "active_review_session_count": latest.get("active_review_session_count", 0),
                    "blocked_milestone_count": latest.get("blocked_milestone_count", 0),
                    "is_stale": latest.get("is_stale", False),
                    "stale_reason": latest.get("stale_reason", ""),
                    "horizon": latest.get("horizon", "project"),
                    "title": latest.get("title", ""),
                }
            return {"has_plan": False, "message": "No plan has been created yet. Run 'auteur plan refresh' to create one."}
        except Exception as e:
            logger.exception("Error getting plan status")
            return {"has_plan": False, "error": str(e)}

    def refresh(
        self,
        horizon: PlanningHorizon = PlanningHorizon.PROJECT,
        chapter_index: int | None = None,
        save: bool = True,
    ) -> ProjectPlan:
        """Create a fresh project plan from current state.

        Args:
            horizon: Planning horizon scope.
            chapter_index: Chapter filter for scoped plans.
            save: Whether to persist the plan snapshot.

        Returns:
            A new ProjectPlan.
        """
        # Load real state
        decisions = self._load_decisions()
        sessions = self._load_sessions()
        status_data = self.assembler.load_status()

        # Assemble graph
        graph, nodes, edges, raw_sessions = self.assembler.assemble(
            decisions=decisions,
            sessions=sessions,
            status_data=status_data,
            horizon=horizon,
            chapter_index=chapter_index,
        )

        # Derive milestones
        milestones = self.milestone_engine.derive_milestones(
            status_data=status_data,
            chapters=[chapter_index] if chapter_index else None,
        )

        # Load previous plan for history comparison
        prev_plan = self.store.load_latest()

        # Create plan
        plan = self.planner.create_plan(
            graph=graph,
            nodes=nodes,
            edges=edges,
            milestones=milestones,
            sessions=raw_sessions,
            horizon=horizon,
            chapter_index=chapter_index,
            prev_plan=prev_plan,
        )

        # Persist if requested
        if save:
            self._persist_plan(plan)

        return plan

    def get_latest_plan(self) -> ProjectPlan | None:
        """Get the latest persisted plan."""
        return self.store.load_latest()

    def get_plan(self, plan_id: str) -> ProjectPlan | None:
        """Get a specific plan by ID."""
        return self.store.load_snapshot(plan_id)

    def explain_node(self, node_or_action_id: str) -> dict[str, Any]:
        """Explain a node or action ID in the current plan."""
        plan = self.store.load_latest()
        if not plan:
            return {"error": "No plan found", "node_id": node_or_action_id}

        # Search in nodes
        for n in plan.nodes:
            if n.node_id == node_or_action_id:
                return {
                    "found": True,
                    "node_id": n.node_id,
                    "node_type": n.node_type.value,
                    "label": n.label,
                    "source_subsystem": n.source_subsystem,
                    "source_ref": n.source_ref,
                    "freshness": n.freshness,
                    "chapter_index": n.chapter_index,
                    "in_cycles": any(node_or_action_id in c for c in plan.cycles),
                    "blocked_milestones": [
                        m.title for m in plan.milestones
                        if node_or_action_id in m.dependent_node_ids
                    ],
                }

        # Search in actions
        actions = list(plan.authority_required_actions)
        if plan.recommended_next_action:
            actions.append(plan.recommended_next_action)
        for a in actions:
            if a.action_id == node_or_action_id or a.source_node_id == node_or_action_id:
                return {
                    "found": True,
                    "action_id": a.action_id,
                    "title": a.title,
                    "reason": a.reason,
                    "authority": a.authority.value,
                    "safe_to_execute": a.safe_to_execute,
                    "source_node_id": a.source_node_id,
                    "expected_result_state": a.expected_result_state,
                }

        return {
            "found": False,
            "node_id": node_or_action_id,
            "message": f"Node or action not found in current plan: {node_or_action_id}",
        }

    def history(self) -> list[dict[str, Any]]:
        """Get plan history."""
        return self.store.list_all_history()

    def list_plans(self) -> list[dict[str, Any]]:
        """List all plan snapshots."""
        return self.store.list_snapshots()


    def diff(self, plan_a_id: str, plan_b_id: str | None = None) -> dict[str, Any]:
        """Diff two plan snapshots. plan_b_id=None → latest."""
        plan_a = self.store.load_snapshot(plan_a_id)
        if plan_a is None:
            raise ValueError(f"Plan not found: {plan_a_id}")
        if plan_b_id:
            plan_b = self.store.load_snapshot(plan_b_id)
            if plan_b is None:
                raise ValueError(f"Plan not found: {plan_b_id}")
        else:
            plan_b = self.store.load_latest()
            if plan_b is None:
                raise ValueError("No latest plan available")
        from auteur.planning.differ import diff_plans
        return diff_plans(plan_a, plan_b).to_dict()

    # ------------------------------------------------------------------
    # User-defined milestones
    # ------------------------------------------------------------------

    def add_user_milestone(self, title: str, scope: str = "project", description: str = "") -> dict[str, Any]:
        """Add a user-defined milestone."""
        import hashlib
        mid = hashlib.sha256(f"user|{title}|{scope}".encode()).hexdigest()[:16]
        user_ms = self.store.load_user_milestones()
        # Check duplicate
        for m in user_ms:
            if m.get("milestone_id") == mid:
                raise ValueError(f"Milestone already exists: {title}")
        entry = {
            "milestone_id": mid,
            "title": title,
            "scope": scope,
            "description": description,
            "state": "not_started",
        }
        user_ms.append(entry)
        self.store.save_user_milestones(user_ms)
        return entry

    def remove_user_milestone(self, milestone_id: str) -> bool:
        """Remove a user-defined milestone by ID. Returns True if found."""
        user_ms = self.store.load_user_milestones()
        filtered = [m for m in user_ms if m.get("milestone_id") != milestone_id]
        if len(filtered) == len(user_ms):
            return False
        self.store.save_user_milestones(filtered)
        return True

    def list_user_milestones(self) -> list[dict[str, Any]]:
        """List all user-defined milestones."""
        return self.store.load_user_milestones()


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_decisions(self) -> list[Any]:
        """Load decisions from DecisionWorkspaceService."""
        try:
            from auteur.decision.service import DecisionWorkspaceService
            service = DecisionWorkspaceService(self.project_root)
            return self.assembler.load_decisions(service)
        except ImportError:
            logger.warning("DecisionWorkspaceService not available")
            return []
        except Exception as e:
            logger.warning(f"Could not load decisions: {e}")
            return []

    def _load_sessions(self) -> list[dict]:
        """Load review sessions from ReviewService."""
        try:
            from auteur.review.service import ReviewService
            service = ReviewService(self.project_root)
            return self.assembler.load_sessions(service)
        except ImportError:
            logger.warning("ReviewService not available")
            return []
        except Exception as e:
            logger.warning(f"Could not load sessions: {e}")
            return []

    def _persist_plan(self, plan: ProjectPlan) -> None:
        """Persist a plan snapshot and update latest pointer."""
        try:
            self.store.save_snapshot(plan)
            self.store.save_latest(plan)
            if plan.plan_history:
                self.store.save_history(plan.plan_id, plan.plan_history)
        except Exception as e:
            logger.warning(f"Could not persist plan: {e}")
