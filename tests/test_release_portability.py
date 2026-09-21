"""Cross-platform release portability invariants.

These tests are intentionally small and deterministic. Release Qualification
runs the complete source suite on Linux, Windows, and macOS, so fixed expected
values here turn platform drift into an explicit candidate failure instead of
a platform-local observation.
"""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

import yaml

from auteur.evaluation.cartographer_replay import canonical_json, sha256_hash
from auteur.expression.book import BookExpressionStore
from auteur.publish import publish


def _make_book(base: Path) -> Path:
    project = base / "project"
    project.mkdir(parents=True, exist_ok=True)
    from conftest import copy_bootstrap_template

    copy_bootstrap_template(project)
    book = BookExpressionStore(project).compose(
        ["chapter_01", "chapter_02"], title="The Lantern at Low Water"
    )
    BookExpressionStore(project).accept(book["book_expression_id"])
    return project


def _manuscript(project: Path) -> Path:
    accepted = yaml.safe_load(
        (project / "book" / "expression" / "accepted.yaml").read_text(encoding="utf-8")
    )
    return project / "book" / "expression" / f"book_v{accepted['revision']:03d}.md"


def _normalized_lf_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def test_canonical_json_has_platform_independent_utf8_hash() -> None:
    value = {
        "accent": "ação",
        "nested": {"z": 2, "a": 1},
        "list": ["α", "β"],
        "line": "first\nsecond",
    }
    assert canonical_json(value) == (
        '{"accent":"ação","line":"first\\nsecond","list":["α","β"],'
        '"nested":{"a":1,"z":2}}'
    ).encode("utf-8")
    assert sha256_hash(value) == (
        "sha256:beb09271e9a83044835d8415b8b63be5879fe03fc9b4aaccd12be5e0cd7b32b3"
    )


def test_publication_normalizes_source_line_endings(tmp_path: Path) -> None:
    lf_root = tmp_path / "lf"
    crlf_root = tmp_path / "crlf"
    lf_project = _make_book(lf_root)
    crlf_project = _make_book(crlf_root)

    lf_manuscript = _manuscript(lf_project)
    crlf_manuscript = _manuscript(crlf_project)
    canonical = _normalized_lf_bytes(lf_manuscript)
    lf_manuscript.write_bytes(canonical)
    crlf_manuscript.write_bytes(canonical.replace(b"\n", b"\r\n"))

    lf_html = lf_root / "book.html"
    crlf_html = crlf_root / "book.html"
    lf_epub = lf_root / "book.epub"
    crlf_epub = crlf_root / "book.epub"
    publish(lf_project, formats=["html"], html_output=lf_html)
    publish(crlf_project, formats=["html"], html_output=crlf_html)
    publish(lf_project, formats=["epub"], epub_output=lf_epub)
    publish(crlf_project, formats=["epub"], epub_output=crlf_epub)

    assert lf_html.read_bytes() == crlf_html.read_bytes()
    assert lf_epub.read_bytes() == crlf_epub.read_bytes()


def test_unicode_project_and_output_paths_round_trip(tmp_path: Path) -> None:
    root = tmp_path / "ação_故事_Δ"
    project = _make_book(root)
    html = root / "saída_故事.html"
    epub = root / "saída_故事.epub"

    publish(project, formats=["html"], html_output=html)
    publish(project, formats=["epub"], epub_output=epub)

    assert html.exists() and html.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")
    assert epub.exists()
    with ZipFile(epub, "r") as zf:
        assert zf.namelist()[0] == "mimetype"


def test_epub_archive_metadata_is_fixed(tmp_path: Path) -> None:
    project = _make_book(tmp_path)
    epub = tmp_path / "fixed.epub"
    publish(project, formats=["epub"], epub_output=epub)

    with ZipFile(epub, "r") as zf:
        assert {info.date_time for info in zf.infolist()} == {
            (1980, 1, 1, 0, 0, 0)
        }


def test_timezone_and_locale_environment_do_not_change_output(
    tmp_path: Path, monkeypatch
) -> None:
    project = _make_book(tmp_path)
    first = tmp_path / "first.epub"
    second = tmp_path / "second.epub"

    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C")
    publish(project, formats=["epub"], epub_output=first)

    monkeypatch.setenv("TZ", "Pacific/Honolulu")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    publish(project, formats=["epub"], epub_output=second)

    assert first.read_bytes() == second.read_bytes()


def test_long_project_path_round_trip(tmp_path: Path) -> None:
    root = tmp_path
    segment = "segment_" + ("x" * 32)
    while len(str(root / "project")) < 280:
        root = root / segment
    root.mkdir(parents=True, exist_ok=True)

    project = _make_book(root)
    output = root / "long-path.epub"
    publish(project, formats=["epub"], epub_output=output)

    assert len(str(project)) >= 280
    assert output.exists()
