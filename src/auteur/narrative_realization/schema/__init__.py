"""Scene schema models for Layer 3 narrative realization.

Defines the core data structures for scenes, including:
- SceneOutline: Main container preserving 5 semantic boundaries
- Scene state/action models: Details added progressively as scenes develop
"""

from auteur.narrative_realization.schema.scene_action import (
    ArcBeatRealization,
    Decision,
    Goal,
    Opposition,
    Outcome,
    Turn,
)
from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
    TemporalRelation,
)
from auteur.narrative_realization.schema.scene_state import (
    EmotionalState,
    EntryState,
    ExitState,
    KnowledgeFact,
)

__all__ = [
    # SceneOutline and status
    "SceneOutline",
    "SceneStatus",
    "TemporalRelation",
    # Dramatic action models
    "Goal",
    "Opposition",
    "Turn",
    "Decision",
    "Outcome",
    "ArcBeatRealization",
    # State models
    "KnowledgeFact",
    "EmotionalState",
    "EntryState",
    "ExitState",
]
