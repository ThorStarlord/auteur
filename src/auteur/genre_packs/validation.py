"""Genre Pack schema validation, identity reconciliation, and contract validation."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from auteur.genre_packs.models import (
    GenrePack,
    GenreProfileCommitment,
    GenreRecommendation,
    GenreAuthorOverride,
    GenreErrorCode,
    GenrePackError,
)
from auteur.genre_packs.registry import get_pack_registry
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    RepairOptions,
    StructureDiagnostic,
)

if TYPE_CHECKING:
    from auteur.identity import StoryIdentity


def validate_pack_schema(pack: GenrePack) -> None:
    """Validate internal coherence and unique stable identifiers of a GenrePack."""
    seen_ids = set()

    # Verify audience promises
    for ap in pack.audience_promises:
        if ap.id in seen_ids:
            raise GenrePackError(
                GenreErrorCode.PACK_INVALID,
                f"Duplicate identifier '{ap.id}' in audience_promises.",
            )
        seen_ids.add(ap.id)

    # Verify emotional targets
    target_emotions = set()
    for et in pack.emotional_targets:
        if et.id in target_emotions:
            raise GenrePackError(
                GenreErrorCode.PACK_INVALID,
                f"Duplicate identifier '{et.id}' in emotional_targets.",
            )
        target_emotions.add(et.id)

    # Verify narrative engines
    narrative_engines = set()
    for ne in pack.narrative_engines:
        if ne.id in narrative_engines:
            raise GenrePackError(
                GenreErrorCode.PACK_INVALID,
                f"Duplicate identifier '{ne.id}' in narrative_engines.",
            )
        narrative_engines.add(ne.id)

    # Verify subgenre profiles
    profile_ids = set()
    for p in pack.subgenre_profiles:
        if p.profile_id in profile_ids:
            raise GenrePackError(
                GenreErrorCode.PACK_INVALID,
                f"Duplicate profile_id '{p.profile_id}' in subgenre_profiles.",
            )
        profile_ids.add(p.profile_id)

        if p.base_pack_id != pack.pack_id:
            raise GenrePackError(
                GenreErrorCode.PACK_INVALID,
                f"Subgenre profile '{p.profile_id}' references unknown base pack '{p.base_pack_id}' (expected '{pack.pack_id}').",
            )

        for emo in p.primary_emotions:
            if emo not in target_emotions:
                raise GenrePackError(
                    GenreErrorCode.PACK_INVALID,
                    f"Profile '{p.profile_id}' references unknown emotional target '{emo}'.",
                )

        for eng in p.preferred_narrative_engines:
            if eng not in narrative_engines:
                raise GenrePackError(
                    GenreErrorCode.PACK_INVALID,
                    f"Profile '{p.profile_id}' references unknown narrative engine '{eng}'.",
                )


def validate_genre_profile_identity(identity: "StoryIdentity") -> list[StructureDiagnostic]:
    """Validate StoryIdentity.genre_profile commitment against the registered Genre Pack."""
    diagnostics: list[StructureDiagnostic] = []
    if not identity.genre_profile:
        return diagnostics

    gp = identity.genre_profile
    registry = get_pack_registry()

    try:
        pack, content_hash = registry.get_pack(gp.primary_pack_id, gp.primary_pack_version)
    except GenrePackError as e:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                layer=DiagnosticLayer.CONSTRAINTS,
                rule="identity.genre_profile.pack_not_found",
                message=e.message,
                evidence=[f"pack_id={gp.primary_pack_id}", f"version={gp.primary_pack_version}"],
                repair_options=RepairOptions(
                    preserve_intent=["Verify pack installation and registry."],
                    challenge_intent=[],
                ),
            )
        )
        return diagnostics

    # Check profile existence
    try:
        profile = registry.get_profile(gp.primary_pack_id, gp.primary_profile_id, gp.primary_pack_version)
    except GenrePackError as e:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                layer=DiagnosticLayer.CONSTRAINTS,
                rule="identity.genre_profile.profile_not_found",
                message=e.message,
                evidence=[f"profile_id={gp.primary_profile_id}"],
                repair_options=RepairOptions(
                    preserve_intent=["Select a valid profile from the pack."],
                    challenge_intent=[],
                ),
            )
        )
        return diagnostics

    # Validate narrative engine family
    valid_engines = {ne.id for ne in pack.narrative_engines}
    if gp.accepted_narrative_engine not in valid_engines:
        diagnostics.append(
            StructureDiagnostic(
                severity=DiagnosticSeverity.ERROR,
                layer=DiagnosticLayer.CONSTRAINTS,
                rule="identity.genre_profile.invalid_engine",
                message=f"Accepted narrative engine '{gp.accepted_narrative_engine}' is not defined in pack '{pack.pack_id}'.",
                evidence=[f"engine={gp.accepted_narrative_engine}"],
                repair_options=RepairOptions(
                    preserve_intent=["Select a narrative engine defined by the pack."],
                    challenge_intent=[],
                ),
            )
        )

    # Validate emotional target keys
    valid_emotions = {et.id for et in pack.emotional_targets}
    for emo_key in gp.accepted_target_emotions:
        if emo_key not in valid_emotions:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    layer=DiagnosticLayer.TARGET_EXPERIENCE,
                    rule="identity.genre_profile.invalid_emotion",
                    message=f"Accepted target emotion '{emo_key}' is not defined in pack '{pack.pack_id}'.",
                    evidence=[f"emotion={emo_key}"],
                    repair_options=RepairOptions(
                        preserve_intent=["Select valid emotional targets."],
                        challenge_intent=[],
                    ),
                )
            )

    # Check explicit author overrides vs warnings
    override_targets = {ao.target_expectation for ao in gp.author_overrides}

    # Example: Check framing alignment
    if gp.accepted_framing.primary != profile.preferred_framing:
        target_key = "genre_profile.primary_framing"
        if target_key not in override_targets and "primary_framing" not in identity.author_overrides:
            diagnostics.append(
                StructureDiagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    layer=DiagnosticLayer.CONSTRAINTS,
                    rule="identity.genre_profile.framing_deviation",
                    message=f"Accepted primary framing '{gp.accepted_framing.primary}' deviates from profile preference '{profile.preferred_framing}'.",
                    evidence=[
                        f"accepted_framing={gp.accepted_framing.primary}",
                        f"preferred_framing={profile.preferred_framing}",
                    ],
                    repair_options=RepairOptions(
                        preserve_intent=["Add explicit author override if this framing choice is intentional."],
                        challenge_intent=["Revert primary framing to profile default."],
                    ),
                )
            )

    return diagnostics


def reconcile_identity_with_recommendation(
    identity: "StoryIdentity",
    recommendation: GenreRecommendation,
    author_overrides: list[GenreAuthorOverride] | None = None,
) -> "StoryIdentity":
    """Perform atomic reconciliation of an accepted GenreRecommendation into StoryIdentity.

    Returns a new or updated StoryIdentity instance. Fails atomically if invalid.
    """
    from auteur.blueprint import Genre, TargetExperience

    registry = get_pack_registry()
    pack, content_hash = registry.get_pack(
        recommendation.recommended_pack_id,
        recommendation.recommended_pack_version,
    )

    # Check staleness
    if content_hash != recommendation.pack_content_hash:
        raise GenrePackError(
            GenreErrorCode.RECOMMENDATION_STALE,
            "The Genre Pack definition has changed since this recommendation was generated.",
            {
                "expected_hash": recommendation.pack_content_hash,
                "current_hash": content_hash,
            },
        )

    # Build GenreProfileCommitment
    overrides_list = list(author_overrides or [])

    prev_commitment = locals().get("commitment")
    commitment = GenreProfileCommitment(
        primary_pack_id=recommendation.recommended_pack_id,
        primary_pack_version=recommendation.recommended_pack_version,
        pack_content_hash=content_hash,
        primary_profile_id=recommendation.recommended_profile_id,
        secondary_genres=[],
        accepted_target_emotions=recommendation.recommended_emotional_targets,
        accepted_narrative_engine=recommendation.recommended_narrative_engine,
        accepted_framing=recommendation.recommended_framing,
        accepted_resolution_contract=recommendation.recommended_resolution_contract,
        adherence_posture=identity.genre_profile.adherence_posture if identity.genre_profile else (prev_commitment.adherence_posture if prev_commitment is not None else "conventional"),
        source_recommendation_id=recommendation.recommendation_id,
        author_overrides=overrides_list,
        accepted_at=datetime.now(timezone.utc).isoformat(),
    )

    # Clone identity to prevent partial mutation
    updated_identity = identity.model_copy(deep=True)
    updated_identity.genre_profile = commitment

    # Reconcile story_type genre & subgenres
    try:
        updated_identity.story_type.genre = Genre(recommendation.recommended_pack_id)
    except ValueError:
        updated_identity.story_type.genre = Genre.EROTIC_FICTION

    updated_identity.story_type.subgenres = [recommendation.recommended_profile_id]

    # Reconcile target_experience
    primary_emo = list(recommendation.recommended_emotional_targets.keys())[0] if recommendation.recommended_emotional_targets else "desire"
    progression_str = " -> ".join(recommendation.recommended_emotional_targets.keys())
    updated_identity.target_experience = TargetExperience(
        primary=primary_emo,
        progression=progression_str,
        avoid=identity.target_experience.avoid if identity.target_experience else [],
    )

    # Validate updated identity
    diags = validate_genre_profile_identity(updated_identity)
    error_diags = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    if error_diags:
        raise GenrePackError(
            GenreErrorCode.IDENTITY_CONFLICT,
            f"Acceptance failed identity validation with {len(error_diags)} error(s): {error_diags[0].message}",
            {"diagnostics": [d.model_dump(mode="json") for d in error_diags]},
        )

    return updated_identity
