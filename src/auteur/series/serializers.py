from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from auteur.series.handlers import (
    SeriesBibleData,
    SeriesCompileData,
    SeriesDiagnoseData,
    SeriesGraphData,
    SeriesHandlerResult,
)


def serialize_series_compile(result: SeriesHandlerResult, output_dir: Path) -> list[Path]:
    if not result.is_success or result.data is None:
        return []
    data: SeriesCompileData = result.data
    written: list[Path] = []
    for index, identity in enumerate(data.identities, start=1):
        book_dir = output_dir / f"book_{index:02d}"
        book_dir.mkdir(parents=True, exist_ok=True)
        path = book_dir / "story_identity.yaml"
        identity.to_yaml(path)
        written.append(path)
    return written


def serialize_series_diagnostics(result: SeriesHandlerResult, output_path: Path) -> Path:
    data: SeriesDiagnoseData = result.data
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps({"diagnostics": [d.model_dump(mode="json") for d in data.diagnostics]}, indent=2),
        encoding="utf-8",
    )
    return output_path


def serialize_series_graph(result: SeriesHandlerResult, output_path: Path) -> Path:
    data: SeriesGraphData = result.data
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(data.graph.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    mermaid_path = output_path.with_suffix(".mmd")
    def mermaid_id(value: str) -> str:
        sanitized = re.sub(r"[^A-Za-z0-9_]", "_", value)
        return sanitized or "node"

    def mermaid_label(value: str) -> str:
        return value.replace('"', "'").replace("[", "(").replace("]", ")").replace("|", "/").replace("\n", " ")

    lines = ["graph LR"]
    for node in data.graph.nodes:
        lines.append(f'    {mermaid_id(node.id)}["{mermaid_label(node.label)}"]')
    for edge in data.graph.edges:
        lines.append(f"    {mermaid_id(edge.source)} -->|{mermaid_label(edge.type.value)}| {mermaid_id(edge.target)}")
    mermaid_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def serialize_series_bible(result: SeriesHandlerResult, output_path: Path) -> Path:
    data: SeriesBibleData = result.data
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data.bible, indent=2), encoding="utf-8")
    return output_path
