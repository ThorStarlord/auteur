"""PipelineRunner — orchestrates planning, drafting, validation, iteration."""

from __future__ import annotations

from typing import Any

import yaml



CARTOGRAPHER_TEMPERATURE = 0.4
CARTOGRAPHER_MAX_TOKENS = 4000



"""YAML parsing for Cartographer outlines."""


def _parse_outline_yaml(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        first_nl = stripped.find("\n")
        last_fence = stripped.rfind("```")
        if first_nl != -1 and last_fence > first_nl:
            stripped = stripped[first_nl + 1 : last_fence].strip()
    try:
        data = yaml.safe_load(stripped)
    except yaml.YAMLError as exc:
        raise ValueError(f"Cartographer YAML parse error: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Cartographer response is not a YAML mapping.")
    from auteur.cartographer_outline import CartographerOutline
    try:
        CartographerOutline.model_validate(data)
    except Exception as exc:
        raise ValueError(
            f"Cartographer outline validation error: {exc}"
        ) from exc
    return data
