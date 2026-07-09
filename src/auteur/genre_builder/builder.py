from __future__ import annotations

from auteur.blueprint import (
    Genre,
    LengthClass,
    MechanicalLoad,
    NarrativeRunway,
    ScopeComplexity,
)
from auteur.genre_builder.models import CustomGenreContract, GenreBrief
from auteur.genre_builder.parser import parse_bullets, parse_key_values, slugify_genre_id
from auteur.genres.models import (
    GenreContract,
    PsychologyBudget,
    PsychologyLevel,
    RequirementLevel,
    ScopeProfile,
    SetupContract,
)


def build_custom_genre_contract(brief: GenreBrief) -> CustomGenreContract:
    sections = brief.sections
    display_name = sections.get("Genre", "Custom Genre").strip() or "Custom Genre"
    scope = parse_key_values(sections.get("Scope", ""))
    required_tropes = parse_bullets(sections.get("Required Tropes", ""))
    optional_tropes = parse_bullets(sections.get("Optional Tropes", ""))
    forbidden_mismatches = parse_bullets(sections.get("Forbidden Mismatches", ""))
    common_failures = parse_bullets(sections.get("Common Failures", ""))
    setup_beats = parse_bullets(sections.get("Setup Requirements", ""))

    contract = GenreContract(
        genre_id=Genre.OTHER,
        display_name=display_name,
        core_truth=sections.get("Core Truth", "").strip(),
        audience_product=sections.get("Emotional Promise", "").strip(),
        primary_excitement_beats=required_tropes[:],
        required_tropes=required_tropes,
        optional_tropes=optional_tropes,
        forbidden_mismatches=forbidden_mismatches,
        common_failure_modes=common_failures,
        psychology_budget=PsychologyBudget(
            level=PsychologyLevel.FUNCTIONAL,
            reason="Custom genre contracts default to functional psychology unless a later builder version captures deeper psychology constraints.",
            motivation_clarity=RequirementLevel.REQUIRED,
            psychological_depth=RequirementLevel.OPTIONAL,
            character_texture=RequirementLevel.ENCOURAGED,
        ),
        scope_profile=ScopeProfile(
            natural_lengths=[_length(scope.get("minimum_viable_length", "novella")), _length(scope.get("default_length", "novel"))],
            minimum_viable_length=_length(scope.get("minimum_viable_length", "novella")),
            default_length=_length(scope.get("default_length", "novel")),
            narrative_runway=_runway(scope.get("narrative_runway", "medium")),
            recommended_complexity=_complexity(scope.get("recommended_complexity", "standard")),
            mechanical_load=_load(scope.get("mechanical_load", "medium")),
            worldbuilding_load=_load(scope.get("worldbuilding_load", "medium")),
            cast_load=_load(scope.get("cast_load", "medium")),
            compression_strategies=[],
            expansion_strategies=[],
            scope_failure_modes=common_failures,
        ),
        setup_contract=SetupContract(
            emotional_runway=_runway(scope.get("narrative_runway", "medium")),
            relationship_establishment=RequirementLevel.OPTIONAL,
            baseline_world_establishment=RequirementLevel.OPTIONAL,
            minimum_setup_beats=setup_beats,
            forbidden_shortcuts=[],
            compression_strategies=[],
        ),
        default_engine_biases=[],
        recommended_subversions=[],
    )
    return CustomGenreContract(
        custom_genre_id=slugify_genre_id(display_name),
        base_genre=Genre.OTHER.value,
        contract=contract,
    )


def _length(value: str) -> LengthClass:
    return LengthClass(value)


def _runway(value: str) -> NarrativeRunway:
    return NarrativeRunway(value)


def _complexity(value: str) -> ScopeComplexity:
    return ScopeComplexity(value)


def _load(value: str) -> MechanicalLoad:
    return MechanicalLoad(value)

