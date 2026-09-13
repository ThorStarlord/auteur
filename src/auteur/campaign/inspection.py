from __future__ import annotations

import hashlib
from pathlib import Path

from pydantic import BaseModel

from auteur.campaign.models import Campaign
from auteur.campaign.validation import validate_campaign


class CampaignFinding(BaseModel):
    code: str
    severity: str
    message: str
    path: str = ""


class CampaignInspection(BaseModel):
    valid: bool
    campaign_id: str
    rule_version: str = "campaign-inspection-v1"
    findings: list[CampaignFinding]


def inspect_campaign(project_root: Path, campaign: Campaign) -> CampaignInspection:
    """Check Campaign dependencies deterministically and read-only."""
    findings: list[CampaignFinding] = []
    shape = validate_campaign(campaign)
    for finding in shape.findings:
        findings.append(
            CampaignFinding(
                code="INVALID_CAMPAIGN",
                severity="blocking",
                message=finding["message"],
            )
        )

    for relative_path, expected_hash in sorted(campaign.source_revisions.items()):
        path = project_root / relative_path
        if not path.is_file():
            findings.append(
                CampaignFinding(
                    code="MISSING_SOURCE",
                    severity="blocking",
                    message=f"source artifact is missing: {relative_path}",
                    path=relative_path,
                )
            )
            continue
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            findings.append(
                CampaignFinding(
                    code="STALE_SOURCE",
                    severity="blocking",
                    message=f"source artifact revision is stale: {relative_path}",
                    path=relative_path,
                )
            )

    for handoff_id in sorted(campaign.pending_handoffs):
        findings.append(
            CampaignFinding(
                code="PENDING_HANDOFF",
                severity="blocking",
                message=f"handoff requires explicit recovery: {handoff_id}",
                path=handoff_id,
            )
        )

    return CampaignInspection(
        valid=not findings,
        campaign_id=campaign.campaign_id,
        findings=findings,
    )
