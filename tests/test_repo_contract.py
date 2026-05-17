from __future__ import annotations

from pathlib import Path


def _readme_text() -> str:
    return (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")


def test_readme_does_not_claim_missing_structure_cli_features() -> None:
    readme = _readme_text().lower()
    stale_fragment = "does not yet have structure generation/diagnosis cli commands, proposal/report artifacts"
    assert stale_fragment not in readme


