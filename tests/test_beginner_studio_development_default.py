"""Graph-first Studio is the default; the previous Beginner stays a reversible fallback.

Owner-selected default (PR #371); Stage-B essential safety exercised live in a
browser for Issue #360. The previous Beginner remains at /beginner.html and can
be served at / with --legacy-default.
"""
from __future__ import annotations

from urllib.request import urlopen

from auteur.beginner.server import BeginnerWorkspaceServer


def _get(base: str, route: str) -> bytes:
    with urlopen(base + route) as response:
        assert response.status == 200
        return response.read()


def _run_case(tmp_path, *, studio_development_default: bool):
    server = BeginnerWorkspaceServer(
        tmp_path, port=0, studio_development_default=studio_development_default
    )
    thread = server.start_in_thread()
    try:
        base = f"http://127.0.0.1:{server.port}"
        root = _get(base, "/")
        legacy = _get(base, "/beginner.html")
        direct_studio = _get(base, "/studio.html")
        index = _get(base, "/index.html")
        assert b'Living Story Studio' in direct_studio
        assert b'href="/beginner.html"' in direct_studio
        assert b'id="app-shell"' in legacy
        assert b'id="app-shell"' in index
        assert b'id="viewport"' not in legacy
        assert b'"status": "ok"' in _get(base, "/api/beginner/health")
        return root
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def test_legacy_beginner_can_still_be_served_at_root(tmp_path):
    root = _run_case(tmp_path, studio_development_default=False)
    assert b'id="app-shell"' in root
    assert b'id="viewport"' not in root


def test_studio_is_default_without_any_flag(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        root = _get(f"http://127.0.0.1:{server.port}", "/")
        assert b'id="viewport"' in root
        assert b'id="app-shell"' not in root
    finally:
        server.stop()
        thread.join(timeout=2)


def test_explicit_development_switch_preserves_reversible_fallback(tmp_path):
    root = _run_case(tmp_path, studio_development_default=True)
    assert b'id="viewport"' in root
    assert b'id="app-shell"' not in root
