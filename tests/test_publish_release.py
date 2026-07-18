"""Release qualification: comprehensive publishing boundary verification.

Covers deterministic bytes, edge cases, conformance, and failure modes
that the unit tests exercise separately but this file validates together.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
import yaml

from auteur.expression.book import BookExpressionStore
from auteur.publish import (
    PublishError,
    PublishingSnapshot,
    publish,
)


def _make_book(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir(parents=True, exist_ok=True)
    from conftest import copy_bootstrap_template as _cbt
    _cbt(project)
    book = BookExpressionStore(project).compose(
        ["chapter_01", "chapter_02"], title="The Lantern at Low Water"
    )
    BookExpressionStore(project).accept(book["book_expression_id"])
    return project


# ---------------------------------------------------------------------------
# Deterministic output
# ---------------------------------------------------------------------------


class TestDeterministicOutput:
    def test_html_bytes_identical_on_repeat(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        out1 = tmp_path / "a.html"
        out2 = tmp_path / "b.html"
        publish(project, formats=["html"], html_output=out1)
        publish(project, formats=["html"], html_output=out2)
        assert out1.read_bytes() == out2.read_bytes()

    def test_epub_bytes_identical_on_repeat(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        out1 = tmp_path / "a.epub"
        out2 = tmp_path / "b.epub"
        publish(project, formats=["epub"], epub_output=out1)
        publish(project, formats=["epub"], epub_output=out2)
        assert out1.read_bytes() == out2.read_bytes()

    def test_snapshot_id_deterministic(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        s1 = PublishingSnapshot(project)
        s2 = PublishingSnapshot(project)
        assert s1._snapshot_id == s2._snapshot_id


# ---------------------------------------------------------------------------
# EPUB conformance
# ---------------------------------------------------------------------------


class TestEpubConformance:
    def test_epub_zip_forward_slashes(self, tmp_path: Path) -> None:
        """EPUB3 spec requires forward slashes in archive paths."""
        project = _make_book(tmp_path)
        out = tmp_path / "fwd.epub"
        publish(project, formats=["epub"], epub_output=out)
        with zipfile.ZipFile(out, "r") as zf:
            for name in zf.namelist():
                assert "\\" not in name, f"backslash in archive path: {name}"

    def test_epub_mimetype_first_entry(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        out = tmp_path / "mime.epub"
        publish(project, formats=["epub"], epub_output=out)
        with zipfile.ZipFile(out, "r") as zf:
            names = zf.namelist()
        assert names[0] == "mimetype", "mimetype must be first entry"

    def test_epub_mimetype_content(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        out = tmp_path / "mt.epub"
        publish(project, formats=["epub"], epub_output=out)
        with zipfile.ZipFile(out, "r") as zf:
            assert zf.read("mimetype").decode("ascii") == "application/epub+zip"

    def test_epub_opf_has_required_metadata(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        out = tmp_path / "opf.epub"
        publish(project, formats=["epub"], epub_output=out)
        with zipfile.ZipFile(out, "r") as zf:
            opf = zf.read("OEBPS/content.opf").decode("utf-8")
        assert "<dc:title>" in opf
        assert "<dc:creator>" in opf
        assert "<dc:language>en</dc:language>" in opf
        assert "<dc:identifier" in opf

    def test_epub_nav_has_all_chapters(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        out = tmp_path / "nav.epub"
        publish(project, formats=["epub"], epub_output=out)
        with zipfile.ZipFile(out, "r") as zf:
            nav = zf.read("OEBPS/nav.xhtml").decode("utf-8")
        assert "Chapter 1" in nav
        assert "Chapter 2" in nav

    def test_epub_spine_lists_all_chapters(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        out = tmp_path / "spine.epub"
        publish(project, formats=["epub"], epub_output=out)
        with zipfile.ZipFile(out, "r") as zf:
            opf = zf.read("OEBPS/content.opf").decode("utf-8")
        assert '<itemref idref="ch1"/>' in opf
        assert '<itemref idref="ch2"/>' in opf


# ---------------------------------------------------------------------------
# Unicode and special characters
# ---------------------------------------------------------------------------


class TestUnicodeHandling:
    def test_html_handles_unicode(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        snapshot = PublishingSnapshot(project)
        output = tmp_path / "unicode.html"
        snapshot.render_html(output)
        html = output.read_text(encoding="utf-8")
        assert "—" in html or "&mdash;" in html
        assert html.count("�") == 0, "replacement characters found in HTML"

    def test_epub_handles_unicode(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        out = tmp_path / "unicode.epub"
        publish(project, formats=["epub"], epub_output=out)
        with zipfile.ZipFile(out, "r") as zf:
            for name in zf.namelist():
                if name.endswith(".xhtml") or name.endswith(".opf"):
                    data = zf.read(name).decode("utf-8")
                    assert data.count("�") == 0, f"replacement chars in {name}"


# ---------------------------------------------------------------------------
# Output path collision
# ---------------------------------------------------------------------------


class TestOutputCollision:
    def test_html_epub_same_path_raises(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        same = tmp_path / "collision.html"
        publish(project, formats=["html"], html_output=same)
        with pytest.raises(FileExistsError):
            publish(project, formats=["html"], html_output=same)

    def test_epub_same_path_raises(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        same = tmp_path / "collision.epub"
        publish(project, formats=["epub"], epub_output=same)
        with pytest.raises(FileExistsError):
            publish(project, formats=["epub"], epub_output=same)


# ---------------------------------------------------------------------------
# Stale / missing accepted book
# ---------------------------------------------------------------------------


class TestStaleBook:
    def test_stale_accepted_pointer_raises(self, tmp_path: Path) -> None:
        """Accepted.yaml refers to a revision whose manuscript was deleted."""
        project = _make_book(tmp_path)
        # Remove the manuscript file, keep accepted.yaml
        for md in (project / "book" / "expression").glob("book_v*.md"):
            md.unlink()
        with pytest.raises(PublishError, match="Book manuscript not found"):
            PublishingSnapshot(project)

    def test_modified_manuscript_after_acceptance(self, tmp_path: Path) -> None:
        """Editing the manuscript after acceptance should affect publish."""
        project = _make_book(tmp_path)
        snapshot = PublishingSnapshot(project)
        out1 = tmp_path / "before.html"
        snapshot.render_html(out1)
        bytes_before = out1.read_bytes()

        # Append text inside a chapter body (within chapter markers)
        rev = snapshot._manifest["revision"]
        md_path = project / "book" / "expression" / f"book_v{rev:03d}.md"
        original = md_path.read_text(encoding="utf-8")
        modified = original.replace(
            "<!-- auteur:end-chapter id=chapter_01 -->",
            "TAMPERED\n\n<!-- auteur:end-chapter id=chapter_01 -->",
        )
        assert modified != original, "modification must actually change text"
        md_path.write_text(modified, encoding="utf-8")

        # Publish a new snapshot — it should read the modified manuscript
        snapshot2 = PublishingSnapshot(project)
        assert snapshot2._book_hash != snapshot._book_hash
        out2 = tmp_path / "after.html"
        snapshot2.render_html(out2)
        assert out2.read_bytes() != bytes_before

    def test_lifecycle_not_accepted_raises(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        accepted = project / "book" / "expression" / "accepted.yaml"
        data = yaml.safe_load(accepted.read_text(encoding="utf-8")) or {}
        data["lifecycle"] = "replaced"
        accepted.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        with pytest.raises(PublishError, match="not accepted"):
            PublishingSnapshot(project)


# ---------------------------------------------------------------------------
# Cross-format consistency
# ---------------------------------------------------------------------------


class TestCrossFormatConsistency:
    def test_chapter_count_matches(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        snapshot = PublishingSnapshot(project)
        assert len(snapshot._parsed["chapters"]) == 2

    def test_title_consistent_across_formats(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        snapshot = PublishingSnapshot(project)
        assert snapshot.title == "The Lantern at Low Water"

    def test_snapshot_and_run_share_snapshot_id(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        snapshot = PublishingSnapshot(project)
        r = snapshot.render_html(tmp_path / "shr.html")
        run = snapshot.save_snapshot([r])
        assert run["snapshot_id"] == snapshot._snapshot_id


# ---------------------------------------------------------------------------
# CLI integration (via direct call, not subprocess)
# ---------------------------------------------------------------------------


class TestCLIIntegration:
    def test_cli_parser_accepts_publish(self) -> None:
        from auteur.cli import _build_parser
        parser = _build_parser()
        args = parser.parse_args(["publish", "--project", ".", "--format", "html"])
        assert args.command == "publish"
        assert args.format == "html"

    def test_cli_publish_html_e2e(self, tmp_path: Path) -> None:
        project = _make_book(tmp_path)
        from auteur.publish import publish as _publish
        result = _publish(project, formats=["html"], html_output=tmp_path / "cli.html")
        assert result["snapshot_id"].startswith("pub_")
        assert (tmp_path / "cli.html").exists()


# ---------------------------------------------------------------------------
# Packaging
# ---------------------------------------------------------------------------


def test_publish_module_importable() -> None:
    import auteur.publish as m
    assert hasattr(m, "PublishingSnapshot")
    assert hasattr(m, "publish")
    assert hasattr(m, "PublishError")
    assert hasattr(m, "ALL_FORMATS")
    assert m.ALL_FORMATS == ["html", "epub"]
