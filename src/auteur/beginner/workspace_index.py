"""Read-only index of persisted Beginner workspaces for the Auteur Home surface."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .contracts import SessionEnvelope


class WorkspaceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    workspace_id: str
    project_id: str
    title: str
    premise_preview: str
    session_version: int
    accepted_milestones: tuple[str, ...]
    updated_at: str


def _display_title(premise: str, *, limit: int = 72) -> str:
    compact = " ".join(premise.split())
    if not compact:
        return "Untitled story"
    sentence = compact.split(".", 1)[0].strip() or compact
    if len(sentence) <= limit:
        return sentence
    clipped = sentence[: limit - 1].rsplit(" ", 1)[0].strip()
    return (clipped or sentence[: limit - 1]).rstrip(" ,;:-") + "…"


def _premise_preview(premise: str, *, limit: int = 180) -> str:
    compact = " ".join(premise.split())
    if len(compact) <= limit:
        return compact
    clipped = compact[: limit - 1].rsplit(" ", 1)[0].strip()
    return (clipped or compact[: limit - 1]).rstrip(" ,;:-") + "…"


def list_workspace_summaries(project_root: Path | str) -> tuple[WorkspaceSummary, ...]:
    """Return readable workspaces newest-first without mutating or repairing them."""

    root = Path(project_root).resolve()
    workspaces_root = (root / ".auteur" / "beginner" / "workspaces").resolve()
    if not workspaces_root.is_dir():
        return ()

    summaries: list[WorkspaceSummary] = []
    for candidate in workspaces_root.iterdir():
        try:
            resolved = candidate.resolve()
            if not resolved.is_dir() or not resolved.is_relative_to(workspaces_root):
                continue
            session_path = resolved / "session.json"
            if not session_path.is_file():
                continue
            session = SessionEnvelope.model_validate_json(session_path.read_text(encoding="utf-8"))
            updated_at = datetime.fromtimestamp(
                session_path.stat().st_mtime,
                tz=timezone.utc,
            ).isoformat()
            summaries.append(
                WorkspaceSummary(
                    workspace_id=candidate.name,
                    project_id=session.project_id,
                    title=_display_title(session.premise),
                    premise_preview=_premise_preview(session.premise),
                    session_version=session.session_version,
                    accepted_milestones=tuple(
                        reference.milestone_id for reference in session.accepted_milestones
                    ),
                    updated_at=updated_at,
                )
            )
        except (OSError, ValueError):
            # Home is an orientation surface, not a repair workflow. One damaged
            # workspace must not prevent access to all healthy stories.
            continue

    summaries.sort(key=lambda item: item.updated_at, reverse=True)
    return tuple(summaries)
