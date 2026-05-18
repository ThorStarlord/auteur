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

def _create_fallback_contract(genre: Genre) -> GenreContract:
    from auteur.genres.models import PsychologyBudget, PsychologyLevel, RequirementLevel
    
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
    )
