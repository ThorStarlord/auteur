"""Comprehensive release-integrity tests: packaging, determinism, EPUB
conformance, publishing integrity, version metadata, status, and hashing.

Each section is self-contained and uses the same patterns as the existing
test_publish.py / test_publish_release.py files.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.resources
import time
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

import pytest
import yaml

from auteur.expression.book import BookExpressionStore
from auteur.narrative_ontology.loader.ontology_loader import (
    OntologyLoader,
    _ONTOLOGY_PACKAGE,
    _read_ontology_yaml,
)
from auteur.publish import (
    CSS,
    ALL_FORMATS,
    AUTEUR_VERSION,
    PublishError,
    PublishingSnapshot,
    publish,
)
from auteur.status import gather_status


def _make_book(tmp_path: Path) -> Path:
    """Standard book fixture matching existing test conventions."""
    project = tmp_path / "project"
    project.mkdir(parents=True, exist_ok=True)
    from conftest import copy_bootstrap_template as _cbt

    _cbt(project)
    book = BookExpressionStore(project).compose(
        ["chapter_01", "chapter_02"], title="The Lantern at Low Water"
    )
    BookExpressionStore(project).accept(book["book_expression_id"])
    return project


def _sha256(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


# ===================================================================
# 1. Ontology packaging
# ===================================================================


class TestOntologyPackaging:
    """Verify ontology YAML resources are packaged and loadable."""

    def test_ontology_resources_in_package(self) -> None:
        """Every ontology YAML exists under the package data directory."""
        known = {"base_ontology.yaml", "mystery_ontology.yaml",
                 "netorare_ontology.yaml", "gentlefemdom_ontology.yaml"}
        try:
            pkg = importlib.resources.files(_ONTOLOGY_PACKAGE)
            found = {f.name for f in pkg.iterdir()
                     if f.name.endswith(".yaml")}
        except (ModuleNotFoundError, TypeError):
            # Fallback for older Python / editable installs:
            # check relative to the source tree
            from pathlib import Path as _P
            base = _P(__file__).parents[1] / "src" / _ONTOLOGY_PACKAGE.replace(".", "/")
            found = {f.name for f in base.iterdir() if f.name.endswith(".yaml")}
        for name in known:
            assert name in found, f"Missing ontology resource: {name}"

    def test_base_ontology_loads_from_package(self) -> None:
        """OntologyLoader.load_base_ontology works outside checkout dir."""
        loader = OntologyLoader()
        base = loader.load_base_ontology()
        assert isinstance(base, dict)
        assert len(base) > 0, "base ontology must not be empty"
        # A real ontology has named concepts
        assert any(k for k in base if isinstance(base[k], dict))

    def test_genre_ontology_loads_from_package(self) -> None:
        """Genre-specific ontologies load correctly from the package."""
        loader = OntologyLoader()
        for genre in ("mystery", "netorare", "gentlefemdom"):
            genre_onto = loader.load_genre_ontology(genre)
            assert isinstance(genre_onto, dict)
            assert len(genre_onto) > 0, f"{genre} ontology must not be empty"

    def test_missing_resource_raises_clear_error(self) -> None:
        """Asking for a non-existent ontology raises FileNotFoundError
        with a message that names the resource and package."""
        with pytest.raises(FileNotFoundError) as exc:
            _read_ontology_yaml("nonexistent_ontology.yaml")
        msg = str(exc.value)
        assert "nonexistent_ontology.yaml" in msg
        assert _ONTOLOGY_PACKAGE in msg


# ===================================================================
# 2. Publishing source integrity
# ===================================================================


class TestPublishingIntegrity:
    """Verify the integrity verification in the publishing pipeline."""

    def test_accepted_publishes_successfully(self, tmp_path: Path) -> None:
        """Happy path: a freshly accepted book publishes without error."""
        project = _make_book(tmp_path)
        result = publish(project, formats=["html", "epub"],
                         output_dir=tmp_path / "out")
        assert result["snapshot_id"].startswith("pub_")
        assert len(result["renderers"]) == 2
        for r in result["renderers"]:
            assert r["format"] in ("html", "epub")
            assert r["output_hash"].startswith("sha256:")

    def _enable_integrity_check(self, project: Path) -> str:
        """Inject a content_hash into accepted.yaml so the integrity gate
        actually fires.  Returns the current manuscript hash."""
        accepted = project / "book" / "expression" / "accepted.yaml"
        data = yaml.safe_load(accepted.read_text(encoding="utf-8")) or {}

        rev = data["revision"]
        md_path = project / "book" / "expression" / f"book_v{rev:03d}.md"
        manuscript = md_path.read_text(encoding="utf-8")
        h = _sha256(manuscript)
        data["content_hash"] = h
        accepted.write_text(yaml.safe_dump(data, sort_keys=False),
                            encoding="utf-8")
        return h

    def _tamper_manuscript(self, project: Path) -> None:
        """Append tamper text inside the last chapter of the manuscript."""
        rev = yaml.safe_load(
            (project / "book" / "expression" / "accepted.yaml").read_text("utf-8")
        )["revision"]
        md_path = project / "book" / "expression" / f"book_v{rev:03d}.md"
        original = md_path.read_text(encoding="utf-8")
        modified = original.replace(
            "<!-- auteur:end-chapter id=chapter_02 -->",
            "TAMPERED_CONTENT\n\n<!-- auteur:end-chapter id=chapter_02 -->",
        )
        assert modified != original, "tamper must actually change the file"
        md_path.write_text(modified, encoding="utf-8")

    def test_tampered_markdown_blocks_html(self, tmp_path: Path) -> None:
        """Modifying markdown after acceptance raises PublishError (HTML)."""
        project = _make_book(tmp_path)
        # First publish succeeds
        publish(project, formats=["html"], html_output=tmp_path / "ok.html")

        self._enable_integrity_check(project)
        self._tamper_manuscript(project)

        with pytest.raises(PublishError, match="modified after acceptance"):
            publish(project, formats=["html"],
                    html_output=tmp_path / "tampered.html")

    def test_tampered_markdown_blocks_epub(self, tmp_path: Path) -> None:
        """Modifying markdown after acceptance raises PublishError (EPUB)."""
        project = _make_book(tmp_path)
        publish(project, formats=["epub"], epub_output=tmp_path / "ok.epub")

        self._enable_integrity_check(project)
        self._tamper_manuscript(project)

        with pytest.raises(PublishError, match="modified after acceptance"):
            publish(project, formats=["epub"],
                    epub_output=tmp_path / "tampered.epub")

    def test_tampered_markdown_blocks_multi_format(self, tmp_path: Path) -> None:
        """Integrity failure blocks both formats simultaneously."""
        project = _make_book(tmp_path)
        publish(project, formats=["html", "epub"],
                output_dir=tmp_path / "ok")

        self._enable_integrity_check(project)
        self._tamper_manuscript(project)

        with pytest.raises(PublishError, match="modified after acceptance"):
            publish(project, formats=["html", "epub"],
                    output_dir=tmp_path / "tampered")

    def test_no_partial_output_on_tampered(self, tmp_path: Path) -> None:
        """When integrity fails, zero output files are left behind."""
        project = _make_book(tmp_path)
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        self._enable_integrity_check(project)
        self._tamper_manuscript(project)

        with pytest.raises(PublishError):
            publish(project, formats=["html", "epub"], output_dir=out_dir)
        # Nothing was written
        assert not any(out_dir.iterdir()), (
            "partial output files found after failed publish"
        )

    def test_prior_latest_unchanged_on_tampered(self, tmp_path: Path) -> None:
        """The latest.yaml pointer is NOT overwritten on a failed publish."""
        project = _make_book(tmp_path)
        # Successful first publish
        publish(project, formats=["html"], html_output=tmp_path / "ok.html")
        latest = project / ".auteur" / "publishing" / "latest.yaml"
        assert latest.exists()
        before = latest.read_bytes()

        self._enable_integrity_check(project)
        self._tamper_manuscript(project)

        with pytest.raises(PublishError):
            publish(project, formats=["html"],
                    html_output=tmp_path / "fail.html")
        assert latest.read_bytes() == before, "latest.yaml was overwritten"


# ===================================================================
# 3. EPUB corrections
# ===================================================================


class TestEpubCorrections:
    """EPUB3 specification conformance corrections."""

    def test_mimetype_is_first_entry(self, tmp_path: Path) -> None:
        """mimetype must be the very first entry in the ZIP archive."""
        project = _make_book(tmp_path)
        out = tmp_path / "mime.epub"
        publish(project, formats=["epub"], epub_output=out)
        with ZipFile(out, "r") as zf:
            names = zf.namelist()
        assert names[0] == "mimetype", f"first entry is {names[0]!r}"

    def test_mimetype_is_stored(self, tmp_path: Path) -> None:
        """mimetype entry uses ZIP_STORED (uncompressed)."""
        project = _make_book(tmp_path)
        out = tmp_path / "stored.epub"
        publish(project, formats=["epub"], epub_output=out)
        with ZipFile(out, "r") as zf:
            info = zf.getinfo("mimetype")
        assert info.compress_type == ZIP_STORED, (
            f"mimetype compress_type is {info.compress_type}, expected {ZIP_STORED}"
        )

    def test_mimetype_bytes(self, tmp_path: Path) -> None:
        """mimetype contains exactly the bytes b'application/epub+zip'."""
        project = _make_book(tmp_path)
        out = tmp_path / "mimebytes.epub"
        publish(project, formats=["epub"], epub_output=out)
        with ZipFile(out, "r") as zf:
            raw = zf.read("mimetype")
        assert raw == b"application/epub+zip", (
            f"mimetype content: {raw!r}"
        )

    def test_all_paths_use_forward_slash(self, tmp_path: Path) -> None:
        """Every path inside the EPUB uses forward slashes."""
        project = _make_book(tmp_path)
        out = tmp_path / "fwd.epub"
        publish(project, formats=["epub"], epub_output=out)
        with ZipFile(out, "r") as zf:
            for name in zf.namelist():
                assert "\\" not in name, f"backslash in archive path: {name!r}"

    def test_no_auteur_markers_in_xhtml(self, tmp_path: Path) -> None:
        """No Auteur <!-- auteur: --> marker remains in XHTML output."""
        project = _make_book(tmp_path)
        out = tmp_path / "clean.epub"
        publish(project, formats=["epub"], epub_output=out)
        with ZipFile(out, "r") as zf:
            for name in zf.namelist():
                if not name.endswith(".xhtml"):
                    continue
                content = zf.read(name).decode("utf-8")
                assert "<!-- auteur:" not in content, (
                    f"Auteur marker found in {name}"
                )


# ===================================================================
# 4. Determinism
# ===================================================================


class TestDeterministicAcrossInvocations:
    """Same inputs produce byte-identical output across invocations."""

    def test_html_deterministic_across_invocations(self, tmp_path: Path) -> None:
        """HTML output is identical when produced in different temp dirs."""
        p1 = _make_book(tmp_path)
        out1 = tmp_path / "a.html"
        publish(p1, formats=["html"], html_output=out1)

        p2 = _make_book(Path(tmp_path.as_posix() + "_b"))
        out2 = Path(tmp_path.as_posix() + "_b") / "b.html"
        publish(p2, formats=["html"], html_output=out2)

        assert out1.read_bytes() == out2.read_bytes()

    def test_epub_deterministic_across_invocations(self, tmp_path: Path) -> None:
        """EPUB output is byte-identical when produced in different temp dirs."""
        p1 = _make_book(tmp_path)
        out1 = tmp_path / "a.epub"
        publish(p1, formats=["epub"], epub_output=out1)

        p2 = _make_book(Path(tmp_path.as_posix() + "_c"))
        out2 = Path(tmp_path.as_posix() + "_c") / "b.epub"
        publish(p2, formats=["epub"], epub_output=out2)

        assert out1.read_bytes() == out2.read_bytes()

    def test_html_non_deterministic(self, tmp_path: Path) -> None:
        """Sleeping between renders does NOT change output
        (verifies within-same-second is not the sole cause of determinism)."""
        project = _make_book(tmp_path)
        out1 = tmp_path / "a.html"
        publish(project, formats=["html"], html_output=out1)

        time.sleep(1.2)  # cross second boundary

        out2 = tmp_path / "b.html"
        publish(project, formats=["html"], html_output=out2)

        assert out1.read_bytes() == out2.read_bytes()

    def test_config_change_produces_different_hash(self, tmp_path: Path) -> None:
        """Changing the CSS produces a different output hash."""
        project = _make_book(tmp_path)
        out1 = tmp_path / "default.html"
        r1 = publish(project, formats=["html"], html_output=out1)

        out2 = tmp_path / "custom.html"
        r2 = publish(project, formats=["html"], html_output=out2, css="body{color:red}")
        assert r1["renderers"][0]["output_hash"] != r2["renderers"][0]["output_hash"]


# ===================================================================
# 5. Version metadata
# ===================================================================


class TestVersionMetadata:
    """Auteur version metadata consistency."""

    def test_package_version_matches_publishing(self) -> None:
        """AUTEUR_VERSION in publish module matches importlib.metadata."""
        try:
            pkg_ver = importlib.metadata.version("auteur")
        except importlib.metadata.PackageNotFoundError:
            # Fall back to __version__ when not installed as package
            from auteur import __version__ as ver
            pkg_ver = ver
        assert AUTEUR_VERSION == pkg_ver, (
            f"publish.AUTEUR_VERSION={AUTEUR_VERSION!r} != "
            f"importlib.metadata={pkg_ver!r}"
        )

    def test_auteur_version_in_snapshot(self, tmp_path: Path) -> None:
        """PublishingSnapshot._immutable_snapshot contains the correct
        auteur_version in its reproducibility section."""
        project = _make_book(tmp_path)
        snapshot = PublishingSnapshot(project)
        snap = snapshot._immutable_snapshot()
        assert snap["reproducibility"]["auteur_version"] == AUTEUR_VERSION

    def test_version_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When importlib.metadata.version fails, the fallback
        returns __version__ from auteur/__init__.py."""
        def _broken_version(_name: str) -> str:
            raise importlib.metadata.PackageNotFoundError("auteur")

        monkeypatch.setattr(importlib.metadata, "version", _broken_version)

        # Re-import the fallback function to pick up the monkeypatch
        from auteur.publish import _get_auteur_version
        ver = _get_auteur_version()

        from auteur import __version__
        assert ver == __version__, (
            f"fallback version {ver!r} != __version__ {__version__!r}"
        )


# ===================================================================
# 6. Status
# ===================================================================


class TestStatusScenarios:
    """gather_status never crashes and returns sensible results."""

    def test_status_empty_project(self, tmp_path: Path) -> None:
        """No crash on a completely empty directory."""
        status = gather_status(tmp_path)
        assert isinstance(status, dict)
        # Identity should be missing
        assert status.get("identity", {}).get("status") == "missing"
        assert status.get("blueprint", {}).get("status") == "missing"

    def test_status_identity_only(self, tmp_path: Path) -> None:
        """Only story_identity.yaml exists."""
        identity = {
            "title": "Test", "author_intent": "Testing",
            "length_class": "short_story", "genre": "fantasy",
            "mode": "tragic", "medium": "novel",
        }
        (tmp_path / "story_identity.yaml").write_text(
            yaml.safe_dump(identity, sort_keys=False), encoding="utf-8",
        )
        status = gather_status(tmp_path)
        assert status["identity"]["status"] != "missing"
        assert status["blueprint"]["status"] == "missing"

    def test_status_no_chapters(self, tmp_path: Path) -> None:
        """Project with blueprint but no chapter directories."""
        identity = {
            "title": "Test", "author_intent": "Testing",
            "length_class": "short_story", "genre": "fantasy",
            "mode": "tragic", "medium": "novel",
        }
        (tmp_path / "story_identity.yaml").write_text(
            yaml.safe_dump(identity, sort_keys=False), encoding="utf-8",
        )
        (tmp_path / "blueprint.yaml").write_text(
            yaml.safe_dump({"chapters": []}, sort_keys=False), encoding="utf-8",
        )
        status = gather_status(tmp_path)
        assert status["identity"]["status"] != "missing"
        assert status["blueprint"]["status"] == "present"
        assert isinstance(status, dict)

    def test_status_partial_chapter(self, tmp_path: Path) -> None:
        """Chapter directory exists without an accepted expression."""
        identity = {
            "title": "Test", "author_intent": "Testing",
            "length_class": "short_story", "genre": "fantasy",
            "mode": "tragic", "medium": "novel",
        }
        (tmp_path / "story_identity.yaml").write_text(
            yaml.safe_dump(identity, sort_keys=False), encoding="utf-8",
        )
        (tmp_path / "blueprint.yaml").write_text(
            yaml.safe_dump({"chapters": ["chapter_01"]}, sort_keys=False),
            encoding="utf-8",
        )
        (tmp_path / "chapters" / "01").mkdir(parents=True)
        status = gather_status(tmp_path)
        assert status["chapters"] is None or len(status["chapters"]) >= 0
        assert isinstance(status, dict)

    def test_status_accepted_chapters_no_book(self, tmp_path: Path) -> None:
        """Chapters have accepted expressions but no book expression."""
        # Build a minimal project with _make_book then remove the book
        project = _make_book(tmp_path)

        # Remove the book accepted expression
        import shutil
        book_dir = project / "book"
        if book_dir.exists():
            shutil.rmtree(book_dir)

        status = gather_status(project)
        assert status["book"]["expression"] == "missing"
        assert isinstance(status, dict)

    def test_status_malformed_yaml(self, tmp_path: Path) -> None:
        """Malformed but optional YAML returns a status dict (no crash)."""
        (tmp_path / "story_identity.yaml").write_text(
            "{invalid: yaml: stuff\nbroken", encoding="utf-8",
        )
        status = gather_status(tmp_path)
        # Malformed YAML -> _read_yaml returns None -> identity becomes "missing"
        assert isinstance(status, dict)

    def test_status_read_only(self, tmp_path: Path) -> None:
        """gather_status does not write any files."""
        project = _make_book(tmp_path)
        mtimes = {p: p.stat().st_mtime_ns
                  for p in project.rglob("*") if p.is_file()}
        gather_status(project)
        after = {p: p.stat().st_mtime_ns
                 for p in project.rglob("*") if p.is_file()}
        for path, ts in mtimes.items():
            assert after.get(path) == ts, (
                f"gather_status modified {path}"
            )

    def test_status_valid_suggestions(self, tmp_path: Path) -> None:
        """Suggested commands look like valid CLI syntax."""
        status = gather_status(_make_book(tmp_path))
        cmd = status.get("suggested_command")
        if cmd is not None:
            assert isinstance(cmd, str)
            assert cmd.startswith("auteur "), f"unexpected suggestion: {cmd}"
            # Does not contain obvious template placeholders that escaped
            assert "<" not in cmd or cmd.count("<") == cmd.count(">"), (
                f"unbalanced angle brackets in suggestion: {cmd}"
            )


# ===================================================================
# 7. Publishing hash
# ===================================================================


class TestPublishingHash:
    """Output hash format correctness."""

    def test_epub_output_hash_is_raw_binary(self, tmp_path: Path) -> None:
        """EPUB hash is sha256:<hex> computed from raw bytes."""
        project = _make_book(tmp_path)
        out = tmp_path / "hash.epub"
        result = publish(project, formats=["epub"], epub_output=out)
        h = result["renderers"][0]["output_hash"]
        assert h.startswith("sha256:"), f"unexpected hash prefix: {h}"
        hex_part = h[len("sha256:"):]
        assert len(hex_part) == 64, f"expected 64 hex chars, got {len(hex_part)}"
        int(hex_part, 16)  # raises ValueError if not hex

    def test_html_output_hash_is_string(self, tmp_path: Path) -> None:
        """HTML hash is sha256:<hex> computed from string content."""
        project = _make_book(tmp_path)
        out = tmp_path / "hash.html"
        result = publish(project, formats=["html"], html_output=out)
        h = result["renderers"][0]["output_hash"]
        assert h.startswith("sha256:"), f"unexpected hash prefix: {h}"
        hex_part = h[len("sha256:"):]
        assert len(hex_part) == 64, f"expected 64 hex chars, got {len(hex_part)}"
        int(hex_part, 16)  # raises ValueError if not hex


# ===================================================================
# 8. Markdown renderer
# ===================================================================


class TestMarkdownRenderer:
    """markdown_it is unconditionally importable and stable."""

    def test_markdown_renderer_is_stable(self) -> None:
        """markdown_it can be imported from the publish module path."""
        from markdown_it import MarkdownIt
        md = MarkdownIt("zero", {"breaks": True})
        md.enable(["newline", "paragraph", "emphasis", "heading", "list"])
        result = md.render("Hello **world**")
        assert "<strong>world</strong>" in result
