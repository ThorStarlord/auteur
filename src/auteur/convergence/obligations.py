"""Source obligation collection — gather explicit requirements for repair."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from auteur.convergence.models import (
    ObligationKind,
    ObligationSource,
    RevisionTarget,
    SourceObligation,
)


def _read_yaml(path: Path) -> dict[str, Any] | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return None


def collect_obligations(
    project: Path,
    target: RevisionTarget,
) -> list[SourceObligation]:
    """Collect explicit obligations from all available sources.

    Sources checked:
    - Story identity
    - Blueprint (structure)
    - Chapter outline
    - Scene purpose (from scene file)
    - Impact findings
    - Character-state inputs
    """
    obligations: list[SourceObligation] = []

    obligations.extend(_from_story_identity(project))
    obligations.extend(_from_blueprint(project, target))
    obligations.extend(_from_chapter_outline(project, target))
    obligations.extend(_from_scene_purpose(project, target))
    obligations.extend(_from_impact(project, target))

    return _deduplicate(obligations)


def _from_story_identity(project: Path) -> list[SourceObligation]:
    """Extract obligations from story_identity.yaml."""
    result = []
    identity = _read_yaml(project / "story_identity.yaml")
    if not identity:
        return result

    story_type = identity.get("story_type", {}) if isinstance(identity.get("story_type"), dict) else {}
    genre = story_type.get("genre", "")
    mode = story_type.get("mode", "")
    medium = story_type.get("medium", "")

    if genre:
        result.append(SourceObligation(
            source=ObligationSource.STORY_IDENTITY,
            kind=ObligationKind.REQUIRED,
            description=f"Story genre: {genre}",
            scope="global",
            authority="canonical",
            source_artifact_id="story_identity",
            evidence=f"genre={genre}",
        ))
    if mode:
        result.append(SourceObligation(
            source=ObligationSource.STORY_IDENTITY,
            kind=ObligationKind.REQUIRED,
            description=f"Story mode: {mode}",
            scope="global",
            authority="canonical",
            source_artifact_id="story_identity",
            evidence=f"mode={mode}",
        ))
    if medium:
        result.append(SourceObligation(
            source=ObligationSource.STORY_IDENTITY,
            kind=ObligationKind.ADVISORY,
            description=f"Story medium: {medium}",
            scope="global",
            authority="canonical",
            source_artifact_id="story_identity",
            evidence=f"medium={medium}",
        ))

    return result


def _from_blueprint(project: Path, target: RevisionTarget) -> list[SourceObligation]:
    """Extract obligations from blueprint chapter structure."""
    result = []
    blueprint = _read_yaml(project / "blueprint.yaml")
    if not blueprint:
        return result

    chapters = blueprint.get("chapters", {}) if isinstance(blueprint.get("chapters"), dict) else {}
    chapter_key = f"chapter_{target.chapter_index:02d}"
    chapter = chapters.get(chapter_key, {}) if isinstance(chapters, dict) else {}

    if isinstance(chapter, dict):
        purpose = chapter.get("purpose", "")
        if purpose:
            result.append(SourceObligation(
                source=ObligationSource.STRUCTURE,
                kind=ObligationKind.REQUIRED,
                description=f"Chapter {target.chapter_index} purpose: {purpose}",
                scope=f"chapter_{target.chapter_index:02d}",
                authority="canonical",
                source_artifact_id="blueprint",
                evidence=f"chapters.{chapter_key}.purpose={purpose}",
            ))

    return result


def _from_chapter_outline(project: Path, target: RevisionTarget) -> list[SourceObligation]:
    """Extract obligations from chapter outline."""
    result = []

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
        return result

    scenes = outline.get("scenes", []) if isinstance(outline.get("scenes"), list) else []
    for scene in scenes:
        if isinstance(scene, dict):
            sid = scene.get("id", "")
            if target.scene_id and sid != target.scene_id:
                continue
            purpose = scene.get("purpose", "")
            if purpose:
                result.append(SourceObligation(
                    source=ObligationSource.CHAPTER_OUTLINE,
                    kind=ObligationKind.REQUIRED,
                    description=f"Scene {sid} purpose: {purpose}",
                    scope=f"scene_{sid}",
                    authority="canonical",
                    source_artifact_id=f"outline_{target.chapter_index:02d}",
                    evidence=f"scenes.{sid}.purpose={purpose}",
                ))

    return result


def _from_scene_purpose(project: Path, target: RevisionTarget) -> list[SourceObligation]:
    """Extract obligations from scene realization files."""
    result = []

    if not target.scene_id:
        return result

    scene_dirs = [
        project / "chapters" / str(target.chapter_index) / "scenes" / f"{target.scene_id}.yaml",
        project / "chapters" / f"{target.chapter_index:02d}" / "scenes" / f"{target.scene_id}.yaml",
    ]

    for d in scene_dirs:
        data = _read_yaml(d)
        if data:
            purpose = data.get("purpose", "")
            if purpose:
                result.append(SourceObligation(
                    source=ObligationSource.SCENE_PURPOSE,
                    kind=ObligationKind.REQUIRED,
                    description=f"Scene purpose: {purpose}",
                    scope=target.scene_id,
                    authority="canonical",
                    source_artifact_id=target.scene_id,
                    evidence=f"purpose={purpose}",
                ))

            beats = data.get("beats", []) if isinstance(data.get("beats"), list) else []
            for beat in beats:
                if isinstance(beat, dict):
                    bid = beat.get("id", "")
                    bdesc = beat.get("description", "")
                    if bdesc:
                        result.append(SourceObligation(
                            source=ObligationSource.BEAT_DECLARATION,
                            kind=ObligationKind.REQUIRED,
                            description=f"Beat {bid}: {bdesc}",
                            scope=f"{target.scene_id}.{bid}",
                            authority="canonical",
                            source_artifact_id=target.scene_id,
                            evidence=f"beats.{bid}.description={bdesc}",
                        ))
            break

    return result


def _from_impact(project: Path, target: RevisionTarget) -> list[SourceObligation]:
    """Extract obligations from impact findings."""
    result = []

    if not target.impact_finding_id:
        return result

    for impact_file in (project / ".auteur" / "impact").rglob("*.yaml"):
        data = _read_yaml(impact_file)
        if not data:
            continue
        findings = data.get("findings", []) if isinstance(data.get("findings"), list) else []
        for finding in findings:
            if isinstance(finding, dict) and finding.get("finding_id") == target.impact_finding_id:
                reason = finding.get("reason", "")
                if reason:
                    result.append(SourceObligation(
                        source=ObligationSource.IMPACT_FINDING,
                        kind=ObligationKind.REQUIRED,
                        description=f"Impact: {reason}",
                        scope=target.scene_id or f"chapter_{target.chapter_index:02d}",
                        authority="derived",
                        source_artifact_id=target.impact_finding_id,
                        evidence=reason,
                    ))
                break

    return result


def _deduplicate(obligations: list[SourceObligation]) -> list[SourceObligation]:
    """Remove duplicate obligations based on description."""
    seen: set[str] = set()
    unique: list[SourceObligation] = []
    for ob in obligations:
        key = f"{ob.source.value}:{ob.description}"
        if key not in seen:
            seen.add(key)
            unique.append(ob)
    return unique
