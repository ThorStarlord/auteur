"""StoryBible — JSON-backed live state for a project.

The blueprint captures *intent* (arcs, milestones, tension targets, contract).
The bible captures *fact* (what actually happened, where characters are now,
which realized tension scores have been recorded). The Story Bible Updater
agent — added in a later phase — reads accepted chapters and mutates this
file. For now it is a thin wrapper that downstream agents and tools can call.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_INITIAL: dict[str, Any] = {
    "characters": {},   # name -> {location, physical, emotional, inventory, relationships, secrets_known, current_arc_pct}
    "locations": {},    # name -> {description, occupants, mood}
    "items": {},        # name -> {holder, properties}
    "factions": {},     # name -> {members, relationships, plans}
    "events": [],       # ordered list of {chapter_index, summary, deltas}
    "realized_tension": [],  # parallel to chapters: list of int 1..10
}


class StoryBible:
    """File-backed knowledge base for the story's evolving state."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        if self.file_path.exists():
            self.data = json.loads(self.file_path.read_text(encoding="utf-8"))
        else:
            self.data = json.loads(json.dumps(_INITIAL))  # deep copy
            self.save()

    def save(self) -> None:
        self.file_path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def upsert_character(self, name: str, **fields: Any) -> None:
        existing = self.data["characters"].get(name, {})
        existing.update(fields)
        self.data["characters"][name] = existing

    def record_event(self, chapter_index: int, summary: str, deltas: dict[str, Any] | None = None) -> None:
        self.data["events"].append(
            {"chapter_index": chapter_index, "summary": summary, "deltas": deltas or {}}
        )

    def record_tension(self, chapter_index: int, score: int) -> None:
        if not 1 <= score <= 10:
            raise ValueError(f"Tension score {score} outside 1-10.")
        scores = self.data["realized_tension"]
        # Pad if a chapter is skipped.
        while len(scores) < chapter_index - 1:
            scores.append(None)
        if len(scores) >= chapter_index:
            scores[chapter_index - 1] = score
        else:
            scores.append(score)

    def query(self, key: str) -> Any:
        """Coarse retrieval — Phase 3 will replace this with an LLM-callable tool."""
        return self.data.get(key)
