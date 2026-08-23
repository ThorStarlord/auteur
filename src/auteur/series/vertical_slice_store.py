from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel

from auteur.provenance import ArtifactMetadata, ArtifactStore, Lifecycle
from auteur.series.vertical_slice_models import (
    AcceptedSeriesDirection,
    SeriesDirectionProposal,
)


class VerticalSliceStore:
    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root)
        self.root = (
            self.project_root / ".auteur" / "series" / "vertical-slice"
        )
        self.artifact_store = ArtifactStore(self.project_root)

    @property
    def accepted_series_direction_path(self) -> Path:
        return self.root / "accepted" / "series-direction.yaml"

    def series_direction_proposal_path(self, proposal_id: str) -> Path:
        if not proposal_id or Path(proposal_id).name != proposal_id:
            raise FileNotFoundError(
                f"Unknown Series Direction proposal: {proposal_id}"
            )
        return (
            self.root
            / "proposals"
            / "series-direction"
            / f"{proposal_id}.yaml"
        )

    def _write_model(self, path: Path, model: BaseModel) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        rendered = yaml.safe_dump(model.model_dump(mode="json"), sort_keys=False)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(path)

    def _restore_artifact_metadata(
        self,
        artifact_id: str,
        previous_sidecar: bytes | None,
        previous_revisions: set[int],
    ) -> None:
        sidecar = self.artifact_store.sidecar_path(artifact_id)
        sidecar.with_suffix(".tmp").unlink(missing_ok=True)
        if previous_sidecar is None:
            sidecar.unlink(missing_ok=True)
        else:
            temporary = sidecar.with_suffix(".rollback.tmp")
            temporary.write_bytes(previous_sidecar)
            temporary.replace(sidecar)

        revision_dir = self.artifact_store.root / "revisions" / artifact_id
        for revision in set(self.artifact_store.list_revisions(artifact_id)) - previous_revisions:
            (revision_dir / f"{revision:06d}.yaml").unlink(missing_ok=True)
        try:
            revision_dir.rmdir()
        except OSError:
            pass

    def save_series_direction_proposal(
        self, proposal: SeriesDirectionProposal
    ) -> None:
        self._write_model(
            self.series_direction_proposal_path(proposal.proposal_id), proposal
        )

    def load_series_direction_proposal(
        self, proposal_id: str
    ) -> SeriesDirectionProposal:
        path = self.series_direction_proposal_path(proposal_id)
        if not path.is_file():
            raise FileNotFoundError(
                f"Unknown Series Direction proposal: {proposal_id}"
            )
        return SeriesDirectionProposal.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )

    def save_accepted_series_direction(
        self,
        accepted: AcceptedSeriesDirection,
        *,
        accepted_by: str,
        rationale: str | None,
    ) -> ArtifactMetadata:
        path = self.accepted_series_direction_path
        staged_path = path.parent / ".staging" / path.name
        artifact_id = staged_path.stem
        sidecar = self.artifact_store.sidecar_path(artifact_id)
        previous_sidecar = sidecar.read_bytes() if sidecar.is_file() else None
        previous_revisions = set(self.artifact_store.list_revisions(artifact_id))
        try:
            self._write_model(staged_path, accepted)
            metadata = self.artifact_store.accept(
                staged_path,
                "series_direction",
                dependencies=[],
                accepted_by=accepted_by,
                rationale=rationale,
            )
            if metadata is None:
                raise RuntimeError("Accepted Series Direction metadata is archived")
            staged_path.replace(path)
            return metadata
        except Exception:
            self._restore_artifact_metadata(
                artifact_id, previous_sidecar, previous_revisions
            )
            raise
        finally:
            staged_path.unlink(missing_ok=True)
            staged_path.with_suffix(".tmp").unlink(missing_ok=True)
            try:
                staged_path.parent.rmdir()
            except OSError:
                pass

    def load_accepted_series_direction(
        self,
    ) -> AcceptedSeriesDirection | None:
        path = self.accepted_series_direction_path
        if not path.is_file():
            return None
        metadata = self.artifact_store.current(path.stem)
        if (
            metadata is None
            or metadata.lifecycle is not Lifecycle.ACCEPTED
            or metadata.artifact_id != path.stem
            or metadata.artifact_type != "series_direction"
            or self.artifact_store.content_hash(path) != metadata.content_hash
        ):
            return None
        accepted = AcceptedSeriesDirection.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
        return accepted if accepted.artifact_id == metadata.artifact_id else None

    def load_series_direction_metadata(self) -> ArtifactMetadata | None:
        return self.artifact_store.current(
            self.accepted_series_direction_path.stem
        )
