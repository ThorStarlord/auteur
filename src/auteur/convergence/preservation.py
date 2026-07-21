"""Preservation analysis — determine what can be kept during revision."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from auteur.convergence.models import (
    PreservedRegion,
    PreservationStatus,
    RevisionTarget,
)


def _read_yaml(path: Path) -> dict[str, Any] | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return None


def analyze_preservation(
    project: Path,
    target: RevisionTarget,
) -> list[PreservedRegion]:
    """Determine what can be preserved in a revision target.

    Uses impact evidence and stable structural boundaries.
    Returns a list of preserved regions with status.
    """
    regions: list[PreservedRegion] = []

    if target.scope.value in ("scene", "beat_range") and target.scene_id:
        regions.extend(_analyze_scene_regions(project, target))
    else:
        regions.extend(_analyze_chapter_regions(project, target))

    return regions


def _analyze_scene_regions(project: Path, target: RevisionTarget) -> list[PreservedRegion]:
    """Analyze preservation for a specific scene."""
    regions: list[PreservedRegion] = []

    scene_paths = [
        project / "chapters" / str(target.chapter_index) / "scenes" / f"{target.scene_id}.yaml",
        project / "chapters" / f"{target.chapter_index:02d}" / "scenes" / f"{target.scene_id}.yaml",
    ]

    scene_data = None
    for sp in scene_paths:
        data = _read_yaml(sp)
        if data:
            scene_data = data
            break

    if not scene_data:
        regions.append(PreservedRegion(
            scene_id=target.scene_id or "",
            status=PreservationStatus.UNKNOWN,
            reason="Scene file not found",
        ))
        return regions

    # Beat-level preservation
    beats = scene_data.get("beats", []) if isinstance(scene_data.get("beats"), list) else []
    for beat in beats:
        if isinstance(beat, dict):
            bid = beat.get("id", "")
            if target.beat_ids and bid not in target.beat_ids:
                regions.append(PreservedRegion(
                    scene_id=target.scene_id or "",
                    beat_id=bid,
                    status=PreservationStatus.PRESERVE,
                    reason="Beat outside revision scope",
                ))
            elif not target.beat_ids:
                regions.append(PreservedRegion(
                    scene_id=target.scene_id or "",
                    beat_id=bid,
                    status=PreservationStatus.PRESERVE_WITH_REVIEW,
                    reason="Scene-level revision; beat may be affected",
                ))

    # Location preservation
    location = scene_data.get("location", "")
    if location:
        regions.append(PreservedRegion(
            scene_id=target.scene_id or "",
            section_id="location",
            status=PreservationStatus.PRESERVE_WITH_REVIEW,
            reason="Location should be preserved if structurally valid",
        ))

    # Opening condition
    opening = scene_data.get("opening", "")
    if opening:
        regions.append(PreservedRegion(
            scene_id=target.scene_id or "",
            section_id="opening",
            status=PreservationStatus.PRESERVE_WITH_REVIEW,
            reason="Opening condition may be preserved unless conflicting with obligations",
        ))

    return regions


def _analyze_chapter_regions(project: Path, target: RevisionTarget) -> list[PreservedRegion]:
    """Analyze preservation for a chapter-level revision."""
    regions: list[PreservedRegion] = []

    outline_dirs = [
        project / "chapters" / str(target.chapter_index) / "outline.yaml",
        project / "chapters" / f"{target.chapter_index:02d}" / "outline.yaml",
    ]

    outline = None
    for d in outline_dirs:
        data = _read_yaml(d)
        if data:
            outline = data
            break

    if not outline:
        regions.append(PreservedRegion(
            status=PreservationStatus.UNKNOWN,
            reason=f"Chapter {target.chapter_index} outline not found",
        ))
        return regions

    scenes = outline.get("scenes", []) if isinstance(outline.get("scenes"), list) else []
    for scene in scenes:
        if isinstance(scene, dict):
            sid = scene.get("id", "")
            if target.scene_id and sid == target.scene_id:
                regions.append(PreservedRegion(
                    scene_id=sid,
                    status=PreservationStatus.REGENERATE,
                    reason="Target scene requires revision",
                ))
            else:
                regions.append(PreservedRegion(
                    scene_id=sid,
                    status=PreservationStatus.PRESERVE_WITH_REVIEW,
                    reason="Non-target scene; review entry/exit conditions for cascade effects",
                ))

    return regions
