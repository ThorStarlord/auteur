from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from auteur.campaign.inspection import inspect_campaign
from auteur.campaign.models import Campaign
from auteur.campaign.persistence import CampaignStore


class Handoff(BaseModel):
    schema_version: int = 1
    handoff_id: str = Field(min_length=1)
    campaign_id: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    source_revisions: dict[str, str]
    authority: Literal["read_only", "proposal", "canonical"] = "proposal"
    status: Literal["pending", "resumed", "rejected"] = "pending"


class ResumeResult(BaseModel):
    allowed: bool
    code: str
    next_action: str = ""
    mutates_canonical: bool = False
    findings: list[dict[str, str]] = Field(default_factory=list)


class HandoffStore:
    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.directory = self.project_root / ".auteur" / "handoffs"

    def create(self, campaign: Campaign, *, operation: str) -> Handoff:
        handoff = Handoff(
            handoff_id=f"handoff-{campaign.campaign_id}-{len(campaign.pending_handoffs) + 1}",
            campaign_id=campaign.campaign_id,
            operation=operation,
            source_revisions=dict(campaign.source_revisions),
            authority="proposal" if operation != "inspect" else "read_only",
        )
        self._write(handoff)
        return handoff

    def load(self, handoff_id: str) -> Handoff:
        path = self.directory / f"{handoff_id}.yaml"
        if not path.is_file():
            raise FileNotFoundError(f"handoff not found: {handoff_id}")
        try:
            return Handoff.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        except (OSError, yaml.YAMLError, TypeError, ValueError) as exc:
            raise ValueError(f"handoff state is invalid: {handoff_id}") from exc

    def _write(self, handoff: Handoff) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.directory / f"{handoff.handoff_id}.yaml"
        fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=self.directory)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(yaml.safe_dump(handoff.model_dump(mode="json"), sort_keys=False))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise


def resume_handoff(project_root: Path, handoff_id: str) -> ResumeResult:
    store = HandoffStore(project_root)
    handoff = store.load(handoff_id)
    if handoff.status != "pending":
        return ResumeResult(allowed=False, code="HANDOFF_NOT_PENDING")
    campaign = CampaignStore(project_root).load()
    if campaign.campaign_id != handoff.campaign_id:
        return ResumeResult(allowed=False, code="CAMPAIGN_MISMATCH")
    report = inspect_campaign(project_root, campaign.model_copy(update={"source_revisions": handoff.source_revisions}))
    if not report.valid:
        return ResumeResult(
            allowed=False,
            code=report.findings[0].code,
            findings=[finding.model_dump() for finding in report.findings],
        )
    return ResumeResult(
        allowed=True,
        code="RESUME_PLAN_READY",
        next_action=handoff.operation,
        mutates_canonical=False,
    )
