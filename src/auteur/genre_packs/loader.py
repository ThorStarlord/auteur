"""Genre Pack loader using package-resource APIs and YAML parsing."""

from pathlib import Path
import importlib.resources
from typing import Union
import yaml
from pydantic import ValidationError

from auteur.genre_packs.models import GenrePack, GenreErrorCode, GenrePackError
from auteur.genre_packs.hashing import compute_pack_content_hash


def load_genre_pack(path_or_text: Union[str, Path]) -> tuple[GenrePack, str]:
    """Load a GenrePack from a YAML file path or raw YAML string.
    
    Returns:
        tuple[GenrePack, content_hash]
    """
    try:
        p = Path(path_or_text)
        if p.exists() and p.is_file():
            text = p.read_text(encoding="utf-8")
        else:
            text = str(path_or_text)
    except Exception:
        text = str(path_or_text)

    try:
        raw_data = yaml.safe_load(text)
    except Exception as e:
        raise GenrePackError(
            GenreErrorCode.PACK_INVALID,
            f"Failed to parse YAML content for Genre Pack: {e}",
            {"error": str(e)},
        ) from e

    if not isinstance(raw_data, dict):
        raise GenrePackError(
            GenreErrorCode.PACK_INVALID,
            "Genre Pack YAML root must be a mapping dictionary.",
            {"raw_data": str(raw_data)},
        )

    try:
        pack = GenrePack.model_validate(raw_data)
    except ValidationError as e:
        raise GenrePackError(
            GenreErrorCode.PACK_INVALID,
            f"Genre Pack schema validation failed: {e}",
            {"validation_errors": e.errors()},
        ) from e

    content_hash = compute_pack_content_hash(text)
    return pack, content_hash


def load_built_in_pack(pack_id: str, version: str = "0.1.0") -> tuple[GenrePack, str]:
    """Load a built-in Genre Pack using importlib.resources."""
    try:
        resource_path = importlib.resources.files("auteur.genre_packs").joinpath(
            f"data/{pack_id}/{version}.yaml"
        )
        text = resource_path.read_text(encoding="utf-8")
        return load_genre_pack(text)
    except Exception as e:
        # Fallback to direct relative path in development
        dev_path = Path(__file__).parent / f"data/{pack_id}/{version}.yaml"
        if dev_path.exists():
            return load_genre_pack(dev_path)

        raise GenrePackError(
            GenreErrorCode.PACK_NOT_FOUND,
            f"Built-in Genre Pack '{pack_id}' version '{version}' not found.",
            {"pack_id": pack_id, "version": version, "error": str(e)},
        ) from e
