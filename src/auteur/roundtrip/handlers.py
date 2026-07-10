from __future__ import annotations

import difflib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from auteur.relations.diagnostics import diagnose_relation_changes
from auteur.relations.models import RelationChangeSet
from auteur.relations.serializers import load_relation_map


@dataclass(frozen=True)
class RoundTripResult:
    is_success: bool
    exit_code: int = 0
    error: str | None = None
    data: object | None = None


@dataclass(frozen=True)
class ExportData:
    source: Path
    output: Path
    text: str


@dataclass(frozen=True)
class ImportData:
    source_draft: Path
    artifact_dir: Path
    run_id: str
    imported_file: Path
    imported_text: str
    diff_report: dict
    drift_report: dict
    proposals: dict
    manifest: dict


def latest_draft_path(project: Path, chapter: int) -> Path:
    chapter_dir = project / "chapters" / f"{chapter:02d}"
    drafts = sorted(chapter_dir.glob("draft_v*.md"), key=_draft_version)
    if not drafts:
        raise FileNotFoundError(f"no draft_v*.md found in {chapter_dir}")
    return drafts[-1]


def resolve_draft_path(project: Path, chapter: int, draft: str | None) -> Path:
    if draft is None:
        return latest_draft_path(project, chapter)
    draft_path = Path(draft)
    if draft_path.is_absolute():
        return draft_path
    return project / "chapters" / f"{chapter:02d}" / draft


def handle_export_chapter(project: Path, chapter: int, fmt: str, draft: str | None = None) -> RoundTripResult:
    if fmt != "md":
        return RoundTripResult(is_success=False, exit_code=1, error="only markdown export is supported in V1")
    try:
        source = resolve_draft_path(project, chapter, draft)
        text = source.read_text(encoding="utf-8")
        output = project / "exports" / f"chapter_{chapter:02d}" / source.name
        return RoundTripResult(is_success=True, data=ExportData(source=source, output=output, text=text))
    except Exception as exc:
        return RoundTripResult(is_success=False, exit_code=1, error=str(exc))


def handle_import_chapter(project: Path, chapter: int, edited_markdown: Path, draft: str | None = None) -> RoundTripResult:
    try:
        source = resolve_draft_path(project, chapter, draft)
        old_text = read_text_normalized(source)
        imported_text = read_text_normalized(edited_markdown)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        run_id = timestamp
        artifact_dir = project / "imports" / f"chapter_{chapter:02d}" / run_id
        diff_report = build_diff_report(source.name, old_text, imported_text)
        drift_report, proposals = build_drift_artifacts(project, chapter)
        manifest = {
            "run_id": run_id,
            "chapter": chapter,
            "source_draft": source.name,
            "imported_file": str(edited_markdown),
            "artifacts": {
                "imported_draft": "imported_draft.md",
                "diff_report": "diff_report.json",
                "drift_report": "drift_report.json",
                "canon_update_proposals": "canon_update_proposals.yaml",
            },
            "timestamp": timestamp,
        }
        return RoundTripResult(
            is_success=True,
            data=ImportData(
                source_draft=source,
                artifact_dir=artifact_dir,
                run_id=run_id,
                imported_file=edited_markdown,
                imported_text=imported_text,
                diff_report=diff_report,
                drift_report=drift_report,
                proposals=proposals,
                manifest=manifest,
            ),
        )
    except Exception as exc:
        return RoundTripResult(is_success=False, exit_code=1, error=str(exc))


def build_diff_report(source_draft: str, old_text: str, new_text: str) -> dict:
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    changed_lines = []
    for opcode in difflib.SequenceMatcher(a=old_lines, b=new_lines).get_opcodes():
        tag, old_start, old_end, new_start, new_end = opcode
        if tag == "equal":
            continue
        max_len = max(old_end - old_start, new_end - new_start)
        for offset in range(max_len):
            changed_lines.append(
                {
                    "type": tag,
                    "old_line": old_start + offset + 1 if old_start + offset < old_end else None,
                    "new_line": new_start + offset + 1 if new_start + offset < new_end else None,
                    "old": old_lines[old_start + offset] if old_start + offset < old_end else None,
                    "new": new_lines[new_start + offset] if new_start + offset < new_end else None,
                }
            )
    return {"source_draft": source_draft, "changed_lines": changed_lines}


def build_drift_artifacts(project: Path, chapter: int) -> tuple[dict, dict]:
    changes_path = project / "chapters" / f"{chapter:02d}" / "relation_changes.yaml"
    diagnostics = []
    proposals = []
    if changes_path.exists() and (project / "relations.yaml").exists():
        relation_map = load_relation_map(project)
        changes = RelationChangeSet.from_yaml(changes_path)
        diagnostics = [item.model_dump(mode="json") for item in diagnose_relation_changes(relation_map, changes)]
        for index, change in enumerate(changes.relation_changes, start=1):
            proposals.append(
                {
                    "id": f"relation_update_{chapter:02d}_{index:03d}",
                    "type": "relation_update",
                    "relation": change.relation,
                    "chapter": chapter,
                    "changes": change.metric_deltas(),
                    "reason": change.reason,
                    "status": "proposed",
                }
            )
    return {
        "analysis_mode": "declared_relation_changes",
        "note": (
            "V1 drift analysis uses chapter relation_changes.yaml. "
            "It does not infer relationship drift from imported prose."
        ),
        "diagnostics": diagnostics,
    }, {"proposals": proposals}


def resolve_import_run_dir(project: Path, chapter: int, run_id: str) -> Path:
    artifact_dir = project / "imports" / f"chapter_{chapter:02d}" / run_id
    if not artifact_dir.is_dir():
        raise FileNotFoundError(f"import run not found: {artifact_dir}")
    return artifact_dir


def confirm_import_proposal(project: Path, chapter: int, run_id: str, proposal_id: str) -> RoundTripResult:
    try:
        artifact_dir = resolve_import_run_dir(project, chapter, run_id)
        return RoundTripResult(is_success=True, data={"artifact_dir": artifact_dir, "proposal_id": proposal_id})
    except Exception as exc:
        return RoundTripResult(is_success=False, exit_code=1, error=str(exc))


def promote_imported_draft(project: Path, chapter: int, run_id: str) -> RoundTripResult:
    try:
        artifact_dir = resolve_import_run_dir(project, chapter, run_id)
        imported = artifact_dir / "imported_draft.md"
        text = imported.read_text(encoding="utf-8")
        chapter_dir = project / "chapters" / f"{chapter:02d}"
        versions = [_draft_version(path) for path in chapter_dir.glob("draft_v*.md")]
        next_version = max(versions, default=0) + 1
        output = chapter_dir / f"draft_v{next_version}.md"
        return RoundTripResult(is_success=True, data={"output": output, "text": text})
    except Exception as exc:
        return RoundTripResult(is_success=False, exit_code=1, error=str(exc))


def _draft_version(path: Path) -> int:
    try:
        return int(path.stem.removeprefix("draft_v"))
    except ValueError:
        return -1


def read_text_normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").lstrip("\ufeff")
