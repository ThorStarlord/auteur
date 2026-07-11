from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from auteur.universe.models import UniverseIdentity


class DiagnosticSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationDiagnostic(BaseModel):
    rule: str
    message: str
    severity: DiagnosticSeverity


def validate_universe_identity(universe: UniverseIdentity) -> list[ValidationDiagnostic]:
    """Validate a UniverseIdentity against domain rules.

    Returns list of diagnostics ordered by severity (error, warning, info).
    """
    diagnostics: list[ValidationDiagnostic] = []

    # Rule: universe.empty_forbidden_and_required
    if not universe.forbidden_elements and not universe.required_elements:
        diagnostics.append(
            ValidationDiagnostic(
                rule="universe.empty_forbidden_and_required",
                message="Universe should define at least one forbidden element or required element to establish world rules.",
                severity=DiagnosticSeverity.WARNING,
            )
        )

    # Rule: universe.setting_and_mythology_coherence
    has_magic = universe.magic_system and len(universe.magic_system.strip()) > 0
    has_mythology = universe.core_mythology and len(universe.core_mythology.strip()) > 0
    if has_magic and not has_mythology:
        diagnostics.append(
            ValidationDiagnostic(
                rule="universe.setting_and_mythology_coherence",
                message="Universe has a magic system but no core mythology. Consider adding lore to explain the origin/nature of magic.",
                severity=DiagnosticSeverity.WARNING,
            )
        )

    # Rule: universe.constraint_severity_balance
    if universe.cross_story_constraints:
        severities = [c.severity for c in universe.cross_story_constraints]
        if all(s == "required" for s in severities):
            diagnostics.append(
                ValidationDiagnostic(
                    rule="universe.constraint_severity_balance",
                    message=f"All {len(universe.cross_story_constraints)} cross-story constraints are 'required'. Consider marking some as 'warning' to allow author flexibility.",
                    severity=DiagnosticSeverity.INFO,
                )
            )

    # Rule: universe.worldbuilding_scope_specificity
    scope = universe.setting_profile.worldbuilding_scope or ""
    if scope.lower() in ["unknown", "other", "varied", ""]:
        diagnostics.append(
            ValidationDiagnostic(
                rule="universe.worldbuilding_scope_specificity",
                message="Setting scope is vague. Consider setting to: 'single_location', 'local', 'regional', 'wide', or 'multi_world'.",
                severity=DiagnosticSeverity.INFO,
            )
        )

    # Sort by severity (error, warning, info)
    severity_order = {"error": 0, "warning": 1, "info": 2}
    diagnostics.sort(key=lambda d: severity_order[d.severity.value])

    return diagnostics
