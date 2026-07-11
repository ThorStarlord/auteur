from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from auteur.identity import StoryIdentity
from auteur.series.bible import compile_series_bible
from auteur.series.compiler import compile_book_identities
from auteur.series.diagnostics import diagnose_series
from auteur.series.graph import SeriesDependencyGraph, build_dependency_graph
from auteur.series.models import SeriesIdentity
from auteur.series.continuity_validators import (
    ThematicProgressionValidator,
    CharacterContinuityValidator,
    RelationshipContinuityValidator,
    LoreConsistencyValidator,
    ChronologyValidator,
    SetupPayoffValidator,
)
from auteur.structure.diagnostics import StructureDiagnostic


@dataclass
class SeriesHandlerResult:
    exit_code: int = 0
    data: Any = None
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0

    @classmethod
    def success(cls, data: Any = None) -> "SeriesHandlerResult":
        return cls(data=data)

    @classmethod
    def failure(cls, message: str, exit_code: int = 1) -> "SeriesHandlerResult":
        return cls(exit_code=exit_code, error=message)


@dataclass
class SeriesValidateData:
    series: SeriesIdentity


@dataclass
class SeriesCompileData:
    identities: list[StoryIdentity]


@dataclass
class SeriesDiagnoseData:
    diagnostics: list[StructureDiagnostic]
    universe_diagnostics: list = field(default_factory=list)


@dataclass
class SeriesGraphData:
    graph: SeriesDependencyGraph


@dataclass
class SeriesBibleData:
    bible: dict


def handle_series_validate(series: SeriesIdentity) -> SeriesHandlerResult:
    return SeriesHandlerResult.success(SeriesValidateData(series=series))


def handle_series_compile(series: SeriesIdentity) -> SeriesHandlerResult:
    # Check for blocking diagnostics before compilation
    from auteur.structure.diagnostics import Severity

    continuity_diags = _collect_continuity_diagnostics(series)
    universe_diags = _collect_universe_diagnostics(series)

    errors = [d for d in continuity_diags + universe_diags if d.severity == Severity.ERROR]
    if errors:
        error_msgs = "\n".join([f"  - {d.id}: {d.description}" for d in errors])
        return SeriesHandlerResult.failure(f"Cannot compile series due to errors:\n{error_msgs}")

    try:
        return SeriesHandlerResult.success(SeriesCompileData(identities=compile_book_identities(series)))
    except Exception as exc:
        return SeriesHandlerResult.failure(f"failed to compile series: {exc}")


def handle_series_diagnose(series: SeriesIdentity) -> SeriesHandlerResult:
    diagnostics = diagnose_series(series)

    # Add Group 3 continuity diagnostics
    continuity_diagnostics = _collect_continuity_diagnostics(series)

    universe_diagnostics = _collect_universe_diagnostics(series)

    all_diagnostics = diagnostics + continuity_diagnostics + universe_diagnostics

    return SeriesHandlerResult.success(
        SeriesDiagnoseData(
            diagnostics=all_diagnostics,
            universe_diagnostics=universe_diagnostics,
        )
    )


def _collect_continuity_diagnostics(series: SeriesIdentity) -> list:
    """Run Group 3 continuity validators and convert diagnostics to StructureDiagnostic format."""
    continuity_diags = []

    continuity_diags.extend(ThematicProgressionValidator().validate(series))
    continuity_diags.extend(CharacterContinuityValidator().validate(series))
    continuity_diags.extend(RelationshipContinuityValidator().validate(series))
    continuity_diags.extend(LoreConsistencyValidator().validate(series))
    continuity_diags.extend(ChronologyValidator().validate(series))
    continuity_diags.extend(SetupPayoffValidator().validate(series))

    # Convert continuity diagnostics to StructureDiagnostic format for compatibility
    from auteur.structure.diagnostics import Severity

    structure_diags = []
    severity_map = {"ERROR": Severity.ERROR, "WARNING": Severity.WARNING, "INFO": Severity.INFO}

    for diag in continuity_diags:
        severity = severity_map.get(diag.severity, Severity.WARNING)
        struct_diag = StructureDiagnostic(
            id=diag.id,
            severity=severity,
            description=diag.explanation,
            affected_section=diag.conflict_source,
            repair_suggestion=diag.explanation,
        )
        structure_diags.append(struct_diag)

    return structure_diags


def _collect_universe_diagnostics(series: SeriesIdentity) -> list:
    """Load the referenced universe (if any) and run cross-layer diagnostics.

    Returns an empty list when no universe is referenced or the universe cannot
    be loaded; a Series is valid independently of any universe reference.
    """
    universe_contract = series.universe_contract
    if not universe_contract:
        return []

    contract_path = Path(universe_contract)
    if not contract_path.exists():
        return []

    try:
        from auteur.series.universe_integration import validate_series_against_universe
        from auteur.universe.models import UniverseIdentity

        universe = UniverseIdentity.from_yaml(contract_path)
        return validate_series_against_universe(series, universe)
    except Exception:
        # Silently skip if universe loading fails; series can exist without universe.
        return []


def handle_series_graph(series: SeriesIdentity) -> SeriesHandlerResult:
    return SeriesHandlerResult.success(SeriesGraphData(graph=build_dependency_graph(series)))


def handle_series_bible(series: SeriesIdentity) -> SeriesHandlerResult:
    return SeriesHandlerResult.success(SeriesBibleData(bible=compile_series_bible(series)))
