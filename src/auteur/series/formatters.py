from __future__ import annotations


def format_series_validate_success(series_path: str) -> str:
    return f"Success: SeriesIdentity {series_path} is valid."


def format_series_compile_success(count: int, output_dir: str) -> str:
    return f"Success: compiled {count} book identities to {output_dir}"


def format_series_diagnostics_success(output_path: str) -> str:
    return f"Series diagnostics written to {output_path}"


def format_series_graph_success(output_path: str) -> str:
    return f"Series dependency graph written to {output_path}"


def format_series_bible_success(output_path: str) -> str:
    return f"Series bible written to {output_path}"
