"""Runs the node unit tests for the Atelier's open-question helpers, and checks that the edited browser scripts parse.

The helpers are pure (no DOM), so their statements are tested directly in node; skipped where node is unavailable.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BROWSER = REPO / "src" / "auteur" / "beginner" / "browser"


def _node() -> str:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is unavailable; the pure helper statements are not run here")
    return node


def test_the_open_question_helpers_keep_their_statements() -> None:
    result = subprocess.run(
        [_node(), "--test", str(REPO / "tests" / "test_studio_atelier_questions.mjs")],
        capture_output=True, text=True, check=False, cwd=REPO,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("name", [
    "studio_atelier_questions.js",
    "studio_atelier.js",
    "studio.js",
    "studio_architecture_graph_actions.js",
])
def test_edited_browser_scripts_parse(name: str) -> None:
    result = subprocess.run([_node(), "--check", str(BROWSER / name)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
