"""Optional writer-facing refinement for a Story Discovery brief."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from auteur.blueprint import EmotionalTrajectory, StoryMedium, StoryMode
from auteur.story_discovery_brief import DiscoveryBrief, assess_intent_adequacy
from auteur.story_discovery_guidance import (
    BriefLifecycleState,
    _display_brief_path,
    _render_ready_summary,
    _write_brief_atomic,
    guide_working_brief,
    inspect_working_brief,
    resolve_working_brief_path,
)
from auteur.story_discovery_intent_controls import (
    CAUSAL_ALIASES,
    CAUSAL_OPTIONS,
    COMPLEXITY_ALIASES,
    COMPLEXITY_OPTIONS,
    HIERARCHY_ALIASES,
    HIERARCHY_OPTIONS,
    MEDIUM_ALIASES,
    MODE_ALIASES,
    UNKNOWN_TOKENS,
    ask_nonempty,
    ask_optional_choice,
    emit,
    enum_options,
    normalize_choice,
    parse_list,
    reader,
    target_payload,
    update_architecture_preference,
    update_emotional_trajectory,
    update_hard_constraints,
    update_story_type,
    update_target_list,
)


def refine_working_brief(
    project_root: str | Path,
    *,
    brief_path: str | Path | None = None,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> DiscoveryBrief:
    """Optionally enrich an adequate brief without forcing new commitments."""

    root = Path(project_root)
    status = inspect_working_brief(root, brief_path)
    if status.state is BriefLifecycleState.INVALID:
        raise ValueError(f"Cannot refine invalid Story Discovery brief {status.path}: {status.error}")
    if status.brief is None:
        raise ValueError("No Story Discovery brief exists to refine. Run start first.")
    brief = status.brief
    path = status.path
    if not assess_intent_adequacy(brief).adequate:
        raise ValueError("Finish the minimum Story Discovery brief before optional refinement.")

    target = target_payload(brief)
    if "secondary_palette" not in target and "secondary" not in target:
        emit(output_fn, "What other feelings may support the primary reader experience?")
        emit(output_fn, "Enter a comma-separated palette, or 'not sure' to leave it unspecified.")
        raw = reader(input_fn)("> ").strip()
        if normalize_choice(raw) not in UNKNOWN_TOKENS:
            values = parse_list(raw)
            if values:
                brief = update_target_list(brief, "secondary_palette", "secondary", values)
                _write_brief_atomic(brief, path)

    target = target_payload(brief)
    if "avoided_experiences" not in target and "avoid" not in target:
        emit(output_fn, "Are there reader experiences you specifically want to avoid?")
        emit(output_fn, "Enter a comma-separated list, or 'not sure' to leave it unspecified.")
        raw = reader(input_fn)("> ").strip()
        if normalize_choice(raw) not in UNKNOWN_TOKENS:
            values = parse_list(raw)
            if values:
                brief = update_target_list(brief, "avoided_experiences", "avoid", values)
                _write_brief_atomic(brief, path)

    target = target_payload(brief)
    if "emotional_trajectory" not in target:
        emit(output_fn, "Do you already know the emotional trajectory? (yes / not sure)")
        answer = normalize_choice(reader(input_fn)("> "))
        if answer in {"yes", "y"}:
            # Construct the complete object before persisting, so interruption never
            # leaves a partial EmotionalTrajectory in the working brief.
            trajectory = EmotionalTrajectory(
                pattern=ask_nonempty("Pattern: ", input_fn=input_fn, output_fn=output_fn),
                start=ask_nonempty("Start: ", input_fn=input_fn, output_fn=output_fn),
                midpoint=ask_nonempty("Midpoint: ", input_fn=input_fn, output_fn=output_fn),
                ending=ask_nonempty("Ending: ", input_fn=input_fn, output_fn=output_fn),
            )
            brief = update_emotional_trajectory(brief, trajectory)
            _write_brief_atomic(brief, path)
        elif answer not in UNKNOWN_TOKENS and answer not in {"no", "n"}:
            emit(output_fn, "Leaving emotional trajectory unspecified.")

    preferences = dict(brief.declared_intent().get("architecture_preferences") or {})
    for field_name, question, why, options, aliases in (
        (
            "complexity",
            "How dense should the story's active narrative machinery feel?",
            "This is an architecture preference, not a reader-emotion target.",
            COMPLEXITY_OPTIONS,
            COMPLEXITY_ALIASES,
        ),
        (
            "causal_distribution",
            "How should meaningful causes be distributed behind major outcomes?",
            "This describes causal architecture rather than how many emotions the story contains.",
            CAUSAL_OPTIONS,
            CAUSAL_ALIASES,
        ),
        (
            "engine_hierarchy",
            "How should multiple narrative engines relate to one another?",
            "This says whether one engine must dominate or several may carry comparable weight.",
            HIERARCHY_OPTIONS,
            HIERARCHY_ALIASES,
        ),
    ):
        if field_name in preferences:
            continue
        value = ask_optional_choice(
            question,
            why,
            options,
            aliases,
            input_fn=input_fn,
            output_fn=output_fn,
        )
        if value is not None:
            brief = update_architecture_preference(brief, field_name, value)
            _write_brief_atomic(brief, path)
            preferences = dict(brief.declared_intent().get("architecture_preferences") or {})

    story_type = dict(brief.declared_intent().get("story_type") or {})
    for field_name, enum_type, aliases, question, why in (
        (
            "medium",
            StoryMedium,
            MEDIUM_ALIASES,
            "Do you already know the medium?",
            "Medium can constrain pacing and delivery, but it is optional at this stage.",
        ),
        (
            "mode",
            StoryMode,
            MODE_ALIASES,
            "Do you already know the story mode?",
            "Mode is optional tonal/structural intent; leaving it unknown keeps the search open.",
        ),
    ):
        if field_name in story_type:
            continue
        value = ask_optional_choice(
            question,
            why,
            enum_options(enum_type),
            aliases,
            input_fn=input_fn,
            output_fn=output_fn,
        )
        if value is not None:
            brief = update_story_type(brief, field_name, value)
            _write_brief_atomic(brief, path)
            story_type = dict(brief.declared_intent().get("story_type") or {})

    if "hard_constraints" not in brief.declared_intent():
        emit(output_fn, "Any hard constraints Auteur must not violate?")
        emit(output_fn, "Enter one literal constraint at a time; blank or 'not sure' leaves this unspecified.")
        first = reader(input_fn)("> ").strip()
        if normalize_choice(first) not in UNKNOWN_TOKENS:
            constraints = [first]
            while True:
                nxt = reader(input_fn)("Another constraint (blank to finish): ").strip()
                if not nxt:
                    break
                constraints.append(nxt)
            brief = update_hard_constraints(brief, constraints)
            _write_brief_atomic(brief, path)

    return brief


def _render_incomplete_summary(project_root: Path, path: Path, brief: DiscoveryBrief) -> None:
    adequacy = assess_intent_adequacy(brief)
    labels = {
        "story_type.genre": "story kind / reader promise",
        "story_type.target_audience": "target audience",
        "target_experience": "primary reader experience",
    }
    print("Your Story Discovery brief was saved, but it is not ready for intent-aware recommendation.\n")
    print("Still needed: " + ", ".join(labels.get(item, item) for item in adequacy.missing))
    print("\nNothing canonical has changed. Any prior intent-aware result should be treated as stale.\n")
    print("Continue:")
    display_path = _display_brief_path(project_root, path)
    print(f"  auteur story-discovery start --project . --brief {display_path}")


def _render_summary(project_root: Path, path: Path, brief: DiscoveryBrief) -> None:
    if assess_intent_adequacy(brief).adequate:
        _render_ready_summary(project_root, path, brief)
    else:
        _render_incomplete_summary(project_root, path, brief)


def dispatch_story_discovery_refinement(args: object) -> int:
    """Dispatch ``start --refine`` or ``start --edit`` without constructing a provider."""

    project_root = Path(getattr(args, "project", Path(".")))
    brief_arg = getattr(args, "brief", None)
    path = resolve_working_brief_path(project_root, brief_arg)
    refine = bool(getattr(args, "refine", False))
    edit = bool(getattr(args, "edit", False))
    premise = getattr(args, "premise", None)

    if edit and premise is not None:
        print(
            "Error: --premise cannot be combined with --edit; edit the premise through the guided edit menu.",
            file=sys.stderr,
        )
        return 2
    if not refine and not edit:
        raise ValueError("G1b refinement dispatch requires --refine or --edit")

    try:
        if edit:
            from auteur.story_discovery_edit import edit_working_brief

            brief = edit_working_brief(project_root, brief_path=brief_arg)
        else:
            # Refinement remains optional: first reach the existing minimum if needed,
            # then ask only for richer fields that are still genuinely unspecified.
            guide_working_brief(project_root, brief_path=brief_arg, premise=premise)
            brief = refine_working_brief(project_root, brief_path=brief_arg)
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        status = inspect_working_brief(project_root, brief_arg)
        if status.brief is not None:
            print("Your Story Discovery brief has been saved through the last complete answer.", file=sys.stderr)
            suffix = "--edit" if edit else "--refine"
            print("Run the same mode to continue:", file=sys.stderr)
            print(f"  auteur story-discovery start --project . {suffix}", file=sys.stderr)
        else:
            print("No Story Discovery answer was saved.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    _render_summary(project_root, path, brief)
    return 0
