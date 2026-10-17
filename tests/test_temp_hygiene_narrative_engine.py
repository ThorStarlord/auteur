"""The narrative-engine diagnostics test must not leave files in the system temp directory.

It used tempfile.mktemp() and wrote a story bible there. Nothing removed that file, so every
full run left one behind in the temp directory the mutation gate uses.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NODE = "tests/test_narrative_engine_integration.py::test_diagnostics_run_without_cartographer_outline"


def test_diagnostics_test_leaves_no_temporary_files(tmp_path):
    scratch = tmp_path / "tmp"
    scratch.mkdir()
    env = dict(os.environ, TMP=str(scratch), TEMP=str(scratch), TMPDIR=str(scratch),
               PYTHONPATH=str(REPO / "src"))
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                             "--basetemp", str(tmp_path / "pt"), NODE],
                            cwd=REPO, env=env, capture_output=True, text=True, timeout=600)
    assert result.returncode == 0, result.stdout[-2000:]
    leftovers = sorted(p.name for p in scratch.iterdir())
    assert leftovers == [], f"the test left temporary files behind: {leftovers}"
