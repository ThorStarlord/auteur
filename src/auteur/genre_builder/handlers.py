from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from auteur.genre_builder.builder import build_custom_genre_contract
from auteur.genre_builder.explainer import explain_custom_genre_contract
from auteur.genre_builder.models import CustomGenreContract
from auteur.genre_builder.parser import parse_genre_brief
from auteur.genre_builder.serializers import load_custom_genre_contract
from auteur.genre_builder.validation import has_errors, validate_custom_genre_contract


@dataclass(frozen=True)
class GenreBuilderResult:
    is_success: bool
    exit_code: int = 0
    error: str | None = None
    data: object | None = None


def handle_genre_build(brief_path: Path) -> GenreBuilderResult:
    try:
        brief = parse_genre_brief(brief_path.read_text(encoding="utf-8"))
        if brief.diagnostics:
            return GenreBuilderResult(False, 1, "; ".join(brief.diagnostics))
        custom = build_custom_genre_contract(brief)
        diagnostics = validate_custom_genre_contract(custom)
        if has_errors(diagnostics):
            return GenreBuilderResult(False, 1, diagnostics[0].message, diagnostics)
        return GenreBuilderResult(True, data=custom)
    except Exception as exc:
        return GenreBuilderResult(False, 1, str(exc))


def handle_genre_validate(contract_path: Path) -> GenreBuilderResult:
    try:
        custom = load_custom_genre_contract(contract_path)
        diagnostics = validate_custom_genre_contract(custom, filename=contract_path.name)
        return GenreBuilderResult(not has_errors(diagnostics), 1 if has_errors(diagnostics) else 0, data=diagnostics)
    except Exception as exc:
        return GenreBuilderResult(False, 1, str(exc))


def handle_genre_explain(contract_path: Path) -> GenreBuilderResult:
    try:
        custom = load_custom_genre_contract(contract_path)
        return GenreBuilderResult(True, data=explain_custom_genre_contract(custom))
    except Exception as exc:
        return GenreBuilderResult(False, 1, str(exc))


def handle_genre_install(contract_path: Path) -> GenreBuilderResult:
    try:
        custom = load_custom_genre_contract(contract_path)
        diagnostics = validate_custom_genre_contract(custom)
        if has_errors(diagnostics):
            return GenreBuilderResult(False, 1, diagnostics[0].message, diagnostics)
        return GenreBuilderResult(True, data=custom)
    except Exception as exc:
        return GenreBuilderResult(False, 1, str(exc))


def list_custom_genres(project: Path) -> list[str]:
    custom_dir = project / "genres" / "custom"
    if not custom_dir.exists():
        return []
    return sorted(path.stem for path in custom_dir.glob("*.yaml"))

