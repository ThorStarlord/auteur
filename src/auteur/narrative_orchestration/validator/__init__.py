"""Validators for Structure composition and orchestration.

This module provides validation for the complete narrative structure,
ensuring coherence across all outline artifacts.
"""

from auteur.narrative_orchestration.validator.chronological_validator import (
    ChronologicalValidator,
    ChronologicalViolation,
    ChronologyViolationType,
)
from auteur.narrative_orchestration.validator.composition_validator import (
    CompositionValidator,
    CompositionValidationResult,
    CompositionStatus,
    AggregatedViolation,
    ValidationSeverity,
)
from auteur.narrative_orchestration.validator.contradiction_validator import (
    ContradictionValidator,
    Contradiction,
    ContradictionSeverity,
)
from auteur.narrative_orchestration.validator.reference_validator import (
    ReferenceValidator,
    ValidationError,
    ValidationResult,
)

__all__ = [
    "ChronologicalValidator",
    "ChronologicalViolation",
    "ChronologyViolationType",
    "CompositionValidator",
    "CompositionValidationResult",
    "CompositionStatus",
    "AggregatedViolation",
    "ValidationSeverity",
    "ContradictionValidator",
    "Contradiction",
    "ContradictionSeverity",
    "ReferenceValidator",
    "ValidationError",
    "ValidationResult",
]
