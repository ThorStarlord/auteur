from __future__ import annotations

import os
from pathlib import Path

import pytest

from auteur.campaign.models import Campaign, CampaignStateError
from auteur.campaign.persistence import CampaignStore


def test_campaign_round_trips_with_versioned_source_fingerprints(tmp_path: Path) -> None:
    store = CampaignStore(tmp_path)
    campaign = Campaign(
        campaign_id="campaign-1",
        project_id="project-1",
        phase="identity",
        source_revisions={"story_identity.yaml": "sha-a"},
    )

    saved = store.save(campaign)
    loaded = store.load()

    assert saved == tmp_path / ".auteur" / "campaign.yaml"
    assert loaded == campaign


def test_load_rejects_malformed_campaign_instead_of_treating_it_as_absent(tmp_path: Path) -> None:
    path = tmp_path / ".auteur" / "campaign.yaml"
    path.parent.mkdir()
    path.write_text("campaign_id: [broken", encoding="utf-8")

    with pytest.raises(CampaignStateError, match="campaign state is invalid"):
        CampaignStore(tmp_path).load()


def test_save_validation_failure_preserves_previous_bytes(tmp_path: Path) -> None:
    store = CampaignStore(tmp_path)
    store.save(Campaign(campaign_id="campaign-1", project_id="project-1"))
    path = store.path
    before = path.read_bytes()

    with pytest.raises(ValueError, match="campaign_id"):
        store.save(Campaign(campaign_id="", project_id="project-1"))

    assert path.read_bytes() == before


def test_unsupported_schema_version_is_blocking(tmp_path: Path) -> None:
    path = tmp_path / ".auteur" / "campaign.yaml"
    path.parent.mkdir()
    path.write_text(
        "schema_version: 99\ncampaign_id: campaign-1\nproject_id: project-1\n",
        encoding="utf-8",
    )

    with pytest.raises(CampaignStateError, match="unsupported schema_version"):
        CampaignStore(tmp_path).load()


def test_atomic_replace_failure_keeps_previous_campaign(tmp_path: Path, monkeypatch) -> None:
    store = CampaignStore(tmp_path)
    store.save(Campaign(campaign_id="campaign-1", project_id="project-1"))
    before = store.path.read_bytes()

    def fail_replace(*args):
        raise OSError("replace interrupted")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(CampaignStateError, match="campaign write failed"):
        store.save(Campaign(campaign_id="campaign-2", project_id="project-1"))

    assert store.path.read_bytes() == before
