"""Project — directory-backed wrapper around a StoryBlueprint and StoryBible.

A project is a directory:
    project/
      blueprint.yaml
      bible.json
      chapters/01/{outline.yaml,draft_v1.md,validation_v1.json,...,final.md}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from auteur.bible import StoryBible
from auteur.blueprint import StoryBlueprint


class Project:
    def __init__(self, path: Path, blueprint: StoryBlueprint, bible: StoryBible):
        self.path = path
        self.blueprint = blueprint
        self.bible = bible

    @classmethod
    def init(cls, path: Path, blueprint: StoryBlueprint) -> "Project":
        if path.exists():
            raise FileExistsError(f"Project path already exists: {path}")
        path.mkdir(parents=True)
        (path / "chapters").mkdir()
        (path / "blueprint.yaml").write_text(
            yaml.safe_dump(blueprint.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        bible = StoryBible(path / "bible.json")
        return cls(path, blueprint, bible)

    @classmethod
    def load(cls, path: Path) -> "Project":
        if not path.is_dir():
            raise FileNotFoundError(f"Project path is not a directory: {path}")
        blueprint = StoryBlueprint.from_yaml(path / "blueprint.yaml")
        bible = StoryBible(path / "bible.json")
        return cls(path, blueprint, bible)

    def chapter_dir(self, n: int) -> Path:
        d = self.path / "chapters" / f"{n:02d}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def next_draft_version(self, n: int) -> int:
        existing = list(self.chapter_dir(n).glob("draft_v*.md"))
        if not existing:
            return 1
        versions = [int(p.stem.removeprefix("draft_v")) for p in existing]
        return max(versions) + 1

    def write_outline(self, n: int, outline: dict[str, Any]) -> Path:
        path = self.chapter_dir(n) / "outline.yaml"
        path.write_text(yaml.safe_dump(outline, sort_keys=False), encoding="utf-8")
        return path

    def write_draft(self, n: int, version: int, prose: str) -> Path:
        path = self.chapter_dir(n) / f"draft_v{version}.md"
        path.write_text(prose, encoding="utf-8")
        return path

    def write_validation(self, n: int, version: int, report: Any) -> Path:
        path = self.chapter_dir(n) / f"validation_v{version}.json"
        if hasattr(report, "model_dump"):
            payload = report.model_dump(mode="json")
        else:
            payload = report
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def write_final(self, n: int, prose: str) -> Path:
        path = self.chapter_dir(n) / "final.md"
        path.write_text(prose, encoding="utf-8")
        return path

    def has_final(self, n: int) -> bool:
        return (self.chapter_dir(n) / "final.md").exists()
