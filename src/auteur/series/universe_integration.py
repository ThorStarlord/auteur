from __future__ import annotations

from typing import TYPE_CHECKING

from auteur.universe.validation import ValidationDiagnostic

if TYPE_CHECKING:
    from auteur.series.models import SeriesIdentity
    from auteur.universe.models import UniverseIdentity


def validate_series_against_universe(
    series: SeriesIdentity, universe: UniverseIdentity
) -> list[ValidationDiagnostic]:
    """Validate that a Series respects its Universe constraints.

    This is a placeholder for cross-layer validation. Future expansions:
    - Check that Series title/description don't contradict the universe.
    - Validate book identities against universe forbidden/required elements.
    - Check that series themes align with universe mythology.

    For now this always passes: universe constraints are treated as guidelines,
    not strict rules, so a Series can reference a Universe without triggering
    errors until concrete cross-layer rules are implemented.
    """
    diagnostics: list[ValidationDiagnostic] = []

    # Future rule: series.universe_compatibility
    # If a series violates universe forbidden elements, append a diagnostic here.

    return diagnostics
