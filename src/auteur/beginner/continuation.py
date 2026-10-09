from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
import yaml

from .author_context import compose_author_context


class OutlineChapter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter_index: int = Field(ge=1)
    role: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    advancing_threads: tuple[str, ...] = ()
    character_pressure: str = Field(min_length=1)
    setup: tuple[str, ...] = ()
    payoff: tuple[str, ...] = ()
    reader_after: str = Field(min_length=1)


class OutlineProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_refs: tuple[str, ...] = Field(min_length=1)
    source_fingerprint: str = ""
    chapters: tuple[OutlineChapter, ...]


class ChapterPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter_index: int = Field(ge=1)
    role: str = Field(min_length=1)
    what_changes: str = Field(min_length=1)
    advancing_threads: tuple[str, ...] = ()
    character_pressure: str = Field(min_length=1)
    setup: tuple[str, ...] = ()
    payoff: tuple[str, ...] = ()
    reader_knows: str = Field(min_length=1)
    reader_feels: str = Field(min_length=1)
    recommended_shape: str = Field(min_length=1)


class ScenePlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    pov: str = Field(min_length=1)
    entry_state: str = Field(min_length=1)
    immediate_goal: str = Field(min_length=1)
    conflict: str = Field(min_length=1)
    important_change: str = Field(min_length=1)
    ending_state: str = Field(min_length=1)
    continuity_constraints: tuple[str, ...] = ()


class DraftHandoff(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter_index: int = Field(ge=1)
    accepted_inputs: tuple[str, ...] = Field(min_length=1)
    command: str = Field(min_length=1)
    status: str = "ready"
    source_fingerprint: str = ""


class ContinuationState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outline_proposal: OutlineProposal | None = None
    outline_accepted: bool = False
    chapter_plan: ChapterPlan | None = None
    chapter_plan_accepted: bool = False
    scene_plans: tuple[ScenePlan, ...] = ()
    scene_plans_accepted: bool = False
    draft_handoff: DraftHandoff | None = None
    draft_status: str = "not_started"
    stale: bool = False
    stale_reason: str | None = None


def accepted_milestone_fingerprint(references: Iterable[object]) -> str:
    """Return a stable digest for the accepted upstream inputs."""
    payload = []
    for reference in references:
        if hasattr(reference, "model_dump"):
            payload.append(reference.model_dump(mode="json"))
        else:
            payload.append(reference)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def derive_outline_chapters(project_root, *, premise: str) -> tuple[OutlineChapter, ...]:
    """Adapt an existing Cartographer outline when one is already available.

    The fallback is intentionally small and deterministic: it creates one
    reviewable Chapter 1 purpose without pretending that a full outline was
    authored by an LLM.
    """
    candidates = (
        project_root / "cartographer_outline.yaml",
        project_root / "chapters" / "01" / "outline.yaml",
    )
    for path in candidates:
        if not path.is_file():
            continue
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            continue
        raw_chapters = payload.get("chapters") if isinstance(payload, dict) else None
        if raw_chapters is None and isinstance(payload, dict):
            raw_chapters = [payload]
        if not isinstance(raw_chapters, list):
            continue
        chapters: list[OutlineChapter] = []
        for position, raw in enumerate(raw_chapters, start=1):
            if not isinstance(raw, dict):
                continue
            summary = str(raw.get("chapter_summary") or raw.get("summary") or premise)
            scenes = raw.get("scenes") or []
            scene_summary = ""
            if isinstance(scenes, list) and scenes and isinstance(scenes[0], dict):
                scene_summary = str(scenes[0].get("summary") or "")
            chapters.append(
                OutlineChapter(
                    chapter_index=int(raw.get("index") or position),
                    role="Advance the accepted whole-story structure",
                    purpose=summary,
                    advancing_threads=("main",),
                    character_pressure=scene_summary or "Apply the next pressure implied by the accepted structure.",
                    setup=tuple(str(item) for item in raw.get("setup", ()) if item),
                    payoff=tuple(str(item) for item in raw.get("payoff", ()) if item),
                    reader_after=summary,
                )
            )
        if chapters:
            return tuple(chapters)
    return (
        OutlineChapter(
            chapter_index=1,
            role="Open the story's central pressure",
            purpose=f"Turn the premise into an active problem: {premise}",
            advancing_threads=("main",),
            character_pressure="The protagonist must respond to the first meaningful disruption.",
            setup=("The premise's unanswered question",),
            payoff=(),
            reader_after="The reader understands what can no longer remain safely unchanged.",
        ),
    )


class ChapterContinuationState(BaseModel):
    """Derived Chapter N -> N+1 position; never canonical story state."""

    model_config = ConfigDict(extra="forbid")

    current_chapter_index: int = Field(ge=1)


class AcceptedChapterOutcome(BaseModel):
    """Accepted prior-chapter state used only as contextual planning evidence."""

    model_config = ConfigDict(extra="forbid")

    chapter_index: int = Field(ge=1)
    summary: str | None = None
    deltas: dict[str, Any] = Field(default_factory=dict)
    source_ref: str = Field(min_length=1)


class ContextualDraftHandoff(BaseModel):
    """Derived readiness projection for the existing draft workflow."""

    model_config = ConfigDict(extra="forbid")

    chapter_index: int = Field(ge=1)
    ready: bool
    source_refs: tuple[str, ...] = ()


class ContextualScenePlan(BaseModel):
    """Lightweight chapter-owned scene projection for continuation planning."""

    model_config = ConfigDict(extra="forbid")

    chapter_index: int = Field(ge=1)
    scene_id: str = Field(min_length=1)
    purpose: str | None = None


class ContextualChapterPlan(BaseModel):
    """Derived continuation plan built from accepted prior state and Structure."""

    model_config = ConfigDict(extra="forbid")

    chapter_index: int = Field(ge=1)
    continuation: ChapterContinuationState
    intended_role: str | None = None
    context: dict[str, Any]
    divergences: tuple[dict[str, Any], ...] = ()
    source_refs: tuple[str, ...] = ()
    draft_handoff_ready: bool
    draft_handoff: ContextualDraftHandoff


def _chapter_dir(project_root: Path, chapter_index: int) -> Path:
    padded = project_root / "chapters" / f"{chapter_index:02d}"
    if padded.is_dir():
        return padded
    return project_root / "chapters" / str(chapter_index)


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return value if isinstance(value, dict) else {}


def _accepted_bible_events(project_root: Path) -> list[dict[str, Any]]:
    path = project_root / "bible.json"
    if not path.is_file():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    events = value.get("events", []) if isinstance(value, dict) else []
    if not isinstance(events, list):
        return []
    return [event for event in events if isinstance(event, dict)]


def _chapter_role(project_root: Path, chapter_index: int) -> tuple[str | None, str | None]:
    chapter_outline = _chapter_dir(project_root, chapter_index) / "outline.yaml"
    if chapter_outline.is_file():
        data = _load_yaml_mapping(chapter_outline)
        role = data.get("chapter_summary") or data.get("purpose") or data.get("role")
        return (
            role if isinstance(role, str) and role.strip() else None,
            chapter_outline.relative_to(project_root).as_posix(),
        )

    for whole_outline in (project_root / "outline.yaml", project_root / "cartographer_outline.yaml"):
        data = _load_yaml_mapping(whole_outline)
        chapters = data.get("chapters")
        if not isinstance(chapters, list):
            continue
        for item in chapters:
            if not isinstance(item, dict):
                continue
            index = item.get("chapter_index") or item.get("index")
            if index != chapter_index:
                continue
            role = item.get("chapter_summary") or item.get("purpose") or item.get("role")
            return (
                role if isinstance(role, str) and role.strip() else None,
                whole_outline.relative_to(project_root).as_posix(),
            )
    return None, None


def _structure_divergences(
    project_root: Path,
    prior_chapter: int,
    events: list[dict[str, Any]],
) -> tuple[dict[str, Any], ...]:
    if prior_chapter < 1:
        return ()
    expected = _load_yaml_mapping(_chapter_dir(project_root, prior_chapter) / "outline.yaml").get(
        "expected_state"
    )
    if not isinstance(expected, dict):
        return ()
    accepted: dict[str, Any] = {}
    for event in events:
        if event.get("chapter_index") == prior_chapter and isinstance(event.get("deltas"), dict):
            accepted.update(event["deltas"])
    return tuple(
        {
            "field": field,
            "planned": planned,
            "accepted": accepted[field],
            "recommendation": "adapt the next chapter to the accepted state",
        }
        for field, planned in expected.items()
        if field in accepted and accepted[field] != planned
    )


def build_contextual_chapter_plan(
    project_root: Path,
    chapter_index: int,
) -> ContextualChapterPlan:
    """Build Chapter N planning context without mutating Structure or canon."""
    if chapter_index < 1:
        raise ValueError("chapter_index must be positive")

    from .post_draft import project_next_chapter_context

    context = dict(project_next_chapter_context(project_root, chapter_index))
    events = _accepted_bible_events(project_root)
    context["whole_story_structure"] = [
        ref
        for ref in ("story_identity.yaml", "blueprint.yaml", "outline.yaml", "cartographer_outline.yaml")
        if (project_root / ref).is_file()
    ]

    role, role_ref = _chapter_role(project_root, chapter_index)
    prior_refs = context.get("prior_chapter_refs", [])
    current_outline = _load_yaml_mapping(_chapter_dir(project_root, chapter_index) / "outline.yaml")

    # F2 uses a compact generation-facing context while preserving every
    # accepted Chapter/event as addressable evidence. Book orientation already
    # owns current pending/stale projection, so reuse it instead of inventing a
    # second reconciliation owner here.
    from .book_orientation import project_book_orientation

    orientation = project_book_orientation(project_root)
    accepted_expressions: list[dict[str, Any]] = []
    for ref in prior_refs:
        if not isinstance(ref, dict):
            continue
        source = ref.get("path")
        index = ref.get("chapter_index")
        if not isinstance(source, str) or type(index) is not int:
            continue
        path = project_root / source
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            # Book orientation already projects unreadable kept Chapters as
            # Needs-attention evidence. Do not fabricate replacement prose.
            continue
        accepted_expressions.append(
            {"chapter_index": index, "source_ref": source, "text": text}
        )

    author_context = compose_author_context(
        chapter_index=chapter_index,
        role=role,
        role_ref=role_ref,
        current_outline=current_outline,
        accepted_events=events,
        prior_chapter_refs=[
            ref for ref in prior_refs if isinstance(ref, dict)
        ],
        structure_refs=context["whole_story_structure"],
        accepted_expressions=accepted_expressions,
        pending_updates=[
            item.model_dump(mode="json") for item in orientation.pending_updates
        ],
        needs_attention=[
            item.model_dump(mode="json") for item in orientation.needs_attention
        ],
    )
    context["author_context"] = author_context
    # Preserve compatibility keys, but make them point at the same bounded,
    # provenance-aware evidence rather than the complete raw Bible payload.
    context["accepted_prior_state"] = author_context["accepted_history"]
    context["realized_state"] = author_context["accepted_state"]

    source_refs = [
        ref["path"]
        for ref in prior_refs
        if isinstance(ref, dict) and isinstance(ref.get("path"), str)
    ]
    source_refs.extend(context["whole_story_structure"])
    if (project_root / "bible.json").is_file():
        source_refs.append("bible.json")
    if role_ref and role_ref not in source_refs:
        source_refs.append(role_ref)
    source_refs.extend(
        item["source_ref"]
        for bucket in ("pending_updates", "uncertainty")
        for item in author_context[bucket]
        if item.get("source_ref")
    )

    # An explicitly requested but missing accepted source would mislead the
    # dependent generation step. Keep the uncertainty visible and fail closed.
    unresolved_sources = author_context["evidence_index"]["unresolved_explicit_source_refs"]
    handoff = ContextualDraftHandoff(
        chapter_index=chapter_index,
        ready=(
            (role is not None or bool(context.get("prior_accepted_chapters")))
            and not unresolved_sources
        ),
        source_refs=tuple(dict.fromkeys(source_refs)),
    )
    return ContextualChapterPlan(
        chapter_index=chapter_index,
        continuation=ChapterContinuationState(current_chapter_index=chapter_index),
        intended_role=role,
        context=context,
        divergences=_structure_divergences(project_root, chapter_index - 1, events),
        source_refs=handoff.source_refs,
        draft_handoff_ready=handoff.ready,
        draft_handoff=handoff,
    )


def build_contextual_scene_plans(
    project_root: Path,
    chapter_index: int,
) -> tuple[ContextualScenePlan, ...]:
    """Project scene ownership from the current chapter outline only."""
    data = _load_yaml_mapping(_chapter_dir(project_root, chapter_index) / "outline.yaml")
    scenes = data.get("scenes")
    if not isinstance(scenes, list):
        return ()
    result: list[ContextualScenePlan] = []
    for position, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("id") or scene.get("scene_id") or f"scene-{chapter_index:02d}-{position:02d}"
        purpose = scene.get("purpose") or scene.get("summary")
        result.append(
            ContextualScenePlan(
                chapter_index=chapter_index,
                scene_id=str(scene_id),
                purpose=purpose if isinstance(purpose, str) else None,
            )
        )
    return tuple(result)
