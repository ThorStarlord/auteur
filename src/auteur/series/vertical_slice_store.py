from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

from auteur.provenance import (
    ArtifactMetadata,
    ArtifactStore,
    DependencyKind,
    DependencySource,
    DependencySpec,
    Lifecycle,
)
from auteur.series.vertical_slice_models import (
    AcceptedBookDirection,
    AcceptedSeriesDirection,
    ArtifactRef,
    BookDirectionProposal,
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

    def accepted_book_direction_path(self, book_number: int) -> Path:
        if book_number < 1:
            raise ValueError("Book number must be at least 1")
        return self.root / "accepted" / f"book-{book_number}-direction.yaml"

    def book_direction_proposal_path(
        self, book_number: int, proposal_id: str
    ) -> Path:
        if book_number < 1:
            raise ValueError("Book number must be at least 1")
        if not proposal_id or Path(proposal_id).name != proposal_id:
            raise FileNotFoundError(
                f"Unknown Book Direction proposal: {proposal_id}"
            )
        return (
            self.root
            / "proposals"
            / "book-direction"
            / f"book-{book_number}"
            / f"{proposal_id}.yaml"
        )

    def _find_book_direction_proposal_path(self, proposal_id: str) -> Path:
        if not proposal_id or Path(proposal_id).name != proposal_id:
            raise FileNotFoundError(
                f"Unknown Book Direction proposal: {proposal_id}"
            )
        proposal_root = self.root / "proposals" / "book-direction"
        matches = [
            path
            for path in proposal_root.glob("book-*/*.yaml")
            if path.stem == proposal_id
        ]
        if len(matches) != 1:
            raise FileNotFoundError(
                f"Unknown Book Direction proposal: {proposal_id}"
            )
        return matches[0]

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

    def save_book_direction_proposal(
        self, proposal: BookDirectionProposal
    ) -> None:
        self._write_model(
            self.book_direction_proposal_path(
                proposal.direction.book_number, proposal.proposal_id
            ),
            proposal,
        )

    def load_book_direction_proposal(
        self, proposal_id: str
    ) -> BookDirectionProposal:
        path = self._find_book_direction_proposal_path(proposal_id)
        return BookDirectionProposal.model_validate(
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

    def _load_accepted_series_revision(
        self, artifact_id: str, revision: int
    ) -> ArtifactMetadata | None:
        if artifact_id != self.accepted_series_direction_path.stem:
            return None
        try:
            metadata = self.artifact_store.get_revision(artifact_id, revision)
        except (OSError, UnicodeError, yaml.YAMLError, ValidationError):
            return None
        if (
            metadata.artifact_id != artifact_id
            or metadata.artifact_type != "series_direction"
            or metadata.revision != revision
            or metadata.lifecycle is not Lifecycle.ACCEPTED
        ):
            return None
        return metadata

    def _validate_current_series_dependency(
        self, source_ref: ArtifactRef
    ) -> None:
        try:
            accepted = self.load_accepted_series_direction()
            current_metadata = self.load_series_direction_metadata()
        except (OSError, UnicodeError, yaml.YAMLError, ValidationError) as error:
            raise ValueError(
                "Invalid accepted Series Direction dependency revision"
            ) from error
        series_revision = self._load_accepted_series_revision(
            source_ref.artifact_id, source_ref.revision
        )
        current_hash = self.artifact_store.content_hash(
            self.accepted_series_direction_path
        )
        if (
            accepted is None
            or current_metadata is None
            or accepted.artifact_id != source_ref.artifact_id
            or current_metadata.artifact_id != source_ref.artifact_id
            or current_metadata.artifact_type != "series_direction"
            or current_metadata.revision != source_ref.revision
            or current_metadata.lifecycle is not Lifecycle.ACCEPTED
            or current_metadata.content_hash != current_hash
            or series_revision is None
            or series_revision.content_hash != current_hash
        ):
            raise ValueError(
                "Invalid accepted Series Direction dependency revision"
            )

    def save_accepted_book_direction(
        self,
        accepted: AcceptedBookDirection,
        *,
        series_source: ArtifactRef,
        accepted_by: str,
        rationale: str | None,
    ) -> ArtifactMetadata:
        self._validate_current_series_dependency(series_source)
        path = self.accepted_book_direction_path(
            accepted.direction.book_number
        )
        staged_path = path.parent / ".staging" / path.name
        artifact_id = staged_path.stem
        sidecar = self.artifact_store.sidecar_path(artifact_id)
        previous_sidecar = sidecar.read_bytes() if sidecar.is_file() else None
        previous_revisions = set(self.artifact_store.list_revisions(artifact_id))
        dependencies = [
            DependencySpec(
                artifact_id=self.accepted_series_direction_path.stem,
                artifact_type="series_direction",
                path=self.accepted_series_direction_path,
                kind=DependencyKind.SEMANTIC,
                source=DependencySource.DECLARED,
            )
        ]
        try:
            self._write_model(staged_path, accepted)
            metadata = self.artifact_store.accept(
                staged_path,
                "book_direction",
                dependencies=dependencies,
                accepted_by=accepted_by,
                rationale=rationale,
            )
            if metadata is None:
                raise RuntimeError("Accepted Book Direction metadata is archived")
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

    def load_accepted_book_direction(
        self, book_number: int
    ) -> AcceptedBookDirection | None:
        path = self.accepted_book_direction_path(book_number)
        if not path.is_file():
            return None
        metadata = self.artifact_store.current(path.stem)
        if (
            metadata is None
            or metadata.lifecycle is not Lifecycle.ACCEPTED
            or metadata.artifact_id != path.stem
            or metadata.artifact_type != "book_direction"
            or self.artifact_store.content_hash(path) != metadata.content_hash
            or len(metadata.dependencies) != 1
        ):
            return None
        dependency = metadata.dependencies[0]
        expected_dependency_path = str(
            self.accepted_series_direction_path.resolve().relative_to(
                self.project_root.resolve()
            )
        )
        if (
            dependency.artifact_id != self.accepted_series_direction_path.stem
            or dependency.artifact_type != "series_direction"
            or dependency.kind is not DependencyKind.SEMANTIC
            or dependency.source is not DependencySource.DECLARED
            or dependency.path != expected_dependency_path
            or dependency.revision is None
            or dependency.fields != []
            or dependency.projection.id != "full"
            or dependency.projection.fields != []
        ):
            return None
        series_revision = self._load_accepted_series_revision(
            dependency.artifact_id, dependency.revision
        )
        if (
            series_revision is None
            or dependency.full_content_hash != series_revision.content_hash
            or dependency.projected_hash != dependency.full_content_hash
        ):
            return None
        accepted = AcceptedBookDirection.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
        if (
            accepted.artifact_id != metadata.artifact_id
            or accepted.direction.book_number != book_number
        ):
            return None
        return accepted

    def load_book_direction_metadata(
        self, book_number: int
    ) -> ArtifactMetadata | None:
        return self.artifact_store.current(
            self.accepted_book_direction_path(book_number).stem
        )
