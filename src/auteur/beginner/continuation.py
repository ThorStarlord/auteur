"""Deterministic Chapter N -> N+1 planning projections."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .post_draft import project_next_chapter_context


@dataclass(frozen=True)
class ContinuationState:
    current_chapter_index: int


@dataclass(frozen=True)
class AcceptedChapterOutcome:
    chapter_index: int
    summary: str | None
    deltas: dict[str, Any]
    source_ref: str


@dataclass(frozen=True)
class DraftHandoff:
    chapter_index: int
    ready: bool
    source_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScenePlan:
    chapter_index: int
    scene_id: str
    purpose: str | None = None


@dataclass(frozen=True)
class ChapterPlan:
    chapter_index: int
    continuation: ContinuationState
    intended_role: str | None
    context: dict[str, Any]
    divergences: list[dict[str, Any]]
    source_refs: list[str]
    draft_handoff_ready: bool
    draft_handoff: DraftHandoff


def _chapter_dir(root: Path, index: int) -> Path:
    padded = root / "chapters" / f"{index:02d}"
    return padded if padded.is_dir() else root / "chapters" / str(index)


def _yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _bible_events(root: Path) -> list[dict[str, Any]]:
    path = root / "bible.json"
    if not path.is_file():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    events = value.get("events", []) if isinstance(value, dict) else []
    return [event for event in events if isinstance(event, dict)] if isinstance(events, list) else []


def _role(root: Path, chapter_index: int) -> tuple[str | None, str | None]:
    chapter_outline = _chapter_dir(root, chapter_index) / "outline.yaml"
    if chapter_outline.is_file():
        data = _yaml(chapter_outline)
        role = data.get("chapter_summary") or data.get("purpose") or data.get("role")
        return role if isinstance(role, str) else None, chapter_outline.relative_to(root).as_posix()
    whole_outline = root / "outline.yaml"
    data = _yaml(whole_outline)
    chapters = data.get("chapters")
    if isinstance(chapters, list):
        for item in chapters:
            if isinstance(item, dict) and item.get("chapter_index") == chapter_index:
                role = item.get("chapter_summary") or item.get("purpose") or item.get("role")
                return role if isinstance(role, str) else None, whole_outline.relative_to(root).as_posix()
    return None, None


def _divergences(root: Path, prior_chapter: int, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expected = _yaml(_chapter_dir(root, prior_chapter) / "outline.yaml").get("expected_state")
    if not isinstance(expected, dict):
        return []
    accepted: dict[str, Any] = {}
    for event in events:
        if event.get("chapter_index") == prior_chapter and isinstance(event.get("deltas"), dict):
            accepted.update(event["deltas"])
    return [
        {
            "field": field,
            "planned": planned,
            "accepted": accepted[field],
            "recommendation": "adapt the next chapter to the accepted state",
        }
        for field, planned in expected.items()
        if field in accepted and accepted[field] != planned
    ]


def build_chapter_plan(project_root: Path, chapter_index: int) -> ChapterPlan:
    """Build a next-chapter plan from accepted state and explicit structure inputs."""
    if chapter_index < 1:
        raise ValueError("chapter_index must be positive")
    context = project_next_chapter_context(project_root, chapter_index)
    events = _bible_events(project_root)
    prior_state = [
        event for event in events if isinstance(event.get("chapter_index"), int) and event["chapter_index"] < chapter_index
    ]
    context = dict(context)
    context["accepted_prior_state"] = prior_state
    context["whole_story_structure"] = [
        ref for ref in ("story_identity.yaml", "blueprint.yaml", "outline.yaml") if (project_root / ref).is_file()
    ]
    role, role_ref = _role(project_root, chapter_index)
    source_refs = list(context.get("prior_chapter_refs", []))
    source_paths = [ref["path"] for ref in source_refs]
    source_paths.extend(context["whole_story_structure"])
    if (project_root / "bible.json").is_file():
        source_paths.append("bible.json")
    if role_ref and role_ref not in source_paths:
        source_paths.append(role_ref)
    handoff = DraftHandoff(chapter_index, ready=role is not None or bool(context.get("prior_accepted_chapters")), source_refs=source_paths)
    return ChapterPlan(
        chapter_index=chapter_index,
        continuation=ContinuationState(chapter_index),
        intended_role=role,
        context=context,
        divergences=_divergences(project_root, chapter_index - 1, events),
        source_refs=source_paths,
        draft_handoff_ready=handoff.ready,
        draft_handoff=handoff,
    )


def build_scene_plans(project_root: Path, chapter_index: int) -> list[ScenePlan]:
    data = _yaml(_chapter_dir(project_root, chapter_index) / "outline.yaml")
    scenes = data.get("scenes")
    if not isinstance(scenes, list):
        return []
    return [
        ScenePlan(chapter_index, str(scene["id"]), scene.get("purpose") if isinstance(scene.get("purpose"), str) else None)
        for scene in scenes
        if isinstance(scene, dict) and scene.get("id") is not None
    ]
