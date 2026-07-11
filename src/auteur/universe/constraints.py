"""Universe constraint representation and loading."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ConstraintType(str, Enum):
    """Types of constraints that can be enforced."""

    GENRE_RULE = "genre_rule"
    THEMATIC_INVARIANT = "thematic_invariant"
    CHARACTER_STATE = "character_state"
    RELATIONSHIP_RULE = "relationship_rule"


class ConstraintEnforcement(str, Enum):
    """How a constraint is validated."""

    DETERMINISTIC = "deterministic"
    ADVISORY = "advisory"


class StructuredConstraint(BaseModel):
    """A machine-enforceable Universe constraint."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    type: ConstraintType
    description: str = Field(min_length=1)
    enforcement: ConstraintEnforcement
    schema: dict[str, Any] = Field(default_factory=dict)

    def matches_genre_rule(self, allowed_genres: list[str]) -> bool:
        """Check if genres are allowed by this constraint."""
        if self.type != ConstraintType.GENRE_RULE:
            return True
        allowed = self.schema.get("allowed_values", [])
        return all(g in allowed for g in allowed_genres)

    def as_diagnostic_context(self) -> dict[str, Any]:
        """Return constraint info for diagnostic messages."""
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "enforcement": self.enforcement.value,
        }
