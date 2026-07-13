from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class Lifecycle(str, Enum):
    DRAFT = "draft"
    ACCEPTED = "accepted"
    REPLACED = "replaced"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ReviewState(str, Enum):
    NONE = "none"
    REVIEW_REQUIRED = "review_required"
    ACKNOWLEDGED_DIVERGENCE = "acknowledged_divergence"


class DependencyKind(str, Enum):
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    STATE_ORDER = "state_order"


class DependencySource(str, Enum):
    DECLARED = "declared"
    INFERRED = "inferred"
    GENERATED = "generated"
    SUGGESTED = "suggested"


@dataclass(frozen=True)
class DependencySpec:
    artifact_id: str
    artifact_type: str
    path: Path
    kind: DependencyKind
    source: DependencySource
    fields: list[str] = field(default_factory=list)


class DependencyRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_type: str
    path: str
    kind: DependencyKind
    source: DependencySource
    fields: list[str] = Field(default_factory=list)
    revision: int | None = None
    content_hash: str | None = None


class StaleReason(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    dependency_id: str
    previous_revision: int | None = None
    current_revision: int | None = None
    affected_fields: list[str] = Field(default_factory=list)
    recommended_action: str = "review"
    severity: str = "review_required"


class ArtifactMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    artifact_type: str
    schema_version: int = 1
    revision: int = 1
    authority: str = "canonical"
    lifecycle: Lifecycle = Lifecycle.DRAFT
    review_state: ReviewState = ReviewState.NONE
    content_hash: str
    dependencies: list[DependencyRecord] = Field(default_factory=list)
    stale_reasons: list[StaleReason] = Field(default_factory=list)
    invalid_reasons: list[str] = Field(default_factory=list)
    provenance_state: str = "tracked"
    accepted_at: str | None = None
    accepted_by: str | None = None
    rationale: str | None = None
    # Computed status; never serialized into the sidecar.
    health: str = "valid"
    freshness: str = "fresh"


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, Enum):
        return value.value
    return value


def canonical_content_hash(path: Path, fields: list[str] | None = None) -> str:
    """Hash semantic YAML/JSON content, independent of formatting and key order."""
    if path.suffix.lower() in {".yaml", ".yml", ".json"}:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if fields and isinstance(data, dict):
            data = {field: data.get(field) for field in fields}
        payload = json.dumps(_normalize(data), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    else:
        text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        text = "\n".join(line.rstrip(" ") for line in text).rstrip("\n") + "\n"
        payload = unicodedata.normalize("NFC", text)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ArtifactStore:
    """File-backed sidecar metadata store for the StoryIdentity pilot chain."""

    def __init__(self, project: Path):
        self.project = Path(project)
        self.root = self.project / ".auteur" / "state" / "artifacts"

    def sidecar_path(self, artifact_id: str) -> Path:
        return self.root / f"{artifact_id}.yaml"

    def _artifact_id(self, path: Path) -> str:
        path = Path(path)
        if path.name == "outline.yaml" and path.parent.name.isdigit():
            return f"chapter_{path.parent.name}"
        return path.stem

    def _stored_path(self, path: Path) -> str:
        try:
            return str(Path(path).resolve().relative_to(self.project.resolve()))
        except ValueError:
            return str(path)

    def _resolved_path(self, stored_path: str) -> Path:
        candidate = Path(stored_path)
        return candidate if candidate.is_absolute() else self.project / candidate

    def content_hash(self, path: Path, fields: list[str] | None = None) -> str:
        return canonical_content_hash(Path(path), fields)

    def _load(self, artifact_id: str) -> ArtifactMetadata | None:
        sidecar = self.sidecar_path(artifact_id)
        if not sidecar.exists():
            return None
        return ArtifactMetadata.model_validate(yaml.safe_load(sidecar.read_text(encoding="utf-8")))

    def _write(self, metadata: ArtifactMetadata) -> ArtifactMetadata:
        self.root.mkdir(parents=True, exist_ok=True)
        payload = metadata.model_dump(mode="json", exclude={"health", "freshness"})
        self.sidecar_path(metadata.artifact_id).write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return metadata

    def _records(self, specs: list[DependencySpec]) -> list[DependencyRecord]:
        records: list[DependencyRecord] = []
        for spec in specs:
            dependency = self._load(spec.artifact_id)
            records.append(
                DependencyRecord(
                    artifact_id=spec.artifact_id,
                    artifact_type=spec.artifact_type,
                    path=self._stored_path(spec.path),
                    kind=spec.kind,
                    source=spec.source,
                    fields=spec.fields,
                    revision=dependency.revision if dependency else None,
                    content_hash=self.content_hash(spec.path, spec.fields) if spec.path.exists() else None,
                )
            )
        return records

    def _infer_dependencies(self, path: Path, artifact_type: str) -> list[DependencySpec]:
        specs: list[DependencySpec] = []
        identity = self.project / "story_identity.yaml"
        blueprint = self.project / "blueprint.yaml"
        semantic_fields = ["core_answer", "target_experience", "story_type", "central_engine", "not_this", "open_questions", "recommendation_mode", "best_basis", "why_this_is_best", "rejected_directions", "author_overrides", "genre_contract_snapshot"]
        if artifact_type == "blueprint" and identity.exists():
            specs.append(DependencySpec("story_identity", "story_identity", identity, DependencyKind.SEMANTIC, DependencySource.INFERRED, semantic_fields))
        elif artifact_type == "chapter_outline":
            if identity.exists():
                specs.append(DependencySpec("story_identity", "story_identity", identity, DependencyKind.SEMANTIC, DependencySource.INFERRED, semantic_fields))
            if blueprint.exists():
                specs.append(DependencySpec("blueprint", "blueprint", blueprint, DependencyKind.STRUCTURAL, DependencySource.INFERRED))
        elif artifact_type == "scene_realization":
            if blueprint.exists():
                specs.append(DependencySpec("blueprint", "blueprint", blueprint, DependencyKind.SEMANTIC, DependencySource.INFERRED))
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                chapter_id = data.get("chapter_id") or data.get("chapter")
                if chapter_id:
                    chapter_path = next((candidate for candidate in (self.project / f"{chapter_id}.yaml", self.project / "chapters" / str(chapter_id) / "outline.yaml") if candidate.exists()), None)
                    if chapter_path:
                        specs.append(DependencySpec(str(chapter_id), "chapter_outline", chapter_path, DependencyKind.STRUCTURAL, DependencySource.INFERRED))
                follows = ((data.get("temporal_relation") or {}).get("follows_scene"))
                if follows:
                    previous = next((candidate for candidate in (path.parent / f"{follows}.yaml", self.project / "scenes" / f"{follows}.yaml") if candidate.exists()), None)
                    if previous:
                        specs.append(DependencySpec(str(follows), "scene_realization", previous, DependencyKind.STATE_ORDER, DependencySource.INFERRED))
            except (OSError, yaml.YAMLError):
                pass
        return specs

    def adopt(self, path: Path, artifact_type: str) -> ArtifactMetadata:
        artifact_id = self._artifact_id(path)
        return self._write(
            ArtifactMetadata(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                content_hash=self.content_hash(path),
                provenance_state="tracked",
                lifecycle=Lifecycle.DRAFT,
            )
        )

    def accept(
        self,
        path: Path,
        artifact_type: str,
        dependencies: list[DependencySpec] | None = None,
        *,
        accepted_by: str = "author",
        rationale: str | None = None,
        acknowledge_divergence: bool = False,
    ) -> ArtifactMetadata | None:
        artifact_id = self._artifact_id(path)
        previous = self._load(artifact_id)
        if previous and previous.lifecycle is Lifecycle.ARCHIVED:
            return None
        if dependencies is not None:
            records = self._records(dependencies)
        elif previous and acknowledge_divergence:
            records = previous.dependencies
        elif previous:
            records = self._records(self._infer_dependencies(path, artifact_type))
        else:
            records = self._records(self._infer_dependencies(path, artifact_type))
        metadata = ArtifactMetadata(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            schema_version=previous.schema_version if previous else 1,
            revision=(previous.revision + 1) if previous else 1,
            authority="canonical",
            lifecycle=Lifecycle.ACCEPTED,
            review_state=ReviewState.ACKNOWLEDGED_DIVERGENCE if acknowledge_divergence else ReviewState.NONE,
            content_hash=self.content_hash(path),
            dependencies=records,
            stale_reasons=previous.stale_reasons if acknowledge_divergence and previous else [],
            provenance_state="tracked",
            accepted_by=accepted_by,
            rationale=rationale,
        )
        return self._write(metadata)

    def status(self, path: Path, artifact_type: str) -> ArtifactMetadata:
        artifact_id = self._artifact_id(path)
        metadata = self._load(artifact_id)
        if metadata is None:
            metadata = ArtifactMetadata(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                content_hash=self.content_hash(path) if path.exists() else "",
                provenance_state="unknown",
                health="valid" if path.exists() else "invalid",
                freshness="unknown",
            )
        reasons: list[StaleReason] = []
        invalid: list[str] = []
        if not path.exists():
            invalid.append("artifact_missing")
        else:
            try:
                document = yaml.safe_load(path.read_text(encoding="utf-8"))
                matching_ids = 0
                for candidate in self.project.rglob("*.yaml"):
                    if ".auteur" in candidate.parts:
                        continue
                    try:
                        candidate_data = yaml.safe_load(candidate.read_text(encoding="utf-8"))
                    except (OSError, yaml.YAMLError):
                        continue
                    candidate_id = self._artifact_id(candidate)
                    if isinstance(candidate_data, dict) and candidate_data.get("id"):
                        candidate_id = str(candidate_data["id"])
                    if candidate_id == artifact_id:
                        matching_ids += 1
                if matching_ids > 1:
                    invalid.append("duplicate_artifact_id")
            except (OSError, yaml.YAMLError):
                invalid.append("malformed_schema")
        for dependency in metadata.dependencies:
            dep_path = self._resolved_path(dependency.path)
            dep_meta = self._load(dependency.artifact_id)
            if dep_meta and dep_meta.lifecycle is Lifecycle.ARCHIVED:
                invalid.append(f"archived_dependency:{dependency.artifact_id}")
                continue
            if not dep_path.exists():
                invalid.append(f"missing_dependency:{dependency.artifact_id}")
                continue
            current_hash = self.content_hash(dep_path, dependency.fields)
            current_revision = dep_meta.revision if dep_meta else None
            if current_hash != dependency.content_hash or current_revision != dependency.revision:
                reasons.append(StaleReason(code="UPSTREAM_DEPENDENCY_CHANGED", dependency_id=dependency.artifact_id, previous_revision=dependency.revision, current_revision=current_revision, affected_fields=dependency.fields))
        metadata.health = "invalid" if invalid else "valid"
        metadata.freshness = "stale" if reasons else "fresh"
        metadata.invalid_reasons = invalid
        metadata.stale_reasons = reasons if reasons else metadata.stale_reasons
        if reasons and metadata.review_state is ReviewState.NONE:
            metadata.review_state = ReviewState.REVIEW_REQUIRED
        return metadata

    def archive(self, path: Path, artifact_type: str, *, reason: str, by: str, replaced_by: str | None = None) -> ArtifactMetadata:
        current = self._load(self._artifact_id(path))
        if current is None:
            current = self.adopt(path, artifact_type)
        current.lifecycle = Lifecycle.ARCHIVED
        current.rationale = f"{reason} (archived by {by})" + (f"; replaced by {replaced_by}" if replaced_by else "")
        return self._write(current)

    def affected_by(self, artifact_id: str) -> set[str]:
        dependents: dict[str, set[str]] = {}
        for sidecar in self.root.glob("*.yaml") if self.root.exists() else []:
            metadata = self._load(sidecar.stem)
            if not metadata:
                continue
            for dependency in metadata.dependencies:
                if dependency.source is not DependencySource.SUGGESTED:
                    dependents.setdefault(dependency.artifact_id, set()).add(metadata.artifact_id)
        affected: set[str] = set()
        frontier = [artifact_id]
        while frontier:
            current = frontier.pop()
            for dependent in dependents.get(current, set()):
                if dependent not in affected:
                    affected.add(dependent)
                    frontier.append(dependent)
        return affected

    def explain(self, path: Path, artifact_type: str) -> list[dict[str, Any]]:
        metadata = self.status(path, artifact_type)
        return [reason.model_dump(mode="json") for reason in metadata.stale_reasons] + [
            {"code": reason} for reason in metadata.invalid_reasons
        ]
