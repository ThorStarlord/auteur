from __future__ import annotations

import hashlib
from pathlib import Path

from auteur.campaign.inspection import inspect_campaign
from auteur.campaign.models import Campaign
from auteur.campaign.validation import validate_campaign


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_validation_accepts_well_shaped_campaign() -> None:
    result = validate_campaign(Campaign(campaign_id="c1", project_id="p1"))
    assert result.valid is True
    assert result.findings == []


def test_inspection_is_read_only_and_detects_stale_source(tmp_path: Path) -> None:
    source = tmp_path / "story_identity.yaml"
    source.write_text("version: one\n", encoding="utf-8")
    campaign = Campaign(
        campaign_id="c1",
        project_id="p1",
        source_revisions={source.name: "wrong"},
    )

    before = source.read_bytes()
    report = inspect_campaign(tmp_path, campaign)

    assert report.valid is False
    assert report.findings[0].code == "STALE_SOURCE"
    assert report.findings[0].severity == "blocking"
    assert source.read_bytes() == before


def test_inspection_order_is_deterministic(tmp_path: Path) -> None:
    campaign = Campaign(
        campaign_id="c1",
        project_id="p1",
        source_revisions={"z.yaml": "sha", "a.yaml": "sha"},
        pending_handoffs=["missing-z", "missing-a"],
    )

    first = inspect_campaign(tmp_path, campaign).model_dump(mode="json")
    second = inspect_campaign(tmp_path, campaign).model_dump(mode="json")

    assert first == second
    assert [finding["code"] for finding in first["findings"]] == [
        "MISSING_SOURCE",
        "MISSING_SOURCE",
        "PENDING_HANDOFF",
        "PENDING_HANDOFF",
    ]


def test_inspection_accepts_current_source(tmp_path: Path) -> None:
    source = tmp_path / "story_identity.yaml"
    source.write_text("version: one\n", encoding="utf-8")
    campaign = Campaign(source_revisions={source.name: _sha(source)}, campaign_id="c1", project_id="p1")

    report = inspect_campaign(tmp_path, campaign)

    assert report.valid is True
    assert report.findings == []
