"""Genre Packs module for Auteur.

Supplies versioned, reusable genre knowledge packages used to recommend
and evaluate story direction. Layer 1 records explicit author commitments.
"""

from auteur.genre_packs.models import (
    RuleStrength,
    AudiencePromise,
    EmotionalTarget,
    NarrativeEngineFamily,
    CoreConvention,
    SceneFunction,
    ConflictFamily,
    SubgenreProfile,
    ResolutionPattern,
    EscalationPattern,
    BoundaryRule,
    FailureModeDefinition,
    EvaluationRule,
    RevisionStrategy,
    GenrePack,
    AdherencePosture,
    FramingCommitment,
    ResolutionContractCommitment,
    GenreAuthorOverride,
    GenreProfileCommitment,
    GenreRecommendation,
    RejectedProfileAnalysis,
    GenreErrorCode,
    GenrePackError,
)
from auteur.genre_packs.hashing import compute_pack_content_hash
from auteur.genre_packs.loader import load_genre_pack, load_built_in_pack
from auteur.genre_packs.registry import GenrePackRegistry, get_pack_registry
from auteur.genre_packs.recommendation import recommend_genre_profile
from auteur.genre_packs.validation import (
    validate_pack_schema,
    validate_genre_profile_identity,
    reconcile_identity_with_recommendation,
)
from auteur.genre_packs.diagnostics import run_genre_diagnostics

__all__ = [
    "RuleStrength",
    "AudiencePromise",
    "EmotionalTarget",
    "NarrativeEngineFamily",
    "CoreConvention",
    "SceneFunction",
    "ConflictFamily",
    "SubgenreProfile",
    "ResolutionPattern",
    "EscalationPattern",
    "BoundaryRule",
    "FailureModeDefinition",
    "EvaluationRule",
    "RevisionStrategy",
    "GenrePack",
    "AdherencePosture",
    "FramingCommitment",
    "ResolutionContractCommitment",
    "GenreAuthorOverride",
    "GenreProfileCommitment",
    "GenreRecommendation",
    "RejectedProfileAnalysis",
    "GenreErrorCode",
    "GenrePackError",
    "compute_pack_content_hash",
    "load_genre_pack",
    "load_built_in_pack",
    "GenrePackRegistry",
    "get_pack_registry",
    "recommend_genre_profile",
    "validate_pack_schema",
    "validate_genre_profile_identity",
    "reconcile_identity_with_recommendation",
    "run_genre_diagnostics",
]
