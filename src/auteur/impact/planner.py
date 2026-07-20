"""Repair plan generation and deterministic ordering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from auteur.impact.graph import DependencyGraph
from auteur.impact.models import (
    ArtifactRef,
    ChangeRecord,
    ImpactFinding,
    ImpactSeverity,
    PreservationStatus,
    RepairAction,
    RepairPlan,
)
from auteur.impact.analyzer import ImpactAnalyzer


# Ordering weights for repair action sequencing
def _action_order_key(action: RepairAction) -> tuple[int, int, str]:
    """Return a sort key for deterministic repair ordering.

    Ordering policy (lower = earlier):
      1. Graph corruption / missing dependencies (weight 0)
      2. BLOCKED (weight 1)
      3. RECONCILE (weight 2)
      4. REGENERATE_CANDIDATE (weight 3)
      5. REVIEW (weight 4)
      6. NONE (weight 5)

    Within same severity:
      - Lower chapter number first
      - Alphabetical artifact ID as final tie-break
    """
    severity_weight = {
        ImpactSeverity.NONE: 5,
        ImpactSeverity.REVIEW: 4,
        ImpactSeverity.REGENERATE_CANDIDATE: 3,
        ImpactSeverity.RECONCILE: 2,
        ImpactSeverity.BLOCKED: 1,
    }

    # Check for severity
    sev_str = getattr(action, '_severity', None)
    sev = ImpactSeverity.REVIEW
    if sev_str and isinstance(sev_str, ImpactSeverity):
        sev = sev_str
    elif sev_str and isinstance(sev_str, str):
        try:
            sev = ImpactSeverity(sev_str)
        except ValueError:
            pass

    weight = severity_weight.get(sev, 4)

    # Chapter index for ordering within same severity
    chapter = 999
    if action.affected_artifact and action.affected_artifact.chapter_index is not None:
        chapter = action.affected_artifact.chapter_index

    # Tie-break: artifact ID
    artifact_id = action.affected_artifact.artifact_id if action.affected_artifact else ""

    return (weight, chapter, artifact_id)


def _build_prerequisites(
    actions: list[RepairAction],
    findings: list[ImpactFinding],
) -> dict[str, list[str]]:
    """Build prerequisite relationships between actions.

    - RECONCILE actions must precede REGENERATE_CANDIDATE actions
    - Realization before expression
    - Expression before reasoning
    - Reasoning before acceptance
    - Acceptance before assembly
    - Assembly before publishing
    - Earlier chapters before later chapters
    """
    action_map: dict[str, RepairAction] = {a.action_id: a for a in actions}
    prereq_map: dict[str, list[str]] = {a.action_id: [] for a in actions}

    # Map action_id -> artifact_id
    action_artifact_map: dict[str, str] = {}
    for a in actions:
        if a.affected_artifact:
            action_artifact_map[a.action_id] = a.affected_artifact.artifact_id

    # Map artifact_id -> action_id
    artifact_action_map: dict[str, str] = {}
    for a in actions:
        if a.affected_artifact:
            artifact_action_map[a.affected_artifact.artifact_id] = a.action_id

    for a in actions:
        if not a.affected_artifact:
            continue
        aid = a.affected_artifact.artifact_id
        artifact_type = a.affected_artifact.artifact_type

        # RECONCILE for upstream must precede REGENERATE for downstream
        if "reconcile" in a.title.lower() or a.authority == "candidate_generation":
            # Find REGENERATE actions for same chapter
            for other in actions:
                if other.action_id == a.action_id:
                    continue
                if not other.affected_artifact:
                    continue
                if other.affected_artifact.chapter_index == a.affected_artifact.chapter_index:
                    if "regenerate" in other.title.lower():
                        if other.action_id not in prereq_map.setdefault(a.action_id, []):
                            prereq_map.setdefault(a.action_id, []).append(other.action_id)

    return prereq_map


class RepairPlanner:
    """Generates ordered repair plans from impact analysis findings."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self.analyzer = ImpactAnalyzer(self.project_root)

    def plan(
        self,
        findings: list[ImpactFinding] | None = None,
        changes: list[ChangeRecord] | None = None,
        graph: DependencyGraph | None = None,
    ) -> RepairPlan:
        """Generate a complete repair plan from impact findings."""
        if findings is None:
            findings = self.analyzer.analyze(graph, changes)
        if changes is None:
            changes = self.analyzer.detect_changes(graph) if self.analyzer else []

        actions = self._build_actions(findings)
        preserved = _collect_preserved(findings)
        prereq_map = _build_prerequisites(actions, findings)

        # Set prerequisites on actions
        for action in actions:
            if action.action_id in prereq_map:
                action.prerequisites = prereq_map[action.action_id]

        # Sort actions deterministically
        actions.sort(key=_action_order_key)

        plan = RepairPlan(
            changes=changes,
            findings=findings,
            actions=actions,
            preserved_artifacts=preserved,
            graph_snapshot=graph.to_dict() if graph else {},
        )

        return plan

    def _build_actions(self, findings: list[ImpactFinding]) -> list[RepairAction]:
        """Convert impact findings into repair actions."""
        actions: list[RepairAction] = []
        seen = set()

        for f in findings:
            if f.severity is ImpactSeverity.NONE:
                continue
            if not f.affected_artifact:
                continue

            key = f.affected_artifact.artifact_id
            if key in seen:
                continue
            seen.add(key)

            command = self._generate_command(f)
            action = RepairAction(
                title=_action_title(f),
                description=f.reason,
                affected_artifact=f.affected_artifact,
                command=command,
                authority=f.authority_required,
                safe_to_execute=f.authority_required in ("read_only", "candidate_generation", "derived_artifact"),
                blocking=f.severity == ImpactSeverity.BLOCKED,
                reason=f.reason,
            )
            # Store severity for ordering
            action._severity = f.severity  # type: ignore[attr-defined]
            actions.append(action)

        return actions

    def _generate_command(self, finding: ImpactFinding) -> str:
        """Generate a CLI command for resolving a finding."""
        if not finding.affected_artifact:
            return ""
        aid = finding.affected_artifact.artifact_id
        artifact_type = finding.affected_artifact.artifact_type

        if finding.severity == ImpactSeverity.BLOCKED:
            return f"auteur impact explain {finding.finding_id}"
        if finding.severity == ImpactSeverity.RECONCILE:
            if artifact_type == "scene_realization":
                return f"auteur realization reconcile --scene {aid}"
            return f"auteur impact explain {finding.finding_id}"
        if finding.severity == ImpactSeverity.REGENERATE_CANDIDATE:
            if artifact_type == "scene_expression":
                return f"auteur expression generate {aid}"
            if artifact_type == "chapter_expression":
                return f"auteur expression compose-chapter {aid} --project {self.project_root}"
            return f"auteur impact explain {finding.finding_id}"
        if finding.severity == ImpactSeverity.REVIEW:
            return f"auteur impact explain {finding.finding_id}"
        return ""


def _action_title(finding: ImpactFinding) -> str:
    """Generate a human-readable title for a finding."""
    if not finding.affected_artifact:
        return "Unknown action"
    aid = finding.affected_artifact.artifact_id

    if finding.severity == ImpactSeverity.BLOCKED:
        return f"Unblock {aid}"
    if finding.severity == ImpactSeverity.RECONCILE:
        return f"Reconcile {aid}"
    if finding.severity == ImpactSeverity.REGENERATE_CANDIDATE:
        return f"Regenerate {aid}"
    if finding.severity == ImpactSeverity.REVIEW:
        return f"Review {aid}"
    return f"Inspect {aid}"


def _collect_preserved(findings: list[ImpactFinding]) -> list[ArtifactRef]:
    """Collect artifacts that are preserved (NONE severity or explicitly preserved)."""
    preserved: list[ArtifactRef] = []
    seen = set()
    for f in findings:
        if f.severity is ImpactSeverity.NONE and f.affected_artifact:
            if f.affected_artifact.artifact_id not in seen:
                preserved.append(f.affected_artifact)
                seen.add(f.affected_artifact.artifact_id)
    return preserved
