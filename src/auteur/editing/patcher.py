from __future__ import annotations

from dataclasses import dataclass

from auteur.editing.models import PatchProposal, PatchStatus


@dataclass(frozen=True)
class PatchApplicationResult:
    text: str
    patch: PatchProposal


def apply_patch_to_text(text: str, patch: PatchProposal) -> PatchApplicationResult:
    if patch.status is not PatchStatus.ACCEPTED:
        raise ValueError("patch must be accepted before application")

    lines = text.splitlines(keepends=True)
    start = patch.location.start_line - 1
    end = patch.location.end_line
    selected = "".join(lines[start:end])
    if selected.count(patch.original) != 1:
        return PatchApplicationResult(text=text, patch=patch.model_copy(update={"status": PatchStatus.STALE}))

    updated_selected = selected.replace(patch.original, patch.replacement, 1)
    updated_lines = [*lines]
    updated_lines[start:end] = [updated_selected]
    return PatchApplicationResult(
        text="".join(updated_lines),
        patch=patch.model_copy(update={"status": PatchStatus.APPLIED}),
    )

