from __future__ import annotations

from pathlib import Path


def _readme_text() -> str:
    return (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")


def test_readme_does_not_claim_missing_structure_cli_features() -> None:
    readme = _readme_text().lower()
    stale_fragment = "does not yet have structure generation/diagnosis cli commands, proposal/report artifacts"
    assert stale_fragment not in readme


def test_repo_sensemaker_reference_docs_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "docs" / "references" / "repo-analysis-template.md",
        root / "docs" / "references" / "weakness-types.md",
        root / "docs" / "references" / "evidence-rules.md",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    assert missing == []