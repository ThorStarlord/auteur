from __future__ import annotations

import re

from auteur.genre_builder.models import GenreBrief


REQUIRED_SECTIONS = [
    "Genre",
    "Emotional Promise",
    "Core Truth",
    "Required Tropes",
    "Optional Tropes",
    "Forbidden Mismatches",
    "Common Failures",
    "Scope",
    "Setup Requirements",
]


def parse_genre_brief(markdown: str) -> GenreBrief:
    sections: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []
    for line in markdown.splitlines():
        heading = re.match(r"^#\s+(.+?)\s*$", line)
        if heading:
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = heading.group(1).strip()
            buffer = []
            continue
        if current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()

    diagnostics = [
        f"Missing required section: {section}"
        for section in REQUIRED_SECTIONS
        if not sections.get(section, "").strip()
    ]
    return GenreBrief(sections=sections, diagnostics=diagnostics)


def parse_bullets(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped:
            items.append(stripped)
    return items


def parse_key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def slugify_genre_id(display_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", display_name.lower()).strip("_")
    return slug or "custom_genre"

