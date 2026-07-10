from __future__ import annotations

import json

import yaml

from auteur.editing.models import EditFinding, EditLocation, EditReport, PatchProposal
from auteur.editing.serializers import write_patch_proposals, write_revised_draft, write_review_artifacts


def _report() -> EditReport:
    location = EditLocation(file="chapters/03/draft_v2.md", start_line=1, end_line=1)
    finding = EditFinding(
        id="finding_001",
        pass_name="aiisms",
        issue_type="ai_ism",
        severity="warning",
        location=location,
        evidence="stood as a testament to",
        rationale="Stock phrasing can flatten the image.",
    )
    patch = PatchProposal(
        id="patch_001",
        finding_id="finding_001",
        patch_type="replace_text",
        location=location,
        original="stood as a testament to",
        replacement="still carried",
        confidence=0.72,
        status="proposed",
    )
    return EditReport(
        chapter=3,
        source_file="chapters/03/draft_v2.md",
        source_draft="draft_v2.md",
        passes=["aiisms"],
        findings=[finding],
        patches=[patch],
    )


def test_review_artifacts_use_versioned_edit_directory(tmp_path) -> None:
    artifact_dir = tmp_path / "project" / "editing" / "chapter_03" / "draft_v2"

    written = write_review_artifacts(_report(), artifact_dir)

    assert written.report_path == artifact_dir / "edit_report.json"
    assert written.patch_path == artifact_dir / "patch_proposals.yaml"
    assert written.review_path == artifact_dir / "review.md"
    assert json.loads(written.report_path.read_text(encoding="utf-8"))["source_draft"] == "draft_v2.md"
    assert yaml.safe_load(written.patch_path.read_text(encoding="utf-8"))["patches"][0]["id"] == "patch_001"
    review = written.review_path.read_text(encoding="utf-8")
    assert "Deterministic suggestion text is safe but simple" in review
    assert "## Next Steps" in review
    assert "auteur edit accept" in review
    assert "auteur edit reject" in review
    assert "auteur edit apply" in review


def test_patch_proposal_write_is_stable_yaml(tmp_path) -> None:
    patch_path = tmp_path / "patch_proposals.yaml"

    write_patch_proposals(_report().patches, patch_path)

    payload = yaml.safe_load(patch_path.read_text(encoding="utf-8"))
    assert list(payload) == ["patches"]
    assert payload["patches"][0]["status"] == "proposed"


def test_revised_draft_write_is_deterministic(tmp_path) -> None:
    output = write_revised_draft("The tower still carried the old threat.\n", tmp_path)

    assert output == tmp_path / "revised_draft.md"
    assert output.read_text(encoding="utf-8") == "The tower still carried the old threat.\n"
