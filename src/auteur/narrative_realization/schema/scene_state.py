"""Scene state models for Layer 3 narrative realization.

Defines entry and exit state models that track knowledge and emotional changes
as scenes progress. Preserves semantic boundary #5: emotional states are
directional and semantic, not numeric.

Architecture:
- KnowledgeFact: Atomic unit of knowledge with how_known and certainty
- EmotionalState: Semantic emotional label with intensity (not numeric scale)
- EntryState: Optional knowledge and emotions at scene start
- ExitState: Required knowledge and emotions when scene is complete
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class KnowledgeFact(BaseModel):
    """A single fact known or learned during or before a scene.

    Tracks not just what is known, but how it became known and with what
    certainty. Preserves the author's intent about knowledge mechanics.

    Attributes:
        what: Description of what is known (author-written)
        how_known: Mechanism by which knowledge was acquired (one of:
            'learned' - direct experience/discovery,
            'perceived' - sensory observation,
            'inferred' - logical deduction,
            'external_source' - told by another character or document)
        degree: Author's certainty about this knowledge (one of:
            'certain' - verified fact,
            'probable' - likely but not proven,
            'suspected' - plausible but uncertain,
            'questioned' - actively doubted or contradicted)
        source: Where this fact originated (one of:
            'chapter_position' - reference to chapter scene (e.g., "Chapter 2, Scene 3"),
            'character_id' - which character revealed this,
            'document' - found in a document or letter,
            'inference' - derived by logical chain)
    """

    what: str = Field(
        ...,
        description="Description of what is known",
        min_length=1,
    )
    how_known: Literal["learned", "perceived", "inferred", "external_source"] = Field(
        ...,
        description="Mechanism by which knowledge was acquired",
    )
    degree: Literal["certain", "probable", "suspected", "questioned"] = Field(
        default="probable",
        description="Author's certainty about this knowledge",
    )
    source: Literal["chapter_position", "character_id", "document", "inference"] = Field(
        ...,
        description="Origin point of this fact",
    )

    @field_validator("what")
    @classmethod
    def what_not_empty(cls, v: str) -> str:
        """Ensure what is not just whitespace."""
        if not v.strip():
            raise ValueError("what must not be empty or only whitespace")
        return v.strip()

    class Config:
        """Pydantic config for KnowledgeFact."""
        json_schema_extra = {
            "example": {
                "what": "The victim was poisoned with arsenic",
                "how_known": "learned",
                "degree": "certain",
                "source": "character_id",
            }
        }


class EmotionalState(BaseModel):
    """A semantic emotional state at a point in the narrative.

    Defines emotions as semantic labels (guarded, suspicious, etc.) rather
    than numeric scales (1-10). Intensity modulates the state but does not
    replace it. This preserves semantic boundary #5: emotions are directional
    and semantic, not numeric.

    Attributes:
        state: Semantic emotional label (author-defined, e.g., "guarded",
            "suspicious", "certain", "vulnerable", etc.)
        intensity: How strong this emotion is (one of:
            'low' - present but subtle,
            'moderate' - noticeable but controlled,
            'high' - dominant, affecting decisions)
        rationale: Optional author note explaining why this emotion exists
            at this point in the scene (for author clarity only)
    """

    state: str = Field(
        ...,
        description="Semantic emotional label (author-defined)",
        min_length=1,
    )
    intensity: Literal["low", "moderate", "high"] = Field(
        default="moderate",
        description="Strength of this emotion",
    )
    rationale: Optional[str] = Field(
        default=None,
        description="Author note explaining this emotional state",
    )

    @field_validator("state")
    @classmethod
    def state_not_empty(cls, v: str) -> str:
        """Ensure state is not just whitespace."""
        if not v.strip():
            raise ValueError("state must not be empty or only whitespace")
        return v.strip()

    @field_validator("rationale")
    @classmethod
    def rationale_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """Ensure rationale is not just whitespace if provided."""
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None

    class Config:
        """Pydantic config for EmotionalState."""
        json_schema_extra = {
            "example": {
                "state": "guarded",
                "intensity": "high",
                "rationale": "Character suspects the protagonist is lying",
            }
        }


class EntryState(BaseModel):
    """State of knowledge and emotions at the start of a scene.

    All fields are optional because scenes can start empty. As a scene develops,
    knowledge is added and emotions shift. The entry state establishes what
    the character(s) knew or felt *before* the dramatic action began.

    Attributes:
        knowledge: List of facts known at scene start (can be empty)
        emotional: Dict mapping emotion names to their states at scene start
            (can be empty)
    """

    knowledge: List[KnowledgeFact] = Field(
        default_factory=list,
        description="Facts known at scene start",
    )
    emotional: Dict[str, EmotionalState] = Field(
        default_factory=dict,
        description="Emotional states at scene start (emotion name → state)",
    )

    class Config:
        """Pydantic config for EntryState."""
        json_schema_extra = {
            "example": {
                "knowledge": [
                    {
                        "what": "The victim was found at midnight",
                        "how_known": "external_source",
                        "degree": "certain",
                        "source": "character_id",
                    }
                ],
                "emotional": {
                    "suspicion": {
                        "state": "suspicious",
                        "intensity": "moderate",
                    }
                },
            }
        }


class ExitState(BaseModel):
    """State of knowledge and emotions at the end of a scene.

    When a scene reaches 'ready' status, the exit state must be fully defined.
    This captures what the character(s) know and feel after the scene's dramatic
    action. Entry state + scene action = exit state.

    Attributes:
        knowledge: List of facts known at scene end (union of entry + learned)
        emotional: Dict mapping emotion names to their states at scene end
    """

    knowledge: List[KnowledgeFact] = Field(
        default_factory=list,
        description="Facts known at scene end (entry + newly learned)",
    )
    emotional: Dict[str, EmotionalState] = Field(
        default_factory=dict,
        description="Emotional states at scene end (emotion name → state)",
    )

    class Config:
        """Pydantic config for ExitState."""
        json_schema_extra = {
            "example": {
                "knowledge": [
                    {
                        "what": "The victim was found at midnight",
                        "how_known": "external_source",
                        "degree": "certain",
                        "source": "character_id",
                    },
                    {
                        "what": "The killer wore gloves to avoid leaving fingerprints",
                        "how_known": "inferred",
                        "degree": "probable",
                        "source": "inference",
                    },
                ],
                "emotional": {
                    "suspicion": {
                        "state": "certain",
                        "intensity": "high",
                        "rationale": "Scene revealed critical evidence",
                    }
                },
            }
        }
