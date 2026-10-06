"""Bounded, provenance-preserving context composition for Chapter continuation.

This module is deliberately not retrieval. It selects from already accepted,
addressable evidence using recency and overlap with the current Chapter plan.
All accepted evidence remains indexed by source reference even when omitted from
the compact generation-facing view.
"""
from __future__ import annotations

import re
from typing import Any


_RECENT_CHAPTER_WINDOW = 2
_STOPWORDS = {
    "about", "after", "again", "against", "already", "because", "before",
    "being", "chapter", "continue", "current", "from", "have", "into",
    "later", "only", "other", "preserve", "should", "story", "their",
    "there", "these", "this", "through", "using", "while", "with",
}


def _text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for item in value.values():
            values.extend(_text_values(item))
        return values
    if isinstance(value, (list, tuple)):
        values = []
        for item in value:
            values.extend(_text_values(item))
        return values
    if value is None:
        return []
    return [str(value)]


def _tokens(*values: Any) -> set[str]:
    words: set[str] = set()
    for value in values:
        for text in _text_values(value):
            normalized = re.sub(r"[^a-z0-9]+", " ", text.casefold())
            words.update(
                word for word in normalized.split()
                if len(word) >= 4 and word not in _STOPWORDS
            )
    return words


def _outline_focus(outline: dict[str, Any], role: str | None) -> set[str]:
    """Use existing planning text; do not infer a new semantic representation."""
    values: list[Any] = [role or ""]
    for key in ("chapter_summary", "summary", "purpose", "role", "setup", "payoff"):
        if key in outline:
            values.append(outline[key])
    scenes = outline.get("scenes")
    if isinstance(scenes, list):
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            for key in (
                "summary", "purpose", "key_events", "character_state_changes",
                "arc_advancements", "continuity_constraints", "entry_state",
                "immediate_goal", "conflict", "important_change", "ending_state",
            ):
                if key in scene:
                    values.append(scene[key])
    return _tokens(values)


def _event_tokens(event: dict[str, Any]) -> set[str]:
    deltas = event.get("deltas") if isinstance(event.get("deltas"), dict) else {}
    return _tokens(event.get("summary", ""), deltas)


def _normalized_notice(item: dict[str, Any], *, authority: str) -> dict[str, Any]:
    return {
        "summary": str(item.get("summary", "")),
        "source_ref": str(item.get("source_ref", "")),
        "chapter_index": item.get("chapter_index") if type(item.get("chapter_index")) is int else None,
        "authority": authority,
        "blocking": bool(item.get("blocking", False)),
    }


def compose_author_context(
    *,
    chapter_index: int,
    role: str | None,
    role_ref: str | None,
    current_outline: dict[str, Any],
    accepted_events: list[dict[str, Any]],
    prior_chapter_refs: list[dict[str, Any]],
    structure_refs: list[str],
    pending_updates: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
    needs_attention: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    """Compose a bounded Chapter-N context while preserving full evidence access.

    Selection is intentionally modest: retain events from the prior two Chapters
    plus older events whose accepted summary/state overlaps the current plan's
    existing text. This is deterministic lexical relevance over accepted data,
    not semantic search, embeddings, or a new source of story truth.
    """
    if chapter_index < 1:
        raise ValueError("chapter_index must be positive")

    focus = _outline_focus(current_outline, role)
    recent_floor = max(1, chapter_index - _RECENT_CHAPTER_WINDOW)
    accepted_history: list[dict[str, Any]] = []
    all_event_refs: list[str] = []
    omitted_event_refs: list[str] = []

    for position, event in enumerate(accepted_events):
        if not isinstance(event, dict):
            continue
        event_chapter = event.get("chapter_index")
        if type(event_chapter) is not int or event_chapter < 1 or event_chapter >= chapter_index:
            continue
        source_ref = f"bible.json#/events/{position}"
        all_event_refs.append(source_ref)
        reasons: list[str] = []
        if event_chapter >= recent_floor:
            reasons.append("recent_accepted_outcome")
        overlap = sorted(focus & _event_tokens(event))
        if overlap:
            reasons.append("current_plan_overlap:" + ",".join(overlap[:6]))
        if not reasons:
            omitted_event_refs.append(source_ref)
            continue
        accepted_history.append(
            {
                "chapter_index": event_chapter,
                "summary": event.get("summary") if isinstance(event.get("summary"), str) else None,
                "deltas": dict(event.get("deltas") or {}) if isinstance(event.get("deltas"), dict) else {},
                "source_ref": source_ref,
                "authority": "accepted",
                "relevance_reasons": reasons,
            }
        )

    accepted_state: dict[str, dict[str, Any]] = {}
    for event in accepted_history:
        for field, value in event["deltas"].items():
            accepted_state[str(field)] = {
                "value": value,
                "chapter_index": event["chapter_index"],
                "source_ref": event["source_ref"],
                "authority": "accepted",
            }

    history_refs = [
        str(ref["path"])
        for ref in prior_chapter_refs
        if isinstance(ref, dict) and isinstance(ref.get("path"), str)
    ]
    pending = [
        _normalized_notice(item, authority="suggested")
        for item in pending_updates
        if isinstance(item, dict)
    ]
    uncertainty = [
        _normalized_notice(item, authority="needs_attention")
        for item in needs_attention
        if isinstance(item, dict)
    ]

    return {
        "schema": "beginner_author_context_v1",
        "current_plan": {
            "chapter_index": chapter_index,
            "role": role,
            "source_ref": role_ref,
            "authority": "planning_context",
        },
        "accepted_history": accepted_history,
        "accepted_state": accepted_state,
        "pending_updates": pending,
        "uncertainty": uncertainty,
        "evidence_index": {
            "accepted_chapter_refs": history_refs,
            "accepted_event_refs": all_event_refs,
            "structure_refs": list(structure_refs),
            "omitted_accepted_event_refs": omitted_event_refs,
        },
        "selection": {
            "mode": "bounded_recency_plus_current_plan_overlap",
            "recent_chapter_window": _RECENT_CHAPTER_WINDOW,
            "accepted_events_considered": len(all_event_refs),
            "accepted_events_selected": len(accepted_history),
            "accepted_events_omitted": len(omitted_event_refs),
        },
    }
