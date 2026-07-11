from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auteur.identity import StoryIdentity
from auteur.series.bible import compile_series_bible
from auteur.series.compiler import compile_book_identities
from auteur.series.diagnostics import diagnose_series
from auteur.series.graph import SeriesDependencyGraph, build_dependency_graph
from auteur.series.models import SeriesIdentity
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
    try:
        return SeriesHandlerResult.success(SeriesCompileData(identities=compile_book_identities(series)))
    except Exception as exc:
        return SeriesHandlerResult.failure(f"failed to compile series: {exc}")


def handle_series_diagnose(series: SeriesIdentity) -> SeriesHandlerResult:
    diagnostics = diagnose_series(series)
    universe_diagnostics = _collect_universe_diagnostics(series)
    return SeriesHandlerResult.success(
        SeriesDiagnoseData(
            diagnostics=diagnostics,
            universe_diagnostics=universe_diagnostics,
        )
    )


def _collect_universe_diagnostics(series: SeriesIdentity) -> list:
    """Load the referenced universe (if any) and run cross-layer diagnostics.

    Returns an empty list when no universe is referenced or the universe cannot
    be loaded; a Series is valid independently of any universe reference.
    """
    path = series.universe_constraint_path
    if not path or not path.exists():
        return []
    try:
        from auteur.series.universe_integration import validate_series_against_universe
        from auteur.universe.models import UniverseIdentity

        universe = UniverseIdentity.from_yaml(path)
        return validate_series_against_universe(series, universe)
    except Exception:
        # Silently skip if universe loading fails; series can exist without universe.
        return []


def handle_series_graph(series: SeriesIdentity) -> SeriesHandlerResult:
    return SeriesHandlerResult.success(SeriesGraphData(graph=build_dependency_graph(series)))


def handle_series_bible(series: SeriesIdentity) -> SeriesHandlerResult:
    return SeriesHandlerResult.success(SeriesBibleData(bible=compile_series_bible(series)))
