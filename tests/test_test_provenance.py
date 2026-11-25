"""The verification run is only evidence about the checkout it was started in.

``tests/conftest.py`` refuses to start unless ``auteur`` loads from this checkout's ``src``. These tests check the
two places a wrong import could still hide: a subprocess started by a test, and the browser assets a served page
actually receives.
"""
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

from auteur.beginner.server import BeginnerWorkspaceServer


def _expected_src() -> Path:
    return Path(os.environ["AUTEUR_TEST_SRC"])


def test_a_subprocess_started_by_a_test_loads_this_checkout():
    out = subprocess.run(
        [sys.executable, "-c", "import auteur; print(auteur.__file__)"],
        capture_output=True, text=True, check=True, timeout=60,
    ).stdout.strip()
    assert Path(out).resolve().is_relative_to(_expected_src()), out


def test_served_browser_assets_are_the_files_of_this_checkout(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        for name in ("studio_atelier.js", "studio_atelier_impact.js"):
            with urllib.request.urlopen(f"http://127.0.0.1:{server.port}/{name}", timeout=10) as response:
                served = response.read()
            assert served == (_expected_src() / "auteur" / "beginner" / "browser" / name).read_bytes(), name
    finally:
        server.stop()
        thread.join(timeout=5)
