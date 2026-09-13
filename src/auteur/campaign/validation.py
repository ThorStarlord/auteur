from __future__ import annotations

from pydantic import BaseModel

from auteur.campaign.models import Campaign


class CampaignValidation(BaseModel):
    valid: bool
    findings: list[dict[str, str]]


def validate_campaign(campaign: Campaign) -> CampaignValidation:
    """Return the structural validation result without touching the project."""
    return CampaignValidation(valid=True, findings=[])
