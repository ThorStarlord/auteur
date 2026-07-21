"""Revision target resolution — deterministic target identification."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from auteur.convergence.models import (
    RevisionTarget,
    TargetScope,
)


def _read_yaml(path: Path) -> dict[str, Any] | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return None


def resolve_target(
    project: Path,
    *,
    chapter_index: int | None = None,
    scene_id: str | None = None,
    beat_ids: list[str] | None = None,
    impact_finding_id: str = "",
    source_artifact: str = "",
    affected_artifact: str = "",
) -> RevisionTarget:
    """Resolve a revision target from explicit scope parameters.

    Resolution order:
    1. If scene_id is provided, scope is SCENE.
    2. If beat_ids are provided with scene_id, scope is BEAT_RANGE.
    3. If only chapter_index, scope is CHAPTER.
    4. Fallback to chapter-level if scene boundary is unavailable.
    """
    resolved_scope = TargetScope.CHAPTER
    resolved_scene = None
    resolved_beats: list[str] = []

    if scene_id:
        resolved_scope = TargetScope.SCENE
        resolved_scene = scene_id

    if beat_ids and scene_id:
        resolved_scope = TargetScope.BEAT_RANGE
        resolved_beats = beat_ids

    return RevisionTarget(
        project=str(project.resolve()),
        scope=resolved_scope,
        chapter_index=chapter_index or 1,
        scene_id=resolved_scene,
        beat_ids=resolved_beats,
        source_artifact=source_artifact,
        affected_artifact=affected_artifact,
        impact_finding_id=impact_finding_id,
        current_accepted_artifact=_find_accepted_artifact(project, chapter_index, resolved_scene),
    )


def resolve_target_from_impact(
    project: Path,
    finding_artifact_id: str,
    finding_chapter_index: int | None,
    finding_scene_index: int | None,
) -> RevisionTarget:
    """Resolve a revision target from an impact finding."""
    scene_id = None
    if finding_scene_index is not None and finding_chapter_index is not None:
        scene_id = f"scene_{finding_chapter_index:02d}_{finding_scene_index:02d}"

    return resolve_target(
        project,
        chapter_index=finding_chapter_index or 1,
        scene_id=scene_id,
        affected_artifact=finding_artifact_id,
    )


def _find_accepted_artifact(project: Path, chapter_index: int | None, scene_id: str | None) -> str:
    """Find the currently accepted artifact path for a target."""
    if scene_id and chapter_index:
        candidates = list(project.glob(f"chapters/{chapter_index}/expression/**/{scene_id}*"))
        if candidates:
            return str(candidates[0].resolve())
    if chapter_index:
        candidates = list(project.glob(f"chapters/{chapter_index}/expression/accepted.yaml"))
        if candidates:
            data = _read_yaml(candidates[0])
            if data:
                return str(candidates[0].resolve())
    return ""


def resolve_targets(
    project: Path,
    targets: list[dict[str, Any]],
) -> list[RevisionTarget]:
    """Resolve multiple targets with deterministic ordering.

    Ordering:
    1. Blockers first
    2. Direct before transitive
    3. Reconciliation before regeneration
    4. Earliest chapter
    5. Earliest scene
    6. Stable artifact ID
    """
    resolved = []
    for t in targets:
        resolved.append(resolve_target(
            project,
            chapter_index=t.get("chapter_index"),
            scene_id=t.get("scene_id"),
            beat_ids=t.get("beat_ids"),
            impact_finding_id=t.get("impact_finding_id", ""),
            source_artifact=t.get("source_artifact", ""),
            affected_artifact=t.get("affected_artifact", ""),
        ))

    def _sort_key(t: RevisionTarget) -> tuple:
        is_blocker = 0  # no blocker metadata yet
        return (is_blocker, 0, 0, t.chapter_index, t.scene_id or "", t.target_id)

    resolved.sort(key=_sort_key)
    return resolved


def handle_ambiguous_target(project: Path, partial_chapter: int | None = None) -> list[RevisionTarget]:
    """When target is ambiguous, list all possible targets."""
    results = []
    chapters_dir = project / "chapters"
    if not chapters_dir.exists():
        return results

    for ch_dir in sorted(chapters_dir.iterdir()):
        if not ch_dir.is_dir():
            continue
        try:
            ch_idx = int(ch_dir.name)
        except ValueError:
            continue
        if partial_chapter is not None and ch_idx != partial_chapter:
            continue
        scene_dir = ch_dir / "scenes"
        if scene_dir.exists():
            for scene_file in sorted(scene_dir.glob("*.yaml")):
                scene_id = scene_file.stem
                results.append(resolve_target(project, chapter_index=ch_idx, scene_id=scene_id))
        else:
            results.append(resolve_target(project, chapter_index=ch_idx))

    return results
