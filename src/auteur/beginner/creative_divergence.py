"""Derived creative-divergence hints for Beginner-facing reconciliation.

This module is intentionally heuristic and non-authoritative. It helps the UI
explain what may have changed in prose. It never mutates accepted story state,
decides canon, or replaces owning semantic workflows.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

_NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b")
_LOCATION_RE = re.compile(
    r"\b(?:at|in|inside|into|to|from)\s+(?:the\s+)?"
    r"([a-z][a-z'-]*(?:\s+[a-z][a-z'-]*){0,4})",
    re.IGNORECASE,
)
_STOP_LOCATION_WORDS = {
    "and", "but", "who", "that", "which", "where", "when", "while", "with",
    "after", "before", "because", "as", "then", "there", "here",
}
_PLACE_HEAD_WORDS = {
    "alley", "apartment", "archive", "attic", "bar", "basement", "beach",
    "bridge", "building", "bunker", "cabin", "cafe", "campus", "castle",
    "cave", "cellar", "chapel", "church", "city", "clinic", "convent",
    "courthouse", "courtroom", "courtyard", "dock", "estate", "factory",
    "farm", "field", "forest", "gallery", "garden", "harbor", "hospital",
    "hotel", "house", "island", "jail", "kitchen", "lab", "laboratory",
    "lake", "library", "lobby", "market", "motel", "mountain", "museum",
    "office", "ocean", "palace", "park", "plaza", "port", "precinct",
    "prison", "restaurant", "river", "road", "room", "school", "sea",
    "shop", "shore", "station", "store", "street", "temple", "theater",
    "theatre", "tower", "town", "tunnel", "valley", "village", "warehouse",
    "woods",
}
_FALSE_NAMES = {
    "Chapter One", "Chapter Two", "Scene One", "Scene Two",
    "Quick Draft", "Story Identity", "Story Structure",
}


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _names(text: str) -> set[str]:
    return {
        value.strip()
        for value in _NAME_RE.findall(text or "")
        if value.strip() not in _FALSE_NAMES
    }


def _looks_like_place(phrase: str) -> bool:
    words = phrase.casefold().split()
    return bool(words) and words[-1] in _PLACE_HEAD_WORDS


def _location_phrases(text: str) -> set[str]:
    phrases: set[str] = set()
    for match in _LOCATION_RE.finditer(text or ""):
        words = match.group(1).strip().split()
        kept: list[str] = []
        for word in words:
            if word.casefold() in _STOP_LOCATION_WORDS:
                break
            kept.append(word)
        phrase = " ".join(kept).strip(" ,.;:!?")
        if (
            len(phrase) >= 4
            and phrase.casefold() not in {"this", "that", "there", "here"}
            and _looks_like_place(phrase)
        ):
            phrases.add(phrase)
    return phrases


def infer_creative_discoveries(
    draft_text: str,
    *,
    baseline_text: str = "",
    plan_alignment: dict[str, Any] | None = None,
    blocking_findings: Iterable[str] = (),
) -> list[dict[str, str]]:
    """Return non-authoritative hints about prose that may need reconciliation."""
    discoveries: list[dict[str, str]] = []
    baseline_norm = _normalize(baseline_text)

    for name in sorted(_names(draft_text)):
        if _normalize(name) not in baseline_norm:
            discoveries.append(
                {
                    "kind": "character_or_named_element",
                    "classification": "additive_discovery",
                    "label": "Possible new character or named element",
                    "value": name,
                    "confidence": "heuristic",
                }
            )

    for place in sorted(_location_phrases(draft_text)):
        if _normalize(place) not in baseline_norm:
            discoveries.append(
                {
                    "kind": "place",
                    "classification": "additive_discovery",
                    "label": "Possible new place",
                    "value": place,
                    "confidence": "heuristic",
                }
            )

    alignment = plan_alignment or {}
    if (
        alignment.get("status") == "observed"
        and int(alignment.get("observed_scene_count") or 0) > 0
        and alignment.get("scene_count_matches") is False
    ):
        discoveries.append(
            {
                "kind": "story_change",
                "classification": "plan_divergence",
                "label": "Chapter shape changed",
                "value": (
                    f"Draft shows {alignment.get('observed_scene_count', 0)} scene heading(s); "
                    f"the plan expected {alignment.get('planned_scene_count', 0)}."
                ),
                "confidence": "observed",
            }
        )

    for finding in blocking_findings:
        if not str(finding).strip():
            continue
        discoveries.append(
            {
                "kind": "conflict",
                "classification": "needs_author_decision",
                "label": "Possible conflict with the existing story",
                "value": str(finding).strip(),
                "confidence": "review_finding",
            }
        )

    # Keep the surface compact and deterministic.
    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in discoveries:
        key = (item["kind"], _normalize(item["value"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped[:12]


def proposal_target_for(discovery: dict[str, str]) -> str:
    kind = discovery.get("kind")
    if kind in {"character_or_named_element", "place"}:
        return "realized_state"
    if kind == "story_change":
        return "realization_or_structure"
    if kind == "conflict":
        return "owning_story_fact"
    return "realized_state"
