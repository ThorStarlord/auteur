"""Application service for reviewing/selecting noncanonical Structure proposals."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

import yaml

from auteur.story_design_packs.models import source_fingerprint
from auteur.story_design_packs.session import TutorSessionStore
from auteur.structure.proposal_models import StructureProposal


_AUTHORITY = "NONCANONICAL PROPOSAL / NOT APPLIED"


class ProposalReviewService:
    """Shared proposal review boundary used by CLI and local Workspace adapters."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def resolve_path(self, proposal: str | Path) -> Path:
        raw = Path(proposal)
        path = raw.resolve() if raw.is_absolute() else (self.project_root / raw).resolve()
        if not path.is_relative_to(self.project_root):
            raise ValueError("Structure proposal path must stay inside the selected project")
        if not path.is_file():
            raise ValueError(f"Structure proposal not found: {proposal}")
        return path

    @staticmethod
    def _load(path: Path) -> StructureProposal:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            return StructureProposal.model_validate(raw)
        except Exception as exc:
            raise ValueError(f"Invalid Structure proposal {path}: {exc}") from exc

    def _tutor_current(self, proposal: StructureProposal) -> bool | None:
        rule = proposal.source_rule or ""
        if not rule.startswith("tutor_session:"):
            return None
        parts = rule.split(":", 2)
        if len(parts) != 3:
            return False
        session_id = parts[1]
        try:
            session = TutorSessionStore(self.project_root).load(session_id)
        except Exception:
            return False
        if session.status == "stale":
            return False
        current: dict[str, str] = {}
        for key in sorted(session.source_fingerprints):
            if "=" not in key:
                return False
            _name, raw = key.split("=", 1)
            source = (self.project_root / raw).resolve()
            if not source.is_relative_to(self.project_root) or not source.is_file():
                return False
            current[key] = source_fingerprint(source.read_bytes())
        if current != session.source_fingerprints:
            return False
        digest = hashlib.sha256(
            json.dumps(current, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return digest == parts[2]

    def _relative(self, path: Path) -> str:
        return path.relative_to(self.project_root).as_posix()

    def _payload(self, path: Path, proposal: StructureProposal) -> dict[str, object]:
        selected = proposal.selection.selected_option_id or None
        accepted = bool(
            selected
            and proposal.decision is not None
            and proposal.decision.status == "accepted"
            and proposal.decision.selected_option_id == selected
        )
        rel = self._relative(path)
        return {
            "proposal_id": proposal.proposal_id,
            "proposal_path": rel,
            "summary": proposal.summary,
            "source_rule": proposal.source_rule,
            "source_domain": proposal.source_domain,
            "options": [
                {
                    "id": option.id,
                    "summary": option.summary,
                    "tradeoffs": option.tradeoffs,
                    "data": option.data,
                }
                for option in proposal.options
            ],
            "selected_option_id": selected,
            "decision": (
                proposal.decision.model_dump(mode="json") if proposal.decision else None
            ),
            "source_current": self._tutor_current(proposal),
            "authority_status": _AUTHORITY,
            "mutates_story": False,
            "ready_for_revision_plan": accepted,
            "select_command": (
                None
                if accepted
                else f"auteur structure proposal select {rel} --option <OPTION_ID> --project ."
            ),
            "next_command": (
                f"auteur structure revision plan --proposal {rel} --project ."
                if accepted
                else None
            ),
        }

    @staticmethod
    def _atomic_save(path: Path, proposal: StructureProposal) -> None:
        rendered = yaml.safe_dump(
            proposal.model_dump(mode="json"), sort_keys=False, allow_unicode=True
        )
        fd, temporary = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(rendered)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def inspect(self, proposal: str | Path) -> dict[str, object]:
        path = self.resolve_path(proposal)
        return self._payload(path, self._load(path))

    def select(
        self,
        proposal: str | Path,
        option_id: str,
        *,
        author: str | None = None,
    ) -> dict[str, object]:
        """Record proposal selection without changing accepted Structure."""
        path = self.resolve_path(proposal)
        model = self._load(path)
        current = self._tutor_current(model)
        if current is False:
            raise ValueError(
                "Tutor-generated Structure proposal is stale; regenerate it before selection"
            )
        existing = model.selection.selected_option_id
        if existing:
            if existing != option_id:
                raise ValueError(
                    "Structure proposal is already selected; selection history is not overwritten"
                )
        else:
            model.accept(option_id, author=author)
            self._atomic_save(path, model)
        return self._payload(path, model)
