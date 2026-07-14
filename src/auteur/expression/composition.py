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
TRANSITION_MARKER_RE = re.compile(r"^<!-- auteur:transition id=([^ ]+) revision=(\d+) -->$")
END_TRANSITION_MARKER_RE = re.compile(r"^<!-- auteur:end-transition id=([^ ]+) -->$")


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
    transition_source_hash: str | None = None
    source_order: list[str] = Field(default_factory=list)
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

    def _transition_manifest_path(self, chapter: str | int) -> Path:
        return self.chapter_dir(chapter) / "transitions.yaml"

    def save_transitions(self, chapter: str | int, transitions: dict[str, dict[str, Any]]) -> Path:
        path = self._transition_manifest_path(chapter)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(transitions, sort_keys=False), encoding="utf-8")
        return path

    def load_transitions(self, chapter: str | int) -> dict[str, dict[str, Any]]:
        path = self._transition_manifest_path(chapter)
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {} if path.exists() else {}

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
            current_order = self._scene_order(yaml.safe_load(chapter_path.read_text(encoding="utf-8")) or {})
            stale_reasons.append({"code": "chapter_structure_changed", "previous_order": metadata.source_order, "current_order": current_order, "message": "Chapter Structure or Scene order changed"})
        transition_path = self._transition_manifest_path(metadata.source_chapter["artifact_id"])
        if metadata.transition_source_hash and transition_path.exists() and _hash_text(transition_path.read_text(encoding="utf-8")) != metadata.transition_source_hash:
            stale_reasons.append({"code": "transition_changed", "message": "Chapter-owned transition content changed"})
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
        invalid_transition = any(item.get("lifecycle") in {"rejected", "archived"} for item in metadata.transitions)
        return {"freshness": "stale" if stale_reasons else "fresh", "review_state": metadata.review_state.value, "lifecycle": metadata.lifecycle.value, "stale_reasons": stale_reasons, "health": "invalid" if metadata.validation_findings or invalid_transition else "valid"}

    def status(self, expression_id: str) -> dict[str, Any]:
        return {"artifact_id": expression_id, **self._current_status(self.inspect(expression_id))}

    def compose(self, chapter: str | int, *, transitions: dict[str, dict[str, Any]] | None = None, scene_overrides: dict[str, Path] | None = None, persist_transitions: bool = True, transformation: dict[str, Any] | None = None, lifecycle: Lifecycle = Lifecycle.DRAFT, authority: str = "derived") -> ChapterExpression:
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
        if transitions is None:
            transitions = self.load_transitions(chapter)
        transition_findings: list[dict[str, Any]] = []
        valid_keys = {f"{scene_ids[index]}->{scene_ids[index + 1]}" for index in range(len(scene_ids) - 1)}
        transition_by_boundary: dict[str, dict[str, Any]] = {}
        for key, transition in transitions.items():
            boundary = f"{transition.get('before_scene')}->{transition.get('after_scene')}"
            if boundary not in valid_keys:
                raise ValueError(f"invalid Scene boundary for transition {transition.get('transition_id', key)}")
            if transition.get("before_scene") == transition.get("after_scene"):
                raise ValueError(f"transition cannot reference itself: {transition.get('transition_id', key)}")
            transition_by_boundary[boundary] = transition
        transitions = transition_by_boundary
        for index, scene_id in enumerate(scene_ids):
            scene_meta, prose_path = self._accepted_scene(scene_id)
            if scene_overrides and scene_id in scene_overrides:
                prose_path = Path(scene_overrides[scene_id])
                scene_meta = dict(scene_meta)
                candidate_metadata_path = scene_overrides.get(f"__metadata__:{scene_id}")
                if candidate_metadata_path:
                    scene_meta.update(yaml.safe_load(Path(candidate_metadata_path).read_text(encoding="utf-8")) or {})
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
            selected.append({"scene_id": scene_id, "expression_candidate_id": scene_meta["candidate_id"], "expression_revision": int(scene_meta["revision"]), "expression_content_hash": _hash_text(prose_path.read_text(encoding="utf-8")) if scene_overrides and scene_id in scene_overrides else scene_meta["content_hash"], "source_scene_revision": scene_status.revision, "source_scene_content_hash": chapter_store.content_hash(scene_path), "freshness": scene_freshness, "review_state": scene_meta.get("review_state", "none")})
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
                    if transition.get("transition_id") in {item.get("transition_id") for item in transition_data}:
                        raise ValueError(f"duplicate transition ID: {transition['transition_id']}")
                    declared = transition.get("declared_events", [])
                    adjacent_text = " ".join(str((yaml.safe_load(self._scene_path(item).read_text(encoding="utf-8")) or {}).get("outcome", "")) for item in (scene_id, scene_ids[index + 1])).lower()
                    for event in declared:
                        if str(event).lower() not in adjacent_text:
                            transition_findings.append({"code": "unowned_transition_event", "severity": "review_required", "transition_id": transition.get("transition_id"), "message": f"Transition declares an event absent from adjacent Realization: {event}", "recommended_action": "create a Realization proposal or remove the event"})
                    if re.search(r"\b(decided|revealed|killed|stole|met)\b", str(transition.get("text", "")), re.IGNORECASE):
                        transition_findings.append({"code": "likely_unowned_transition_event", "severity": "advisory", "transition_id": transition.get("transition_id"), "message": "Transition prose may introduce a canonical event", "recommended_action": "review transition ownership"})
                    text = str(transition.get("text", "")).strip()
                    item = {"transition_id": transition.get("transition_id", f"transition_{scene_id}_{scene_ids[index + 1]}"), "candidate_id": transition.get("candidate_id"), "before_scene": scene_id, "after_scene": scene_ids[index + 1], "revision": int(transition.get("revision", 1)), "lifecycle": transition.get("lifecycle", "accepted"), "text": text, "content_hash": _hash_text(text)}
                    transition_data.append(item)
                    chunks.extend([f"<!-- auteur:transition id={item['transition_id']} revision={item['revision']} -->", text, f"<!-- auteur:end-transition id={item['transition_id']} -->"])
                    sections.append({"section_id": item["transition_id"], "kind": "transition", "before_scene": scene_id, "after_scene": scene_ids[index + 1]})
                else:
                    chunks.append("")
        text = "\n".join(chunks).rstrip() + "\n"
        revision = self._next_revision(chapter)
        artifact_id = f"{self.chapter_id(chapter)}:expression_v{revision:03d}"
        metadata = ChapterExpression(artifact_id=artifact_id, revision=revision, lifecycle=lifecycle, authority=authority, review_state=ReviewState.REVIEW_REQUIRED if review_required or transition_findings else ReviewState.NONE, source_chapter={"artifact_id": self.chapter_id(chapter), "revision": outline_status.revision, "content_hash": chapter_store.content_hash(outline_path)}, source_scenes=selected, transitions=transition_data, section_map=sections, source_order=scene_ids, transition_source_hash=_hash_text(yaml.safe_dump(transitions, sort_keys=False)) if transitions else None, content_hash=_hash_text(text), transformation=transformation or {"id": "expression.compose_chapter", "version": 1, "executor": "deterministic"}, validation_findings=transition_findings)
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
            if transitions and persist_transitions:
                self.save_transitions(chapter, transitions)
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
        lines = [line for line in text.splitlines() if not any(pattern.match(line) for pattern in (MARKER_RE, END_MARKER_RE, TRANSITION_MARKER_RE, END_TRANSITION_MARKER_RE))]
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def inspect_markers(text: str) -> dict[str, Any]:
        """Strictly inspect internal markers without semantic reconstruction."""
        findings: list[dict[str, str]] = []
        scenes: list[str] = []
        open_scene: str | None = None
        for line_number, line in enumerate(text.splitlines(), 1):
            if "<!-- auteur:" in line and not any(pattern.match(line) for pattern in (MARKER_RE, END_MARKER_RE, TRANSITION_MARKER_RE, END_TRANSITION_MARKER_RE)):
                findings.append({"code": "malformed_marker", "line": str(line_number), "message": "Malformed Auteur marker-like syntax", "recommended_action": "restore the exact marker grammar"})
                continue
            start = MARKER_RE.match(line)
            end = END_MARKER_RE.match(line)
            if start:
                scene_id = start.group(1)
                if open_scene is not None or scene_id in scenes:
                    findings.append({"code": "ambiguous_marker", "line": str(line_number), "message": f"duplicate or nested Scene marker: {scene_id}", "recommended_action": "retain one ordered section marker"})
                scenes.append(scene_id)
                open_scene = scene_id
            elif end:
                if open_scene != end.group(1):
                    findings.append({"code": "ambiguous_marker", "line": str(line_number), "message": f"unmatched Scene end marker: {end.group(1)}", "recommended_action": "match the closing ID to its opening marker"})
                open_scene = None
        if open_scene is not None:
            findings.append({"code": "missing_marker", "line": str(len(text.splitlines())), "message": f"missing end marker for {open_scene}", "recommended_action": f"add <!-- auteur:end-scene id={open_scene} -->"})
        if not scenes:
            findings.append({"code": "unresolved_divergence", "line": "1", "message": "Chapter prose has no stable Scene markers", "recommended_action": "restore markers, manually map sections, retain Chapter divergence, create Scene candidates, or discard the import"})
        return {"scene_ids": scenes, "findings": findings, "status": "unresolved_divergence" if findings else "mapped"}

    def inspect_manuscript(self, manuscript: Path, against: str) -> dict[str, Any]:
        text = Path(manuscript).read_text(encoding="utf-8")
        marker_report = self.inspect_markers(text)
        if marker_report["status"] == "unresolved_divergence":
            return {"status": "unresolved_divergence", "message": "No reliable Scene ownership can be established; source prose will not be overwritten.", "actions": ["restore markers", "manually map sections", "retain Chapter-local divergence", "create Scene-level candidates", "discard the import"], "marker_report": marker_report}
        assembly = self.inspect(against)
        expected = {item["scene_id"]: item for item in assembly.source_scenes}
        positions: dict[str, list[int]] = {}
        lines = text.splitlines()
        current: str | None = None
        sections: dict[str, list[str]] = {}
        for line in lines:
            start = MARKER_RE.match(line)
            end = END_MARKER_RE.match(line)
            if start:
                current = start.group(1); positions.setdefault(current, []).append(len(positions.get(current, [])))
                sections.setdefault(current, [])
            elif end:
                current = None
            elif current:
                sections.setdefault(current, []).append(line)
        report: dict[str, Any] = {"status": "mapped", "unchanged": [], "modified": [], "moved": [], "missing": [], "duplicated": [], "unsourced": []}
        expected_order = [item["scene_id"] for item in assembly.source_scenes]
        actual_order = list(positions)
        for scene_id, item in expected.items():
            if scene_id not in positions:
                report["missing"].append(scene_id); continue
            if len(positions[scene_id]) > 1:
                report["duplicated"].append(scene_id); continue
            expected_prose = (self._scene_path(scene_id).parent / scene_id / f"prose_v{item['expression_revision']:03d}.md").read_text(encoding="utf-8").strip()
            (report["unchanged"] if "\n".join(sections.get(scene_id, [])).strip() == expected_prose else report["modified"]).append({"scene_id": scene_id, "source": f"prose_v{item['expression_revision']:03d}"})
        if actual_order != expected_order and set(actual_order) == set(expected_order):
            report["moved"] = [{"scene_id": scene_id, "expected_position": expected_order.index(scene_id) + 1, "current_position": actual_order.index(scene_id) + 1} for scene_id in expected_order if expected_order.index(scene_id) != actual_order.index(scene_id)]
        return report
