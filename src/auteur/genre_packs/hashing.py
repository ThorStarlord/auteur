"""Deterministic hashing for Genre Pack definitions."""

import hashlib
import json
from typing import Any
from auteur.genre_packs.models import GenrePack


def compute_pack_content_hash(pack_or_data: GenrePack | dict[str, Any] | bytes | str) -> str:
    """Compute a deterministic SHA-256 hash of a GenrePack's contents."""
    if isinstance(pack_or_data, GenrePack):
        data = pack_or_data.model_dump(mode="json")
    elif isinstance(pack_or_data, dict):
        data = pack_or_data
    elif isinstance(pack_or_data, (bytes, str)):
        if isinstance(pack_or_data, str):
            raw_bytes = pack_or_data.encode("utf-8")
        else:
            raw_bytes = pack_or_data
        return hashlib.sha256(raw_bytes).hexdigest()
    else:
        raise ValueError(f"Unsupported type for pack content hashing: {type(pack_or_data)}")

    canonical_json = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
