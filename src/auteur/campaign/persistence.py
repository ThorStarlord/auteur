from __future__ import annotations

import os
import tempfile
from pathlib import Path

import yaml
from pydantic import ValidationError

from auteur.campaign.models import Campaign, CampaignStateError


class CampaignStore:
    """Atomic persistence adapter for the project-local Campaign record."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.path = self.project_root / ".auteur" / "campaign.yaml"

    def save(self, campaign: Campaign) -> Path:
        if campaign.schema_version != 1:
            raise CampaignStateError(
                f"unsupported schema_version: {campaign.schema_version}"
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = yaml.safe_dump(campaign.model_dump(mode="json"), sort_keys=False)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        except (OSError, ValueError) as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise CampaignStateError(f"campaign write failed: {exc}") from exc
        return self.path

    def load(self) -> Campaign:
        if not self.path.exists():
            raise CampaignStateError(f"campaign state is absent: {self.path}")
        try:
            raw = yaml.safe_load(self.path.read_text(encoding="utf-8"))
            campaign = Campaign.model_validate(raw)
        except (OSError, yaml.YAMLError, ValidationError, TypeError, ValueError) as exc:
            raise CampaignStateError(f"campaign state is invalid: {exc}") from exc
        if campaign.schema_version != 1:
            raise CampaignStateError(
                f"unsupported schema_version: {campaign.schema_version}"
            )
        return campaign
