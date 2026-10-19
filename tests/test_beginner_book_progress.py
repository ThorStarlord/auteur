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


def test_book_progress_uses_authoritative_plan_for_completed_orientation(
    tmp_path: Path, monkeypatch,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    chapters = project / "chapters"
    for index in range(1, 7):
        chapter = chapters / f"{index:02d}"
        chapter.mkdir(parents=True)
        prose = f"Kept chapter {index}.\n".encode()
        (chapter / "final.md").write_bytes(prose)
        (chapter / "draft_v1.md").write_bytes(prose)

    monkeypatch.setattr(
        "auteur.beginner.book_progress.gather_status",
        lambda _root: {
            "chapters": [{} for _ in range(6)],
            "blueprint": {"chapters": 0, "planned_chapters": 6},
            "book": {},
            "reconciliation": {},
        },
    )

    progress = project_book_progress(project)

    assert progress.planned_chapters == 6
    assert progress.accepted_chapters == 6
    assert progress.current_chapter == 6
    assert progress.current_chapter_state == "Kept"
    assert progress.next_story_action == "Review your Book"


def test_accepted_discovered_chapters_do_not_infer_book_completion(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "project"
    project.mkdir()
    chapters = project / "chapters"
    for index in range(1, 7):
        chapter = chapters / f"{index:02d}"
        chapter.mkdir(parents=True)
        prose = f"Kept chapter {index}.\n".encode()
        (chapter / "final.md").write_bytes(prose)
        (chapter / "draft_v1.md").write_bytes(prose)

    monkeypatch.setattr(
        "auteur.beginner.book_progress.gather_status",
        lambda _root: {
            "chapters": [{} for _ in range(6)],
            "blueprint": {},
            "book": {},
            "reconciliation": {},
        },
    )

    progress = project_book_progress(project)

    assert progress.planned_chapters == 0
    assert progress.discovered_chapters == 6
    assert progress.accepted_chapters == 6
    assert progress.current_chapter == 7
    assert progress.current_chapter_state == "Working"
    assert progress.next_story_action == "Write Chapter 7"


def test_estimated_blueprint_chapters_are_authoritative_plan(tmp_path: Path) -> None:
    project = _accepted_book_project(tmp_path)
    blueprint = project / "blueprint.yaml"
    blueprint.write_text("structure:\n  estimated_chapters: 2\n", encoding="utf-8")

    progress = project_book_progress(project)

    assert progress.planned_chapters == 2


def test_newer_working_revision_remains_working_alongside_kept_version(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    copy_bootstrap_template(project)
    (project / "blueprint.yaml").write_text(
        "structure:\n  estimated_chapters: 2\n", encoding="utf-8",
    )
    chapter_one = project / "chapters" / "01"
    chapter_one.mkdir(parents=True, exist_ok=True)
    (chapter_one / "final.md").write_text("Kept Chapter 1.\n", encoding="utf-8")
    (chapter_one / "draft_v1.md").write_text("Kept Chapter 1.\n", encoding="utf-8")
    chapter_two = project / "chapters" / "02"
    chapter_two.mkdir(parents=True, exist_ok=True)
    kept = "Previously accepted Chapter 2.\n"
    working = "New unaccepted Chapter 2 revision.\n"
    (chapter_two / "final.md").write_text(kept, encoding="utf-8")
    (chapter_two / "draft_v1.md").write_text(kept, encoding="utf-8")
    (chapter_two / "draft_v2.md").write_text(working, encoding="utf-8")

    progress = project_book_progress(project)

    assert progress.current_chapter == 2
    assert progress.current_chapter_state == "Working"
    assert "chapters/02/final.md" in progress.accepted_chapter_refs
    assert progress.next_story_action == "Continue Chapter 2"
    assert (chapter_two / "final.md").read_text(encoding="utf-8") == kept
    assert (chapter_two / "draft_v2.md").read_text(encoding="utf-8") == working


def test_book_progress_reuses_accepted_book_as_publication_preflight(tmp_path: Path) -> None:
    project = _accepted_book_project(tmp_path)

    progress = project_book_progress(project)

    # Accepted Book-expression sources are not Chapter final.md history used
    # by the Book re-entry projection.
    assert progress.accepted_chapters == 0
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
