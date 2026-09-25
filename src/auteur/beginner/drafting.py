"""Candidate-only Chapter drafting for the Beginner product journey."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from auteur.bard import draft_chapter as bard_draft
from auteur.bible import StoryBible
from auteur.cli_handlers import handle_accept
from auteur.critic import ValidationReport
from auteur.identity import StoryIdentity, compile_to_blueprint
from auteur.llm import LLMClient
from auteur.pipeline.runner import _run_critics_via_runtime
from auteur.project import Project

from .continuation import ContinuationState


@dataclass(frozen=True)
class CandidateDraftResult:
    chapter_index: int
    draft_path: Path
    validation_path: Path
    validation_passed: bool


def _draft_version(path: Path) -> int:
    return int(path.stem.removeprefix("draft_v"))


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


def _outline_from_continuation(continuation: ContinuationState) -> dict[str, Any]:
    plan = continuation.chapter_plan
    if plan is None or not continuation.chapter_plan_accepted:
        raise ValueError("accept the Chapter 1 plan before drafting")
    if not continuation.scene_plans or not continuation.scene_plans_accepted:
        raise ValueError("accept the Chapter 1 scene plans before drafting")
    return {
        "scope": "chapter",
        "chapter_index": 1,
        "chapter_summary": plan.what_changes,
        "scenes": [
            {
                "scene_id": scene.scene_id,
                "pov_character": scene.pov,
                "location": "",
                "summary": scene.purpose,
                "key_events": [scene.important_change],
                "character_state_changes": [],
                "arc_advancements": [],
                "estimated_tension": None,
                "emotional_tone": scene.ending_state,
                "entry_state": scene.entry_state,
                "immediate_goal": scene.immediate_goal,
                "conflict": scene.conflict,
                "continuity_constraints": list(scene.continuity_constraints),
            }
            for scene in continuation.scene_plans
        ],
        "arc_pushes": [],
        "contract_compliance": [],
        "expected_elements_touched": [],
        "forbidden_tropes_avoided": [],
        "estimated_chapter_tension": None,
        "thematic_reinforcement": plan.reader_feels,
        "conflict_report": None,
    }


def _project_for_candidate(project_root: Path) -> Project:
    identity_path = project_root / "story_identity.yaml"
    if not identity_path.is_file():
        raise FileNotFoundError("accepted Story Identity is required before Chapter 1 drafting")
    blueprint = compile_to_blueprint(StoryIdentity.from_yaml(identity_path))
    scratch_bible = StoryBible(project_root / ".auteur" / "beginner" / "draft_bible.json")
    return Project(project_root, blueprint, scratch_bible)


def _completed_result(project: Project, version: int) -> CandidateDraftResult | None:
    chapter_dir = project.chapter_dir(1)
    draft_path = chapter_dir / f"draft_v{version}.md"
    validation_path = chapter_dir / f"validation_v{version}.json"
    if not (draft_path.is_file() and validation_path.is_file()):
        return None
    report = ValidationReport.model_validate_json(validation_path.read_text(encoding="utf-8"))
    return CandidateDraftResult(1, draft_path, validation_path, report.passed)


def draft_candidate_chapter(
    project_root: Path,
    continuation: ContinuationState | None,
    *,
    llm: LLMClient,
    command_id: str,
) -> CandidateDraftResult:
    """Write one reviewable candidate and validation report, never accepted canon."""
    if not command_id or any(char in command_id for char in "/\\"):
        raise ValueError("command_id must be a non-empty path-safe identifier")
    if continuation is None or continuation.draft_handoff is None:
        raise ValueError("prepare the Chapter 1 draft before drafting")
    if continuation.stale:
        raise ValueError(continuation.stale_reason or "review stale continuation before drafting")

    project_root = Path(project_root)
    project = _project_for_candidate(project_root)
    outline = _outline_from_continuation(continuation)
    project.write_outline(1, outline)

    receipt_path = project_root / ".auteur" / "beginner" / "drafting" / f"{command_id}.json"
    receipt: dict[str, Any] | None = None
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        version = int(receipt["draft_version"])
        completed = _completed_result(project, version)
        if completed is not None:
            if receipt.get("status") != "complete":
                _write_json_atomic(receipt_path, {**receipt, "status": "complete"})
            return completed
    else:
        version = project.next_draft_version(1)
        receipt = {
            "status": "started",
            "command_id": command_id,
            "chapter_index": 1,
            "draft_version": version,
            "source_fingerprint": continuation.draft_handoff.source_fingerprint,
        }
        _write_json_atomic(receipt_path, receipt)

    chapter_dir = project.chapter_dir(1)
    draft_path = chapter_dir / f"draft_v{version}.md"
    validation_path = chapter_dir / f"validation_v{version}.json"

    previous = sorted(
        (path for path in chapter_dir.glob("draft_v*.md") if _draft_version(path) < version),
        key=_draft_version,
    )
    prior_draft = previous[-1].read_text(encoding="utf-8") if previous else None
    prior_findings = None
    if previous:
        previous_version = _draft_version(previous[-1])
        previous_validation = chapter_dir / f"validation_v{previous_version}.json"
        if not previous_validation.is_file():
            raise RuntimeError(f"matching validation is missing for {previous[-1].name}")
        prior_findings = ValidationReport.model_validate_json(
            previous_validation.read_text(encoding="utf-8")
        ).findings

    if draft_path.is_file():
        prose = draft_path.read_text(encoding="utf-8")
    else:
        prose = bard_draft(
            outline=outline,
            bible=project.bible,
            blueprint=project.blueprint,
            chapter_index=1,
            llm=llm,
            prior_draft=prior_draft,
            findings=prior_findings,
        )
        project.write_draft(1, version, prose)

    report = _run_critics_via_runtime(
        draft=prose,
        outline=outline,
        blueprint=project.blueprint,
        bible=project.bible,
        chapter_index=1,
        iteration=version,
        llm=llm,
        report_dir=project_root / ".auteur" / "reasoning",
    )
    project.write_validation(1, version, report)
    _write_json_atomic(receipt_path, {**receipt, "status": "complete", "validation_passed": report.passed})
    return CandidateDraftResult(1, draft_path, validation_path, report.passed)


def accept_beginner_chapter(project_root: Path, chapter_index: int) -> Any:
    """Delegate explicit acceptance through the existing chapter owner."""
    identity_path = Path(project_root) / "story_identity.yaml"
    if not identity_path.is_file():
        raise FileNotFoundError("accepted Story Identity is required before Chapter acceptance")
    blueprint = compile_to_blueprint(StoryIdentity.from_yaml(identity_path))
    project = Project(Path(project_root), blueprint, StoryBible(Path(project_root) / "bible.json"))
    return handle_accept(project, chapter_index)
