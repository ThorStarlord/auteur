"""Session-scoped bootstrap cache + xdist support.

Caches the expensive ``CanonicalStoryBootstrap`` setup once per session
so every test file can ``copytree`` instead of re-bootstrapping.

With ``pytest-xdist``, each worker process builds its own cache
(once per worker).  Run with ``-n auto`` to parallelise across test files.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from auteur.canonical_story import CanonicalStoryBootstrap
from auteur.expression.book import BookExpressionStore

_BOOTSTRAP_CACHE: Path | None = None


def copy_bootstrap_template(dest: Path) -> Path:
    """Fast-copy the session-cached bootstrap into *dest*.

    Returns ``dest`` (files are placed directly inside it) so callers can use
    the same path contract as ``_make_book``.
    """
    global _BOOTSTRAP_CACHE
    if _BOOTSTRAP_CACHE is None:
        _fallback_bootstrap(dest)
        return dest
    shutil.copytree(_BOOTSTRAP_CACHE, dest, dirs_exist_ok=True)
    return dest


def _fallback_bootstrap(dest: Path) -> None:
    """Slow bootstrap when the session cache isn't available."""
    bootstrap = CanonicalStoryBootstrap(Path("examples/canonical_story"))
    bootstrap.copy_to(dest)
    bootstrap.accept_native_identity_and_structure(dest)
    bootstrap.accept_scene_realizations(dest)
    bootstrap.bootstrap_expressions(dest)
    bootstrap.bootstrap_second_chapter(dest)


@pytest.fixture(scope="session", autouse=True)
def _bootstrap_cache_session() -> None:
    """Build the bootstrap template once per session (once per xdist worker).

    The fixture is ``autouse`` so it always runs before any test, populating
    ``_BOOTSTRAP_CACHE`` before any test file's ``_make_book`` call.
    """
    global _BOOTSTRAP_CACHE
    tmp = Path(tempfile.mkdtemp())
    _fallback_bootstrap(tmp)
    _BOOTSTRAP_CACHE = tmp
    yield
    shutil.rmtree(tmp)
