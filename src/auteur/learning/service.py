from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .models import LearningEvent, LearningState


class LearningService:
    """Persist observable learning events without scoring literary ability."""

    def __init__(self, project_root: Path) -> None:
        self.path = Path(project_root) / ".auteur" / "learning" / "state.json"

    def load(self) -> LearningState:
        if not self.path.exists():
            return LearningState()
        return LearningState.model_validate_json(self.path.read_text(encoding="utf-8"))

    def record(self, event: LearningEvent) -> LearningState:
        state = self.load()
        state.events.append(event)
        state.concepts.setdefault(event.concept, set()).add(event.event)
        self._save(state)
        return state

    def scaffolding(self, concept: str) -> str:
        observed = self.load().concepts.get(concept, set())
        if "demonstrated_independently" in observed:
            return "recommend"
        if "practiced" in observed:
            return "explain"
        return "teach"

    def _save(self, state: LearningState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=".learning.", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(state.model_dump_json(indent=2))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
