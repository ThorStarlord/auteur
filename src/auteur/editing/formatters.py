from __future__ import annotations

from pathlib import Path


def format_edit_review_success(artifact_dir: Path) -> str:
    return f"Edit review written to {artifact_dir}"


def format_edit_patch_status_success(patch_id: str, status: str) -> str:
    return f"Patch {patch_id} marked {status}."


def format_edit_apply_success(patch_id: str, revised_path: Path) -> str:
    return f"Patch {patch_id} applied. Revised draft written to {revised_path}"


def format_edit_error(message: str) -> str:
    return f"Error: {message}"

