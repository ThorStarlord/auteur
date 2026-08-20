"""Explicit writer-facing editing for an existing Story Discovery brief."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Callable

from auteur.blueprint import EmotionalTrajectory, Genre, StoryMedium, StoryMode, TargetAudience
from auteur.story_discovery_brief import DiscoveryBrief
from auteur.story_discovery_guidance import BriefLifecycleState, _write_brief_atomic, inspect_working_brief
from auteur.story_discovery_intent_controls import (
    AUDIENCE_ALIASES,
    CAUSAL_ALIASES,
    CAUSAL_OPTIONS,
    CLEAR_TOKENS,
    COMPLEXITY_ALIASES,
    COMPLEXITY_OPTIONS,
    DONE_TOKENS,
    GENRE_ALIASES,
    HIERARCHY_ALIASES,
    HIERARCHY_OPTIONS,
    MEDIUM_ALIASES,
    MODE_ALIASES,
    ask_nonempty,
    current_value,
    emit,
    enum_options,
    normalize_choice,
    parse_list,
    reader,
    update_architecture_preference,
    update_emotional_trajectory,
    update_hard_constraints,
    update_story_type,
    update_target_list,
    update_target_primary,
)

_EDIT_FIELDS = {
    "1": "premise", "premise": "premise",
    "2": "genre", "genre": "genre",
    "3": "audience", "audience": "audience",
    "4": "primary", "primary": "primary", "primary experience": "primary",
    "5": "secondary", "secondary": "secondary", "secondary palette": "secondary",
    "6": "avoid", "avoid": "avoid", "avoided experiences": "avoid",
    "7": "trajectory", "trajectory": "trajectory", "emotional trajectory": "trajectory",
    "8": "complexity", "complexity": "complexity",
    "9": "causal", "causal": "causal", "causal distribution": "causal",
    "10": "hierarchy", "hierarchy": "hierarchy", "engine hierarchy": "hierarchy",
    "11": "medium", "medium": "medium",
    "12": "mode", "mode": "mode",
    "13": "constraints", "constraints": "constraints", "hard constraints": "constraints",
}


def _edit_story_type_value(
    brief: DiscoveryBrief,
    *,
    label: str,
    field_name: str,
    options: dict[str, Enum],
    aliases: dict[str, Enum],
    current_key: str,
    input_fn: Callable[[str], str] | None,
    output_fn: Callable[[str], None] | None,
) -> DiscoveryBrief:
    emit(output_fn, f"Current {label}: {current_value(brief, current_key)}")
    emit(output_fn, "Enter a new value, 'clear'/'not sure' to omit it, or press Enter to keep it.")
    emit(output_fn, "Choices: " + ", ".join(options))
    read = reader(input_fn)
    while True:
        raw = read("> ")
        normalized = normalize_choice(raw)
        if not raw.strip():
            return brief
        if normalized in CLEAR_TOKENS:
            return update_story_type(brief, field_name, None)
        match = aliases.get(normalized)
        if match is not None:
            return update_story_type(brief, field_name, match)
        emit(output_fn, "I didn't recognize that choice. Use a listed value, 'clear', or Enter.")


def _edit_architecture_value(
    brief: DiscoveryBrief,
    *,
    label: str,
    field_name: str,
    options: dict[str, Enum],
    aliases: dict[str, Enum],
    current_key: str,
    input_fn: Callable[[str], str] | None,
    output_fn: Callable[[str], None] | None,
) -> DiscoveryBrief:
    emit(output_fn, f"Current {label}: {current_value(brief, current_key)}")
    emit(output_fn, "Enter a new value, 'not sure'/'clear' to omit it, or press Enter to keep it.")
    emit(output_fn, "Choices: " + ", ".join(options))
    read = reader(input_fn)
    while True:
        raw = read("> ")
        normalized = normalize_choice(raw)
        if not raw.strip():
            return brief
        if normalized in CLEAR_TOKENS:
            return update_architecture_preference(brief, field_name, None)
        match = aliases.get(normalized)
        if match is not None:
            return update_architecture_preference(brief, field_name, match)
        emit(output_fn, "I didn't recognize that choice. Use a listed value, 'clear', or Enter.")


def edit_working_brief(
    project_root: str | Path,
    *,
    brief_path: str | Path | None = None,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> DiscoveryBrief:
    """Interactively edit explicit brief commitments, including clearing them."""

    root = Path(project_root)
    status = inspect_working_brief(root, brief_path)
    if status.state is BriefLifecycleState.ABSENT:
        raise ValueError("No Story Discovery brief exists to edit. Run start first.")
    if status.state is BriefLifecycleState.INVALID:
        raise ValueError(
            f"Cannot safely edit invalid Story Discovery brief {status.path}: {status.error}. "
            "Repair or move the file first."
        )
    assert status.brief is not None
    brief = status.brief
    path = status.path
    read = reader(input_fn)

    emit(
        output_fn,
        "Edit the Story Discovery brief. Changes are non-canonical, but changed "
        "declared intent makes prior intent-aware results stale.",
    )
    emit(output_fn, "Choose a field by number/name. Type 'done' when finished.")
    emit(
        output_fn,
        "1 premise | 2 genre | 3 audience | 4 primary experience | "
        "5 secondary palette | 6 avoided experiences",
    )
    emit(
        output_fn,
        "7 emotional trajectory | 8 complexity | 9 causal distribution | "
        "10 engine hierarchy | 11 medium | 12 mode | 13 hard constraints",
    )

    while True:
        normalized_field = normalize_choice(read("Edit field: "))
        if normalized_field in DONE_TOKENS:
            return brief
        field = _EDIT_FIELDS.get(normalized_field)
        if field is None:
            emit(output_fn, "I didn't recognize that field. Choose a listed field or type 'done'.")
            continue
        before = brief.declared_intent()

        if field == "premise":
            emit(output_fn, f"Current premise: {brief.premise}")
            raw = read("New premise (Enter keeps current): ").strip()
            if raw:
                if normalize_choice(raw) in CLEAR_TOKENS:
                    emit(output_fn, "Premise cannot be cleared because DiscoveryBrief requires one.")
                else:
                    payload = brief.declared_intent()
                    payload["premise"] = raw
                    brief = DiscoveryBrief.model_validate(payload)
        elif field == "genre":
            brief = _edit_story_type_value(
                brief, label="genre", field_name="genre", options=enum_options(Genre),
                aliases=GENRE_ALIASES, current_key="genre", input_fn=input_fn, output_fn=output_fn,
            )
        elif field == "audience":
            brief = _edit_story_type_value(
                brief, label="audience", field_name="target_audience", options=enum_options(TargetAudience),
                aliases=AUDIENCE_ALIASES, current_key="audience", input_fn=input_fn, output_fn=output_fn,
            )
        elif field == "medium":
            brief = _edit_story_type_value(
                brief, label="medium", field_name="medium", options=enum_options(StoryMedium),
                aliases=MEDIUM_ALIASES, current_key="medium", input_fn=input_fn, output_fn=output_fn,
            )
        elif field == "mode":
            brief = _edit_story_type_value(
                brief, label="mode", field_name="mode", options=enum_options(StoryMode),
                aliases=MODE_ALIASES, current_key="mode", input_fn=input_fn, output_fn=output_fn,
            )
        elif field == "primary":
            emit(output_fn, f"Current primary reader experience: {current_value(brief, 'primary')}")
            emit(
                output_fn,
                "Enter a new governing experience, 'clear'/'not sure' to remove the whole "
                "target-experience block, or Enter to keep it.",
            )
            raw = read("> ").strip()
            if raw:
                brief = update_target_primary(
                    brief,
                    None if normalize_choice(raw) in CLEAR_TOKENS else raw,
                )
        elif field in {"secondary", "avoid"}:
            if brief.target_experience is None:
                emit(output_fn, "Set a primary target experience before editing supporting experience fields.")
            else:
                label = "secondary emotional palette" if field == "secondary" else "avoided experiences"
                emit(output_fn, f"Current {label}: {current_value(brief, field)}")
                emit(
                    output_fn,
                    "Enter a comma-separated replacement, 'clear'/'not sure' to omit it, or Enter to keep it.",
                )
                raw = read("> ").strip()
                if raw:
                    values = None if normalize_choice(raw) in CLEAR_TOKENS else parse_list(raw)
                    if field == "secondary":
                        brief = update_target_list(brief, "secondary_palette", "secondary", values)
                    else:
                        brief = update_target_list(brief, "avoided_experiences", "avoid", values)
        elif field == "trajectory":
            if brief.target_experience is None:
                emit(output_fn, "Set a primary target experience before editing emotional trajectory.")
            else:
                emit(output_fn, f"Current emotional trajectory: {current_value(brief, 'trajectory')}")
                emit(
                    output_fn,
                    "Enter a new pattern, 'clear'/'not sure' to omit the trajectory, or Enter to keep it.",
                )
                pattern = read("Pattern: ").strip()
                if pattern:
                    if normalize_choice(pattern) in CLEAR_TOKENS:
                        brief = update_emotional_trajectory(brief, None)
                    else:
                        trajectory = EmotionalTrajectory(
                            pattern=pattern,
                            start=ask_nonempty("Start: ", input_fn=input_fn, output_fn=output_fn),
                            midpoint=ask_nonempty("Midpoint: ", input_fn=input_fn, output_fn=output_fn),
                            ending=ask_nonempty("Ending: ", input_fn=input_fn, output_fn=output_fn),
                        )
                        brief = update_emotional_trajectory(brief, trajectory)
        elif field == "complexity":
            brief = _edit_architecture_value(
                brief, label="architecture complexity", field_name="complexity", options=COMPLEXITY_OPTIONS,
                aliases=COMPLEXITY_ALIASES, current_key="complexity", input_fn=input_fn, output_fn=output_fn,
            )
        elif field == "causal":
            brief = _edit_architecture_value(
                brief, label="causal distribution", field_name="causal_distribution", options=CAUSAL_OPTIONS,
                aliases=CAUSAL_ALIASES, current_key="causal", input_fn=input_fn, output_fn=output_fn,
            )
        elif field == "hierarchy":
            brief = _edit_architecture_value(
                brief, label="engine hierarchy", field_name="engine_hierarchy", options=HIERARCHY_OPTIONS,
                aliases=HIERARCHY_ALIASES, current_key="hierarchy", input_fn=input_fn, output_fn=output_fn,
            )
        elif field == "constraints":
            emit(output_fn, f"Current hard constraints: {current_value(brief, 'constraints')}")
            emit(
                output_fn,
                "Enter replacement constraints one at a time. 'clear'/'not sure' removes "
                "the declaration; Enter keeps it.",
            )
            first = read("> ").strip()
            if first:
                if normalize_choice(first) in CLEAR_TOKENS:
                    brief = update_hard_constraints(brief, None)
                else:
                    constraints = [first]
                    while True:
                        nxt = read("Another constraint (blank to finish): ").strip()
                        if not nxt:
                            break
                        constraints.append(nxt)
                    brief = update_hard_constraints(brief, constraints)

        if brief.declared_intent() != before:
            _write_brief_atomic(brief, path)
            emit(output_fn, "Saved.")
        else:
            emit(output_fn, "No change.")
