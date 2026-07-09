from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from auteur.editing.models import EditReport, PatchProposal, PatchStatus
from auteur.editing.patcher import apply_patch_to_text
from auteur.editing.runner import run_edit_review


@dataclass(frozen=True)
class EditHandlerResult:
    is_success: bool
    exit_code: int = 0
    error: str | None = None
    data: object | None = None


@dataclass(frozen=True)
class EditReviewData:
    report: EditReport
    artifact_dir: Path


@dataclass(frozen=True)
class EditPatchStateData:
    patches: list[PatchProposal]
    artifact_dir: Path
    patch_id: str


@dataclass(frozen=True)
class EditApplyData:
    patches: list[PatchProposal]
    artifact_dir: Path
    revised_text: str | None
    patch_id: str
    stale: bool = False


def normalize_passes(raw_passes: str | list[str]) -> list[str]:
    if isinstance(raw_passes, str):
        return [item.strip() for item in raw_passes.split(",") if item.strip()]
    passes: list[str] = []
    for value in raw_passes:
        passes.extend(item.strip() for item in value.split(",") if item.strip())
    return passes or ["aiisms"]


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


def artifact_dir_for(project: Path, chapter: int, draft_path: Path) -> Path:
    return project / "editing" / f"chapter_{chapter:02d}" / draft_path.stem


def handle_edit_review(project: Path, chapter: int, raw_passes: str | list[str], draft: str | None = None) -> EditHandlerResult:
    try:
        draft_path = resolve_draft_path(project, chapter, draft)
        text = draft_path.read_text(encoding="utf-8")
        passes = normalize_passes(raw_passes)
        report = run_edit_review(
            text,
            source_file=draft_path,
            chapter=chapter,
            source_draft=draft_path.name,
            passes=passes,
        )
        return EditHandlerResult(
            is_success=True,
            data=EditReviewData(report=report, artifact_dir=artifact_dir_for(project, chapter, draft_path)),
        )
    except Exception as exc:
        return EditHandlerResult(is_success=False, exit_code=1, error=str(exc))


def handle_edit_accept(project: Path, chapter: int, patch_id: str, draft: str | None = None) -> EditHandlerResult:
    return _set_patch_status(project, chapter, patch_id, PatchStatus.ACCEPTED, draft)


def handle_edit_reject(project: Path, chapter: int, patch_id: str, draft: str | None = None) -> EditHandlerResult:
    return _set_patch_status(project, chapter, patch_id, PatchStatus.REJECTED, draft)


def handle_edit_apply(project: Path, chapter: int, patch_id: str, draft: str | None = None) -> EditHandlerResult:
    from auteur.editing.serializers import load_patch_proposals

    try:
        draft_path = resolve_draft_path(project, chapter, draft)
        artifact_dir = artifact_dir_for(project, chapter, draft_path)
        patches = load_patch_proposals(artifact_dir / "patch_proposals.yaml")
        patch = _find_patch(patches, patch_id)
        text = draft_path.read_text(encoding="utf-8")
        result = apply_patch_to_text(text, patch)
        updated = [result.patch if candidate.id == patch_id else candidate for candidate in patches]
        stale = result.patch.status is PatchStatus.STALE
        return EditHandlerResult(
            is_success=not stale,
            exit_code=2 if stale else 0,
            error="patch is stale" if stale else None,
            data=EditApplyData(
                patches=updated,
                artifact_dir=artifact_dir,
                revised_text=None if stale else result.text,
                patch_id=patch_id,
                stale=stale,
            ),
        )
    except Exception as exc:
        return EditHandlerResult(is_success=False, exit_code=1, error=str(exc))


def _set_patch_status(
    project: Path,
    chapter: int,
    patch_id: str,
    status: PatchStatus,
    draft: str | None,
) -> EditHandlerResult:
    from auteur.editing.serializers import load_patch_proposals

    try:
        draft_path = resolve_draft_path(project, chapter, draft)
        artifact_dir = artifact_dir_for(project, chapter, draft_path)
        patches = load_patch_proposals(artifact_dir / "patch_proposals.yaml")
        _find_patch(patches, patch_id)
        updated = [patch.model_copy(update={"status": status}) if patch.id == patch_id else patch for patch in patches]
        return EditHandlerResult(
            is_success=True,
            data=EditPatchStateData(patches=updated, artifact_dir=artifact_dir, patch_id=patch_id),
        )
    except Exception as exc:
        return EditHandlerResult(is_success=False, exit_code=1, error=str(exc))


def _find_patch(patches: list[PatchProposal], patch_id: str) -> PatchProposal:
    for patch in patches:
        if patch.id == patch_id:
            return patch
    raise ValueError(f"patch not found: {patch_id}")


def _draft_version(path: Path) -> int:
    try:
        return int(path.stem.removeprefix("draft_v"))
    except ValueError:
        return -1

