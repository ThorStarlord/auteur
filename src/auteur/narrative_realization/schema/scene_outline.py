"""SceneOutline: Main container for Layer 3 narrative realization.

Preserves 5 semantic boundaries:
1. Scene owns chapter_id (ownership boundary)
2. References to arc beats (not ownership)
3. Unique narrative_position (not duplicate for parallel)
4. Knowledge tracked separately (validated in Task 6)
5. Emotional states semantic (defined in Task 2)

Status progression: draft → incomplete → ready
- draft: minimal required fields (id, chapter_id)
- incomplete: core dramatic structure added
- ready: full scene with all fields required for validation
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Literal, Optional, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from auteur.narrative_realization.schema.scene_action import (
    ArcBeatRealization,
    Decision,
    Goal,
    Opposition,
    Outcome,
    Turn,
)
from auteur.narrative_realization.schema.scene_state import (
    EmotionalState,
    EntryState,
    ExitState,
    KnowledgeFact,
)


# ---------------------------------------------------------------------------
# Enums & Status
# ---------------------------------------------------------------------------


class SceneStatus(str, Enum):
    """Scene development stage: draft → incomplete → ready."""

    DRAFT = "draft"
    INCOMPLETE = "incomplete"
    READY = "ready"


class TemporalRelationType(str, Enum):
    """How scenes relate temporally."""

    PARALLEL = "parallel"
    FOLLOWS = "follows"


# ---------------------------------------------------------------------------
# Temporal Relations
# ---------------------------------------------------------------------------


class TemporalRelation(BaseModel):
    """Scene temporal positioning within chapter narrative."""

    model_config = ConfigDict(extra="forbid")

    # Parallel scenes: happen at the same time, different locations/POVs
    parallel_with: list[str] = Field(
        default_factory=list,
        description="Scene IDs that happen simultaneously (must be mutual)",
    )

    # Follows scenes: this scene happens after another
    follows_scene: Optional[str] = Field(
        default=None, description="Scene ID that must resolve before this begins"
    )

    @field_validator("parallel_with")
    @classmethod
    def validate_parallel_list(cls, value: list[str]) -> list[str]:
        """Ensure parallel_with contains valid scene IDs."""
        for scene_id in value:
            if not cls._is_valid_scene_id(scene_id):
                raise ValueError(f"Invalid scene ID in parallel_with: {scene_id}")
        return value

    @field_validator("follows_scene")
    @classmethod
    def validate_follows_scene(cls, value: Optional[str]) -> Optional[str]:
        """Ensure follows_scene is valid if set."""
        if value is not None and not cls._is_valid_scene_id(value):
            raise ValueError(f"Invalid scene ID in follows_scene: {value}")
        return value

    @staticmethod
    def _is_valid_scene_id(scene_id: str) -> bool:
        """Check if a scene ID matches scene_XX_YY format."""
        return bool(re.match(r"^scene_\d{2}_\d{2}$", scene_id))


# ---------------------------------------------------------------------------
# Main SceneOutline Container
# ---------------------------------------------------------------------------


class SceneOutline(BaseModel):
    """Main container for Layer 3 scene realization.

    Preserves semantic boundaries:
    1. Owns chapter_id (parent reference, not ownership of content)
    2. References arc beats (not ownership)
    3. Unique narrative_position within chapter
    4. Knowledge handled separately (Task 6)
    5. Emotional states defined later (Task 2)

    Status progression controls field requirements:
    - draft: minimal (id, chapter_id)
    - incomplete: core structure
    - ready: full validation-ready scene
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    # -----------------------------------------------------------------------
    # Core Identity (required for all statuses)
    # -----------------------------------------------------------------------

    id: str = Field(
        description="Scene ID in scene_XX_YY format (XX=chapter, YY=sequence)"
    )

    chapter_id: str = Field(
        description="Parent chapter ID (e.g., 'chapter_01'). Ownership boundary."
    )

    status: SceneStatus = Field(
        default=SceneStatus.DRAFT, description="Development stage: draft|incomplete|ready"
    )

    # -----------------------------------------------------------------------
    # Narrative Structure (required for incomplete/ready)
    # -----------------------------------------------------------------------

    narrative_position: Optional[int] = Field(
        default=None,
        ge=1,
        description="Unique position within chapter (not incremented for parallel scenes)",
    )

    story_time: Optional[str] = Field(
        default=None,
        description="When scene occurs (flexible format: 'day_3_evening' or datetime)",
    )

    # -----------------------------------------------------------------------
    # Temporal Relations (optional, validated only when set)
    # -----------------------------------------------------------------------

    temporal_relation: Optional[TemporalRelation] = Field(
        default=None, description="How this scene relates temporally to others"
    )

    # -----------------------------------------------------------------------
    # Characters & Perspective (required for incomplete/ready)
    # -----------------------------------------------------------------------

    pov_character_id: Optional[str] = Field(
        default=None,
        description="Whose perspective/POV this scene is told from. Identity reference.",
    )

    participants: list[str] = Field(
        default_factory=list,
        description="Character IDs present in this scene. Can be empty in draft.",
    )

    # -----------------------------------------------------------------------
    # Dramatic Action (required for incomplete/ready)
    # -----------------------------------------------------------------------

    goal: Optional[Goal] = Field(
        default=None,
        description="Goal pursued in scene (actor, objective, rationale)",
    )

    opposition: Optional[Opposition] = Field(
        default=None,
        description="Opposition/obstacles (source, pressure, rationale)",
    )

    turn: Optional[Turn] = Field(
        default=None,
        description="Turning point or discovery (type, event, impact)",
    )

    decision: Optional[Decision] = Field(
        default=None,
        description="Critical decision made (actor, choice, rationale)",
    )

    outcome: Optional[Outcome] = Field(
        default=None,
        description="Result and consequences (result, knowledge, emotions, consequences)",
    )

    # -----------------------------------------------------------------------
    # Narrative State (required for ready)
    # -----------------------------------------------------------------------

    entry_state: Optional[EntryState] = Field(
        default=None,
        description="Knowledge and emotional state at scene start",
    )

    exit_state: Optional[ExitState] = Field(
        default=None,
        description="Knowledge and emotional state at scene end",
    )

    # -----------------------------------------------------------------------
    # Arc Beat Realization (with degree: full/partial/implied/deferred)
    # -----------------------------------------------------------------------

    realizes_arc_beats: list[ArcBeatRealization] = Field(
        default_factory=list,
        description="Arc beats realized in this scene with degree of realization",
    )

    # -----------------------------------------------------------------------
    # Narrative Setup/Payoff (optional)
    # -----------------------------------------------------------------------

    setups_created: list[str] = Field(
        default_factory=list,
        description="Setup elements created in this scene (narrative hooks)",
    )

    payoffs_triggered: list[str] = Field(
        default_factory=list,
        description="Setup IDs from earlier scenes that are paid off here",
    )

    # -----------------------------------------------------------------------
    # Metadata (optional)
    # -----------------------------------------------------------------------

    notes: str = Field(
        default="", description="Drafting notes, author intent, or structural notes"
    )

    tags: list[str] = Field(
        default_factory=list, description="Categorical tags (e.g., 'reveal', 'climax')"
    )

    # -----------------------------------------------------------------------
    # Validators: ID Format
    # -----------------------------------------------------------------------

    @field_validator("id")
    @classmethod
    def validate_scene_id(cls, value: str) -> str:
        """Validate scene ID format: scene_XX_YY."""
        if not re.match(r"^scene_\d{2}_\d{2}$", value):
            raise ValueError(
                f"Scene ID must match format 'scene_XX_YY', got '{value}'"
            )
        return value

    @field_validator("chapter_id")
    @classmethod
    def validate_chapter_id(cls, value: str) -> str:
        """Validate chapter ID format."""
        if not value or not isinstance(value, str):
            raise ValueError("chapter_id must be a non-empty string")
        return value

    # -----------------------------------------------------------------------
    # Validators: Field Optionality by Status
    # -----------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_fields_by_status(self) -> Self:
        """Enforce field requirements based on status.

        draft: id, chapter_id only
        incomplete: + narrative_position, pov_character_id, participants, goal, opposition, outcome
        ready: all fields required for validation (including entry/exit states and dramatic arc)
        """
        if self.status == SceneStatus.DRAFT:
            # Minimal requirements: already have id and chapter_id
            pass

        elif self.status == SceneStatus.INCOMPLETE:
            # Core dramatic structure required
            if self.narrative_position is None:
                raise ValueError(
                    f"status={self.status}: narrative_position is required"
                )
            if not self.pov_character_id:
                raise ValueError(
                    f"status={self.status}: pov_character_id is required"
                )
            # At minimum, POV character should be in participants
            if not self.participants:
                raise ValueError(
                    f"status={self.status}: participants must include at least POV character"
                )
            if self.pov_character_id not in self.participants:
                raise ValueError(
                    f"status={self.status}: pov_character_id must be in participants"
                )
            # Core dramatic structure
            if self.goal is None:
                raise ValueError(
                    f"status={self.status}: goal is required for dramatic structure"
                )
            if self.opposition is None:
                raise ValueError(
                    f"status={self.status}: opposition is required for dramatic structure"
                )
            if self.outcome is None:
                raise ValueError(
                    f"status={self.status}: outcome is required for dramatic structure"
                )

        elif self.status == SceneStatus.READY:
            # Full validation-ready scene
            required_fields = {
                "narrative_position": self.narrative_position,
                "story_time": self.story_time,
                "pov_character_id": self.pov_character_id,
                "participants": self.participants,
            }

            missing = [f for f, v in required_fields.items() if not v]
            if missing:
                raise ValueError(
                    f"status=ready: required fields missing: {', '.join(missing)}"
                )

            # Story time must be set and non-empty
            if not self.story_time or not self.story_time.strip():
                raise ValueError("status=ready: story_time must be non-empty")

            # POV character must be in participants
            if self.pov_character_id not in self.participants:
                raise ValueError(
                    "status=ready: pov_character_id must be in participants"
                )

            # Full dramatic structure required
            if self.goal is None:
                raise ValueError("status=ready: goal is required")
            if self.opposition is None:
                raise ValueError("status=ready: opposition is required")
            if self.turn is None:
                raise ValueError("status=ready: turn is required")
            if self.decision is None:
                raise ValueError("status=ready: decision is required")
            if self.outcome is None:
                raise ValueError("status=ready: outcome is required")

            # Entry and exit states required
            if self.entry_state is None:
                raise ValueError("status=ready: entry_state is required")
            if self.exit_state is None:
                raise ValueError("status=ready: exit_state is required")

        return self

    # -----------------------------------------------------------------------
    # Validators: Temporal Relations
    # -----------------------------------------------------------------------

    @model_validator(mode="after")
    def validate_temporal_consistency(self) -> Self:
        """Validate temporal relations make sense."""
        if not self.temporal_relation:
            return self

        tr = self.temporal_relation

        # Can't have both follows_scene and parallel_with simultaneously
        # (not a strict error, but unusual)

        # follows_scene should not reference self
        if tr.follows_scene and tr.follows_scene == self.id:
            raise ValueError("Scene cannot follow itself")

        # parallel_with should not reference self
        if tr.parallel_with and self.id in tr.parallel_with:
            raise ValueError("Scene cannot be parallel with itself")

        return self

    # -----------------------------------------------------------------------
    # Validators: Arc Beat & Setup/Payoff References
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Validators: Arc Beat Realizations
    # -----------------------------------------------------------------------

    @field_validator("realizes_arc_beats")
    @classmethod
    def validate_realizes_arc_beats(
        cls, value: list[ArcBeatRealization]
    ) -> list[ArcBeatRealization]:
        """Validate arc beat realization references."""
        for realization in value:
            if not isinstance(realization, ArcBeatRealization):
                raise ValueError("realizes_arc_beats must contain ArcBeatRealization objects")
            # The ArcBeatRealization class has its own validators
        return value

    @field_validator("setups_created")
    @classmethod
    def validate_setups_created(cls, value: list[str]) -> list[str]:
        """Validate setup narrative hooks."""
        for setup in value:
            if not setup or not isinstance(setup, str):
                raise ValueError("Setup IDs must be non-empty strings")
        return value

    @field_validator("payoffs_triggered")
    @classmethod
    def validate_payoffs_triggered(cls, value: list[str]) -> list[str]:
        """Validate payoff references to earlier setups."""
        for payoff in value:
            if not payoff or not isinstance(payoff, str):
                raise ValueError("Payoff setup IDs must be non-empty strings")
        return value

    # -----------------------------------------------------------------------
    # Validators: Participants
    # -----------------------------------------------------------------------

    @field_validator("participants")
    @classmethod
    def validate_participants(cls, value: list[str]) -> list[str]:
        """Validate participant character IDs."""
        for char_id in value:
            if not char_id or not isinstance(char_id, str):
                raise ValueError("Participant IDs must be non-empty strings")
        # Allow duplicates to be caught by set operations later
        return value

    @field_validator("pov_character_id")
    @classmethod
    def validate_pov_character_id(cls, value: Optional[str]) -> Optional[str]:
        """Validate POV character ID if set."""
        if value is not None:
            if not value or not isinstance(value, str):
                raise ValueError("pov_character_id must be a non-empty string")
        return value
