"""Change detection and impact propagation analysis."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from auteur.impact.graph import DependencyGraph
from auteur.impact.models import (
    ArtifactRef,
    ChangeRecord,
    ChangeType,
    ImpactFinding,
    ImpactSeverity,
    PreservationStatus,
)
from auteur.impact.rules import RULES, highest_severity, match_rule
from auteur.provenance.store import ArtifactStore, canonical_content_hash


def _detect_changes(
    store: ArtifactStore,
    known_artifacts: dict[str, ArtifactRef],
) -> list[ChangeRecord]:
    """Detect changes between recorded provenance state and current files."""
    changes: list[ChangeRecord] = []
    project_root = store.project

    for artifact_id, ref in known_artifacts.items():
        file_path = project_root / ref.file_path if ref.file_path else Path(ref.file_path)
        if not file_path.exists():
            changes.append(ChangeRecord(
                artifact_ref=ref,
                change_type=ChangeType.ARTIFACT_REMOVED,
                previous_hash=ref.content_hash,
                current_hash="",
                evidence=f"File no longer exists: {ref.file_path}",
            ))
            continue

        if not file_path.is_file():
            continue

        current_hash = canonical_content_hash(file_path)
        if current_hash != ref.content_hash and ref.content_hash:
            changes.append(ChangeRecord(
                artifact_ref=ref,
                change_type=ChangeType.CONTENT_CHANGED,
                previous_hash=ref.content_hash,
                current_hash=current_hash,
                evidence=f"Content hash changed: {ref.content_hash[:16]}... → {current_hash[:16]}...",
            ))

        # Check accepted source changes
        if ref.accepted and file_path.suffix in (".yaml", ".yml"):
            try:
                data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
                source_ref = data.get("source_chapter") or data.get("source") or {}
                if isinstance(source_ref, dict) and source_ref.get("artifact_id"):
                    src_id = source_ref["artifact_id"]
                    src_meta = store.current(src_id)
                    src_ref = known_artifacts.get(src_id)
                    if src_meta and src_ref:
                        src_hash = canonical_content_hash(project_root / src_ref.file_path) if src_ref.file_path else ""
                        if src_hash and src_hash != src_ref.content_hash:
                            changes.append(ChangeRecord(
                                artifact_ref=ref,
                                change_type=ChangeType.ACCEPTED_SOURCE_CHANGED,
                                previous_hash=src_ref.content_hash,
                                current_hash=src_hash,
                                evidence=f"Accepted source {src_id} hash changed",
                            ))
            except (OSError, yaml.YAMLError):
                pass

    return changes


def _classify_impact(
    graph: DependencyGraph,
    changes: list[ChangeRecord],
    all_artifacts: dict[str, ArtifactRef],
) -> list[ImpactFinding]:
    """Classify impact from changes through the dependency graph."""
    findings: list[ImpactFinding] = {}
    change_map: dict[str, ChangeRecord] = {}

    for change in changes:
        if change.artifact_ref:
            change_map[change.artifact_ref.artifact_id] = change

    for change in changes:
        if not change.artifact_ref:
            continue
        source_id = change.artifact_ref.artifact_id
        source_type = change.artifact_ref.artifact_type
        change_type = change.change_type.value if isinstance(change.change_type, ChangeType) else str(change.change_type)

        # Direct dependents
        for edge in graph.direct_dependents(source_id):
            target_id = edge.target_id
            target_ref = graph.get_node(target_id)
            if not target_ref:
                continue

            target_type = target_ref.artifact_type
            matched_rules = match_rule(source_type, target_type, change_type)

            # Default if no rule matches
            if not matched_rules:
                matched_rules = [("UNKNOWN", ImpactSeverity.REVIEW, f"{source_id} changed; {target_id} may be affected")]

            for rule_id, severity, reason in matched_rules:
                finding_key = f"{source_id}→{target_id}"
                if finding_key not in findings:
                    preservation = _infer_preservation(target_ref, change, graph, all_artifacts)
                    findings[finding_key] = ImpactFinding(
                        source_change=change,
                        affected_artifact=target_ref,
                        is_direct=True,
                        severity=severity,
                        rule_id=rule_id,
                        reason=reason,
                        dependency_path=[source_id, target_id],
                        preservation=preservation,
                        recommended_action=_recommend_action(severity, target_ref),
                        authority_required=_authority_for_severity(severity),
                    )

        # Transitive dependents
        transitive = graph.transitive_dependents(source_id)
        for target_id, dep_path in transitive.items():
            if target_id == source_id:
                continue
            # Skip if already handled as direct
            already_direct = any(
                f.affected_artifact and f.affected_artifact.artifact_id == target_id and f.is_direct
                for f in findings.values()
            )
            if already_direct:
                continue

            target_ref = graph.get_node(target_id)
            if not target_ref:
                continue

            target_type = target_ref.artifact_type
            matched_rules = match_rule(source_type, target_type, change_type)
            if not matched_rules:
                matched_rules = [("UNKNOWN", ImpactSeverity.REVIEW,
                                 f"Transitive impact from {source_id} through {dep_path}")]

            for rule_id, severity, reason in matched_rules:
                # Reduce severity for transitive (one level down)
                if severity == ImpactSeverity.BLOCKED:
                    transit_severity = ImpactSeverity.REGENERATE_CANDIDATE
                elif severity == ImpactSeverity.REGENERATE_CANDIDATE:
                    transit_severity = ImpactSeverity.REVIEW
                elif severity == ImpactSeverity.RECONCILE:
                    transit_severity = ImpactSeverity.REVIEW
                else:
                    transit_severity = severity

                finding_key = f"{source_id}→→{target_id}"
                if finding_key not in findings:
                    preservation = PreservationStatus.UNKNOWN if target_ref.accepted else PreservationStatus.REGENERATE
                    findings[finding_key] = ImpactFinding(
                        source_change=change,
                        affected_artifact=target_ref,
                        is_direct=False,
                        severity=transit_severity,
                        rule_id=rule_id,
                        reason=reason,
                        dependency_path=dep_path,
                        preservation=preservation,
                        recommended_action=_recommend_action(transit_severity, target_ref),
                        authority_required=_authority_for_severity(transit_severity),
                    )

    # For artifacts not affected by any change, mark as NONE
    for aid, ref in all_artifacts.items():
        if aid not in change_map:
            is_affected = any(
                f.affected_artifact and f.affected_artifact.artifact_id == aid
                for f in findings.values()
            )
            if not is_affected:
                finding_key = f"nochange:{aid}"
                findings[finding_key] = ImpactFinding(
                    affected_artifact=ref,
                    is_direct=True,
                    severity=ImpactSeverity.NONE,
                    rule_id="R016",
                    reason=f"{aid} unchanged; no impact",
                    preservation=PreservationStatus.PRESERVE,
                    recommended_action="No action required",
                    authority_required="read_only",
                )

    return _deduplicate_findings(list(findings.values()))


def _deduplicate_findings(findings: list[ImpactFinding]) -> list[ImpactFinding]:
    """Deduplicate findings for the same artifact, keeping highest severity."""
    from auteur.impact.rules import SEVERITY_ORDER, highest_severity
    best_per_artifact: dict[str, ImpactFinding] = {}
    for f in findings:
        if not f.affected_artifact:
            continue
        aid = f.affected_artifact.artifact_id
        if aid not in best_per_artifact:
            best_per_artifact[aid] = f
        else:
            existing = best_per_artifact[aid]
            combined = highest_severity([existing.severity, f.severity])
            if combined == f.severity and combined != existing.severity:
                f.dependency_path = list(set(existing.dependency_path + f.dependency_path))
                best_per_artifact[aid] = f
            else:
                existing.dependency_path = list(set(existing.dependency_path + f.dependency_path))

    return sorted(best_per_artifact.values(), key=lambda f: (f.affected_artifact.artifact_id if f.affected_artifact else ""))


def _infer_preservation(
    ref: ArtifactRef,
    change: ChangeRecord,
    graph: DependencyGraph,
    all_artifacts: dict[str, ArtifactRef],
) -> PreservationStatus:
    """Infer preservation status for an affected artifact."""
    if change.change_type == ChangeType.ARTIFACT_REMOVED:
        return PreservationStatus.REGENERATE
    if ref.accepted and change.change_type == ChangeType.CONTENT_CHANGED:
        if change.previous_hash == change.current_hash:
            return PreservationStatus.PRESERVE
        if change.previous_hash and change.current_hash:
            return PreservationStatus.PRESERVE_WITH_REVIEW
    if ref.accepted:
        return PreservationStatus.PRESERVE_WITH_REVIEW
    # Non-accepted derived artifacts
    if ref.authority == "derived":
        return PreservationStatus.REGENERATE
    return PreservationStatus.UNKNOWN


def _recommend_action(severity: ImpactSeverity, ref: ArtifactRef) -> str:
    if severity == ImpactSeverity.BLOCKED:
        return f"Resolve upstream changes before progressing {ref.artifact_id}"
    if severity == ImpactSeverity.RECONCILE:
        return f"Reconcile {ref.artifact_id} with updated source"
    if severity == ImpactSeverity.REGENERATE_CANDIDATE:
        return f"Regenerate {ref.artifact_id} as candidate"
    if severity == ImpactSeverity.REVIEW:
        return f"Inspect {ref.artifact_id} for potential impact"
    return "No action required"


def _authority_for_severity(severity: ImpactSeverity) -> str:
    if severity == ImpactSeverity.BLOCKED:
        return "authority_bearing"
    if severity in (ImpactSeverity.RECONCILE, ImpactSeverity.REGENERATE_CANDIDATE):
        return "candidate_generation"
    return "read_only"


class ImpactAnalyzer:
    """Orchestrates change detection, impact propagation, and preservation inference."""

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self.store = ArtifactStore(self.project_root)

    def _resolve_artifact_path(self, artifact_id: str) -> str:
        """Resolve the file path for an artifact ID using known patterns."""
        known_paths = {
            "story_identity": "story_identity.yaml",
            "blueprint": "blueprint.yaml",
        }
        if artifact_id in known_paths:
            return known_paths[artifact_id]
        if artifact_id.startswith("chapter_"):
            ch_num = artifact_id.replace("chapter_", "")
            if ch_num.isdigit():
                return f"chapters/{ch_num}/outline.yaml"
        if artifact_id.startswith("scene_"):
            parts = artifact_id.split("_")
            if len(parts) == 2:
                return f"chapters/{parts[1]}/{artifact_id}.yaml"
            if len(parts) >= 3:
                return f"chapters/{parts[1]}/{parts[0]}_{parts[1]}_{parts[2]}.yaml"
        return ""

    def build_graph(self) -> DependencyGraph:
        """Build a dependency graph from the project's provenance data."""
        graph = DependencyGraph()
        store = self.store

        # Discover all artifacts from provenance store
        sidecar_root = store.root
        artifact_refs: dict[str, ArtifactRef] = {}
        if sidecar_root.exists():
            for sidecar_file in sorted(sidecar_root.glob("*.yaml")):
                try:
                    meta = store.current(sidecar_file.stem)
                    if not meta:
                        continue
                    file_path = self._resolve_artifact_path(meta.artifact_id)
                    ref = ArtifactRef(
                        artifact_id=meta.artifact_id,
                        artifact_type=meta.artifact_type,
                        content_hash=meta.content_hash,
                        authority=meta.authority,
                        accepted=meta.lifecycle.value == "accepted" if hasattr(meta.lifecycle, 'value') else False,
                        file_path=file_path,
                    )
                    artifact_refs[meta.artifact_id] = ref
                    graph.add_node(ref)
                except (OSError, yaml.YAMLError):
                    continue

        # Add edges from provenance dependency records
        if sidecar_root.exists():
            for sidecar_file in sorted(sidecar_root.glob("*.yaml")):
                try:
                    meta = store.current(sidecar_file.stem)
                    if not meta:
                        continue
                    for dep in meta.dependencies:
                        if dep.artifact_id in artifact_refs:
                            graph.add_edge(
                                dep.artifact_id,
                                meta.artifact_id,
                                kind=dep.kind.value if hasattr(dep.kind, 'value') else str(dep.kind),
                                source=dep.source.value if hasattr(dep.source, 'value') else str(dep.source),
                                fields=tuple(dep.fields) if dep.fields else tuple(dep.projection.fields if dep.projection else []),
                                rule_id="PROVENANCE",
                            )
                except (OSError, yaml.YAMLError):
                    continue

        # Add standard workflow edges for any missing relationships
        graph.add_standard_workflow_edges()

        return graph

    def detect_changes(
        self,
        graph: DependencyGraph | None = None,
    ) -> list[ChangeRecord]:
        """Detect changes between stored provenance and current files."""
        if graph is None:
            graph = self.build_graph()
        return _detect_changes(self.store, graph.nodes())

    def analyze(
        self,
        graph: DependencyGraph | None = None,
        changes: list[ChangeRecord] | None = None,
    ) -> list[ImpactFinding]:
        """Run full impact analysis."""
        if graph is None:
            graph = self.build_graph()
        if changes is None:
            changes = self.detect_changes(graph)
        return _classify_impact(graph, changes, graph.nodes())

    def has_unresolved_impact(self, findings: list[ImpactFinding] | None = None) -> bool:
        """Check if there are unresolved high-priority impact findings."""
        if findings is None:
            findings = self.analyze()
        for f in findings:
            if f.severity in (ImpactSeverity.BLOCKED, ImpactSeverity.RECONCILE, ImpactSeverity.REGENERATE_CANDIDATE):
                return True
        return False

    def workflow_actions(self, findings: list[ImpactFinding] | None = None) -> list[dict[str, Any]]:
        """Generate workflow-compatible action dicts from impact findings."""
        if findings is None:
            findings = self.analyze()
        actions: list[dict[str, Any]] = []
        for f in findings:
            if f.severity is ImpactSeverity.NONE:
                continue
            actions.append({
                "label": f.recommended_action or f"Handle {f.affected_artifact.artifact_id if f.affected_artifact else 'unknown'} impact",
                "command": f"auteur impact explain {f.finding_id}",
                "authority": f.authority_required,
                "description": f.reason,
                "auto_executable": f.authority_required in ("read_only", "candidate_generation"),
                "impact_finding_id": f.finding_id,
                "severity": f.severity.value if hasattr(f.severity, 'value') else str(f.severity),
            })
        return actions
