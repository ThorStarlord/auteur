from __future__ import annotations

import hashlib
import json
import posixpath
import zipfile
from pathlib import Path

from pydantic import BaseModel, Field

from auteur.campaign.persistence import CampaignStore


class BundleError(RuntimeError):
    """A Campaign bundle cannot be safely exported or staged."""


class BundleInspection(BaseModel):
    valid: bool
    bundle_version: int = 1
    campaign_id: str
    files: list[str] = Field(default_factory=list)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def export_bundle(project_root: Path, output: Path) -> Path:
    """Write a deterministic Campaign bundle without changing project state."""
    root = Path(project_root)
    campaign_path = CampaignStore(root).path
    campaign = CampaignStore(root).load()
    members: dict[str, bytes] = {".auteur/campaign.yaml": campaign_path.read_bytes()}
    for relative_path in sorted(campaign.source_revisions):
        path = root / relative_path
        if not path.is_file():
            raise BundleError(f"source artifact is missing: {relative_path}")
        members[relative_path.replace("\\", "/")] = path.read_bytes()
    manifest = {
        "bundle_version": 1,
        "campaign_id": campaign.campaign_id,
        "project_id": campaign.project_id,
        "files": [
            {"path": name, "sha256": _digest(data)}
            for name, data in sorted(members.items())
        ],
    }
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        _write_member(archive, "manifest.json", json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode())
        for name, data in sorted(members.items()):
            _write_member(archive, name, data)
    return output


def inspect_bundle(bundle: Path, staging: Path) -> BundleInspection:
    """Verify and extract a bundle into an isolated staging directory."""
    bundle = Path(bundle)
    try:
        with zipfile.ZipFile(bundle) as archive:
            names = archive.namelist()
            _validate_names(names)
            manifest = json.loads(archive.read("manifest.json"))
            if manifest.get("bundle_version") != 1 or not manifest.get("campaign_id"):
                raise BundleError("manifest is invalid")
            entries = manifest.get("files")
            if not isinstance(entries, list):
                raise BundleError("manifest is invalid")
            for entry in entries:
                name = entry.get("path")
                if not isinstance(name, str) or name not in names:
                    raise BundleError("manifest is invalid")
                if _digest(archive.read(name)) != entry.get("sha256"):
                    raise BundleError(f"bundle hash mismatch: {name}")
            target = Path(staging)
            target.mkdir(parents=True, exist_ok=True)
            for name in names:
                if name == "manifest.json":
                    continue
                destination = target / Path(name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.read(name))
    except BundleError:
        raise
    except (OSError, KeyError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        raise BundleError(f"manifest is invalid: {exc}") from exc
    return BundleInspection(
        valid=True,
        campaign_id=manifest["campaign_id"],
        files=sorted(entry["path"] for entry in manifest["files"]),
    )


def _validate_names(names: list[str]) -> None:
    for name in names:
        normalized = posixpath.normpath(name)
        if name.startswith("/") or normalized == ".." or normalized.startswith("../"):
            raise BundleError(f"unsafe bundle path: {name}")


def _write_member(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o600 << 16
    archive.writestr(info, data)
