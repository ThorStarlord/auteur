"""Deterministic, writer-facing reconstruction of Story Discovery evidence."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from auteur.story_discovery_state import (
    StoryDiscoveryProjectState,
    StoryDiscoveryStateKind,
    classify_story_discovery_project,
)


def _load_mapping(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return payload


def _text(value: object | None, fallback: str = "Not recorded in the persisted evidence.") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _items(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _title(path: Path | None, candidate_id: str | None = None) -> str:
    if path is None:
        return candidate_id or "Story direction"
    try:
        payload = _load_mapping(path)
    except Exception:
        return candidate_id or path.stem
    return _text(payload.get("title"), candidate_id or path.stem)


def _print_list(label: str, values: list[str]) -> None:
    print(label)
    if not values:
        print("- Not recorded in the persisted evidence.")
        return
    for value in values:
        print(f"- {value}")


def _profile(discovery_set: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    causal = discovery_set.get("causal_analysis")
    if not isinstance(causal, dict):
        return {}
    profiles = causal.get("profiles")
    if not isinstance(profiles, dict):
        return {}
    raw = profiles.get(candidate_id)
    return raw if isinstance(raw, dict) else {}


def _render_mechanics(profile: dict[str, Any]) -> None:
    print("\nWhat this story actually has the characters doing")
    print(f"Primary strategy: {_text(profile.get('primary_strategy'))}")
    print(f"Causal owner: {_text(profile.get('causal_owner'))}")
    _print_list("External actions:", _items(profile.get("external_action_pattern")))
    print(f"Pressure system: {_text(profile.get('pressure_system'))}")
    _print_list("Reversal mechanics:", _items(profile.get("reversal_mechanics")))
    print(f"Climax mechanic: {_text(profile.get('climax_mechanic'))}")
    _print_list("Recurring scene families:", _items(profile.get("scene_families")))


def _experience_lines(discovery_set: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    target = candidate.get("target_experience")
    if not isinstance(target, dict):
        declared = discovery_set.get("declared_author_intent")
        if isinstance(declared, dict):
            target = declared.get("target_experience")
    if not isinstance(target, dict):
        return ["Primary: Not recorded in the persisted evidence."]

    primary = target.get("primary_emotional_promise") or target.get("primary")
    secondary = target.get("secondary_palette") or target.get("secondary") or []
    avoided = target.get("avoided_experiences") or target.get("avoid") or []
    trajectory = target.get("emotional_trajectory")

    lines = [f"Primary: {_text(primary)}"]
    secondary_items = _items(secondary)
    if secondary_items:
        lines.append("Supporting: " + ", ".join(secondary_items))
    if isinstance(trajectory, dict):
        points = [
            _text(trajectory.get("start"), ""),
            _text(trajectory.get("midpoint"), ""),
            _text(trajectory.get("ending"), ""),
        ]
        points = [point for point in points if point]
        pattern = _text(trajectory.get("pattern"), "")
        if points or pattern:
            route = " -> ".join(points)
            prefix = f"{pattern}: " if pattern else ""
            lines.append(f"Trajectory: {prefix}{route}".rstrip())
    avoided_items = _items(avoided)
    if avoided_items:
        lines.append("Avoid: " + ", ".join(avoided_items))
    return lines


def _craft_impacts(discovery_set: dict[str, Any]) -> dict[str, dict[str, Any]]:
    craft = discovery_set.get("craft_analysis")
    if not isinstance(craft, dict) or craft.get("status") != "complete":
        return {}
    impacts = craft.get("impacts")
    if not isinstance(impacts, dict):
        return {}
    return {
        str(candidate_id): impact
        for candidate_id, impact in impacts.items()
        if isinstance(impact, dict)
    }


def _render_tradeoffs(
    root: Path,
    discovery_set: dict[str, Any],
    state: StoryDiscoveryProjectState,
) -> None:
    impacts = _craft_impacts(discovery_set)
    if not impacts and not state.problems:
        return

    print("\nTradeoffs and meaningful alternatives")
    if not impacts:
        print("Detailed craft comparison is unavailable from the current persisted evidence.")
    for candidate_id, impact in impacts.items():
        candidate_path = root / "story_discovery" / f"{candidate_id}.yaml"
        print(f"\n{_title(candidate_path, candidate_id)}")
        print(f"Gain: {_text(impact.get('gain'))}")
        print(f"Give up: {_text(impact.get('give_up'), 'No explicit give-up was recorded.')}")
        print(
            "Thematic effect: "
            + _text(impact.get("thematic_effect"), "No explicit thematic shift was recorded.")
        )
        print(f"Composition fit: {_text(impact.get('composability'))}")
        note = impact.get("composition_note")
        if isinstance(note, str) and note.strip():
            print(f"Composition note: {note.strip()}")

    if state.problems:
        print("\nEvidence notes")
        for problem in state.problems:
            print(f"- {problem}")


def _render_recommendation_actions(root: Path, state: StoryDiscoveryProjectState) -> None:
    print("\nNothing canonical has changed.")
    print("\nYou can:")
    if state.recommended_candidate_path is not None:
        try:
            display_path = state.recommended_candidate_path.relative_to(root)
        except ValueError:
            display_path = state.recommended_candidate_path
        print("- Accept this direction explicitly:")
        print(f"    auteur story-discovery accept {display_path} --output story_identity.yaml")
    if state.can_compose:
        alternatives = ", ".join(state.compatible_secondary_candidate_ids)
        print(f"- Explore a compatible composition from: {alternatives}")
        print("  The compose command still requires you to name the mechanism to borrow.")
    print("- Change your declared intent:")
    print("    auteur story-discovery start --project . --edit")
    print("- Generate a different search space:")
    print(
        "    auteur story-discovery run --brief story_discovery/brief.yaml "
        "--recommend --output story_discovery --project ."
    )


def _render_recommendation(root: Path, state: StoryDiscoveryProjectState) -> None:
    discovery_set = _load_mapping(root / "story_discovery" / "discovery_set.yaml")
    assert state.recommended_candidate_id is not None
    assert state.recommended_candidate_path is not None
    candidate = _load_mapping(state.recommended_candidate_path)
    profile = _profile(discovery_set, state.recommended_candidate_id)

    if state.recommendation_basis == "explicit_intent_fit":
        print("Best fit to your declared intent\n")
        rationale_heading = "Why this direction fits what you said you want"
        basis_note = None
    elif state.recommendation_basis == "advisory_artistic_preference":
        print("Auteur's advisory preference\n")
        rationale_heading = "Why Auteur prefers it"
        basis_note = (
            "This is a craft judgment among compatible directions, not an additional author requirement."
        )
    else:
        # Legacy artifacts predate the recommendation-basis contract. Preserve
        # their old surface without retroactively claiming an evidentiary basis.
        print("Recommended story direction\n")
        rationale_heading = "Why this fits what you said you want"
        basis_note = None

    print(_title(state.recommended_candidate_path, state.recommended_candidate_id))
    print(f"\n{rationale_heading}")
    print(
        _text(
            discovery_set.get("recommendation_rationale"),
            "The persisted run records this as the advisory recommendation, but no "
            "additional rationale was saved.",
        )
    )
    if basis_note is not None:
        print(f"\n{basis_note}")
    _render_mechanics(profile)
    print("\nReader experience")
    for line in _experience_lines(discovery_set, candidate):
        print(line)
    _render_tradeoffs(root, discovery_set, state)
    _render_recommendation_actions(root, state)


def _shared_profile_summary(discovery_set: dict[str, Any]) -> None:
    causal = discovery_set.get("causal_analysis")
    profiles = causal.get("profiles") if isinstance(causal, dict) else None
    if not isinstance(profiles, dict) or not profiles:
        return
    print("\nWhat the analyzed directions currently have in common")
    for candidate_id, raw in profiles.items():
        if not isinstance(raw, dict):
            continue
        print(
            f"- {candidate_id}: {_text(raw.get('primary_strategy'))}; "
            f"pressure = {_text(raw.get('pressure_system'))}"
        )


def _candidate_tradeoffs(discovery_set: dict[str, Any]) -> dict[str, str]:
    raw = discovery_set.get("candidate_tradeoffs")
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for candidate_id, tradeoff in raw.items():
        if isinstance(candidate_id, str) and isinstance(tradeoff, str) and tradeoff.strip():
            result[candidate_id] = tradeoff.strip()
    return result


def _render_comparative_non_adjudicable(
    root: Path,
    discovery_set: dict[str, Any],
) -> None:
    print("Auteur does not have an honest preference here.\n")
    print(
        "The surviving directions are causally distinct, but your current intent leaves "
        "the deciding artistic value genuinely open. Auteur will not invent that preference for you."
    )
    rationale = discovery_set.get("recommendation_rationale")
    if isinstance(rationale, str) and rationale.strip():
        print(f"\n{rationale.strip()}")

    tradeoffs = _candidate_tradeoffs(discovery_set)
    if tradeoffs:
        print("\nMeaningful alternatives")
        for candidate_id, tradeoff in tradeoffs.items():
            path = root / "story_discovery" / f"{candidate_id}.yaml"
            print(f"- {_title(path, candidate_id)} (`{candidate_id}`) — {tradeoff}")

    print("\nNothing canonical has changed.")
    print("\nYou can:")
    for candidate_id in tradeoffs:
        path = root / "story_discovery" / f"{candidate_id}.yaml"
        if not path.is_file():
            continue
        try:
            display_path = path.relative_to(root)
        except ValueError:
            display_path = path
        print(f"- Choose {_title(path, candidate_id)} explicitly:")
        print(f"    auteur story-discovery accept {display_path} --output story_identity.yaml")
    print("- Refine or change what you want:")
    print("    auteur story-discovery start --project . --edit")
    print("- Generate a different search space:")
    print(
        "    auteur story-discovery run --brief story_discovery/brief.yaml "
        "--recommend --output story_discovery --project ."
    )


def _render_non_adjudicable(root: Path, state: StoryDiscoveryProjectState) -> None:
    discovery_set = _load_mapping(root / "story_discovery" / "discovery_set.yaml")
    if state.non_adjudicable_reason == "comparative_judgment":
        _render_comparative_non_adjudicable(root, discovery_set)
        return

    print("Auteur does not have a defensible recommendation yet.\n")
    if state.causal_status == "not_adjudicable_near_duplicate":
        print(
            "The surviving alternatives are too causally similar to justify calling one "
            "meaningfully better than the others."
        )
    else:
        print(
            "The persisted causal evidence is too uncertain to claim that the surviving "
            "alternatives are materially different."
        )
    _shared_profile_summary(discovery_set)
    print("\nNothing canonical has changed.")
    print("\nYou can:")
    print("- Refine or change what you want:")
    print("    auteur story-discovery start --project . --edit")
    print("- Generate a genuinely different search space:")
    print(
        "    auteur story-discovery run --brief story_discovery/brief.yaml "
        "--recommend --output story_discovery --project ."
    )


def _render_composed(root: Path, state: StoryDiscoveryProjectState) -> None:
    assert state.composed_candidate_path is not None
    assert state.composition_report_path is not None
    report = _load_mapping(state.composition_report_path)
    composed = _load_mapping(state.composed_candidate_path)
    primary_id = _text(report.get("primary_candidate_id"), "current primary")
    primary_path = root / "story_discovery" / f"{primary_id}.yaml"
    hierarchy = report.get("hierarchy_assessment")
    hierarchy = hierarchy if isinstance(hierarchy, dict) else {}
    profile = report.get("composed_causal_profile")
    profile = profile if isinstance(profile, dict) else {}

    print("Composed story direction\n")
    print(_text(composed.get("title"), "Composed candidate"))
    print(f"\nGoverning primary: {_title(primary_path, primary_id)}")
    print("Borrowed subordinate mechanisms:")
    borrowed = report.get("borrowed")
    if isinstance(borrowed, list) and borrowed:
        for item in borrowed:
            if isinstance(item, dict):
                print(f"- {_text(item.get('candidate_id'))}: {_text(item.get('mechanism'))}")
    else:
        print("- Not recorded in the persisted evidence.")

    print("\nWhy the primary still governs")
    print(_text(hierarchy.get("rationale")))
    _render_mechanics(profile)
    risks = _items(hierarchy.get("risks"))
    if risks:
        _print_list("\nHierarchy risks:", risks)

    print("\nNothing canonical has changed.")
    print("\nYou can:")
    try:
        composed_display = state.composed_candidate_path.relative_to(root)
    except ValueError:
        composed_display = state.composed_candidate_path
    print("- Accept the composed candidate explicitly:")
    print(f"    auteur story-discovery accept {composed_display} --output story_identity.yaml")
    if primary_path.is_file():
        try:
            primary_display = primary_path.relative_to(root)
        except ValueError:
            primary_display = primary_path
        print("- Or accept the uncomposed primary:")
        print(f"    auteur story-discovery accept {primary_display} --output story_identity.yaml")
    print("- Change your declared intent:")
    print("    auteur story-discovery start --project . --edit")


def _render_unreviewable(state: StoryDiscoveryProjectState) -> int:
    messages = {
        StoryDiscoveryStateKind.NO_BRIEF: "No Story Discovery brief or recommendation is available yet.",
        StoryDiscoveryStateKind.INVALID_BRIEF: "The current Story Discovery brief is invalid.",
        StoryDiscoveryStateKind.INCOMPLETE_BRIEF: "The current Story Discovery brief is incomplete.",
        StoryDiscoveryStateKind.READY_TO_DISCOVER: "The current brief needs a fresh Story Discovery run.",
        StoryDiscoveryStateKind.DISCOVERY_INVALID: "The current Story Discovery evidence is invalid.",
    }
    message = messages.get(state.kind, "There is nothing reviewable yet.")
    print(f"Error: {message}", file=sys.stderr)
    for problem in state.problems:
        print(f"- {problem}", file=sys.stderr)
    return 1


def dispatch_story_discovery_review(args: object) -> int:
    """Render current Story Discovery evidence without mutation or provider access."""

    root = Path(getattr(args, "project", Path(".")))
    try:
        state = classify_story_discovery_project(root)
        if state.kind is StoryDiscoveryStateKind.NON_ADJUDICABLE:
            _render_non_adjudicable(root, state)
            return 0
        if state.kind is StoryDiscoveryStateKind.COMPOSED_CANDIDATE_AVAILABLE:
            _render_composed(root, state)
            return 0
        if state.kind is StoryDiscoveryStateKind.RECOMMENDATION_AVAILABLE:
            _render_recommendation(root, state)
            return 0
        return _render_unreviewable(state)
    except Exception as exc:
        print(f"Error: Could not reconstruct Story Discovery review: {exc}", file=sys.stderr)
        return 1
