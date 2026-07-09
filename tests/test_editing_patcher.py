from __future__ import annotations

import pytest

from auteur.editing.models import EditLocation, PatchProposal, PatchStatus
from auteur.editing.patcher import apply_patch_to_text


def _patch(*, line: int, status: str = "accepted") -> PatchProposal:
    return PatchProposal(
        id="patch_001",
        finding_id="finding_001",
        patch_type="replace_text",
        location=EditLocation(file="chapters/03/draft_v2.md", start_line=line, end_line=line),
        original="stood as a testament to",
        replacement="still carried",
        confidence=0.72,
        status=status,
    )


def test_accepted_patch_applies_only_to_expected_line_range() -> None:
    text = (
        "The arch stood as a testament to old kings.\n"
        "Mara waited.\n"
        "The tower stood as a testament to bad decisions.\n"
    )

    result = apply_patch_to_text(text, _patch(line=3))

    assert "The arch stood as a testament to old kings." in result.text
    assert "The tower still carried bad decisions." in result.text
    assert result.patch.status is PatchStatus.APPLIED


@pytest.mark.parametrize("status", ["proposed", "rejected"])
def test_only_accepted_patches_apply(status: str) -> None:
    with pytest.raises(ValueError):
        apply_patch_to_text("The tower stood as a testament to failure.\n", _patch(line=1, status=status))


def test_stale_patch_is_detected_from_expected_line_range() -> None:
    result = apply_patch_to_text(
        "The tower refused to carry the old boast.\n",
        _patch(line=1),
    )

    assert result.text == "The tower refused to carry the old boast.\n"
    assert result.patch.status is PatchStatus.STALE


def test_patch_is_stale_when_expected_range_has_multiple_matches() -> None:
    result = apply_patch_to_text(
        "stood as a testament to, stood as a testament to\n",
        _patch(line=1),
    )

    assert result.patch.status is PatchStatus.STALE
    assert result.text == "stood as a testament to, stood as a testament to\n"
