"""Schema module for narrative orchestration composition rules."""

from auteur.narrative_orchestration.schema.ownership import (
    ArtifactType,
    OwnershipMapping,
    OwnershipRule,
    StructuralFact,
)
from auteur.narrative_orchestration.schema.references import (
    ArcReference,
    ArtifactTypePrefix,
    BeatReference,
    ChapterReference,
    IdFormat,
    PayoffReference,
    Reference,
    ReferenceGraph,
    ReferenceResolver,
    ReferenceType,
    SetupReference,
)

# Try to import composition_rules if it exists and is valid
try:
    from auteur.narrative_orchestration.schema.composition_rules import (
        ArcCoverageConstraint,
        ChronologicalOrderingConstraint,
        CompositionConstraintSet,
        ConstraintEvaluation,
        ConstraintViolation,
        OptionalityConstraint,
        OptionalityLevel,
        StateTransition,
        StateValidityConstraint,
        create_gentlefemdom_constraints,
        create_mystery_constraints,
        create_netorare_constraints,
        get_constraints_for_genre,
    )

    __all__ = [
        # Ownership
        "OwnershipRule",
        "OwnershipMapping",
        "ArtifactType",
        "StructuralFact",
        # References
        "Reference",
        "ArcReference",
        "ChapterReference",
        "BeatReference",
        "PayoffReference",
        "SetupReference",
        "ReferenceType",
        "ReferenceResolver",
        "ReferenceGraph",
        "IdFormat",
        "ArtifactTypePrefix",
        # Composition (if available)
        "ChronologicalOrderingConstraint",
        "CompositionConstraintSet",
        "ConstraintEvaluation",
        "ConstraintViolation",
        "OptionalityConstraint",
        "OptionalityLevel",
        "StateTransition",
        "StateValidityConstraint",
        "ArcCoverageConstraint",
        "create_gentlefemdom_constraints",
        "create_mystery_constraints",
        "create_netorare_constraints",
        "get_constraints_for_genre",
    ]
except (ImportError, Exception):
    # Composition rules not yet available or have errors, export ownership and references
    __all__ = [
        # Ownership
        "OwnershipRule",
        "OwnershipMapping",
        "ArtifactType",
        "StructuralFact",
        # References
        "Reference",
        "ArcReference",
        "ChapterReference",
        "BeatReference",
        "PayoffReference",
        "SetupReference",
        "ReferenceType",
        "ReferenceResolver",
        "ReferenceGraph",
        "IdFormat",
        "ArtifactTypePrefix",
    ]
