from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

from auteur.provenance import ArtifactStore, Lifecycle, ReviewState

MARKER_RE = re.compile(r"^<!-- auteur:scene id=([^ ]+) expression_revision=(\d+) -->$")
END_MARKER_RE = re.compile(r"^<!-- auteur:end-scene id=([^ ]+) -->$")


class ChapterExpression(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_type: str = "expression_chapter"
    revision: int
    lifecycle: Lifecycle = Lifecycle.DRAFT
    authority: str = "derived"
    review_state: ReviewState = ReviewState.NONE
    source_chapter: dict[str, Any]
    source_scenes: list[dict[str, Any]]
    transitions: list[dict[str, Any]] = Field(default_factory=list)
    section_map: list[dict[str, Any]]
    content_hash: str
    transformation: dict[str, Any]
    validation_findings: list[dict[str, Any]] = Field(default_factory=list)
    accepted_at: str | None = None
    accepted_by: str | None = None


def _hash_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


class ChapterExpressionStore:
    """Focused deterministic assembly of accepted Scene Expressions."""

    def __init__(self, project: Path):
        self.project = Path(project)

    def chapter_id(self, chapter: str | int) -> str:
        value = str(chapter)
        return value if value.startswith("chapter_") else f"chapter_{int(value):02d}"

    def chapter_dir(self, chapter: str | int) -> Path:
        identifier = self.chapter_id(chapter)
        number = identifier.removeprefix("chapter_")
        return self.project / "chapters" / number / "expression"

    def _chapter_outline(self, chapter: str | int) -> Path:
        identifier = self.chapter_id(chapter)
        number = identifier.removeprefix("chapter_")
        candidates = [
            self.project / f"{identifier}.yaml",
            self.project / f"{number}.yaml",
            self.project / "chapters" / number / "outline.yaml",
        ]
        for path in candidates:
            if path.exists():
                return path
        raise FileNotFoundError(f"Chapter Structure not found for {identifier}")

    def _scene_path(self, scene_id: str) -> Path:
        matches = list(self.project.glob(f"chapters/*/scenes/{scene_id}.yaml"))
        if not matches:
            matches = list(self.project.glob(f"**/{scene_id}.yaml"))
        if not matches:
            raise FileNotFoundError(f"Scene Realization not found: {scene_id}")
        return matches[0]

    def _accepted_scene(self, scene_id: str) -> tuple[dict[str, Any], Path]:
        scene = self._scene_path(scene_id)
        accepted = scene.parent / scene.stem / "accepted.yaml"
        if not accepted.exists():
            raise ValueError(f"Scene has no accepted Expression: {scene_id}")
        metadata = yaml.safe_load(accepted.read_text(encoding="utf-8")) or {}
        if metadata.get("lifecycle") != Lifecycle.ACCEPTED.value:
            raise ValueError(f"Scene Expression is not accepted: {scene_id}")
        candidate = scene.parent / scene.stem / f"prose_v{int(metadata['revision']):03d}.md"
        if not candidate.exists():
            candidate = next((item for item in scene.parent.joinpath(scene.stem).glob("prose_v*.md") if item.stem.endswith(f"{int(metadata['revision']):03d}")), None)
        if candidate is None or not candidate.exists():
            raise ValueError(f"Accepted Scene prose is missing: {scene_id}")
        return metadata, candidate

    @staticmethod
    def _scene_order(raw: dict[str, Any]) -> list[str]:
        values = raw.get("scenes") or raw.get("scene_ids") or raw.get("ordered_scenes")
        if not values:
            raise ValueError("Chapter Structure has no Scene order")
        result = []
        for value in values:
            result.append(str(value.get("id") if isinstance(value, dict) else value))
        if any(not value for value in result) or len(set(result)) != len(result):
            raise ValueError("Chapter Structure contains invalid or duplicate Scene IDs")
        return result

    def _next_revision(self, chapter: str | int) -> int:
        versions = [int(match.group(1)) for path in self.chapter_dir(chapter).glob("chapter_v*.yaml") if (match := re.fullmatch(r"chapter_v(\d+)", path.stem))]
        return max(versions, default=0) + 1

    def _metadata_path(self, expression_id: str) -> Path:
        for path in self.project.glob("chapters/*/expression/chapter_v*.yaml"):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if data.get("artifact_id") == expression_id:
                return path
        raise FileNotFoundError(f"Chapter Expression not found: {expression_id}")

    def inspect(self, expression_id: str) -> ChapterExpression:
        path = self._metadata_path(expression_id)
        return ChapterExpression.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

    def _current_status(self, metadata: ChapterExpression) -> dict[str, Any]:
        stale_reasons: list[dict[str, Any]] = []
        chapter_path = self._chapter_outline(metadata.source_chapter["artifact_id"])
        chapter_store = ArtifactStore(self.project)
        chapter_status = chapter_store.status(chapter_path, "chapter_outline")
        if chapter_status.revision != metadata.source_chapter["revision"] or chapter_store.content_hash(chapter_path) != metadata.source_chapter["content_hash"]:
            stale_reasons.append({"code": "chapter_structure_changed", "message": "Chapter Structure changed"})
        for item in metadata.source_scenes:
            try:
                scene_meta, _ = self._accepted_scene(item["scene_id"])
                scene_path = self._scene_path(item["scene_id"])
                scene_status = chapter_store.status(scene_path, "scene_realization")
                if scene_meta.get("revision") != item["expression_revision"] or scene_meta.get("content_hash") != item["expression_content_hash"]:
                    stale_reasons.append({"code": "scene_expression_changed", "scene_id": item["scene_id"], "message": f"Selected Expression changed for {item['scene_id']}"})
                if scene_status.revision != item["source_scene_revision"] or chapter_store.content_hash(scene_path) != item["source_scene_content_hash"]:
                    stale_reasons.append({"code": "scene_realization_changed", "scene_id": item["scene_id"], "message": f"Scene Realization changed for {item['scene_id']}"})
            except (FileNotFoundError, ValueError) as exc:
                stale_reasons.append({"code": "scene_dependency_unavailable", "scene_id": item["scene_id"], "message": str(exc)})
        return {"freshness": "stale" if stale_reasons else "fresh", "review_state": metadata.review_state.value, "lifecycle": metadata.lifecycle.value, "stale_reasons": stale_reasons, "health": "invalid" if metadata.validation_findings else "valid"}

    def status(self, expression_id: str) -> dict[str, Any]:
        return {"artifact_id": expression_id, **self._current_status(self.inspect(expression_id))}

    def compose(self, chapter: str | int, *, transitions: dict[str, dict[str, Any]] | None = None) -> ChapterExpression:
        outline_path = self._chapter_outline(chapter)
        chapter_store = ArtifactStore(self.project)
        outline_status = chapter_store.status(outline_path, "chapter_outline")
        if outline_status.lifecycle is not Lifecycle.ACCEPTED or outline_status.health != "valid":
            raise ValueError("Chapter Structure must be accepted and valid")
        raw = yaml.safe_load(outline_path.read_text(encoding="utf-8")) or {}
        scene_ids = self._scene_order(raw)
        selected: list[dict[str, Any]] = []
        sections: list[dict[str, Any]] = []
        chunks: list[str] = []
        transition_data = []
        review_required = False
        transitions = transitions or {}
        for index, scene_id in enumerate(scene_ids):
            scene_meta, prose_path = self._accepted_scene(scene_id)
            from auteur.expression.pilot import ExpressionStore
            expression_status = ExpressionStore(self.project).status(scene_meta["candidate_id"])
            if expression_status["health"] != "valid":
                raise ValueError(f"Scene Expression is invalid: {scene_id}")
            if expression_status["freshness"] == "stale" and expression_status["review_state"] != ReviewState.ACKNOWLEDGED_DIVERGENCE.value:
                raise ValueError(f"Scene Expression requires review: {scene_id}")
            scene_freshness = "divergent" if expression_status["review_state"] == ReviewState.ACKNOWLEDGED_DIVERGENCE.value else "fresh"
            review_required = review_required or scene_freshness == "divergent"
            scene_path = self._scene_path(scene_id)
            scene_status = chapter_store.status(scene_path, "scene_realization")
            if scene_status.health != "valid":
                raise ValueError(f"Scene Realization is invalid: {scene_id}")
            prose = prose_path.read_text(encoding="utf-8")
            selected.append({"scene_id": scene_id, "expression_candidate_id": scene_meta["candidate_id"], "expression_revision": int(scene_meta["revision"]), "expression_content_hash": scene_meta["content_hash"], "source_scene_revision": scene_status.revision, "source_scene_content_hash": chapter_store.content_hash(scene_path), "freshness": scene_freshness, "review_state": scene_meta.get("review_state", "none")})
            start = f"<!-- auteur:scene id={scene_id} expression_revision={int(scene_meta['revision'])} -->"
            end = f"<!-- auteur:end-scene id={scene_id} -->"
            chunks.extend([start, prose.rstrip(), end])
            sections.append({"section_id": scene_id, "kind": "scene", "expression_revision": int(scene_meta["revision"])})
            if index < len(scene_ids) - 1:
                key = f"{scene_id}->{scene_ids[index + 1]}"
                transition = transitions.get(key)
                if transition:
                    if transition.get("before_scene") != scene_id or transition.get("after_scene") != scene_ids[index + 1]:
                        raise ValueError(f"transition references invalid Scene boundary: {key}")
                    text = str(transition.get("text", "")).strip()
                    item = {"transition_id": transition.get("transition_id", f"transition_{scene_id}_{scene_ids[index + 1]}"), "before_scene": scene_id, "after_scene": scene_ids[index + 1], "revision": int(transition.get("revision", 1)), "lifecycle": transition.get("lifecycle", "accepted"), "text": text, "content_hash": _hash_text(text)}
                    transition_data.append(item)
                    chunks.append(text)
                    sections.append({"section_id": item["transition_id"], "kind": "transition", "before_scene": scene_id, "after_scene": scene_ids[index + 1]})
                else:
                    chunks.append("")
        text = "\n".join(chunks).rstrip() + "\n"
        revision = self._next_revision(chapter)
        artifact_id = f"{self.chapter_id(chapter)}:expression_v{revision:03d}"
        metadata = ChapterExpression(artifact_id=artifact_id, revision=revision, review_state=ReviewState.REVIEW_REQUIRED if review_required else ReviewState.NONE, source_chapter={"artifact_id": self.chapter_id(chapter), "revision": outline_status.revision, "content_hash": chapter_store.content_hash(outline_path)}, source_scenes=selected, transitions=transition_data, section_map=sections, content_hash=_hash_text(text), transformation={"id": "expression.compose_chapter", "version": 1, "executor": "deterministic"})
        directory = self.chapter_dir(chapter)
        directory.mkdir(parents=True, exist_ok=True)
        md_path, yaml_path = directory / f"chapter_v{revision:03d}.md", directory / f"chapter_v{revision:03d}.yaml"
        md_tmp = md_path.with_name(md_path.name + ".tmp")
        yaml_tmp = yaml_path.with_name(yaml_path.name + ".tmp")
        try:
            md_tmp.write_text(text, encoding="utf-8")
            yaml_tmp.write_text(yaml.safe_dump(metadata.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
            md_tmp.replace(md_path)
            yaml_tmp.replace(yaml_path)
        except Exception:
            for path in (md_tmp, yaml_tmp):
                if path.exists(): path.unlink()
            raise
        return metadata

    def accept(self, expression_id: str, *, accepted_by: str = "author", allow_review: bool = False) -> ChapterExpression:
        metadata = self.inspect(expression_id)
        status = self.status(expression_id)
        if status["health"] != "valid":
            raise ValueError("cannot accept invalid Chapter Expression")
        if status["freshness"] == "stale":
            raise ValueError("cannot accept stale Chapter Expression")
        if metadata.review_state is not ReviewState.NONE and not allow_review:
            raise ValueError("Chapter Expression requires explicit review acknowledgement")
        prior = self.chapter_dir(metadata.source_chapter["artifact_id"]) / "accepted.yaml"
        if prior.exists():
            previous = ChapterExpression.model_validate(yaml.safe_load(prior.read_text(encoding="utf-8")))
            previous.lifecycle = Lifecycle.REPLACED
            self._metadata_path(previous.artifact_id).write_text(yaml.safe_dump(previous.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
        metadata.lifecycle = Lifecycle.ACCEPTED
        metadata.accepted_by = accepted_by
        metadata.accepted_at = datetime.now(timezone.utc).isoformat()
        path = self._metadata_path(expression_id)
        path.write_text(yaml.safe_dump(metadata.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
        prior.write_text(yaml.safe_dump(metadata.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
        return metadata

    def clean_export(self, expression_id: str) -> str:
        metadata = self.inspect(expression_id)
        path = self._metadata_path(expression_id).with_suffix(".md")
        text = path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if not MARKER_RE.match(line) and not END_MARKER_RE.match(line)]
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def inspect_markers(text: str) -> dict[str, Any]:
        """Inspect internal markers without attempting semantic reconstruction."""
        findings: list[dict[str, str]] = []
        scenes: list[str] = []
        open_scene: str | None = None
        for line in text.splitlines():
            start = MARKER_RE.match(line)
            end = END_MARKER_RE.match(line)
            if start:
                scene_id = start.group(1)
                if open_scene is not None or scene_id in scenes:
                    findings.append({"code": "ambiguous_marker", "message": f"duplicate or nested Scene marker: {scene_id}"})
                scenes.append(scene_id)
                open_scene = scene_id
            elif end:
                if open_scene != end.group(1):
                    findings.append({"code": "ambiguous_marker", "message": f"unmatched Scene end marker: {end.group(1)}"})
                open_scene = None
        if open_scene is not None:
            findings.append({"code": "missing_marker", "message": f"missing end marker for {open_scene}"})
        if not scenes:
            findings.append({"code": "unresolved_divergence", "message": "Chapter prose has no stable Scene markers"})
        return {"scene_ids": scenes, "findings": findings, "status": "unresolved_divergence" if findings else "mapped"}
