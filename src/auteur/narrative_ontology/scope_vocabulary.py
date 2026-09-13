"""Medium-neutral narrative scope vocabulary.

ADR 020 introduces Entry/Segment as semantic vocabulary without migrating the
existing Book/Chapter persistence contracts.  This module is deliberately
small and side-effect free so higher layers can opt into generic terminology
without changing stored authority or provenance.
"""

from __future__ import annotations

from enum import Enum


class EntryKind(str, Enum):
    """Presentation forms that may occupy the semantic Entry scope."""

    BOOK = "book"
    EPISODE = "episode"
    FILM = "film"
    STORY = "story"
    ROUTE = "route"
    MISSION = "mission"
    OTHER = "other"


class SegmentKind(str, Enum):
    """Presentation forms that may occupy the semantic Segment scope."""

    CHAPTER = "chapter"
    ACT = "act"
    SEQUENCE = "sequence"
    SECTION = "section"
    MISSION = "mission"
    OTHER = "other"


LEGACY_SCOPE_ALIASES: dict[str, str] = {
    "book": "entry",
    "chapter": "segment",
}


def semantic_scope_name(scope: str) -> str:
    """Return medium-neutral scope terminology without mutating stored data.

    Unknown scope names are returned unchanged.  The function is a display /
    reasoning adapter, not a persistence migration.
    """

    normalized = scope.strip().lower()
    return LEGACY_SCOPE_ALIASES.get(normalized, normalized)
