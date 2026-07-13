"""Pydantic models for scene action elements.

This module defines the dramatic action models for a scene: Goal, Opposition, Turn,
Decision, and Outcome. These models represent the concrete dramatic units that occur
within a scene.
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class Goal(BaseModel):
    """Represents a goal pursued within a scene.

    A goal is what an actor wants to accomplish in the scene. It provides the
    motivation and direction for the scene's dramatic action.

    Attributes:
        actor_id: Character ID of the actor pursuing the goal (required)
        objective: What they want to accomplish (required)
        rationale: Why they want it (optional, for clarity and coherence checking)
    """

    actor_id: str = Field(..., description="Character ID pursuing the goal")
    objective: str = Field(..., description="What they want to accomplish")
    rationale: Optional[str] = Field(
        default=None, description="Why they want it (optional)"
    )

    @field_validator("actor_id", mode="before")
    @classmethod
    def validate_actor_id_not_empty(cls, v: str) -> str:
        """Validate that actor_id is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("actor_id must be a non-empty string")
        return v.strip()

    @field_validator("objective", mode="before")
    @classmethod
    def validate_objective_not_empty(cls, v: str) -> str:
        """Validate that objective is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("objective must be a non-empty string")
        return v.strip()


class Opposition(BaseModel):
    """Represents opposition or obstacles within a scene.

    Opposition is what blocks the goal: another character, external force, or
    internal conflict. It creates the dramatic tension.

    Attributes:
        source_id: Character ID or "external" for non-character opposition (required)
        pressure: What they do to block or resist (required)
        rationale: Why they oppose (optional, for coherence checking)
    """

    source_id: str = Field(
        ..., description="Character ID or 'external' for non-character opposition"
    )
    pressure: str = Field(..., description="What they do to block or resist")
    rationale: Optional[str] = Field(
        default=None, description="Why they oppose (optional)"
    )

    @field_validator("source_id", mode="before")
    @classmethod
    def validate_source_id_not_empty(cls, v: str) -> str:
        """Validate that source_id is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("source_id must be a non-empty string")
        return v.strip()

    @field_validator("pressure", mode="before")
    @classmethod
    def validate_pressure_not_empty(cls, v: str) -> str:
        """Validate that pressure is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("pressure must be a non-empty string")
        return v.strip()


class Turn(BaseModel):
    """Represents a turning point or plot development within a scene.

    A turn is an event that changes the situation: a discovery, reversal, decision,
    revelation, or complication. It's the moment that matters.

    Attributes:
        type: Type of turn (discovery, reversal, decision, revelation, complication)
        event: What actually happens (required)
        impact: How it changes the situation (required)
    """

    type: Literal["discovery", "reversal", "decision", "revelation", "complication"] = (
        Field(..., description="Type of turn event")
    )
    event: str = Field(..., description="What actually happens")
    impact: str = Field(..., description="How it changes the situation")

    @field_validator("event", mode="before")
    @classmethod
    def validate_event_not_empty(cls, v: str) -> str:
        """Validate that event is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("event must be a non-empty string")
        return v.strip()

    @field_validator("impact", mode="before")
    @classmethod
    def validate_impact_not_empty(cls, v: str) -> str:
        """Validate that impact is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("impact must be a non-empty string")
        return v.strip()


class Decision(BaseModel):
    """Represents a critical decision made within a scene.

    A decision is a choice point where a character commits to a course of action.
    It captures what they chose and why.

    Attributes:
        actor_id: Character ID making the decision (required)
        choice: What they choose (required)
        rationale: Why they choose it (optional, for coherence and motivation)
    """

    actor_id: str = Field(..., description="Character ID making the decision")
    choice: str = Field(..., description="What they choose (description)")
    rationale: Optional[str] = Field(
        default=None, description="Why they choose it (optional)"
    )

    @field_validator("actor_id", mode="before")
    @classmethod
    def validate_actor_id_not_empty(cls, v: str) -> str:
        """Validate that actor_id is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("actor_id must be a non-empty string")
        return v.strip()

    @field_validator("choice", mode="before")
    @classmethod
    def validate_choice_not_empty(cls, v: str) -> str:
        """Validate that choice is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("choice must be a non-empty string")
        return v.strip()


class ArcBeatRealization(BaseModel):
    """Represents how an arc beat is realized in a scene outcome.

    Attributes:
        beat_id: ID of the arc beat being realized (required)
        degree: Degree of realization (full, partial, implied, deferred)
    """

    beat_id: str = Field(..., description="ID of the arc beat being realized")
    degree: Literal["full", "partial", "implied", "deferred"] = Field(
        ..., description="Degree of realization"
    )

    @field_validator("beat_id", mode="before")
    @classmethod
    def validate_beat_id_not_empty(cls, v: str) -> str:
        """Validate that beat_id is not empty."""
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("beat_id must be a non-empty string")
        return v.strip()


class Outcome(BaseModel):
    """Represents the result and consequences of a scene's dramatic action.

    An outcome captures what actually happens as a result of goal/opposition/turn/decision,
    including knowledge gained, emotional changes, and ripple effects.

    Attributes:
        result: Success level (success, partial, failure)
        knowledge_added: List of new facts learned in the scene
        knowledge_questioned: List of facts no longer trusted
        emotional_shifts: Dict mapping character emotions to new states
        consequences: List of ripple effects forward in the story
        arc_beats_realized: List of arc beat realizations
    """

    result: Literal["success", "partial", "failure"] = Field(
        ..., description="Success level of the scene's action"
    )
    knowledge_added: List[str] = Field(
        default_factory=list, description="New facts learned in the scene"
    )
    knowledge_questioned: List[str] = Field(
        default_factory=list, description="Facts no longer trusted"
    )
    emotional_shifts: Dict[str, str] = Field(
        default_factory=dict, description="How emotions changed for characters"
    )
    consequences: List[str] = Field(
        default_factory=list, description="Ripple effects forward in the story"
    )
    arc_beats_realized: List[ArcBeatRealization] = Field(
        default_factory=list, description="Arc beats realized in this scene"
    )

    @field_validator("knowledge_added", "knowledge_questioned", "consequences", mode="before")
    @classmethod
    def validate_list_items_not_empty(cls, v: List[str]) -> List[str]:
        """Validate that list items are not empty strings."""
        if not isinstance(v, list):
            raise ValueError("Field must be a list")
        # Filter out empty strings and validate
        cleaned = [item.strip() for item in v if isinstance(item, str) and item.strip()]
        return cleaned

    @field_validator("emotional_shifts", mode="before")
    @classmethod
    def validate_emotional_shifts_format(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate emotional_shifts dictionary format."""
        if not isinstance(v, dict):
            raise ValueError("emotional_shifts must be a dictionary")
        # Validate all keys and values are non-empty strings
        for key, value in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("emotional_shifts keys must be non-empty strings")
            if not isinstance(value, str) or not value.strip():
                raise ValueError("emotional_shifts values must be non-empty strings")
        # Clean whitespace from values but keep keys as-is for character reference
        return {k: v.strip() for k, v in v.items()}
