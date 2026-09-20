"""Read-only whole-book orientation for the Beginner Workspace.

This module adapts existing project status and publishing owners into a small
beginner-facing projection. It never composes, accepts, reconciles, or
publishes a Book.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict

from auteur.publish import PublishError, PublishingSnapshot
from auteur.status import gather_status


class BookProgressProjection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    planned_chapters: int
    discovered_chapters: int
    accepted_chapters: int
    book_expression: str
    reconciliation_status: str
    publication_ready: bool
    publication_blocker: str | None = None
    next_command: str | None = None
    publish_commands: tuple[str, ...] = ()
    authority_status: str = "DERIVED / NOT CANON"


def project_book_progress(project_root: Path) -> BookProgressProjection:
    """Project whole-book progress without crossing any story authority boundary."""
    root = Path(project_root)
    status = gather_status(root)
    chapters = status.get("chapters") or []
    blueprint = status.get("blueprint") or {}
    book = status.get("book") or {}
    reconciliation = status.get("reconciliation") or {}

    accepted_chapters = sum(
        1
        for chapter in chapters
        if isinstance(chapter, dict)
        and "accepted" in str(chapter.get("expression", ""))
    )
    planned_chapters = int(blueprint.get("chapters") or len(chapters) or 0)

    publication_ready = False
    publication_blocker: str | None = None
    try:
        PublishingSnapshot(root)
        publication_ready = True
    except (PublishError, FileNotFoundError, KeyError, OSError, TypeError, ValueError) as exc:
        publication_blocker = str(exc)

    publish_commands = (
        (
            "auteur publish --project . --format html",
            "auteur publish --project . --format epub",
        )
        if publication_ready
        else ()
    )

    return BookProgressProjection(
        planned_chapters=planned_chapters,
        discovered_chapters=len(chapters),
        accepted_chapters=accepted_chapters,
        book_expression=str(book.get("expression", "missing")),
        reconciliation_status=str(reconciliation.get("status", "not_started")),
        publication_ready=publication_ready,
        publication_blocker=publication_blocker,
        next_command=status.get("suggested_command"),
        publish_commands=publish_commands,
    )
