"""Plan diff — compare two plan snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auteur.planning.models import ProjectPlan


@dataclass
class NodeDiff:
    added: list[dict] = field(default_factory=list)
    removed: list[dict] = field(default_factory=list)
    changed: list[dict] = field(default_factory=list)


@dataclass
class MilestoneDiff:
    added: list[dict] = field(default_factory=list)
    removed: list[dict] = field(default_factory=list)
    state_changed: list[dict] = field(default_factory=list)


@dataclass
class BlockerDiff:
    resolved: list[dict] = field(default_factory=list)
    new: list[dict] = field(default_factory=list)


@dataclass
class PlanDiff:
    """Complete diff between two plan snapshots."""
    plan_a_id: str = ""
    plan_b_id: str = ""
    created_a: str = ""
    created_b: str = ""
    nodes: NodeDiff = field(default_factory=NodeDiff)
    edges_added: int = 0
    edges_removed: int = 0
    milestones: MilestoneDiff = field(default_factory=MilestoneDiff)
    blockers: BlockerDiff = field(default_factory=BlockerDiff)
    paths_added: int = 0
    paths_removed: int = 0
    actions_added: int = 0
    actions_removed: int = 0
    has_changes: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_a_id": self.plan_a_id,
            "plan_b_id": self.plan_b_id,
            "created_a": self.created_a,
            "created_b": self.created_b,
            "nodes": {
                "added": self.nodes.added,
                "removed": self.nodes.removed,
                "changed": self.nodes.changed,
            },
            "edges_added": self.edges_added,
            "edges_removed": self.edges_removed,
            "milestones": {
                "added": self.milestones.added,
                "removed": self.milestones.removed,
                "state_changed": self.milestones.state_changed,
            },
            "blockers": {
                "resolved": self.blockers.resolved,
                "new": self.blockers.new,
            },
            "paths_added": self.paths_added,
            "paths_removed": self.paths_removed,
            "actions_added": self.actions_added,
            "actions_removed": self.actions_removed,
            "has_changes": self.has_changes,
        }


def _node_key(n: Any) -> str:
    return getattr(n, "node_id", "") or getattr(n, "id", "")


def _milestone_key(m: Any) -> str:
    return getattr(m, "milestone_id", "") or getattr(m, "id", "")


def _blocker_key(b: Any) -> str:
    return getattr(b, "blocker_id", "") or getattr(b, "id", "") or getattr(b, "message", "")


def _action_key(a: Any) -> str:
    return getattr(a, "action_id", "") or getattr(a, "id", "") or getattr(a, "label", "")


def _path_key(p: Any) -> str:
    return getattr(p, "path_id", "") or getattr(p, "id", "") or str(getattr(p, "leverage_score", 0))


def _simple(obj: Any) -> dict[str, Any]:
    """Convert a model object to a simple dict for diff display."""
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, dict):
        return obj
    return {"id": str(obj)}


def diff_plans(plan_a: ProjectPlan, plan_b: ProjectPlan) -> PlanDiff:
    """Compare two project plans and produce a PlanDiff."""
    result = PlanDiff(
        plan_a_id=plan_a.plan_id,
        plan_b_id=plan_b.plan_id,
        created_a=plan_a.created_at,
        created_b=plan_b.created_at,
    )

    # Nodes
    a_nodes = {_node_key(n): n for n in plan_a.nodes}
    b_nodes = {_node_key(n): n for n in plan_b.nodes}
    a_node_keys = set(a_nodes.keys())
    b_node_keys = set(b_nodes.keys())

    for k in sorted(b_node_keys - a_node_keys):
        result.nodes.added.append(_simple(b_nodes[k]))
    for k in sorted(a_node_keys - b_node_keys):
        result.nodes.removed.append(_simple(a_nodes[k]))
    for k in sorted(a_node_keys & b_node_keys):
        na = a_nodes[k]
        nb = b_nodes[k]
        if getattr(na, "status", "") != getattr(nb, "status", ""):
            result.nodes.changed.append({"node_id": k, "from": getattr(na, "status", ""), "to": getattr(nb, "status", "")})

    # Edges
    a_edge_keys = {
        (getattr(e, "source_id", ""), getattr(e, "target_id", ""))
        for e in plan_a.edges
    }
    b_edge_keys = {
        (getattr(e, "source_id", ""), getattr(e, "target_id", ""))
        for e in plan_b.edges
    }
    result.edges_added = len(b_edge_keys - a_edge_keys)
    result.edges_removed = len(a_edge_keys - b_edge_keys)

    # Milestones
    a_ms = {_milestone_key(m): m for m in plan_a.milestones}
    b_ms = {_milestone_key(m): m for m in plan_b.milestones}
    a_ms_keys = set(a_ms.keys())
    b_ms_keys = set(b_ms.keys())
    for k in sorted(b_ms_keys - a_ms_keys):
        result.milestones.added.append(_simple(b_ms[k]))
    for k in sorted(a_ms_keys - b_ms_keys):
        result.milestones.removed.append(_simple(a_ms[k]))
    for k in sorted(a_ms_keys & b_ms_keys):
        sa = getattr(a_ms[k], "state", "")
        sb = getattr(b_ms[k], "state", "")
        if sa != sb:
            result.milestones.state_changed.append({"milestone_id": k, "from": sa, "to": sb})

    # Blockers
    a_bl = {_blocker_key(b): b for b in plan_a.blockers}
    b_bl = {_blocker_key(b): b for b in plan_b.blockers}
    a_bl_keys = set(a_bl.keys())
    b_bl_keys = set(b_bl.keys())
    for k in sorted(a_bl_keys - b_bl_keys):
        result.blockers.resolved.append(_simple(a_bl[k]))
    for k in sorted(b_bl_keys - a_bl_keys):
        result.blockers.new.append(_simple(b_bl[k]))

    # Critical paths
    a_pk = {_path_key(p) for p in plan_a.critical_paths}
    b_pk = {_path_key(p) for p in plan_b.critical_paths}
    result.paths_added = len(b_pk - a_pk)
    result.paths_removed = len(a_pk - b_pk)

    # Actions — authority_required_actions + recommended_next_action
    a_actions = set()
    for act in plan_a.authority_required_actions:
        a_actions.add(_action_key(act))
    if plan_a.recommended_next_action:
        a_actions.add(_action_key(plan_a.recommended_next_action) + "_next")
    b_actions = set()
    for act in plan_b.authority_required_actions:
        b_actions.add(_action_key(act))
    if plan_b.recommended_next_action:
        b_actions.add(_action_key(plan_b.recommended_next_action) + "_next")
    result.actions_added = len(b_actions - a_actions)
    result.actions_removed = len(a_actions - b_actions)

    result.has_changes = (
        bool(result.nodes.added or result.nodes.removed or result.nodes.changed)
        or result.edges_added > 0 or result.edges_removed > 0
        or bool(result.milestones.added or result.milestones.removed or result.milestones.state_changed)
        or bool(result.blockers.resolved or result.blockers.new)
        or result.paths_added > 0 or result.paths_removed > 0
        or result.actions_added > 0 or result.actions_removed > 0
    )

    return result
