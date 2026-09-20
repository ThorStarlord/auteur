from __future__ import annotations

import json
from pathlib import Path
from urllib.request import urlopen

from auteur.beginner.book_progress import project_book_progress
from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.expression.book import BookExpressionStore
from conftest import copy_bootstrap_template


def _accepted_book_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir(parents=True)
    copy_bootstrap_template(project)
    store = BookExpressionStore(project)
    book = store.compose(["chapter_01", "chapter_02"], title="Whole Book")
    store.accept(book["book_expression_id"])
    return project


def test_book_progress_is_read_only_when_publication_is_not_ready(tmp_path: Path) -> None:
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    progress = project_book_progress(tmp_path)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert after == before
    assert progress.publication_ready is False
    assert progress.publish_commands == ()
    assert progress.authority_status == "DERIVED / NOT CANON"


def test_book_progress_reuses_accepted_book_as_publication_preflight(tmp_path: Path) -> None:
    project = _accepted_book_project(tmp_path)

    progress = project_book_progress(project)

    assert progress.accepted_chapters >= 2
    assert progress.book_expression.startswith("accepted")
    assert progress.publication_ready is True
    assert progress.publication_blocker is None
    assert progress.publish_commands == (
        "auteur publish --project . --format html",
        "auteur publish --project . --format epub",
    )


def test_book_progress_endpoint_is_read_only(tmp_path: Path) -> None:
    project = _accepted_book_project(tmp_path)
    accepted = project / "book" / "expression" / "accepted.yaml"
    before = accepted.read_bytes()

    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    try:
        with urlopen(
            f"http://127.0.0.1:{server.port}/api/beginner/book/progress",
            timeout=5,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        server.stop()
        thread.join(timeout=5)

    assert payload["publication_ready"] is True
    assert payload["authority_status"] == "DERIVED / NOT CANON"
    assert accepted.read_bytes() == before


def test_browser_exposes_whole_book_orientation_without_mutation_action() -> None:
    html = Path("src/auteur/beginner/browser/index.html").read_text(encoding="utf-8")
    app = Path("src/auteur/beginner/browser/app.js").read_text(encoding="utf-8")

    assert 'id="book-progress-panel"' in html
    assert "/api/beginner/book/progress" in app
    assert "Publication handoff ready" in app
    assert "/api/beginner/book/accept" not in app
    assert "/api/beginner/book/publish" not in app
