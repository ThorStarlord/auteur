"""Deterministic controls shared by Story Discovery refine/edit flows."""

from __future__ import annotations

from enum import Enum
from typing import Callable

from auteur.blueprint import EmotionalTrajectory, Genre, StoryMedium, StoryMode, TargetAudience
from auteur.narrative_ontology.architecture_preferences import (
    CausalDistributionPreference,
    ComplexityPreference,
    EngineHierarchyPreference,
)
from auteur.story_discovery_brief import DiscoveryBrief

UNKNOWN_TOKENS = {"", "not sure", "unsure", "unknown", "skip"}
CLEAR_TOKENS = {"clear", "remove", "unset", "not sure", "unsure", "unknown"}
DONE_TOKENS = {"done", "finish", "finished", "exit", "quit"}

COMPLEXITY_OPTIONS = {
    "focused": ComplexityPreference.FOCUSED,
    "layered": ComplexityPreference.LAYERED,
    "richly interconnected": ComplexityPreference.MAXIMALIST,
}
CAUSAL_OPTIONS = {
    "one strong cause": CausalDistributionPreference.CONCENTRATED,
    "one main cause with meaningful contributors": CausalDistributionPreference.LAYERED,
    "several interacting causes": CausalDistributionPreference.MIXED,
}
HIERARCHY_OPTIONS = {
    "one clearly dominant engine": EngineHierarchyPreference.SINGLE_CENTER,
    "one main engine with substantial supporting layers": EngineHierarchyPreference.PRIMARY_WITH_LAYERS,
    "several engines carrying comparable weight": EngineHierarchyPreference.ENSEMBLE,
}


def emit(output_fn: Callable[[str], None] | None, text: str = "") -> None:
    (print if output_fn is None else output_fn)(text)


def reader(input_fn: Callable[[str], str] | None) -> Callable[[str], str]:
    return input if input_fn is None else input_fn


def normalize_choice(value: str) -> str:
    return " ".join(value.strip().casefold().replace("_", " ").replace("-", " ").split())


def choice_aliases(enum_type: type[Enum]) -> dict[str, Enum]:
    return {normalize_choice(str(member.value)): member for member in enum_type}


def option_aliases(options: dict[str, Enum]) -> dict[str, Enum]:
    aliases: dict[str, Enum] = {}
    for label, member in options.items():
        aliases[normalize_choice(label)] = member
        aliases[normalize_choice(str(member.value))] = member
    return aliases


GENRE_ALIASES = choice_aliases(Genre)
GENRE_ALIASES["science fiction"] = Genre.SCI_FI
GENRE_ALIASES["scifi"] = Genre.SCI_FI
AUDIENCE_ALIASES = choice_aliases(TargetAudience)
MEDIUM_ALIASES = choice_aliases(StoryMedium)
MODE_ALIASES = choice_aliases(StoryMode)
COMPLEXITY_ALIASES = option_aliases(COMPLEXITY_OPTIONS)
CAUSAL_ALIASES = option_aliases(CAUSAL_OPTIONS)
HIERARCHY_ALIASES = option_aliases(HIERARCHY_OPTIONS)


def enum_options(enum_type: type[Enum]) -> dict[str, Enum]:
    return {str(member.value).replace("_", " "): member for member in enum_type}


def ask_nonempty(
    prompt: str,
    *,
    input_fn: Callable[[str], str] | None,
    output_fn: Callable[[str], None] | None,
) -> str:
    read = reader(input_fn)
    while True:
        value = read(prompt).strip()
        if value:
            return value
        emit(output_fn, "Please give me a complete value, or interrupt and resume later.")


def ask_optional_choice(
    question: str,
    why: str,
    options: dict[str, Enum],
    aliases: dict[str, Enum],
    *,
    input_fn: Callable[[str], str] | None,
    output_fn: Callable[[str], None] | None,
) -> Enum | None:
    emit(output_fn, question)
    emit(output_fn, f"Why this matters: {why}")
    emit(output_fn, "Choices: " + ", ".join(options) + ", not sure")
    read = reader(input_fn)
    while True:
        normalized = normalize_choice(read("> "))
        if normalized in UNKNOWN_TOKENS:
            return None
        match = aliases.get(normalized)
        if match is not None:
            return match
        emit(output_fn, "I didn't recognize that choice. Use a listed option or 'not sure'.")


def parse_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def update_story_type(brief: DiscoveryBrief, field_name: str, value: Enum | None) -> DiscoveryBrief:
    payload = brief.declared_intent()
    story_type = dict(payload.get("story_type") or {})
    if value is None:
        story_type.pop(field_name, None)
    else:
        story_type[field_name] = value.value
    if story_type:
        payload["story_type"] = story_type
    else:
        payload.pop("story_type", None)
    return DiscoveryBrief.model_validate(payload)


def target_payload(brief: DiscoveryBrief) -> dict[str, object]:
    return dict(brief.declared_intent().get("target_experience") or {})


def update_target_primary(brief: DiscoveryBrief, primary: str | None) -> DiscoveryBrief:
    payload = brief.declared_intent()
    if primary is None:
        # TargetExperience requires a primary promise, so do not persist an invalid
        # secondary-only block when the author explicitly clears the primary.
        payload.pop("target_experience", None)
        return DiscoveryBrief.model_validate(payload)
    target = dict(payload.get("target_experience") or {})
    target.pop("primary", None)
    target["primary_emotional_promise"] = primary
    payload["target_experience"] = target
    return DiscoveryBrief.model_validate(payload)


def update_target_list(
    brief: DiscoveryBrief,
    field_name: str,
    compatibility_field: str,
    values: list[str] | None,
) -> DiscoveryBrief:
    payload = brief.declared_intent()
    target = dict(payload.get("target_experience") or {})
    if not target:
        raise ValueError("Set a primary target experience before refining supporting experience fields.")
    target.pop(compatibility_field, None)
    if values is None:
        target.pop(field_name, None)
    else:
        target[field_name] = values
    payload["target_experience"] = target
    return DiscoveryBrief.model_validate(payload)


def update_emotional_trajectory(
    brief: DiscoveryBrief,
    trajectory: EmotionalTrajectory | None,
) -> DiscoveryBrief:
    payload = brief.declared_intent()
    target = dict(payload.get("target_experience") or {})
    if not target:
        raise ValueError("Set a primary target experience before refining its emotional trajectory.")
    target.pop("progression", None)
    if trajectory is None:
        target.pop("emotional_trajectory", None)
    else:
        target["emotional_trajectory"] = trajectory.model_dump(mode="json")
    payload["target_experience"] = target
    return DiscoveryBrief.model_validate(payload)


def update_architecture_preference(
    brief: DiscoveryBrief,
    field_name: str,
    value: Enum | None,
) -> DiscoveryBrief:
    payload = brief.declared_intent()
    preferences = dict(payload.get("architecture_preferences") or {})
    if value is None:
        preferences.pop(field_name, None)
    else:
        preferences[field_name] = value.value
    if preferences:
        payload["architecture_preferences"] = preferences
    else:
        payload.pop("architecture_preferences", None)
    return DiscoveryBrief.model_validate(payload)


def update_hard_constraints(brief: DiscoveryBrief, constraints: list[str] | None) -> DiscoveryBrief:
    payload = brief.declared_intent()
    if constraints is None:
        payload.pop("hard_constraints", None)
    else:
        payload["hard_constraints"] = list(constraints)
    return DiscoveryBrief.model_validate(payload)


def current_value(brief: DiscoveryBrief, field_name: str) -> str:
    declared = brief.declared_intent()
    story_type = dict(declared.get("story_type") or {})
    target = dict(declared.get("target_experience") or {})
    preferences = dict(declared.get("architecture_preferences") or {})
    values: dict[str, object] = {
        "premise": brief.premise,
        "genre": story_type.get("genre"),
        "audience": story_type.get("target_audience"),
        "primary": target.get("primary_emotional_promise") or target.get("primary"),
        "secondary": target.get("secondary_palette") or target.get("secondary"),
        "avoid": target.get("avoided_experiences") or target.get("avoid"),
        "trajectory": target.get("emotional_trajectory"),
        "complexity": preferences.get("complexity"),
        "causal": preferences.get("causal_distribution"),
        "hierarchy": preferences.get("engine_hierarchy"),
        "medium": story_type.get("medium"),
        "mode": story_type.get("mode"),
        "constraints": declared.get("hard_constraints"),
    }
    value = values.get(field_name)
    return "not specified" if value is None else str(value)
