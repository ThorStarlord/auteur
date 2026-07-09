from __future__ import annotations

import re

from auteur.genre_builder.models import CustomGenreContract, GenreBuilderDiagnostic


SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9_]*$")


def validate_custom_genre_contract(custom: CustomGenreContract, *, filename: str | None = None) -> list[GenreBuilderDiagnostic]:
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


def has_errors(diagnostics: list[GenreBuilderDiagnostic]) -> bool:
    return any(diagnostic.severity == "error" for diagnostic in diagnostics)

