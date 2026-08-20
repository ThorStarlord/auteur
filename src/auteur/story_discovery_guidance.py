"""Deterministic writer-facing guidance for Story Discovery briefs.

This is a UX adapter over the existing DiscoveryBrief contract. It never
constructs an LLM client, never invents omitted intent, and never promotes
canonical StoryIdentity state.
"""

from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

import yaml

from auteur.blueprint import Genre, TargetAudience
from auteur.story_discovery_brief import DiscoveryBrief, IntentAdequacy, assess_intent_adequacy


DEFAULT_BRIEF_RELATIVE_PATH = Path("story_discovery/brief.yaml")


class BriefLifecycleState(str, Enum):
    ABSENT = "absent"
    INVALID = "invalid"
    INCOMPLETE = "incomplete"
    ADEQUATE = "adequate"


@dataclass(frozen=True)
class WorkingBriefStatus:
    state: BriefLifecycleState
    path: Path
    brief: DiscoveryBrief | None = None
    adequacy: IntentAdequacy | None = None
    error: str | None = None


def resolve_working_brief_path(
    project_root: str | Path,
    brief_path: str | Path | None = None,
) -> Path:
    root = Path(project_root)
    if brief_path is None:
        return root / DEFAULT_BRIEF_RELATIVE_PATH
    path = Path(brief_path)
    return path if path.is_absolute() else root / path


def inspect_working_brief(
    project_root: str | Path,
    brief_path: str | Path | None = None,
) -> WorkingBriefStatus:
    """Classify the visible working brief without mutating project state."""

    path = resolve_working_brief_path(project_root, brief_path)
    if not path.exists():
        return WorkingBriefStatus(BriefLifecycleState.ABSENT, path)
    if not path.is_file():
        return WorkingBriefStatus(
            BriefLifecycleState.INVALID,
            path,
            error="working brief path is not a file",
        )
    try:
        brief = DiscoveryBrief.from_yaml(path)
    except Exception as exc:
        return WorkingBriefStatus(BriefLifecycleState.INVALID, path, error=str(exc))

    adequacy = assess_intent_adequacy(brief)
    state = BriefLifecycleState.ADEQUATE if adequacy.adequate else BriefLifecycleState.INCOMPLETE
    return WorkingBriefStatus(state, path, brief=brief, adequacy=adequacy)


def intent_aware_run_matches_brief(project_root: str | Path, brief: DiscoveryBrief) -> bool:
    """Return whether persisted intent-aware evidence matches current declared intent."""

    path = Path(project_root) / "story_discovery" / "discovery_set.yaml"
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return False
    return (
        isinstance(payload, dict)
        and payload.get("intent_mode") == "intent_aware"
        and payload.get("declared_author_intent") == brief.declared_intent()
    )


def _write_brief_atomic(brief: DiscoveryBrief, path: Path) -> None:
    """Persist explicit declared intent only, replacing the file atomically."""

    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(brief.declared_intent(), sort_keys=False, allow_unicode=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(rendered)
            temp_path = Path(handle.name)
        temp_path.replace(path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def _emit(output_fn: Callable[[str], None] | None, text: str = "") -> None:
    (print if output_fn is None else output_fn)(text)


def _ask_nonempty(
    prompt: str,
    *,
    input_fn: Callable[[str], str] | None,
    output_fn: Callable[[str], None] | None,
) -> str:
    reader = input if input_fn is None else input_fn
    while True:
        value = reader(prompt).strip()
        if value:
            return value
        _emit(output_fn, "Please give me a concrete answer, or interrupt and resume later.")


def _choice_aliases(enum_type: type[Enum]) -> dict[str, Enum]:
    aliases: dict[str, Enum] = {}
    for member in enum_type:
        value = str(member.value)
        aliases[value.casefold()] = member
        aliases[value.replace("_", " ").casefold()] = member
        aliases[value.replace("_", "-").casefold()] = member
    return aliases


_GENRE_ALIASES = _choice_aliases(Genre)
_GENRE_ALIASES.update(
    {
        "science fiction": Genre.SCI_FI,
        "sci fi": Genre.SCI_FI,
        "sci-fi": Genre.SCI_FI,
        "scifi": Genre.SCI_FI,
    }
)
_AUDIENCE_ALIASES = _choice_aliases(TargetAudience)


def _ask_enum_choice(
    question: str,
    why: str,
    enum_type: type[Enum],
    aliases: dict[str, Enum],
    *,
    input_fn: Callable[[str], str] | None,
    output_fn: Callable[[str], None] | None,
) -> Enum:
    _emit(output_fn, question)
    _emit(output_fn, f"Why this matters: {why}")
    _emit(output_fn, "Choices: " + ", ".join(str(v.value).replace("_", " ") for v in enum_type))
    reader = input if input_fn is None else input_fn
    while True:
        match = aliases.get(reader("> ").strip().casefold())
        if match is not None:
            return match
        _emit(output_fn, "I didn't recognize that choice. Use one of the listed options.")


def _resolve_premise_seed(raw: str, project_root: Path) -> str:
    try:
        supplied = Path(raw)
        candidates = [supplied] if supplied.is_absolute() else [supplied, project_root / supplied]
    except (OSError, ValueError):
        return raw.strip()
    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8").strip()
        except OSError:
            continue
    return raw.strip()


def _update_story_type(brief: DiscoveryBrief, field_name: str, value: Enum) -> DiscoveryBrief:
    payload = brief.declared_intent()
    story_type = dict(payload.get("story_type") or {})
    story_type[field_name] = value.value
    payload["story_type"] = story_type
    return DiscoveryBrief.model_validate(payload)


def _update_target_experience(brief: DiscoveryBrief, primary: str) -> DiscoveryBrief:
    payload = brief.declared_intent()
    payload["target_experience"] = {"primary_emotional_promise": primary}
    return DiscoveryBrief.model_validate(payload)


def guide_working_brief(
    project_root: str | Path,
    *,
    brief_path: str | Path | None = None,
    premise: str | None = None,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> DiscoveryBrief:
    """Create or resume the minimum F2-adequate brief from explicit answers only."""

    root = Path(project_root)
    status = inspect_working_brief(root, brief_path)
    path = status.path
    if status.state is BriefLifecycleState.INVALID:
        raise ValueError(
            f"Cannot safely resume invalid Story Discovery brief {path}: {status.error}. "
            "Auteur will not overwrite or guess missing intent. Repair or move the file, "
            "then run start again."
        )

    if status.state is BriefLifecycleState.ABSENT:
        if premise is None:
            _emit(output_fn, "Tell me the story you think you want to write.")
            premise_text = _ask_nonempty("> ", input_fn=input_fn, output_fn=output_fn)
        else:
            premise_text = _resolve_premise_seed(premise, root)
            if not premise_text:
                raise ValueError("--premise resolved to empty text")
        brief = DiscoveryBrief(premise=premise_text)
        _write_brief_atomic(brief, path)
    else:
        assert status.brief is not None
        brief = status.brief
        if premise is not None and _resolve_premise_seed(premise, root) != brief.premise:
            raise ValueError(
                "A working Story Discovery brief already exists. G1a will not silently replace "
                "its premise; resume it without --premise."
            )

    while True:
        adequacy = assess_intent_adequacy(brief)
        if adequacy.adequate:
            return brief
        if "story_type.genre" in adequacy.missing:
            genre = _ask_enum_choice(
                "What kind of story should this fundamentally be for the reader?",
                "This gives Auteur the reader promise the alternatives must serve.",
                Genre,
                _GENRE_ALIASES,
                input_fn=input_fn,
                output_fn=output_fn,
            )
            brief = _update_story_type(brief, "genre", genre)
        elif "story_type.target_audience" in adequacy.missing:
            audience = _ask_enum_choice(
                "Who do you imagine reading this?",
                "The same premise can support different intensity, complexity, and conventions depending on who it is for.",
                TargetAudience,
                _AUDIENCE_ALIASES,
                input_fn=input_fn,
                output_fn=output_fn,
            )
            brief = _update_story_type(brief, "target_audience", audience)
        elif "target_experience" in adequacy.missing:
            _emit(output_fn, "What should the story primarily make them experience?")
            _emit(
                output_fn,
                "Why this matters: Without a governing reader experience, Auteur can show you different stories this premise could become, but it cannot honestly say which one best serves the story you want.",
            )
            primary = _ask_nonempty("> ", input_fn=input_fn, output_fn=output_fn)
            brief = _update_target_experience(brief, primary)
        else:
            raise RuntimeError(
                "DiscoveryBrief adequacy reported unsupported missing fields: "
                + ", ".join(adequacy.missing)
            )
        _write_brief_atomic(brief, path)


def print_inadequate_brief_recovery(adequacy: IntentAdequacy) -> None:
    """Render writer-facing recovery while retaining machine paths for diagnostics."""

    labels = {
        "story_type.genre": "What kind of story / reader promise this fundamentally is",
        "story_type.target_audience": "Who the story is primarily for",
        "target_experience": "What the story should primarily make the reader experience",
    }
    print(
        "Error: I can explore possibilities from this premise, but I do not yet know enough "
        "to honestly recommend which direction best serves the story you want.",
        file=sys.stderr,
    )
    print("\nStill needed:", file=sys.stderr)
    for field in adequacy.missing:
        print(f"- {labels.get(field, field)}", file=sys.stderr)
    print("\nContinue the brief:", file=sys.stderr)
    print("  auteur story-discovery start --project .", file=sys.stderr)
    print(
        "\nOr run raw-premise Story Discovery if you only want exploratory possibilities.",
        file=sys.stderr,
    )
    print("\nMissing machine fields: " + ", ".join(adequacy.missing), file=sys.stderr)


def _display_brief_path(project_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _render_ready_summary(project_root: Path, path: Path, brief: DiscoveryBrief) -> None:
    story_type = brief.story_type
    assert story_type is not None and story_type.genre is not None
    assert story_type.target_audience is not None and brief.target_experience is not None
    display_path = _display_brief_path(project_root, path)
    print("Your Story Discovery brief is ready for an intent-aware search.\n")
    print(f"Premise: {brief.premise}")
    print(f"Genre: {story_type.genre.value}")
    print(f"Audience: {story_type.target_audience.value}")
    print(f"Primary reader experience: {brief.target_experience.primary}")
    print(
        "Optional architecture preferences: "
        + ("not specified" if brief.architecture_preferences is None else "specified")
    )
    print(
        "Hard constraints: "
        + ("none declared" if not brief.hard_constraints else f"{len(brief.hard_constraints)} declared")
    )
    print("\nNothing canonical has changed.\n")
    print("Next:")
    print(
        "  auteur story-discovery run "
        f"--brief {display_path} --recommend --output story_discovery --project ."
    )


def dispatch_story_discovery_start(args: object) -> int:
    project_root = Path(getattr(args, "project", Path(".")))
    brief_arg = getattr(args, "brief", None)
    path = resolve_working_brief_path(project_root, brief_arg)
    try:
        brief = guide_working_brief(
            project_root,
            brief_path=brief_arg,
            premise=getattr(args, "premise", None),
        )
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        status = inspect_working_brief(project_root, brief_arg)
        if status.brief is not None:
            print("Your Story Discovery brief has been saved.", file=sys.stderr)
            print("Run the same command to continue:", file=sys.stderr)
            print("  auteur story-discovery start --project .", file=sys.stderr)
        else:
            print("No Story Discovery answer was saved.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    _render_ready_summary(project_root, path, brief)
    return 0
