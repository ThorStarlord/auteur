"""Layer 3 narrative realization validators.

This module provides validators for Scene artifacts ensuring:
1. Knowledge consistency (no retroactive forgetting, logical progressions)
2. Temporal relationships (unique positions, mutual parallel references, no circular deps)
3. Arc beat realization (valid references, consistent degrees, critical beats realized)

Each validator works identically across genres and can be called independently.
Validators compose cleanly, producing actionable error messages.

Exports:
    KnowledgeValidator: Validates knowledge consistency across scenes
    TemporalValidator: Validates narrative positioning and temporal relations
    RealizationValidator: Validates arc beat references and realization degrees
    ValidationError: Standard error structure for all validators
"""

from auteur.narrative_realization.validator.knowledge_validator import (
    KnowledgeValidator,
    KnowledgeViolation,
)
from auteur.narrative_realization.validator.temporal_validator import (
    TemporalValidator,
    TemporalViolation,
)
from auteur.narrative_realization.validator.realization_validator import (
    RealizationValidator,
    RealizationViolation,
)

__all__ = [
    "KnowledgeValidator",
    "KnowledgeViolation",
    "TemporalValidator",
    "TemporalViolation",
    "RealizationValidator",
    "RealizationViolation",
]
