"""Layer 0 vocabulary for authorial narrative-architecture preferences.

These concepts describe how an author prefers narrative machinery to be composed.
They are not genre, target-experience, premise, or generation-provenance fields.
Concrete commitments are optional: ``None`` always means the author has not made
that commitment (UNKNOWN), never a hidden default.
"""

from enum import Enum

from pydantic import BaseModel, Field


class ComplexityPreference(str, Enum):
    """Preferred density of simultaneously active narrative machinery."""

    FOCUSED = "focused"
    LAYERED = "layered"
    MAXIMALIST = "maximalist"


class CausalDistributionPreference(str, Enum):
    """Preferred distribution of meaningful causes behind major outcomes."""

    CONCENTRATED = "concentrated"
    LAYERED = "layered"
    MIXED = "mixed"


class EngineHierarchyPreference(str, Enum):
    """Preferred hierarchy among multiple narrative engines or causal systems."""

    SINGLE_CENTER = "single_center"
    PRIMARY_WITH_LAYERS = "primary_with_layers"
    ENSEMBLE = "ensemble"


class NarrativeArchitecturePreferences(BaseModel):
    """Optional Layer 1 commitments using the Layer 0 architecture vocabulary.

    Each dimension is independently optional so partially specified author intent
    remains distinguishable from a concrete preference. No dimension is inferred
    from the others.
    """

    complexity: ComplexityPreference | None = Field(
        default=None,
        description=(
            "Preferred density of active narrative machinery. None = UNKNOWN / "
            "no author commitment."
        ),
    )
    causal_distribution: CausalDistributionPreference | None = Field(
        default=None,
        description=(
            "Preferred distribution of causes behind important outcomes. None = "
            "UNKNOWN / no author commitment."
        ),
    )
    engine_hierarchy: EngineHierarchyPreference | None = Field(
        default=None,
        description=(
            "Preferred hierarchy among narrative engines. None = UNKNOWN / no "
            "author commitment."
        ),
    )
