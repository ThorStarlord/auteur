"""Derived post-draft review contracts.

This module deliberately reads existing chapter artifacts.  It does not write
canon, call a provider, or decide whether prose is artistically successful.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class ChapterProductionStatus(str, Enum):
    NOT_STARTED = "not_started"
    HANDOFF_READY = "handoff_ready"
    CANDIDATE_DRAFT = "candidate_draft"
    REVISION_REQUIRED = "revision_required"
    ACCEPTED = "accepted"
    STALE = "stale"


@dataclass(frozen=True)
class DraftReviewProjection:
    chapter_index: int
    source_draft: str | None
    draft_version: int | None
    production_status: ChapterProductionStatus
    accepted: bool
    review_artifact: str | None = None
    review_available: bool = False
    review_error: str | None = None
    blocking_findings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    plan_alignment: dict[str, Any] = field(default_factory=dict)
    accepted_input_refs: list[str] = field(default_factory=list)
    revision_options: list[str] = field(default_factory=list)
    recommended_next_action: str = ""
    stale: bool = False


@dataclass(frozen=True)
class AcceptanceReconciliation:
    chapter_index: int
    command_id: str
    reconciled: bool
    authority_result: Any = None


@dataclass(frozen=True)
class RevisionHandoff:
    chapter_index: int
    source_draft: str
    route: str
    decision: str
    path: Path


def _draft_version(path: Path) -> int:
    match = re.fullmatch(r"draft_v(\d+)", path.stem)
    if not match:
        raise ValueError(f"invalid draft filename: {path.name}")
    return int(match.group(1))


def _upstream_fingerprint(project_root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        [
            project_root / "story_identity.yaml",
            project_root / "blueprint.yaml",
            project_root / "outline.yaml",
        ]
        + list(project_root.glob("chapters/*/outline.yaml"))
        + list(project_root.glob("chapters/*/scene*.yaml"))
    ):
        if path.is_file():
            digest.update(path.relative_to(project_root).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _findings(report: Any) -> tuple[list[str], list[str]]:
    if not isinstance(report, dict) or not isinstance(report.get("findings", []), list):
        raise ValueError("review report has no findings list")
    blocking: list[str] = []
    warnings: list[str] = []
    for finding in report["findings"]:
        if not isinstance(finding, dict):
            raise ValueError("review finding is not an object")
        message = finding.get("message") or finding.get("explanation") or finding.get("detail")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("review finding has no message")
        severity = str(finding.get("severity", "WARNING")).upper()
        (blocking if severity in {"ERROR", "FATAL", "BLOCKER"} else warnings).append(message)
    return blocking, warnings


def _plan_alignment(chapter_dir: Path, draft: Path | None) -> dict[str, Any]:
    outline_path = chapter_dir / "outline.yaml"
    if not outline_path.is_file():
        return {"status": "unknown", "reason": "chapter plan unavailable"}
    try:
        outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {"status": "unknown", "reason": "chapter plan is malformed"}
    if not isinstance(outline, dict):
        return {"status": "unknown", "reason": "chapter plan is malformed"}
    scenes = outline.get("scenes")
    if not isinstance(scenes, list):
        return {"status": "unknown", "reason": "planned scenes unavailable"}
    observed = 0
    if draft is not None:
        observed = sum(1 for line in draft.read_text(encoding="utf-8").splitlines() if re.match(r"^\s*#{0,3}\s*scene\b", line, re.I))
    return {
        "status": "observed",
        "planned_scene_count": len(scenes),
        "observed_scene_count": observed,
        "scene_count_matches": len(scenes) == observed,
    }


def project_draft_review(project_root: Path, chapter_index: int) -> DraftReviewProjection:
    """Project a beginner-readable review without mutating or invoking providers."""
    chapter_dir = project_root / "chapters" / f"{chapter_index:02d}"
    if not chapter_dir.exists():
        chapter_dir = project_root / "chapters" / str(chapter_index)
    drafts = sorted(chapter_dir.glob("draft_v*.md"), key=_draft_version) if chapter_dir.is_dir() else []
    final = chapter_dir / "final.md"
    latest = drafts[-1] if drafts else None
    version = _draft_version(latest) if latest else None
    accepted = final.is_file()
    stale = False
    if latest is not None:
        meta_path = chapter_dir / f"{latest.stem}.meta.json"
        if meta_path.is_file():
            try:
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
                stale = metadata.get("upstream_fingerprint") != _upstream_fingerprint(project_root)
            except (OSError, json.JSONDecodeError):
                stale = True

    blocking: list[str] = []
    warnings: list[str] = []
    review_artifact: str | None = None
    review_available = False
    review_error: str | None = None
    if version is not None:
        report_path = chapter_dir / f"validation_v{version}.json"
        if report_path.is_file():
            review_artifact = report_path.name
            try:
                blocking, warnings = _findings(json.loads(report_path.read_text(encoding="utf-8")))
                review_available = True
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                review_error = f"invalid review artifact: {exc}"
        else:
            review_error = f"review artifact missing for draft_v{version}"

    if accepted:
        status = ChapterProductionStatus.ACCEPTED
    elif stale:
        status = ChapterProductionStatus.STALE
    elif blocking:
        status = ChapterProductionStatus.REVISION_REQUIRED
    elif latest:
        status = ChapterProductionStatus.CANDIDATE_DRAFT
    elif (chapter_dir / "outline.yaml").is_file():
        status = ChapterProductionStatus.HANDOFF_READY
    else:
        status = ChapterProductionStatus.NOT_STARTED

    alignment = _plan_alignment(chapter_dir, latest)
    if stale:
        next_action = "Review the draft against the newer story plan."
    elif blocking:
        next_action = f"Resolve the highest-priority review finding: {blocking[0]}"
    elif accepted:
        next_action = f"Re-orient the story and plan Chapter {chapter_index + 1}."
    elif latest:
        next_action = "Review the candidate draft before accepting or revising it."
    else:
        next_action = "Prepare the chapter draft handoff."
    return DraftReviewProjection(
        chapter_index=chapter_index,
        source_draft=latest.name if latest else None,
        draft_version=version,
        production_status=status,
        accepted=accepted,
        review_artifact=review_artifact,
        review_available=review_available,
        review_error=review_error,
        blocking_findings=blocking,
        warnings=warnings,
        plan_alignment=alignment,
        revision_options=["revise", "accept_deliberate_divergence"] if latest and not accepted else [],
        recommended_next_action=next_action,
        stale=stale,
    )


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f"{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _receipt_value(value: Any) -> Any:
    if is_dataclass(value):
        return _receipt_value(asdict(value))
    if isinstance(value, dict):
        return {str(key): _receipt_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_receipt_value(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "value"):
        return value.value
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def accept_latest_chapter(
    project_root: Path,
    chapter_index: int,
    *,
    command_id: str,
    owner: Any | None = None,
) -> AcceptanceReconciliation:
    """Delegate acceptance and reconcile a durable receipt on retry.

    ``owner`` is injectable for application integration tests.  The default
    routes through the existing CLI acceptance handler; this module never
    writes ``final.md`` or ``bible.json`` itself.
    """
    if not command_id or any(char in command_id for char in "/\\"):
        raise ValueError("command_id must be a non-empty path-safe identifier")
    chapter_dir = project_root / "chapters" / f"{chapter_index:02d}"
    if not chapter_dir.is_dir():
        chapter_dir = project_root / "chapters" / str(chapter_index)
    drafts = sorted(chapter_dir.glob("draft_v*.md"), key=_draft_version)
    if not drafts:
        raise FileNotFoundError(f"no candidate draft for chapter {chapter_index}")
    latest = drafts[-1]
    final = chapter_dir / "final.md"
    receipt_path = project_root / ".auteur" / "beginner" / "acceptance" / f"{chapter_index}-{command_id}.json"
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("status") == "complete":
            return AcceptanceReconciliation(chapter_index, command_id, True, receipt.get("authority_result"))
    receipt = {
        "status": "started",
        "chapter_index": chapter_index,
        "command_id": command_id,
        "candidate": latest.name,
        "candidate_sha256": hashlib.sha256(latest.read_bytes()).hexdigest(),
    }
    _write_json_atomic(receipt_path, receipt)

    # If the owning service completed before the process died, the matching
    # final artifact is sufficient to reconcile without replaying acceptance.
    reconciled = final.is_file() and final.read_bytes() == latest.read_bytes()
    if reconciled:
        result: Any = {"accepted": True, "reconciled_from_authority": True}
    else:
        if owner is None:
            from auteur.cli_handlers import handle_accept
            from auteur.project import Project

            project = Project.load(project_root)
            result = handle_accept(project, chapter_index)
        else:
            result = owner(project_root, chapter_index)
        if not final.is_file() or final.read_bytes() != latest.read_bytes():
            raise RuntimeError("acceptance owner did not produce matching final.md")
    receipt.update({"status": "complete", "authority_result": _receipt_value(result)})
    _write_json_atomic(receipt_path, receipt)
    return AcceptanceReconciliation(chapter_index, command_id, reconciled, result)


def prepare_revision_handoff(
    project_root: Path,
    chapter_index: int,
    *,
    command_id: str,
    decision: str,
    route: str,
) -> RevisionHandoff:
    """Persist a non-canonical routing handoff for retry or deterministic editing."""
    if route not in {"retry", "editing"}:
        raise ValueError("route must be 'retry' or 'editing'")
    chapter_dir = project_root / "chapters" / f"{chapter_index:02d}"
    if not chapter_dir.is_dir():
        chapter_dir = project_root / "chapters" / str(chapter_index)
    drafts = sorted(chapter_dir.glob("draft_v*.md"), key=_draft_version)
    if not drafts:
        raise FileNotFoundError(f"no candidate draft for chapter {chapter_index}")
    source = drafts[-1]
    path = project_root / ".auteur" / "beginner" / "revisions" / f"{chapter_index}-{command_id}.json"
    payload = {
        "canonical": False,
        "chapter_index": chapter_index,
        "source_draft": source.name,
        "decision": decision,
        "route": route,
    }
    _write_json_atomic(path, payload)
    return RevisionHandoff(chapter_index, source.name, route, decision, path)


def project_chapter_outcome(project_root: Path, chapter_index: int) -> dict[str, Any]:
    """Return a derived expression/state comparison for an accepted chapter."""
    chapter_dir = project_root / "chapters" / f"{chapter_index:02d}"
    if not (chapter_dir / "final.md").is_file():
        chapter_dir = project_root / "chapters" / str(chapter_index)
    final = chapter_dir / "final.md"
    if not final.is_file():
        raise FileNotFoundError(f"accepted chapter not found: {final}")
    events: list[Any] = []
    bible_path = project_root / "bible.json"
    if bible_path.is_file():
        data = json.loads(bible_path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("events"), list):
            events = [event for event in data["events"] if isinstance(event, dict) and event.get("chapter_index") == chapter_index]
    return {
        "accepted_expression": final.name,
        "chapter_index": chapter_index,
        "events": events,
        "realization_delta": "review_required",
        "source_refs": [f"chapters/{chapter_index:02d}/final.md"],
    }


def project_next_chapter_context(project_root: Path, chapter_index: int) -> dict[str, Any]:
    """Project context for planning N from accepted prior chapter artifacts."""
    prior_refs: list[dict[str, Any]] = []
    for path in sorted((project_root / "chapters").glob("*/final.md")) if (project_root / "chapters").is_dir() else []:
        match = re.fullmatch(r"\d+", path.parent.name)
        if match and int(path.parent.name) < chapter_index:
            prior_refs.append({"chapter_index": int(path.parent.name), "path": path.relative_to(project_root).as_posix()})
    bible: Any = {}
    bible_path = project_root / "bible.json"
    if bible_path.is_file():
        bible = json.loads(bible_path.read_text(encoding="utf-8"))
    return {
        "chapter_index": chapter_index,
        "prior_accepted_chapters": [ref["chapter_index"] for ref in prior_refs],
        "prior_chapter_refs": prior_refs,
        "realized_state": bible,
        "outline_purpose": None,
    }
