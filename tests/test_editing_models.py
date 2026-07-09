from __future__ import annotations

import json

import pytest
import yaml
from pydantic import ValidationError

from auteur.editing.models import (
    EditFinding,
    EditLocation,
    EditReport,
    PatchProposal,
    PatchStatus,
)


def test_editing_models_round_trip_through_json_and_yaml() -> None:
    location = EditLocation(file="chapters/03/draft_v2.md", start_line=4, end_line=4)
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
    report = EditReport(
        chapter=3,
        source_file="chapters/03/draft_v2.md",
        source_draft="draft_v2.md",
        passes=["aiisms"],
        findings=[finding],
        patches=[patch],
    )

    json_payload = json.loads(report.model_dump_json())
    yaml_payload = yaml.safe_load(yaml.safe_dump(report.model_dump(mode="json")))

    assert EditReport.model_validate(json_payload).patches[0].status is PatchStatus.PROPOSED
    assert EditReport.model_validate(yaml_payload).findings[0].id == "finding_001"


def test_findings_may_exist_without_patches() -> None:
    report = EditReport(
        chapter=3,
        source_file="chapters/03/draft_v2.md",
        source_draft="draft_v2.md",
        passes=["aiisms"],
        findings=[
            EditFinding(
                id="finding_001",
                pass_name="aiisms",
                issue_type="ai_ism",
                severity="warning",
                location=EditLocation(file="chapters/03/draft_v2.md", start_line=1, end_line=1),
                evidence="a whisper of",
                rationale="Stock phrasing was detected.",
            )
        ],
        patches=[],
    )

    assert len(report.findings) == 1
    assert report.patches == []


def test_invalid_patch_status_fails_schema_validation() -> None:
    with pytest.raises(ValidationError):
        PatchProposal(
            id="patch_001",
            finding_id="finding_001",
            patch_type="replace_text",
            location=EditLocation(file="draft.md", start_line=1, end_line=1),
            original="stood as a testament to",
            replacement="still carried",
            confidence=0.72,
            status="done",
        )


def test_location_requires_valid_line_range() -> None:
    with pytest.raises(ValidationError):
        EditLocation(file="draft.md", start_line=4, end_line=3)
