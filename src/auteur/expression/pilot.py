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

from auteur.provenance import ArtifactStore, Lifecycle, ReviewState


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
    review_state: ReviewState = ReviewState.NONE
    metadata_revision: int = 1
    review_history: list[dict[str, Any]] = Field(default_factory=list)
    realization_evidence: dict[str, Any] = Field(default_factory=dict)
    rejection: dict[str, str] | None = None
    reviewed_source: SourceScene | None = None


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
            raw_stale = source.revision != metadata.source_scene.revision or current_hash != metadata.source_scene.content_hash
            acknowledged_snapshot = metadata.review_state is ReviewState.ACKNOWLEDGED_DIVERGENCE and metadata.reviewed_source is not None and source.revision == metadata.reviewed_source.revision and current_hash == metadata.reviewed_source.content_hash
            stale = raw_stale and not acknowledged_snapshot
            if raw_stale and metadata.review_state is ReviewState.ACKNOWLEDGED_DIVERGENCE and not acknowledged_snapshot:
                metadata.review_state = ReviewState.REVIEW_REQUIRED
                metadata.review_history.append({"state": "review_required", "reason": "reviewed dependency changed", "at": datetime.now(timezone.utc).isoformat()})
                self._write_metadata(metadata)
            health = "invalid" if any(f.get("severity", "error") == "error" for f in metadata.validation_findings) else "valid"
            freshness = "stale" if stale else "divergent" if acknowledged_snapshot else "fresh"
            review_required = stale or metadata.review_state is ReviewState.REVIEW_REQUIRED or metadata.lifecycle is Lifecycle.REJECTED
            return {"candidate_id": candidate_id, "health": health, "freshness": freshness, "lifecycle": metadata.lifecycle.value, "review_state": metadata.review_state.value, "review_required": review_required, "findings": metadata.validation_findings, "recommended_actions": self._recommended_actions(metadata, stale)}
        except (FileNotFoundError, ValueError) as exc:
            return {"candidate_id": candidate_id, "health": "invalid", "freshness": "unknown", "lifecycle": metadata.lifecycle.value, "review_state": metadata.review_state.value, "review_required": True, "findings": [{"code": "source_unavailable", "message": str(exc), "severity": "error", "recommended_action": "restore the source Scene, then revalidate"}], "recommended_actions": ["restore the source Scene", "revalidate the candidate"]}

    def _write_metadata(self, metadata: ProseCandidate) -> None:
        path = self._metadata_path(metadata.candidate_id)
        path.write_text(yaml.safe_dump(metadata.model_dump(mode="json"), sort_keys=False), encoding="utf-8")

    @staticmethod
    def _recommended_actions(metadata: ProseCandidate, stale: bool) -> list[str]:
        if metadata.lifecycle is Lifecycle.REJECTED:
            return ["reopen the candidate explicitly if it should be reconsidered"]
        if stale or metadata.review_state is ReviewState.REVIEW_REQUIRED:
            return ["revalidate if the prose still matches", "acknowledge intentional divergence", "reject the candidate"]
        if any(f.get("severity", "error") == "error" for f in metadata.validation_findings):
            return ["revise the prose to resolve blocking findings"]
        return ["accept the candidate", "reject the candidate"]

    def accept(self, candidate_id: str, *, accepted_by: str = "author", allow_divergence: bool = False) -> ProseCandidate:
        metadata = self.inspect(candidate_id)
        status = self.status(candidate_id)
        if status["health"] == "invalid":
            raise ValueError("cannot accept an invalid prose candidate")
        if status["freshness"] == "stale" and not (allow_divergence and status["review_state"] == ReviewState.ACKNOWLEDGED_DIVERGENCE.value):
            raise ValueError("candidate is stale and requires revalidation or acknowledged divergence before acceptance")
        if status["freshness"] == "divergent" and not allow_divergence:
            raise ValueError("divergent acceptance requires --allow-divergence")
        if metadata.lifecycle is Lifecycle.REJECTED:
            raise ValueError("cannot normally accept a rejected prose candidate")
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

    def revalidate(self, candidate_id: str, *, reviewed_by: str = "author") -> ProseCandidate:
        metadata = self.inspect(candidate_id)
        source, scene_path = self._source(self._scene_path(metadata))
        metadata.source_scene.revision = source.revision
        metadata.source_scene.content_hash = ArtifactStore(self.project).content_hash(scene_path)
        metadata.metadata_revision += 1
        metadata.review_state = ReviewState.NONE
        metadata.reviewed_source = None
        metadata.review_history.append({"state": "revalidated", "by": reviewed_by, "at": datetime.now(timezone.utc).isoformat(), "source_revision": source.revision, "source_hash": metadata.source_scene.content_hash})
        metadata.validation_findings = self.validate_prose(scene_path, self.prose_path(candidate_id).read_text(encoding="utf-8"), realization_evidence=metadata.realization_evidence)
        self._write_metadata(metadata)
        return metadata

    def acknowledge(self, candidate_id: str, *, acknowledged_by: str = "author", reason: str) -> ProseCandidate:
        if not reason.strip():
            raise ValueError("divergence acknowledgement requires a rationale")
        metadata = self.inspect(candidate_id)
        status = self.status(candidate_id)
        if status["freshness"] != "stale":
            raise ValueError("candidate is not stale; acknowledge divergence is only for changed source Scenes")
        metadata.metadata_revision += 1
        metadata.review_state = ReviewState.ACKNOWLEDGED_DIVERGENCE
        source, scene_path = self._source(self._scene_path(metadata))
        metadata.reviewed_source = SourceScene(
            artifact_id=source.artifact_id,
            revision=source.revision,
            content_hash=ArtifactStore(self.project).content_hash(scene_path),
            path=metadata.source_scene.path,
        )
        metadata.review_history.append({"state": "acknowledged_divergence", "by": acknowledged_by, "reason": reason, "at": datetime.now(timezone.utc).isoformat(), "source_revision": metadata.source_scene.revision, "source_hash": metadata.source_scene.content_hash})
        self._write_metadata(metadata)
        return metadata

    def reject(self, candidate_id: str, *, rejected_by: str = "author", reason: str = "") -> ProseCandidate:
        metadata = self.inspect(candidate_id)
        metadata.lifecycle = Lifecycle.REJECTED
        metadata.metadata_revision += 1
        metadata.rejection = {"by": rejected_by, "reason": reason, "at": datetime.now(timezone.utc).isoformat()}
        metadata.review_history.append({"state": "rejected", **metadata.rejection})
        self._write_metadata(metadata)
        return metadata

    def compare(self, first_id: str, second_id: str) -> dict[str, Any]:
        first, second = self.inspect(first_id), self.inspect(second_id)
        first_text, second_text = self.prose_path(first_id).read_text(encoding="utf-8"), self.prose_path(second_id).read_text(encoding="utf-8")
        import difflib
        return {"candidates": [{"candidate_id": item.candidate_id, "executor": item.executor.model_dump(mode="json"), "source_revision": item.source_scene.revision, "lifecycle": item.lifecycle.value, "status": self.status(item.candidate_id)} for item in (first, second)], "diff": "".join(difflib.unified_diff(first_text.splitlines(keepends=True), second_text.splitlines(keepends=True), fromfile=first_id, tofile=second_id))}

    def validate_prose(self, scene_path: Path, prose: str, *, realization_evidence: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        data = yaml.safe_load(Path(scene_path).read_text(encoding="utf-8")) or {}
        findings: list[dict[str, str]] = []
        participants = data.get("participants") or []
        pov = data.get("pov_character_id")
        if pov and pov not in participants:
            findings.append({"code": "invalid_pov", "message": "declared POV is not a scene participant"})
        outcome = data.get("outcome", "")
        outcome_text = outcome.get("result", "") if isinstance(outcome, dict) else str(outcome)
        evidence = (realization_evidence or {}).get("outcome", {})
        if evidence.get("status") == "contradicted":
            findings.append({"code": "outcome_contradiction", "severity": "error", "confidence": "high", "message": "structured evidence marks the canonical outcome as contradicted", "recommended_action": "revise the prose or revise the Scene Realization"})
        elif outcome_text and re.search(rf"\b(?:not|never|fails?\s+to)\s+(?:{re.escape(outcome_text)})\b", prose, re.IGNORECASE):
            findings.append({"code": "outcome_contradiction", "severity": "warning", "confidence": "high", "message": "prose likely contradicts the declared scene outcome", "recommended_action": "review the outcome realization"})
        knowledge = data.get("entry_state", {}).get("knowledge", []) if isinstance(data.get("entry_state"), dict) else []
        known_facts = {str(item.get("what", "")).lower() for item in knowledge if isinstance(item, dict)}
        for fact in data.get("knowledge", []) or []:
            fact_text = fact.get("what", "") if isinstance(fact, dict) else str(fact)
            if fact_text and re.search(rf"\b(?:knew|knows|remembered)\s+(?:that\s+)?{re.escape(fact_text)}\b", prose, re.IGNORECASE) and fact_text.lower() not in known_facts:
                findings.append({"code": "unavailable_knowledge", "severity": "error", "confidence": "high", "message": f"prose asserts unavailable POV knowledge: {fact_text}", "recommended_action": "attribute the information to a source, conceal it, or revise the Scene knowledge state"})
        if re.search(r"\b(?:jon|he)\s+(?:privately\s+)?(?:knew|remembered)\b", prose, re.IGNORECASE) and data.get("pov_character_id") not in {"jon", None}:
            findings.append({"code": "private_knowledge_exposure", "severity": "warning", "confidence": "high", "message": "limited POV prose exposes another character's private knowledge", "recommended_action": "attribute the knowledge to dialogue/action or make the perspective explicit"})
        if realization_evidence and realization_evidence.get("knowledge_disclosures"):
            for item in realization_evidence["knowledge_disclosures"]:
                if item.get("status") == "contradicted":
                    findings.append({"code": "knowledge_contradiction", "severity": "error", "confidence": "high", "message": f"structured evidence contradicts knowledge fact {item.get('fact_id', 'unknown')}", "recommended_action": "revise the disclosure or revise the Scene knowledge state"})
        return findings

    def create_upstream_proposal(self, scene_path: Path, *, problem: str, suggested_change: str, evidence: str, source_candidate_id: str | None = None) -> dict[str, Any]:
        source = ArtifactStore(self.project).status(Path(scene_path), "scene_realization")
        target_hash = ArtifactStore(self.project).content_hash(Path(scene_path))
        proposal = {
            "proposal_id": f"expression_{Path(scene_path).stem}",
            "target_artifact": source.artifact_id,
            "target_path": str(Path(scene_path).resolve().relative_to(self.project.resolve())),
            "target_layer": "Realization",
            "source_scene_revision": source.revision,
            "target_revision": source.revision,
            "target_projected_hash": target_hash,
            "transformation": {"id": "expression.propose_realization_change", "version": 1},
            "source_candidate_id": None,
            "source_candidate_revision": None,
            "problem": problem,
            "suggested_change": suggested_change,
            "evidence": evidence,
            "status": "proposed",
        }
        if source_candidate_id is not None:
            candidate = self.inspect(source_candidate_id)
            proposal["source_candidate_id"] = candidate.candidate_id
            proposal["source_candidate_revision"] = candidate.revision
        path = self.project / "expression" / "proposals" / f"{proposal['proposal_id']}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
        return proposal

    def proposal_status(self, proposal_id: str) -> dict[str, Any]:
        path = self.project / "expression" / "proposals" / f"{proposal_id}.yaml"
        proposal = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        target = self.project / proposal.get("target_path", "") if proposal.get("target_path") else next(self.project.rglob(f"{proposal.get('target_artifact')}.yaml"), None)
        stale = target is None or ArtifactStore(self.project).content_hash(target) != proposal.get("target_projected_hash")
        return {"proposal": proposal, "status": "stale" if stale else proposal.get("status", "proposed"), "stale": stale}

    def apply_proposal(self, proposal_id: str) -> None:
        if self.proposal_status(proposal_id)["stale"]:
            raise ValueError("stale proposal cannot be applied; regenerate or manually rebase it")
