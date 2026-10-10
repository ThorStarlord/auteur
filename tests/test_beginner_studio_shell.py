"""Opt-in Studio shell is served by the existing Beginner HTTP process."""
from __future__ import annotations

from contextlib import contextmanager
from urllib.request import urlopen

from auteur.beginner.server import BeginnerWorkspaceServer


@contextmanager
def server_running(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        yield server
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def test_studio_shell_is_opt_in_and_asset_allowlisted(tmp_path):
    with server_running(tmp_path) as server:
        base = f"http://127.0.0.1:{server.port}"
        for path, expected in (
            ("/studio.html", b"Living Story Studio"),
            ("/studio.js", b"Working association created"),
            ("/studio.css", b".node"),
        ):
            with urlopen(base + path) as response:
                assert response.status == 200
                assert expected in response.read()
        with urlopen(base + "/") as response:
            assert b'href="/studio.html"' in response.read()


def test_studio_says_content_is_not_automatically_persisted(tmp_path):
    with server_running(tmp_path) as server:
        with urlopen(f"http://127.0.0.1:{server.port}/studio.html") as response:
            html = response.read().decode("utf-8")
        assert "not automatically saved" in html
        assert "Export JSON" in html and "Import JSON" in html
        assert "does not accept canon" in html
