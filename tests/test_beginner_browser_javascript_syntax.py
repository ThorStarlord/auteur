from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


APP = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "auteur"
    / "beginner"
    / "browser"
    / "app.js"
)


def test_beginner_browser_javascript_parses() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is unavailable; static browser contract tests still run")
    result = subprocess.run(
        [node, "--check", str(APP)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
