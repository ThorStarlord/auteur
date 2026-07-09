from __future__ import annotations
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List
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


# ============================================================================
# Phase 4: GenrePipelineSpec Registry - Makes genres first-class plugins
# ============================================================================

@dataclass(frozen=True)
class GenrePipelineSpec:
    """Complete specification for a genre pipeline. Makes it first-class."""
    genre: Genre
    slug: str
    core_ids: tuple
    template_factory: Callable[[str], 'CoreTemplate']
    validate_choices: Callable
    identity_strategy: Callable
    browser_title: str
    session_dir_name: str
    contract_file: str


_GENRE_SPECS: Dict[Genre, GenrePipelineSpec] = {}


def _register_netorare():
    """Register netorare genre."""
    from auteur.netorare.core_templates import (
        HumiliationTemplate, HorrorTemplate, MysteryTemplate as NetorareMysteryTemplate
    )

    def factory(core_id: str):
        templates = {
            "classic_humiliation": HumiliationTemplate,
            "horror": HorrorTemplate,
            "mystery": NetorareMysteryTemplate,
        }
        return templates[core_id]()

    from auteur.netorare.validation import validate_choices
    from auteur.netorare.identity_generator import IdentityGenerator

    spec = GenrePipelineSpec(
        genre=Genre.NETORARE,
        slug="netorare",
        core_ids=("classic_humiliation", "horror", "mystery"),
        template_factory=factory,
        validate_choices=validate_choices,
        identity_strategy=IdentityGenerator.from_choices,
        browser_title="Netorare Story Identity Authoring",
        session_dir_name="netorare",
        contract_file="src/auteur/genres/data/netorare.yaml",
    )
    _GENRE_SPECS[Genre.NETORARE] = spec


def _register_mystery():
    """Register mystery genre."""
    from auteur.mystery.core_templates import HowdunitTemplate, ParanoiaTemplate, CozyTemplate

    def factory(core_id: str):
        templates = {
            "howdunit": HowdunitTemplate,
            "paranoia": ParanoiaTemplate,
            "cozy": CozyTemplate,
        }
        return templates[core_id]()

    from auteur.mystery.validation import validate_choices
    from auteur.netorare.identity_generator import IdentityGenerator

    spec = GenrePipelineSpec(
        genre=Genre.MYSTERY,
        slug="mystery",
        core_ids=("howdunit", "paranoia", "cozy"),
        template_factory=factory,
        validate_choices=validate_choices,
        identity_strategy=IdentityGenerator.from_choices,
        browser_title="Mystery Story Identity Authoring",
        session_dir_name="mystery",
        contract_file="src/auteur/genres/data/mystery.yaml",
    )
    _GENRE_SPECS[Genre.MYSTERY] = spec


def _register_gentlefemdom():
    """Register gentlefemdom genre."""
    from auteur.gentlefemdom.core_templates import (
        SensualDominanceTemplate, TenderSurrenderTemplate, RomanticAuthorityTemplate
    )

    def factory(core_id: str):
        templates = {
            "sensual_dominance": SensualDominanceTemplate,
            "tender_surrender": TenderSurrenderTemplate,
            "romantic_authority": RomanticAuthorityTemplate,
        }
        return templates[core_id]()

    from auteur.gentlefemdom.validation import validate_choices
    from auteur.netorare.identity_generator import IdentityGenerator

    spec = GenrePipelineSpec(
        genre=Genre.GENTLEFEMDOM,
        slug="gentlefemdom",
        core_ids=("sensual_dominance", "tender_surrender", "romantic_authority"),
        template_factory=factory,
        validate_choices=validate_choices,
        identity_strategy=IdentityGenerator.from_choices,
        browser_title="Gentle Femdom Story Identity Authoring",
        session_dir_name="gentlefemdom",
        contract_file="src/auteur/genres/data/gentlefemdom.yaml",
    )
    _GENRE_SPECS[Genre.GENTLEFEMDOM] = spec


def _initialize_registry():
    """Initialize all registered genres."""
    _register_netorare()
    _register_mystery()
    _register_gentlefemdom()


def get_genre_pipeline(genre: Genre) -> GenrePipelineSpec:
    """Get pipeline spec for a genre."""
    if not _GENRE_SPECS:
        _initialize_registry()
    if genre not in _GENRE_SPECS:
        raise ValueError(f"Unknown genre: {genre}")
    return _GENRE_SPECS[genre]


def get_all_genres() -> List[GenrePipelineSpec]:
    """Get all registered genre specs."""
    if not _GENRE_SPECS:
        _initialize_registry()
    return list(_GENRE_SPECS.values())
