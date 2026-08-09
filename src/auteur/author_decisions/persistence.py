"""Persistence for author decision artifacts and acceptance records.

Author-owned artifacts live at <project>/author_decisions/<id>.yaml (versionable,
author-editable). Tool-written acceptance records live at
<project>/author_decisions/.acceptance/<id>.yaml (never authored by hand).
Writes are atomic (temp file + os.replace). Fingerprints are sha256 of file bytes
and are the deterministic basis for staleness checks.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml as _yaml

from auteur.author_decisions.models import DecisionValidationError, validate_decision_id


def artifact_path(project: Path, decision_id: str) -> Path:
    validate_decision_id(decision_id)  # F1: no path is derived from an unvalidated ID
    return project / "author_decisions" / f"{decision_id}.yaml"


def acceptance_path(project: Path, decision_id: str) -> Path:
    validate_decision_id(decision_id)  # F1
    return project / "author_decisions" / ".acceptance" / f"{decision_id}.yaml"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _yaml.safe_dump(data, sort_keys=False)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def read_yaml(path: Path) -> dict:
    data = _yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected a YAML mapping: {path}")
    return data


def write_acceptance_record(
    project: Path,
    decision_id: str,
    *,
    identity_fingerprint: str,
    blueprint_fingerprint: str,
    resolved_constraints: list[dict],
    blocked_count: int,
    blocked_provenance_verified: bool,
    resolved_defaults: dict,
) -> Path:
    record = {
        "decision_id": decision_id,
        "accepted_at": datetime.now(timezone.utc).isoformat(),
        "identity_fingerprint": identity_fingerprint,
        "blueprint_fingerprint": blueprint_fingerprint,
        "resolved_constraints": resolved_constraints,
        "blocked_count": blocked_count,
        "blocked_provenance_verified": blocked_provenance_verified,
        "resolved_defaults": resolved_defaults,
    }
    out = acceptance_path(project, decision_id)
    atomic_write_yaml(out, record)
    return out


def load_acceptance_record(project: Path, decision_id: str) -> dict | None:
    path = acceptance_path(project, decision_id)
    if not path.exists():
        return None
    return read_yaml(path)
