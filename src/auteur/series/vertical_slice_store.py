from __future__ import annotations

from pathlib import Path
import re

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
    AcceptedRealizationBundle,
    AcceptedSeriesDirection,
    ArtifactRef,
    BookDirectionProposal,
    BookPlanningIntent,
    BookPlanningContext,
    CanonicalState,
    DecisionAction,
    NextDecisionProposal,
    PlanningEntry,
    RealizationCandidate,
    RepeatedBookPlanningContext,
    SeriesDirectionProposal,
)


_PATH_SAFE_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
_REALIZATION_ARTIFACT_PREFIX = "realization-bundle-"
_NEXT_DECISION_PROPOSAL_ID = re.compile(
    r"book-2-next-decision-[0-9a-f]{32}\Z"
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

    @property
    def canonical_state_path(self) -> Path:
        return self.root / "derived" / "canonical-state.yaml"

    def planning_entry_path(self, book_number: int) -> Path:
        if book_number <= 1:
            raise ValueError("Planning entry requires a Book number greater than 1")
        return self.root / "workflow" / f"book-{book_number}-planning.yaml"

    def book_planning_intent_path(self, book_number: int) -> Path:
        if book_number <= 1:
            raise ValueError(
                "Planning intent requires a Book number greater than 1"
            )
        return (
            self.root
            / "workflow"
            / "book-planning-intent"
            / f"book-{book_number}.yaml"
        )

    def book_planning_context_path(self, book_number: int) -> Path:
        if book_number <= 1:
            raise ValueError("Planning context requires a Book number greater than 1")
        return self.root / "derived" / f"book-{book_number}-context.yaml"

    def repeated_book_context_path(self, book_number: int) -> Path:
        if book_number <= 1:
            raise ValueError(
                "Repeated planning context requires a Book number greater than 1"
            )
        return (
            self.root
            / "derived"
            / f"repeated-book-{book_number}-context.yaml"
        )

    def next_decision_proposal_path(self, proposal_id: str) -> Path:
        if _PATH_SAFE_IDENTIFIER.fullmatch(proposal_id) is None:
            raise FileNotFoundError(
                f"Unknown Next Decision proposal: {proposal_id}"
            )
        return (
            self.root
            / "proposals"
            / "next-decision"
            / f"{proposal_id}.yaml"
        )

    def decision_actions_path(self, proposal_id: str) -> Path:
        if _PATH_SAFE_IDENTIFIER.fullmatch(proposal_id) is None:
            raise FileNotFoundError(
                f"Unknown Next Decision proposal: {proposal_id}"
            )
        return (
            self.root
            / "workflow"
            / "decision-actions"
            / f"{proposal_id}.yaml"
        )

    def realization_candidate_path(self, candidate_id: str) -> Path:
        if _PATH_SAFE_IDENTIFIER.fullmatch(candidate_id) is None:
            raise ValueError("Realization candidate ID must be path-safe")
        return (
            self.root
            / "proposals"
            / "realization"
            / f"{candidate_id}.yaml"
        )

    def accepted_realization_bundle_path(self, bundle_id: str) -> Path:
        if _PATH_SAFE_IDENTIFIER.fullmatch(bundle_id) is None:
            raise ValueError("Realization bundle ID must be path-safe")
        return self.root / "accepted" / "realization" / f"{bundle_id}.yaml"

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

    def save_realization_candidate(
        self, candidate: RealizationCandidate
    ) -> None:
        self._write_model(
            self.realization_candidate_path(candidate.candidate_id), candidate
        )

    def load_realization_candidate(
        self, candidate_id: str
    ) -> RealizationCandidate:
        path = self.realization_candidate_path(candidate_id)
        if not path.is_file():
            raise FileNotFoundError(
                f"Unknown Realization candidate: {candidate_id}"
            )
        return RealizationCandidate.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )

    def load_book_direction_proposal(
        self, proposal_id: str
    ) -> BookDirectionProposal:
        path = self._find_book_direction_proposal_path(proposal_id)
        return BookDirectionProposal.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )

    def save_next_decision_proposal(
        self, proposal: NextDecisionProposal
    ) -> None:
        self._validate_next_decision_identity(proposal)
        actions = self._load_decision_action_payloads(proposal)
        self.validate_decision_history(proposal, actions)
        path = self.next_decision_proposal_path(proposal.proposal_id)
        if path.is_file():
            persisted = self._load_next_decision_proposal_payload(
                proposal.proposal_id
            )
            persisted_actions = self._load_decision_action_payloads(persisted)
            self.validate_decision_history(persisted, persisted_actions)
            if proposal != persisted:
                raise ValueError(
                    "Next Decision proposal is immutable once created"
                )
            return
        self._write_next_decision_proposal(proposal)

    def _write_next_decision_proposal(
        self, proposal: NextDecisionProposal
    ) -> None:
        self._write_model(
            self.next_decision_proposal_path(proposal.proposal_id), proposal
        )

    def load_next_decision_proposal(
        self, proposal_id: str
    ) -> NextDecisionProposal:
        proposal = self._load_next_decision_proposal_payload(proposal_id)
        actions = self._load_decision_action_payloads(proposal)
        self.validate_decision_history(proposal, actions)
        return proposal

    def _load_next_decision_proposal_payload(
        self, proposal_id: str
    ) -> NextDecisionProposal:
        path = self.next_decision_proposal_path(proposal_id)
        if not path.is_file():
            raise FileNotFoundError(
                f"Unknown Next Decision proposal: {proposal_id}"
            )
        proposal = NextDecisionProposal.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
        self._validate_next_decision_identity(
            proposal, requested_id=proposal_id
        )
        return proposal

    @staticmethod
    def _validate_next_decision_identity(
        proposal: NextDecisionProposal,
        *,
        requested_id: str | None = None,
    ) -> None:
        if requested_id is not None and proposal.proposal_id != requested_id:
            raise ValueError(
                f"Next Decision proposal {proposal.proposal_id} does not match "
                f"requested proposal {requested_id}"
            )
        if proposal.book_number != 2:
            raise ValueError("Next Decision proposal must be for Book 2")
        if _NEXT_DECISION_PROPOSAL_ID.fullmatch(proposal.proposal_id) is None:
            raise ValueError(
                "Next Decision proposal ID does not match Book 2 convention"
            )

    def save_decision_action(self, action: DecisionAction) -> None:
        raise ValueError(
            "Decision actions must be saved with proposal status"
        )

    def _write_decision_action(self, action: DecisionAction) -> None:
        path = self.decision_actions_path(action.proposal_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        rendered = yaml.safe_dump(
            [action.model_dump(mode="json")],
            sort_keys=False,
        )
        temporary = path.with_suffix(".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(path)

    def load_decision_actions(self, proposal_id: str) -> list[DecisionAction]:
        proposal = self._load_next_decision_proposal_payload(proposal_id)
        actions = self._load_decision_action_payloads(proposal)
        self.validate_decision_history(proposal, actions)
        return actions

    def _load_decision_action_payloads(
        self, proposal: NextDecisionProposal
    ) -> list[DecisionAction]:
        path = self.decision_actions_path(proposal.proposal_id)
        if not path.is_file():
            return []
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        actions = [DecisionAction.model_validate(item) for item in payload]
        for action in actions:
            self.validate_decision_action(proposal, action)
        return actions

    @staticmethod
    def validate_decision_action(
        proposal: NextDecisionProposal, action: DecisionAction
    ) -> None:
        if action.proposal_id != proposal.proposal_id:
            raise ValueError(
                "Decision action proposal does not match the requested proposal"
            )
        option_ids = {option.option_id for option in proposal.options}
        if action.action == "choose_recommended":
            if action.selected_option_id != proposal.recommended_option_id:
                raise ValueError(
                    "The recommended action must select the recommended option"
                )
        elif action.action == "choose_other":
            if action.selected_option_id not in option_ids:
                raise ValueError(
                    f"Unknown decision option: {action.selected_option_id}"
                )
            if action.selected_option_id == proposal.recommended_option_id:
                raise ValueError(
                    "Choose another option must select a presented alternative"
                )
        elif action.selected_option_id is not None:
            raise ValueError("A deferred decision cannot select an option")

    @staticmethod
    def validate_decision_history(
        proposal: NextDecisionProposal,
        actions: list[DecisionAction],
    ) -> None:
        consistent = False
        if proposal.status == "proposed":
            consistent = not actions
        elif proposal.status == "resolved":
            consistent = (
                len(actions) == 1
                and actions[0].action
                in {"choose_recommended", "choose_other"}
            )
        elif proposal.status == "deferred":
            consistent = len(actions) == 1 and actions[0].action == "defer"
        if not consistent:
            raise ValueError("Next Decision proposal status/history mismatch")

    def save_decision_action_with_status(
        self,
        action: DecisionAction,
        proposal: NextDecisionProposal,
    ) -> None:
        if action.proposal_id != proposal.proposal_id:
            raise ValueError(
                "Decision action proposal does not match the status proposal"
            )
        persisted = self.load_next_decision_proposal(proposal.proposal_id)
        persisted_actions = self.load_decision_actions(proposal.proposal_id)
        if proposal.model_copy(
            update={"status": "proposed"}
        ) != persisted.model_copy(update={"status": "proposed"}):
            raise ValueError(
                "Decision status proposal does not match persisted proposal"
            )
        if persisted.status != "proposed" or persisted_actions:
            raise ValueError(
                "Next Decision proposal already has a terminal action"
            )
        self.validate_decision_action(persisted, action)
        self.validate_decision_history(proposal, [action])
        proposal_path = self.next_decision_proposal_path(proposal.proposal_id)
        actions_path = self.decision_actions_path(proposal.proposal_id)
        proposal_snapshot = proposal_path.read_bytes()
        actions_snapshot = (
            actions_path.read_bytes() if actions_path.is_file() else None
        )
        try:
            self._write_decision_action(action)
            self._write_next_decision_proposal(proposal)
        except Exception:
            self._restore_workflow_file(proposal_path, proposal_snapshot)
            self._restore_workflow_file(actions_path, actions_snapshot)
            raise

    @staticmethod
    def _restore_workflow_file(path: Path, snapshot: bytes | None) -> None:
        path.with_suffix(".tmp").unlink(missing_ok=True)
        if snapshot is None:
            path.unlink(missing_ok=True)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".rollback.tmp")
        temporary.write_bytes(snapshot)
        temporary.replace(path)

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
                record_accepted_at=True,
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

    def validate_book_context_source(
        self,
        metadata: ArtifactMetadata,
        *,
        artifact_id: str,
        artifact_type: str,
        path: Path,
    ) -> None:
        try:
            current = self.artifact_store.current(artifact_id)
            revision = self.artifact_store.get_revision(
                artifact_id, metadata.revision
            )
            content_hash = self.artifact_store.content_hash(path)
        except (OSError, UnicodeError, yaml.YAMLError, ValidationError) as error:
            raise ValueError(
                "Invalid Book planning context source metadata"
            ) from error
        if (
            current != metadata
            or revision != metadata
            or metadata.artifact_id != artifact_id
            or metadata.artifact_type != artifact_type
            or metadata.lifecycle is not Lifecycle.ACCEPTED
            or metadata.content_hash != content_hash
        ):
            raise ValueError("Invalid Book planning context source metadata")

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
                record_accepted_at=True,
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

    def _load_accepted_book_revision(
        self,
        book_number: int,
        artifact_id: str,
        revision: int,
    ) -> ArtifactMetadata | None:
        expected_id = self.accepted_book_direction_path(book_number).stem
        if artifact_id != expected_id:
            return None
        try:
            metadata = self.artifact_store.get_revision(artifact_id, revision)
        except (OSError, UnicodeError, yaml.YAMLError, ValidationError):
            return None
        if (
            metadata.artifact_id != artifact_id
            or metadata.artifact_type != "book_direction"
            or metadata.revision != revision
            or metadata.lifecycle is not Lifecycle.ACCEPTED
        ):
            return None
        return metadata

    def validate_current_book_dependency(
        self, book_number: int, source_ref: ArtifactRef
    ) -> None:
        try:
            accepted = self.load_accepted_book_direction(book_number)
            current_metadata = self.load_book_direction_metadata(book_number)
        except (OSError, UnicodeError, yaml.YAMLError, ValidationError) as error:
            raise ValueError(
                "Invalid accepted Book Direction dependency revision"
            ) from error
        path = self.accepted_book_direction_path(book_number)
        expected_id = path.stem
        revision_metadata = self._load_accepted_book_revision(
            book_number, source_ref.artifact_id, source_ref.revision
        )
        current_hash = self.artifact_store.content_hash(path)
        if (
            accepted is None
            or current_metadata is None
            or source_ref.artifact_id != expected_id
            or accepted.artifact_id != source_ref.artifact_id
            or current_metadata.artifact_id != source_ref.artifact_id
            or current_metadata.artifact_type != "book_direction"
            or current_metadata.revision != source_ref.revision
            or current_metadata.lifecycle is not Lifecycle.ACCEPTED
            or current_metadata.content_hash != current_hash
            or revision_metadata is None
            or revision_metadata.content_hash != current_hash
        ):
            raise ValueError(
                "Invalid accepted Book Direction dependency revision"
            )

    def save_accepted_realization_bundle(
        self,
        accepted: AcceptedRealizationBundle,
        *,
        book_source: ArtifactRef,
        accepted_by: str,
        rationale: str | None,
    ) -> ArtifactMetadata:
        existing = self.load_accepted_realization_bundles()
        self.validate_current_book_dependency(
            accepted.book_number, book_source
        )
        path = self.accepted_realization_bundle_path(accepted.bundle_id)
        if (
            accepted.artifact_id != accepted.bundle_id
            or path.stem != accepted.artifact_id
            or not accepted.artifact_id.startswith(
                _REALIZATION_ARTIFACT_PREFIX
            )
        ):
            raise ValueError(
                "Accepted Realization artifact ID must match its bundle path"
            )
        artifact_id = accepted.artifact_id
        sidecar = self.artifact_store.sidecar_path(artifact_id)
        revision_dir = self.artifact_store.root / "revisions" / artifact_id
        if path.exists() or sidecar.exists() or revision_dir.exists():
            raise ValueError(
                f"Realization candidate is already accepted: {accepted.candidate_id}"
            )
        staged_path = path.parent / ".staging" / path.name
        previous_sidecar = sidecar.read_bytes() if sidecar.is_file() else None
        previous_revisions = set(
            self.artifact_store.list_revisions(artifact_id)
        )
        dependencies = [
            DependencySpec(
                artifact_id=book_source.artifact_id,
                artifact_type="book_direction",
                path=self.accepted_book_direction_path(accepted.book_number),
                kind=DependencyKind.SEMANTIC,
                source=DependencySource.DECLARED,
            )
        ]
        if existing:
            previous_bundle, previous_metadata = existing[-1]
            if previous_metadata.revision != 1:
                raise ValueError(
                    "Invalid accepted Realization metadata history"
                )
            dependencies.append(
                DependencySpec(
                    artifact_id=previous_bundle.artifact_id,
                    artifact_type="accepted_realization_bundle",
                    path=self.accepted_realization_bundle_path(
                        previous_bundle.bundle_id
                    ),
                    kind=DependencyKind.STATE_ORDER,
                    source=DependencySource.DECLARED,
                )
            )
        try:
            self._write_model(staged_path, accepted)
            metadata = self.artifact_store.accept(
                staged_path,
                "accepted_realization_bundle",
                dependencies=dependencies,
                accepted_by=accepted_by,
                rationale=rationale,
                record_accepted_at=True,
            )
            if metadata is None:
                raise RuntimeError("Accepted Realization metadata is archived")
            staged_path.replace(path)
            return metadata
        except Exception:
            self._restore_artifact_metadata(
                artifact_id,
                previous_sidecar,
                previous_revisions,
            )
            raise
        finally:
            staged_path.unlink(missing_ok=True)
            staged_path.with_suffix(".tmp").unlink(missing_ok=True)
            try:
                staged_path.parent.rmdir()
            except OSError:
                pass

    def _validate_realization_book_dependency(
        self,
        bundle: AcceptedRealizationBundle,
        metadata: ArtifactMetadata,
    ) -> bool:
        book_dependencies = [
            dependency
            for dependency in metadata.dependencies
            if dependency.kind is DependencyKind.SEMANTIC
        ]
        if len(book_dependencies) != 1:
            return False
        dependency = book_dependencies[0]
        book_path = self.accepted_book_direction_path(bundle.book_number)
        expected_path = str(
            book_path.resolve().relative_to(self.project_root.resolve())
        )
        if (
            dependency.artifact_id != book_path.stem
            or dependency.artifact_type != "book_direction"
            or dependency.kind is not DependencyKind.SEMANTIC
            or dependency.source is not DependencySource.DECLARED
            or dependency.path != expected_path
            or dependency.revision is None
            or dependency.fields != []
            or dependency.projection.id != "full"
            or dependency.projection.fields != []
        ):
            return False
        book_revision = self._load_accepted_book_revision(
            bundle.book_number,
            dependency.artifact_id,
            dependency.revision,
        )
        return (
            book_revision is not None
            and dependency.full_content_hash == book_revision.content_hash
            and dependency.projected_hash == dependency.full_content_hash
        )

    def _realization_history_artifact_ids(
        self,
    ) -> tuple[set[str], set[str], set[str]]:
        payload_ids = {
            path.stem
            for path in (self.root / "accepted" / "realization").glob("*.yaml")
        }
        sidecar_ids = {
            path.stem
            for path in self.artifact_store.root.glob("*.yaml")
            if path.stem.startswith(_REALIZATION_ARTIFACT_PREFIX)
            or path.stem == "realization-bundles"
        }
        revision_root = self.artifact_store.root / "revisions"
        revision_ids = (
            {
                path.name
                for path in revision_root.iterdir()
                if path.is_dir()
                and (
                    path.name.startswith(_REALIZATION_ARTIFACT_PREFIX)
                    or path.name == "realization-bundles"
                )
            }
            if revision_root.is_dir()
            else set()
        )
        return payload_ids, sidecar_ids, revision_ids

    def load_accepted_realization_bundles(
        self,
    ) -> list[tuple[AcceptedRealizationBundle, ArtifactMetadata]]:
        payload_ids, sidecar_ids, revision_ids = (
            self._realization_history_artifact_ids()
        )
        if not payload_ids and not sidecar_ids and not revision_ids:
            return []
        if payload_ids != sidecar_ids or payload_ids != revision_ids:
            raise ValueError("Invalid accepted Realization metadata history")

        loaded_by_id: dict[
            str, tuple[AcceptedRealizationBundle, ArtifactMetadata]
        ] = {}
        predecessor_by_id: dict[str, str | None] = {}
        for artifact_id in sorted(payload_ids):
            path = self.accepted_realization_bundle_path(artifact_id)
            try:
                bundle = AcceptedRealizationBundle.model_validate(
                    yaml.safe_load(path.read_text(encoding="utf-8"))
                )
                current = self.artifact_store.current(artifact_id)
                revisions = self.artifact_store.list_revisions(artifact_id)
            except (OSError, UnicodeError, yaml.YAMLError, ValidationError) as error:
                raise ValueError(
                    "Invalid accepted Realization metadata history"
                ) from error
            if (
                bundle.artifact_id != artifact_id
                or bundle.bundle_id != artifact_id
                or current is None
                or current.artifact_id != artifact_id
                or current.artifact_type != "accepted_realization_bundle"
                or current.lifecycle is not Lifecycle.ACCEPTED
                or current.revision != 1
                or revisions != [1]
            ):
                raise ValueError(
                    "Invalid accepted Realization metadata history"
                )
            revision_dir = (
                self.artifact_store.root / "revisions" / artifact_id
            )
            revision_files = list(revision_dir.glob("*.yaml"))
            if len(revision_files) != 1 or revision_files[0].stem != "000001":
                raise ValueError(
                    "Invalid accepted Realization metadata history"
                )
            try:
                revision_metadata = self.artifact_store.get_revision(
                    artifact_id, 1
                )
            except (OSError, UnicodeError, yaml.YAMLError, ValidationError) as error:
                raise ValueError(
                    "Invalid accepted Realization metadata history"
                ) from error
            state_dependencies = [
                dependency
                for dependency in current.dependencies
                if dependency.kind is DependencyKind.STATE_ORDER
            ]
            if (
                revision_metadata != current
                or self.artifact_store.content_hash(path)
                != current.content_hash
                or not self._validate_realization_book_dependency(
                    bundle, current
                )
                or len(state_dependencies) > 1
                or len(current.dependencies) != 1 + len(state_dependencies)
            ):
                raise ValueError(
                    "Invalid accepted Realization metadata history"
                )
            predecessor_by_id[artifact_id] = (
                state_dependencies[0].artifact_id
                if state_dependencies
                else None
            )
            loaded_by_id[artifact_id] = (bundle, current)

        successors: dict[str, str] = {}
        roots: list[str] = []
        for artifact_id, predecessor_id in predecessor_by_id.items():
            if predecessor_id is None:
                roots.append(artifact_id)
                continue
            if predecessor_id not in loaded_by_id or predecessor_id in successors:
                raise ValueError("Invalid accepted Realization metadata history")
            dependency = next(
                dependency
                for dependency in loaded_by_id[artifact_id][1].dependencies
                if dependency.kind is DependencyKind.STATE_ORDER
            )
            predecessor_bundle, predecessor_metadata = loaded_by_id[
                predecessor_id
            ]
            predecessor_path = self.accepted_realization_bundle_path(
                predecessor_bundle.bundle_id
            )
            expected_path = str(
                predecessor_path.resolve().relative_to(
                    self.project_root.resolve()
                )
            )
            if (
                dependency.artifact_type != "accepted_realization_bundle"
                or dependency.source is not DependencySource.DECLARED
                or dependency.path != expected_path
                or dependency.revision != predecessor_metadata.revision
                or dependency.full_content_hash
                != predecessor_metadata.content_hash
                or dependency.projected_hash
                != dependency.full_content_hash
                or dependency.fields != []
                or dependency.projection.id != "full"
                or dependency.projection.fields != []
            ):
                raise ValueError("Invalid accepted Realization metadata history")
            successors[predecessor_id] = artifact_id

        if len(roots) != 1:
            raise ValueError("Invalid accepted Realization metadata history")
        ordered: list[tuple[AcceptedRealizationBundle, ArtifactMetadata]] = []
        current_id: str | None = roots[0]
        while current_id is not None:
            ordered.append(loaded_by_id[current_id])
            current_id = successors.get(current_id)
        if len(ordered) != len(loaded_by_id):
            raise ValueError("Invalid accepted Realization metadata history")
        return ordered

    def rollback_accepted_realization_bundle(
        self, bundle_id: str, revision: int
    ) -> None:
        current = self.artifact_store.current(bundle_id)
        if current is None or current.revision != revision:
            raise RuntimeError("Cannot roll back accepted Realization revision")
        self.accepted_realization_bundle_path(bundle_id).unlink(missing_ok=True)
        sidecar = self.artifact_store.sidecar_path(bundle_id)
        sidecar.unlink(missing_ok=True)
        revision_dir = (
            self.artifact_store.root
            / "revisions"
            / bundle_id
        )
        (revision_dir / f"{revision:06d}.yaml").unlink(missing_ok=True)
        try:
            revision_dir.rmdir()
        except OSError:
            pass

    def save_canonical_state(self, state: CanonicalState) -> None:
        self._write_model(self.canonical_state_path, state)

    def load_canonical_state(self) -> CanonicalState:
        if not self.canonical_state_path.is_file():
            return CanonicalState(state_version=0)
        return CanonicalState.model_validate(
            yaml.safe_load(
                self.canonical_state_path.read_text(encoding="utf-8")
            )
        )

    def save_planning_entry(self, entry: PlanningEntry) -> None:
        self._write_model(self.planning_entry_path(entry.book_number), entry)

    def load_planning_entry(self, book_number: int) -> PlanningEntry | None:
        path = self.planning_entry_path(book_number)
        if not path.is_file():
            return None
        entry = PlanningEntry.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
        if entry.book_number != book_number:
            raise ValueError(
                f"Planning entry Book {entry.book_number} does not match "
                f"requested Book {book_number}"
            )
        return entry

    def save_book_planning_intent(self, intent: BookPlanningIntent) -> None:
        self._write_model(
            self.book_planning_intent_path(intent.book_number), intent
        )

    def load_book_planning_intent(
        self, book_number: int
    ) -> BookPlanningIntent | None:
        path = self.book_planning_intent_path(book_number)
        if not path.is_file():
            return None
        intent = BookPlanningIntent.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
        if intent.book_number != book_number:
            raise ValueError(
                f"Planning intent Book {intent.book_number} does not match "
                f"requested Book {book_number}"
            )
        return intent

    def save_book_planning_context(self, context: BookPlanningContext) -> None:
        self._write_model(
            self.book_planning_context_path(context.book_number), context
        )

    def delete_book_planning_context(self, book_number: int) -> None:
        path = self.book_planning_context_path(book_number)
        path.with_suffix(".tmp").unlink(missing_ok=True)
        path.unlink(missing_ok=True)

    def save_repeated_book_context(
        self, context: RepeatedBookPlanningContext
    ) -> None:
        self._write_model(
            self.repeated_book_context_path(context.book_number), context
        )

    def load_repeated_book_context(
        self, book_number: int
    ) -> RepeatedBookPlanningContext | None:
        path = self.repeated_book_context_path(book_number)
        if not path.is_file():
            return None
        context = RepeatedBookPlanningContext.model_validate(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        )
        if context.book_number != book_number:
            raise ValueError(
                f"Repeated planning context Book {context.book_number} does "
                f"not match requested Book {book_number}"
            )
        return context

    def delete_repeated_book_context(self, book_number: int) -> None:
        path = self.repeated_book_context_path(book_number)
        path.with_suffix(".tmp").unlink(missing_ok=True)
        path.unlink(missing_ok=True)

    def snapshot_canonical_state(self) -> bytes | None:
        if not self.canonical_state_path.is_file():
            return None
        return self.canonical_state_path.read_bytes()

    def restore_canonical_state(self, snapshot: bytes | None) -> None:
        path = self.canonical_state_path
        path.with_suffix(".tmp").unlink(missing_ok=True)
        if snapshot is None:
            path.unlink(missing_ok=True)
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".rollback.tmp")
        temporary.write_bytes(snapshot)
        temporary.replace(path)
