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
_MAX_EXPRESSION_CHAPTERS = 4
_ACCEPTED_SOURCE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_./#-])(?:bible\.json#/events/[0-9]+|chapters/[0-9]+/final\.md)"
    r"(?![A-Za-z0-9_/#-])"
)
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


def _explicit_continuity_sources(outline: dict[str, Any]) -> set[str]:
    """Read only existing Chapter/scene continuity constraints, not free prose.

    A pointer is a *request* for accepted evidence, never evidence of acceptance.
    Exact matching against the accepted source index happens below.
    """
    constraints: list[Any] = [outline.get("continuity_constraints", ())]
    scenes = outline.get("scenes")
    if isinstance(scenes, list):
        for scene in scenes:
            if isinstance(scene, dict):
                constraints.append(scene.get("continuity_constraints", ()))
    return {
        match.group(0)
        for value in constraints
        for text in _text_values(value)
        for match in _ACCEPTED_SOURCE_PATTERN.finditer(text)
    }


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
    accepted_expressions: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
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
    requested_sources = _explicit_continuity_sources(current_outline)
    recent_floor = max(1, chapter_index - _RECENT_CHAPTER_WINDOW)
    # Preserve newer accepted changes to an explicitly referenced old field,
    # even when the new event uses entirely different words.
    explicit_fields: dict[str, int] = {}
    for position, event in enumerate(accepted_events):
        if not isinstance(event, dict):
            continue
        index = event.get("chapter_index")
        if type(index) is not int or index < 1 or index >= chapter_index:
            continue
        if f"bible.json#/events/{position}" not in requested_sources:
            continue
        deltas = event.get("deltas")
        if isinstance(deltas, dict):
            for field in deltas:
                explicit_fields[str(field)] = min(index, explicit_fields.get(str(field), index))
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
        if source_ref in requested_sources:
            reasons.append("explicit_accepted_source")
        elif isinstance(event.get("deltas"), dict) and any(
            str(field) in explicit_fields
            and event_chapter >= explicit_fields[str(field)]
            for field in event["deltas"]
        ):
            reasons.append("later_update_to_explicit_source")
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
    # The Bible may contain out-of-order historical entries. The latest accepted
    # Chapter wins for each field; same-Chapter entries retain source order.
    for event in sorted(accepted_history, key=lambda item: item["chapter_index"]):
        for field, value in event["deltas"].items():
            accepted_state[str(field)] = {
                "value": value,
                "chapter_index": event["chapter_index"],
                "source_ref": event["source_ref"],
                "authority": "accepted",
            }

    # Accepted Expression remains downstream evidence even when realized-state
    # synchronization is incomplete. Select at Chapter granularity so the
    # composer stays deterministic and inspectable rather than inventing a
    # semantic summarizer or hidden retrieval layer.
    expression_candidates: list[tuple[bool, bool, int, int, dict[str, Any]]] = []
    all_expression_refs: list[str] = []
    for item in accepted_expressions:
        if not isinstance(item, dict):
            continue
        expression_chapter = item.get("chapter_index")
        source_ref = item.get("source_ref")
        text = item.get("text")
        if (
            type(expression_chapter) is not int
            or expression_chapter < 1
            or expression_chapter >= chapter_index
            or not isinstance(source_ref, str)
            or not source_ref
            or not isinstance(text, str)
        ):
            continue
        all_expression_refs.append(source_ref)
        overlap = focus & _tokens(text)
        recent = expression_chapter >= recent_floor
        explicit = source_ref in requested_sources
        if recent or overlap or explicit:
            expression_candidates.append(
                (explicit, recent, len(overlap), expression_chapter, {
                    "chapter_index": expression_chapter,
                    "text": text,
                    "source_ref": source_ref,
                    "authority": "accepted_expression",
                    "relevance_reasons": (
                        (["explicit_accepted_source"] if explicit else [])
                        + (["recent_accepted_expression"] if recent else [])
                        + (["current_plan_overlap:" + ",".join(sorted(overlap)[:6])] if overlap else [])
                    ),
                })
            )
    expression_candidates.sort(key=lambda row: (row[0], row[1], row[2], row[3]), reverse=True)
    selected_expression = [row[4] for row in expression_candidates[:_MAX_EXPRESSION_CHAPTERS]]
    selected_expression_refs = {item["source_ref"] for item in selected_expression}
    accepted_source_refs = set(all_event_refs) | set(all_expression_refs)
    unresolved_sources = sorted(
        (requested_sources - accepted_source_refs)
        | ((requested_sources & set(all_expression_refs)) - selected_expression_refs)
    )

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
    uncertainty.extend(
        {
            "summary": "A required Chapter continuity source is not available in the accepted context.",
            "source_ref": ref,
            "chapter_index": None,
            "authority": "needs_attention",
            "blocking": True,
        }
        for ref in unresolved_sources
    )

    return {
        "schema": "beginner_author_context_v1",
        "current_plan": {
            "chapter_index": chapter_index,
            "role": role,
            "source_ref": role_ref,
            "authority": "planning_context",
        },
        "accepted_history": accepted_history,
        "accepted_expression": selected_expression,
        "accepted_state": accepted_state,
        "pending_updates": pending,
        "uncertainty": uncertainty,
        "evidence_index": {
            "accepted_chapter_refs": history_refs,
            "accepted_expression_refs": all_expression_refs,
            "omitted_accepted_expression_refs": [
                ref for ref in all_expression_refs if ref not in selected_expression_refs
            ],
            "accepted_event_refs": all_event_refs,
            "structure_refs": list(structure_refs),
            "omitted_accepted_event_refs": omitted_event_refs,
            "unresolved_explicit_source_refs": unresolved_sources,
        },
        "selection": {
            "mode": "bounded_recency_plus_current_plan_overlap",
            "recent_chapter_window": _RECENT_CHAPTER_WINDOW,
            "explicit_sources_requested": len(requested_sources),
            "explicit_sources_unresolved": len(unresolved_sources),
            "accepted_events_considered": len(all_event_refs),
            "accepted_events_selected": len(accepted_history),
            "accepted_events_omitted": len(omitted_event_refs),
            "accepted_expression_chapters_selected": len(selected_expression),
            "accepted_expression_chapter_limit": _MAX_EXPRESSION_CHAPTERS,
        },
    }
