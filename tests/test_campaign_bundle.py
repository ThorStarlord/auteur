from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest

from auteur.campaign.bundle import BundleError, export_bundle, inspect_bundle
from auteur.campaign.models import Campaign
from auteur.campaign.persistence import CampaignStore


def test_bundle_export_is_deterministic_and_import_is_isolated(tmp_path: Path) -> None:
    source = tmp_path / "story_identity.yaml"
    source.write_text("identity: current\n", encoding="utf-8")
    campaign = Campaign(
        campaign_id="c1",
        project_id="p1",
        source_revisions={source.name: hashlib.sha256(source.read_bytes()).hexdigest()},
    )
    CampaignStore(tmp_path).save(campaign)
    first = tmp_path / "first.auteur-bundle"
    second = tmp_path / "second.auteur-bundle"

    export_bundle(tmp_path, first)
    export_bundle(tmp_path, second)

    assert first.read_bytes() == second.read_bytes()
    staging = tmp_path / "staging"
    report = inspect_bundle(first, staging)
    assert report.valid is True
    assert (staging / ".auteur" / "campaign.yaml").is_file()
    assert (tmp_path / "story_identity.yaml").read_text(encoding="utf-8") == "identity: current\n"


def test_bundle_rejects_path_traversal(tmp_path: Path) -> None:
    bundle = tmp_path / "bad.bundle"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("../escape.txt", "unsafe")

    with pytest.raises(BundleError, match="unsafe bundle path"):
        inspect_bundle(bundle, tmp_path / "staging")


def test_bundle_rejects_corrupt_manifest(tmp_path: Path) -> None:
    bundle = tmp_path / "bad.bundle"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("manifest.json", "{}")

    with pytest.raises(BundleError, match="manifest is invalid"):
        inspect_bundle(bundle, tmp_path / "staging")
