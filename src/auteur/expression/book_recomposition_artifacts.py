"""Storage seam for derived Book recomposition and comparison artifacts.

This module owns only deterministic persistence mechanics for Phase C1/C2
derived evidence: recomposition/comparison paths, atomic writes, and loads.
Recomposition assembly, freshness validation, comparison ownership reasoning,
readiness semantics, and every authority-bearing action remain owned by
`BookReconciliationStore`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class BookRecompositionArtifactStore:
    """Persist derived recomposition and comparison evidence."""

    def __init__(self, project: Path) -> None:
        self.project = Path(project)
        self.root = self.project / "book" / "expression" / "reconciliation"

    def recompositions_dir(self) -> Path:
        return self.root / "recompositions"

    def recomposition_path(self, publication_id: str) -> Path:
        return self.recompositions_dir() / f"{publication_id}_recomposed.yaml"

    def store_recomposed_book(self, recomposed: dict[str, Any]) -> Path:
        path = self.recomposition_path(recomposed["publication_id"])
        self._atomic_yaml_write(path, recomposed)
        return path

    def load_recomposed_book(self, publication_id: str) -> dict[str, Any]:
        path = self.recomposition_path(publication_id)
        if not path.exists():
            raise FileNotFoundError(f"Book recomposition not found: {publication_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def comparisons_dir(self) -> Path:
        return self.root / "comparisons"

    def comparison_path(self, comparison_id: str) -> Path:
        return self.comparisons_dir() / f"{comparison_id}.yaml"

    def store_comparison_report(self, report: dict[str, Any]) -> Path:
        path = self.comparison_path(report["comparison_id"])
        self._atomic_yaml_write(path, report)
        return path

    def load_book_comparison(self, comparison_id: str) -> dict[str, Any]:
        path = self.comparison_path(comparison_id)
        if not path.exists():
            raise FileNotFoundError(f"Book comparison not found: {comparison_id}")
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    @staticmethod
    def _atomic_yaml_write(path: Path, artifact: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".yaml.tmp")
        try:
            tmp.write_text(
                yaml.safe_dump(artifact, sort_keys=False),
                encoding="utf-8",
            )
            tmp.replace(path)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise
