from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field
import yaml


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
