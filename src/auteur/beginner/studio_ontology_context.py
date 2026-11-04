"""Bounded, source-referenced ontology meanings for Studio architecture requests.

The packaged ontology remains authoritative. This module projects only the
definitions and relationship directions a working architecture request needs;
it never declares author intent, accepts a genre, or writes ontology resources.
"""
from __future__ import annotations

import re
from typing import Any

from auteur.narrative_ontology.loader.ontology_loader import OntologyLoader

_BASE_SOURCE = "auteur.data.ontology:base_ontology.yaml"
_FOUNDATIONAL_CONCEPTS = (
    "Theme", "Conflict", "Arc", "Setup", "Payoff", "Revelation", "Reversal",
    "Goal", "Beat", "Symbol", "Relationship", "Character",
)
_GENRE_ALIASES: dict[str, tuple[str, ...]] = {
    "mystery": ("mystery", "mysteries", "detective", "whodunit"),
    "netorare": ("netorare",),
    "gentlefemdom": ("gentlefemdom", "gentle femdom"),
}
_MAX_RELATIONSHIPS_PER_CONCEPT = 12
_MAX_DEFINITION_CHARS = 1200


def _mentions(text: str, alias: str) -> bool:
    if " " in alias:
        return alias in text
    return re.search(
        rf"(?<![a-z0-9_]){re.escape(alias)}(?![a-z0-9_])", text,
    ) is not None


def _explicit_genres(
    vision: str, accepted_identity: dict | None,
) -> list[tuple[str, str]]:
    """Return (genre, selection source) only for explicit, installed genres."""
    selected: dict[str, str] = {}
    if accepted_identity:
        story_type = accepted_identity.get("story_type") or {}
        accepted = " ".join(
            str(story_type.get(key) or "")
            for key in ("genre", "subgenre")
        ).lower()
        for genre, aliases in _GENRE_ALIASES.items():
            if genre in accepted or any(_mentions(accepted, alias) for alias in aliases):
                selected[genre] = "accepted_story_identity"
    text = (vision or "").lower()
    for genre, aliases in _GENRE_ALIASES.items():
        if genre not in selected and any(_mentions(text, alias) for alias in aliases):
            selected[genre] = "story_vision"
    return sorted(selected.items())


def _relationship_projection(concept: dict[str, Any]) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for relationship in concept.get("relationships", []):
        if not isinstance(relationship, dict):
            continue
        entry = {
            key: relationship[key]
            for key in (
                "source_concept", "target_concept", "cardinality",
                "description", "required",
            )
            if key in relationship
        }
        if entry:
            projected.append(entry)
        if len(projected) >= _MAX_RELATIONSHIPS_PER_CONCEPT:
            break
    return projected


def _concept_projection(
    name: str, concept: dict[str, Any], source_ref: str, genre: str | None = None,
) -> dict[str, Any]:
    entry = {
        "name": name,
        "definition": str(concept.get("definition", ""))[:_MAX_DEFINITION_CHARS],
        "relationships": _relationship_projection(concept),
        "source_ref": source_ref,
    }
    if genre is not None:
        entry["genre_extension"] = genre
    return entry


def build_relevant_ontology_context(
    vision: str, accepted_identity: dict | None,
) -> dict[str, Any]:
    """Project stable ontology meanings relevant to one working architecture.

    Foundational relationship vocabulary is always present so a fresh host agent
    receives meanings, not merely a path it may never open. Installed genre
    definitions appear only when the Vision or accepted Identity names them.
    """
    loader = OntologyLoader()
    base = loader.load_base_ontology()
    concepts = [
        _concept_projection(name, base[name], _BASE_SOURCE)
        for name in _FOUNDATIONAL_CONCEPTS if name in base
    ]
    source_refs = [_BASE_SOURCE]
    genre_extensions: list[dict[str, Any]] = []
    for genre, source in _explicit_genres(vision, accepted_identity):
        try:
            genre_concepts = loader.load_genre_ontology(genre)
        except FileNotFoundError:
            continue
        genre_source = f"auteur.data.ontology:{genre}_ontology.yaml"
        source_refs.append(genre_source)
        concepts.extend(
            _concept_projection(name, genre_concepts[name], genre_source, genre)
            for name in sorted(genre_concepts)
        )
        genre_extensions.append({
            "genre": genre,
            "source": source,
            "reason": (
                "The accepted Story Identity names this installed genre."
                if source == "accepted_story_identity"
                else "The Story Vision explicitly names this installed genre."
            ),
        })
    return {
        "kind": "relevant_narrative_ontology_context",
        "authority": "derived_ontology_guidance",
        "source_refs": source_refs,
        "concepts": concepts,
        "selection": {
            "foundational_concepts": [
                name for name in _FOUNDATIONAL_CONCEPTS if name in base
            ],
            "genre_extensions": genre_extensions,
            "rationale": (
                "Foundational definitions and relationship directions are "
                "always included. Installed genre definitions are added only "
                "when explicitly named; an unnamed genre stays unknown."
            ),
            "not_story_intent": (
                "These shared ontology meanings constrain interpretation; they "
                "are not declarations of author preference or accepted canon."
            ),
        },
    }
