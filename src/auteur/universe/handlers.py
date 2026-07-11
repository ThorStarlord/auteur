from __future__ import annotations

from pathlib import Path
from typing import Generic, NamedTuple, Optional, TypeVar

from auteur.universe.models import UniverseIdentity
from auteur.universe.validation import validate_universe_identity


T = TypeVar("T")


class Result(NamedTuple, Generic[T]):
    is_success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    exit_code: int = 0


def handle_universe_validate(path: Path) -> Result[None]:
    """Validate a universe_identity.yaml file.

    Returns Result with is_success=True if no errors, False otherwise.
    """
    try:
        universe = UniverseIdentity.from_yaml(path)
    except FileNotFoundError:
        return Result(is_success=False, error=f"File not found: {path}", exit_code=1)
    except Exception as exc:
        return Result(is_success=False, error=f"Failed to load universe: {exc}", exit_code=1)

    diagnostics = validate_universe_identity(universe)
    errors = [d for d in diagnostics if d.severity.value == "error"]

    if errors:
        error_msg = "\n".join(f"  {d.rule}: {d.message}" for d in errors)
        return Result(is_success=False, error=error_msg, exit_code=1)

    return Result(is_success=True, exit_code=0)


def handle_universe_diagnose(path: Path) -> Result[str]:
    """Run diagnostics on a universe_identity.yaml file.

    Returns Result with diagnostic report as string.
    """
    try:
        universe = UniverseIdentity.from_yaml(path)
    except FileNotFoundError:
        return Result(is_success=False, error=f"File not found: {path}", exit_code=1)
    except Exception as exc:
        return Result(is_success=False, error=f"Failed to load universe: {exc}", exit_code=1)

    diagnostics = validate_universe_identity(universe)

    report_lines = [
        f"# Universe Diagnostics: {universe.name}",
        "",
        f"**Slug:** {universe.slug}",
        f"**Description:** {universe.description or '(none)'}",
        "",
        "## Validation Results",
        "",
    ]

    if not diagnostics:
        report_lines.append("[OK] No diagnostics found. Universe is well-formed.")
    else:
        for diagnostic in diagnostics:
            icon = "[ERROR]" if diagnostic.severity.value == "error" else ("[WARN]" if diagnostic.severity.value == "warning" else "[INFO]")
            report_lines.append(f"{icon} **{diagnostic.rule}** ({diagnostic.severity.value})")
            report_lines.append(f"   {diagnostic.message}")
            report_lines.append("")

    report_lines.append("## Universe Profile")
    report_lines.append(f"- **Setting Type:** {universe.setting_profile.setting_type}")
    report_lines.append(f"- **Primary Location:** {universe.setting_profile.primary_location}")
    report_lines.append(f"- **Magic System:** {universe.magic_system or '(none)'}")
    report_lines.append(f"- **Core Mythology:** {universe.core_mythology or '(none)'}")
    report_lines.append(f"- **Timeline:** {universe.timeline.current_era} ({universe.timeline.years_of_history} years of history)")
    report_lines.append(f"- **Forbidden Elements:** {', '.join(universe.forbidden_elements) or '(none)'}")
    report_lines.append(f"- **Required Elements:** {', '.join(universe.required_elements) or '(none)'}")
    report_lines.append(f"- **Cross-Story Constraints:** {len(universe.cross_story_constraints)} defined")

    return Result(is_success=True, data="\n".join(report_lines), exit_code=0)
