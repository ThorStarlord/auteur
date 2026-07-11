from __future__ import annotations
import yaml
from pathlib import Path
from auteur.blueprint import Genre
from auteur.genres.models import GenreContract

_REGISTRY_CACHE: dict[Genre, GenreContract] = {}

def load_genre_contract(genre: Genre | str) -> GenreContract:
    """Load and return the GenreContract for the given Genre.
    
    Caches loaded contracts in memory to avoid repeated disk reads.
    If the genre is not pre-registered or has no YAML file, falls back to
    creating a minimal contract.
    """
    if isinstance(genre, str):
        try:
            genre_enum = Genre(genre)
        except ValueError:
            genre_enum = Genre.OTHER
    else:
        genre_enum = genre

    if genre_enum in _REGISTRY_CACHE:
        return _REGISTRY_CACHE[genre_enum]

    # Find the YAML file in the data/ directory next to this file
    data_dir = Path(__file__).parent / "data"
    yaml_name = f"{genre_enum.value}.yaml"
    yaml_path = data_dir / yaml_name

    if yaml_path.exists():
        try:
            content = yaml_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            contract = GenreContract.model_validate(data)
            _REGISTRY_CACHE[genre_enum] = contract
            return contract
        except Exception:
            # If loading fails, let it fallback to default
            pass

    # Fallback default contract for undefined genres (e.g. cozy_mystery, space_opera)
    fallback_contract = _create_fallback_contract(genre_enum)
    _REGISTRY_CACHE[genre_enum] = fallback_contract
    return fallback_contract


def load_project_genre_contract(project_path: Path, genre: Genre | str) -> GenreContract:
    """Load a built-in or project-local custom GenreContract.

    Custom genre contracts live under ``<project>/genres/custom/<id>.yaml`` and
    use the Genre Builder V1 wrapper shape. Built-in enum genres continue to use
    the package registry unchanged.
    """
    genre_id = genre.value if isinstance(genre, Genre) else str(genre)
    custom_path = project_path / "genres" / "custom" / f"{genre_id}.yaml"
    if custom_path.exists():
        from auteur.genre_builder.serializers import load_custom_genre_contract

        return load_custom_genre_contract(custom_path).contract
    return load_genre_contract(genre)

def _create_fallback_contract(genre: Genre) -> GenreContract:
    from auteur.blueprint import LengthClass, MechanicalLoad, NarrativeRunway, ScopeComplexity
    from auteur.genres.models import PsychologyBudget, PsychologyLevel, RequirementLevel, ScopeProfile, SetupContract
    
    if genre == Genre.LITERARY:
        level = PsychologyLevel.PSYCHOLOGICALLY_DEEP
        reason = "Literary fiction focuses heavily on interiority and character change."
        depth = RequirementLevel.REQUIRED
    elif genre in (Genre.EPIC_FANTASY, Genre.URBAN_FANTASY, Genre.SCI_FI, Genre.SPACE_OPERA, Genre.YA_FANTASY):
        level = PsychologyLevel.FUNCTIONAL
        reason = "Speculative fiction typically runs on external plots and world rules, requiring functional motive."
        depth = RequirementLevel.OPTIONAL
    else:
        level = PsychologyLevel.FUNCTIONAL
        reason = "Default functional psychology suitable for most genres."
        depth = RequirementLevel.OPTIONAL

    return GenreContract(
        genre_id=genre,
        display_name=genre.value.replace("_", " ").title(),
        core_truth="Actions have consequences and characters have clear intent.",
        audience_product="Engagement and narrative satisfaction.",
        primary_excitement_beats=["inciting incident", "rising action", "climax", "resolution"],
        psychology_budget=PsychologyBudget(
            level=level,
            reason=reason,
            motivation_clarity=RequirementLevel.REQUIRED,
            psychological_depth=depth,
            character_texture=RequirementLevel.ENCOURAGED,
        ),
        scope_profile=ScopeProfile(
            natural_lengths=[LengthClass.NOVELLA, LengthClass.NOVEL],
            minimum_viable_length=LengthClass.SHORT_STORY,
            default_length=LengthClass.NOVEL,
            narrative_runway=NarrativeRunway.MEDIUM,
            recommended_complexity=ScopeComplexity.STANDARD,
            mechanical_load=MechanicalLoad.MEDIUM,
            worldbuilding_load=MechanicalLoad.MEDIUM,
            cast_load=MechanicalLoad.MEDIUM,
            compression_strategies=[
                "Prefer one main conflict and collapse optional threads into the main pressure."
            ],
            expansion_strategies=[
                "Increase length before adding ensemble POVs, factions, or parallel timelines."
            ],
            scope_failure_modes=[
                "The selected container carries more cast, setting, or subplot machinery than it can pay off."
            ],
        ),
        setup_contract=SetupContract(
            emotional_runway=NarrativeRunway.MEDIUM,
            relationship_establishment=RequirementLevel.OPTIONAL,
            baseline_world_establishment=RequirementLevel.OPTIONAL,
            minimum_setup_beats=[
                "Establish the protagonist's ordinary starting status quo",
                "Introduce the initial point of connection or threat trigger",
            ],
            forbidden_shortcuts=[
                "Stating the relationships or stakes purely through exposition without scene work",
            ],
            compression_strategies=[
                "Compress the setup by introducing the core conflict within the first scene",
            ],
        ),
    )


# Compatibility imports: contract loading remains in this module while the
# operational interactive-pipeline registry lives in auteur.genre_pipeline.
from auteur.genre_pipeline.models import CoreIdentityProfile, GenrePipelineSpec  # noqa: E402
from auteur.genre_pipeline.registry import (  # noqa: E402
    get_all_genres,
    get_genre_pipeline,
    get_genre_pipeline_for_core,
)
