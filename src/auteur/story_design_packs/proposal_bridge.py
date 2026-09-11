"""Bridge a resolved Tutor choice into a validated noncanonical StructureProposal."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from auteur.blueprint import StoryBlueprint
from auteur.llm import LLMClient, LLMRequest
from auteur.structure.proposal_models import ProposalOption, ProposalType, StructureProposal

from .handoff import derive_decision_handoff
from .models import AuthorAction, source_fingerprint
from .session import TutorSession


_ALLOWED_PATCH_FIELDS = frozenset(
    {
        "structure",
        "story_engine",
        "contract",
        "emotional_design",
        "characters",
        "tension_waveform",
        "theme",
    }
)

_SYSTEM = """You are a bounded narrative Structure proposal planner.
Translate one already-selected Tutor design direction into ONE concrete, minimal
noncanonical Structure proposal option for the supplied current blueprint.

Return JSON only with this exact shape:
{
  "summary": "short proposal summary",
  "option": {
    "summary": "what this concrete realization changes",
    "tradeoffs": "specific costs and benefits",
    "data": {"<allowed top-level blueprint field>": <COMPLETE replacement value>}
  }
}

Rules:
- Use only the allowed top-level fields supplied in the request.
- Never return `identity` or invent authority/acceptance/selection/proposal IDs.
- Each value in `data` must be the COMPLETE replacement value for that top-level
  blueprint field, not a partial nested patch.
- Change at most two top-level fields and only when needed to realize the chosen intent.
- Preserve unrelated accepted content.
- Do not claim that the proposal is accepted, canonical, or automatically applicable.
"""


class GeneratedProposalOption(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: str = Field(min_length=1)
    tradeoffs: str = Field(min_length=1)
    data: dict[str, object] = Field(min_length=1)


class GeneratedProposalContent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    summary: str = Field(min_length=1)
    option: GeneratedProposalOption


class TutorStructureProposalResult(BaseModel):
    """Author-facing result for a generated noncanonical proposal candidate."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_id: str
    card_id: str
    selected_tutor_value: str
    proposal_id: str
    proposal_path: str
    proposal: StructureProposal
    authority_status: Literal["DERIVED / NOT CANON"] = "DERIVED / NOT CANON"
    mutates_story: Literal[False] = False
    requires_author_selection: Literal[True] = True
    ready_for_revision_plan: Literal[False] = False
    inspect_command: str
    next_command_after_selection: str


def _parse_json_object(text: str) -> dict[str, object]:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Tutor Structure proposal response is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Tutor Structure proposal response must be a JSON object")
    return parsed


def _source_path(project_root: Path, source_key: str) -> Path:
    if "=" not in source_key:
        raise ValueError(f"Persisted Tutor source is not a NAME=PATH identity: {source_key}")
    _name, raw = source_key.split("=", 1)
    root = project_root.resolve()
    path = (root / raw).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Persisted Tutor source escaped the selected project")
    if not path.is_file():
        raise ValueError(f"Persisted Tutor source is missing: {raw}")
    return path


def _current_sources(project_root: Path, session: TutorSession) -> dict[str, str]:
    current: dict[str, str] = {}
    for key in sorted(session.source_fingerprints):
        path = _source_path(project_root, key)
        current[key] = source_fingerprint(path.read_bytes())
    return current


def _blueprint_source(project_root: Path, session: TutorSession) -> Path:
    matches = [
        _source_path(project_root, key)
        for key in sorted(session.source_fingerprints)
        if key.split("=", 1)[-1].replace("\\", "/").endswith("blueprint.yaml")
    ]
    if len(matches) != 1:
        raise ValueError("Tutor proposal bridge requires exactly one bound blueprint.yaml source")
    return matches[0]


def _snapshot_digest(source_fingerprints: dict[str, str]) -> str:
    raw = json.dumps(source_fingerprints, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate_patch(blueprint: StoryBlueprint, data: dict[str, object]) -> None:
    fields = set(data)
    if not fields:
        raise ValueError("Generated Structure proposal option must change at least one field")
    unsupported = fields - _ALLOWED_PATCH_FIELDS
    if unsupported:
        joined = ", ".join(sorted(unsupported))
        raise ValueError(f"Generated Structure proposal contains unsupported field(s): {joined}")
    if len(fields) > 2:
        raise ValueError("Generated Structure proposal may change at most two top-level fields")

    current = blueprint.model_dump(mode="json")
    changed = False
    candidate = dict(current)
    for key, value in data.items():
        if current.get(key) != value:
            changed = True
        candidate[key] = value
    if not changed:
        raise ValueError("Generated Structure proposal is a no-op against the current blueprint")

    try:
        StoryBlueprint.model_validate(candidate)
    except ValidationError as exc:
        raise ValueError(
            "Generated Structure proposal does not contain valid complete replacement values"
        ) from exc


def _request(session: TutorSession, blueprint: StoryBlueprint) -> LLMRequest:
    payload = {
        "selected_tutor_value": session.response_value,
        "decision": session.card.decision,
        "recommendation": session.card.recommendation,
        "alternatives": session.card.alternatives,
        "tradeoffs": session.card.tradeoffs,
        "evidence": session.card.evidence,
        "downstream_consequences": session.card.downstream_consequences,
        "allowed_top_level_fields": sorted(_ALLOWED_PATCH_FIELDS),
        "current_blueprint": blueprint.model_dump(mode="json"),
    }
    return LLMRequest(
        system=_SYSTEM,
        user=json.dumps(payload, indent=2, ensure_ascii=False),
        temperature=0.2,
        max_tokens=5000,
    )


def _proposal_from_content(
    session: TutorSession,
    content: GeneratedProposalContent,
    source_fingerprints: dict[str, str],
) -> StructureProposal:
    snapshot = _snapshot_digest(source_fingerprints)
    semantic = {
        "session_id": session.session_id,
        "card_id": session.card_id,
        "selected_tutor_value": session.response_value,
        "snapshot": snapshot,
        "content": content.model_dump(mode="json"),
    }
    content_hash = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    proposal_id = f"tutor_{session.session_id[:12]}_{snapshot[:8]}_{content_hash[:10]}"
    option_id = f"option_{content_hash[:12]}"

    return StructureProposal(
        proposal_id=proposal_id,
        type=ProposalType.REPAIR,
        source_rule=f"tutor_session:{session.session_id}:{snapshot}",
        source_domain=f"tutor_card:{session.card_id}",
        summary=f"Tutor choice {session.response_value!r}: {content.summary}",
        options=[
            ProposalOption(
                id=option_id,
                summary=content.option.summary,
                tradeoffs=content.option.tradeoffs,
                data=content.option.data,
            )
        ],
    )


def _atomic_write_proposal(project_root: Path, proposal: StructureProposal) -> Path:
    proposals_dir = project_root.resolve() / ".auteur" / "structure" / "proposals"
    path = proposals_dir / f"{proposal.proposal_id}.yaml"
    rendered = yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False, allow_unicode=True)

    if path.exists():
        if path.read_text(encoding="utf-8") != rendered:
            raise ValueError(f"Proposal ID collision at {path}")
        return path

    proposals_dir.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return path


def generate_structure_proposal_from_tutor(
    project_root: Path,
    session: TutorSession,
    client: LLMClient,
) -> TutorStructureProposalResult:
    """Generate and atomically persist one validated noncanonical proposal candidate."""
    project_root = project_root.resolve()
    current = _current_sources(project_root, session)
    if current != session.source_fingerprints:
        raise ValueError("Tutor session source snapshot is stale; regenerate the decision first")
    if session.status != "resolved" or session.response_action != AuthorAction.CHOOSE:
        raise ValueError("Tutor proposal bridge requires a resolved choose response")
    if not session.response_value:
        raise ValueError("Tutor proposal bridge requires a selected response value")

    handoff = derive_decision_handoff(session)
    if handoff.status != "route_identified" or handoff.workflow != "structure_revision":
        raise ValueError("Tutor session does not identify a supported Structure authority route")

    blueprint_path = _blueprint_source(project_root, session)
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    response = client.complete(_request(session, blueprint))
    try:
        content = GeneratedProposalContent.model_validate(_parse_json_object(response.text))
    except ValidationError as exc:
        raise ValueError("Tutor Structure proposal response does not match the required schema") from exc
    _validate_patch(blueprint, content.option.data)

    proposal = _proposal_from_content(session, content, current)
    path = _atomic_write_proposal(project_root, proposal)
    relative = path.relative_to(project_root).as_posix()
    return TutorStructureProposalResult(
        session_id=session.session_id,
        card_id=session.card_id,
        selected_tutor_value=session.response_value,
        proposal_id=proposal.proposal_id,
        proposal_path=relative,
        proposal=proposal,
        inspect_command=f"auteur structure proposal inspect {relative} --project .",
        next_command_after_selection=(
            f"auteur structure revision plan --proposal {relative} --project ."
        ),
    )
