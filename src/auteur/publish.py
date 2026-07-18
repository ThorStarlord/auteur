"""Immutable publishing pipeline: snapshot accepted Book state and render
to HTML, EPUB, or other publication formats."""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from zipfile import ZipFile, ZIP_DEFLATED

import yaml

try:
    from markdown_it import MarkdownIt

    _md = MarkdownIt("zero", {"breaks": True})
    _md.enable(["newline", "paragraph", "emphasis", "heading", "list"])
except ImportError:
    _md = None


Format = Literal["html", "epub"]
ALL_FORMATS: list[Format] = ["html", "epub"]


class PublishError(Exception):
    """Raised when publishing fails (no accepted book, missing content, etc.)."""


def _sha256(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _read_accepted_book_manifest(project: Path) -> dict[str, Any]:
    accepted = project / "book" / "expression" / "accepted.yaml"
    if not accepted.exists():
        raise PublishError(
            f"No accepted Book Expression found at {accepted}. "
            "Use 'auteur book accept' first."
        )
    data = yaml.safe_load(accepted.read_text(encoding="utf-8")) or {}
    if data.get("lifecycle") != "accepted":
        raise PublishError("Book Expression exists but is not accepted")
    return data


def _read_book_markdown(project: Path, manifest: dict[str, Any]) -> str:
    rev = manifest["revision"]
    md_path = project / "book" / "expression" / f"book_v{rev:03d}.md"
    if not md_path.exists():
        raise PublishError(f"Book manuscript not found at {md_path}")
    return md_path.read_text(encoding="utf-8")


CHAP_RE = re.compile(
    r"<!--\s*auteur:chapter\s+id=(\S+).*?-->\s*\n(.*?)<!--\s*auteur:end-chapter\s+id=\1\s*-->",
    re.DOTALL,
)

MARKER_RE = re.compile(
    r"^<!-- auteur:(?:chapter|end-chapter|book-separator|end-book-separator"
    r"|scene|end-scene|transition|end-transition).*?-->\s*$",
    re.MULTILINE,
)


def _strip_markers(text: str) -> str:
    return MARKER_RE.sub("", text).strip()


def _split_chapters(markdown: str) -> list[dict[str, Any]]:
    chapters = []
    for match in CHAP_RE.finditer(markdown):
        body = _strip_markers(match.group(2)).strip()
        if body:
            chapters.append({"id": match.group(1), "body": body})
    return chapters


def _parse_book_markdown(markdown: str) -> dict[str, Any]:
    title = ""
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
    chapters = _split_chapters(markdown)
    return {"title": title, "chapters": chapters}


def _md_to_html(text: str) -> str:
    if _md is not None:
        return _md.render(text).strip()
    lines = []
    for para in text.strip().split("\n\n"):
        para = para.strip()
        if not para:
            continue
        lines.append(f"<p>{para}</p>")
    return "\n".join(lines)


def _chapter_title(chapter_id: str, blueprint: dict[str, Any]) -> str:
    for ch in blueprint.get("chapters", []):
        if ch.get("id") == chapter_id:
            title = ch.get("title", "")
            if title:
                return title
    num = chapter_id.removeprefix("chapter_")
    return f"Chapter {int(num)}"


CSS = """\
body {
    font-family: Georgia, 'Times New Roman', serif;
    line-height: 1.8;
    max-width: 38em;
    margin: 0 auto;
    padding: 1em 1.5em 3em;
    color: #1a1a1a;
}
.title-page {
    text-align: center;
    margin: 4em 0 3em;
    page-break-after: always;
}
.title-page h1 {
    font-size: 2.5em;
    margin-bottom: 0.3em;
    line-height: 1.2;
}
.title-page .author {
    font-size: 1.3em;
    color: #555;
}
.title-page .publisher-line {
    margin-top: 2em;
    font-size: 0.9em;
    color: #888;
}
nav#toc {
    margin: 2em 0 3em;
    page-break-after: always;
}
nav#toc h2 {
    text-align: center;
    font-size: 1.6em;
    margin-bottom: 1em;
}
nav#toc ul {
    list-style: none;
    padding: 0;
}
nav#toc li {
    margin: 0.4em 0;
    font-size: 1.1em;
}
nav#toc a {
    text-decoration: none;
    color: #1a1a1a;
}
nav#toc a:hover {
    text-decoration: underline;
}
.chapter {
    margin-top: 2em;
    page-break-before: always;
}
.chapter h2 {
    text-align: center;
    font-size: 1.5em;
    margin: 1em 0 0.5em;
}
.chapter h3 {
    font-size: 1.2em;
    margin: 1.2em 0 0.4em;
}
.chapter p {
    margin: 0 0 0.8em;
    text-indent: 1.5em;
}
.chapter p:first-of-type {
    text-indent: 0;
}
.chapter hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 1.5em auto;
    width: 25%;
}
.section-separator {
    text-align: center;
    margin: 1.5em 0;
    color: #999;
    font-size: 0.9em;
}"""


def _render_html_inner(
    snapshot: "PublishingSnapshot",
    *,
    title_page: bool = True,
    toc: bool = True,
    css: str | None = None,
) -> str:
    parsed = snapshot._parsed
    style = css if css is not None else CSS
    title = snapshot.title
    author = snapshot.author
    parts: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{title}</title>",
        f"<style>{style}</style>",
        "</head>",
        "<body>",
    ]

    if title_page:
        parts.append('<div class="title-page">')
        parts.append(f"<h1>{_escape_html(title)}</h1>")
        parts.append(f'<p class="author">{_escape_html(author)}</p>')
        parts.append(
            '<p class="publisher-line">'
            f"Generated by Auteur &mdash; {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
            "</p>"
        )
        parts.append("</div>")

    if toc:
        parts.append('<nav id="toc">')
        parts.append("<h2>Contents</h2>")
        parts.append("<ul>")
        for ch in parsed["chapters"]:
            ch_title = _chapter_title(ch["id"], snapshot._blueprint)
            parts.append(
                f'<li><a href="#ch-{ch["id"]}">{_escape_html(ch_title)}</a></li>'
            )
        parts.append("</ul></nav>")

    for ch in parsed["chapters"]:
        ch_title = _chapter_title(ch["id"], snapshot._blueprint)
        body_html = _md_to_html(ch["body"])
        parts.append(f'<div class="chapter" id="ch-{ch["id"]}">')
        parts.append(f"<h2>{_escape_html(ch_title)}</h2>")
        parts.append(body_html)
        parts.append("</div>")

    parts.append("</body></html>")
    return "\n".join(parts)


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_epub_archive(
    snapshot: "PublishingSnapshot",
    output: Path,
    *,
    css: str | None = None,
) -> dict[str, Any]:
    parsed = snapshot._parsed
    title = snapshot.title
    author = snapshot.author
    style = css if css is not None else CSS
    uid = f"urn:uuid:{_sha256(title + author + snapshot._manifest['book_expression_id'])[:36]}"

    chapters_html: list[dict[str, str]] = []
    for i, ch in enumerate(parsed["chapters"], 1):
        ch_title = _chapter_title(ch["id"], snapshot._blueprint)
        body_html = _md_to_html(ch["body"])
        file_name = f"chapter_{i:02d}.xhtml"
        content = _epub_chapter_xhtml(ch_title, body_html, uid, i)
        chapters_html.append({"id": ch["id"], "title": ch_title, "file": file_name, "content": content})

    with ZipFile(output, "w", ZIP_DEFLATED) as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=ZIP_DEFLATED)
        zf.writestr("META-INF/container.xml", _epub_container_xml())
        zf.writestr("OEBPS/stylesheet.css", style)
        zf.writestr("OEBPS/content.opf", _epub_opf_xml(title, author, uid, chapters_html))
        zf.writestr("OEBPS/nav.xhtml", _epub_nav_xhtml(title, chapters_html, uid))
        for ch in chapters_html:
            zf.writestr(f"OEBPS/{ch['file']}", ch["content"])

    return {
        "format": "epub",
        "version": 1,
        "output_path": str(output.resolve()),
        "output_hash": _sha256(output.read_bytes().decode("latin-1")),
        "chapter_count": len(chapters_html),
    }


def _epub_container_xml() -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '  <rootfiles>\n'
        '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
        "  </rootfiles>\n"
        "</container>\n"
    )


def _epub_opf_xml(
    title: str, author: str, uid: str, chapters: list[dict[str, str]]
) -> str:
    items_xml = '\n'.join(
        f'    <item id="ch{i}" href="{ch["file"]}" media-type="application/xhtml+xml"/>'
        for i, ch in enumerate(chapters, 1)
    )
    refs_xml = '\n'.join(
        f'    <itemref idref="ch{i}"/>'
        for i in range(1, len(chapters) + 1)
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="book-id">\n'
        f'  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f'    <dc:identifier id="book-id">{uid}</dc:identifier>\n'
        f'    <dc:title>{_escape_html(title)}</dc:title>\n'
        f'    <dc:creator>{_escape_html(author)}</dc:creator>\n'
        f'    <dc:language>en</dc:language>\n'
        f'    <meta property="dcterms:modified">{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}</meta>\n'
        f'  </metadata>\n'
        f'  <manifest>\n'
        f'    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>\n'
        f'    <item id="css" href="stylesheet.css" media-type="text/css"/>\n'
        f'{items_xml}\n'
        f'  </manifest>\n'
        f'  <spine>\n'
        f'{refs_xml}\n'
        f'  </spine>\n'
        f'</package>\n'
    )


def _epub_nav_xhtml(title: str, chapters: list[dict[str, str]], uid: str) -> str:
    items_li = "\n".join(
        f'      <li><a href="{ch["file"]}">{_escape_html(ch["title"])}</a></li>'
        for ch in chapters
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
        "<head>\n"
        f'  <title>{_escape_html(title)}</title>\n'
        "</head>\n"
        "<body>\n"
        '  <nav epub:type="toc">\n'
        f"    <h1>{_escape_html(title)}</h1>\n"
        "    <ol>\n"
        f"{items_li}\n"
        "    </ol>\n"
        "  </nav>\n"
        "</body>\n"
        "</html>\n"
    )


def _epub_chapter_xhtml(title: str, body_html: str, uid: str, position: int) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml">\n'
        "<head>\n"
        f'  <title>{_escape_html(title)}</title>\n'
        '  <link rel="stylesheet" type="text/css" href="stylesheet.css"/>\n'
        "</head>\n"
        "<body>\n"
        f'  <div class="chapter">\n'
        f"    <h2>{_escape_html(title)}</h2>\n"
        f"    {body_html}\n"
        f"  </div>\n"
        "</body>\n"
        "</html>\n"
    )


class PublishingSnapshot:
    """Immutable snapshot of accepted Book state for publishing.

    Reads the accepted Book Expression, captures its manifest and manuscript,
    and provides render methods for publication formats.
    """

    def __init__(self, project: Path) -> None:
        self._project = Path(project)
        self._manifest = _read_accepted_book_manifest(self._project)
        self._markdown = _read_book_markdown(self._project, self._manifest)
        self._book_hash = _sha256(self._markdown)
        self._parsed = _parse_book_markdown(self._markdown)
        self._identity = self._read_identity()
        self._blueprint = self._read_blueprint()
        raw = self._manifest["book_expression_id"] + str(self._manifest["revision"]) + self._book_hash
        self._snapshot_id = "pub_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    @property
    def title(self) -> str:
        return self._identity.get("title") or self._parsed["title"] or "Untitled"

    @property
    def author(self) -> str:
        return self._identity.get("author") or "Unknown Author"

    def _read_identity(self) -> dict[str, Any]:
        path = self._project / "story_identity.yaml"
        if path.exists():
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return {}

    def _read_blueprint(self) -> dict[str, Any]:
        path = self._project / "blueprint.yaml"
        if path.exists():
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return {}

    def render_html(
        self,
        output: Path,
        *,
        title_page: bool = True,
        toc: bool = True,
        css: str | None = None,
    ) -> dict[str, Any]:
        output = Path(output)
        if output.exists():
            raise FileExistsError(f"output already exists: {output}")
        html = _render_html_inner(self, title_page=title_page, toc=toc, css=css)
        output.write_text(html, encoding="utf-8")
        return {
            "format": "html",
            "version": 1,
            "output_path": str(output.resolve()),
            "output_hash": _sha256(html),
        }

    def render_epub(
        self,
        output: Path,
        *,
        css: str | None = None,
    ) -> dict[str, Any]:
        output = Path(output)
        if output.exists():
            raise FileExistsError(f"output already exists: {output}")
        return _build_epub_archive(self, output, css=css)

    def _immutable_snapshot(self) -> dict[str, Any]:
        """Source book state only — no renderer results or timestamps.
        This is the immutable publication identity, written once.
        """
        chapters = [
            {
                "id": ch["id"],
                "position": i + 1,
                "title": _chapter_title(ch["id"], self._blueprint),
            }
            for i, ch in enumerate(self._parsed["chapters"])
        ]
        return {
            "snapshot_id": self._snapshot_id,
            "artifact_type": "book_publishing_snapshot",
            "authority": "derived",
            "lifecycle": "published",
            "source_book": {
                "book_expression_id": self._manifest["book_expression_id"],
                "revision": self._manifest["revision"],
                "content_hash": self._book_hash,
            },
            "title": self.title,
            "author": self.author,
            "chapters": chapters,
            "reproducibility": {
                "auteur_version": "0.1.0",
                "markdown_it_version": str(getattr(_md, "VERSION", "0") if _md else "0"),
                "python_implementation": "cpython",
            },
        }

    def _run_record(self, renderer_results: list[dict[str, Any]]) -> dict[str, Any]:
        """A specific publish invocation: which snapshot + renderer results + timestamp."""
        return {
            "run_type": "publishing_run",
            "snapshot_id": self._snapshot_id,
            "source_book": {
                "book_expression_id": self._manifest["book_expression_id"],
                "revision": self._manifest["revision"],
                "content_hash": self._book_hash,
            },
            "title": self.title,
            "author": self.author,
            "formats": [r["format"] for r in renderer_results],
            "renderers": renderer_results,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def save_snapshot(
        self,
        renderer_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        snapshot_dir = self._project / ".auteur" / "publishing"
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Immutable snapshot: source book state, written ONCE (never overwritten).
        snap_path = snapshot_dir / f"{self._snapshot_id}.yaml"
        if not snap_path.exists():
            snap_path.write_text(
                yaml.safe_dump(self._immutable_snapshot(), sort_keys=False),
                encoding="utf-8",
            )

        # Run record: this specific publish invocation.
        run = self._run_record(renderer_results)
        runs_dir = snapshot_dir / "runs"
        runs_dir.mkdir(exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        uid = uuid.uuid4().hex[:8]
        run_path = runs_dir / f"run_{ts}_{uid}.yaml"
        run_path.write_text(yaml.safe_dump(run, sort_keys=False), encoding="utf-8")

        # Convenience pointer to the latest run (overwritten each time).
        latest = snapshot_dir / "latest.yaml"
        latest.write_text(yaml.safe_dump(run, sort_keys=False), encoding="utf-8")
        return run


def publish(
    project: Path,
    *,
    formats: list[Format] | None = None,
    output_dir: Path | None = None,
    html_output: Path | None = None,
    epub_output: Path | None = None,
    css: str | None = None,
    title_page: bool = True,
    toc: bool = True,
) -> dict[str, Any]:
    if formats is None:
        formats = ["html"]

    snapshot = PublishingSnapshot(project)
    renderer_results: list[dict[str, Any]] = []

    for fmt in formats:
        fmt = fmt.lower()
        if fmt not in ALL_FORMATS:
            raise PublishError(f"unknown format: {fmt!r} (choose from {ALL_FORMATS})")

        if fmt == "html":
            out = html_output
            if out is None:
                out = (output_dir or project) / "book.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            renderer_results.append(
                snapshot.render_html(out, title_page=title_page, toc=toc, css=css)
            )

        elif fmt == "epub":
            out = epub_output
            if out is None:
                out = (output_dir or project) / "book.epub"
            out.parent.mkdir(parents=True, exist_ok=True)
            renderer_results.append(snapshot.render_epub(out, css=css))

    snapshot.save_snapshot(renderer_results)
    return {
        "snapshot_id": snapshot._snapshot_id,
        "title": snapshot.title,
        "author": snapshot.author,
        "source_revision": snapshot._manifest["revision"],
        "renderers": renderer_results,
    }
