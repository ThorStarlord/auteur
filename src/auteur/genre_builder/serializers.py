from __future__ import annotations

from pathlib import Path

import yaml

from auteur.genre_builder.models import CustomGenreContract


def load_custom_genre_contract(path: Path) -> CustomGenreContract:
    return CustomGenreContract.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})


def write_custom_genre_contract(custom: CustomGenreContract, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(custom.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    return path


def write_genre_guide(markdown: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return path


def install_custom_genre_contract(custom: CustomGenreContract, project: Path) -> Path:
    return write_custom_genre_contract(
        custom,
        project / "genres" / "custom" / f"{custom.custom_genre_id}.yaml",
    )

