"""Cross-domain revision validity seam backed by provenance metadata."""

from __future__ import annotations

from pathlib import Path

from auteur.provenance.store import ArtifactStore
from auteur.state_validity import StateValidity


class RevisionLedger:
    """Translate artifact/provenance state into the shared validity contract."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.store = ArtifactStore(self.project_root)

    def validate(self, path: Path, artifact_type: str) -> StateValidity:
        artifact_id = self.store.artifact_id_for(Path(path))
        try:
            metadata = self.store.status(Path(path), artifact_type)
        except (OSError, ValueError, KeyError) as exc:
            return StateValidity.unavailable(artifact_id, str(exc))
        if "artifact_missing" in metadata.invalid_reasons:
            return StateValidity.missing(artifact_id)
        if metadata.invalid_reasons:
            return StateValidity.malformed(artifact_id, "; ".join(metadata.invalid_reasons))
        if metadata.freshness == "stale":
            return StateValidity.stale(artifact_id, metadata.summary)
        if metadata.freshness != "fresh":
            return StateValidity.unknown(artifact_id, metadata.summary)
        return StateValidity.fresh(artifact_id)
