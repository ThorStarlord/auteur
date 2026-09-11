"""Bounded author-action service for the qualified V1 decision loop."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from auteur.llm import LLMProviderError
from auteur.story_design_packs.handoff import derive_decision_handoff
from auteur.story_design_packs.models import source_fingerprint
from auteur.story_design_packs.proposal_bridge import generate_structure_proposal_from_tutor
from auteur.story_design_packs.session import TutorSession, TutorSessionStore
from auteur.structure.proposal_service import ProposalReviewService
from auteur.structure.revision_preview import build_revision_preview
from auteur.structure.revision_reassessment import build_revision_reassessment
from auteur.structure.revision_service import RevisionService


class AuthorActionOutcome(BaseModel):
    """Transport-neutral result of one bounded author action."""

    action: str
    status: Literal["ok", "blocked", "error"]
    authority_status: str
    mutates_story: bool = False
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    message: str | None = None


class AuthorActionService:
    """Execute existing decision-loop application operations without CLI shelling."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        if not (self.project_root / ".auteur").exists():
            raise ValueError(f"Not an Auteur project: {self.project_root}")

    def _current_fingerprints(self, session: TutorSession) -> dict[str, str]:
        current: dict[str, str] = {}
        for spec in session.source_fingerprints:
            if "=" not in spec:
                raise ValueError("Tutor source fingerprint key is malformed")
            _name, raw = spec.split("=", 1)
            path = (self.project_root / raw).resolve()
            if not path.is_relative_to(self.project_root) or not path.is_file():
                raise ValueError(f"Tutor source is unavailable: {raw}")
            current[spec] = source_fingerprint(path.read_bytes())
        return current

    def tutor_choose(
        self,
        session_id: str,
        action: str,
        *,
        value: str | None = None,
    ) -> AuthorActionOutcome:
        store = TutorSessionStore(self.project_root)
        session = store.load(session_id)
        current = self._current_fingerprints(session)
        session = store.record_response(
            session_id,
            action,
            value,
            current_source_fingerprints=current,
        )
        return AuthorActionOutcome(
            action="tutor_choose",
            status="ok",
            authority_status="LOCAL / NONCANONICAL",
            data=session.model_dump(mode="json"),
        )

    def tutor_handoff(self, session_id: str) -> AuthorActionOutcome:
        store = TutorSessionStore(self.project_root)
        session = store.load(session_id)
        if session.source_fingerprints:
            session = store.refresh_status(session_id, self._current_fingerprints(session))
        handoff = derive_decision_handoff(session)
        return AuthorActionOutcome(
            action="tutor_handoff",
            status="ok" if handoff.status == "route_identified" else "blocked",
            authority_status="DERIVED / NOT CANON",
            data=handoff.model_dump(mode="json"),
            message=None if handoff.status == "route_identified" else handoff.rationale,
        )

    def tutor_propose(
        self,
        session_id: str,
        *,
        provider: str = "anthropic",
        model: str | None = None,
    ) -> AuthorActionOutcome:
        store = TutorSessionStore(self.project_root)
        session = store.load(session_id)
        if session.source_fingerprints:
            session = store.refresh_status(session_id, self._current_fingerprints(session))
        handoff = derive_decision_handoff(session)
        if handoff.status != "route_identified" or handoff.workflow != "structure_revision":
            raise ValueError("Tutor session has no current supported Structure authority route")
        from auteur.llm.factory import build_client

        result = generate_structure_proposal_from_tutor(
            self.project_root,
            session,
            build_client(provider, model),
        )
        return AuthorActionOutcome(
            action="tutor_propose",
            status="ok",
            authority_status="NONCANONICAL PROPOSAL / NOT APPLIED",
            data=result.model_dump(mode="json"),
        )

    def proposal_select(
        self,
        proposal: str,
        option_id: str,
        *,
        author: str | None = None,
    ) -> AuthorActionOutcome:
        data = ProposalReviewService(self.project_root).select(
            proposal, option_id, author=author
        )
        return AuthorActionOutcome(
            action="proposal_select",
            status="ok",
            authority_status="NONCANONICAL PROPOSAL / NOT APPLIED",
            data=data,
        )

    def revision_plan(self, proposal: str) -> AuthorActionOutcome:
        raw = Path(proposal)
        path = raw.resolve() if raw.is_absolute() else (self.project_root / raw).resolve()
        if not path.is_relative_to(self.project_root):
            raise ValueError("Revision proposal path must stay inside the selected project")
        plan = RevisionService(self.project_root).plan(proposal_path=path)
        return AuthorActionOutcome(
            action="revision_plan",
            status="ok",
            authority_status="REVISION PLAN / NOT APPLIED",
            data=plan.model_dump(mode="json"),
        )

    def revision_validate(self, plan_id: str) -> AuthorActionOutcome:
        state, preconditions = RevisionService(self.project_root).validate(plan_id)
        return AuthorActionOutcome(
            action="revision_validate",
            status="ok" if state == "ready" else "blocked",
            authority_status="REVISION PLAN / NOT APPLIED",
            data={"plan_id": plan_id, "state": state, "preconditions": preconditions},
        )

    def revision_preview(self, plan_id: str) -> AuthorActionOutcome:
        preview = build_revision_preview(self.project_root, plan_id)
        return AuthorActionOutcome(
            action="revision_preview",
            status="ok",
            authority_status="DERIVED PREVIEW / NOT APPLIED",
            data=preview,
        )

    def revision_apply(
        self,
        plan_id: str,
        *,
        confirmed: bool,
    ) -> AuthorActionOutcome:
        if not confirmed:
            return AuthorActionOutcome(
                action="revision_apply",
                status="blocked",
                authority_status="CONFIRMATION REQUIRED / NOT APPLIED",
                message="Explicit confirmation is required before Structure authority changes.",
                error_code="confirmation_required",
            )
        application = RevisionService(self.project_root).apply(plan_id, confirmed=True)
        success = application.state == "applied" and all(
            result.success for result in application.target_results
        )
        return AuthorActionOutcome(
            action="revision_apply",
            status="ok" if success else "blocked",
            authority_status=(
                "STRUCTURE AUTHORITY CHANGED" if success else "STRUCTURE APPLICATION BLOCKED"
            ),
            mutates_story=success,
            data=application.model_dump(mode="json"),
        )

    def revision_reassess(self, application_id: str) -> AuthorActionOutcome:
        data = build_revision_reassessment(self.project_root, application_id)
        return AuthorActionOutcome(
            action="revision_reassess",
            status="ok",
            authority_status="DERIVED REASSESSMENT / READ ONLY",
            data=data,
        )

    def execute(self, action: str, payload: dict[str, Any]) -> AuthorActionOutcome:
        """Dispatch the browser-facing bounded action vocabulary."""
        try:
            if action == "tutor-choose":
                return self.tutor_choose(
                    str(payload.get("session_id", "")),
                    str(payload.get("response_action", "choose")),
                    value=payload.get("value"),
                )
            if action == "tutor-handoff":
                return self.tutor_handoff(str(payload.get("session_id", "")))
            if action == "tutor-propose":
                return self.tutor_propose(
                    str(payload.get("session_id", "")),
                    provider=str(payload.get("provider", "anthropic")),
                    model=payload.get("model"),
                )
            if action == "proposal-select":
                return self.proposal_select(
                    str(payload.get("proposal", "")),
                    str(payload.get("option", "")),
                    author=payload.get("author"),
                )
            if action == "revision-plan":
                return self.revision_plan(str(payload.get("proposal", "")))
            if action == "revision-validate":
                return self.revision_validate(str(payload.get("plan_id", "")))
            if action == "revision-preview":
                return self.revision_preview(str(payload.get("plan_id", "")))
            if action == "revision-apply":
                return self.revision_apply(
                    str(payload.get("plan_id", "")),
                    confirmed=payload.get("confirmed") is True,
                )
            if action == "revision-reassess":
                return self.revision_reassess(str(payload.get("application_id", "")))
            return AuthorActionOutcome(
                action=action,
                status="error",
                authority_status="NO ACTION",
                error_code="unknown_action",
                message=f"Unknown Workspace action: {action}",
            )
        except LLMProviderError as exc:
            return AuthorActionOutcome(
                action=action,
                status="blocked",
                authority_status="NO STORY MUTATION",
                error_code=exc.code.value,
                message=str(exc),
            )
        except (FileNotFoundError, KeyError, OSError, ValueError) as exc:
            return AuthorActionOutcome(
                action=action,
                status="blocked",
                authority_status="NO STORY MUTATION",
                error_code="action_blocked",
                message=str(exc),
            )
