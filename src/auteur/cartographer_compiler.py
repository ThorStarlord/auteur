"""Cartographer compiler & validator — logic layer for Layer 7 Cartographer.

Handles calling LLM planning prompts for all chapters, constructing unified outlines,
auto-splitting into individual chapters, and validating continuous constraints.
"""
from __future__ import annotations

import yaml as _yaml
from pathlib import Path
from typing import Any

from auteur.blueprint import StoryBlueprint
from auteur.cartographer import render_cartographer_prompt
from auteur.cartographer_models import PlanningCall
from auteur.cartographer_outline import CartographerOutline
from auteur.llm import LLMClient, LLMRequest


def compile_outline(
    project_path: Path,
    blueprint_path: Path,
    output_path: Path,
    split_output: bool = True,
    llm: LLMClient | None = None
) -> None:
    """Compile the entire storyline blueprint into a unified and validated scene outline."""
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    num_chapters = blueprint.structure.estimated_chapters or 1

    if llm is None:
        from auteur.llm.factory import build_client
        # Cartographer default
        _bp = None
        try:
            _bp = StoryBlueprint.from_yaml(blueprint_path)
        except Exception:
            pass
        llm = build_client("anthropic", None, agent_type="cartographer", blueprint=_bp)

    compiled_chapters: list[dict[str, Any]] = []

    for idx in range(1, num_chapters + 1):
        call = PlanningCall.for_chapter(blueprint, idx)
        system, user = render_cartographer_prompt(call)

        resp = llm.complete(LLMRequest(
            system=system,
            user=user,
            temperature=0.1,
            max_tokens=4000
        ))

        cleaned_text = resp.text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        chapter_outline_data = _yaml.safe_load(cleaned_text)
        
        # Verify schema
        CartographerOutline.model_validate(chapter_outline_data)
        
        chapter_outline_data["index"] = idx
        compiled_chapters.append(chapter_outline_data)

    unified_outline = {
        "title": blueprint.identity.title,
        "total_chapters": num_chapters,
        "chapters": compiled_chapters
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        _yaml.safe_dump(unified_outline, sort_keys=False),
        encoding="utf-8"
    )

    if split_output:
        for idx, ch_data in enumerate(compiled_chapters, start=1):
            ch_dir = project_path / "chapters" / f"{idx:02d}"
            ch_dir.mkdir(parents=True, exist_ok=True)
            ch_path = ch_dir / "outline.yaml"
            ch_path.write_text(
                _yaml.safe_dump(ch_data, sort_keys=False),
                encoding="utf-8"
            )


def validate_outline(
    outline_path: Path,
    blueprint_path: Path | None = None
) -> bool:
    """Deterministic, local validator for compiled cartographer outlines."""
    if not outline_path.exists():
        raise FileNotFoundError(f"Outline file not found: {outline_path}")

    data = _yaml.safe_load(outline_path.read_text(encoding="utf-8"))
    
    if isinstance(data, dict) and "chapters" in data:
        chapters = data["chapters"]
    else:
        # Chapter-scoped fallback
        chapters = [data]

    # 1. Pydantic validation
    for ch in chapters:
        CartographerOutline.model_validate(ch)

    # 2. Sequence Audit (only if full-story unified outline)
    if isinstance(data, dict) and "chapters" in data:
        indices = [ch.get("index") for ch in chapters]
        if indices != list(range(1, len(chapters) + 1)):
            raise ValueError(f"Chapter index sequence gap detected: indices found are {indices}")

    # 3. Blueprint tension waveform target comparison (if blueprint provided)
    if blueprint_path is not None:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
        for ch in chapters:
            ch_idx = ch.get("index")
            if ch_idx is not None:
                target = blueprint.tension_waveform.target_for(ch_idx)
                if target is not None:
                    estimated = ch.get("estimated_chapter_tension")
                    if estimated is not None:
                        deviation = abs(estimated - target.score)
                        if deviation > 1:
                            raise ValueError(
                                f"estimated_chapter_tension deviates from blueprint target (target={target.score}, estimated={estimated})"
                            )

    # 4. Continuous Carrier Path Checks (Local teleportation checks)
    last_known_locations: dict[str, str] = {}
    for ch in chapters:
        for scene in ch.get("scenes", []):
            for change in scene.get("character_state_changes", []):
                char = change.get("character")
                field = change.get("field")
                before = change.get("before")
                after = change.get("after")

                if field == "location":
                    prev_loc = last_known_locations.get(char)
                    if prev_loc is not None and before is not None and before != prev_loc:
                        raise ValueError(
                            f"carriers.location_teleportation: Character {char} teleported. "
                            f"Last known location was {prev_loc}, but scene started with {before}."
                        )
                    if after is not None:
                        last_known_locations[char] = after

    return True
