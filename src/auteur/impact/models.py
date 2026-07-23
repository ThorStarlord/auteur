from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class ChangeType(str, enum.Enum):
    CONTENT_CHANGED = "content_changed"
    POINTER_CHANGED = "pointer_changed"
    ARTIFACT_REMOVED = "artifact_removed"
    ARTIFACT_ADDED = "artifact_added"
    ACCEPTED_SOURCE_CHANGED = "accepted_source_changed"
    DEPENDENCY_CHANGED = "dependency_changed"
    SCHEMA_VERSION_CHANGED = "schema_version_changed"


class ImpactSeverity(str, enum.Enum):
    NONE = "none"
    REVIEW = "review"
    RECONCILE = "reconcile"
    REGENERATE_CANDIDATE = "regenerate_candidate"
    BLOCKED = "blocked"


class PreservationStatus(str, enum.Enum):
    PRESERVE = "preserve"
    PRESERVE_WITH_REVIEW = "preserve_with_review"
    PARTIAL_PRESERVATION = "partial_preservation"
    REGENERATE = "regenerate"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    artifact_type: str = ""
    chapter_index: int | None = None
    scene_index: int | None = None
    file_path: str = ""
    content_hash: str = ""
    authority: str = "canonical"
    accepted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "chapter_index": self.chapter_index,
            "scene_index": self.scene_index,
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "authority": self.authority,
            "accepted": self.accepted,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ArtifactRef:
        return cls(
            artifact_id=d["artifact_id"],
            artifact_type=d.get("artifact_type", ""),
            chapter_index=d.get("chapter_index"),
            scene_index=d.get("scene_index"),
            file_path=d.get("file_path", ""),
            content_hash=d.get("content_hash", ""),
            authority=d.get("authority", "canonical"),
            accepted=d.get("accepted", False),
        )


@dataclass(frozen=True)
class DependencyEdge:
    source_id: str
    target_id: str
    kind: str = "structural"
    source: str = "inferred"
    fields: tuple[str, ...] = field(default_factory=tuple)
    rule_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "kind": self.kind,
            "source": self.source,
            "fields": list(self.fields),
            "rule_id": self.rule_id,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DependencyEdge:
        return cls(
            source_id=d["source_id"],
            target_id=d["target_id"],
            kind=d.get("kind", "structural"),
            source=d.get("source", "inferred"),
            fields=tuple(d.get("fields", [])),
            rule_id=d.get("rule_id", ""),
        )


@dataclass
class ChangeRecord:
    change_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    artifact_ref: ArtifactRef | None = None
    change_type: ChangeType = ChangeType.CONTENT_CHANGED
    previous_hash: str = ""
    current_hash: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "change_id": self.change_id,
            "artifact_ref": self.artifact_ref.to_dict() if self.artifact_ref else None,
            "change_type": self.change_type.value if isinstance(self.change_type, ChangeType) else self.change_type,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
            "detected_at": self.detected_at,
            "evidence": self.evidence,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ChangeRecord:
        return cls(
            change_id=d.get("change_id", ""),
            artifact_ref=ArtifactRef.from_dict(d["artifact_ref"]) if d.get("artifact_ref") else None,
            change_type=ChangeType(d["change_type"]) if isinstance(d.get("change_type"), str) else ChangeType.CONTENT_CHANGED,
            previous_hash=d.get("previous_hash", ""),
            current_hash=d.get("current_hash", ""),
            detected_at=d.get("detected_at", ""),
            evidence=d.get("evidence", ""),
        )


@dataclass
class ImpactFinding:
    finding_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    source_change: ChangeRecord | None = None
    affected_artifact: ArtifactRef | None = None
    is_direct: bool = True
    severity: ImpactSeverity = ImpactSeverity.REVIEW
    rule_id: str = ""
    reason: str = ""
    dependency_path: list[str] = field(default_factory=list)
    preservation: PreservationStatus = PreservationStatus.UNKNOWN
    recommended_action: str = ""
    authority_required: str = "read_only"

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "source_change": self.source_change.to_dict() if self.source_change else None,
            "affected_artifact": self.affected_artifact.to_dict() if self.affected_artifact else None,
            "is_direct": self.is_direct,
            "severity": self.severity.value if isinstance(self.severity, ImpactSeverity) else self.severity,
            "rule_id": self.rule_id,
            "reason": self.reason,
            "dependency_path": self.dependency_path,
            "preservation": self.preservation.value if isinstance(self.preservation, PreservationStatus) else self.preservation,
            "recommended_action": self.recommended_action,
            "authority_required": self.authority_required,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ImpactFinding:
        return cls(
            finding_id=d.get("finding_id", ""),
            source_change=ChangeRecord.from_dict(d["source_change"]) if d.get("source_change") else None,
            affected_artifact=ArtifactRef.from_dict(d["affected_artifact"]) if d.get("affected_artifact") else None,
            is_direct=d.get("is_direct", True),
            severity=ImpactSeverity(d["severity"]) if isinstance(d.get("severity"), str) else ImpactSeverity.REVIEW,
            rule_id=d.get("rule_id", ""),
            reason=d.get("reason", ""),
            dependency_path=d.get("dependency_path", []),
            preservation=PreservationStatus(d["preservation"]) if isinstance(d.get("preservation"), str) else PreservationStatus.UNKNOWN,
            recommended_action=d.get("recommended_action", ""),
            authority_required=d.get("authority_required", "read_only"),
        )


@dataclass
class RepairAction:
    action_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    description: str = ""
    affected_artifact: ArtifactRef | None = None
    prerequisites: list[str] = field(default_factory=list)
    command: str = ""
    authority: str = "read_only"
    safe_to_execute: bool = False
    blocking: bool = False
    reason: str = ""
    preserved_artifacts: list[ArtifactRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "title": self.title,
            "description": self.description,
            "affected_artifact": self.affected_artifact.to_dict() if self.affected_artifact else None,
            "prerequisites": self.prerequisites,
            "command": self.command,
            "authority": self.authority,
            "safe_to_execute": self.safe_to_execute,
            "blocking": self.blocking,
            "reason": self.reason,
            "preserved_artifacts": [a.to_dict() for a in self.preserved_artifacts],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> RepairAction:
        return cls(
            action_id=d.get("action_id", ""),
            title=d.get("title", ""),
            description=d.get("description", ""),
            affected_artifact=ArtifactRef.from_dict(d["affected_artifact"]) if d.get("affected_artifact") else None,
            prerequisites=d.get("prerequisites", []),
            command=d.get("command", ""),
            authority=d.get("authority", "read_only"),
            safe_to_execute=d.get("safe_to_execute", False),
            blocking=d.get("blocking", False),
            reason=d.get("reason", ""),
            preserved_artifacts=[ArtifactRef.from_dict(a) for a in d.get("preserved_artifacts", [])],
        )


@dataclass
class RepairPlan:
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    changes: list[ChangeRecord] = field(default_factory=list)
    findings: list[ImpactFinding] = field(default_factory=list)
    actions: list[RepairAction] = field(default_factory=list)
    preserved_artifacts: list[ArtifactRef] = field(default_factory=list)
    graph_snapshot: dict[str, Any] = field(default_factory=dict)
    tool_version: str = "0.5.0"
    authority: str = "derived"
    canonical: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "created_at": self.created_at,
            "changes": [c.to_dict() for c in self.changes],
            "findings": [f.to_dict() for f in self.findings],
            "actions": [a.to_dict() for a in self.actions],
            "preserved_artifacts": [a.to_dict() for a in self.preserved_artifacts],
            "graph_snapshot": self.graph_snapshot,
            "tool_version": self.tool_version,
            "authority": self.authority,
            "canonical": self.canonical,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> RepairPlan:
        return cls(
            plan_id=d.get("plan_id", ""),
            created_at=d.get("created_at", ""),
            changes=[ChangeRecord.from_dict(c) for c in d.get("changes", [])],
            findings=[ImpactFinding.from_dict(f) for f in d.get("findings", [])],
            actions=[RepairAction.from_dict(a) for a in d.get("actions", [])],
            preserved_artifacts=[ArtifactRef.from_dict(a) for a in d.get("preserved_artifacts", [])],
            graph_snapshot=d.get("graph_snapshot", {}),
            tool_version=d.get("tool_version", "0.5.0"),
            authority=d.get("authority", "derived"),
            canonical=d.get("canonical", False),
        )


# ---------------------------------------------------------------------------
# v0.8.0 — Impact preview simulation models
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImpactedArtifact:
    """An artifact that would be affected by accepting a candidate."""
    artifact_id: str
    artifact_type: str = ""
    chapter_index: int | None = None
    impact_kind: str = "definite"  # "definite" or "inferred"
    impact_reason: str = ""
    downstream_cost: int = 1


@dataclass(frozen=True)
class ImpactPreview:
    """Simulation of consequences of accepting a candidate, no state mutation."""
    candidate_id: str
    target_artifact_id: str
    simulated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    definite_impacts: list[ImpactedArtifact] = field(default_factory=list)
    inferred_impacts: list[ImpactedArtifact] = field(default_factory=list)
    unchanged_artifacts: list[str] = field(default_factory=list)
    downstream_work_summary: str = ""
    impact_graph: dict[str, Any] = field(default_factory=dict)

    def total_cost_score(self) -> int:
        """Heuristic: definite*2 + inferred."""
        return len(self.definite_impacts) * 2 + len(self.inferred_impacts)
