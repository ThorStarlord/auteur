"""Deterministic, provenance-rich Book Manuscript assembly."""

from __future__ import annotations

import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
import re

from auteur.expression.composition import ChapterExpressionStore
from auteur.provenance import Lifecycle


def _hash(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


class BookPreviewNotAcceptableError(ValueError):
    """Raised when a derived/proposed artifact (such as an application preview)
    is submitted for Book acceptance.

    Acceptance is reserved for canonical, accepted Book content. Previews are
    derived and proposed by construction, so blocking is expressed as explicit
    metadata validation rather than an incidental path lookup failure.
    """


class BookExpressionStore:
    """Own Book ordering and assembly, never Chapter content or authority."""

    def __init__(self, project: Path, *, book_id: str = "book_01") -> None:
        self.project = Path(project)
        self.book_id = book_id
        self.directory = self.project / "book" / "expression"
        self.structure_path = self.project / "book" / "structure.yaml"

    def _path(self, revision: int, suffix: str) -> Path:
        return self.directory / f"book_v{revision:03d}.{suffix}"

    def _next_revision(self) -> int:
        versions = [int(path.stem.removeprefix("book_v")) for path in self.directory.glob("book_v*.yaml")]
        return max(versions, default=0) + 1

    def _load(self, expression_id: str) -> dict[str, Any]:
        for path in self.directory.glob("book_v*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("book_expression_id") == expression_id:
                return data
        raise FileNotFoundError(f"Book Manuscript not found: {expression_id}")

    def _accepted_chapter(self, chapter_id: str) -> dict[str, Any]:
        path = next(self.project.glob(f"chapters/*/expression/accepted.yaml"), None)
        matches = []
        for candidate in self.project.glob("chapters/*/expression/accepted.yaml"):
            data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
            if data.get("source_chapter", {}).get("artifact_id") == chapter_id:
                matches.append(data)
        if not matches:
            raise ValueError(f"Chapter has no accepted Chapter Expression: {chapter_id}")
        chapter = matches[-1]
        if chapter.get("lifecycle") != Lifecycle.ACCEPTED.value:
            raise ValueError(f"Chapter Expression is not accepted: {chapter_id}")
        return chapter

    def _chapter_text(self, chapter: dict[str, Any]) -> str:
        store = ChapterExpressionStore(self.project)
        return store.clean_export(chapter["artifact_id"]).strip()

    def compose(self, chapter_ids: list[str], *, title: str = "", separator: str = "---") -> dict[str, Any]:
        if not chapter_ids or len(set(chapter_ids)) != len(chapter_ids):
            raise ValueError("Book Chapter ordering must be non-empty and unique")
        chapters = [self._accepted_chapter(chapter_id) for chapter_id in chapter_ids]
        sections = []
        references = []
        for position, chapter in enumerate(chapters, 1):
            references.append({
                "chapter_id": chapter["source_chapter"]["artifact_id"],
                "chapter_expression_id": chapter["artifact_id"],
                "accepted_revision": chapter["revision"],
                "content_hash": chapter["content_hash"],
                "position": position,
            })
            sections.append(f"<!-- auteur:chapter id={chapter['source_chapter']['artifact_id']} expression_revision={chapter['revision']} -->\n{self._chapter_text(chapter)}\n<!-- auteur:end-chapter id={chapter['source_chapter']['artifact_id']} -->")
        text = f"# {title}\n\n" if title else ""
        pieces = []
        for index, section in enumerate(sections):
            if index:
                pieces.append(f"<!-- auteur:book-separator id=separator_{index:02d} revision=1 -->\n{separator}\n<!-- auteur:end-book-separator id=separator_{index:02d} -->")
            pieces.append(section)
        text += "\n\n".join(pieces) + "\n"
        revision = self._next_revision()
        expression_id = f"{self.book_id}:expression_v{revision:03d}"
        manifest = {
            "book_expression_id": expression_id, "book_id": self.book_id,
            "revision": revision, "authority": "derived", "lifecycle": "proposed",
            "freshness": "fresh", "chapters": references,
            "book_owned_content": {"title": title, "separator": separator},
            "transformation": {"id": "expression.compose_book", "version": 1},
            "dependencies": references, "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.directory.mkdir(parents=True, exist_ok=True)
        yaml_path, md_path = self._path(revision, "yaml"), self._path(revision, "md")
        yaml_tmp, md_tmp = yaml_path.with_suffix(".yaml.tmp"), md_path.with_suffix(".md.tmp")
        try:
            md_tmp.write_text(text, encoding="utf-8")
            yaml_tmp.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            md_tmp.replace(md_path); yaml_tmp.replace(yaml_path)
            self.structure_path.parent.mkdir(parents=True, exist_ok=True)
            self.structure_path.write_text(yaml.safe_dump({"book_id": self.book_id, "chapters": chapter_ids}, sort_keys=False), encoding="utf-8")
        except Exception:
            for path in (md_tmp, yaml_tmp):
                if path.exists(): path.unlink()
            raise
        return manifest

    def inspect(self, expression_id: str) -> dict[str, Any]:
        manifest = self._load(expression_id)
        current_order = yaml.safe_load(self.structure_path.read_text(encoding="utf-8")).get("chapters", []) if self.structure_path.exists() else [item["chapter_id"] for item in manifest["chapters"]]
        stale_sources = []
        for item in manifest["chapters"]:
            try:
                current = self._accepted_chapter(item["chapter_id"])
            except ValueError as exc:
                stale_sources.append({"chapter_id": item["chapter_id"], "reason": str(exc)})
                continue
            if current["revision"] != item["accepted_revision"] or current["content_hash"] != item["content_hash"]:
                stale_sources.append({"chapter_id": item["chapter_id"], "expected_revision": item["accepted_revision"], "current_revision": current["revision"], "reason": "accepted Chapter Expression changed"})
        if current_order != [item["chapter_id"] for item in manifest["chapters"]]:
            stale_sources.append({"reason": "Chapter order changed", "expected_order": [item["chapter_id"] for item in manifest["chapters"]], "current_order": current_order})
        manifest["freshness"] = "stale" if stale_sources else "fresh"
        return {"metadata": manifest, "freshness": manifest["freshness"], "stale_sources": stale_sources, "recommended_action": "recompose the Book Manuscript" if stale_sources else "none"}

    def _validate_acceptable_artifact(self, artifact: dict[str, Any]) -> None:
        """Explicitly reject artifacts that can never become accepted Book content.

        Metadata-driven (not path-based): an acceptable artifact must be
        ``authority == 'accepted'``, must not be an ``application_preview`` role,
        and must be ``lifecycle == 'accepted'``. A derived, proposed preview
        fails every one of these, so it is blocked with an explicit message
        instead of an incidental ``FileNotFoundError``.
        """
        message = (
            "Previews are derived and proposed; they cannot become canonical "
            "accepted Book content."
        )
        if artifact.get("authority") != "accepted":
            raise BookPreviewNotAcceptableError(message)
        if artifact.get("role") == "application_preview":
            raise BookPreviewNotAcceptableError(message)
        if artifact.get("lifecycle") != "accepted":
            raise BookPreviewNotAcceptableError(message)

    def accept(self, expression_id: Any, *, accepted_by: str = "author") -> dict[str, Any]:
        if isinstance(expression_id, dict):
            # A full artifact dict was supplied directly (for example a preview).
            # Validate its metadata explicitly before any disk lookup so a
            # derived/proposed artifact is blocked with a precise error.
            self._validate_acceptable_artifact(expression_id)
            expression_id = expression_id.get("book_expression_id")
        inspected = self.inspect(expression_id)
        if inspected["freshness"] != "fresh":
            raise ValueError("cannot accept stale Book Manuscript")
        manifest = inspected["metadata"]
        accepted_path = self.directory / "accepted.yaml"
        if accepted_path.exists():
            previous = yaml.safe_load(accepted_path.read_text(encoding="utf-8")) or {}
            previous["lifecycle"] = "replaced"
            self._path(previous["revision"], "yaml").write_text(yaml.safe_dump(previous, sort_keys=False), encoding="utf-8")
        manifest.update({"lifecycle": "accepted", "accepted_by": accepted_by, "accepted_at": datetime.now(timezone.utc).isoformat()})
        self._path(manifest["revision"], "yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        accepted_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
        return manifest

    def compare(self, first_id: str, second_id: str) -> dict[str, Any]:
        first, second = self._load(first_id), self._load(second_id)
        a, b = [item["chapter_id"] for item in first["chapters"]], [item["chapter_id"] for item in second["chapters"]]
        by_a, by_b = {item["chapter_id"]: item for item in first["chapters"]}, {item["chapter_id"]: item for item in second["chapters"]}
        first_text, second_text = self._path(first["revision"], "md").read_text(encoding="utf-8"), self._path(second["revision"], "md").read_text(encoding="utf-8")
        return {"book_a": first_id, "book_b": second_id, "added_chapters": [x for x in b if x not in a], "removed_chapters": [x for x in a if x not in b], "order_changed": a != b, "changed_chapters": [x for x in a if x in by_b and by_a[x]["content_hash"] != by_b[x]["content_hash"]], "separator_changed": first["book_owned_content"] != second["book_owned_content"], "diff": "".join(difflib.unified_diff(first_text.splitlines(True), second_text.splitlines(True), fromfile=first_id, tofile=second_id))}

    def export(self, expression_id: str, output: Path) -> Path:
        output = Path(output)
        if output.exists(): raise FileExistsError(f"output already exists: {output}")
        text = self._path(self._load(expression_id)["revision"], "md").read_text(encoding="utf-8")
        text = re.sub(r"^<!-- auteur:(?:chapter|end-chapter|book-separator|end-book-separator).*?-->\s*$", "", text, flags=re.MULTILINE)
        output.write_text(text, encoding="utf-8")
        return output
