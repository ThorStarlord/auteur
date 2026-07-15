"""Bootstrap adapter for the committed canonical-story reference.

This adapter only maps reference files into a temporary project and delegates
lifecycle state to public provenance APIs. It does not fabricate accepted
metadata sidecars or alter the committed example.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from auteur.provenance import ArtifactStore


class CanonicalStoryBootstrap:
    def __init__(self, reference_root: Path) -> None:
        self.reference_root = Path(reference_root)

    def copy_to(self, workspace: Path) -> Path:
        destination = Path(workspace) / "canonical_story"
        shutil.copytree(self.reference_root, destination)
        return destination

    def accept_scene_realizations(self, project_root: Path, *, accepted_by: str = "canonical-dogfood") -> list[dict[str, Any]]:
        """Accept the five committed realization documents through ArtifactStore."""
        store = ArtifactStore(project_root)
        accepted = []
        for path in sorted(Path(project_root).glob("canonical_story/chapter_01/scene_*/realization.yaml")):
            metadata = store.accept(path, "scene_realization", accepted_by=accepted_by,
                                    rationale="canonical demonstration project bootstrap")
            if metadata is not None:
                accepted.append(metadata.model_dump(mode="json"))
        return accepted

    @staticmethod
    def external_edit_path(project_root: Path) -> Path:
        return Path(project_root) / "canonical_story" / "external_edit.md"

