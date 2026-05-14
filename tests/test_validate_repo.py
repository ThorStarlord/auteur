from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_validator_module():
    root = Path(__file__).resolve().parents[1]
    module_path = root / "scripts" / "validate_repo.py"
    assert module_path.exists(), "scripts/validate_repo.py must exist"

    spec = importlib.util.spec_from_file_location("validate_repo", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validate_repo_passes_for_current_repository() -> None:
    module = _load_validator_module()
    root = Path(__file__).resolve().parents[1]
    errors = module.validate_repo(root)
    assert errors == []


def test_validate_repo_flags_stale_readme_claim(tmp_path: Path) -> None:
    module = _load_validator_module()

    (tmp_path / "README.md").write_text(
        "The implementation is still early. It does not yet have structure generation/diagnosis CLI commands, proposal/report artifacts.",
        encoding="utf-8",
    )
    references = tmp_path / "docs" / "references"
    references.mkdir(parents=True)
    for name in ["repo-analysis-template.md", "weakness-types.md", "evidence-rules.md"]:
        (references / name).write_text("ok", encoding="utf-8")

    errors = module.validate_repo(tmp_path)
    assert any("README" in error and "stale" in error for error in errors)


def test_validate_repo_flags_missing_reference_docs(tmp_path: Path) -> None:
    module = _load_validator_module()

    (tmp_path / "README.md").write_text("clean", encoding="utf-8")
    (tmp_path / "docs" / "references").mkdir(parents=True)
    (tmp_path / "docs" / "references" / "repo-analysis-template.md").write_text("ok", encoding="utf-8")

    errors = module.validate_repo(tmp_path)
    assert any("docs/references/weakness-types.md" in error for error in errors)
    assert any("docs/references/evidence-rules.md" in error for error in errors)