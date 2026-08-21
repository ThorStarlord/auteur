"""Writer-facing guided handoff to the existing F5 composition engine."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

import yaml

from auteur.story_discovery_state import (
    StoryDiscoveryStateKind,
    classify_story_discovery_project,
)

_YES = {"y", "yes"}
_NO = {"", "n", "no"}
_CANCEL = {"/cancel", "/quit", "/exit"}


class _AuthorInterrupted(Exception):
    pass


def _read(input_fn: Callable[[str], str], prompt: str) -> str:
    try:
        return input_fn(prompt)
    except (EOFError, KeyboardInterrupt) as exc:
        raise _AuthorInterrupted from exc


def _candidate_label(path: Path, candidate_id: str) -> str:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return candidate_id
    if isinstance(raw, dict):
        title = raw.get("title")
        if isinstance(title, str) and title.strip():
            return f"{candidate_id} — {title.strip()}"
    return candidate_id


def _existing_composition_artifacts(discovery_dir: Path) -> list[Path]:
    return [
        path
        for path in (
            discovery_dir / "composed_candidate.yaml",
            discovery_dir / "composition_report.yaml",
        )
        if path.exists()
    ]


def _choose_candidate(
    compatible_ids: list[str],
    labels: dict[str, str],
    *,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> str | None:
    while True:
        output_fn("\nCompatible subordinate alternatives:")
        for index, candidate_id in enumerate(compatible_ids, start=1):
            output_fn(f"  {index}. {labels[candidate_id]}")
        raw = _read(input_fn, "Choose an alternative by number or candidate ID (/cancel to stop): ").strip()
        normalized = raw.lower()
        if normalized in _CANCEL:
            return None
        if raw.isdigit():
            index = int(raw)
            if 1 <= index <= len(compatible_ids):
                return compatible_ids[index - 1]
        if raw in compatible_ids:
            return raw
        output_fn("I didn't recognize that alternative. Choose one of the listed options.")


def _ask_mechanism(
    candidate_id: str,
    *,
    input_fn: Callable[[str], str],
    output_fn: Callable[[str], None],
) -> str | None:
    output_fn(
        f"\nDescribe what you want to borrow from {candidate_id} in your own words. "
        "Auteur will treat that as a subordinate mechanism, not a new primary engine."
    )
    while True:
        raw = _read(input_fn, "Mechanism to borrow (/cancel to stop): ").strip()
        if raw.lower() in _CANCEL:
            return None
        if raw:
            return raw
        output_fn("Please describe a concrete mechanism, or type /cancel.")


def dispatch_story_discovery_guided_compose(
    args: object,
    *,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> int:
    """Collect author choices, then delegate unchanged eligibility/generation to F5."""

    read = input_fn or input
    emit = output_fn or print
    root = Path(getattr(args, "project", Path(".")))
    discovery_dir = root / "story_discovery"

    try:
        state = classify_story_discovery_project(root)
    except Exception as exc:
        print(f"Error: Could not inspect Story Discovery state: {exc}", file=sys.stderr)
        return 1

    if state.kind is StoryDiscoveryStateKind.COMPOSED_CANDIDATE_AVAILABLE:
        print(
            "Error: A current composed candidate already exists. Review it before creating another; "
            "guided composition never overwrites composition evidence.",
            file=sys.stderr,
        )
        return 1
    existing = _existing_composition_artifacts(discovery_dir)
    if existing:
        names = ", ".join(path.name for path in existing)
        print(
            "Error: Existing composition artifacts are stale, incomplete, or otherwise not current "
            f"({names}). Guided composition will not overwrite them.",
            file=sys.stderr,
        )
        return 1
    if state.kind is not StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE:
        print(
            "Error: Guided composition requires a current defensible Story Discovery recommendation. "
            "Run or review Story Discovery first.",
            file=sys.stderr,
        )
        return 1
    if not state.can_compose or state.recommended_candidate_id is None:
        print(
            "Error: The current recommendation has no F4 alternatives approved as compatible subordinate mechanisms.",
            file=sys.stderr,
        )
        return 1

    primary_id = state.recommended_candidate_id
    primary_path = state.recommended_candidate_path or discovery_dir / f"{primary_id}.yaml"
    compatible_ids = list(state.compatible_secondary_candidate_ids)
    labels = {
        candidate_id: _candidate_label(discovery_dir / f"{candidate_id}.yaml", candidate_id)
        for candidate_id in compatible_ids
    }

    try:
        emit("Guided Story Discovery composition")
        emit(f"\nRecommended governing primary: {_candidate_label(primary_path, primary_id)}")
        confirm = _read(
            read,
            "Keep this recommendation as the governing primary engine? [y/N]: ",
        ).strip().lower()
        if confirm in _CANCEL or confirm in _NO:
            emit("Composition cancelled. Nothing changed.")
            return 0
        if confirm not in _YES:
            emit("Composition cancelled because the governing primary was not confirmed.")
            return 0

        borrows: list[str] = []
        remaining = list(compatible_ids)
        while remaining:
            candidate_id = _choose_candidate(
                remaining,
                labels,
                input_fn=read,
                output_fn=emit,
            )
            if candidate_id is None:
                if not borrows:
                    emit("Composition cancelled. Nothing changed.")
                    return 0
                break
            mechanism = _ask_mechanism(
                candidate_id,
                input_fn=read,
                output_fn=emit,
            )
            if mechanism is None:
                emit("Composition cancelled. Nothing changed.")
                return 0
            borrows.append(f"{candidate_id}:{mechanism}")
            remaining.remove(candidate_id)
            if not remaining:
                break
            more = _read(read, "Add another compatible subordinate layer? [y/N]: ").strip().lower()
            if more not in _YES:
                break
    except _AuthorInterrupted:
        emit("\nComposition cancelled by the author. Nothing changed.")
        return 130

    # Author choices are complete. F5 still re-loads and re-validates F3/F4 evidence
    # before constructing a provider, then re-profiles and verifies primary hierarchy.
    from auteur.story_discovery_compose import dispatch_story_discovery_compose

    f5_args = SimpleNamespace(
        discovery_dir=discovery_dir,
        primary=primary_id,
        borrow=borrows,
        output=None,
        provider=getattr(args, "provider", "anthropic"),
        model=getattr(args, "model", None),
    )
    return dispatch_story_discovery_compose(f5_args)
