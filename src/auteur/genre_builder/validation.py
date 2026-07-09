from __future__ import annotations

import re

from auteur.blueprint import LengthClass, MechanicalLoad, NarrativeRunway, ScopeComplexity
from auteur.genre_builder.models import CustomGenreContract, GenreBrief, GenreBuilderDiagnostic
from auteur.genre_builder.parser import parse_key_values


SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_]*$")
REQUIRED_SCOPE_FIELDS = {
    "minimum_viable_length": LengthClass,
    "default_length": LengthClass,
    "narrative_runway": NarrativeRunway,
    "recommended_complexity": ScopeComplexity,
    "mechanical_load": MechanicalLoad,
    "worldbuilding_load": MechanicalLoad,
    "cast_load": MechanicalLoad,
}


def validate_custom_genre_contract(
    custom: CustomGenreContract | GenreBrief,
    *,
    filename: str | None = None,
) -> list[GenreBuilderDiagnostic]:
    if isinstance(custom, GenreBrief):
        return validate_genre_brief(custom)

    diagnostics: list[GenreBuilderDiagnostic] = []
    if not SAFE_ID.fullmatch(custom.custom_genre_id):
        diagnostics.append(
            GenreBuilderDiagnostic(
                rule="genre_builder.unsafe_custom_genre_id",
                severity="error",
                message="custom_genre_id must contain only lowercase letters, numbers, and underscores.",
            )
        )
    if not custom.contract.required_tropes and not custom.contract.forbidden_mismatches:
        diagnostics.append(
            GenreBuilderDiagnostic(
                rule="genre_builder.empty_contract_constraints",
                severity="error",
                message="A custom genre contract needs required tropes or forbidden mismatches.",
            )
        )
    if not custom.contract.setup_contract.minimum_setup_beats:
        diagnostics.append(
            GenreBuilderDiagnostic(
                rule="genre_builder.empty_setup_contract",
                severity="error",
                message="A custom genre contract needs at least one setup requirement.",
            )
        )
    if filename is not None and filename != f"{custom.custom_genre_id}.yaml":
        diagnostics.append(
            GenreBuilderDiagnostic(
                rule="genre_builder.filename_mismatch",
                severity="error",
                message="Installed custom genre filename must match custom_genre_id.",
            )
        )
    return diagnostics


def validate_genre_brief(brief: GenreBrief) -> list[GenreBuilderDiagnostic]:
    diagnostics: list[GenreBuilderDiagnostic] = [
        GenreBuilderDiagnostic(
            rule="genre_builder.missing_required_section",
            severity="error",
            message=message,
        )
        for message in brief.diagnostics
    ]
    scope = parse_key_values(brief.sections.get("Scope", ""))
    for field, enum_type in REQUIRED_SCOPE_FIELDS.items():
        value = scope.get(field)
        if value is None or not value.strip():
            diagnostics.append(
                GenreBuilderDiagnostic(
                    rule="genre_builder.missing_scope_field",
                    severity="error",
                    message=f"Missing required scope field: {field}",
                )
            )
            continue
        try:
            enum_type(value)
        except ValueError:
            diagnostics.append(
                GenreBuilderDiagnostic(
                    rule="genre_builder.invalid_scope_value",
                    severity="error",
                    message=f"Invalid value for scope field {field}: {value}",
                )
            )
    return diagnostics


def has_errors(diagnostics: list[GenreBuilderDiagnostic]) -> bool:
    return any(diagnostic.severity == "error" for diagnostic in diagnostics)
