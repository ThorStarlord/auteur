from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from auteur.campaign.handoff import HandoffStore, resume_handoff
from auteur.campaign.models import Campaign
from auteur.campaign.persistence import CampaignStore


def test_handoff_round_trips_and_resume_is_plan_only(tmp_path: Path) -> None:
    source = tmp_path / "story_identity.yaml"
    source.write_text("identity: current\n", encoding="utf-8")
    campaign = Campaign(
        campaign_id="c1",
        project_id="p1",
        source_revisions={source.name: hashlib.sha256(source.read_bytes()).hexdigest()},
    )
    CampaignStore(tmp_path).save(campaign)
    store = HandoffStore(tmp_path)
    handoff = store.create(campaign, operation="prepare-acceptance")

    result = resume_handoff(tmp_path, handoff.handoff_id)

    assert result.allowed is True
    assert result.mutates_canonical is False
    assert result.next_action == "prepare-acceptance"
    assert store.load(handoff.handoff_id) == handoff


def test_resume_rejects_stale_handoff_without_mutating_campaign(tmp_path: Path) -> None:
    source = tmp_path / "story_identity.yaml"
    source.write_text("identity: current\n", encoding="utf-8")
    campaign = Campaign(
        campaign_id="c1",
        project_id="p1",
        source_revisions={source.name: hashlib.sha256(source.read_bytes()).hexdigest()},
    )
    CampaignStore(tmp_path).save(campaign)
    handoff = HandoffStore(tmp_path).create(campaign, operation="accept")
    source.write_text("identity: changed\n", encoding="utf-8")

    result = resume_handoff(tmp_path, handoff.handoff_id)

    assert result.allowed is False
    assert result.code == "STALE_SOURCE"
    assert result.mutates_canonical is False


def test_missing_handoff_is_an_explicit_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="handoff not found"):
        resume_handoff(tmp_path, "missing")
