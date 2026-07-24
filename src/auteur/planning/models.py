"""Typed models for Project-Level Narrative Planning."""

from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PlanningHorizon(str, enum.Enum):
    PROJECT = "project"
    BOOK = "book"
    ACT = "act"
    CHAPTER = "chapter"
    SCENE = "scene"


class NodeType(str, enum.Enum):
    DECISION = "decision"
    REVIEW_SESSION = "review_session"
    MILESTONE = "milestone"
    REFRESH = "refresh"


class DependencyType(str, enum.Enum):
    PREREQUISITE = "prerequisite"
    BLOCKS = "blocks"
    INVALIDATES = "invalidates"
    REQUIRES_EVIDENCE_FROM = "requires_evidence_from"
    REQUIRES_ACCEPTANCE_OF = "requires_acceptance_of"
    REQUIRES_REVIEW_COMPLETION = "requires_review_completion"
    REFRESH_AFTER = "refresh_after"
    SUPERSEDES = "supersedes"


class DependencyStrength(str, enum.Enum):
    HARD = "hard"
    SOFT = "soft"
    INFORMATIONAL = "informational"


class MilestoneState(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    READY = "ready"
    COMPLETED = "completed"
    STALE = "stale"


class ActionAuthority(str, enum.Enum):
    READ_ONLY = "read_only"
    RECOMMENDATION = "recommendation"
    AUTHORITY_REQUIRED = "authority_required"
    CANONICAL_MUTATION = "canonical_mutation"


class CoordinationFindingType(str, enum.Enum):
    COMPATIBLE = "compatible"
    ORDER_REQUIRED = "order_required"
    STALE = "stale"
    CONFLICTING = "conflicting"
    SUPERSEDED = "superseded"
    BLOCKED = "blocked"


SCHEMA_VERSION = "project-plan-v1"
"""Current schema version for project plan snapshots."""


# ---------------------------------------------------------------------------
# Identity helpers
# ---------------------------------------------------------------------------

def _stable_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def compute_plan_id(project: str, horizon: str, timestamp: str) -> str:
    return _stable_id(project, horizon, timestamp)


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlanningNode:
    """A node in the project planning dependency graph."""
    node_id: str
    node_type: NodeType
    label: str
    chapter_index: int | None = None
    book_index: int | None = None
    act_index: int | None = None
    scene_id: str | None = None
    source_subsystem: str = ""
    source_ref: str = ""
    freshness: str = "current"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DependencyEvidence:
    """Evidence backing a dependency edge."""
    reason: str
    source_subsystem: str
    supporting_artifact: str = ""
    freshness: str = "current"


@dataclass(frozen=True)
class PlanDependency:
    """A dependency edge between two planning nodes."""
    edge_id: str
    source_id: str
    target_id: str
    dependency_type: DependencyType
    strength: DependencyStrength = DependencyStrength.HARD
    reason: str = ""
    evidence: DependencyEvidence | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlanMilestone:
    """A project milestone derived from artifact and authority state."""
    milestone_id: str
    title: str
    scope: PlanningHorizon
    state: MilestoneState = MilestoneState.NOT_STARTED
    chapter_index: int | None = None
    book_index: int | None = None
    act_index: int | None = None
    required_conditions: list[str] = field(default_factory=list)
    completed_conditions: list[str] = field(default_factory=list)
    blocked_conditions: list[str] = field(default_factory=list)
    dependent_node_ids: list[str] = field(default_factory=list)
    dependent_session_ids: list[str] = field(default_factory=list)
    authority_requirement: str = "read_only"
    evidence: str = ""
    status_reason: str = ""


@dataclass(frozen=True)
class CriticalPath:
    """A deterministic blocking critical path."""
    path_id: str
    ordered_node_ids: list[str]
    dependency_edges: list[PlanDependency]
    blocked_milestone_ids: list[str]
    cumulative_leverage: float = 0.0
    authority_required_steps: list[str] = field(default_factory=list)
    safe_steps: list[str] = field(default_factory=list)
    explanation: str = ""
    alternatives: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PlanBlocker:
    """A blocker in the project plan."""
    blocker_id: str
    source_node_id: str
    target_node_id: str | None = None
    description: str = ""
    severity: str = "blocking"
    category: str = "dependency"
    evidence: str = ""


@dataclass(frozen=True)
class PlanAction:
    """A recommended project action."""
    action_id: str
    title: str
    reason: str
    source_node_id: str = ""
    target: str = ""
    command: str = ""
    prerequisites: list[str] = field(default_factory=list)
    authority: ActionAuthority = ActionAuthority.READ_ONLY
    safe_to_execute: bool = False
    expected_result_state: str = ""
    blocked_milestones_released: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParallelWorkGroup:
    """A group of actions that may proceed concurrently."""
    group_id: str
    action_ids: list[str]
    shared_assumptions: list[str] = field(default_factory=list)
    conflict_checks: list[str] = field(default_factory=list)
    authority_categories: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CoordinationFinding:
    """A cross-session coordination finding."""
    finding_id: str
    finding_type: CoordinationFindingType
    session_ids: list[str]
    description: str = ""
    recommendation: str = ""
    target_overlap: str = ""
    evidence: str = ""


@dataclass(frozen=True)
class PlanHistoryEntry:
    """A semantic history entry for plan changes."""
    entry_id: str
    plan_id: str
    timestamp: str
    change_type: str  # decision_opened, decision_resolved, session_started, etc.
    description: str
    before_state: str = ""
    after_state: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectPlan:
    """Complete project plan with all analysis."""
    plan_id: str
    project: str
    horizon: PlanningHorizon = PlanningHorizon.PROJECT
    title: str = ""
    snapshot_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = SCHEMA_VERSION
    tool_version: str = "0.10.0"

    # State overview
    open_decision_count: int = 0
    active_review_session_count: int = 0
    blocked_milestone_count: int = 0

    # Detailed data
    nodes: list[PlanningNode] = field(default_factory=list)
    edges: list[PlanDependency] = field(default_factory=list)
    milestones: list[PlanMilestone] = field(default_factory=list)
    cycles: list[list[str]] = field(default_factory=list)
    critical_paths: list[CriticalPath] = field(default_factory=list)
    blockers: list[PlanBlocker] = field(default_factory=list)
    safe_parallel_work: list[ParallelWorkGroup] = field(default_factory=list)
    coordination_findings: list[CoordinationFinding] = field(default_factory=list)
    authority_required_actions: list[PlanAction] = field(default_factory=list)
    recommended_next_action: PlanAction | None = None

    # Freshness
    is_stale: bool = False
    stale_reason: str = ""
    plan_history: list[PlanHistoryEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON output."""
        return {
            "plan_id": self.plan_id,
            "project": self.project,
            "horizon": self.horizon.value,
            "title": self.title,
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
            "open_decision_count": self.open_decision_count,
            "active_review_session_count": self.active_review_session_count,
            "blocked_milestone_count": self.blocked_milestone_count,
            "nodes": [_node_to_dict(n) for n in self.nodes],
            "edges": [_edge_to_dict(e) for e in self.edges],
            "milestones": [_milestone_to_dict(m) for m in self.milestones],
            "cycles": self.cycles,
            "critical_paths": [_path_to_dict(p) for p in self.critical_paths],
            "blockers": [_blocker_to_dict(b) for b in self.blockers],
            "safe_parallel_work": [_parallel_to_dict(g) for g in self.safe_parallel_work],
            "coordination_findings": [_coordination_to_dict(c) for c in self.coordination_findings],
            "authority_required_actions": [_action_to_dict(a) for a in self.authority_required_actions],
            "recommended_next_action": _action_to_dict(self.recommended_next_action) if self.recommended_next_action else None,
            "is_stale": self.is_stale,
            "stale_reason": self.stale_reason,
        }


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _node_to_dict(n: PlanningNode) -> dict[str, Any]:
    return {
        "node_id": n.node_id,
        "node_type": n.node_type.value,
        "label": n.label,
        "chapter_index": n.chapter_index,
        "book_index": n.book_index,
        "act_index": n.act_index,
        "scene_id": n.scene_id,
        "source_subsystem": n.source_subsystem,
        "source_ref": n.source_ref,
        "freshness": n.freshness,
        "metadata": n.metadata,
    }


def _edge_to_dict(e: PlanDependency) -> dict[str, Any]:
    d: dict[str, Any] = {
        "edge_id": e.edge_id,
        "source_id": e.source_id,
        "target_id": e.target_id,
        "dependency_type": e.dependency_type.value,
        "strength": e.strength.value,
        "reason": e.reason,
    }
    if e.evidence:
        d["evidence"] = {
            "reason": e.evidence.reason,
            "source_subsystem": e.evidence.source_subsystem,
            "supporting_artifact": e.evidence.supporting_artifact,
            "freshness": e.evidence.freshness,
        }
    if e.metadata:
        d["metadata"] = e.metadata
    return d


def _milestone_to_dict(m: PlanMilestone) -> dict[str, Any]:
    return {
        "milestone_id": m.milestone_id,
        "title": m.title,
        "scope": m.scope.value,
        "state": m.state.value,
        "chapter_index": m.chapter_index,
        "book_index": m.book_index,
        "act_index": m.act_index,
        "required_conditions": m.required_conditions,
        "completed_conditions": m.completed_conditions,
        "blocked_conditions": m.blocked_conditions,
        "dependent_node_ids": m.dependent_node_ids,
        "dependent_session_ids": m.dependent_session_ids,
        "authority_requirement": m.authority_requirement,
        "evidence": m.evidence,
        "status_reason": m.status_reason,
    }


def _path_to_dict(p: CriticalPath) -> dict[str, Any]:
    return {
        "path_id": p.path_id,
        "ordered_node_ids": p.ordered_node_ids,
        "dependency_edges": [_edge_to_dict(e) for e in p.dependency_edges],
        "blocked_milestone_ids": p.blocked_milestone_ids,
        "cumulative_leverage": p.cumulative_leverage,
        "authority_required_steps": p.authority_required_steps,
        "safe_steps": p.safe_steps,
        "explanation": p.explanation,
        "alternatives": p.alternatives,
    }


def _blocker_to_dict(b: PlanBlocker) -> dict[str, Any]:
    return {
        "blocker_id": b.blocker_id,
        "source_node_id": b.source_node_id,
        "target_node_id": b.target_node_id,
        "description": b.description,
        "severity": b.severity,
        "category": b.category,
        "evidence": b.evidence,
    }


def _parallel_to_dict(g: ParallelWorkGroup) -> dict[str, Any]:
    return {
        "group_id": g.group_id,
        "action_ids": g.action_ids,
        "shared_assumptions": g.shared_assumptions,
        "conflict_checks": g.conflict_checks,
        "authority_categories": g.authority_categories,
    }


def _coordination_to_dict(c: CoordinationFinding) -> dict[str, Any]:
    return {
        "finding_id": c.finding_id,
        "finding_type": c.finding_type.value,
        "session_ids": c.session_ids,
        "description": c.description,
        "recommendation": c.recommendation,
        "target_overlap": c.target_overlap,
        "evidence": c.evidence,
    }


def _action_to_dict(a: PlanAction) -> dict[str, Any]:
    d: dict[str, Any] = {
        "action_id": a.action_id,
        "title": a.title,
        "reason": a.reason,
        "source_node_id": a.source_node_id,
        "target": a.target,
        "command": a.command,
        "prerequisites": a.prerequisites,
        "authority": a.authority.value,
        "safe_to_execute": a.safe_to_execute,
        "expected_result_state": a.expected_result_state,
        "blocked_milestones_released": a.blocked_milestones_released,
    }
    if a.metadata:
        d["metadata"] = a.metadata
    return d


# ---------------------------------------------------------------------------
# JSON round-trip helpers
# ---------------------------------------------------------------------------

def plan_from_dict(data: dict[str, Any]) -> ProjectPlan:
    """Deserialize a ProjectPlan from a dict."""
    nodes = [_node_from_dict(n) for n in data.get("nodes", [])]
    edges = [_edge_from_dict(e) for e in data.get("edges", [])]
    milestones = [_milestone_from_dict(m) for m in data.get("milestones", [])]
    critical_paths = [_path_from_dict(p) for p in data.get("critical_paths", [])]
    blockers = [_blocker_from_dict(b) for b in data.get("blockers", [])]
    parallel = [_parallel_from_dict(g) for g in data.get("safe_parallel_work", [])]
    coordination = [_coordination_from_dict(c) for c in data.get("coordination_findings", [])]
    authority = [_action_from_dict(a) for a in data.get("authority_required_actions", [])]
    next_action = _action_from_dict(data["recommended_next_action"]) if data.get("recommended_next_action") else None

    return ProjectPlan(
        plan_id=data["plan_id"],
        project=data["project"],
        horizon=PlanningHorizon(data["horizon"]),
        title=data.get("title", ""),
        snapshot_id=data.get("snapshot_id", ""),
        created_at=data.get("created_at", ""),
        schema_version=data.get("schema_version", SCHEMA_VERSION),
        tool_version=data.get("tool_version", "0.10.0"),
        open_decision_count=data.get("open_decision_count", 0),
        active_review_session_count=data.get("active_review_session_count", 0),
        blocked_milestone_count=data.get("blocked_milestone_count", 0),
        nodes=nodes,
        edges=edges,
        milestones=milestones,
        cycles=data.get("cycles", []),
        critical_paths=critical_paths,
        blockers=blockers,
        safe_parallel_work=parallel,
        coordination_findings=coordination,
        authority_required_actions=authority,
        recommended_next_action=next_action,
        is_stale=data.get("is_stale", False),
        stale_reason=data.get("stale_reason", ""),
    )


def _node_from_dict(d: dict[str, Any]) -> PlanningNode:
    return PlanningNode(
        node_id=d["node_id"],
        node_type=NodeType(d["node_type"]),
        label=d["label"],
        chapter_index=d.get("chapter_index"),
        book_index=d.get("book_index"),
        act_index=d.get("act_index"),
        scene_id=d.get("scene_id"),
        source_subsystem=d.get("source_subsystem", ""),
        source_ref=d.get("source_ref", ""),
        freshness=d.get("freshness", "current"),
        metadata=d.get("metadata", {}),
    )


def _edge_from_dict(d: dict[str, Any]) -> PlanDependency:
    ev = d.get("evidence")
    evidence = DependencyEvidence(ev["reason"], ev["source_subsystem"], ev.get("supporting_artifact", ""), ev.get("freshness", "current")) if ev else None
    return PlanDependency(
        edge_id=d["edge_id"],
        source_id=d["source_id"],
        target_id=d["target_id"],
        dependency_type=DependencyType(d["dependency_type"]),
        strength=DependencyStrength(d.get("strength", "hard")),
        reason=d.get("reason", ""),
        evidence=evidence,
        metadata=d.get("metadata", {}),
    )


def _milestone_from_dict(d: dict[str, Any]) -> PlanMilestone:
    return PlanMilestone(
        milestone_id=d["milestone_id"],
        title=d["title"],
        scope=PlanningHorizon(d["scope"]),
        state=MilestoneState(d.get("state", "not_started")),
        chapter_index=d.get("chapter_index"),
        book_index=d.get("book_index"),
        act_index=d.get("act_index"),
        required_conditions=d.get("required_conditions", []),
        completed_conditions=d.get("completed_conditions", []),
        blocked_conditions=d.get("blocked_conditions", []),
        dependent_node_ids=d.get("dependent_node_ids", []),
        dependent_session_ids=d.get("dependent_session_ids", []),
        authority_requirement=d.get("authority_requirement", "read_only"),
        evidence=d.get("evidence", ""),
        status_reason=d.get("status_reason", ""),
    )


def _path_from_dict(d: dict[str, Any]) -> CriticalPath:
    edges = [_edge_from_dict(e) for e in d.get("dependency_edges", [])]
    return CriticalPath(
        path_id=d["path_id"],
        ordered_node_ids=d["ordered_node_ids"],
        dependency_edges=edges,
        blocked_milestone_ids=d.get("blocked_milestone_ids", []),
        cumulative_leverage=d.get("cumulative_leverage", 0.0),
        authority_required_steps=d.get("authority_required_steps", []),
        safe_steps=d.get("safe_steps", []),
        explanation=d.get("explanation", ""),
        alternatives=d.get("alternatives", []),
    )


def _blocker_from_dict(d: dict[str, Any]) -> PlanBlocker:
    return PlanBlocker(
        blocker_id=d["blocker_id"],
        source_node_id=d["source_node_id"],
        target_node_id=d.get("target_node_id"),
        description=d.get("description", ""),
        severity=d.get("severity", "blocking"),
        category=d.get("category", "dependency"),
        evidence=d.get("evidence", ""),
    )


def _parallel_from_dict(d: dict[str, Any]) -> ParallelWorkGroup:
    return ParallelWorkGroup(
        group_id=d["group_id"],
        action_ids=d["action_ids"],
        shared_assumptions=d.get("shared_assumptions", []),
        conflict_checks=d.get("conflict_checks", []),
        authority_categories=d.get("authority_categories", []),
    )


def _coordination_from_dict(d: dict[str, Any]) -> CoordinationFinding:
    return CoordinationFinding(
        finding_id=d["finding_id"],
        finding_type=CoordinationFindingType(d["finding_type"]),
        session_ids=d["session_ids"],
        description=d.get("description", ""),
        recommendation=d.get("recommendation", ""),
        target_overlap=d.get("target_overlap", ""),
        evidence=d.get("evidence", ""),
    )


def _action_from_dict(d: dict[str, Any]) -> PlanAction:
    return PlanAction(
        action_id=d["action_id"],
        title=d["title"],
        reason=d["reason"],
        source_node_id=d.get("source_node_id", ""),
        target=d.get("target", ""),
        command=d.get("command", ""),
        prerequisites=d.get("prerequisites", []),
        authority=ActionAuthority(d.get("authority", "read_only")),
        safe_to_execute=d.get("safe_to_execute", False),
        expected_result_state=d.get("expected_result_state", ""),
        blocked_milestones_released=d.get("blocked_milestones_released", []),
        metadata=d.get("metadata", {}),
    )
