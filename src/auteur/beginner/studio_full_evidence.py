"""Read only actually present legacy genre contracts for a Studio candidate.

Never use the legacy registry's generated fallback: an absent YAML is *unknown*,
not a genre norm. These are legacy references, never verified Genre Packs.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Callable, Any

import yaml


def project_legacy_genre_evidence(
    candidate: dict | None,
    *,
    data_dir: Path | None = None,
    validate_contract: Callable[[dict], Any] | None = None,
) -> list[dict]:
    """Return source-attributed, genre-local references with no writer side effects."""
    if not isinstance(candidate, dict):
        return []
    if data_dir is None:
        data_dir = Path(__file__).resolve().parents[1] / "genres" / "data"
    output: list[dict] = []
    used: set[str] = set()
    nodes = candidate.get("nodes")
    for node in (nodes if isinstance(nodes, list) else [])[:80]:
        if not isinstance(node, dict) or node.get("category") != "genre":
            continue
        name = node.get("title")
        node_id = node.get("id")
        if not isinstance(name, str) or not isinstance(node_id, str) or not node_id:
            continue
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9 _-]{0,100}", name):
            continue
        slug = re.sub(r"[ -]+", "_", name.strip().lower())
        if not slug or slug in used or len(output) >= 14:
            continue
        filename = slug + ".yaml"
        path = data_dir / filename
        if not path.is_file() or path.is_symlink():
            continue
        try:
            content = path.read_bytes()
            if len(content) > 300_000:
                continue
            raw = yaml.safe_load(content.decode("utf-8"))
            if not isinstance(raw, dict) or raw.get("genre_id") != slug:
                continue
            if validate_contract is None:
                from auteur.genres.models import GenreContract
                validated = GenreContract.model_validate(raw)
            else:
                validated = validate_contract(raw)
            contract = validated.model_dump(mode="json") if hasattr(validated, "model_dump") else validated
            if not isinstance(contract, dict) or contract.get("genre_id") != slug:
                continue
        except (OSError, UnicodeError, ValueError, yaml.YAMLError):
            continue
        output.append({
            "genreId": node_id,
            "sourceKind": "legacy_contract",
            "sourceRef": f"genres/data/{filename}",
            "contentHash": hashlib.sha256(content).hexdigest(),
            "contract": contract,
        })
        used.add(slug)
    return output
