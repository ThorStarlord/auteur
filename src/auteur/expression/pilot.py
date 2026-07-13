from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic import BaseModel, ConfigDict, Field

from auteur.provenance import ArtifactStore, Lifecycle


class ExpressionConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pov: str | None = None
    tense: str | None = None
    narrative_distance: str | None = None
    voice_id: str | None = None
    target_effect: str | None = None
    content_boundaries: list[str] = Field(default_factory=list)


class SourceScene(BaseModel):
    artifact_id: str
    revision: int
    content_hash: str
    path: str


class TransformationRecord(BaseModel):
    id: str = "realization.generate_expression"
    category: str = "generation"
    family: str = "knowledge_creation"
    version: int = 1


class ExecutorRecord(BaseModel):
    kind: str = "human-authored"
    provider: str | None = None
    model: str | None = None
    configuration_hash: str | None = None


class ProseCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    artifact_type: str = "expression_scene_prose"
    revision: int
    lifecycle: Lifecycle = Lifecycle.DRAFT
    authority: str = "candidate"
    source_scene: SourceScene
    transformation: TransformationRecord = Field(default_factory=TransformationRecord)
    executor: ExecutorRecord = Field(default_factory=ExecutorRecord)
    expression_constraints: ExpressionConstraints = Field(default_factory=ExpressionConstraints)
    content_hash: str
    generated_at: str
    accepted_at: str | None = None
    accepted_by: str | None = None
    accepted_revision: int | None = None
    validation_findings: list[dict[str, str]] = Field(default_factory=list)


def _hash_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _configuration_hash(constraints: ExpressionConstraints) -> str:
    payload = json.dumps(constraints.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return _hash_text(payload)


def build_scene_prompt(scene_path: Path, constraints: dict[str, Any] | ExpressionConstraints | None = None) -> str:
    data = yaml.safe_load(Path(scene_path).read_text(encoding="utf-8")) or {}
    constraints_model = constraints if isinstance(constraints, ExpressionConstraints) else ExpressionConstraints.model_validate(constraints or {})
    canonical_keys = [
        "participants", "location", "event_order", "goal", "opposition", "turn",
        "decision", "outcome", "knowledge", "emotional_changes", "arc_realizations",
    ]
    facts = {key: data.get(key) for key in canonical_keys if key in data}
    return "\n".join([
        "# CANONICAL FACTS",
        yaml.safe_dump(facts, sort_keys=False).rstrip(),
        "",
        "# EXPRESSION CONSTRAINTS",
        yaml.safe_dump(constraints_model.model_dump(exclude_none=True, mode="json"), sort_keys=False).rstrip(),
        "",
        "# EXPRESSION FREEDOM",
        "You may choose wording, dialogue, imagery, rhythm, sensory rendering, interiority, paragraphing, and local pacing.",
        "Do not change the Scene Realization, Blueprint, Chapter Outline, Story Identity, or Bible.",
        "Return prose only.",
    ])


def render_scene_bard_prompt(scene_path: Path, constraints: dict[str, Any] | ExpressionConstraints | None = None) -> tuple[str, str]:
    """Adapt Bard's existing prose contract to one Scene Realization."""
    from auteur.bard import SYSTEM_PROMPT

    return SYSTEM_PROMPT, build_scene_prompt(scene_path, constraints)


class ExpressionStore:
    """Focused Scene Realization -> prose candidate persistence."""

    def __init__(self, project: Path):
        self.project = Path(project)

    def candidate_dir(self, scene_path: Path) -> Path:
        scene_path = Path(scene_path)
        return scene_path.parent / scene_path.stem

    def _candidate_files(self) -> list[Path]:
        return list(self.project.glob("chapters/*/scenes/*/prose_v*.yaml"))

    def _metadata_path(self, candidate_id: str) -> Path:
        for path in self._candidate_files():
            metadata = ProseCandidate.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
            if metadata.candidate_id == candidate_id:
                return path
        raise FileNotFoundError(f"expression candidate not found: {candidate_id}")

    def _scene_path(self, metadata: ProseCandidate) -> Path:
        return self.project / metadata.source_scene.path

    def prose_path(self, candidate_id: str) -> Path:
        metadata_path = self._metadata_path(candidate_id)
        return metadata_path.with_suffix(".md")

    def accepted_path(self, scene_path: Path, candidate_id: str) -> Path:
        metadata_path = self._metadata_path(candidate_id)
        return metadata_path.parent / "accepted.yaml"

    def _source(self, scene_path: Path) -> tuple[Any, Path]:
        scene_path = Path(scene_path)
        source_store = ArtifactStore(self.project)
        status = source_store.status(scene_path, "scene_realization")
        if status.lifecycle is not Lifecycle.ACCEPTED:
            raise ValueError("source Scene Realization must be accepted")
        if status.health != "valid":
            raise ValueError("source Scene Realization is invalid")
        return status, scene_path

    def _next_revision(self, scene_path: Path) -> int:
        directory = self.candidate_dir(scene_path)
        versions = []
        for path in directory.glob("prose_v*.yaml") if directory.exists() else []:
            match = re.fullmatch(r"prose_v(\d+)", path.stem)
            if match:
                versions.append(int(match.group(1)))
        return max(versions, default=0) + 1

    def generate(
        self,
        scene_path: Path,
        prose: str | Callable[[], str],
        *,
        constraints: dict[str, Any] | ExpressionConstraints | None = None,
        executor: dict[str, Any] | ExecutorRecord | None = None,
    ) -> ProseCandidate:
        source, scene_path = self._source(scene_path)
        text = prose() if callable(prose) else prose
        if not isinstance(text, str) or not text.strip():
            raise ValueError("generation produced no prose")
        constraint_model = constraints if isinstance(constraints, ExpressionConstraints) else ExpressionConstraints.model_validate(constraints or {})
        executor_model = executor if isinstance(executor, ExecutorRecord) else ExecutorRecord.model_validate(executor or {})
        executor_model.configuration_hash = executor_model.configuration_hash or _configuration_hash(constraint_model)
        revision = self._next_revision(scene_path)
        candidate_id = f"{scene_path.stem}:prose_v{revision:03d}"
        metadata = ProseCandidate(
            candidate_id=candidate_id,
            revision=revision,
            source_scene=SourceScene(
                artifact_id=source.artifact_id,
                revision=source.revision,
                content_hash=source.content_hash,
                path=str(scene_path.resolve().relative_to(self.project.resolve())),
            ),
            executor=executor_model,
            expression_constraints=constraint_model,
            content_hash=_hash_text(text),
            generated_at=datetime.now(timezone.utc).isoformat(),
            validation_findings=self.validate_prose(scene_path, text),
        )
        directory = self.candidate_dir(scene_path)
        directory.mkdir(parents=True, exist_ok=True)
        prose_path = directory / f"prose_v{revision:03d}.md"
        metadata_path = directory / f"prose_v{revision:03d}.yaml"
        prose_tmp = prose_path.with_name(prose_path.name + ".tmp")
        metadata_tmp = metadata_path.with_name(metadata_path.name + ".tmp")
        try:
            prose_tmp.write_text(text, encoding="utf-8")
            metadata_tmp.write_text(yaml.safe_dump(metadata.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
            prose_tmp.replace(prose_path)
            metadata_tmp.replace(metadata_path)
        except Exception:
            for path in (prose_tmp, metadata_tmp):
                if path.exists():
                    path.unlink()
            raise
        return metadata

    def generate_with_llm(
        self,
        scene_path: Path,
        llm: Any,
        *,
        constraints: dict[str, Any] | ExpressionConstraints | None = None,
        executor: dict[str, Any] | ExecutorRecord | None = None,
    ) -> ProseCandidate:
        from auteur.llm import LLMRequest

        system, user = render_scene_bard_prompt(scene_path, constraints)
        response = llm.complete(LLMRequest(system=system, user=user, temperature=0.85, max_tokens=8000))
        return self.generate(scene_path, response.text, constraints=constraints, executor=executor)

    def inspect(self, candidate_id: str) -> ProseCandidate:
        path = self._metadata_path(candidate_id)
        return ProseCandidate.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

    def status(self, candidate_id: str) -> dict[str, Any]:
        metadata = self.inspect(candidate_id)
        scene_path = self._scene_path(metadata)
        try:
            source, _ = self._source(scene_path)
            current_hash = ArtifactStore(self.project).content_hash(scene_path)
            stale = source.revision != metadata.source_scene.revision or current_hash != metadata.source_scene.content_hash
            health = "invalid" if metadata.validation_findings else "valid"
            return {"candidate_id": candidate_id, "health": health, "freshness": "stale" if stale else "fresh", "lifecycle": metadata.lifecycle.value, "findings": metadata.validation_findings}
        except (FileNotFoundError, ValueError) as exc:
            return {"candidate_id": candidate_id, "health": "invalid", "freshness": "unknown", "lifecycle": metadata.lifecycle.value, "findings": [{"code": "source_unavailable", "message": str(exc)}]}

    def accept(self, candidate_id: str, *, accepted_by: str = "author") -> ProseCandidate:
        metadata = self.inspect(candidate_id)
        status = self.status(candidate_id)
        if status["health"] == "invalid":
            raise ValueError("cannot accept an invalid prose candidate")
        metadata.lifecycle = Lifecycle.ACCEPTED
        metadata.authority = "canonical"
        metadata.accepted_by = accepted_by
        metadata.accepted_at = datetime.now(timezone.utc).isoformat()
        prior_accepted = []
        for path in self._candidate_files():
            other = ProseCandidate.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
            if other.source_scene.artifact_id == metadata.source_scene.artifact_id and other.lifecycle is Lifecycle.ACCEPTED and other.candidate_id != candidate_id:
                other.lifecycle = Lifecycle.REPLACED
                path.write_text(yaml.safe_dump(other.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
                prior_accepted.append(other)
        metadata.accepted_revision = max((item.accepted_revision or 0 for item in prior_accepted), default=0) + 1
        path = self._metadata_path(candidate_id)
        path.write_text(yaml.safe_dump(metadata.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
        self.accepted_path(scene_path=self._scene_path(metadata), candidate_id=candidate_id).write_text(yaml.safe_dump(metadata.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
        return metadata

    def validate_prose(self, scene_path: Path, prose: str) -> list[dict[str, str]]:
        data = yaml.safe_load(Path(scene_path).read_text(encoding="utf-8")) or {}
        findings: list[dict[str, str]] = []
        participants = data.get("participants") or []
        pov = data.get("pov_character_id")
        if pov and pov not in participants:
            findings.append({"code": "invalid_pov", "message": "declared POV is not a scene participant"})
        outcome = str(data.get("outcome", "")).strip()
        if outcome and re.search(rf"\bnot\s+{re.escape(outcome)}\b", prose, re.IGNORECASE):
            findings.append({"code": "outcome_contradiction", "message": "prose explicitly contradicts the declared scene outcome"})
        for fact in data.get("knowledge", []) or []:
            if isinstance(fact, str) and re.search(rf"\bknew\s+{re.escape(fact)}\b", prose, re.IGNORECASE) and fact not in str(data.get("entry_state", "")):
                findings.append({"code": "unavailable_knowledge", "message": f"prose asserts unavailable knowledge: {fact}"})
        return findings

    def create_upstream_proposal(self, scene_path: Path, *, problem: str, suggested_change: str, evidence: str) -> dict[str, Any]:
        source = ArtifactStore(self.project).status(Path(scene_path), "scene_realization")
        proposal = {
            "proposal_id": f"expression_{Path(scene_path).stem}",
            "target_artifact": source.artifact_id,
            "target_layer": "Realization",
            "source_scene_revision": source.revision,
            "problem": problem,
            "suggested_change": suggested_change,
            "evidence": evidence,
            "status": "proposed",
        }
        path = self.project / "expression" / "proposals" / f"{proposal['proposal_id']}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
        return proposal
