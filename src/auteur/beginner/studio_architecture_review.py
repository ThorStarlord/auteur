"""Deterministic review projection for a working Narrative Architecture revision.

The comparator reports observable before/after meaning and the candidate's own
summary. It never invents why an agent changed a component and never treats a
JSON difference as accepted-story impact.
"""
from __future__ import annotations

from typing import Any

_COMPONENT_FIELDS = (
    ("nodes", "id", "node", "title"),
    ("links", "id", "link", "id"),
    ("phases", "id", "phase", "title"),
    ("emotion_targets", "id", "emotion_target", "id"),
    ("complex_emotions", "id", "complex_emotion", "title"),
    ("genre_contracts", "genre_node_id", "genre_contract", "genre_node_id"),
    ("genre_interactions", "id", "genre_interaction", "id"),
)

_FIELD_LABELS = {field: label for field, _, label, _ in _COMPONENT_FIELDS}
_ID_KEYS = {field: key for field, key, _, _ in _COMPONENT_FIELDS}


def candidate_diff(previous: dict, proposed: dict) -> dict:
    """Explain a revision without confusing proposal changes with story impact."""
    categories: dict[str, Any] = {}
    for field, key, _, _ in _COMPONENT_FIELDS:
        old = {entry[key]: entry for entry in previous.get(field, [])}
        new = {entry[key]: entry for entry in proposed.get(field, [])}
        categories[field] = {
            "added": sorted(new.keys() - old.keys()),
            "removed": sorted(old.keys() - new.keys()),
            "changed": sorted(k for k in new.keys() & old.keys() if new[k] != old[k]),
        }
    categories["summary_changed"] = previous.get("summary") != proposed.get("summary")
    categories["note"] = (
        "Working architecture proposal only. Accepted Identity, Structure, Book, "
        "relations and prose remain unchanged. Any real downstream impact needs "
        "the existing source-backed impact/revision workflows."
    )
    return categories


def _title(kind: str, identifier: str, entry: dict | None) -> str:
    if not entry:
        return identifier
    if kind == "node":
        return str(entry.get("title") or identifier)
    if kind == "link":
        return f"{entry.get('source', '?')} -> {entry.get('target', '?')}"
    if kind == "phase":
        return str(entry.get("title") or identifier)
    if kind == "emotion_target":
        return f"{entry.get('emotion', 'emotion')} · {entry.get('role', 'role')}"
    if kind == "complex_emotion":
        return str(entry.get("title") or identifier)
    if kind == "genre_contract":
        return str(entry.get("genre_node_id") or identifier)
    if kind == "genre_interaction":
        return (
            f"{entry.get('source_genre_id', '?')} "
            f"{entry.get('kind', 'interaction')} "
            f"{entry.get('target_genre_id', '?')}"
        )
    return identifier


def _summary(kind: str, entry: dict | None) -> str:
    if not entry:
        return "(not present)"
    if kind == "node":
        return str(entry.get("summary") or "(no summary)")
    if kind == "link":
        return str(entry.get("function") or "(no relationship function)")
    if kind == "phase":
        parts = [str(entry.get("narrative_function") or "(no narrative function)")]
        if entry.get("reader_experience"):
            parts.append(f"Reader experience: {entry['reader_experience']}")
        if entry.get("transition"):
            parts.append(f"Transition: {entry['transition']}")
        return " | ".join(parts)
    if kind == "emotion_target":
        parts = [str(entry.get("intended_effect") or "(no intended effect)")]
        if entry.get("eliciting_condition"):
            parts.append(f"Elicited by: {entry['eliciting_condition']}")
        return " | ".join(parts)
    if kind == "complex_emotion":
        components = ", ".join(str(value) for value in entry.get("basic_emotions", []))
        return f"{entry.get('context') or '(no context)'} ({components})"
    if kind == "genre_contract":
        return (
            f"Role: {entry.get('role')}; engine: "
            f"{entry.get('narrative_engine') or '(none)'}; structure: "
            f"{entry.get('structural_pattern') or '(none)'}"
        )
    if kind == "genre_interaction":
        return str(entry.get("mechanism") or "(no interaction mechanism)")
    return str(entry)


def _changed_fields(before: dict, after: dict) -> list[str]:
    keys = set(before) | set(after)
    return sorted(key for key in keys if before.get(key) != after.get(key))


def _component(
    kind: str, identifier: str, before: dict | None, after: dict | None,
    change: str,
) -> dict:
    return {
        "kind": kind,
        "id": identifier,
        "title": _title(kind, identifier, after or before),
        "change": change,
        "before": _summary(kind, before),
        "after": _summary(kind, after),
        "changed_fields": (
            _changed_fields(before, after) if before is not None and after is not None
            else []
        ),
    }


def _author_declared_preservation(
    previous: dict, proposed: dict, preserved_ids: dict[str, set[str]],
) -> tuple[list[dict], list[dict]]:
    previous_targets = {
        target.get("id"): target for target in previous.get("emotion_targets", [])
    }
    proposed_targets = {
        target.get("id"): target for target in proposed.get("emotion_targets", [])
    }
    preserved: list[dict] = []
    changed: list[dict] = []
    for identifier, target in proposed_targets.items():
        if target.get("provenance") != "author_declared":
            continue
        if identifier in preserved_ids["emotion_targets"]:
            preserved.append({
                "id": identifier,
                "emotion": target.get("emotion"),
                "role": target.get("role"),
                "status": "preserved",
            })
        elif identifier in previous_targets:
            changed.append({
                "id": identifier,
                "before": previous_targets[identifier].get("role"),
                "after": target.get("role"),
                "status": "changed",
            })
    return preserved, changed


def build_architecture_review(
    previous: dict, proposed: dict, instruction: str,
    accepted_identity: dict | None = None,
) -> dict:
    """Project a before/after review from observable candidate fields only."""
    changes = candidate_diff(previous, proposed)
    changed_components: list[dict] = []
    preserved_ids: dict[str, set[str]] = {}
    for field, key, kind, _ in _COMPONENT_FIELDS:
        old = {entry[key]: entry for entry in previous.get(field, [])}
        new = {entry[key]: entry for entry in proposed.get(field, [])}
        preserved_ids[field] = set(old.keys() & new.keys()) - set(
            changes[field]["changed"]
        )
        for identifier in changes[field]["added"]:
            changed_components.append(
                _component(kind, identifier, None, new[identifier], "added"),
            )
        for identifier in changes[field]["removed"]:
            changed_components.append(
                _component(kind, identifier, old[identifier], None, "removed"),
            )
        for identifier in changes[field]["changed"]:
            changed_components.append(
                _component(kind, identifier, old[identifier], new[identifier], "changed"),
            )
    if changes["summary_changed"]:
        changed_components.insert(0, {
            "kind": "summary",
            "id": "summary",
            "title": "Governing summary",
            "change": "changed",
            "before": str(previous.get("summary") or "(not present)"),
            "after": str(proposed.get("summary") or "(not present)"),
            "changed_fields": ["summary"],
        })
    author_preserved, author_changed = _author_declared_preservation(
        previous, proposed, preserved_ids,
    )
    accepted_constraints: list[str] = []
    accepted_not_this: list[str] = []
    if accepted_identity:
        accepted_constraints = list(accepted_identity.get("hard_constraints") or [])
        accepted_not_this = list(accepted_identity.get("not_this") or [])
    summary = proposed.get("summary")
    rationale = (
        {
            "status": "provided",
            "source": "candidate.summary",
            "text": str(summary),
        }
        if isinstance(summary, str) and summary.strip()
        else {
            "status": "missing",
            "source": "candidate.summary",
            "text": None,
            "note": "The candidate supplied no rationale summary; none was invented.",
        }
    )
    return {
        "authority": "working_architecture_comparison_not_story_impact",
        "requested_change": instruction,
        "changes": changes,
        "changed_components": changed_components,
        "preserved": {
            "ids": {
                field: sorted(preserved_ids[field]) for field, _, _, _ in _COMPONENT_FIELDS
            },
            "counts": {
                field: len(preserved_ids[field]) for field, _, _, _ in _COMPONENT_FIELDS
            },
            "author_declared_emotion_targets": author_preserved,
            "author_declared_emotion_changes": author_changed,
            "accepted_constraints": accepted_constraints,
            "accepted_not_this": accepted_not_this,
        },
        "proposed_rationale": rationale,
        "note": (
            "This is a review of a noncanonical working proposal. It does not "
            "change accepted Identity, Structure, Realization, Expression or "
            "shared ontology."
        ),
    }
