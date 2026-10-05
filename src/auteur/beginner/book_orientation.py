"""Read-only author re-entry over existing Chapter and discovery owners.

These are presentation states, not new acceptance or persistence states. Missing
or stale evidence is reported, never silently promoted into accepted meaning.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict


class StoryNotice(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: str
    source_ref: str
    state: Literal["Working", "Suggested", "Kept", "Needs attention"]
    chapter_index: int | None = None
    blocking: bool = False


class BookOrientation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    current_chapter: int = 1
    current_chapter_state: Literal["Working", "Kept"] = "Working"
    recent_changes: tuple[StoryNotice, ...] = ()
    pending_updates: tuple[StoryNotice, ...] = ()
    needs_attention: tuple[StoryNotice, ...] = ()
    accepted_chapter_refs: tuple[str, ...] = ()
    next_story_action: str = "Write Chapter 1"
    next_action_chapter: int | None = 1
    orientation_reason: str = "No Chapter has been kept yet."


def _positive_index(value: object) -> bool:
    return type(value) is int and value > 0


def _notice(summary: str, source: str, chapter: int | None = None) -> StoryNotice:
    return StoryNotice(summary=summary, source_ref=source,
                       chapter_index=chapter, state="Needs attention")


def _mapping(path: Path, root: Path, attention: list[StoryNotice]) -> dict:
    if not path.is_file():
        return {}
    ref = path.relative_to(root).as_posix()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("expected an object")
        return value
    except (OSError, UnicodeError, ValueError):
        attention.append(_notice("This story record could not be read. Review its source before relying on it.", ref))
        return {}


def _chapters(root: Path, attention: list[StoryNotice]) -> dict[int, Path]:
    chapters: dict[int, Path] = {}
    for path in sorted((root / "chapters").glob("*")):
        if not path.is_dir() or not re.fullmatch(r"[0-9]+", path.name):
            continue
        index = int(path.name)
        if index < 1:
            continue
        if index in chapters:
            attention.append(_notice("Two folders describe this Chapter. Review the duplicate before relying on its continuity.",
                                     path.relative_to(root).as_posix(), index))
            # Match the existing Chapter owners: padded folder wins.
            if path.name != f"{index:02d}":
                continue
        chapters[index] = path
    return dict(sorted(chapters.items()))


def read_accepted_history(root: Path, chapters: dict[int, Path],
                          attention: list[StoryNotice]) -> tuple[dict[int, bytes], list[StoryNotice]]:
    """Return historical prose bytes and notices, never candidate-only evidence."""
    accepted: dict[int, bytes] = {}
    for index, path in chapters.items():
        final = path / "final.md"
        if final.is_file():
            try:
                accepted[index] = final.read_bytes()
            except OSError:
                attention.append(_notice("The kept Chapter could not be read.",
                                         final.relative_to(root).as_posix(), index))
    bible = _mapping(root / "bible.json", root, attention)
    events = bible.get("events", [])
    if not isinstance(events, list):
        attention.append(_notice("Chapter history could not be read from the story record.", "bible.json"))
        events = []
    history: list[StoryNotice] = []
    with_events: set[int] = set()
    for position, event in enumerate(events):
        if not isinstance(event, dict) or not _positive_index(event.get("chapter_index")):
            continue
        index = event["chapter_index"]
        if index not in accepted:
            continue
        summary = event.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            summary = f"Story state was updated in Chapter {index}."
        history.append(StoryNotice(summary=summary, source_ref=f"bible.json#/events/{position}",
                                   chapter_index=index, state="Kept"))
        with_events.add(index)
    for index in accepted.keys() - with_events:
        history.append(StoryNotice(summary=f"Chapter {index} kept.", chapter_index=index,
                                   source_ref=(chapters[index] / "final.md").relative_to(root).as_posix(),
                                   state="Kept"))
    # Reverse chronology, preserving event order within each Chapter.
    history.sort(key=lambda item: item.chapter_index or 0)
    return accepted, list(reversed(history))


def read_pending_updates(root: Path, accepted: dict[int, bytes],
                         attention: list[StoryNotice]) -> tuple[StoryNotice, ...]:
    """Project current noncanonical receipts; the existing owner still resolves them."""
    pending: list[StoryNotice] = []
    seen: set[tuple] = set()
    for path in sorted((root / ".auteur/beginner/reconciliation").glob("*.json")):
        receipt = _mapping(path, root, attention)
        if receipt.get("status") != "proposal_ready":
            continue
        index = receipt.get("chapter_index")
        ref = path.relative_to(root).as_posix()
        if (receipt.get("canonical") is not False or receipt.get("chapter_accepted") is not True
                or not _positive_index(index) or index not in accepted):
            attention.append(_notice("This story update has no matching kept Chapter.", ref))
            continue
        if receipt.get("candidate_sha256") != hashlib.sha256(accepted[index]).hexdigest():
            attention.append(_notice("The kept Chapter changed after this story update. Review the update again.", ref, index))
            continue
        items = receipt.get("proposal_items")
        if not isinstance(items, list):
            attention.append(_notice("Suggested story updates could not be read.", ref, index))
            continue
        for position, item in enumerate(items):
            if not isinstance(item, dict) or item.get("status") != "proposed" or item.get("canonical") is not False:
                continue
            label, value = item.get("label"), item.get("value")
            parts = [text.strip() for text in (label, value) if isinstance(text, str) and text.strip()]
            summary = ": ".join(parts) or f"Review the story update from Chapter {index}."
            key = (index, receipt["candidate_sha256"], summary, str(item.get("target_owner", "")))
            if key in seen:
                continue
            seen.add(key)
            pending.append(StoryNotice(summary=summary, chapter_index=index, state="Suggested",
                                       source_ref=f"{ref}#/proposal_items/{position}"))
    return tuple(pending)


def project_book_orientation(project_root: Path, *, planned_chapters: int = 0) -> BookOrientation:
    """Answer re-entry questions without modifying any project bytes.

    A newer working draft does not remove the historical final. Data issues are
    visible and nonblocking for writing; this projection does not certify that a
    downstream acceptance/continuity boundary may be crossed.
    """
    if type(planned_chapters) is not int or planned_chapters < 0:
        raise ValueError("planned_chapters must be a nonnegative integer")
    root = Path(project_root)
    attention: list[StoryNotice] = []
    chapters = _chapters(root, attention)
    accepted, history = read_accepted_history(root, chapters, attention)
    pending = read_pending_updates(root, accepted, attention)
    working: set[int] = set()
    for index, path in chapters.items():
        drafts = [(int(match[1]), draft) for draft in path.glob("draft_v*.md")
                  if (match := re.fullmatch(r"draft_v([0-9]+)\.md", draft.name))]
        if drafts:
            latest = max(drafts)[1]
            try:
                if latest.read_bytes() != accepted.get(index):
                    working.add(index)
            except OSError:
                working.add(index)
                attention.append(_notice("The working draft could not be read.", latest.relative_to(root).as_posix(), index))
    # Stop at the first unfinished Chapter, including a deliberate new revision.
    current = 1
    while current in accepted and current not in working:
        current += 1
    completed = bool(planned_chapters and current > planned_chapters and not working)
    if completed:
        current, action, target, state = planned_chapters, "Review your Book", None, "Kept"
        reason = "Every planned Chapter has a kept version and no newer working draft."
    else:
        if working and (current > max(working) or (planned_chapters and current > planned_chapters)):
            current = min(working)
        state, target = "Working", current
        action = f"Continue Chapter {current}" if current in chapters else f"Write Chapter {current}"
        reason = "Continue the first Chapter without a kept current draft; prior kept versions remain history."
    return BookOrientation(
        current_chapter=current, current_chapter_state=state,
        recent_changes=tuple(history[:5]), pending_updates=pending,
        needs_attention=tuple(attention),
        accepted_chapter_refs=tuple((chapters[index] / "final.md").relative_to(root).as_posix() for index in accepted),
        next_story_action=action, next_action_chapter=target, orientation_reason=reason,
    )
