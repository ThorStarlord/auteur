from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _readme_text() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_does_not_claim_missing_structure_cli_features() -> None:
    readme = _readme_text().lower()
    stale_fragment = "does not yet have structure generation/diagnosis cli commands, proposal/report artifacts"
    assert stale_fragment not in readme


def test_repo_has_pytest_config() -> None:
    """Check that pyproject.toml has a [tool.pytest.ini_options] section."""
    pyproject = ROOT / "pyproject.toml"
    raw = pyproject.read_bytes()
    data = tomllib.loads(raw.decode("utf-8"))
    assert "tool" in data, "pyproject.toml must have a [tool] section"
    assert "pytest" in data["tool"], (
        "pyproject.toml must have [tool.pytest] section with ini_options"
    )
    ini_opts = data["tool"]["pytest"].get("ini_options", {})
    addopts = ini_opts.get("addopts", "")
    assert "-q" in addopts, "ini_options.addopts should include quiet mode (-q)"
    assert "--tb=no" in addopts, "ini_options.addopts should suppress tracebacks (--tb=no)"
