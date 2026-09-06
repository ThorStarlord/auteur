"""Resource loader for Story Design Packs."""
from __future__ import annotations

import importlib.resources
import json
from pathlib import Path
from typing import Any

import yaml

from .models import StoryDesignPack


def content_hash(pack: StoryDesignPack | dict[str, Any] | str) -> str:
    import hashlib
    if isinstance(pack, StoryDesignPack):
        value = pack.model_dump(mode="json")
    elif isinstance(pack, dict):
        value = pack
    else:
        value = yaml.safe_load(pack)
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_story_design_pack(path_or_text: str | Path) -> tuple[StoryDesignPack, str]:
    path = Path(path_or_text)
    text = path.read_text(encoding="utf-8") if path.is_file() else str(path_or_text)
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        raise ValueError("Story Design Pack YAML root must be a mapping")
    pack = StoryDesignPack.model_validate(raw)
    return pack, content_hash(pack)


def load_builtin_pack(pack_id: str, version: str = "0.1.0") -> tuple[StoryDesignPack, str]:
    resource = importlib.resources.files("auteur.story_design_packs").joinpath(
        f"data/{pack_id}/{version}.yaml"
    )
    try:
        return load_story_design_pack(resource.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Story Design Pack '{pack_id}' version '{version}' not found") from exc
